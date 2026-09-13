[LINK](https://dreamhack.io/wargame/challenges/2764)

- first , configure remote debuging
    - add debugpy into the requirements.txt file.
    - expose port 5678 in the web service
- content of nginx.conf:
```
worker_processes  1;

error_log  /var/log/nginx/error.log warn;
pid        /var/run/nginx.pid;

events { worker_connections 1024; }

http {
  underscores_in_headers on;
  ignore_invalid_headers off;

  include       /etc/nginx/mime.types;
  default_type  application/octet-stream;

  proxy_cache_path /var/cache/nginx levels=1:2 keys_zone=cdn_cache:10m max_size=100m inactive=5m use_temp_path=off;

  log_format  main  '$remote_addr - $host "$request" $status $body_bytes_sent ' 
                     '"$http_referer" "$http_user_agent" cache=$upstream_cache_status';
  access_log  /var/log/nginx/access.log main;

  sendfile        on;
  keepalive_timeout  65;

  upstream web_upstream { server web:4000; }
  upstream fetcher_upstream { server fetcher:5000; }

  server {
    listen 3000 default_server;
    server_name _;

    location / {
      proxy_pass http://web_upstream;
      proxy_set_header Host $host;
      proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
  }

  server {
    listen 3000;
    server_name data.local;

    location / {
      proxy_cache cdn_cache;
      proxy_cache_key $host$uri$is_args$args;
      proxy_cache_valid 200 302 5m;
      add_header X-Cache-Status $upstream_cache_status always;

      proxy_pass http://fetcher_upstream;
      proxy_set_header Host $host;
      proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
  }
}
```
- `underscores_in_headers on;` : allow header has character "_" , default it is ignored
- `ignore_invalid_headers off` : alllow all header
- `  upstream web_upstream { server web:4000; }
  upstream fetcher_upstream { server fetcher:5000; }` . hese upstreams point to two backend Docker containers: the web container on port 4000 and the fetcher container on port 5000.
- `listen 3000 default_server;` Because it is configured as the **default_server** , any request with unrecognized **host** header will back to this container
- ` proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;` : `$proxy_add_x_forwarded_for = $http_x_forwarded_for + ", " + $remote_addr`
- `proxy_cache cdn_cache;
      proxy_cache_key $host$uri$is_args$args;
      proxy_cache_valid 200 302 5m;
      add_header X-Cache-Status $upstream_cache_status always;` : Caching is enabled for this route . Responses with status codes 200 and 302 are cached for 5 minutes . The server appens the **X-Cache-Status** header in response . the value will be **MISS** for un-cached requests and **HIT** when serving from the cache
- word flow : ![image](https://hackmd.io/_uploads/r1zrNOIo-g.png)
- Because the database always hardcodes the admin value to false, we must manipulate the fetch bot to make a request under our control.
- `CTRL_RE = re.compile(rb'[\x00-\x1f\x7f]+')`
- ![image](https://hackmd.io/_uploads/BJG_RPLs-x.png)
- `name_clean = CTRL_RE.sub(b"", name)` : It replaces the matched characters with the name variable
- Due to the inconsistency in how fetch and Nginx parse the Host header, we can successfully perform Cache Poisoning.
- make malicious server:![image](https://hackmd.io/_uploads/HySvLoUsWg.png)

PAYLOAD :+1: ![image](https://hackmd.io/_uploads/rkCrl6Ij-e.png)
![image](https://hackmd.io/_uploads/HyIPe6LsZe.png)