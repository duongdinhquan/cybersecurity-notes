
## 1. SSRF
[link chi tiết](https://blog.voorivex.team/we-need-to-talk-about-csrf-again)
Mục đích: "CSRF chỉ xảy ra với HTML Form cổ điển. API nhận JSON thì trình duyệt bắt buộc phải gửi Preflight (OPTIONS), mà CORS không mở thì attacker chịu chết."

The session cookie has to actually be sent on cross-origin requests, which depends on its `SameSite` attribute.
- `SameSite=Strict`: Cookie tuyệt đối không được gửi đi trong bất kỳ request cross-site nào (kể cả khi người dùng bấm vào một đường link dẫn từ trang web khác sang). Cookie chỉ được đính kèm khi bạn thao tác trực tiếp hoàn toàn trong phạm vi website đó. Điều này giúp chống tấn công CSRF (Cross-Site Request Forgery) triệt để nhất.
- `SameSite=Lax`: Đây là mức mặc định của hầu hết trình duyệt hiện đại. Cookie sẽ được gửi đi trong các request điều hướng cấp cao (top-level navigation) – ví dụ như khi người dùng click vào một đường link từ trang ngoài dẫn đến trang của bạn. Tuy nhiên, nó sẽ bị chặn đối với các request ngầm chéo nguồn như `fetch`, `XMLHttpRequest`, hoặc việc tải hình ảnh/iframe từ một trang web khác.
- `SameSite=None` (kèm cờ Secure): Cookie sẽ được phép đính kèm và gửi đi trong mọi request cross-site (cả điều hướng lẫn các request ngầm như fetch/XHR). Bắt buộc phải đi kèm thuộc tính Secure (chỉ truyền qua HTTPS) thì trình duyệt mới chấp nhận cấu hình này. Đây là cấu hình thường được dùng cho các tài nguyên chia sẻ bên ngoài hoặc các kịch bản tấn công yêu cầu cookie phải "bám" theo request chéo nguồn.

### SOP (Same-origin-policy)
- một scrip hay một programming không thể tương tác hoặc lấy dữ liệu từ một trang web khác (khác origin) trừ khi cùng origin
- nó được thưc thi bởi TRÌNH DUYỆT không liên quan đến server
- `origin = protocol + domain + port`
- SOP chỉ ngăn cản việc ĐỌC , THAO TÁC  dữ liệu KHÁC origin chứ KHÔNG CẤM HIỂN THỊ NỘI DUNG (ví dụ src trong iframe khác origin). SOP chỉ quyết định xem trang web hiện tại có được đọc response được phản hồi từ origin khác hay không.
- để đọc được phản hồi phụ thuộc vào reponse headere : `Access-Control-Allow-Origin:`
- `Access-Control-Allow-Origin` : 
- **NOTE** : trình duyệt CẤM load các file local từ một trang web bên ngoài (tranh web có giao thức http/https) đối với trình duyệt được mở bằng giao thức `file://` thì `ĐƯỢC PHÉP` load local file và sử dụng HTTPSS/HTTP để load internal web pages

### CORS (Cross-Origin Resource Sharing)
Cross Origin Resource Sharing (CORS) is a security mechanism implemented by web browsers that allows web applications to access resources from domains other than the one serving the application
- `Access-Control-Allow-Origin`: 
    - Server chỉ định origin (tên miền nguồn) nào được phép truy cập tài nguyên này.
    - Nếu giá trị trả về không khớp với origin đang chạy script trên trình duyệt, trình duyệt sẽ chặn không cho JavaScript đọc response
- `Access-Control-Allow-Methods`: Dùng trong bước Preflight, server báo cho trình duyệt biết những phương thức HTTP nào (PUT, DELETE, PATCH, POST,...) được phép dùng trên endpoint này.
- `Access-Control-Allow-Headers`: Dùng trong bước Preflight, server chỉ định những HTTP header tùy biến hoặc không chuẩn nào được phép xuất hiện trong request chính.
- `Access-Control-Allow-Credentials`: Cho phép JavaScript đọc response khi request có mang theo thông tin xác thực nhạy cảm (như Cookie, HTTP Authentication, hoặc Client Certificate).
    - Giá trị duy nhất có hiệu lực: `Access-Control-Allow-Credentials: true.`
    - Nếu request có credentials: '`include`' (tức là có gửi kèm cookie session của nạn nhân), thì Server bắt buộc phải trả về cả 2 điều kiện:
    1. `Access-Control-Allow-Credentials: true`
    2. `Access-Control-Allow-Origin`uyệt đối không được dùng dấu sao `*`.
    

Request được xem là simple request nếu `Content-Type` values:
- application/x-www-form-urlencoded
- multipart/form-data
- text/plain
Simple request sẽ bỏ qua bước  `Preflight request`