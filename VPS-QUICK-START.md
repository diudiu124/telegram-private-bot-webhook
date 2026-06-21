# VPS 快速开始

这份文件只放最实用的复制粘贴命令。

你现在没有域名，所以默认走 `polling`。

## 0. 先准备好

- 一台 Ubuntu VPS（阿里云、腾讯云、轻量服务器都行）
- Telegram Bot Token
- 你的 GitHub 仓库地址，或者把项目文件夹传上去

## 1. 登录服务器

在你本机 PowerShell 里输入：

```powershell
ssh ubuntu@你的服务器IP
```

如果你是 root 用户，就改成：

```powershell
ssh root@你的服务器IP
```

如果系统提示要密码，就输入服务器密码。

登录成功后，你会看到类似这样的提示符：

```bash
ubuntu@xxx:~$
```

## 2. 安装基础环境

复制粘贴这一段：

```bash
sudo apt update
sudo apt install -y python3 python3-pip python3-venv git
python3 -m pip install --upgrade pip
```

## 3. 把项目放到服务器

如果你是从 GitHub 拉代码：

```bash
cd ~
git clone 你的仓库地址 telegram-private-bot-webhook
cd telegram-private-bot-webhook
```

如果你是手动上传文件，就先把项目文件夹放到服务器，再进入项目目录。

## 4. 创建虚拟环境

```bash
python3 -m venv .venv
source .venv/bin/activate
```

看到命令行前面出现 `(.venv)` 就对了。

## 5. 安装项目

```bash
pip install -e .
```

如果你要 AI：

```bash
pip install -e ".[ai]"
```

## 6. 创建 `.env`

先复制一份：

```bash
cp .env.example .env
```

然后打开 `.env` 修改：

```bash
nano .env
```

至少填这些：

```text
BOT_TOKEN=你的Telegram机器人Token
RUN_MODE=polling
ADMIN_GROUP_CHAT_ID=你的客服超级群ID
ADMIN_USER_IDS=你的Telegram用户ID
```

保存后按 `Ctrl + O`，回车，再按 `Ctrl + X` 退出。

## 7. 先手动启动一次

```bash
python3 -m telegram_private_bot_webhook
```

如果看到：

```text
Application started
```

说明可以继续。

## 8. 做成开机自启

复制服务文件：

```bash
sudo cp deploy/telegram-private-bot-polling.service /etc/systemd/system/telegram-private-bot-polling.service
```

然后编辑它，把这 3 个地方改成你的真实路径：

- `WorkingDirectory=/opt/telegram-private-bot-webhook`
- `EnvironmentFile=/opt/telegram-private-bot-webhook/.env`
- `ExecStart=/opt/telegram-private-bot-webhook/.venv/bin/telegram-private-bot-webhook`

如果你的项目放在 `~/telegram-private-bot-webhook`，就改成：

- `WorkingDirectory=/home/ubuntu/telegram-private-bot-webhook`
- `EnvironmentFile=/home/ubuntu/telegram-private-bot-webhook/.env`
- `ExecStart=/home/ubuntu/telegram-private-bot-webhook/.venv/bin/telegram-private-bot-webhook`

修改后执行：

```bash
sudo systemctl daemon-reload
sudo systemctl enable telegram-private-bot-polling
sudo systemctl start telegram-private-bot-polling
sudo systemctl status telegram-private-bot-polling
```

## 9. 看日志

如果出问题，看实时日志：

```bash
journalctl -u telegram-private-bot-polling -f
```

## 10. 更新代码

以后更新就按这三步：

```bash
cd ~/telegram-private-bot-webhook
git pull
pip install -e .
sudo systemctl restart telegram-private-bot-polling
```

如果用了 AI 依赖，再补一次：

```bash
pip install -e ".[ai]"
```

