## lý thuyết
Khai thác để đọc thông tin nhạy cảm victim cũng tương tự `Web cache poisoning` nó cũng tận dụng cơ chế cache. Ở lỗ hổng này tận dụng sự bất đồng bộ giữa nginx(reverse proxy) với phía BE server xử lý.

ở nginx thường cấu hình các file được lưu cache là những tài nguyên tĩnh ,thiết lập các cache rules  theo các dang như đuối file , hay thư mục bắt đầu hay là file name , ....

Kịch bản: 

Cấu hình nginx cache những URL kết thúc bằng các phần mở rộng:
```
.css
.js
.png
.jpg
.ico
```

BE viết code như sau:Tất cả các endpoint bắt đầu bằng `/my-account` đều trả về `user_id`
```php
$path = $_SERVER['REQUEST_URI'];

if (strpos($path, '/my-account') === 0) {
    showAccount($_SESSION['user_id']);
}
```

khi victim truy cập  `/my-account/example.css` sẽ được lưu cache + trả về user . Sau đó kẻ tấn công chỉ cần xác định đúng key_cache rồi truy cập để xem thông tin của victim.

## Lab: Exploiting path mapping for web cache deception
Xác định được logic BE và kịch bản tương tự như demo ở phần lý thuyết.

Xác định được `cache_key = METHOD + URL`

Khai thác: `https://0a80002604e86b9a81c10289006c0027.web-security-academy.net/my-account/wcd.js` cho victim để người ta truy cập để lưu cache tiếp đó attacker truy câp lại URL này để lấy API key của carlos

## Lab: Exploiting path delimiters for web cache deception