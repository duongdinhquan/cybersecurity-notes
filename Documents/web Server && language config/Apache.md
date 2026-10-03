## apache2.conf
Trong Apache thì file `apache2.conf` là filecấu hình chính (main configuration file) của Apache.

Làm sạch file khỏi comment: `grep -vE '^\s*(#|$)' apache2.conf > apache2_clean.conf`
Ví dụ:
```DefaultRuntimeDir ${APACHE_RUN_DIR}
PidFile ${APACHE_PID_FILE}
Timeout 300
KeepAlive On
MaxKeepAliveRequests 100
KeepAliveTimeout 5
User ${APACHE_RUN_USER}
Group ${APACHE_RUN_GROUP}
HostnameLookups Off
ErrorLog ${APACHE_LOG_DIR}/error.log
LogLevel warn
IncludeOptional mods-enabled/*.load
IncludeOptional mods-enabled/*.conf
Include ports.conf
<Directory />
        Options FollowSymLinks
        AllowOverride None
        Require all denied
</Directory>
<Directory /usr/share>
        AllowOverride None
        Require all granted
</Directory>
<Directory /var/www/>
        Options Indexes FollowSymLinks
        AllowOverride None
        Require all granted
</Directory>
<Directory /tmp>
        AllowOverride None
        Require all granted
</Directory>
Alias /images/ /tmp/
AccessFileName .htaccess
<FilesMatch "^\.ht">
        Require all denied
</FilesMatch>
<FilesMatch ".*flag.*">
        Require all denied
</FilesMatch>
LogFormat "%v:%p %h %l %u %t \"%r\" %>s %O \"%{Referer}i\" \"%{User-Agent}i\"" vhost_combined
LogFormat "%h %l %u %t \"%r\" %>s %O \"%{Referer}i\" \"%{User-Agent}i\"" combined
LogFormat "%h %l %u %t \"%r\" %>s %O" common
LogFormat "%{Referer}i -> %U" referer
LogFormat "%{User-agent}i" agent
IncludeOptional conf-enabled/*.conf
IncludeOptional sites-enabled/*.conf

```

Một số cấu hình cần chú ý:
```
<FilesMatch "REGEX">
    Require all denied
</FilesMatch>
```
`<FilesMatch>`: để áp dụng rule dựa trên tên file

`Require all denied`: cấm truy cập , sẽ bị trả `403 Forbidden`

```
<Directory tên_thư_mục>
    AllowOverride None
    Require all granted
</Directory>
```
`<Directory>`: cấu hình quyền của Apache đối với thư mục

`AllowOverride None`: Không cho phép `.htaccess` trong thư mục

`Require all granted`: Cho phép Apache phục vụ các tài nguyên trong thư mục cho client

```
Alias /đường_dẫn_url /thư_mục
```
ánh xạ URL /đường_dẫn_url trực tiếp vào /thư_mục






##v 000-default.conf
Trên Ubuntu/Debian: `/etc/apache2/sites-available/000-default.conf` , file cấu hình Vhost
```
<VirtualHost *:80>

        ServerAdmin webmaster@localhost
        DocumentRoot /var/www/html
        RewriteEngine On
        RewriteRule  ^(.+\.php)$  $1  [H=application/x-httpd-php]
        LogLevel trace8

        ErrorLog ${APACHE_LOG_DIR}/error.log
        CustomLog ${APACHE_LOG_DIR}/access.log combined

</VirtualHost>

```
thiết lập và quản lý cách Apache phục vụ một trang web cụ thể trên máy chủ.

## Config Directives in Apache HTTP Server
**1. Xử lý yêu cầu (Handlers & Types)**

`SetHandler`: ép toàn bộ các file trong thư mục trên os được xử lý bởi handler cụ thể

`AddHandler handler-name extension [extension]`: mapping extension nhất định đến một handler

`AddType media-type extension [extension]`
```
AddHandler application/x-httpd-php .php
→ set r->handler.

AddType application/x-httpd-php .php
→ set r->content_type, không set r->handler.
``
Cả 2 cái trên đều có thể sử dụng thay thế cho nhau 

`RewriteRule regex substitution`: thuộc  module `mod_rewrite` trong Apache. URL do user nhập qua trình duyệt nếu match với regex này thì sẽ được chuyển thành substitution này và substitution vẫn là một URL-path. 