File php.ini là fie cấu hình chung cho các cấu hình 

`grep -vE '^\s*(;|$)' php.ini > php_clean.ini`: làm sạch comment 

Tìm kiếm `[H=application/x-httpd-php]` để xem các file nào được đươc vào PHP handle.(đây là cấu hình thuộc webserve hay vHost)

Đường dẫn `/phpinfo.php` có thể được public cho nhiều thông tin về request hiện tại.


## Cấu hình ở file ini.conf
```ini

expose_php              = Off   # tắt php version ở response header
display_errors          = Off   # không hiển thị lỗi trực tiếp ra trình duyệt
log_errors              = On    # bật tính năng ghi log hệ thống
error_log               = /valid_path/PHP-logs/php_error.log    # đường dẫn file ghi log
ignore_repeated_errors  = Off   # ghi lại các lỗi lặp lại nếu xảy ra

doc_root                = /path/DocumentRoot/PHP-scripts/   # thư mục gốc chứa tệp php sẽ được thực thi
open_basedir            = /path/DocumentRoot/PHP-scripts/   # php chỉ có thể mở đọc các file trong thư mục này.
allow_url_fopen         = Off   # các hàm như file_get_contents(), fopen() không được mở url
allow_url_include       = Off   # chặn url ở các hàm include

file_uploads            = On    # cho phép upload file
upload_tmp_dir          = /path/PHP-uploads/    # cấu hình thư mục tạm khi file được upload trước khi dùng move_uploaded_file()
upload_max_filesize     = 2M    # dung lượng tối đa của một tệp tin
max_file_uploads        = 2     # số lượng file đc upload in per request.

enable_dl               = Off   # Vô hiệu hóa hàm dl() tránh load file thư viện như .so .dll
disable_functions       =       # cấm các function
disable_classes         =

 session.save_path      = /path/PHP-session/    # đường dẫn lưu file session
```
## PHP Realpath Cache
Mặc định được bật , xem cấu hình `realpath_cache_size`  và `realpath_cache_ttl` trong `php.ini`.

Document:
- https://tideways.com/profiler/blog/how-does-the-php-realpath-cache-work-and-how-to-configure-it
- https://blog.csdn.net/jrckkyy/article/details/148512052

Phân tích:
- Realpath Cache is a file path caching system built into PHP that converts relative paths into absolute paths and caches them. Ví dụ khi code kiểu `include './config.php'`  lúc này PHP kích hoạt `Realpath Cache` để chuyển nó thành absolute path
- enable Realpath Cache: ![](image/2026-09-24-22-04-37.png)
- vòng đời:
    - đầu tiên sẽ parse path và lưu trữ trong path trong cache.
    - Sau đó path lưu trong cache này sẽ được sử dụng trực tiếp nếu vẫn trong `ttl`
- Mục đích của tính năng này là lưu sẵn `abosolute path` vào cache tránh việc tính toán lặp đi lặp lại

- Cái này ảnh hướng đến việc đọc file trong khai thác , nếu 
