File php.ini là fie cấu hình chung cho các cấu hình 

`grep -vE '^\s*(;|$)' php.ini > php_clean.ini`: làm sạch comment 

Tìm kiếm `[H=application/x-httpd-php]` để xem các file nào được đươc vào PHP handle.

Đường dẫn `/phpinfo.php` có thể được public cho nhiều thông tin về request hiện tại.

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
