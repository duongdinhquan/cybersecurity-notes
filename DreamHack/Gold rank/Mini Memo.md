[link](https://dreamhack.io/wargame/challenges/2329)

- Recon:
    - this functions of lab are related to creating and viewing templates.
    - in the database.py , memos.db file  is located in the root , users.db file is loacted in /data
    - this lab use render_template() and render_template_string() to display the content of template .
    - we can be observed that the flag of this lab is value of app.secret_key.
- exploit: 
```
@app.route('/memo/<int:memo_id>')
def memo_view(memo_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = get_memo_db_connection()
    c = conn.cursor()
    c.execute("SELECT title, content, template FROM memos WHERE id = ? AND user_id = ?",
              (memo_id, session['user_id']))
    memo = c.fetchone()
    conn.close()

    if not memo:
        return "Memo not found", 404

    title, content, template = memo

    template_path = f"data/templates/{template}"

    if template.startswith("/") or template.startswith("../"):
        template_path = f"data/templates/default"

    template_path = os.path.normpath(template_path)
    if not template_path.startswith("data/"):
        template_path = "data/templates/default"

    try:
        with open(template_path, 'r', encoding='utf-8', errors='ignore') as f:
            template_content = f.read()
    except FileNotFoundError:
        with open("data/templates/default", 'r', encoding='utf-8') as f:
            template_content = f.read()

    rendered_memo = render_template_string(template_content, title=title, content=content)

    return rendered_memo

```
- `rendered_memo = render_template_string(template_content, title=title, content=content)` .
in the above code , we can control  the **title , content** and the goal is control **template_content** by bypass the path traversal restriction.
- The value of template_content is the content of the file specified by template_path.
- we can bypass path traversal restriction using a payload such as **users.db/../../** because content of users.db is controlled . 
- in end point **/memo/new** , send a payload such as ![image](https://hackmd.io/_uploads/Hki_i0aa-l.png)
- access to endpoint **/memo/<id>** to receive result : ![image](https://hackmd.io/_uploads/r1URsR6a-l.png)

- step 1 : 
    - register username : **{{config}}**
- step 2
    - in end point **/memo/new** , send a payload such as  ![image](https://hackmd.io/_uploads/BJDEpApaZl.png)
    - result in endpoint **/memo/<id>**![image](https://hackmd.io/_uploads/rJ7LRA6a-e.png)
    - **'SECRET_KEY': 'FLAG1:DH{85bbcce15adac36a5682ae6fce4cec7e'**
- step 3:
    - using the SECRET_KEY to create the admin session . 
    - OS command : `flask-unsign --sign --cookie "{'role': 'admin', 'user_id': 1, 'username': 'admin'}" --secret "FLAG1:DH{85bbcce15adac36a5682ae6fce4cec7e"`
    - access endpoint /flag to receive second flag . ![image](https://hackmd.io/_uploads/ryn3bJC6Zl.png)

    
- final flag : DH{85bbcce15adac36a5682ae6fce4cec7e0d2768542a3019bc94b34829f8995f98}