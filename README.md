# **Student Exchange Forum of BJUT**
## **1.  Introduction**
This project is a special forum for the communication of students, called **Student Exchange Forum of BJUT**.
It will bring new elements to Beijing University of Technology, which pursues "newness for the future". 
## **2. Deployment**
**Please use PyCharm as much as possible for the entire project, which can simplify the process of environment configuration.**

### **Clone project to local** 

```shell
git clone https://csgitlab.ucd.ie/18206155/debugger.git
```

### **Configure Python interpreter**

![1](https://tva1.sinaimg.cn/large/00831rSTly1gdhixxulqfj31560u0jwt.jpg)
![2](https://tva1.sinaimg.cn/large/00831rSTly1gdhizov9fqj31te07mace.jpg)
![3](https://tva1.sinaimg.cn/large/00831rSTly1gdhj0yt7f9j31a60u042j.jpg)
![4](https://tva1.sinaimg.cn/large/00831rSTly1gdhj1j47dzj314r0u0jv7.jpg)

> This is a brand new virtual environment and will not be affected by other environments in your computer.

### **Install all the packages we need in the new virtual environment**

```shell
pip install -r requirements.txt
```
### Problem that may arise
**In the process of using pip to download the package, we have various problems. You can refer to these following information.**
1. If the terminal prompts "Requirement already satisfied: ..." but it cannot find the package we originally installed when running.
* Solution: We need to clear the cache data of PyCharm and reinstall all the packages we need through the "requirements.txt" file.
* And How to Clear the Cache Data: <https://jingyan.baidu.com/article/656db918b1e142a281249cc8.html>


2. Internet speed is too slow resulting in download failure.
* Solution：Download via douban source.  <http://pypi.douban.com/simple>
* Reference: <https://blog.csdn.net/ITYTI/article/details/83313463>

3. After excluding the above problems, still cannot install any packet.
* Error info: Cannot connect to proxy solution：
* Solution: It may be caused by a proxy server set on the computer. Just shut off the proxy the sever.
* Reference: <https://www.cnblogs.com/arvinls/p/6149417.html>


### **Finally, you need to run these codes**
* For Linux and macOS,
```shell script
export FLASK_APP=flasky.py
flask run
```
* For Windows
```shell script
set FLASK_APP=flasky.py
flask run
```
### Test
* You can register an account by yourself and log in to your account.
* Please pay attention to the student number must be 8 digits，ID card number must be 10 to 18 digits. 
Moreover, you cannot register for the same student number repeatedly.


## **3.**  **About Group 16**
### **3.1 Group Name**
**Debugger**

### **3.2  Group Members**

| UCD Student Numbers | BJUT Student Numbers |    Name    |          Email           | 中文名字 |
| :-----------------: | :------------------: | :--------: | :----------------------: | :------: |
|      18206155       |       18372216       | Han Haozhi | haozhi.han@ucdconnect.ie |  韩昊知  |
|      18206178       |       18372315       | Yang Qifan | qifan.yang@ucdconnect.ie |  杨其帆  |
|      18206187       |       18372330       | Yang Xiao  | xiao.yang1@ucdconnect.ie |   杨骁   |
|      18206184       |       18372326       |  Ou Liwei  |  liwei.ou@ucdconnect.ie  |  欧立炜  |
|      18206366       |       18372314       | Cai Songge | songge.cai@ucdconnect.ie |  蔡颂歌  |
