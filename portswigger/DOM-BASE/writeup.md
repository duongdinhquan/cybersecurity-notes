# Lý thuyết
- Source : Nơi accept data mà potentially attacker-controlled.Ví dụ như location.search , location.hash , document.referrer , window.name
![image](https://hackmd.io/_uploads/ryvhmxpWZe.png)

- Sink : dangerous JavaScript function hoặc DOM objection có thể dẫn đến các hành vi không mong muốn nếu attacker-controlled. 
![image](https://hackmd.io/_uploads/S1X-EgT-We.png)
- DOM clobbering:
    + một vài hành vi của trình duyêt : Bất kỳ thẻ HTML nào có thuộc tính **id** (hoặc **name** trong một số trường hợp) sẽ tự động trở thành một biến toàn cục trong đối tượng **window**

    + nhận biết : sử dụng toán tử || or sử dụng form 
- trong DOM thì các elements html điều là object .
    - trong một page<Chome> nếu có hai id trùng nhau thì khi dùng cấu lệnh "window.ten_id" trả về một **HTMLCollection** đây cũng là một **object** . **id** trở trành một global variable
    - Tính năng named property access của HTMLCollection : Khi một **HTMLCollection** có attribute **id** or **name** thì có thể truy cập vào elements bằng value của attribute này 
    - toString() : Nếu với các elements html thì kết quả của toString() luôn là [object HTML_tên element_Element] . **Riêng với element <area> và element <a> thì kết quả trả về là values của attribute href**
     - VÍ DỤ : ![image](https://hackmd.io/_uploads/ByHQWlBOge.png)
    - command : window.link ==> trả về **HTMLCollection** (chứa hai thẻ a)  .
    - command:  window.link.quandz ==> trả về thẻ a thứ 2 (đây là một **object**)
    - **NỐI CHUỖI thì hàm toString() sẽ được tự động gọi . Nếu với các elements html thì kết quả của toString() luôn là [object HTML_tên element_Element] . Riêng với element <area> và element <a> thì kết quả trả về là values của attribute href**
    - cid: (or xmpp:)là prototol mà trong allow_list của DOMPurify nên kí tự entries html : &quot: se được browser decode lại lúc render mà cắt end chuỗi
# LAB
## Lab: DOM XSS using web messages

![image](https://hackmd.io/_uploads/ryjZJbWOel.png)

- start:
- ở trang Home có đoạn script ![image](https://hackmd.io/_uploads/S15-gZbueg.png) 
- Nhận một message(event build-in trong js **https://developer.mozilla.org/en-US/docs/Web/API/Window/message_event**) tóm lại là event message được dành cho giao tiếp cross-origin (sự kiện message – một sự kiện built-in trong JavaScript được kích hoạt khi một thông điệp (message) được gửi đến cửa sổ (window) bằng phương thức postMessage())
- đoạn script không check e.origin và dùng .innerHTML để chèn data vào DOM
- payload : ![image](https://hackmd.io/_uploads/B1odFjWuee.png)
- khi content của trang html trong src được load thì mới thực thi postMessage() . postMessage() phải được gọi bởi đối tượng windown của site html nhận message


## Lab: DOM XSS using web messages and a JavaScript URL

![image](https://hackmd.io/_uploads/S1MJU1Mdll.png)

- Start:
- ![image](https://hackmd.io/_uploads/BJYJ_1Muel.png)
- nhận một message từ different site thông qua  postMessage() . Dùng indexOf() để check protocol là https or http . nhưng indexOf() chỉ kiểm tra vị trí đầu tiên của kí tự 
-thực thi javascript trong herf
- payload :![image](https://hackmd.io/_uploads/SJ7Llez_ee.png)
//https: là để bypass indexOf() và mã javascript sẽ thành:
**location.herf=javascript:print()** có dấu comment nên sẽ đúng cú pháp

## Lab: DOM XSS using web messages and JSON.parse

![image](https://hackmd.io/_uploads/SkCiVgz_xx.png)

- Start:
- ở trang home có đoạn javascript: ![image](https://hackmd.io/_uploads/BktWreGOex.png)
- không kiểm tra e.origion nếu attacker dùng iframe để nhúng site này vào iframe và dùng postMessage() để gửi message 
- payload : ![image](https://hackmd.io/_uploads/SyW6imzdxx.png)

## Lab: DOM-based open redirection
![image](https://hackmd.io/_uploads/SyvgmIf_ge.png)

- Start:
- regex.exec(location) , location là là url hiện tại (sink)

![image](https://hackmd.io/_uploads/rk-JX8zuxl.png)
-payload : ![image](https://hackmd.io/_uploads/Hy0jNIz_xx.png)

## Lab: DOM-based cookie manipulation

![image](https://hackmd.io/_uploads/S1t0LIz_ge.png)

- Start:
- lấy windown.location làm cookies=lastViewedProduct mà cái này là du user manipulation
- ![image](https://hackmd.io/_uploads/By_tlkX_lg.png)
-giá trị của href là cookies=lastViewedProduct![image](https://hackmd.io/_uploads/ByxCl1XOxl.png)
- gây XSS ở đây : 
- thay đổi url thành : ![image](https://hackmd.io/_uploads/ryzku17_xe.png)
- kiểm tra cookies có thay đổi theo url không?![image](https://hackmd.io/_uploads/SJ_zdkXugg.png). cookies thay đổi theo url
- quay lại load trang lần 2 thì alert() thực thi
- dùng iframe nhúng target site vào nhưng làm cho load 2 lần :))
- payload : ![image](https://hackmd.io/_uploads/B1lzbeX_lx.png)
- iframe load lần 1 , then onload executed nó kiểm tra attribute 'hehe' không có nên nó sẽ thay đổi src bằng chính nó nên load lần 2 , thiết lập attribute'hehe'=1 để không load vô hạn


## Lab: Exploiting DOM clobbering to enable XSS
![image](https://hackmd.io/_uploads/BJYLEeQuex.png)


- Start:
- **LÝ THUYẾT**: 
    - trong DOM thì các elements html điều là object .
    - trong một page<Chome> nếu có hai id trùng nhau thì khi dùng cấu lệnh "window.ten_id" trả về một **HTMLCollection** đây cũng là một **object** . **id** trở trành một global variable
    - Tính năng named property access của HTMLCollection : Khi một **HTMLCollection** có attribute **id** or **name** thì có thể truy cập vào elements bằng value của attribute này 
    - toString() : Nếu với các elements html thì kết quả của toString() luôn là [object HTML_tên element_Element] . **Riêng với element <area> và element <a> thì kết quả trả về là values của attribute href**
     - VÍ DỤ : ![image](https://hackmd.io/_uploads/ByHQWlBOge.png)
    - command : window.link ==> trả về **HTMLCollection** (chứa hai thẻ a)  .
    - command:  window.link.quandz ==> trả về thẻ a thứ 2 (đây là một **object**)
    
- Solution:
#### CÁCH 1:
- payload 2: do sử dụng DOMPurify version 2.0.15 <= 2.0.17 nên dính lỗi Mutation XSS : ![image](https://hackmd.io/_uploads/By-YfCY_gl.png)
                                                        
[Mutation XSS](https://hackmd.io/W8oWWkmRShSYoOa9JpX-KA)
                                                           [Mutation XSS gốc](https://research.securitum.com/mutation-xss-via-mathml-mutation-dompurify-2-0-17-bypass/)
                                                           
#### CÁCH 2:                                                       
- nhận thấy đoạn code sau để bị DOM clobbering: ![image](https://hackmd.io/_uploads/BkAnwuBuxx.png)
    vì . Global variable defaultAvatar dễ bị DOM clobbering  vì nếu chèn hai element html có id='defaultAvatar' thì có thể truy cập vào 
- phân tích code : vì comment.avatar luôn false nên src kết quả sẽ được **NỐI CHUỖI** thì hàm **toString()** sẽ được tự động gọi . Nếu với các elements html thì kết quả của toString() luôn là [object HTML_tên element_Element] . **Riêng với element \<area> và element \<a> thì kết quả trả về là values của attribute href**
     - payload 1 : tạo ra hai thẻ a với **id="defaultAvatar"** với **name="avatar"** để phá với việc reference của code.   
![image](https://hackmd.io/_uploads/rkaKQ0ruxx.png)

   - kiểm tra trên consolog xem DOM clobbering thành công nhưng avatar unchange???. ![image](https://hackmd.io/_uploads/SkczVCSdlg.png)
![image](https://hackmd.io/_uploads/Syx44Ar_el.png)
    - Không change được vì khi post comment lần 1 thì nó chi mới tạo elemnts html trên page chứ không vẫn chưa áp dụng vào thử tạo một comment thứ 2 thì thấy avatar đã change . ![image](https://hackmd.io/_uploads/BkLFS0S_lx.png)
    - element trên page : ![image](https://hackmd.io/_uploads/H14pSABuxe.png)
    paylaod : ![image](https://hackmd.io/_uploads/BJPQs7q_xl.png)
    **cid:** (or **xmpp:**)là prototol mà trong allow_list của DOMPurify nên kí tự entries html : **&quot:** se được browser decode lại lúc render mà cắt end chuỗi 
    

## Lab: Clobbering DOM attributes to bypass HTML filters
    
    
![image](https://hackmd.io/_uploads/BJCWTm9Oel.png)
    
    
- Start:
    - Lab này sử dụng một **custom library (HTMLJanitor)** để filter comments before it is posted in lab.
    - file : **/resources/js/htmlJanitor.js** đây là file để build a custom library **HTMLJanitor**. 
    file này thực hiện duyệt sanitize data do user post before được post lên lab . Sử dụng TreeWalKer để duyệt từng DOM node . và lọc . 
    ![image](https://hackmd.io/_uploads/B1sTlKouxx.png)
theo như config này thì nó cho phép tag **form,input,b,p**. Do không thể khai thác qua global variable nên chúng ta sẽ khai thác quá tag form vì : nếu chúng ta chèn vào một thẻ input có id="attributes" thì đoạn code sau : ![image](https://hackmd.io/_uploads/BJpbNtidel.png)
    **node.atributes**  thay vì trả về một **NameNodeMap** thì nó lại trả về thẻ input nếu id="adtributes":
    - Payload : ![image](https://hackmd.io/_uploads/HJiWIFougx.png)
    payload này làm cho **node.attributes.length** trả về **undefine** nên **a<undefine** là **false** nên vòng lặp check attribute không xảy ra 
    - kết quả : ![image](https://hackmd.io/_uploads/B1w2Utoulx.png) 
    - truy cập id=1 qua url thì alert() xuất hiện ![image](https://hackmd.io/_uploads/BJElvKouxe.png)
    - payload : ![image](https://hackmd.io/_uploads/HyF7Ktidxx.png)đợi iframe load trang rồi sau 1s load thêm 1 lần nữa để print() chạy
