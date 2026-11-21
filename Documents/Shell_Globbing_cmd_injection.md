## reference
https://blog.csdn.net/FL1768317420/article/details/141006014

https://compenv.phys.ethz.ch/linux/basics_1/52_shell_globbing/

https://compenv.phys.ethz.ch/linux/basics_1/51_posix_regular_expressions/

https://github.com/micromatch/posix-character-classes

https://www.regular-expressions.info/posixbrackets.html

https://unix.stackexchange.com/questions/463198/search-for-special-characters-using-grep

## Phân tích

`${IFS}` để thay thế space

`~`:thay thế bằng đường dẫn thư mục home

`?`: khớp bất kì 1 kí tự trong file

`*`: Khớp 0 hoặc nhiều ký tự trong một đường dẫn

`+`: khớp 1 hoặc nhiều kí tự 

`[abc]`: Khớp 1 ký tự thuộc tập cho trước

`{a,b}`: sinh ra nhiều chuỗi

`$VAR, ${VAR}`: Lấy hoặc biến đổi giá trị biến

`$(command)`: Thay bằng kết quả stdout của lệnh

`$((expression))`: Tính toán số học

`@(pattern1|pattern2)`: khớp đúng một trong các pattern được liệt kê

`!(pattern)`: phủ định một pattern


## POSIX Character Classes

| POSIX Class | Biểu thức tương đương (ASCII) | Ý nghĩa |
|---|---|---|
| `[:alnum:]` | `[A-Za-z0-9]` | Chữ cái viết hoa, viết thường và chữ số |
| `[:alpha:]` | `[A-Za-z]` | Chữ cái viết hoa và viết thường |
| `[:ascii:]` | `[\x00-\x7F]` | Tất cả ký tự thuộc bảng mã ASCII |
| `[:blank:]` | `[ \t]` | Dấu cách (space) và tab ngang |
| `[:cntrl:]` | `[\x00-\x1F\x7F]` | Các ký tự điều khiển |
| `[:digit:]` | `[0-9]` | Các chữ số từ 0 đến 9 |
| `[:graph:]` | `[^ [:cntrl:]]` | Ký tự hiển thị được, không bao gồm khoảng trắng và ký tự điều khiển |
| `[:lower:]` | `[a-z]` | Chữ cái viết thường |
| `[:print:]` | `[[:graph:] ]` | Ký tự có thể in, bao gồm cả dấu cách |
| `[:punct:]` | `[\x21-\x2F\x3A-\x40\x5B-\x60\x7B-\x7E]` | Các dấu câu và ký hiệu đặc biệt, không bao gồm chữ cái và chữ số |
| `[:space:]` | `[ \t\n\r\f\v]` | Ký tự khoảng trắng: space, tab, xuống dòng, carriage return, form feed và vertical tab |
| `[:upper:]` | `[A-Z]` | Chữ cái viết hoa |
| `[:word:]` | `[A-Za-z0-9_]` | Chữ cái, chữ số và dấu gạch dưới |
| `[:xdigit:]` | `[0-9A-Fa-f]` | Chữ số hệ thập lục phân (0–9, A–F, a–f) |