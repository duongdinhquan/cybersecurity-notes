## Sửa lỗi DNS trên máy ảo
mới VMWARE bằng quyền root 
edit (thanh trên cùng của vmware) ---> Virtual Network Editor...  ---> restore default

## 1. PYTHON
Flask python
B1 : 	Chỉnh sửa file Dockerfile
![image](https://hackmd.io/_uploads/r1fpNrxKZg.png)

![image](https://hackmd.io/_uploads/ByB1HBeK-g.png)


```
FROM python:3.8
RUN pip install flask
RUN pip install debugpy # add this

COPY ./src /app

WORKDIR /app
# CMD ["python","app.py"]
CMD ["python", "-m" , "debugpy", "--listen", "0.0.0.0:5678", "app.py"] # add this

```
        
	
  

B2:	Chỉnh sửa file docker-compose.yml
![image](https://hackmd.io/_uploads/rJICzDYdbe.png)

		- "5678:5678" # Thêm dòng này: Mở cổng Debug cho VS Code
B3:	Ở vscode
 Cấu hình VS Code (Tạo file launch.json)VS Code cần biết phải kết nối đến đâu để bắt tín hiệu debug.Trong VS Code, bấm sang tab Run and Debug (biểu tượng con bọ ở thanh bên trái) $\rightarrow$ Nhấp vào create a launch.json file.Chọn Python Debugger $\rightarrow$ Chọn Remote Attach.
 
![image](https://hackmd.io/_uploads/ByzVISgFbg.png)

 
 
 ## 2. PHP thuần
 
 1. Chỉnh sửa Dockerfile
 - thêm các câu lệnh sau để cài **Xdebug**
```
RUN pecl install xdebug \
    && docker-php-ext-enable xdebug \
    && echo "xdebug.mode=debug" >> /usr/local/etc/php/conf.d/docker-php-ext-xdebug.ini \
    && echo "xdebug.start_with_request=yes" >> /usr/local/etc/php/conf.d/docker-php-ext-xdebug.ini \
    && echo "xdebug.client_host=192.168.6.1" >> /usr/local/etc/php/conf.d/docker-php-ext-xdebug.ini \
    && echo "xdebug.client_port=9003" >> /usr/local/etc/php/conf.d/docker-php-ext-xdebug.ini
```

![image](https://hackmd.io/_uploads/S19nqbo_be.png)
- 192.168.6.1 : địa chỉ ip của máy thực hiện remote debug 
- 9003 : là port mà IDE của máy debug sẽ lắng nghe để debug 

2. Chỉnh sửa docker-compose.yaml
 - thêm lệnh ![image](https://hackmd.io/_uploads/r1p1dxsd-x.png)
ở dịch vụ web
```
version: "3.9"

services:
  app:
    build: ./deploy/
    ports:
      - "8585:80"
    extra_hosts:
      - "host.docker.internal:host-gateway"
```

3. trên vscodoe
- thêm phần được in đậm này vào :![image](https://hackmd.io/_uploads/Skpails_We.png)
    - "/var/www/html": là nới chưa mã nguồn của web trong container
    - vế phải lại là nới chứa mã nguồn trên vscode
```
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Listen for Xdebug",
      "type": "php",
      "request": "launch",
      "port": 9003,
      "pathMappings": {
        "/var/www/html": "${workspaceFolder}/deploy/web/src"
      }
    }
  ]
}
```

## 3. JAVA SPRING BOOT TRÊN IntelliJ IDEA 2025.1.2

- ở docker-compose mở thêm một port để remote  debug . Sau đó tạo một biến môi trường có nội dung như sau:
```
JAVA_TOOL_OPTIONS: "-agentlib:jdwp=transport=dt_socket,server=y,suspend=n,address=*:5005"
```
với 5005 là port được mở 

- ở IntelliJ IDEA 2025.1.2 : 

## 4. ASP.NET 
1. Trong file Dockerfile
- Sửa Dockerfile để cài debugger (vsdbg)
```
# 👉 CÀI DEBUGGER
RUN apt-get update \
	&& apt-get install -y --no-install-recommends curl unzip procps \
	&& rm -rf /var/lib/apt/lists/* \
	&& curl -sSL https://aka.ms/getvsdbgsh | bash /dev/stdin -v latest -l /vsdbg
```

2. Câu hình  VSCODE **(quan trọng)**


- nội dung full:
```
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Attach ASP.NET in Docker via SSH",
      "type": "coreclr",
      "request": "attach",
      "processId": "1",
      "justMyCode": false,
      "pipeTransport": {
        "pipeProgram": "ssh",
        "pipeArgs": [
          "root@192.168.111.128",
          "docker",
          "exec",
          "-i",
          "qlsv-api"
        ],
        "debuggerPath": "/vsdbg/vsdbg",
        "quoteArgs": false
      },
      "sourceFileMap": {
        "/app": "${workspaceFolder}"
      }
    }
  ]
}
```

chú ý:
```
"pipeArgs": [
          "root@192.168.111.128",
          "docker",
          "exec",
          "-i",
          "qlsv-api"
        ]
```
- qlsv-api : bắt buộc là **container_name** của dịch vụ web 
```
processId": "1"
```
- bắt buộc là process chạy app trong container . Xác định bằng `docker exec -it qlsv-api ps aux`

```
"/app": "${workspaceFolder}"
```
- **/app** : là WORKDIR trong Dockerfile `WORKDIR /app`


## 5 Node.js
**bản chất là chạy node với inspector**
- **docker-compose.yaml**
    - thêm dòng code sau :
```
    ports:     
         - "9229:9229"
    command: ["node", "--inspect=0.0.0.0:9229", "app.js"]

```
- cách thay thế nếu ở docker-compose.yaml không có command ở `dockerfile` nếu ở
```
CMD ["node", "--inspect=0.0.0.0:9229", "app.js"]
```
- app.js là entry point của lab , nhìn vào file **package.json** để xác định , 
```
"scripts": {
  "start": "node app.js"
}
# đôi lúc được khai báo ở main
"main": "app.js"
```
Tổng quan file docker-compose.yml sẽ như thế này:
![image](https://hackmd.io/_uploads/HJyCH7CaZe.png)

- **trong case lab được chạy bằng npm**
    - thực chất là câu sẽ gọi : `node app.js`
    - sửa script trong `package.json`:
```
{
  "scripts": {
    "start": "node app.js",
    "debug": "node --inspect=0.0.0.0:9229 app.js" # thêm ở đây
  }
}
```
- dockerfile hay docker-compose : `CMD ["npm", "run", "debug"]`
![image](https://hackmd.io/_uploads/B1Tqdwqxzg.png)
- **case supervisord**
    - sửa supervisord.conf như sau
```
[supervisord]
nodaemon=true

[program:nginx]
command=nginx -g "daemon off;"
autostart=true
autorestart=true
stdout_logfile=/dev/stdout
stderr_logfile=/dev/stderr

[program:app]
directory=/app
command=node --inspect=0.0.0.0:9229 server.js   # thêm ở đây
autostart=true
autorestart=true
stdout_logfile=/dev/stdout
stderr_logfile=/dev/stderr
```
`docker-compose.yml` map port debug:
```
services:
  app:
    ports:
      - "8080:8080"
      - "0.0.0.0:9229:9229"
```
- trên vscode
```
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Attach to Docker Node",
      "type": "node",
      "request": "attach",
      "address": "192.168.x.x", 
      "port": 9229,
      "localRoot": "${workspaceFolder}/src",
      "remoteRoot": "/app/src",
      "protocol": "inspector"
    }
  ]
}
```