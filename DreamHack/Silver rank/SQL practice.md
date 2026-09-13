[LINK](https://dreamhack.io/wargame/challenges/2613)

- From observing the lab , it appears that  the flag is actually password of admin account . Addtionally , the application constructs SQL  query through string conatenation , there fore it is like vulnable to SQLi
-![image](https://hackmd.io/_uploads/HyaoOQ7YZg.png)

- the lab use regex to limit the allowed characters . I want **\** character to encape the **'** character in the original query .
-![image](https://hackmd.io/_uploads/r1tjFmXYbx.png)
i use the above payload and successfull the login to access user account
- Before i denterming the content of admin password , i firt want to idenfity the length of admin password , know that adim is the firt record in table
- ![image](https://hackmd.io/_uploads/ryEZo7mKbg.png)
![image](https://hackmd.io/_uploads/SJA-s77KWx.png)
 - i just create a code to identify length of admin password . **Note that we need to set allow_redirects=False so that the requests library does not automatically follow the redirect**
-![image](https://hackmd.io/_uploads/rJZbxEQFZl.png)

the result show in above pickture indicate that length of admin password is 4