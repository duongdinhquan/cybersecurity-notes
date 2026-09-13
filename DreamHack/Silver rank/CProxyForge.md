Program Analysis
index.js file
```
// Web proxy. Accesses host, port, and path entered by the user.
app.get('/proxy', requireAuth, async (req, res, next) => {
    const {scheme, host, port, path} = req.query;
    
    /* Construct URL by combining user inputs. This value is used as the key. */
    const url = await net.buildUrl(scheme, host, port, path, bypassDns=true);
    const cacheKey = url ? hashKey(url) : undefined;
    const cachedRes = url ? cache.get(cacheKey) : undefined;

    if (cachedRes === undefined) { // If it's a new request, proceed to make the request
        req.cacheKey = cacheKey;
        next(); (*) Proceeds to the block defined below.
    } else { // If cached information exists, respond with it immediately
        net.sendResponse(res, cachedRes);
    }
}, async (req, res) => { // Followed from the block above
    const param = {};
    for (c of ['scheme', 'host', 'port', 'path']) {
        param[c] = req.param(c); // Fetch user inputs
    }
    const {scheme, host, port, path} = param;

    /* Construct URL with user input. However, invalid inputs are blocked here. */
    const url = await net.buildUrl(scheme, host, port, path);
    if (url === undefined) { // If a prohibited URL address is entered
        return res.sendStatus(404);
    }

    const proxyRes = await net.get(url); // Send the actual request
    (Omitted: On successful request, the response is shown to the user and saved to cache.)
});

/* Internal network route. Accessing this API from the internal network yields the flag. */
app.get('/api/local/flag', requireLocal, async (req, res) => {
    return res.send(await fs.readFile('/flag_forge', { encoding: 'ascii' }));
});
```
The /proxy route constructs a URL using the scheme, host, port, and path entered into the input fields, sends a request to that address, and displays the response to the user. Requests are rejected if a prohibited address is supplied.
Only the internal network can access /api/local/flag, which yields the flag upon access.

Input validation and request handling functions are defined in net.js.

```


dns.setServers([ // Standard DNS servers used
    '1.1.1.1',
    '8.8.8.8',
]);

function isPrivateIP(ip) { // Check whether the IP address is internal/private
    var s = ip.split('.').map(x => parseInt(x, 10));
    return s[0] === 10 ||                               // 10.0.0.0/8
        (s[0] === 172 && s[1] >= 16 && s[1] < 32) ||    // 172.16.0.0/12
        (s[0] === 192 && s[1] === 168) ||               // 192.168.0.0/16
        s[0] === 127 ||                                 // 127.0.0.0/8
        ip === '0.0.0.0';                               // 0.0.0.0/32
}

async function isSafeHost(host) { // Validate host safety
    if (!/^[A-Za-z0-9.]+$/.test(host)) { // Block if characters other than specified are present
        return false;
    }
    try {
        const address = await dns.resolve4(host); // Resolve the host's actual public IP address
        return address.every(addr => !isPrivateIP(addr)); // Block if any resolved IP is internal/private
    } catch {
        return false; // Block non-existent addresses as well
    }
}

/* Construct URL */
async function buildUrl(scheme, host, port, path, bypassDns=false) {
    // Watchdog proxy endpoint allowlist
    if (scheme === 'http' && host === 'cproxy' && // Default input values
        port === '8080' && path === '/api/ping') {
        return 'http://cproxy:8080/api/ping';
    }
    
    /* All inputs must be strings, and the host must not resolve to an internal/private IP. */
    if ((scheme !== 'http' && scheme !== 'https') ||
        typeof host !== 'string' ||
        typeof port !== 'string' ||
        typeof path !== 'string' ||
        (!bypassDns && !await isSafeHost(host))) {
        return;
    }

    let url = `${scheme}://${host}`;

    if (port === '') {
        port = scheme === 'http' ? '80' : '443';
    }
    const intPort = parseInt(port, 10);
    if (intPort === NaN || intPort < 0 || intPort >= 0x10000) {
        return; // Port must be a valid integer
    }
    url += `:${intPort}`;

    if (!path.startsWith('/')) { // Path must start with /
        path = '/' + path;
    }
    url += path;
    
    return url;
}

async function get(url) {
    (Omitted: Sends request to the user-supplied URL using axios.)
}

function sendResponse(res, { status, statusText, headers, data }) {
    (Omitted: Loads and sends request results stored in cache.)
}


```

Vulnerability Analysis
1. isSafeHost() uses dns.resolve4() to resolve the IP address of the input host. If the resolved IP matches the blocklist, the request is blocked.

2. During get(), axios() resolves the domain name again to dispatch the actual network request.

Exploitation Strategy
Generate a specialized domain using an online DNS rebinding tool.

Configure A as 127.0.0.1.

Configure B as any public IP address not present on the server's blocklist (such as a personal VPS IP or any valid public IP).

Submitting this configuration produces a rebinding host name. The tool alternates DNS responses between these records rapidly with a TTL of 0. Querying this host will alternate between resolving to 127.0.0.1 (A) and the external IP (B).

config: ![image](https://hackmd.io/_uploads/rkQRyYGFzl.png)
payload: ![image](https://hackmd.io/_uploads/SJBRlKftfl.png)
