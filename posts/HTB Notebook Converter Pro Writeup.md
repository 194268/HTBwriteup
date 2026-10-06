
![](https://cdn-images-1.medium.com/max/1000/1*WVYbmQElIdOPvRpCzoZ9OQ.png)

#### Challenge Scenario

---

Welcome to NotebookConverter Pro, a tool for converting Jupyter notebooks into different formats with ease. While it appears simple and efficient, there may be more happening behind the scenes than meets the eye.

key:CVE-2026–39377

![](https://cdn-images-1.medium.com/max/1000/1*Ciay16F5jaKt__yoOT8THA.png)

so,check the source code 

ai told me three founds

![](https://cdn-images-1.medium.com/max/1000/1*s3fj9WUxYMKsddzsRMo3Dg.png)

![](https://cdn-images-1.medium.com/max/1000/1*4nKM7HNQ1q7zCqq2xnJIRA.png)

![](https://cdn-images-1.medium.com/max/1000/1*FknHRO6sqRul6EswGGw_cQ.png)

#### key one

> src_path = os.path.join(self.path, src) 

> if not os.path.exists(src_path): return None 

> with open(src_path, “rb”) as fobj: 

> return f”data:{mime_type};base64,{base64_str}” 

we can found the src was controlled by user

> os.path.join 

when meet start with “/” it will give up all the things before

so if we use 

!【x】(/etc/passwd)

it means 

- `src = "/etc/passwd"`
- `src_path = "/etc/passwd"`
- `os.path.exists` → True
- `open(..., "rb").read()`

#### key two

> for fname in cell.attachments:  
>  …  
>  new_filename = os.path.join(self.path_name, fname)  
>  resources[self.resources_item_key][new_filename] = decoded

and fname was controllable like before

> dest = os.path.join(build_dir, filename)  
> self._makedir(os.path.dirname(dest))  
> with open(dest, “wb”) as f:  
>  f.write(data)

here even help you make a dir to make it aviliable

#### **key three**

at exporters/markdown.py we found 

ExtractAttachmentsPreprocessor: enabled=Flase

### whole path

step 1:

register a new account and login it

![](https://cdn-images-1.medium.com/max/1000/1*oOD67Av439m_IXKNJGXmyg.png)

step 2:

make a evil object and convert it 

![](https://cdn-images-1.medium.com/max/1000/1*UrBzji_eLzoQ-MrMUph-Jw.png)

  

![](https://cdn-images-1.medium.com/max/1000/1*guICZcqKd_lp9FkLmCGmMg.png)

![](https://cdn-images-1.medium.com/max/1000/1*7XFTBJNCIyOkO8tjXmcF6w.png)

![](https://cdn-images-1.medium.com/max/1000/1*flQmZZcgoEAjR2E_IRaGFw.png)

step 3:

![](https://cdn-images-1.medium.com/max/1000/1*gYD2-ziRR2RqY0ASa2Vz_A.png)

![](https://cdn-images-1.medium.com/max/1000/1*NH54lqAw5503XVf2p9Mabg.png)

use it to get the data from what we download before

![](https://cdn-images-1.medium.com/max/1000/1*02j6M9fY40faWDUc_lOYkg.png)

step 4:

now we sign in as admin

![](https://cdn-images-1.medium.com/max/1000/1*-Zc24nMHswhfMmE5HLWWwA.png)

and we check the admin panel and ensure

_Save exported asset files Keep generated Markdown support files available for downstream publishing workflows._

![](https://cdn-images-1.medium.com/max/1000/1*Wy04knLEi5yOR7WghyzK6Q.png)

it will help us a lot

step 5:

use the `attachments`of Jupyter to rewrite the `/srv/app/app/converter/json.py`

by using this

![](https://cdn-images-1.medium.com/max/1000/1*US6Cjk9Leq71OYcXOoGvKA.png)

![](https://cdn-images-1.medium.com/max/1000/1*BqGABynqBczTrfZTMiA29g.png)

upload this 

step 6：

upload a simple notebook to trigger the RCE

![](https://cdn-images-1.medium.com/max/1000/1*RQYGFWDjMZ7JBkfebB1qHA.png)

step 7:

the final step 

use the payload like step 2 but use

 !【x】(/tmp/flag_out.txt) to read the flag

like this

![](https://cdn-images-1.medium.com/max/1000/1*sXQ6ND2OFr1lKkXgxb5QYA.png)

![](https://cdn-images-1.medium.com/max/1000/1*bKo_-5cGzfmLfsRyskCN4A.png)

and get the final flag like step 3

![](https://cdn-images-1.medium.com/max/1000/1*dFeHHdECN-RPAg1CWBApHA.png)

yep

we got the final flag

**_HTB{y3t_4n0th3r_pyth0n_c0nv3rt3r_cve}_**