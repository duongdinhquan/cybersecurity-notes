- after searching , i found the flag stored in db . it was past of the admin's blog , which was password-protected.
- the request was capturedd.
![image](https://hackmd.io/_uploads/Byd0w1QKzx.png)

- source code analysis
```
app.post('/article/:id', async (req, res) => {
  const id = req.params.id;
  const { password } = req.body;

  const q = 'SELECT id, title, author, content FROM articles WHERE id = ? AND is_private = 1 AND password = ? LIMIT 1';
  try {
    const rows = await dbQuery(q, [id, password]);
    if (!rows || rows.length === 0) {
      const metaQ = 'SELECT id, title, author FROM articles WHERE id = ? LIMIT 1';
      const metaRows = await dbQuery(metaQ, [id]);
      const meta = (metaRows && metaRows[0]) ? metaRows[0] : { id, title: 'Unknown', author: '' };
      return res.render('article', { article: meta, showPasswordForm: true, error: 'Wrong Password.' });
    }

    const article = rows[0];
    const contentHtml = escapeAndFormat(article.content);
    return res.render('article', { article: { id: article.id, title: article.title, author: article.author, contentHtml }, showPasswordForm: false, error: null });
  } catch (err) {
    console.error('Error verifying password:', err);
    res.status(500).send('Server error');
  }
});

```

to retrive flag content with correct password , i'm aiming to **`SQL type coercion`**
```
CREATE TABLE IF NOT EXISTS articles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    author VARCHAR(100) NOT NULL,
    content TEXT,
    is_private TINYINT(1) DEFAULT 0,
    password VARCHAR(255) DEFAULT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

filed password of articles tables is VARCHAR(255). 
Assuming the input password is the number `1` while the passwowrd values is `"1aaaa"` string. The where condition evaluates `True` in MySQL/MariaDB.

Configure remotte debug with payload json format we can controll type of password value
![image](https://hackmd.io/_uploads/r1eylemKMg.png)
![image](https://hackmd.io/_uploads/BklCylQFfl.png)

payload to flag
![image](https://hackmd.io/_uploads/SknzUeXFze.png)