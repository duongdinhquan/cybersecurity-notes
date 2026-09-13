[link](https://dreamhack.io/wargame/challenges/2914)

- in the package.json file ,  i noticed that this lab uses `flatnest` libraries , which is used for merging , cloning  objects . If the input is not properly sanitized , it can cause the prototype pollution.
- the `flatnest` libraries provides two function : `flatten()`, which flattens objects, and `nest()`, which reconstructs (or nests) objects.
- flatnest version 1.0.1 has the CVE related to prototype pollution. 
- os command : `grep -rnE "(flatten|nest)" src/ `
![image](https://hackmd.io/_uploads/B1pow4JRWl.png)
- after some sesearch  , i discovered an RCE vulnerability in ESJ template v3.1.10 [link](https://medium.com/@albertoc_91016/prototype-pollution-in-open-source-libraries-exploiting-rce-in-ejs-ae93016630a3)
```
function lookupId(input) {
  const fields = ['username', 'customer', 'id'];

  if (typeof input === 'string') {
    return input;
  }

  if (input && typeof input === 'object') {
    for (const field of fields) {
      if (typeof input[field] === 'string') {
        return input[field];
      }
    }
  }

  return '';
}

```
- the above code excutes performs a search for username
```

router.post('/login', (req, res) => {
  const { username, password } = req.body || {};

  if (!password || typeof password !== 'string') {
    return res.status(400).json({ error: 'Password is required' });
  }

  const user = findUser(username);

  if (!user) {
    return res.status(400).json({ error: 'Unknown user' });
  }

  if (user.password !== password) {
    return res.status(400).json({ error: 'Invalid password' });
  }

  const session = signSession(username);
  setSession(res, session);

  return res.json({ session });
});
```
- this code only check  type of password field .
- **nest() function**
```
var circular = /\[Circular \((.+)\)\]/
var nestedRe = /(\.|\[)/
var scrub = /]/g

function nest(obj) {
  var key,
      i,
      nested = {}

  var keys = Object.keys(obj)
  var len = keys.length
  for (i = 0; i < len; i++) {
    key = keys[i]

    if (typeof obj[key] == "string" && circular.test(obj[key])) {
      var ref = circular.exec(obj[key])[1]
      if (ref == "this")
        obj[key] = nested
      else
        obj[key] = seek(nested, ref)
    }
    insert(nested, key, obj[key])
  }

  return nested
}

```
**insert() function**
```
function insert(target, path, value) {
  path = path.replace(scrub, "")

  var pathBits = path.split(nestedRe)
  var parent = target
  var len = pathBits.length
  for (var i = 0; i < len; i += 2) {
    var key = pathBits[i]
    if (key === "__proto__") continue
    if (key === "constructor" && typeof target[key] == "function") continue
    var type = pathBits[i + 1]

    if (type == null && key) parent[key] = value
    if (type == "." && parent[key] == null) parent[key] = {}
    if (type == "[" && parent[key] == null) parent[key] = []

    parent = parent[key]
  }
}

```
**seek() function**
```
function seek(obj, path) {
  path = path.replace(scrub, "")
  var pathBits = path.split(nestedRe)
  var len = pathBits.length
  var layer = obj
  for (var i = 0; i < len; i += 2) {
    if (layer == null) return undefined
    var key = pathBits[i]
    layer = layer[key]
  }
  return layer
}

```
- in the `seek()`function , objects are nested without validation of value keys , which lead to prototype pullotion vulnerability . However , the `seek()` function is called when the `if` statement is true . Therefore , the payload following as:
`{"key":"[Circular (some_thing)]"}` and some_thing is `__proto__` or `constructor.prototype`.

- how to get RCE throught ESJ tempalte v3.1.10 by abusing prototype pullution vulnerability.
    - [detail](https://medium.com/@albertoc_91016/prototype-pollution-in-open-source-libraries-exploiting-rce-in-ejs-ae93016630a3)
    - sumary:
        - polluted `Object.prototype.settings.view options`
        - payload : ![image](https://hackmd.io/_uploads/BJGN-lHC-g.png)

- final solution:
    - step 1: register a valid account.![image](https://hackmd.io/_uploads/H1zhblrRbg.png)
    - step 2 : login with a valid account and receive a seesion![image](https://hackmd.io/_uploads/BksWMxSCbg.png)
    - styep 3: access `assets/flag.txt` to get the flag![image](https://hackmd.io/_uploads/SJdgVxHCZg.png)