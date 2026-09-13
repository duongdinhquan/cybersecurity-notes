[LINK](https://dreamhack.io/wargame/challenges/2684)

- mục tiêu của lab này là đọc được nội dung của file **flag.txt** . Lab này có chức năng gọi một API khác thông qua post request . Thực hiện debug code thì nhận thấy flow logic như sau : ![image](https://hackmd.io/_uploads/rkurFSod-x.png)
nội dung của  **sanitize_song_url**![image](https://hackmd.io/_uploads/SJNDtHo_-e.png)
nội dung của **safe_get** ![image](https://hackmd.io/_uploads/HyuOYBiObl.png)
    - fucntion **sanitize_song_url** thực hiện kiểm tra CẤU TRÚC và kí tự http:// hoặc https:// PHẢI CÓ trong url thì mới trả về URL nếu không sẽ trả về null
    - function safe_get có hàm file_get_contents() sử dụng để đọc nội dung của một file mà nó CHẤP NHÂN MỘT URL và nội dung trả về là body của URL đó . 
    - nếu body trả về của URL có kí tự DH{", "<" thì sẽ bị trả về Suspicious output! . Nếu giá trị trả về của URL không phải là JSON và không đủ các key ['album','artist','cover_url','duration_seconds','id','title','year'] thì sẽ bị báo Invalid data. Ngược lại thì sẽ hiển thị nó lại lên trình duyệt.
    
- ý tưởng là nhận vào một url dạng **file:///flag.txt** để nhận flag nhưng chắc chắn là không được nên cần bypass bộ lọc .
- mục tiêu là dùng một url hợp lệ + biến đổi phản hồi thành một custom-response mà lab này sử dụng **file_get_contents($url)** để đọc nội dung của url nên có thể sử dụng **PHP Stream Wrapper**  để thay đổi dữ liệu khi PHP đọc input stream đó.
- cấu trúc chuẩn của **php://filter** : `php://filter/[read=<bộ_lọc_đọc>]/[write=<bộ_lọc_ghi>]/resource=<luồng_hoặc_đường_dẫn_file>`
- để đọc được nội dung của flag.txt sẽ áp dung kĩ thuật **"PHP filter chains: file read from error-based oracle"**[chi tiết](https://www.synacktiv.com/publications/php-filter-chains-file-read-from-error-based-oracle#file-read-with-errorbased-oracle) và công cụ [php_filter_chains_oracle_exploit](https://github.com/synacktiv/php_filter_chains_oracle_exploit)
- để sử dụng công cụ này thì sẽ thực hiện brute-force để tìm ra phản hồi gây ra lỗi Memory Exhaustion trong php
- sử dụng [đoạn code sau](https://) để tìm sự khác nhau khi tạo lỗi Memory Exhausion:![image](https://hackmd.io/_uploads/HyqQ8WAdbe.png)
- nhận thấy chuối để xác định kí tự đúng : **bytes exhausted**
- lý do mà có hiện lỗi lúc runtime : ![image](https://hackmd.io/_uploads/HJmhwZ0d-g.png)

- sử dụng php_filter_chains_oracle_exploit chạy câu lệnh này để steal /flag.txt
![image](https://hackmd.io/_uploads/SJdl5ZA_bl.png)

[TÀI LIỆU ](https://www.synacktiv.com/publications/php-filter-chains-file-read-from-error-based-oracle#file-read-with-errorbased-oracle)

### Hạn chế của kĩ thuật này:
- yêu cầu các hàm PHP đọc file từ user-controlled input mà không kiểm tra chặt chẽ đường dẫn (ví dụ: file_get_contents(), include(), sha1_file(), md5_file(...), readfile(...), fopen(...) + fread(...), v.v.).
- Nếu code có kiểm tra: file_exists() / is_file() / is_readable() → không khai thác được (vì các hàm này không hỗ trợ wrapper php://filter).
- Phụ thuộc nặng vào cấu hình PHP : Cần display_errors = On hoặc lỗi memory được trả về trong response (để oracle nhận biết positive).
- memory_limit phải đủ thấp
- allow_url_fopen = On (mặc định) → nếu Off → php://filter không hoạt động.