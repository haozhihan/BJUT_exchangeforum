# **Student Exchange Forum of BJUT**
## **1.  Introduction**
This project is a special forum for the communication of students, called **Student Exchange Forum of BJUT**.
It will bring new elements to Beijing University of Technology, which pursues "newness for the future". 
## **2. Deployment**

### 2. 1 Run with Docker

**You can download the docker image we have prepared from Docker Hub, or you can generate a new docker image based on the Dockerfile inside the code, **

> The premise of using docker is that your computer has docker

#### 2.1.1 Download Docker Image



#### 2.1.2 Generate a new Docker Image

* Generate

```shell
docker build -t team16:latest .
```

* Run 

```shell
docker run -d -p 5000:5000 team16:latest
```

* Open Web APP

```shell
# If your computer is mac you can use this.
open -a "Google Chrome"  http://127.0.0.1:5000/ 
# If your computer is windows you can use this.
You can visit directly in the browser: 127.0.0.1:5000 to view.
```

* Kill Run

```shell
docker ps   #View the CONTAINER ID of the running container
```

```shell
docker kill <CONTAINER ID>  #Stop run
```



### 2.2 Run with Virtualenv Environment

**Please use PyCharm as much as possible for the entire project, which can simplify the process of environment configuration.**

#### **2.2.1 Clone project to local** 

```shell
git clone https://csgitlab.ucd.ie/18206155/debugger.git
```

#### 2.2.2 Configure Python interpreter

<img src="https://tva1.sinaimg.cn/large/00831rSTly1gdhixxulqfj31560u0jwt.jpg" alt="1" style="zoom: 33%;" />
<img src="https://tva1.sinaimg.cn/large/00831rSTly1gdhizov9fqj31te07mace.jpg" alt="2" style="zoom: 33%;" />
<img src="https://tva1.sinaimg.cn/large/00831rSTly1gdhj0yt7f9j31a60u042j.jpg" alt="3" style="zoom: 33%;" />
<img src="https://tva1.sinaimg.cn/large/00831rSTly1gdhj1j47dzj314r0u0jv7.jpg" alt="4" style="zoom: 33%;" />

> This is a brand new virtual environment and will not be affected by other environments in your computer.

#### 2.2.3 Install all the packages

```shell
pip install -r requirements.txt
```
#### 2.2.4 Run codes

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

#### 2.2.5 Problem that may arise

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



## 3. Test





## **4.**  **About Group 16**
### **4.1 Group Name**
**Debugger**

### **4.2  Group Members**

| UCD Student Numbers | BJUT Student Numbers |    Name    |          Email           | 中文名字 |
| :-----------------: | :------------------: | :--------: | :----------------------: | :------: |
|      18206155       |       18372216       | Han Haozhi | haozhi.han@ucdconnect.ie |  韩昊知  |
|      18206178       |       18372315       | Yang Qifan | qifan.yang@ucdconnect.ie |  杨其帆  |
|      18206187       |       18372330       | Yang Xiao  | xiao.yang1@ucdconnect.ie |   杨骁   |
|      18206184       |       18372326       |  Ou Liwei  |  liwei.ou@ucdconnect.ie  |  欧立炜  |
|      18206366       |       18372314       | Cai Songge | songge.cai@ucdconnect.ie |  蔡颂歌  |
