## JAVA
### kiến thức cần thiết
**để sử dụng được các method thì bắt buộc là nó phải là OBJECT . Trong java các kiểu dữ liệu NGUYÊN THỦY không phải là OBJECT nên không áp dụng được**
.getSuperclass() : truy cập đến class cha của đối tượng 
.getClass() : truy cập đến bản bulerpint của đối tượng 
- Tải class động :
	+ Class.forName("tên.class")		# trả về class type
- Lấy method (static hoặc instance) :
	+ Class.getMethod("tênMethod", Class[] params)
- Gọi method thật sự
	+ Method.invoke(Object obj, Object... args)
- Tạo object mới (Class ở đây là kết quả của tải class động)
	+ Class.newInstance(args)		
	+ Class.getDeclaredConstructor(Class[] params)
	+ Constructor.newInstance(args)				# trả về  đối tượng 
	+ Class.getContructor(class type của agrs)			# ở đây chỉ là tạo đối tượng Constructor chứ chưa tạo đối tượng 
- Lấy Class của bất kỳ object nào
	+ Object.getClass()

### kiến thức nền tảng :+1:
- Kiểu dữ liệu Class : Trong Java, mỗi kiểu dữ liệu đều có một object đại diện kiểu đó, gọi là Class
- ví dụ : 
    + `String.class        // Class của kiểu String`
    + `Object.class        // Class của kiểu Object`

    + 👉 Những cái này đều là object thuộc kiểu Class
-result trong lúc debug : `class java.lang.String`
![image](https://hackmd.io/_uploads/Hy1BxUOcWx.png)
- phân biệt Giá trị (value) , (2) Object , (3) Class của nó
    + `String s = "abc";`
        + s : giá trị
        + new String() : đối tượng
        + String.class : kiểu dữ liệu (Class)
- Khi gọi **getConstructor()** → c**ần Class**
- Khi gọi **newInstance()** → **cần giá trị thật** (value , object )

- **mẹo xác định 1 chain có trả về loại Class không** :  nhập chain vào code frame lúc debug nếu result trả về dạng : class tên_đầy_đủ_của_class(Fully Qualified Class Name (FQCN))
- lúc debug nếu thấy result dạng class something
    + Bạn đang ở Class level
    + 
- Lúc debug và result dạng something
    + Bạn đang ở instance level
    + có thể gọi các method của instance đó

### Các phương thức của java.lang.Class , java.lang.reflect.Method

#### 1. trả về đối tượng Class () Nhiệm vụ của nó là trả về kiểu dữ liệu thực sự (runtime class) của đối tượng đang gọi nó.
1. "".getClass() 								# dùng instance của một đối tượng để gọi class 
2. Class.forName("fullName_class")					# dùng static method để gọi . fullName_class là Tên đầy đủ của Class (Fully Qualified Class Name) mà bạn muốn máy ảo Java (JVM) tìm kiếm và nạp vào bộ nhớ tại thời điểm chương trình đang chạy.
3. Thread.currentThread().getContextClassLoader().loadClass("tên_class")		# dùng ClassLoader để gọi 


node : .getClass() là sẽ truy cập blueprint của đối tượng đó 

#### 2. truy cập vào các method của bản blueprint 

1. getMethods() 	 					kết quả trả về một MẢNG chứa toàn bộ các public method của bản blueprint hiện tại (bao gồm cả hàm kế thừa từ lớp cha)
2. getMethod(String name , Class... params)	Tìm đích danh 1 hàm public.				
3. getDeclaredMethods()					Lấy mảng tất cả các hàm tự viết trong class đó (private, public, v.v.), không lấy của lớp cha.
4. getDeclaredMethod(String name, Class... params)	: Tìm đích danh 1 hàm bất kỳ (kể cả private).

#### 3 : Nhóm quét Biến/Thuộc tính (Fields)

1. getFields() : lấy tất cả các fields của **class hiện tại** và **superclass**
2. getDeclaredFields(): Lấy mảng **các** biến của class hiện tại **không quan tâm modifer**
3. getField(String name) / getDeclaredField(String name): Tìm đích danh 1 biến (ví dụ: tìm biến lưu trữ mảng byte bên trong chuỗi String).
- các câu lệnh này trả về  class **Field** (java.lang.reflect.Field) , đây là chỉ là bản mô tả về filed được chỉ định
- các method của class **Field**:
    - getName() : Trả về tên của trường.
    - getType() : Trả về đối tượng **Class** đại diện cho kiểu dữ liệu của trường.
    - getModifiers(): trả về mã số (integer) đại diện cho các từ khóa của trường (private, static, final...). Dùng lớp Modifier để giải mã.
    - getDeclaringClass() : Trả về đối tượng Class của lớp chứa trường này.
    - get(Object obj) : Trả về giá trị của trường từ đối tượng obj cụ thể. (trả về object ) , ojb phải là 1 instance của class
    - set(Object obj, Object value): Gán giá trị mới value cho trường của đối tượng obj.
    - 
#### 4. Nhóm quét Hàm tạo (Constructors)

1. getConstructors() / getDeclaredConstructors(): 	Xem class này có thể được khởi tạo bằng những cách nào (dùng từ khóa new như thế nào).
2. getConstructor(**1 mảng kiểu Class chứa kiểu dữ liệu của từng tham số**)			:	trả về đối tượng Constructor , Các tham số truyền vào bắt buộc là kiểu tham số chứ không phải giá trị . Nó chỉ ra lệnh là tìm kiếm contructor có kiểu dữ dự liệu như thế này , blabala , sau đó sử dụng newInstance() mới là tạo đối tượng thức sự

### Các phương thức của  java.lang.reflect.Method

- Khi truy cập vào method của thì nó sẽ trả về kiểu dữ liệu Method , có thể sử dụng các phương thức sau trên chính đối tượng Method đó:
	+ invoke(Object obj, Object... args) : Hãy chạy hàm này với các tham số này, trên đối tượng này!
	+ setAccessible(boolean flag)	: Nếu hàm này là private và Java cấm bạn chạy nó? Chỉ cần gọi setAccessible(true), hệ thống bảo mật của Java sẽ bị vô hiệu hóa đối với hàm này.

### Các package mạnh có thể hỗ trợ payload

#### 1. "java.lang.Runtime"
- Runtime là class đại diện cho runtime environment của JVM.
- có static getRuntime() trả về đối tượng **Runtime** . từ đối tượng runtime này có thể gọi các method như exec("...") để thực thi lệnh OS (trả về Process) . 

## C#
**1. Phân cấp cấu trúc lập trình**
![image](https://hackmd.io/_uploads/SJJlBpdabl.png)
- trong đó :+1: 
    - Assemblies : Gioongs như một container là một file đã được biên dịch, thường có phần mở rộng là **.dll** (Dynamic Link Library) hoặc **.exe** (Executable).Nó giống với file **.jar** chứa các file **.class** trong **java core**
    - modiles : Bên trong một Assembly có thể chia thành nhiều phân vùng logic gọi là các Module (các file .netmodule).
    - Type (Kiểu): Đây là thuật ngữ tổng quát trong C# dùng để gọi chung các cấu trúc lập trình như: Class, Interface, Struct, Enum, và Delegate.Member (Thành viên): Đây là những "mảnh ghép" nhỏ nhất cấu tạo nên một Type (một Class hoặc Interface).Các Member bao gồm:
        - Fields (Biến/Trường dữ liệu)
        - Properties (Thuộc tính - C# có khái niệm Property rất mạnh, kết hợp giữa getter/setter)
        - Methods (Hàm/Phương thức)
        - Constructors (Hàm khởi tạo)
        - Events (Sự kiện)
        
**2.Core API System.Reflection**
[link](https://blog.csdn.net/bugcom/article/details/156658748)
- sơ đồ kế thừa của các lớp cốt lõi trong Reflection API nền tảng C#/.NET
![image](https://hackmd.io/_uploads/HJOKzfi6bx.png)
    - FieldInfo class : Đại diện cho các trường (fields) hay còn gọi là các biến cấp lớp. Lớp này cho phép bạn lấy hoặc thay đổi giá trị của một biến trong đối tượn
    - PropertyInfo class : Đại diện cho các thuộc tính (properties).
    - MethodBase class: Lớp cơ sở trừu tượng dành riêng cho các hành vi (hàm). Nó chứa thông tin chung về danh sách tham số (parameters), cờ (flags),
        - ConstructorInfo: Đại diện cụ thể cho các hàm khởi tạo (constructors).
        - MethodInfo: Đại diện cho các phương thức (methods) thông thường.
    - EventInfo: Đại diện cho các sự kiện (events). Dùng để kiểm tra các sự kiện được khai báo trong lớp và có thể dùng để đính kèm (attach) hoặc gỡ bỏ (detach) các trình xử lý sự kiện (event handlers) một cách động.
- core member 
![image](https://hackmd.io/_uploads/SJrFmGjpbl.png)

- trong C# thì "**Type** is the **entry class** to the entire reflection system, and almost all reflection operations start from it."
- sử dụng **BaseType** để truy cập vào type của class cha
    **1. cách để nhận được 1 Type** : 
        - `Object.GetType()` : trong C# mọi thứ đề kế thừa từ Object trừ kí tự (character) nên Object có thể là : "" , 1, 2, .... 
            - cấu lệnh này trả về Type của loại Object 
            - mọi Object đều có method **GetType()** để lấy type của class đó
    - method GetType(string) : là static method của **System.Type** class  và trong **Assembly**. Vậy các cách để lấy được type của **System.Type** class hay là 1 Assembly:
        - cách lấy type của **System.Type** class
            - Type : đã là type của **System.Type** class
            - Type.GetType("System.Type")
        - Cách lấy được **Assembly**
            - trong các type của bất kì class nào đều có Assembly . 
            - "".GetType().Assembly
    - **2.cách lấy contructor**
        - Type.GetConstructors() # lấy tất cả các contructor công khai
        - type.GetConstructor(một mảng các Type[] chứ các tham số)
    - **3. khởi tạo instance**
        - Activator.CreateInstance(Type target class)
        - sau khi chọn được Constructor thì gọi **invoke()** để tạo instance
    - sau khi truy cập được type của target class thì cần truy cập vào các method  VÀ thực thi chúng
        - case 1 : Instance method  (cần khởi tạo instance của class mơi gọi được)
            - tạo instance rồi sau đó gọi tên method sau đó gọi **invoke()** để thực thi
        - case 2 : static method (gọi method không cần )
            - gọi tên method thông qua type của class.
           

# Python 

**1. Phân cấp kiến trúc trong python**
- Package : thư mục chứa code 
- Module (py) : một file mã nguồn python
- Class : dùng để định nghĩa các khuôn mẫu(blueprint) để khởi tạo đối tượng 
- Attribute : bao gồm các filed , properties , method.

**2. cách xây payload**
- tư duy:
    ![image](https://hackmd.io/_uploads/BJ4TpZekzg.png)
- một vài magic method được sử dụng
    ![image](https://hackmd.io/_uploads/H15N7GgkMx.png)
- một vài chú ý về `__globals__`
    - CHỈ CÓ THỂ truy cập `__globals__` từ một HÀM (Function) hoặc PHƯƠNG THỨC (Method) được viết bằng ngôn ngữ Python thuần túy.
    - Nó không tồn tại trên
        - Object (Đối tượng): `"".__globals__ `➔ Lỗi
        - Class (Lớp): `str.__globals__` ➔ Lỗi
        - Hàm built-in (Viết bằng C): `len.__globals__`, `print.__globals__` ➔ Lỗi
    - `hàm_nào_đó.__globals__` :  Trả về một Dictionary chứa TOÀN BỘ các biến, hàm, class và các module đã được import ở cấp độ Global (Toàn cục) thuộc về cái file (module) nơi hàm đó được sinh ra.
    - truy cập vào method mà không cần khởi tạo đối tượng : `__subclasses__()[index].ten_method`
- Khi truy cập được class mục tiêu nếu muốn khởi tạo đối tượng thì chỉ cần thêm `()` ví dụ `__subclasses__()[index]()`
- **NOTE** : Nếu không thể tận dụng được các `subclass` thì mục tiêu là tryt cập vào `globals` . Khi truy cập được vào `globals` thì tìm kiếm các mục tiêu sau:
    - `__builtins__` : 
        - chỉ tồn tại ở phạm vi `Globals (file)`
        - có `__import__()` sẽ import các thư viện khác bất chấp cấu hình bị cấm
    - Các module hệ thống trực tiếp (`os`, `subprocess`)
    - Truy cập vào các model có thể bên trong đó được dev import thư viện os . 
- Truy cập vào Global thông qua các function **có sẵn** khi khởi động ứng dụng 

## PHP
-