[LINK](https://dreamhack.io/wargame/challenges/2566)

- Start:
- nhận thấy đoạn code này dễ bị SQLi vì nối chuỗi trực tiếp
```
@app.get('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('home'))
    try:
        page = int(request.args.get('page', 0))
    except Exception:
        page = 0
    try:
        keyword = request.args.get('keyword', '').strip().lower()
    except Exception:
        keyword = ''
    conn = None
    count = 0
    try:
        conn = get_conn()
        cursor = conn.cursor()
        if page < 0:
            page = 0
        size = 10
        offset = page * size
        if ("'" in keyword):        # check xem trong key có kí tự ' không
            return render_template('not_found.html') 
        if (keyword == ''):
            count = math.ceil(cursor.execute("SELECT * FROM anime") / size)
        else:
            # filter : lọc kí tự ' của keyword
            count = math.ceil(cursor.execute(f"SELECT * FROM anime WHERE LOWER(title) REGEXP '{keyword}' or LOWER(description) REGEXP '{keyword}'") / size)
        cursor.scroll(offset, mode='absolute')
        result = cursor.fetchmany(size)
    except Exception:
        return render_template('not_found.html')
    return render_template('dashboard.html', result=result, page=page, count=count, keyword=keyword)

```

- code chỉ lọc kí tự **'** trong tham số **keyword** . 

- SQL QUERY : ![image]![image](https://hackmd.io/_uploads/rkkEPLuzbe.png)

 như ảnh nếu thêm kí tự **\\**  để DBMS hiểu kí tự **'** là chuỗi thì chúng ta có thể làm cho đoạn giữa REGEXP ............. OR là một chuỗi nhưng mà do BE chặn kí tự ' nên vẫn không qua được nên cần decode nhưng DBMS vẫn hiểu: decode kí tự \\' thành : **'**
 - payload : ![image](https://hackmd.io/_uploads/BJEZCUuGZg.png)
nhưng có vẻ payload này sai syntax nên không thấy response trả về . 
- Sau thời gian tìm hiểu thì tôi thấy chơ chế của câu truy vẫn ![image](https://hackmd.io/_uploads/rJq9uZtMbe.png)
là  nó so sánh **bản mẫu** với từng row trong bảng **anime** theo như thông tin của code SQL thì bản này có 101 bản ghi nên mỗi lần so sánh nó sẽ ngủ 5s nên khi truy vẫn toàn bộ bản ghi nó sẽ ngủ 5005s ====> TIME OUT
- payload : ![image](https://hackmd.io/_uploads/Skwyi-YfZx.png)

Chúng ta thấy time response là khoảng 5000ms nên chứng tỏ payload đã thành công ^_^

- payload: ![image](https://hackmd.io/_uploads/Hyhz-rtG-g.png)
- ![image](https://hackmd.io/_uploads/HkHm-BtMWe.png), chứng tỏ password của admin là 50 kí tự 
- payload xác định password của admin:
- ![image](https://hackmd.io/_uploads/HJwxSHtzZe.png)
sử dụng intruder để bute-force password của admin
![image](https://hackmd.io/_uploads/HkP8rBKGWx.png)
nhưng chỉ nhận 1 chuỗi 50 kí tự 0 login thấy sai vì **'a'=0 thì mysql sẽ trả về true**
- giải pháp dùng ascii để convert sang số ![image](https://hackmd.io/_uploads/BJeQlqKmbg.png)
- password : **this_is_fake_admin_password_will_be_change_in_prod**
- sau khi truy cập được trang admin nhưng vẫn không thể đọc đươc file flag.txt vì lab đã thay thế **../** ![image](https://hackmd.io/_uploads/Hyfwu9F7-e.png)
- thử xem đọc được file /etc/passwd cấu hình chứa thông tin về người dùng hệ thống ![image](https://hackmd.io/_uploads/Hkc0u5FQWe.png)
- ta thấy người dùng ctf có thư mục home như hình trên . Truy cập ![image](https://hackmd.io/_uploads/r142LYcFmbx.png)



**CHÚ Ý : Cơ chế "Ép kiểu ngầm định" của MySQL**
- khi so sánh 1 chuỗi với 1 số thì **mysql** sẽ convert chuỗi sang số để so sánh , ví dụ : 123aaaa --> 123 ; anaa ----> 0
    + đối với các DBMS khác thì:
        -  PostgreSQL , Oracle : so sánh 'abbaa' = 0 thì bị ném lỗi
        -  SQL server : '1234' thì sẽ được convert sang số là 1234 , còn nếu là chuỗi 'aaaa' thì bị ném lỗi , '111aaa' ném lỗi
- thay vì biểu diễn chuỗi trong cặp nháy đơn thì có thể biểu diễn ở các hệ khác như hexa (0x....) , .....