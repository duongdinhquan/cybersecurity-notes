## University 
Cần truy cập biến môi trường để lấy flag. Build lab lên thấy trang login và không có register nên khả năng phải bypass cái này để login vào
```python
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        try:
            
            response = requests.get(
                f"http://localhost:5000/api/users/{username}/auth",
                timeout=3,
            )

            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE username=?", (username,))
            user = cursor.fetchone()
            conn.close()

            if user and user[2] == password:
                session["username"] = username
                session["session_token"] = secrets.token_hex(16)
                return redirect(url_for("dashboard"))
            elif user:
                return render_template("login.html", error="Invalid password")
            elif response.status_code == 200:
                session["username"] = username
                session["session_token"] = secrets.token_hex(16)
                return redirect(url_for("dashboard"))
            else:
                return render_template("login.html", error="User not found")
        except requests.RequestException:
            return render_template("login.html",
                                   error="Error during username validation")

    return render_template("login.html")

```

Trang login ở đây thực hiện 2 cơ chế : vừa thực hiện truy vấn db và thực hiện gọi api khác để check cridential của user . Do trong db chắc chắn không có nên chỉ có thể bypass ở gọi API. Chỉ cần API trả về `200 ok` thì sẽ login thành công
```
response = requests.get(
                f"http://localhost:5000/api/users/{username}/auth",
                timeout=3,
            )
```
Thực hiện nối chuỗi trực tiếp input của user. Ở trang web này tồi tại `/health` luôn trả về `200 OK` nên `{username}` có giá trị là `/../../../../../health#` thì thư viện `request` (thực tế là `urllib3 `) sẽ tự động chuẩn hóa url nên `URL` nên thực tế sẽ là `requests.get("http://localhost:5000/health#/auth")`.

![](image/2026-10-04-15-52-38.png)

Sau khi login thì được truyền đến trang `/dashboard` ở đây có lỗ hổng SSTI --> ở đây sử dụng để đọc flag.
```python
@app.route("/add_note", methods=["POST"])
def add_note():
    if "username" in session and "session_token" in session:
        note_content = request.form["note"]
        
        note_content = (note_content
                        .replace("'", "")
                        .replace('"', "")
                        .replace("[", "")
                        .replace("]", "")
                        .replace("request", "")
                        .replace("%", ""))

        session_token = session.get("session_token")

       
        template = Template(note_content)
        rendered_note = template.render()

        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO notes (username, note, session_token) VALUES (?, ?, ?)",
            (session["username"], rendered_note, session_token),
        )
        conn.commit()
        conn.close()
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))

```

Ở  đây nó lọc các kí tự `' , " , [ , ] , request , %` thành rỗng.

payload: `{{ lipsum.__globals__.os.environ }}`

flag: `flag{sst1_v1a_j1nj4_t3mpl4t3_3nv1r0nm3nt}`

## Identity Breach 
Flag được trả về khi login được tài khoản là admin

Khởi tạo db của chall , sử dụng `char(20)` là dạng `fix-length` không flexible giống `varchar()`
```sql
USE intelDB;

CREATE TABLE IF NOT EXISTS soldiers (
    username CHAR(20),
    password CHAR(20)
);

-- Admin với password bí mật
INSERT INTO soldiers VALUES ('admin', 'not_that_easy ;)');

```

login.php
```php
    $conn = get_db();
    $stmt = $conn->prepare("SELECT * FROM soldiers WHERE username = ? AND password = ?");
    $stmt->bind_param("ss", $username, $password);
    $stmt->execute();
    $result = $stmt->get_result();
    $user = $result->fetch_assoc();
    $conn->close();

    if ($user) {
        $_SESSION["user"] = trim($user["username"]); 
        header("Location: /account.php");
        exit;
    } else {
        $error = "Sai username hoặc password.";
    }
```
`trim($user["username"])`: cắt space 2 đầu vì dùng `char()` sẽ được thêm padding để đủ 20 kí tự

register.php
```php
        $stmt = $conn->prepare("SELECT username FROM soldiers WHERE username = ?");
        $stmt->bind_param("s", $username);
        $stmt->execute();
        $result = $stmt->get_result();

        if ($result->num_rows > 0) {
            $error = "Username đã tồn tại.";
        } else {
           
            $stmt = $conn->prepare("INSERT INTO soldiers (username, password) VALUES (?, ?)");
            $stmt->bind_param("ss", $username, $password);
            if ($stmt->execute()) {
                $success = "Đăng ký thành công! Hãy đăng nhập.";
            } else {
                $error = "Đăng ký thất bại: " . $conn->error;
            }
        }
```

Ở đây nếu đăng kí với 1 user: `admin + 15 space + kí_tự_lạ` thì điều kiện `where` sẽ false và đăng kí thành công nhưng khi `inser into` thì lại chỉ lưu `admin + 15 space` vì db được thiết kế với `char(20)` nên khi login thì sẽ có session của admin. 

Điều kiện khả thi: Mysql tắt chế độ `strict` nếu bật sẽ bị ném lõi `Data too long for column 'username'`

![](image/2026-10-05-00-01-04.png)
flag: `HACKFEST{ch4r_trunc4t10n_1s_d4ng3r0us}`



