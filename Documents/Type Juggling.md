## PHP
### reference
https://www.php.cn/faq/1435869.html

https://blog.csdn.net/gitblog_00941/article/details/166897981

https://berlinonline.github.io/php-introduction/chapters/type_juggling/


### Phân tích
So sánh một chuỗi `Scientific Notation` ứng dụng trong bypass Cookies.

Điều kiện: chuỗi dạng `/^0e\d+$/` or `/^00e\d+$/` thì nếu sử dụng so sánh lỏng lẻo thì sẽ hoạt động như sau:

1. Chuỗi được convert sang số: $$0 \times 10^{x} = 0.0 \quad (\text{với mọi } x > 0)$$
2. khi đó phép so sánh sẽ thành `0.0 = 0.0` sẽ trả về `True` 

| **Biểu thức so sánh** | **PHP 5.x** | **PHP 7.x** | **PHP 8.x** | **Cơ chế hoạt động & Lý do khác biệt giữa các phiên bản** |
|---|---:|---:|---:|---|
| `'0010e2' == '1e3'` | `true` | `true` | `true` | Cả hai đều là chuỗi số khoa học hợp lệ, tự động ép về số thực: `10 × 10² = 1000` và `1 × 10³ = 1000` → `1000.0 == 1000.0`. |
| `"0e123..." == "0e456..."` | `true` | `true` | `true` | **Magic Hash chuẩn (`0e\d+`)**. Cả hai chuỗi đều có dạng số khoa học và được ép về số thực: `0 × 10^x = 0.0` → `0.0 == 0.0`. |
| `'0x01' == 1` | `true` | `false` | `false` | **PHP 5:** Nhận diện chuỗi `0x...` là số Hex và ép thành số `1`.<br>**PHP 7+:** Loại bỏ cơ chế tự động parse chuỗi Hex trong phép so sánh lỏng, coi `'0x01'` là chuỗi thông thường. |
| `'0x1234Ab' == '1193131'` | `true` | `false` | `false` | **PHP 5:** Chuyển đổi mã Hex `0x1234Ab` thành số thập phân `1,193,131`.<br>**PHP 7+:** Coi đây là hai chuỗi ký tự khác nhau. |
| `'0xABCdef' == ' 0xABCdef'` | `true` | `false` | `false` | **PHP 5:** Cắt khoảng trắng đầu chuỗi và ép cả hai về cùng giá trị số Hex.<br>**PHP 7+:** So sánh chuỗi ký tự thông thường nên khoảng trắng đầu chuỗi làm hai chuỗi khác nhau. |
| `'123' == 123` | `true` | `true` | `true` | Chuỗi thuần số (**numeric string**), mọi phiên bản đều ép về số nguyên `123` → `123 == 123`. |
| `'123a' == 123` | `true` | `true` | `false` | **PHP 5/7:** Trích xuất phần số hợp lệ ở đầu chuỗi (`'123'`), bỏ qua chữ `'a'`.<br>**PHP 8:** Chuỗi chứa ký tự chữ không còn được coi là numeric string hợp lệ → PHP 8 chuyển số `123` thành chuỗi `'123'` → so sánh `'123a' == '123'` → `false`. |
| `'abc' == 0` | `true` | `true` | `false` | **PHP 5/7:** Chuỗi không có số ở đầu bị ép về số nguyên `0` → `0 == 0`.<br>**PHP 8:** Ép số `0` thành chuỗi `'0'` → so sánh `'abc' == '0'` → `false`. |
| `'' == 0` | `true` | `true` | `false` | **PHP 5/7:** Chuỗi rỗng `''` bị ép về số `0`.<br>**PHP 8:** Ép số `0` thành chuỗi `'0'` → so sánh `'' == '0'` → `false`. |
| `0 == false` | `true` | `true` | `true` | Số `0` được đánh giá là **falsy** khi chuyển đổi sang Boolean → `false == false`. |
| `false == NULL` | `true` | `true` | `true` | Cả `false` và `NULL` đều thuộc nhóm giá trị được xem là tương đương trong phép so sánh lỏng. |
| `NULL == ''` | `true` | `true` | `true` | `NULL` khi được chuyển đổi sang chuỗi sẽ trở thành chuỗi rỗng `""`. |
| `NULL == 0` | `true` | `true` | `false` | **PHP 5/7:** `NULL` bị ép thành số nguyên `0` → `NULL == 0` là `true`.<br>**PHP 8:** Thay đổi quy tắc so sánh → `NULL` không còn bằng `0`. |




| **Biểu thức** | **PHP 5.x / 7.x** | **PHP 8.x** | **Ý nghĩa bảo mật** |
|---|---|---|---|
| `strcmp($_POST['pass'], $secret) == 0`<br>*(khi truyền `pass[]=`)* | **Bypass thành công**<br><br>`strcmp()` nhận mảng thay vì string và trong các phiên bản cũ có thể trả về `NULL` kèm cảnh báo. Sau đó:<br>`NULL == 0` → `true`. | **Chặn đứng**<br><br>PHP 8 ném `TypeError` khi `strcmp()` nhận kiểu dữ liệu không hợp lệ (array thay vì string), khiến phép so sánh không được thực hiện. | Trên PHP 8, kỹ thuật truyền tham số dạng mảng (`pass[]=`) không còn có thể lợi dụng để ép `strcmp()` trả về `NULL`, sau đó dùng loose comparison để bypass. |
| `md5([])` | Trả về `NULL` kèm `Warning` trên các phiên bản cũ. | Ném `TypeError`. | Triệt tiêu khả năng truyền array để ép hàm hash trả về `NULL`, sau đó lợi dụng loose comparison với chuỗi rỗng hoặc `0`. |
| `sha1([])` | Trả về `NULL` kèm `Warning` trên các phiên bản cũ. | Ném `TypeError`. | Tương tự `md5([])`: PHP 8 ngăn việc truyền array vào hàm hash để tạo ra giá trị `NULL` ngoài dự kiến. |


`PHP5 - PHP7`: Các chuỗi bắt đầu bằng `0x...` không còn được xem là số. Kỹ thuật lợi dụng mã Hex để bypass so sánh lỏng chỉ khả thi trên` PHP 5`.
 
`PHP7` : Khi so sánh `number` với `string` thì `string` được chuyển sang `number`
`PHP8` : Khi so sánh `number` với `string` thì `number` được chuyển sang `string`
### Một số hàm có thể bị bypass


`strcmp($string1 , $string2)` so sánh 2 chuỗi nếu bằng nhau trả về `0`. Đối với version `PHP 7.x` thì nếu so sánh một mảng rỗng `[]` với `string` hàm này sẽ phát tra `Warning` và trả về `NULL` nếu sử dụng sử dụng so sánh lỏng lẻo thì sẽ bị bypasss
```php
if($_GET['login'] === "1"){
    if (strcmp($_POST['username'], "admin") == 0 && strcmp($_POST['password'], $pass) == 0) {
        echo "Welcome! </br> Go to the <a href=\"dashboard.php\">dashboard</a>";
    }
}
```

`md5()` / `sha1()`: version `PHP 7.x`hai hàm này khi nhận vào một mảng rỗng thì sẽ phát tra `Warning` và trả về `NULL` . Kết hợp với ` Magic Hash` và `loose comparison` thì chúng sẽ bằng nhau
```
md5([]) ==> NUll ==> so sánh lỏng lẻo với chuỗi /^0e\d+$/ or /^00e\d+$/ thì sẽ trả về true có thẻ là bypass
```

`in_array(value, array, strict=false)`: default là false nên cho phép so sánh lỏng lẻo. Nên chú ý cách so sảnh lỏng lẻo ở version PHP `7.x` và `8.x`. 

`array_search(value, array, strict=flase)`: search an array for a value and returns the key.

`switch .... case ...`: mặc định có so sánh lỏng lẻo

`empty()`: Trả về `True` khi nó là `falsy` gồm: `false , 0 , 0.0 , "" , "0" , [] , array() , null`

