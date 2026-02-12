本项目采用前后端分离架构，后端基于 Django REST Framework，前端基于 Vue3 + Vite

---

## 🛠 开发环境要求
* Python 3.9+
* Node.js 16+
* MySQL 8.0+

---

## 🚀 后端启动步骤
1、创建并激活虚拟环境
python -m venv venv
# Windows
.\venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

2、安装依赖
pip install -r requirements.txt

3、配置数据库
默认使用mysql数据库，数据库名为jgzx_platform， 检查 settings.py 中的 DATABASES 配置（用户名、密码）

4、执行数据库迁移
python manage.py makemigrations
python manage.py migrate

5、启动服务
python manage.py runserver

6、默认后端地址
http://127.0.0.1:8000/

## 🚀 前端启动步骤 (Frontend)
1、进入前端目录
cd frontend

2、安装依赖
npm install

3、配置代理
检查 vite.config.ts 中的 proxy 是否指向 http://127.0.0.1:8000

4、启动项目
npm run dev
访问地址：http://localhost:5173/