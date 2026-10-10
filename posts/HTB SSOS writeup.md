  

![](https://pic-out.zhimg.com/v2-282bf35110fc2a705ead1fb88dab579b~resize:1440:q75.png?animatedImageAutoPlay=false&animatedImagePlayCount=1&auth_key=1791653815-0-0-975d27c8d3674affb77d9da66f7d2d2d&bizSceneCode=article_draft&expiration=1791653815&incremental=false&mid=f4895042b7822c0d6aab7ef8dd43ec39&overTime=60&precoder=false&protocol=v2&retryCount=3&sampling=false&sceneCode=editor_copy_outbound&source=bfcaadb1)
### Challenge Scenario

Homework? Never heard of her. Let's dance.

先看看主页，应该是以sso为主的挑战了

![](https://pic-out.zhimg.com/v2-1760d39ca17fcb68cfd7c9bc021a9d66~resize:1440:q75.png?animatedImageAutoPlay=false&animatedImagePlayCount=1&auth_key=1791653815-0-0-40ae80d7affb8782795c54e9c6cfe0e5&bizSceneCode=article_draft&expiration=1791653815&incremental=false&mid=f4895042b7822c0d6aab7ef8dd43ec39&overTime=60&precoder=false&protocol=v2&retryCount=3&sampling=false&sceneCode=editor_copy_outbound&source=bfcaadb1)

注册并登录后，我们可以看到这是一个教师布置与批改作业的网站

（记得修改/etc/hosts）

![](https://pic-out.zhimg.com/v2-ca883a93a5196a75bf27dc9704c01c2a~resize:1440:q75.png?animatedImageAutoPlay=false&animatedImagePlayCount=1&auth_key=1791653815-0-0-0cf0390d3da62763afea47e4b37718a2&bizSceneCode=article_draft&expiration=1791653815&incremental=false&mid=f4895042b7822c0d6aab7ef8dd43ec39&overTime=60&precoder=false&protocol=v2&retryCount=3&sampling=false&sceneCode=editor_copy_outbound&source=bfcaadb1)![](https://pic-out.zhimg.com/v2-a376fed98864ceaca61c476ff6166e95~resize:1440:q75.png?animatedImageAutoPlay=false&animatedImagePlayCount=1&auth_key=1791653815-0-0-05d7dfc8c2820920be8892ac184804b9&bizSceneCode=article_draft&expiration=1791653815&incremental=false&mid=f4895042b7822c0d6aab7ef8dd43ec39&overTime=60&precoder=false&protocol=v2&retryCount=3&sampling=false&sceneCode=editor_copy_outbound&source=bfcaadb1)

查看源码可以看到有个bot以teacher的权限

所以我们想到应该是通过xss或者ssrf来带出bot的权限

之前分析源码就可知flag就在提交的submission里，只有老师和提交的那个学生邮箱可以看到

_**所以猛干了几个小时看怎么带出这个teacher的权限。**_

![](https://pic-out.zhimg.com/v2-11d8441c3972f79dfa9b63c7dbac27ae~resize:1440:q75.png?animatedImageAutoPlay=false&animatedImagePlayCount=1&auth_key=1791653815-0-0-b326c9b1390fc05ad354f147e67f5e12&bizSceneCode=article_draft&expiration=1791653815&incremental=false&mid=f4895042b7822c0d6aab7ef8dd43ec39&overTime=60&precoder=false&protocol=v2&retryCount=3&sampling=false&sceneCode=editor_copy_outbound&source=bfcaadb1)![](https://pic-out.zhimg.com/v2-264aa41c62fb35dfb3927436de80ce15~resize:1440:q75.png?animatedImageAutoPlay=false&animatedImagePlayCount=1&auth_key=1791653815-0-0-d4629fa645c07a97fca2907c2b3e6caf&bizSceneCode=article_draft&expiration=1791653815&incremental=false&mid=f4895042b7822c0d6aab7ef8dd43ec39&overTime=60&precoder=false&protocol=v2&retryCount=3&sampling=false&sceneCode=editor_copy_outbound&source=bfcaadb1)![](https://pic-out.zhimg.com/v2-6e3039ee274844a6f88f1fdd58ce2087~resize:1440:q75.png?animatedImageAutoPlay=false&animatedImagePlayCount=1&auth_key=1791653815-0-0-498280bce6bf7e4d074f55554105857a&bizSceneCode=article_draft&expiration=1791653815&incremental=false&mid=f4895042b7822c0d6aab7ef8dd43ec39&overTime=60&precoder=false&protocol=v2&retryCount=3&sampling=false&sceneCode=editor_copy_outbound&source=bfcaadb1)

难道还有什么是我们没发现的吗，不可能啊，我把源码都喂给ai了

于是我选择了借鉴大佬的思路，顿觉豁然开朗。

![](https://pic-out.zhimg.com/v2-f4a8f8ae168fc4b74a516025bec4c38c~resize:1440:q75.png?animatedImageAutoPlay=false&animatedImagePlayCount=1&auth_key=1791653815-0-0-0df4a22681b11e2585afefab3bcbe329&bizSceneCode=article_draft&expiration=1791653815&incremental=false&mid=f4895042b7822c0d6aab7ef8dd43ec39&overTime=60&precoder=false&protocol=v2&retryCount=3&sampling=false&sceneCode=editor_copy_outbound&source=bfcaadb1)

原来一直出现在源码里，但是我没注意到的注册行为是破局的关键

这里用到了我们平时游戏或者软件注册开始时常用到的手段，

**抢注**

我们抢先注册**学生**的邮箱

然后构造一个csrf网页

**`POST /submit-url`**，并附上一个表单能执行**`文本/纯`CSRF登录**的URL。

bot发送了URL，自动提交表单，响应覆盖了与**学生**会话共享的SSO Cookie

所以，我们就可以以**作业上传学生**的身份去读取到flag，而不是死磕**教师**身份

①**bot的loginSSO()忽略凭证参数、用共享cookie jar当前的token授权**

②**Gin ShouldBindJSON忽略Content-Type→text/plain表单CSRF打JSON API**

③**SSO token cookie无SameSite→跨站登录Set-Cookie被bot接受**

④**[student@edulearn.htb](mailto:student@edulearn.htb)固定邮箱→启动15s抢注竞争。攻击=抢注student→等3个assignment→喷/submit-url指向data:text/html页面(text/plain CSRF表单登录我们的账号)→bot共享jar的token换成我们的会话→loginSSO(忽略参数)用我们cookie授权→submitFlag把FLAG写进我们账号→正常登录自读。**

在了解了思路后，经过一些修改，我们很快获取了可用的payload，我们只要在启动HTB实例时，快速复制ip与端口到这里使用，就可以实现抢注到获取flag的一条龙

![](https://pic-out.zhimg.com/v2-cfb27dd3d8121661ea6f33b3c0194c02~resize:1440:q75.png?animatedImageAutoPlay=false&animatedImagePlayCount=1&auth_key=1791653815-0-0-e0dadce1acc0fc6c593801b0c738465d&bizSceneCode=article_draft&expiration=1791653815&incremental=false&mid=f4895042b7822c0d6aab7ef8dd43ec39&overTime=60&precoder=false&protocol=v2&retryCount=3&sampling=false&sceneCode=editor_copy_outbound&source=bfcaadb1)

_**HTB{w0u1d_y0u_l1k3_t0_O4uth_d4nc3_w1th_m3_r1ght_n0w}**_

![](https://pic-out.zhimg.com/v2-cfa11768f4434daea1cf24d28ed07467~resize:1440:q75.png?animatedImageAutoPlay=false&animatedImagePlayCount=1&auth_key=1791653815-0-0-35ef34bc9473a4bee8e1f024e9a08b9b&bizSceneCode=article_draft&expiration=1791653815&incremental=false&mid=f4895042b7822c0d6aab7ef8dd43ec39&overTime=60&precoder=false&protocol=v2&retryCount=3&sampling=false&sceneCode=editor_copy_outbound&source=bfcaadb1)