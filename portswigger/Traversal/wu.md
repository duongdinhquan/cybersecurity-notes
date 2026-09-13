 ## File path traversal, simple case
 Ứng dụng web load ảnh của các post thông qua tham số filename.
 ![image](https://hackmd.io/_uploads/SJdLQqMYfl.png)
Truy cập đường dẫn load ảnh của post bất kì. Ảnh này có vẻ nằm ở đường dẫn /var/www/html (web root directory của Linux).![image](https://hackmd.io/_uploads/H1TDm9zYMg.png)
Thay đổi tham số filename thành ../../../etc/passwd để traverse về thư mục root và truy cập file /etc/passwd.![image](https://hackmd.io/_uploads/ryO_mqztzg.png)
##  File path traversal, traversal sequences blocked with absolute path bypass
Ứng dụng web load ảnh của các post thông qua tham số filename và ta lại khai thác lỗ hổng File path traversal ở tham số này.![image](https://hackmd.io/_uploads/HkU275GFze.png)
Khi traverse bằng ../../../etc/passwd thì bị trả về 400 bad request. Lí do là do ứng dụng đã xóa ../ nếu nó xuất hiện trong param filename.![image](https://hackmd.io/_uploads/BkxaQqfFMe.png)
Tuy nhiên, theo mô tả thì nó làm việc đó không triệt để. Cụ thể, với ....// thì nó sẽ chỉ xóa ../ ở giữa, và kết quả vẫn còn lại ../ → ta có thể bypass để traverse. Sử dụng payload ....//....//....//etc/passwd ta sẽ đọc được nội dung file /etc/passwd thành công.
![image](https://hackmd.io/_uploads/Hyjp7cfKzx.png)

![image](https://hac
Ứng dụng web load ảnh của các post thông qua tham số filename và ta lại khai thác lỗ hổng File path traversal ở tham số này.![image](https://hackmd.io/_uploads/HkU275GFze.png)
Khi traverse bằng ../../../etc/passwd thì bị trả về 400 bad request. Lí do là do ứng dụng đã xóa ../ nếu nó xuất hiện trong param filename.![image](https://hackmd.io/_uploads/BkxaQqfFMe.png)
Tuy nhiên, theo mô tả thì nó làm việc đó không triệt để. Cụ thể, với ....// thì nó sẽ chỉ xóa ../ ở giữa, và kết quả vẫn còn lại ../ → ta có thể bypass để traverse. Sử dụng payload ....//....//....//etc/passwd ta sẽ đọc được nội dung file /etc/passwd thành công.
![image](https://hackmd.io/_uploads/Hyjp7cfKzx.png)
kmd.io/_uploads/H11qQcfKMg.png)
Khi traverse bằng ../../../etc/passwd thì bị trả về 400 bad request → Có vẻ như server đã chặn ../.![image](https://hackmd.io/_uploads/rk9qmczYfl.png)
Tuy nhiên, khi truy cập bằng đường dẫn tuyệt đối /etc/passwd thì server trả về nội dung file thành công.![image](https://hackmd.io/_uploads/S1QoQqzFfg.png)
## File path traversal, traversal sequences stripped non-recursively
Ứng dụng web load ảnh của các post thông qua tham số filename và ta lại khai thác lỗ hổng File path traversal ở tham số này.![image](https://hackmd.io/_uploads/HkU275GFze.png)
Khi traverse bằng ../../../etc/passwd thì bị trả về 400 bad request. Lí do là do ứng dụng đã xóa ../ nếu nó xuất hiện trong param filename.![image](https://hackmd.io/_uploads/BkxaQqfFMe.png)
Tuy nhiên, theo mô tả thì nó làm việc đó không triệt để. Cụ thể, với ....// thì nó sẽ chỉ xóa ../ ở giữa, và kết quả vẫn còn lại ../ → ta có thể bypass để traverse. Sử dụng payload ....//....//....//etc/passwd ta sẽ đọc được nội dung file /etc/passwd thành công.
![image](https://hackmd.io/_uploads/Hyjp7cfKzx.png)

## File path traversal, traversal sequences stripped with superfluous URL-decode
Ứng dụng web load ảnh của các post thông qua tham số filename và ta lại khai thác lỗ hổng File path traversal ở tham số này.![image](https://hackmd.io/_uploads/r1My_qztze.png)
Khi traverse bằng ../../../etc/passwd thì bị trả về 400 bad request → ứng dụng chặn ../ để traverse.![image](https://hackmd.io/_uploads/HJT1_czKGe.png)Thử encode URL kí tự / thành %2f, kết quả cũng trả về 400 do có thể web browser đã decode trước và server vẫn hiểu đó là /![image](https://hackmd.io/_uploads/S1ae_5GKGe.png)
Nếu đọc kĩ mô tả, có vẻ như server còn có 1 bước URL decode nữa sau khi check ../ → Nếu ta double encoding ../ -> ..%2f -> ..%252f thì khi submit request, server sẽ hiểu ..%252f thành ..%2f, và cái này trải qua một bước URL decode nữa sẽ thành ../ → Ta bypass thành công và xem được nội dung file /etc/passwd với payload như hình dưới.![image](https://hackmd.io/_uploads/ByOWd9zFMg.png)

## File path traversal, validation of start of path
Ứng dụng web load ảnh của các post thông qua tham số filename với đường dẫn tuyệt đối tại /var/www/html/<file-name>.jpg.![image](https://hackmd.io/_uploads/S1eS_5ftfx.png)
Thử truyền vào filename giá trị /etc/passwd thì không thành công. Theo mô tả thì server sẽ validate filename phải bắt đầu bằng /var/ww/html/
Như vậy chỉ cần bypass bằng cách traverse dựa trên folder /var/ww/html/ với payload /var/www/html/../../../etc/passwd, ta sẽ solve được challenge.![image](https://hackmd.io/_uploads/HyeDOcfYze.png)

## File path traversal, validation of file extension with null byte bypass
    
Ứng dụng web load ảnh của các post thông qua tham số filename.
![image](https://hackmd.io/_uploads/SkEOuczFMl.png)
Theo mô tả, nó yêu cầu filename phải chứa extension .jpg.
![image](https://hackmd.io/_uploads/ryytdcGKzl.png)

Do đó, để đọc được file /etc/passwd ta sẽ traverse và dùng null byte theo cách sau để bypass ../../../etc/passwd%00.jpg. Khi đó payload sẽ thỏa điều kiện của ứng dụng và từ đó ta đọc được nội dụng /etc/passwd.
![image](https://hackmd.io/_uploads/ryntd5Gtzg.png)
