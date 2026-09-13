### 1. Redis Key Collision in `Auth()` class

In the `Auth.set()` method, the application uses the raw email string directly as a key in Redis to track the number of verification requests:

```python
setcount = conn.get(self.email)
...
conn.set(self.email, setcount)
```

Meanwhile, the OTP token is stored under the key `auth:{self.email}`. If an attacker registers a user with the userid `auth:admin`, their email becomes `auth:admin@ctfprob.dreamhack.io`. When requesting an email verification, Redis stores the counter value (`1`) under the key `auth:admin@ctfprob.dreamhack.io`. This directly overwrites the OTP token storage key belonging to the legitimate `admin` user.

### 2. Lowercase Logic Flaw in `User.to_json()`

The `to_json()` method converts the `userid` and `email` to lowercase before saving them into the session:

```jsx
def to_json(self):
    return {
        "userid": self.userid.lower(),
        "password": self.password.lower(),
        "email": self.email.lower(),
        "auth": self.auth,
    }

```

Registering an account with uppercase letters (e.g., `ADMIN`) allows it to bypass database uniqueness checks against `admin`, but the active session treats the user as lowercase `admin`.

### Exploitation Steps

### Step 1: Register a Bait Account

- Go to `/signup`.
- Register with:
    - **userid**: `auth:admin`
    - **userpw**: `1234`
- The system assigns the email `auth:admin@ctfprob.dreamhack.io`.

### Step 2: Poison the Admin OTP Key

- Log in with the `auth:admin` account and navigate to `/email_verify`.
- Send a POST request to trigger `Auth.set()`.
- **Backend Effect:** Redis saves the counter `1` under the key `auth:admin@ctfprob.dreamhack.io`, accidentally turning the admin's OTP code into `1`.

### Step 3: Register a Spoofed Admin Account

- Log out via `/signout`.
- Go to `/signup` and create a new account:
    - **userid**: `ADMIN` (fully capitalized)
    - **userpw**: `1234`
- **Backend Effect:** The `to_json()` function forces the userid and email into lowercase (`admin` and `admin@ctfprob.dreamhack.io`), updating your current session context to impersonate the real administrator.

### Step 4: Bypass Verification Check

- **Important:** Do **not** visit `/email_verify`, as doing so would overwrite the poisoned key with a new random OTP.
- Directly access `/email_verify_chk`.
- Enter **`1`** as the verification code and submit.
- **Backend Effect:** `Auth.get()` reads the value `1` from Redis, matches it successfully, and updates the legitimate `admin` user's record in SQLite to `auth = True`.

### Step 5: Retrieve the Flag

- Navigate to `/flag`.
- The system evaluates `myusr.userid == "admin" and myusr.auth`, which resolves to true and grants the flag.

### Flag

`DH{3cd6941075580d889519fcf1bd422bd1}`