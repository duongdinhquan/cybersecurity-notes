## Basic SSRF against the local server
Ứng dụng web bán hàng có chức năng kiểm tra số hàng trong kho của mỗi sản phẩm Check stock.
![image](https://hackmd.io/_uploads/Bkz-AtfFzl.png)
Khi thực hiện Check stock, một POST request gửi đến /product/stock với body là địa chỉ đường dẫn một API. Có thể hiểu rằng server query lên API lấy kết quả trước khi trả về cho người dùng.
![image](https://hackmd.io/_uploads/B10-RFzFGl.png)
Tuy nhiên, mình có thể SSRF - sử dụng chính stockApi này để query lên các local URL. Để solve challenge, ta sẽ vào http://localhost/admin.

![image](https://hackmd.io/_uploads/BkkmRKfYzx.png)
Kết quả ta đã vào được trang admin. Bây giờ thực hiện truyền vào stockApi giá trị http://localhost/admin/delete?username=carlos để xóa user carlos.
![image](https://hackmd.io/_uploads/HJl4AYGtfg.png)

## Basic SSRF against another back-end system
Ứng dụng lab này tiếp tục bị dính SSRF tại chức năng check stock. Tuy nhiên, lần này ta sẽ đi thực hiện request đến trang admin của ứng dụng web khác có địa chỉ http://192.168.0.X:8080/admin. Ta phải đi tìm X bằng cách bruteforce 255 giá trị từ 1-255 bằng Intruder.
![image](https://hackmd.io/_uploads/H1nHRKzFfl.png)
Kết quả trả về với http://192.168.0.171:8080/admin, ta truy cập được trang admin thành công.
![image](https://hackmd.io/_uploads/BkewCtzFGx.png)
![image](https://hackmd.io/_uploads/ryuP0KMFzl.png)
Thực hiện xóa user carlos.![image](https://hackmd.io/_uploads/r1BdCtMYze.png)
## SSRF with blacklist-based input filter
Bài này nâng cấp hơn bằng cách blacklist filter một số chuỗi như localhost, 127.0.0.1, … Thử với payload http://localhost thì bị trả 400 Bad Request. Tương tự với 127.0.0.1.
![image](https://hackmd.io/_uploads/SJhtRtzKzl.png)
Ta sẽ bypass bằng http://127.1. Lúc này ta truy cập được trang chủ thành công.
![image](https://hackmd.io/_uploads/r1i50FGtze.png)
Thử vào http://127.1/admin thì bị 400 Bad Request → chuỗi admin bị filter.
![image](https://hackmd.io/_uploads/SyvoAKztfx.png)
Ta bypass bằng cách obfuscate admin thành AdMiN hoặc AdmIn, …
![image](https://hackmd.io/_uploads/H19nCtfYfe.png)
Sau khi bypass thành công, ta vào được trang admin và xóa user carlos.
![image](https://hackmd.io/_uploads/rJOTCYGFfx.png)

## SSRF with filter bypass via open redirection vulnerability
Thực hiện gán stockApi=http://192.168.0.12:8080/admin luôn thì bị trả về 400 Bad Request vì server đã validate URL này.
![image](https://hackmd.io/_uploads/rJy1kqGKfe.png)
Tuy nhiên, để ý tại mỗi post sản phẩm có chức năng chuyển trang Next product.
![image](https://hackmd.io/_uploads/rJsy1czFGl.png)
Click thử và bắt request, ta thấy nó là GET request /product/nextProduct?currentProductId=2&path=/product?productId=3 có chứa 1 tham số path là đường dẫn đến post sản phẩm tiếp theo.
![image](https://hackmd.io/_uploads/rktxy9MYzg.png)
Như vậy ta sẽ thử SSRF tại stockApi với đường dẫn như /product/nextProduct?currentProductId=2&path=/product?productId=3. Kết quả truy cập thành công. Server có thể không validate tham số path này, và ta sẽ tận dụng nó để SSRF đến ứng dụng cần tấn công.
![image](https://hackmd.io/_uploads/rkOW1qfFMl.png)
Truyền path=http://192.168.0.12:8080/admin, ta đã truy cập được trang admin của ứng dụng khác thành công.
![image](https://hackmd.io/_uploads/H1-GkcfKGx.png)
Thực hiện xóa user carlos.
![image](https://hackmd.io/_uploads/S1qGkqzKfl.png)

## Blind SSRF with out-of-band detection
Ứng dụng lab này sử dụng 1 software khác luôn fetch đến URL tại trường header Referer mỗi khi user truy cập 1 trang sản phẩm bất kì. Như vậy ta có thể OOB SSRF bằng cách đưa vào trường Referer URL mà mình control. Sử dụng Burp Collaborator.
![image](https://hackmd.io/_uploads/rJ3Vk9fFMe.png)
Gủi request và kiểm tra log của Burp Collaborator, ta thấy HTTP kèm theo DNS query được gửi đến URL. Điều này chứng tỏ software trên đã truy cập đến URL mà mình đã define trong trường Referer
![image](https://hackmd.io/_uploads/S1Pry9MKMg.png)

## SSRF with whitelist-based input filter
Đối với bài này, ứng dụng thực hiện filter theo whitelist. Cụ thể, khi gán stockApi=http://localhost thì server trả về 400 Bad Request yêu cầu URL cần có host stock.weliketoshop.net.
![image](https://hackmd.io/_uploads/Hy1O1qfKGg.png)
Sử dụng fragment # để bypass không thành công.
![image](https://hackmd.io/_uploads/Skau19ftMg.png)
Thử dùng chèn thêm tài khoản trước hostname bằng @ thì thấy server đã trả 500 response chứng tỏ server đã cố gắng connect đến URL đó không thành.
![image](https://hackmd.io/_uploads/BkqtyqzKzl.png)
Lúc này thử kết hợp fragment # (encoded) vào sau localhost và @. Tuy nhiên kết quả lần này đã bị fail.
![image](https://hackmd.io/_uploads/H1NqkqMKfg.png)
Double encoded # thành %2523 thì thấy, ta đã truy cập thành công trang localhost → lỗi parse URL lúc validate URL.

![image](https://hackmd.io/_uploads/ryJi1qGFfx.png)
Bây giờ chỉ cần /admin để truy cập trang admin.![image](https://hackmd.io/_uploads/r1ij1qMFfl.png)
Thực hiện xóa user carlos.

![image](https://hackmd.io/_uploads/rJ72y5GtMx.png)
