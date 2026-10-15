  

![](https://pic-out.zhimg.com/v2-dbdc9a0bf0f51c95b5446964bffb2d0e~resize:1440:q75.png?animatedImageAutoPlay=false&animatedImagePlayCount=1&auth_key=1792086950-0-0-b4db114f6798361457135746472fa9d3&bizSceneCode=article_draft&expiration=1792086950&incremental=false&mid=f4895042b7822c0d6aab7ef8dd43ec39&overTime=60&precoder=false&protocol=v2&retryCount=3&sampling=false&sceneCode=editor_copy_outbound&source=bfcaadb1)

这里我们访问查看目标，可以发现他是一个**机场航站楼运行系统。**

### **一、快照泄露与账密复用**

![](https://pic-out.zhimg.com/v2-26a5189a21660e00bfbc5f5baacf74ac~resize:1440:q75.png?animatedImageAutoPlay=false&animatedImagePlayCount=1&auth_key=1792086950-0-0-edcfefafa4b98b95aa6b9b72f35c2704&bizSceneCode=article_draft&expiration=1792086950&incremental=false&mid=f4895042b7822c0d6aab7ef8dd43ec39&overTime=60&precoder=false&protocol=v2&retryCount=3&sampling=false&sceneCode=editor_copy_outbound&source=bfcaadb1)

我们做一个简单的查询就可以发现

![](https://pic-out.zhimg.com/v2-b0520f9f7433a48dc6438289b1144035~resize:1440:q75.png?animatedImageAutoPlay=false&animatedImagePlayCount=1&auth_key=1792086950-0-0-51116688cdd21eb40866bc661939cbc5&bizSceneCode=article_draft&expiration=1792086950&incremental=false&mid=f4895042b7822c0d6aab7ef8dd43ec39&overTime=60&precoder=false&protocol=v2&retryCount=3&sampling=false&sceneCode=editor_copy_outbound&source=bfcaadb1)

可以发现这里有个十分重要的**heapdump**

我们下载下来做详细的分析

![](https://pic-out.zhimg.com/v2-44c2e8929a61ea732d1ad463b2d93d9e~resize:1440:q75.png?animatedImageAutoPlay=false&animatedImagePlayCount=1&auth_key=1792086950-0-0-b536ff439948494a983dd3562e6f5f88&bizSceneCode=article_draft&expiration=1792086950&incremental=false&mid=f4895042b7822c0d6aab7ef8dd43ec39&overTime=60&precoder=false&protocol=v2&retryCount=3&sampling=false&sceneCode=editor_copy_outbound&source=bfcaadb1)

可以发现凭证**svc_events / Yl4aCgh4y2PnU**，但是这个凭据暂时只是H2的内部密钥

经过查找后，我们发现这个房间存在密码复用的标签

通过这个凭据复用，我们可以连接到目标数据库

![](https://pic-out.zhimg.com/v2-ef96f4b3590bb0bb6bda7dc258aaad1c~resize:1440:q75.png?animatedImageAutoPlay=false&animatedImagePlayCount=1&auth_key=1792086950-0-0-c8fe4c2dcb1172885e6ccf02ab015b61&bizSceneCode=article_draft&expiration=1792086950&incremental=false&mid=f4895042b7822c0d6aab7ef8dd43ec39&overTime=60&precoder=false&protocol=v2&retryCount=3&sampling=false&sceneCode=editor_copy_outbound&source=bfcaadb1)

### 二、xxe漏洞以及横向移动

远程连接到目标后，我们去细看这个AIDX管道

![](https://pic-out.zhimg.com/v2-c81f69f9bd039ba916b2f826b74b546b~resize:1440:q75.png?animatedImageAutoPlay=false&animatedImagePlayCount=1&auth_key=1792086950-0-0-431f075c3bdd68e08f695534caa077ee&bizSceneCode=article_draft&expiration=1792086950&incremental=false&mid=f4895042b7822c0d6aab7ef8dd43ec39&overTime=60&precoder=false&protocol=v2&retryCount=3&sampling=false&sceneCode=editor_copy_outbound&source=bfcaadb1)![](https://pic-out.zhimg.com/v2-add6bb2dab4bd728547150d000a02e8c~resize:1440:q75.png?animatedImageAutoPlay=false&animatedImagePlayCount=1&auth_key=1792086950-0-0-66f063b434661698a4427278233415ef&bizSceneCode=article_draft&expiration=1792086950&incremental=false&mid=f4895042b7822c0d6aab7ef8dd43ec39&overTime=60&precoder=false&protocol=v2&retryCount=3&sampling=false&sceneCode=editor_copy_outbound&source=bfcaadb1)

我们可以发现这里很适合xxe的利用

![](https://pic-out.zhimg.com/v2-ffeef50ad9071dfe2d743e3b0f4fe209~resize:1440:q75.png?animatedImageAutoPlay=false&animatedImagePlayCount=1&auth_key=1792086950-0-0-9db65d87d6676472468e6d2a4923b142&bizSceneCode=article_draft&expiration=1792086950&incremental=false&mid=f4895042b7822c0d6aab7ef8dd43ec39&overTime=60&precoder=false&protocol=v2&retryCount=3&sampling=false&sceneCode=editor_copy_outbound&source=bfcaadb1)![](https://pic-out.zhimg.com/v2-dfd5e61f1c2294303bf63798b2673224~resize:1440:q75.png?animatedImageAutoPlay=false&animatedImagePlayCount=1&auth_key=1792086950-0-0-4234352338fc76d2f15478fff913e4f1&bizSceneCode=article_draft&expiration=1792086950&incremental=false&mid=f4895042b7822c0d6aab7ef8dd43ec39&overTime=60&precoder=false&protocol=v2&retryCount=3&sampling=false&sceneCode=editor_copy_outbound&source=bfcaadb1)

通过xxe实现远程文件读取/etc/passwd，我们可以找到两个待会会用到的妙妙工具

![](https://pic-out.zhimg.com/v2-06cd320b5a8e20785eaa28fa887dff2b~resize:1440:q75.png?animatedImageAutoPlay=false&animatedImagePlayCount=1&auth_key=1792086950-0-0-368e03845afe406224769d91b1a7abeb&bizSceneCode=article_draft&expiration=1792086950&incremental=false&mid=f4895042b7822c0d6aab7ef8dd43ec39&overTime=60&precoder=false&protocol=v2&retryCount=3&sampling=false&sceneCode=editor_copy_outbound&source=bfcaadb1)

我们还能发现在kafka这个链条中，我们可以去读取配置，在其中我们可以发现刚刚看到的一个熟悉的名字

没错，就是**svn-infra**，同时我们还发现了他的凭据**Ny2hdpme$bwT3**

![](https://pic-out.zhimg.com/v2-1e769a5456679c29bdc20f97a93feb94~resize:1440:q75.png?animatedImageAutoPlay=false&animatedImagePlayCount=1&auth_key=1792086950-0-0-8a971b1526707519f5bd86731675f143&bizSceneCode=article_draft&expiration=1792086950&incremental=false&mid=f4895042b7822c0d6aab7ef8dd43ec39&overTime=60&precoder=false&protocol=v2&retryCount=3&sampling=false&sceneCode=editor_copy_outbound&source=bfcaadb1)

通过获取的凭据，我们就可以ssh连接到目标

![](https://pic-out.zhimg.com/v2-0f623270b706f7d34297fbc3fc70d174~resize:1440:q75.png?animatedImageAutoPlay=false&animatedImagePlayCount=1&auth_key=1792086950-0-0-96dfa416edd264a12ec98833b9702e98&bizSceneCode=article_draft&expiration=1792086950&incremental=false&mid=f4895042b7822c0d6aab7ef8dd43ec39&overTime=60&precoder=false&protocol=v2&retryCount=3&sampling=false&sceneCode=editor_copy_outbound&source=bfcaadb1)

那么接下来的问题就是怎么横向到另一个用户了，

在经过多次寻觅后

我们又把目光放到了kafka这个之前帮助我们获取shell的功臣身上

- AIDX 管道消费 `aidx.identity.json.v1`，把身份数据从 Kafka 同步到 ClickHouse
- 这条数据流里的消息就是**用户身份记录**（username、password、email、roles）
- `martin_cole` 是系统用户，他的身份记录自然在这条流里

![](https://pic-out.zhimg.com/v2-faf3f1628bddaacb353710f23d6f0ecf~resize:1440:q75.png?animatedImageAutoPlay=false&animatedImagePlayCount=1&auth_key=1792086950-0-0-a43aca4425def24767ed2a65f3a80f62&bizSceneCode=article_draft&expiration=1792086950&incremental=false&mid=f4895042b7822c0d6aab7ef8dd43ec39&overTime=60&precoder=false&protocol=v2&retryCount=3&sampling=false&sceneCode=editor_copy_outbound&source=bfcaadb1)

果然，我们获得了他的密钥

![](https://pic-out.zhimg.com/v2-a5d7d0660915eeb11ebfb52c38edb1aa~resize:1440:q75.png?animatedImageAutoPlay=false&animatedImagePlayCount=1&auth_key=1792086950-0-0-80234d4abd2dbf383202735912b2edff&bizSceneCode=article_draft&expiration=1792086950&incremental=false&mid=f4895042b7822c0d6aab7ef8dd43ec39&overTime=60&precoder=false&protocol=v2&retryCount=3&sampling=false&sceneCode=editor_copy_outbound&source=bfcaadb1)

简单用john解密后，我们获取了这个用户的密码

![](https://pic-out.zhimg.com/v2-ff9c6321da914c957ce1a0856246c58a~resize:1440:q75.png?animatedImageAutoPlay=false&animatedImagePlayCount=1&auth_key=1792086950-0-0-aad08abb94d4a758dc34c0da721fea03&bizSceneCode=article_draft&expiration=1792086950&incremental=false&mid=f4895042b7822c0d6aab7ef8dd43ec39&overTime=60&precoder=false&protocol=v2&retryCount=3&sampling=false&sceneCode=editor_copy_outbound&source=bfcaadb1)

**martin_cole：tinkerbell**

![](https://pic-out.zhimg.com/v2-8fcd23d7f2494653854ccf9aa6e6ea8e~resize:1440:q75.png?animatedImageAutoPlay=false&animatedImagePlayCount=1&auth_key=1792086950-0-0-127a3ceef78a68543d10cc5965b69054&bizSceneCode=article_draft&expiration=1792086950&incremental=false&mid=f4895042b7822c0d6aab7ef8dd43ec39&overTime=60&precoder=false&protocol=v2&retryCount=3&sampling=false&sceneCode=editor_copy_outbound&source=bfcaadb1)

终于，我们获取了第一个flag

![](https://pic-out.zhimg.com/v2-344b830570f782538fcf1712ac94c3fd~resize:1440:q75.png?animatedImageAutoPlay=false&animatedImagePlayCount=1&auth_key=1792086950-0-0-2168d1b71e1ee43f5bb42b4359d0aaba&bizSceneCode=article_draft&expiration=1792086950&incremental=false&mid=f4895042b7822c0d6aab7ef8dd43ec39&overTime=60&precoder=false&protocol=v2&retryCount=3&sampling=false&sceneCode=editor_copy_outbound&source=bfcaadb1)

**_8f6b8703716c30843ecccb9381ae0ddc_**

### 三、提权root

接下来，我们的目标就是root了

我们把目光放在martin自己的房间里，除了flag以外，我们还有一个backups

![](https://pic-out.zhimg.com/v2-1ea10b8733af3f4283a0f4fee0a58327~resize:1440:q75.png?animatedImageAutoPlay=false&animatedImagePlayCount=1&auth_key=1792086950-0-0-d8e6c59d2b31fe0ec26f7e17a3675d0d&bizSceneCode=article_draft&expiration=1792086950&incremental=false&mid=f4895042b7822c0d6aab7ef8dd43ec39&overTime=60&precoder=false&protocol=v2&retryCount=3&sampling=false&sceneCode=editor_copy_outbound&source=bfcaadb1)

这是kopia的备份仓库

查看一些基础信息

然后用martin的凭据链接上去

![](https://pic-out.zhimg.com/v2-bc7265e3297fba9e9b65021ba5d18ccc~resize:1440:q75.png?animatedImageAutoPlay=false&animatedImagePlayCount=1&auth_key=1792086950-0-0-7a7ad9f2d18928c2f720242d355c1d12&bizSceneCode=article_draft&expiration=1792086950&incremental=false&mid=f4895042b7822c0d6aab7ef8dd43ec39&overTime=60&precoder=false&protocol=v2&retryCount=3&sampling=false&sceneCode=editor_copy_outbound&source=bfcaadb1)

我们标准方式去获取保存的**日志备份**的内容

![](https://pic-out.zhimg.com/v2-e0c8a07f060ad79208ece1c8c2b700e7~resize:1440:q75.png?animatedImageAutoPlay=false&animatedImagePlayCount=1&auth_key=1792086950-0-0-e0b923489ea5e67e44c2e4a1aba655d2&bizSceneCode=article_draft&expiration=1792086950&incremental=false&mid=f4895042b7822c0d6aab7ef8dd43ec39&overTime=60&precoder=false&protocol=v2&retryCount=3&sampling=false&sceneCode=editor_copy_outbound&source=bfcaadb1)

在备份里有两个文件，我们去查看错误文件

![](https://pic-out.zhimg.com/v2-6266c92cb2b8ce350f6c9a9047fced18~resize:1440:q75.png?animatedImageAutoPlay=false&animatedImagePlayCount=1&auth_key=1792086950-0-0-9c9aa8bd6f55c427cc0e0ad8a60a948e&bizSceneCode=article_draft&expiration=1792086950&incremental=false&mid=f4895042b7822c0d6aab7ef8dd43ec39&overTime=60&precoder=false&protocol=v2&retryCount=3&sampling=false&sceneCode=editor_copy_outbound&source=bfcaadb1)

我们看到了默认的密钥，也看到了对应的服务：clickhouse

![](https://pic-out.zhimg.com/v2-e1440ea9b33c0e049151700ccd95f640~resize:1440:q75.png?animatedImageAutoPlay=false&animatedImagePlayCount=1&auth_key=1792086950-0-0-870f4835f7e617134d3eb73b60a074a8&bizSceneCode=article_draft&expiration=1792086950&incremental=false&mid=f4895042b7822c0d6aab7ef8dd43ec39&overTime=60&precoder=false&protocol=v2&retryCount=3&sampling=false&sceneCode=editor_copy_outbound&source=bfcaadb1)

验证发现这个密钥确实可用

![](https://pic-out.zhimg.com/v2-595561a9343dde33f789b03b5d1b4c21~resize:1440:q75.png?animatedImageAutoPlay=false&animatedImagePlayCount=1&auth_key=1792086950-0-0-d840f61a89d54007d7e8511b7ac4994a&bizSceneCode=article_draft&expiration=1792086950&incremental=false&mid=f4895042b7822c0d6aab7ef8dd43ec39&overTime=60&precoder=false&protocol=v2&retryCount=3&sampling=false&sceneCode=editor_copy_outbound&source=bfcaadb1)

ClickHouse 是一个**列式 OLAP 数据库，**是 **AIDX 航班数据处理管道的存储终点。**

它支持把查询结果**写到服务器磁盘上的任意路径。**

而我们获取的数据库用户权限过大，这就变成了**任意文件写入**原语。

有了文件写入的方式，我买还需要一个标靶。

![](https://pic-out.zhimg.com/v2-f71be9c4f77ba6a542ac42fddca015c4~resize:1440:q75.png?animatedImageAutoPlay=false&animatedImagePlayCount=1&auth_key=1792086950-0-0-6e846ce6997d4e4dbd7507a3a47c8b63&bizSceneCode=article_draft&expiration=1792086950&incremental=false&mid=f4895042b7822c0d6aab7ef8dd43ec39&overTime=60&precoder=false&protocol=v2&retryCount=3&sampling=false&sceneCode=editor_copy_outbound&source=bfcaadb1)

DLQ Drainer 是一个 **root 拥有的 systemd 服务**，它**定期执行一个 Python 脚本**来处理死信队列消息。这个设计有两个致命问题：

1. **脚本路径固定**，攻击者知道去哪覆写
2. **脚本以 root 执行**，覆写后直接获得最高权限

现在有了靶子，我们就开始瞄准吧

找到这个服务

![](https://pic-out.zhimg.com/v2-df1f3c9e986470f95050745cb737c3d5~resize:1440:q75.png?animatedImageAutoPlay=false&animatedImagePlayCount=1&auth_key=1792086950-0-0-2729f0358cd1dfcf05ebfa5012bfaca5&bizSceneCode=article_draft&expiration=1792086950&incremental=false&mid=f4895042b7822c0d6aab7ef8dd43ec39&overTime=60&precoder=false&protocol=v2&retryCount=3&sampling=false&sceneCode=editor_copy_outbound&source=bfcaadb1)

再确认这个服务的运行

![](https://pic-out.zhimg.com/v2-1626e1b31b506044eb23a9bb566adce1~resize:1440:q75.png?animatedImageAutoPlay=false&animatedImagePlayCount=1&auth_key=1792086950-0-0-99cb08bee36684921a2c79bf1bb493ce&bizSceneCode=article_draft&expiration=1792086950&incremental=false&mid=f4895042b7822c0d6aab7ef8dd43ec39&overTime=60&precoder=false&protocol=v2&retryCount=3&sampling=false&sceneCode=editor_copy_outbound&source=bfcaadb1)

查询这个服务的内容

![](https://pic-out.zhimg.com/v2-7e77a4dfe33db9a490b135272add012c~resize:1440:q75.png?animatedImageAutoPlay=false&animatedImagePlayCount=1&auth_key=1792086950-0-0-9b51ccb7a315d24a86d47568a8bfd8bd&bizSceneCode=article_draft&expiration=1792086950&incremental=false&mid=f4895042b7822c0d6aab7ef8dd43ec39&overTime=60&precoder=false&protocol=v2&retryCount=3&sampling=false&sceneCode=editor_copy_outbound&source=bfcaadb1)

可以发现确实是root，而且亮出了执行的py文件

![](https://pic-out.zhimg.com/v2-b7f8a9e78cdd6fd90deda8a28bba3c5a~resize:1440:q75.png?animatedImageAutoPlay=false&animatedImagePlayCount=1&auth_key=1792086950-0-0-9ab0940884ddfeef55cb2ea2419d263c&bizSceneCode=article_draft&expiration=1792086950&incremental=false&mid=f4895042b7822c0d6aab7ef8dd43ec39&overTime=60&precoder=false&protocol=v2&retryCount=3&sampling=false&sceneCode=editor_copy_outbound&source=bfcaadb1)

虽然，这个是只有root可写的文件，但是看内容，我们就能发现另一个可写的文件

![](https://pic-out.zhimg.com/v2-0d8f669536d6d807f48aa7810c642576~resize:1440:q75.png?animatedImageAutoPlay=false&animatedImagePlayCount=1&auth_key=1792086950-0-0-e22a4458cb6a397b82ff3c08eea10ca8&bizSceneCode=article_draft&expiration=1792086950&incremental=false&mid=f4895042b7822c0d6aab7ef8dd43ec39&overTime=60&precoder=false&protocol=v2&retryCount=3&sampling=false&sceneCode=editor_copy_outbound&source=bfcaadb1)![](https://pic-out.zhimg.com/v2-04a6b4e5a92fbc1fc58960e68abe0c62~resize:1440:q75.png?animatedImageAutoPlay=false&animatedImagePlayCount=1&auth_key=1792086950-0-0-71b89946f4e6681e7955097c78938156&bizSceneCode=article_draft&expiration=1792086950&incremental=false&mid=f4895042b7822c0d6aab7ef8dd43ec39&overTime=60&precoder=false&protocol=v2&retryCount=3&sampling=false&sceneCode=editor_copy_outbound&source=bfcaadb1)

我们正常写入

![](https://pic-out.zhimg.com/v2-035d99f41d95a921a89dc4634e88e574~resize:1440:q75.png?animatedImageAutoPlay=false&animatedImagePlayCount=1&auth_key=1792086950-0-0-4da9c129d822646afb30c423871a4cd0&bizSceneCode=article_draft&expiration=1792086950&incremental=false&mid=f4895042b7822c0d6aab7ef8dd43ec39&overTime=60&precoder=false&protocol=v2&retryCount=3&sampling=false&sceneCode=editor_copy_outbound&source=bfcaadb1)

我们可以看到，已经成功修改了aidx_quarantine.py

之后就是**扣下扳机**，静待佳音

![](https://pic-out.zhimg.com/v2-f8cf4bab9fd168cf7528d1a1bcf94100~resize:1440:q75.png?animatedImageAutoPlay=false&animatedImagePlayCount=1&auth_key=1792086950-0-0-3afbfcf85ba8c930c8ca37cf792aef4b&bizSceneCode=article_draft&expiration=1792086950&incremental=false&mid=f4895042b7822c0d6aab7ef8dd43ec39&overTime=60&precoder=false&protocol=v2&retryCount=3&sampling=false&sceneCode=editor_copy_outbound&source=bfcaadb1)

yes,完美命中目标

![](https://pic-out.zhimg.com/v2-3c2d05d592069566d34ddf0b09cb5c2e~resize:1440:q75.png?animatedImageAutoPlay=false&animatedImagePlayCount=1&auth_key=1792086950-0-0-da119b4b07c247b766fb26e6425f5c55&bizSceneCode=article_draft&expiration=1792086950&incremental=false&mid=f4895042b7822c0d6aab7ef8dd43ec39&overTime=60&precoder=false&protocol=v2&retryCount=3&sampling=false&sceneCode=editor_copy_outbound&source=bfcaadb1)

获取root flag

**_f5ab5dd8a9bb7c0f54966674fd4b416d_**

![](https://pic-out.zhimg.com/v2-005c8a1cbabfa8ad6729b2eb370245b5~resize:1440:q75.png?animatedImageAutoPlay=false&animatedImagePlayCount=1&auth_key=1792086950-0-0-218f00e6961ab07ed5a8f26991510b50&bizSceneCode=article_draft&expiration=1792086950&incremental=false&mid=f4895042b7822c0d6aab7ef8dd43ec39&overTime=60&precoder=false&protocol=v2&retryCount=3&sampling=false&sceneCode=editor_copy_outbound&source=bfcaadb1)