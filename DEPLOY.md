# 部署到公网（长期地址）

本地那套（`启动游戏.bat` + `开公网链接.bat`）是临时方案：电脑关机就没了，trycloudflare 每次还会换地址。
这份文档是把项目放到**免费云平台**上，得到**固定 https 地址、电脑关机也能玩**。

> 现在只有一个站点，云端也就是**一个服务、一个网址**。
> 云端跑 Linux + gunicorn；Windows 本机继续用 `启动游戏.bat`，互不影响。

---

## 方案 A：Render（推荐）

准备：**GitHub 账号**（免费）+ **Render 账号**（用 GitHub 一键登录）。

### 1. 把项目传到 GitHub

新建一个仓库（public / private 都行），上传下面这些**必需文件**：

```
app.py
wsgi_new.py
requirements.txt
render.yaml
templates/index.html
```

**不要上传**：`cloudflared.exe`（55MB）、`.shots/`、`启动游戏.bat`、`开公网链接.bat`、`.archive/`、`__pycache__/`
（`.gitignore` 已经帮你忽略它们了；也可以直接用 `deploy.zip` 解压出来的文件。）

### 2. 在 Render 里一键建服务

1. 打开 <https://dashboard.render.com> → 右上 **New +** → **Blueprint**
2. 选刚才那个仓库 → **Apply**
3. `render.yaml` 会自动建一个免费 Web Service：`fanzhayouxi`

### 3. 等 2~3 分钟，拿到地址

形如 `https://fanzhayouxi.onrender.com`（名字被占用时 Render 会自动加后缀，以控制台里显示的为准）。

### 4. 免费版要注意

- 15 分钟没人访问会**休眠**，下次打开要等约 30~60 秒唤醒；之后速度正常。
- 免费额度 750 实例小时/月（休眠不计时），一个服务日常完全够用。

---

## 方案 B：PythonAnywhere（不用 GitHub）

1. 注册 <https://www.pythonanywhere.com>（Beginner，免费）
2. **Files** → 进入 `/home/你的用户名/` → 新建目录 `fanzhayouxi`
3. 上传：`app.py`、`wsgi_new.py`、`templates/index.html`（在目录里再建 `templates`）
4. **Web** → **Add a new web app** → **Flask** → Python 3.12
5. 打开它生成的 WSGI 配置文件，把内容替换成：

```python
import sys

path = '/home/你的用户名/fanzhayouxi'
if path not in sys.path:
    sys.path.insert(0, path)

from app import app as application
```

6. 点 **Reload**，访问 `https://你的用户名.pythonanywhere.com`

---

## 打不开时，按这个顺序查

### 第 1 步：确认服务真的建出来了

Render 控制台里应该能看到 `fanzhayouxi`。**看不到 = 根本没部署**，那么对应域名永远是 404。

### 第 2 步：看服务状态灯

| 状态 | 含义 | 处理 |
| --- | --- | --- |
| **Live** | 跑起来了 | 点服务页顶部的 URL，而不是手打域名 |
| **Deploying / In progress** | 还在构建 | 等 2~5 分钟 |
| **Build failed** | 构建挂了 | 看 Logs，多半是 `pip install` 或文件缺失 |
| **Deploy failed / Crashed** | 启动挂了 | 看 Logs 最后 20 行 |
| **Suspended** | 免费额度用完 | 等下月或升级 |

### 第 3 步：按报错对号入座

| 现象 / 日志 | 原因 | 解决 |
| --- | --- | --- |
| `Not Found`（Render 的 404 页） | 服务不存在或域名拼错 | 只从控制台点进去 |
| `No open ports detected` | 启动命令没绑端口 | 必须是 `--bind 0.0.0.0:$PORT` |
| `gunicorn: command not found` | 没装 gunicorn | `requirements.txt` 里要有 `gunicorn>=21.2` |
| `ModuleNotFoundError: wsgi_new` | 文件不在仓库根目录 | Render → Settings → **Root Directory** 填子目录名 |
| 打开转圈 30~60 秒后 502 | 免费实例休眠被唤醒 | 再刷新一次 |
| 页面开了但答题没反应 | 前端请求失败 | F12 → Network 看 `/get_question/0` 是否 200 |

### 第 4 步：直接看日志

服务页 → **Logs**，把最后 20 行贴给我，我能直接定位。

---

## 更稳的建法：手动建 Web Service

1. Render → **New +** → **Web Service** → 选仓库
2. 填：
   - **Language**：`Python 3`
   - **Build Command**：`pip install -r requirements.txt`
   - **Start Command**：`gunicorn wsgi_new:app --bind 0.0.0.0:$PORT`
   - **Instance Type**：`Free`
3. Create → 等变绿 → 点页面上的 URL

---

## 本地验证过的内容

- 用 `waitress`（同为 WSGI 服务器）跑 `wsgi_new:app`：页面、`/get_question/0`、`/check_ans` 全部正常
- `deploy.zip` 解压到空目录也能直接跑起来（模板路径没问题）

## 上线后建议

1. 把永久地址写进 README 顶部。
2. 关掉临时隧道窗口，`cloudflared.exe` 可以删。
3. 展示前提前 1 分钟打开一次，把休眠的服务叫醒。
