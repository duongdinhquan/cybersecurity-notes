## Bug logic
Ở change passwd có thể thử một vài case sau:
- thay trường host thành gmail attacker
- một mảng gồm email victim và attacker.

Bypass F2A
    - [video](https://www.youtube.com/watch?v=mV7qOw0iFew). Bypass phía FE , vì FE dựa vào http response để cho phép truy cập vào account . Kẻ tấn công chặn request và thay đổi response về dạng một otp hợp lệ và session được tạo sau khi f2a đã được xác thực.