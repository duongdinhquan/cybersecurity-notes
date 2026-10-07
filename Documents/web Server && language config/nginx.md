Cấu hình một `nginx.conf` cơ bản:
```nginxconf
user nobody; # chạy dưới quyền của user nobody
worker_processes 1;
pid /run/nginx.pid;

events {
    worker_connections 768; # xử lý đồng thời 768 connection
}

http { # khối http cấu hình chung cho Web server
    server_tokens off; # ẩn version nginx khi báo lỗi

    include /etc/nginx/mime.types; # include các file xác định content-type để trả về trình duyệt
    default_type application/octet-stream;

    proxy_cache_path /var/cache/nginx keys_zone=cache:10m max_size=1g  
inactive=60m use_temp_path=off;
    # cấu hình cache:
        # response được backend trả về lưu ở /var/cache/nginx
        # space lưu cache tên là cache
        # inactive 60m : Xóa cache nếu không ai truy vập trong 60ph

    server { # khối server cấu hình một Vhost cụ thể
        listen 1337; 
        
        server_name _;  # _ nghĩa là không match với vHost nào thì chọn cái này. 

        location ~* \.(css|js|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {# phù hợp URI
            proxy_cache cache; # bật name space tên cache đã khai báo ở trên
            proxy_cache_valid 200 3m; # status 200 ok lưu cache trong 3 phút
            proxy_cache_use_stale error timeout updating; # dùng cache cũ khi gặp lỗi or timeout
            expires 3m;
            add_header Cache-Control "public";

            proxy_pass http://unix:/tmp/gunicorn.sock;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            
        }

        location / {
            proxy_pass http://unix:/tmp/gunicorn.sock;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            
        }

        access_log /var/log/nginx/access.log; # ghi lịch sử truy cập tại đây
        error_log /var/log/nginx/error.log; # ghi lỗi tại đây
    }
}

```

Cách hoạt động của một số directive:

`location`: Tìm kiếm match với `URI`
```
Bước 1: Tìm exact match (=)
        └─ Nếu tìm thấy → DÙNG NGAY, DỪNG.

Bước 2: Tìm prefix match DÀI NHẤT (bao gồm cả ^~)
        └─ Ghi nhớ location này (gọi là "longest prefix match").

Bước 3: Nếu longest prefix match có modifier ^~
        └─ DÙNG NGAY, DỪNG. (Không kiểm tra regex nữa)

Bước 4: Duyệt qua các regex location (~ và ~*) THEO THỨ TỰ XUẤT HIỆN
        └─ Regex ĐẦU TIÊN khớp → DÙNG NGAY, DỪNG.

Bước 5: Nếu không có regex nào khớp
        └─ DÙNG longest prefix match từ Bước 2.
```

`proxy_pass`: Chuyển tiếp request đến một backend server (upstream) khác. 
```
location /api/ {
    proxy_pass http://backend;
}
location /api/ {
    proxy_pass http://backend/;
}

Là hoàn toàn khác nhau:
Công thức: URI_backend = URI_client - Prefix_location + URI_proxy_pass
    - GET /api/users thì backend sẽ nhận GET /api/users
    - GET /api/users thì backend sẽ nhận GET /users bỏ đi prefix

```

`rewrite <regex> <replacement> [flag];`: nó sẽ rewrite URI
`alias`: map giữa URI và filesystem path

`proxy_cache_key $scheme$proxy_host$request_uri;` default `key_cache ` nêu ở file cấu hình không có. 
`proxy_cache_use_stale error timeout updating;`Khi backend gặp sự cố (error, timeout) hoặc đang được cập nhật (updating), Nginx sẽ phục vụ cache CŨ (stale) thay vì trả lỗi cho client. 

LỖ HỔNG `Web Cache Deception ` thường dính ở quy tắc cache dựa trên phần mở rộng của file tĩnh