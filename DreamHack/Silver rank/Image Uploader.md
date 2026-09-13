- in file **upload.php** , I indetified a logic bug in the code snippet below:
![image](https://hackmd.io/_uploads/HJH7PvUTWx.png)
    - in the **if** statement , the codes use **&&** orperator , meaning the internal logic only executes when the both condition is true . 
    - The internal logic will not execute if either of the two conditions evaluates to false
- the application only change name of uploaded file and forgot extension name . ![image](https://hackmd.io/_uploads/r1v_cPIaZe.png)
- payload : ![image](https://hackmd.io/_uploads/BJqGjwUp-x.png)
    - namefile : shell.php
    - insert content of malicous code into the content of original file png but no change the magic byte of file . 
- access the target : **http://host8.dreamhack.games:9040/uploads/20260422154027_9303_shell.php** and use **cmd=cat%20../flag.txt** parameter to control the target system .
- flag : **DH{6cb5076e71927728a48baa3ed77dbc9d}** 