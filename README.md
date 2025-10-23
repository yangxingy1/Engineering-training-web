# Engineering-training-web



## 项目简介

这是一个为“工程创新实践基地软件组培训”设计的课程主页。它不仅仅是一个静态的展示页面，更是一个集成了后端数据交互和核心**在线判题 (Mini-OJ)** 功能的全栈Web应用。 用户可以在主页浏览课程核心概念，并直接在页面上提交 Python 代码来解决特定问题。后端会利用 **Docker 沙箱**对代码进行安全的编译、运行和测试，并实时返回判题结果（如 "Accept", "Wrong Answer" 等）。





## 技术选择

\- **现代化的前端界面**:   

- 动态的粒子背景，富有科技感。    
- 响应式布局，适配不同设备尺寸。    -
-  使用 AJAX 异步提交表单，无需刷新页面即可与后端交互并获取实时结果。 

- **高性能的 Python 后端**:    
- 使用 **FastAPI** 框架，提供高速、异步的 API 接口。   
- 使用 **Loguru** 进行日志记录，监控用户提交和判题状态。    
- 用户信息和判题状态通过 **SQLite** 数据库进行持久化存储。





## 项目流程

1. **提交**: 用户在前端页面点击“提交”按钮，浏览器将代码、昵称和邮箱以 JSON 格式发送到后端的 `/api/judge` 接口。
2. **接收**: FastAPI 后端接收到请求，并将用户信息存入（或更新）SQLite 数据库。
3. **分发**: FastAPI 调用 `judge_code` 函数，将代码传递给判题模块。 
4. **沙箱创建**: 判题模块使用 `python-docker-sdk` 调用宿主机的 Docker 服务，根据 `Dockerfile.sandbox` 构建或启动一个**临时的、安全的、隔离的**判题容器。
5. **执行**: 用户代码和测试用例的输入被挂载到容器中。容器在低权限、无网络、资源受限的环境下执行用户代码。 
6. **捕获与比对**: 主程序捕获容器的标准输出，并与预期的测试用例输出进行比对。 
7. **销毁**: 无论执行成功与否，该临时容器都会被**立即销毁**，不留任何痕迹。 
8. **返回**: 最终的判题结果（`Accept`, `Wrong Answer` 等）被返回给 FastAPI，再由 FastAPI 返回给前端页面进行展示。





## 项目结构

```markdown
gc_training/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── crud.py
│   │   ├── database.py
│   │   ├── main.py
│   │   ├── models.py
│   │   └── schemas.py
│   ├── data/
│   ├── logs/
│   ├── judge/
│   │   ├── __init__.py
│   │   ├── Dockerfile.sandbox
│   │   └── run_sandbox.py
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── image/
│   ├── lib/
│   ├── home.html
│   ├── style.css
│   ├── script.js
│   ├── Dockerfile
│   └── nginx.conf
└── docker-compose.yml
```





## 部署指南

#### **第 1 步：准备并上传项目**

1. **克隆项目**：

   - 打开一个新的 PowerShell 或 CMD 窗口。

   - 输入指令clone项目代码

     ```cmd
     git clone git@github.com:yangxingy1/Engineering-training-web.git
     ```



#### **第 2 步：在服务器上部署**

1. **登录服务器**： 通过 SSH 登录到您的云服务器。

   Bash

   ```
   ssh <您的服务器用户名>@<您的服务器公网IP>
   ```

2. **进入项目目录**：

   ```cmd
   cd gc_training
   ```

3. **构建并启动服务**： 这是最后的命令。Docker Compose 将会读取 `docker-compose.yml` 文件，自动完成所有工作：构建 `frontend` 和 `backend` 两个主镜像、构建 `python-sandbox-env` 判题沙箱镜像（当后端服务首次启动时）、创建并启动所有容器。

   Bash

   ```
   docker compose up --build -d
   ```

   - 第一次执行此命令，由于需要从头构建所有镜像，会花费几分钟时间，请耐心等待。



#### **第 3 步：最终验证**

1. **检查容器状态**： 等待 `docker-compose up` 命令执行完毕后，检查所有容器是否都正常运行。

   ```cmd
   docker ps
   ```

   您应该能看到 `homepage-backend` 和 `homepage-frontend` 两个容器正在运行 (`STATUS` 为 `Up ...`)。

2. **检查防火墙**： 请务必确认您的云服务商（阿里云、腾讯云等）的**安全组**已经**开放了 80 端口**的入站访问。

3. **访问您的网站**： 打开您本地的浏览器，在地址栏输入您服务器的**公网 IP 地址**。

   ```
   http://<您的服务器公网IP>
   ```

4. **全面测试**：

   - 提交一次代码（使用正确的代码），确认能收到 "Accept" 结果。
   - 提交一次错误的代码，确认能收到 "Wrong Answer" 结果。
   - 在服务器上，进入 `gc_training/backend/data` 目录，检查 `visitors.db` 是否已生成。
   - 登录 PyCharm 或其他工具连接该数据库，确认用户数据和判题状态已正确写入。





## 项目维护

项目维护常用指令:所有指令都需要在项目根目录（即 `docker-compose.yml` 文件所在的目录）下运行。 

* **查看服务状态**    检查所有容器是否正在正常运行。

   

  ```cmd
  docker compose ps
  ```

* **查看实时日志 (非常重要)**    实时监控后端服务的日志输出，是排查问题的首选工具。

  ```cmd
  docker compose logs -f backend
  ```

  Ctrl + c 退出日志

* **停止所有服务**    此命令会停止并移除本次部署创建的所有容器和内部网络。  

  ```cmd
  docker compose down 
  ```

  

* **重启服务**    在服务停止后，使用此命令可以快速重新启动它们。

  ```cmd
  docker compose up -d
  ```

* **更新应用代码**    当您修改了本地代码并希望部署更新时，请执行以下操作：    

  * 1. 将修改后的代码上传到服务器，覆盖旧文件。   

    2. 项目根目录下运行以下命令。

       ```cmd
       docker compose up --build -d
       ```

* **进入容器内部 (高级操作)**    如果需要进入正在运行的后端容器内部进行调试，可以执行：  

  ```cmd
  docker compose exec backend bash
  ```

* **查询数据库** 

  ​	先进入容器内部,然后执行:

  ```cmd
  sqlite3 data/visitors.db
  ```

  ​	提示符变成 **sqlite>** 后,写入SQL语句如:

  ```sql
  SELECT * FROM visitors WHERE visitors.judge_status = 'Accept'
  ```

  
