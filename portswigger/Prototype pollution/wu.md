## I, lý thuyết
### 1. prototype and inheritance
- [đọc ở đây](https://portswigger.net/web-security/prototype-pollution/javascript-prototypes-and-inheritance#what-is-an-object-in-javascript)
- ngắn ngọn :+1: 
    -  prototype : là một cái khung chứa các method , attribute mà các object kết thừa
    -  khi tạo một object thì bên trong nó luôn có một attribute là '**prototype**'
    -  localStorage/sessionStorage  cũng kế thừa từ Object.prototype . nếu truy cập localStorage bằng property access thì có thể dính lỗi
    -  cách truy cập vào prototype
    ![image](https://hackmd.io/_uploads/S1eESo_0el.png)
    ![image](https://hackmd.io/_uploads/Ska4rjuAge.png)
        + sử dụng contructor để tham chiếu đến protopye
        + ![image](https://hackmd.io/_uploads/rknnSj_0ex.png)

        + ![image](https://hackmd.io/_uploads/S1YpSi_Axe.png)
    - tóm lại : ![image](https://hackmd.io/_uploads/HyoW8s_Rge.png)

### một vài chú ý:

- **Object.defineProperty()** : [lý thuyết](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Object/defineProperty) . nếu không xét value ở tham số thứ 3 , khi không set value thì nó sẽ là undefine . Nếu Object.prototype có attribute value thì khi truy cập vào attribute thì js sẽ trả về giá trị value này:![image](https://hackmd.io/_uploads/H160uTdAgg.png)
- ![image](https://hackmd.io/_uploads/B1OktpdRxl.png)
- **for...in Loop**: được thiết kế để chạy các key(property) trong Object **khồn phân biệt property của nó hay được  kế thừa từ prototype **




### 2. nhận biết một số code dễ bị dính lỗi
- sử dụng toán tử **||** ví dụ : 
- **let transport_url = config.transport_url ||defaults.transport_url;**
-![image](https://hackmd.io/_uploads/HyGPQtLClg.png)

### 3.1 server-side
-


+ BE thường lấy body từ POST request sau đó sử dụng JSON.parse(body) = body để convert một chuỗi sang object . sau đó sử dụng **FOR....IN** để duyệt . nếu không kueemr tra property thì sẽ bị dĩnh lỗi:mô tả code . ![image](https://hackmd.io/_uploads/ryGWMds0gl.png)


- nếu không có reflect ở response
    + Status code override : nếu đoạn code tương tự nhau sau :**status = err.status || err.statusCode || status** 
    + trigger lỗi xem BE có trả về lỗi kèm Object lỗi không? check xem trong object đó có trường nào xem override được không?
    + Charset override

## REC via server-side prototype pollution: [chi tiết](https://portswigger.net/web-security/prototype-pollution/server-side#remote-code-execution-via-server-side-prototype-pollution)
- child process in node.js : [chi tiết](https://www.w3schools.com/nodejs/nodejs_child_process.asp)**<ý thưởng chính là prototype tham số options>**
    + đọc cách sử dụng các thuộc tính trong tham số options và cách nó được sử dụng ví dụ như:
        + ![image](https://hackmd.io/_uploads/rJCncK20ge.png)
cách mà child_process truy cập vào các thuộc tính của options
    + NODE_OPTIONS : Đây là biến môi trường (environment variable) trong Node.js, cho phép định nghĩa các flag dòng lệnh mặc định khi khởi động Node process mới (qua child_process). Nếu không được định nghĩa rõ ràng, nó có thể được lấy từ prototype của object process.env (vì env là object).. cho phép **define a string of command-line arguments that should be used by default whenever you start a new Node process**
    + NODE_OPTIONS  là property của **env object** . **env object** có thể bị control thông quan prototype pollution
    + Shell property: Một số hàm trong child_process (như exec, spawn) chấp nhận option shell, chỉ định shell để chạy lệnh (mặc định là /bin/sh trên Unix). Nếu đặt shell: 'node', thì lệnh sẽ chạy như một Node process mới.
- sau khi đã prototype pollution thì tìm end point thực thi lệnh hệ thống bằng **child_process.exec , child_process.execFile() , child_process.spawn() , child_process.fork()** , .... 
- mô tả code phía BE : 
![image](https://hackmd.io/_uploads/H1w46pi0xl.png)
![image](https://hackmd.io/_uploads/SJwB6pj0ee.png)

- **child_process.fork()**
    + syntax : ![image](https://hackmd.io/_uploads/BkK_hEh0xx.png)
    + 

    + execArgv: Array flag như ['--max-old-space-size=4096']. Nếu kiểm soát được, kẻ tấn công có thể thêm --eval='malicious code'.(thuộc options)
    + --eval: Cho phép thực thi JS tùy ý trong subprocess, ví dụ load module như require('fs') để đọc file, hoặc require('child_process') để spawn lệnh khác
- **child_process.execSync()**
    + syntax: **child_process.execSync(command[, options])**
    + execSync(): Thực thi string như lệnh hệ thống (ví dụ: execSync('ls')), dễ bị command injection nếu string bị kiểm soát.
    +options : có các property như shell và input(input: String hoặc Buffer được pass vào stdin của subprocess. Nếu undefined, không có input.)
- Các options quan trọng cho RCE
    + các options sẽ được chạy trước (lúc nạp node.js) trước khi chạy tiến trình con
    + execArgv options nguy hiểm:
        + --eval <\code\>: Thực thi JavaScript code or --e
        + --require <\module\>: Pre-load module
        + --inspect=<\host>: Mở debug port **chỉ tạo DNS lookup**
        + **khi chạy thì nó tương đương với câu lệnh node --eval..... , tương tứ**
    + Shell options:
        + shell: 'node': Cho phép JavaScript execution
        + shell: 'vim'/'ex': Cho phép command execution qua input
            + vim:  
                + là một text editor nhưng có thể executable system command
                + để thực thi system command cần syntax : **:! command system**
                + system command có thể nhận qua thuộc tính **input** của stdin stream
                + ![image](https://hackmd.io/_uploads/BySU9z00ex.png)
                + các model thực thi trong **vim**
                + ![image](https://hackmd.io/_uploads/r1-sqfCAlg.png)


        + shell: 'bash'/'sh': System command execution
## labs
### Lab: Client-side prototype pollution via browser APIs
![image](https://hackmd.io/_uploads/BkLjZ2YReg.png)

- start:
- thử thay đổi query trên URL thành : ![image](https://hackmd.io/_uploads/SkhLYnKRxl.png)
quay lại console nhập Object.prototype:![image](https://hackmd.io/_uploads/Hkv5F2tAex.png)
không thấy hehe properties . thử thay đổi URL thành![image](https://hackmd.io/_uploads/Bkj0F2YAee.png) và đã thấy ![image](https://hackmd.io/_uploads/SJRyq3tRlx.png)
- tìm gadget(đoạn code js để thực thi)
- vào source check hai file js . ![image](https://hackmd.io/_uploads/B1aj5nKRxx.png)
ta thấy đoạn code này có vấn đề: ![image](https://hackmd.io/_uploads/S1Wg1TYCex.png)

- ta nhận thấy ở ![image](https://hackmd.io/_uploads/r1APag90gg.png) không định dạnh value ở tham số thứ 3 . nên khi truy cập **config.stransport_url** nó sẽ truy cập vào phần kế thừa từ prototype của Object . 
- tạo payload : ![image](https://hackmd.io/_uploads/BJkQIW5Rex.png)


### Lab: DOM XSS via client-side prototype pollution
![image](https://hackmd.io/_uploads/ByfNvWqCex.png)

tương tự như lab trên

### LLab: DOM XSS via an alternative prototype pollution vector

- thay đổi url thành ![image](https://hackmd.io/_uploads/HkFbbLcRle.png)
 và nhận thấy  prototype pollution đã xảy ra ở Object.prototype![image](https://hackmd.io/_uploads/BycI-Uq0xe.png)
 - tìm code js có thể thực thi . ![image](https://hackmd.io/_uploads/BkbFZU5Alg.png)
đoạn code này có sử dụng eval() sẽ nhận một chuỗi và thực thi code . **manager.macro** sẽ trả về macros[property]
- payload : ![image](https://hackmd.io/_uploads/HJuhVU90lg.png)


### Lab: Client-side prototype pollution via flawed sanitization
![image](https://hackmd.io/_uploads/rkdFq8q0el.png)

![image](https://hackmd.io/_uploads/SJoJRwcRlx.png)
lab này sử dụng bộ lọc nhưng yếu , bộ lọc không đệ quy mà chỉ lọc một lần
- url : ![image](https://hackmd.io/_uploads/HkO7Cw50xx.png)
nhận thấy Object.prototype bị polluted ![image](https://hackmd.io/_uploads/S1UIAwq0le.png)
payload : ![image](https://hackmd.io/_uploads/rJ4l1uq0ee.png)

### Lab: Privilege escalation via server-side prototype pollution
![image](https://hackmd.io/_uploads/BkiLaei0lg.png)
-start:

![image](https://hackmd.io/_uploads/B1MUReoRlg.png)

thấy response nó reflect các trường từ request kèm theo filed:**isAdmin**![image](https://hackmd.io/_uploads/r1ph0ljRgx.png)
reflect toàn bộ mà không có một định dạng nhất định , khả năng cao sử dụng JSON.parse() rồi sau đó dùng for để lặp từ cặp key để merge vào object gửi về FE.
- payload :+1: 
- ![image](https://hackmd.io/_uploads/Hk2PkWiRlx.png)


### Lab: Bypassing flawed input filters for server-side prototype pollution
![image](https://hackmd.io/_uploads/S1jJ4ziRgx.png)
- start:
- request gốc : ![image](https://hackmd.io/_uploads/HyJI7usRle.png)BE dùng express frame
- thử chèn payload đơn giản ![image](https://hackmd.io/_uploads/H1ko7ujAgl.png)
thì nhận thấy không có sự thay đổi , có vẻ có bộ lọc chặn .
- ![image](https://hackmd.io/_uploads/HyrRXOjCxl.png)
logic filter có vẻ không phải là loại bỏ mà là chặn keyword luôn
- thử dùng với **constructor**![image](https://hackmd.io/_uploads/BkdKr_oCgg.png)thành công
- payload : ![image](https://hackmd.io/_uploads/HJznSdsRge.png)

### Lab: Remote code execution via server-side prototype pollution
![image](https://hackmd.io/_uploads/HJaW20oCxx.png)
- start:
- **các case BE dùng child_process.fork(),child_process.execSync()
- có bị prototype pollution**
- ![image](https://hackmd.io/_uploads/Bk9ArL3Cgg.png)
- một payload xác nhận xác sử dụng DNS lookup
- ![image](https://hackmd.io/_uploads/SycYcZCRxx.png)
- payload sử dụng eval để thực thi code
- ![image](https://hackmd.io/_uploads/Hk-JjZACxg.png)

- request tương tác với os command
- ![image](https://hackmd.io/_uploads/SkXVULhRee.png)
- payload : xóa file ![image](https://hackmd.io/_uploads/SyQ7sWA0ll.png)
