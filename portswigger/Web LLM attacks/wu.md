## reference
https://arxiv.org/abs/2602.10453

https://lilianweng.github.io/posts/2023-10-25-adv-attack-llm/

https://github.com/elder-plinius/L1B3RT4S

https://nguyentranthanhlam.notion.site/Singapore-AI-CTF-2025-28be971444e48073911ffc01192607a7

## lý thuyết

Quy trình thông thường khi tích hợp LLM vào một website:
1. The client calls the LLM with the user's prompt.
2. The LLM detects that a function needs to be called and returns a JSON object containing arguments adhering to the external API's schema.
3. The client calls the function with the provided arguments.
4. The client processes the function's response.
5. The client calls the LLM again, appending the function response as a new message.
6. The LLM calls the external API with the function response.
7. The LLM summarizes the results of this API call back to the user.

### Ví dụ: đặt vé tàu
![](image/2026-11-25-09-26-20.png)

Bạn nhắn: “Tìm cho tôi một vé tàu từ Hà Nội đến Hải Phòng sáng mai.”
1. Ứng dụng gửi câu hỏi và danh sách công cụ cho LLM. Chẳng hạn, công cụ search_trains nhận nơi đi, nơi đến, ngày và khung giờ. Định nghĩa các trường này gọi là schema.
2. LLM trả về yêu cầu gọi công cụ. Dưới đây là JSON minh họa. tomorrow là giá trị mà backend sẽ đổi thành ngày cụ thể theo múi giờ của người dùng.
```json
   {
     "name": "search_trains",
     "arguments": {
       "from": "Hà Nội",
       "to": "Hải Phòng",
       "date": "tomorrow",
       "time_of_day": "morning"
     }
   }
```
3. Backend kiểm tra tham số và gọi API bán vé. Giả sử API trả về một chuyến lúc 08:00, còn chỗ, giá 150.000 đồng.
4. Backend gửi kết quả về cho LLM dưới dạng kết quả công cụ. LLM trả lời: “Có chuyến lúc 08:00, giá 150.000 đồng. Bạn có muốn mua vé này không?”


MÔ tả mã nguồn:
```python
import json
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from openai import OpenAI

client = OpenAI()  # Đọc OPENAI_API_KEY từ biến môi trường
model = "gpt-4.1-mini"

# 1. Lập trình viên định nghĩa schema và gửi cho LLM.
tools = [
    {
        "type": "function",
        "name": "search_trains",
        "description": "Tìm chuyến tàu theo tuyến, ngày và khung giờ.",
        "strict": True,
        "parameters": {
            "type": "object",
            "properties": {
                "from": {"type": "string"},
                "to": {"type": "string"},
                "date": {"type": "string", "description": "Ngày dạng YYYY-MM-DD"},
                "time_of_day": {
                    "type": "string",
                    "enum": ["morning", "afternoon", "evening"],
                },
            },
            "required": ["from", "to", "date", "time_of_day"],
            "additionalProperties": False,
        },
    }
]


def search_trains(origin, destination, date, time_of_day):
    # Khi tích hợp thật, backend dùng các tham số này để gọi API bán vé.
    return {
        "from": origin,
        "to": destination,
        "date": date,
        "time_of_day": time_of_day,
        "trains": [{"departure": "08:00", "price_vnd": 150000}],
    }


today = datetime.now(ZoneInfo("Asia/Ho_Chi_Minh")).date()
tomorrow = today + timedelta(days=1)

# 2. Backend gửi câu hỏi và schema. LLM có thể trả về một tool call.
first = client.responses.create(
    model=model,
    instructions=f"Hôm nay là {today.isoformat()}, ngày mai là {tomorrow.isoformat()}.",
    input="Tìm vé tàu Hà Nội đi Hải Phòng sáng mai.",
    tools=tools,
)

# 3. Backend đọc tool call và tự chạy hàm Python.
tool_outputs = []
for item in first.output:
    if item.type != "function_call" or item.name != "search_trains":
        continue

    args = json.loads(item.arguments)
    result = search_trains(
        origin=args["from"],
        destination=args["to"],
        date=args["date"],
        time_of_day=args["time_of_day"],
    )

    tool_outputs.append({
        "type": "function_call_output",
        "call_id": item.call_id,
        "output": json.dumps(result, ensure_ascii=False),
    })

# 4. Backend gửi kết quả về LLM để viết câu trả lời.
if tool_outputs:
    final = client.responses.create(
        model=model,
        previous_response_id=first.id,
        input=tool_outputs,
    )
    print(final.output_text)
else:
    print(first.output_text)
```
### nguyên nhân 
 
Do chèn trực tiếp `input_user`vào câu chỉ dẫn trước khi promt lên LLM

```python
# ❌ CODE DÍNH LỖI
import openai

def chat(user_input: str):
    system_prompt = "Bạn là trợ lý chăm sóc khách hàng của ngân hàng ABC. Chỉ trả lời về sản phẩm ngân hàng."

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user",   "content": user_input},   # ← input thô, không lọc
        ],
    )
    return response.choices[0].message.content
```

### Một số case 
-  Direct Prompt Injection
- Indirect Prompt Injection : nhúng chỉ thị độc vào dữ liệu mà bot sẽ đọc.


## Lab
### Lab: Exploiting LLM APIs with excessive agency
![](image/2026-11-25-12-04-19.png)

Thấy nó thể truy cập được ĐB và thử promt một câu truy vấn thì thấy 1 bản ghi được trả về
![](image/2026-11-25-12-05-18.png)

thực hiện xóa bản ghi:
![](image/2026-11-25-12-06-00.png)

### Lab: Exploiting vulnerabilities in LLM APIs



