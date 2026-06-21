# 阿里云 VPS 一步一步部署

这份文档是给第一次接触云服务器的人写的。

你现在没有域名，所以先走最简单、最稳的路线：`VPS + polling`。
这条路线不需要 Cloudflare，不需要域名，也不需要 webhook。

最重要的一句先放在前面：
- 你的电脑关机，不影响机器人运行
- 机器人跑在云服务器上，云服务器开着就行

## 先看结论

你要做的事其实就 6 步：

1. 买一台阿里云 ECS
2. 用 SSH 登录它
3. 安装 Python 和 Git
4. 把项目放到服务器
5. 启动机器人
6. 设置开机自启

如果你现在还没有域名，先不要碰 Cloudflare。

## 第 1 步：买服务器时怎么选

### 系统怎么选

直接选这些里面的一个：

- `Ubuntu 22.04 LTS`
- `Ubuntu 24.04 LTS`

不要选这些：

- WordPress
- 宝塔面板
- Docker 镜像
- Dify
- n8n

原因很简单：这些预装镜像对你这个机器人没帮助，只会让流程变复杂。

### 地域怎么选

优先选离你近、你能顺利买到的地域。

如果你只是在阿里云的控制台里挑一个能买的地区，先别纠结，能正常开机最重要。

### 登录方式怎么选

优先选：

- `密码登录`

如果控制台后面让你设置密码，就记住这个密码。

## 第 2 步：买完以后先记住 3 个东西

你要记住：

1. 公网 IP
2. 登录用户名
3. 登录密码

### 常见用户名

Ubuntu 系统一般常见用户名是：

- `ubuntu`

有些机器也可能允许 `root`，但 Ubuntu 官方镜像上更常见的是 `ubuntu`。

### 如果你不知道用哪个用户名

先试：

```powershell
ssh ubuntu@你的服务器IP
```

如果不行，再看阿里云控制台里写的默认用户名。

## 第 3 步：确保 22 端口是开的

SSH 登录走的是 22 端口。

你要在阿里云安全组里确认：

- 入方向允许 TCP 22
- 来源可以先放宽到你的电脑公网 IP，或者临时 0.0.0.0/0 测试

如果 22 端口没开，SSH 会连不上。

## 第 4 步：从 Windows 登录服务器

在你的本机 PowerShell 里输入：

```powershell
ssh ubuntu@你的服务器IP
```

例如：

```powershell
ssh ubuntu@1.2.3.4
```

如果你用的是 root，也可以试：

```powershell
ssh root@1.2.3.4
```

### 第一次连接时可能会看到什么

如果系统问你：

```text
Are you sure you want to continue connecting (yes/no/[fingerprint])?
```

输入：

```text
yes
```

然后回车。

接着它会让你输入密码。

### 如果你看到 `Connection closed by ... port 22`

先检查这 3 件事：

1. 安全组有没有放行 22 端口
2. 你输入的用户名对不对
3. 你输入的密码对不对

### 登录成功后长什么样

登录成功后，命令行通常会变成类似这样：

```bash
ubuntu@VM-0-9-ubuntu:~$
```

这就说明你已经进到服务器里了。

## 第 5 步：安装基础环境

在服务器里复制粘贴这一段：

```bash
sudo apt update
sudo apt install -y python3 python3-pip python3-venv git
python3 -m pip install --upgrade pip
```

这一步是在装 Python、pip、虚拟环境和 Git。

## 第 6 步：把项目放到服务器

这里有两种最简单的办法。

### 方案 A：用 GitHub 拉代码

如果你已经把项目放到 GitHub 上了，直接执行：

```bash
cd ~
git clone 你的仓库地址 telegram-private-bot-webhook
cd telegram-private-bot-webhook
```

这样以后更新代码也最方便。

### 方案 B：直接把整个文件夹传上去

如果你不想碰 GitHub，可以用下面任意一种工具把整个项目文件夹传到服务器：

- WinSCP
- MobaXterm

你在 Windows 上把整个 `telegram-private-bot-webhook` 文件夹上传过去，然后进入这个目录就行。

### 你后面会用到的目录

假设你把项目放在这里：

```text
/home/ubuntu/telegram-private-bot-webhook
```

那么后面服务文件里的路径就要写这个。

如果你是 root 用户并且放在 root 目录，路径可能是：

```text
/root/telegram-private-bot-webhook
```

## 第 7 步：创建虚拟环境

在项目目录里执行：

```bash
python3 -m venv .venv
source .venv/bin/activate
```

如果你看到命令行前面出现 `(.venv)`，就说明虚拟环境已经生效。

## 第 8 步：安装项目

执行：

```bash
pip install -e .
```

如果你要用 AI，再执行：

```bash
pip install -e ".[ai]"
```

## 第 9 步：准备 `.env`

先复制一份配置文件：

```bash
cp .env.example .env
```

然后打开编辑：

```bash
nano .env
```

### 先至少填这些

```text
BOT_TOKEN=你的Telegram机器人Token
RUN_MODE=polling
ADMIN_GROUP_CHAT_ID=你的客服超级群ID
ADMIN_USER_IDS=你的Telegram用户ID
```

### 如果你要接 AI 中转站，再加这些

```text
REPLY_MODE=hybrid
OPENAI_API_KEY=你的中转站Key
OPENAI_BASE_URL=你的中转站地址
OPENAI_MODEL=你的模型名
```

### 重要提醒

不要把 Token 直接输入到 PowerShell 里。
Token 要写进 `.env`。

### 保存方法

在 `nano` 里：

1. 按 `Ctrl + O`
2. 回车
3. 按 `Ctrl + X`

## 第 10 步：先手动启动一次

在项目目录里执行：

```bash
python3 -m telegram_private_bot_webhook
```

如果你看到类似这行：

```text
Application started
```

就说明机器人已经跑起来了。

### 现在先做 3 个测试

在 Telegram 里给机器人发：

1. `/start`
2. `esim`
3. `返佣`

如果能回消息，就说明主功能没问题。

## 第 11 步：设置开机自启

我们用 `systemd` 来让它一直跑着。

项目里有现成模板：

- `deploy/telegram-private-bot-polling.service`

### 先把模板复制到系统目录

```bash
sudo cp deploy/telegram-private-bot-polling.service /etc/systemd/system/telegram-private-bot-polling.service
```

### 再编辑这个文件

```bash
sudo nano /etc/systemd/system/telegram-private-bot-polling.service
```

你会看到里面有 3 个地方最重要：

```ini
WorkingDirectory=/opt/telegram-private-bot-webhook
EnvironmentFile=/opt/telegram-private-bot-webhook/.env
ExecStart=/opt/telegram-private-bot-webhook/.venv/bin/telegram-private-bot-webhook
```

### 这 3 行一定要改成你自己的真实路径

如果你的项目放在：

```text
/home/ubuntu/telegram-private-bot-webhook
```

那就改成：

```ini
WorkingDirectory=/home/ubuntu/telegram-private-bot-webhook
EnvironmentFile=/home/ubuntu/telegram-private-bot-webhook/.env
ExecStart=/home/ubuntu/telegram-private-bot-webhook/.venv/bin/telegram-private-bot-webhook
```

如果你的项目放在：

```text
/root/telegram-private-bot-webhook
```

那就改成：

```ini
WorkingDirectory=/root/telegram-private-bot-webhook
EnvironmentFile=/root/telegram-private-bot-webhook/.env
ExecStart=/root/telegram-private-bot-webhook/.venv/bin/telegram-private-bot-webhook
```

### 改完以后执行

```bash
sudo systemctl daemon-reload
sudo systemctl enable telegram-private-bot-polling
sudo systemctl start telegram-private-bot-polling
sudo systemctl status telegram-private-bot-polling
```

如果状态里看到 `active (running)`，就说明开机自启已经做好了。

## 第 12 步：看日志

如果机器人没起来，执行：

```bash
journalctl -u telegram-private-bot-polling -f
```

这个命令会实时显示日志。

你可以一边看日志，一边在 Telegram 里发消息测试。

## 第 13 步：以后怎么更新代码

### 如果你是用 GitHub 拉代码

以后更新时只要做这几步：

```bash
cd ~/telegram-private-bot-webhook
git pull
pip install -e .
sudo systemctl restart telegram-private-bot-polling
```

如果你启用了 AI 依赖，再补一条：

```bash
pip install -e ".[ai]"
```

### 如果你是手动上传文件

以后你就把改好的文件重新传上去，然后执行：

```bash
pip install -e .
sudo systemctl restart telegram-private-bot-polling
```

如果你只改了 `rules.py` 或文案文件，通常重启服务就够了。

## 第 14 步：Cloudflare 要不要加

现在先不要加。

因为你现在没有域名，而 `polling` 已经够用了。

### 什么时候才需要 Cloudflare

- 你以后有了域名
- 你以后想改成 `webhook`
- 你想临时用 Cloudflare Tunnel 把本地服务临时暴露出去

### 现在最简单的结论

- 本地测试：不用 Cloudflare
- VPS 常驻：不用 Cloudflare
- 以后有域名：再考虑 Cloudflare + webhook

## 第 15 步：最常见的坑

### 1. `ssh` 连不上

先看安全组是不是开了 22 端口。

再看你是不是用了正确的用户名：

- `ubuntu`
- `root`

### 2. `Permission denied`

通常是用户名不对或者密码不对。

### 3. `Application started` 没出来

先检查 `.env` 里的 `BOT_TOKEN` 和 `RUN_MODE=polling`。

### 4. `systemctl` 起不来

大概率是这 3 行路径没改对：

- `WorkingDirectory`
- `EnvironmentFile`
- `ExecStart`

### 5. 你把项目放哪了，就把服务文件里的路径改成哪

这是最容易出错的地方。

## 最后给你一个超短版

如果你只想照着最短路线走，就按这个顺序：

1. 买 `Ubuntu 22.04 LTS`
2. 开 22 端口
3. `ssh ubuntu@IP`
4. `sudo apt install -y python3 python3-pip python3-venv git`
5. `git clone 你的仓库地址`
6. `python3 -m venv .venv`
7. `source .venv/bin/activate`
8. `pip install -e .`
9. 配 `.env`
10. `python3 -m telegram_private_bot_webhook`
11. 复制并改 `telegram-private-bot-polling.service`
12. `sudo systemctl enable --now telegram-private-bot-polling`

这样就能跑起来了。
