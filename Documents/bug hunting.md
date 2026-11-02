## Bug logic
Ở change passwd có thể thử một vài case sau:
- thay trường host thành gmail attacker
- một mảng gồm email victim và attacker.

Bypass F2A
    - [video](https://www.youtube.com/watch?v=mV7qOw0iFew). Bypass phía FE , vì FE dựa vào http response để cho phép truy cập vào account . Kẻ tấn công chặn request và thay đổi response về dạng một otp hợp lệ và session được tạo sau khi f2a đã được xác thực.


## take over account.
Ở đăng kí tài khoản thì sẽ có hai phương pháp chủ yếu:
- sử dụng email + password để tạo tài khoản
- tạo tài khoản thông qua oauth2.0 

### 1. pre-account takeover 
https://hackerone.com/reports/1074047

Lý do: 
- Lỗi logic trong luồng đăng ký/đăng nhập và liên kết tài khoản OAuth. 
- attacker tạo một tài khoản bằng email của victim bằng phương pháp (email + passwd) nhưng không xác thực email
- Victim đăng nhập/đăng ký bằng OAuth Google/Facebook/... với cùng email, hệ thống lại liên kết OAuth vào tài khoản đã tồn tại từ trước, nhưng không vô hiệu hóa mật khẩu do kẻ tấn công đặt hoặc không tách email chưa xác minh ngay lập tức.

Kết quả: nạn nhân đăng nhập được bằng OAuth, còn kẻ tấn công vẫn đăng nhập được bằng mật khẩu cũ → chiếm tài khoản.

mô tả mã nguồn
```python
// VICTIM_EMAIL được lấy sau khi sử dụng access_token để lấy thông tin sau khi OAuth .

user = conn.execute(
        "SELECT * FROM users WHERE email = ?", (VICTIM_EMAIL,)
    ).fetchone()

    if user:
        # Account already exists → MERGE OAuth into it (vulnerable!)
        conn.execute(
            """
            UPDATE users
               SET oauth_provider='google',
                   oauth_id='victim_google_uid_123',
                   email_verified=1,
                   flag=?
             WHERE email=?
            """,
            (FLAG, VICTIM_EMAIL),
        )
        msg = ("Victim logged in via Google OAuth — <b>linked to the "
               "existing account</b> registered with this email.")

```
Pathched:
- Nếu user tồn tại với email_verified=0 → từ chối merge,
- Khi merge OAuth → set `password = NULL` và `email_verified = 1`
- yêu cầu nhập lại password cũ để xác thực rồi mới merge


Có thể kết hợp với IDOR để take over account . Ví dụ như người dùng liên kết tài khoản với google mà lại sử dụng một tham số ví dụ như `ownerBid` để xác định tài khoản . [link](https://0xgaurang.medium.com/case-study-oauth-misconfiguration-leads-to-account-takeover-d3621fe8308b)

