[LINK](https://dreamhack.io/wargame/challenges/434)

- filter:
```
def xss_filter(text):
    _filter = ["script", "on", "javascript"]
    for f in _filter:
        if f in text.lower():
            return "filtered!!!"

    advanced_filter = ["window", "self", "this", "document", "location", "(", ")", "&#"]
    for f in advanced_filter:
        if f in text.lower():
            return "filtered!!!"

    return text
```
- We can bypass these filters by exploiting the attribute normalization (e.g., src in iframes, href in links). This mechanism automatically discards special characters like `\t` and `\n` or decodes encoded inputs, thereby neutralizing the filter's logic.
-  bypass the restriction on commas `(,)`, which is intended to prevent function calls with multiple arguments, we can utilize alternative techniques such as template literals (backticks `), or the `onerror` attribute combined with the `throw` statement.
- payload : ![image](https://hackmd.io/_uploads/Byzmd86fMx.png)
![image](https://hackmd.io/_uploads/rym4_86fMe.png)
![image](https://hackmd.io/_uploads/Sy1S_ITMGx.png)