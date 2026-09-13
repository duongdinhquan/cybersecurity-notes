## Lab: Blind XXE with out-of-band interaction via XML parameter entities

![image](https://hackmd.io/_uploads/Hkuur8utgl.png)

- start:
    - request ở check stock function : ![image](https://hackmd.io/_uploads/SkIpH8utlg.png)
    body là xml 
    - payload : ![image](https://hackmd.io/_uploads/SJqlIL_Flx.png)nhận thông báo cấm entities chứng tỏ  Backend không cho dùng entity trong nội dung XML (application data) NHƯNG một số thư viện thì  backend vẫn cho parse DTD và resolve parameter entity. **Không dùng được General Entity (dùng &)-cái này là dùng trong nội dung của XML còn parameter entity lại dùng trong phần định nghĩa của TDT **

    - payload : ![image](https://hackmd.io/_uploads/Byv9_8OKle.png)

## Lab: Exploiting blind XXE to exfiltrate data using a malicious external DTD

![image](https://hackmd.io/_uploads/SJmeq8uFle.png)

- start:
- body post request check stock : ![image](https://hackmd.io/_uploads/BJlsTEFKlx.png)
- payload : ![image](https://hackmd.io/_uploads/ryhkCNYFgl.png)
nhận thông báo : **"Entities are not allowed for security reasons"** . Phía backend không cho dùng entitry trong xml . 
- check xem backend có xử lý prameter entity không? ![image](https://hackmd.io/_uploads/Sy2AZBKtee.png)
nhận thấy có request đến server . ===> lỗi 
- payload : ![image](https://hackmd.io/_uploads/BJSxXLFFgl.png)
- setup server : ![image](https://hackmd.io/_uploads/r1vZQLtFeg.png)
- **&#x25;** là định dạng HTML encode của ký tự % do được chứa trong một định nghĩa parameter entity khác
- Và cần lưu ý rằng, kỹ thuật trên có thể không hoạt động với một số nội dung trong các tệp tin (chẳng hạn ký tự xuống dòng trong /etc/passwd). Một trong những khắc phục là sử dụng giao thức FTP thay thế cho HTTP.



## Lab: Exploiting blind XXE to retrieve data via error messages



- start:
- request check stock : ![image](https://hackmd.io/_uploads/H1jmzoYKlx.png)
- payload : ![image](https://hackmd.io/_uploads/r11SfjYYlg.png)nhận thấy host server nó reflect ở response: ![image](https://hackmd.io/_uploads/HJhUGjYKll.png)
nếu bỏ đi protocal thì nó ghép vào một đường dẫn file để đọc file 
- payload : ![image](https://hackmd.io/_uploads/rkgbtjtYex.png)

- setup server : ![image](https://hackmd.io/_uploads/SkkGKiYtgg.png)


## Lab: Exploiting XInclude to retrieve files

![image](https://hackmd.io/_uploads/HJKO_RKKxx.png)
- start:
- ![image](https://hackmd.io/_uploads/HJXUcAttxx.png)
- không thấy gửi lên một XML document . Nhưng theo đề bài là perfom a Xinclude attack . Có thể backend nó receive client-submitted data , sau đó gắn Values của các file này vào XML document để xử lý , nếu backend not sanitize very well input and support Xinclude có thể bị dính lỗi
- nhận thấy value of productId trong response . ![image](https://hackmd.io/_uploads/B1MrhRKYxg.png)

- paylaod : ![image](https://hackmd.io/_uploads/HkU8k1qKee.png)
nhận thấy có request trên server . Backend lấy value recive from server then inject into XML document
- payload : ![image](https://hackmd.io/_uploads/HkZCykqFll.png)
thành công 


## Lab: Exploiting XXE via image file upload
![image](https://hackmd.io/_uploads/r1IFe1cYll.png)

- start:
- bắt request post ảnh: ![image](https://hackmd.io/_uploads/H1QzSs9tgx.png)
- Apache batik library xử lý file .png và jpg có hỗ trợ xử lý .SVG file
- ![image](https://hackmd.io/_uploads/rJpdTi9Ylg.png)
gửi một payload có nội dung như trên thì thấy ở server có HTTP resquest , chứng tỏ là backend đã parse cái nội dung của XML document này . 
- payload : ![image](https://hackmd.io/_uploads/ry8Qx0cKee.png)


## Lab: Exploiting XXE to retrieve data by repurposing a local DTD
![image](https://hackmd.io/_uploads/rkLilVsFlg.png)

- start:
- request check stocjk : ![image](https://hackmd.io/_uploads/BkF9bEstgg.png)
![image](https://hackmd.io/_uploads/By9nW4jtgl.png)
nhận thấy lab có xử lý các kí tự bị decode ,
- payload : ![image](https://hackmd.io/_uploads/B1EGNNoFgx.png)
có request lên server ===> lỗi . và response trả về nó reflect input user .
-payload : ![image](https://hackmd.io/_uploads/Skiy8VsFle.png)
response "**"XML parser exited with error: java.net.UnknownHostException: attacker.com"**" có một white list obtain host
- payload :![image](https://hackmd.io/_uploads/HJwP8VoYle.png)
theo như đề bài chỉ cho upload local DTD . không thấy báo lỗi :))
- payload : ![image](https://hackmd.io/_uploads/HJDLPVoFle.png)

để ý thứ tự encode kí tự **%** để tạo ra 2 stage tránh parse lỗi , cứ hiểu đơn giản là trong một encode entity thì cần encode một lần nữa để nó bóc từ ngoài vào . Tải docbookx.dtd từ hệ thống , trong file này obtain an entity called ISOamso . Nên overwrite enity này
