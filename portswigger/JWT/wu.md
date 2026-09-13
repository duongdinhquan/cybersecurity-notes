## lý thuyết
- một vài kiểu khóa (hệ mật) cần biết
    + RSA : Nó sử dụng một cặp 
khóa gồm khóa công khai và khóa riêng để mã hóa và giải mã thông điệp . Các bước xác định cặp khóa công khai và khóa riêng:
![image](https://hackmd.io/_uploads/SJVCsbG3xl.png)
    khóa riêng (n,d) dùng để sign token còn (n,e) để xác thực token
    + hướng dẫn convert public key (PEM) to secret 
    có thể lấy nguyên nội dung của file PEM or mỗi nội dung key (cần test từng case) or lấy nguyên nội dung của base64 trong file PEM mà không cần encode base64 gì hết: ![image](https://hackmd.io/_uploads/SJ66AFBnle.png)

  

## Một vài case
- không xác thực signature <không có alg or có như không:))>
- không sign token
- sử dụng secret mặc định của một số libraries một số secrets ở [đây1](https://github.com/wallarm/jwt-secrets/blob/master/jwt.secrets.list) <brute force>
- trong JWT header ngoài **alg** đôi lúc vẫn còn một số header khác :+1: 
    + jwk : nơi để public_key
    + jku : có url trỏ đến một file chứa nhiều JWK <cái dùng để xác thực>
    + kid : một chuỗi (ID) để đánh dấu khóa dùng để ký token. Khi có nhiều khóa, kid giúp validator chọn đúng khóa nhanh mà không phải thử toàn bộ. Đôi lúc **kid có thể được chỉ định giá trị đường dẫn trỏ đến tệp chứa thông tin khóa xác minh.-**
- BE dựa vào các header filed này để verify token
    cả 3 paramater is user-controllable , **check xem BE có hỗ trợ các trường này không**
- BE không có white_list public_key để verified token của FE gửi lên (vd dùng alg: HS256 , )
- BE tin tưởng hoàn toàn vào alg header để verified JWT token , lỗi logic sử dụng public_key của (RS256) làm secret của (HS256) ,,....
- dùng public key để verify cho HS256 
- Một số thư viện không thực hiện chỉ cung cấp một method cho việc verify signature như:
    + jwt.verify(token , key) trong nodejs : nó đọc alg header từ token và verify theo nó
    + jwt.decode(token , key , algorithms="auto") : để alg là auto thì cũng tương tự như trong nodejs
    + **một số cách xác định public_key**
        - để lộ thông qua một số standard endpoint : như /jwks.json , /.well-known/jwks.json , 
        - no standard endpoint : /jwks, /keys, or /auth/jwks , ... (custom endpoint)
        - dùng tool **Dirsearch** :  công cụ dò quét đường dẫn file 
        - command : sudo docker run --rm -it portswigger/sig2n <token 1> <token 2>
- An algorithm confusion attack generally involves the following high-level steps:
- Performing an algorithm confusion attack
Obtain the server's public key

Convert the public key to a suitable format (**QUAN TRỌNG**)

Create a malicious JWT with a modified payload and the alg header set to HS256.

Sign the token with HS256, using the public key as the secret.
- một vài case mà BE xử lý public key
    + PEM nguyên mẫu:
    + Base64-encoded PEM:
    + Phần Base64 bên trong PEM
    + Dùng trường n của jwk
    + dùng full nội dung của jwk
     
    
## Lab: JWT authentication bypass via unverified signature
![image](https://hackmd.io/_uploads/ByDguNz3gx.png)

- Solution:
    
    - bắt request đến enpoit /myacount : ![image](https://hackmd.io/_uploads/Bk_h6Nf3gx.png)
nhận thấy session dạng jwt token, thông tin về token ![image](https://hackmd.io/_uploads/S1CJCVGnll.png)
dùng RS256 để sign và verify jwt token . 
- thay sub : một trong các gias trị ["administrator" , "admin" , "1" , "0" , "ADMIN__" , ....] và thử sign lại một token khác gửi lên BE thì nhận thấy trả về trang của admin.
- giữ nguyên jwt token của admin và truy cập và endpoint :"/admin/delete?username=carlos " để xóa carlos
    
- mô tả lỗi : BE không verify jwt token mà đọc luôn payload of jwt token để authenticate 

## Lab: JWT authentication bypass via flawed signature verification
    
- Solution:
    - thông tin về jwt token : 
    

![image](https://hackmd.io/_uploads/BJXE5UG3gl.png)
    nhận thấy nếu thay đổi wiener bằng administrator thì bị verify nhưng nếu để alg:"none" thì thấy BE vẫn nhận token và không verify . Có vẻ BE dựa vài alg header để xác thực việc co verify hay không?
    - để alg:"none" và sub:"administrator" thì thấy truy cập được trang admin , để xóa user thì truy cập endpoint "/admin/delete?username=carlos"
    - lỗ hổng : không xác thực alg header 
    - mô tả code : <code nhưng nếu k có singature đều bị ném lỗi:)))>
    
    
## Lab: JWT authentication bypass via weak signing key
![image](https://hackmd.io/_uploads/S1XzAFm2gx.png)

- Solution:
    - thông tin về jwt token ![image](https://hackmd.io/_uploads/ryLf15Xhel.png). để bypass đực cần biết được secret_key mà BE sử dụng để tạo signature . một số devoloper sử dụng luôn secret_key default của library để code nên có thể brute-force
    - cách 1 : dùng hashcat để bute-force
        + tạo một file word_list gồm các secret_key mà BE dùng để kí
        + hashcat -h thông tin cách dùng
        + -m 16500 là model jwt 
        + -a 3 là loại tấn công : brute force
        + command : hashcat -a 3 -m 16500 <jwt_token> /home/ddq/list.txt
        + thấy secret là : **secret1**
        + tạo token dựa trên secret ở [đây](https://jwt.io/)
        +token : **eyJraWQiOiI3NmFjODBkOC0yMzA3LTQ5OWUtYmMxNC1iMGE1N2E1Y2E2M2QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJwb3J0c3dpZ2dlciIsImV4IjoxNzU4ODc1Mzc5LCJzdWIiOiJhZG1pbmlzdHJhdG9yIn0.o3AhCCwPRKlkgo9t9OiIzoJLUHgx7HUzSO8i9z8Kd-U
**    
        + tạo token dựa trên JWT Editor  , chỉ định key : secret1 và tạo 
    
    
    - cách 2: code python tìm secret của BE : ![image](https://hackmd.io/_uploads/SJU1HAm2le.png)
    
- code lỗi :+1: 
    ![image](https://hackmd.io/_uploads/Byptr0Xhgg.png)

## Lab: JWT authentication bypass via jwk header injection
    
![image](https://hackmd.io/_uploads/B1yhBA7hel.png)

- Solution
    - thông tin về jwt token : ![image](https://hackmd.io/_uploads/S1SIvyEhex.png) nhận thấy alg:"RS256" thuật toán kí RS256 , **kid** field là id của key
    - inject header {
    "kid": "848fee41-fdd6-4f5f-94a9-a2c449d96478",
    "typ": "JWT",
    "alg": "RS256",
    "jwk": {
        "kty": "RSA",
        "e": "AQAB",
        "kid": "848fee41-fdd6-4f5f-94a9-a2c449d96478",
        "n": "rWC_We9lpqMTi_V9Nl82HB7BqLesTShQVz2J1ak1P83Ee4hx5IjlxMhC9bngrQVbBtx7YVvH83TFnvh4fGcTHtVY15SlhjC1c__W4ASqtvQin-D6Z8fP9CTGCYwHLHUW_M2o0DI_inYbpmO7JG2C20edfn8CZ6z46Nj0pZufgU0"
    }
}
    nhận thấy vân bypass được verifer của BE , chứng tỏ BE lấy cặp public_key từ token và verify 
    
- mô tả code lỗi : ![image](https://hackmd.io/_uploads/SJntNGN3el.png)
    cần dùng public key do chính BE tạo ra hoặc có white_list public key
    

    
## Lab: JWT authentication bypass via jku header injection
![image](https://hackmd.io/_uploads/r1-b8zNhel.png)
    
- Solution
 - như mô tả thây BE support cho jwk header , chèn jwk header vào payload với url chỉ đến server của burp ![image](https://hackmd.io/_uploads/HyjEhmVhlx.png)
    nhận thây có request đến server![image](https://hackmd.io/_uploads/HJnr3Q43xx.png)
- setup server
    {
  "keys": [
    {
    "kty": "RSA",
    "e": "AQAB",
    "kid": "hhe",
    "n": "58jMtiyTrkooE5TSvqAOXlOy6OszlUqY2WuJJqsrRHorTtgpPE4ZUL-Uz9loIJvc765-yl05MPJVVS_vx_wNAa3WJ1XvmErwUHAbVRsIHYEFNDR6l4X5lVTEhBUqTYYZb9laW0eIIqLUdmZt_LvNuQZXzbsz18UjPeUehEHS21Xi4AFvZ5h-60EQn3bLOEbQ3EG7mGQ4dcAiT2I35I_dzm_c9FE3FQMthPB8MDU3kAIDcwWzfurE8GwReeGcf2PuVMA0VoMP1c_4YKBYzGUFqlvg3qc5WG2CVFAGeDccPdyJsGg2E289ZECsvaRyw8ksLtpeZYSwcAUssSUeEOJXKw"
}
  ]
}

để ý "kid" phải trùng nhau
    thấy trả về 200ok 
    
truy cập endpoint để xóa user
    
    
## Lab: JWT authentication bypass via kid header path traversal
![image](https://hackmd.io/_uploads/HJEnX44hge.png)

- Solution:
    ![image](https://hackmd.io/_uploads/SJ30a4V2xx.png)

    - theo như mô tả để bài thì path traveral thì chỉ xảy ra khi đọc file , "kid" thường chứa nội dung key của secret_key mà BE dùng để sign và verify . đôi lúc thì nó còn chứa đường dấn tới một file chứa nội dung
    - trên linux có **/dev/null** là một tệp tin rỗng tồn tại hầu hết 
    - Tạo mới một Symmetric Key, với giá trị là null byte (AA== là dạng base64 encode của null byte)![image](https://hackmd.io/_uploads/B1WbkB4hge.png)
    - làm tương tự như những lab trên
    
    
## Lab: JWT authentication bypass via algorithm confusion
![image](https://hackmd.io/_uploads/SypwWSV3ex.png)
- Solution:
    - jwt gốc: ![image](https://hackmd.io/_uploads/HkLRQH4hex.png)
    dùng RS256 
    - truy cập một số standard endpoint có thể expose public_key như :/jwks.json , /.well-known/jwks.json và nhận được public_key :![image](https://hackmd.io/_uploads/Hk42JYH3gl.png)theo format JWK 

    - như mô tả của lab thì bị dính algorithm confusion thì case có thể dính là do BE verify dựa trên alg header of token . 
    - BE lưu public_key theo dạng file PEM
    - hướng dẫn convert : ![image](https://hackmd.io/_uploads/SJ66AFBnle.png)

## Lab: JWT authentication bypass via algorithm confusion with no exposed key
![image](https://hackmd.io/_uploads/HJKWJ9B3xe.png)
- Solution:
    



