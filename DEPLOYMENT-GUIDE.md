# Telegram 私聊机器人部署指南

这份指南按“不会代码也能照着做”来写。

你现在没有域名，**最推荐的部署方式是：VPS + polling**。

如果你想要更短的复制粘贴版，先看 [`VPS-QUICK-START.md`](VPS-QUICK-START.md)。

如果你用的是阿里云，先看 [`ALIYUN-STEP-BY-STEP.md`](ALIYUN-STEP-BY-STEP.md)。

## 先选路线

- `polling`：推荐给你现在用。没有域名也能跑，VPS 上最省事。
- `webhook`：以后你有域名，或者想临时用 Cloudflare Tunnel 时再用。

一句话理解：

- `polling` 像“机器人一直自己去问 Telegram 有没有新消息”
- `webhook` 像“Telegram 主动把消息推到你的服务器门口”

你现在没有域名，所以先别折腾 webhook，直接用 `polling`。

## 你需要准备什么

1. Telegram 账号
2. Telegram Bot Token
3. 一台 VPS 或一台一直开着的电脑
4. 如果要 AI，再准备中转站的 `API Key`、`Base URL`、`Model`

## 第一部分：先在本机确认能跑

### 1. 打开项目目录

进入项目目录：

```powershell
cd "C:\Users\Yin\Documents\New project\telegram-private-bot-webhook"
```

注意：不要停留在 `C:\Windows\system32>`。

### 2. 安装依赖

执行：

```powershell
py -3 -m pip install -e .
```

如果要 AI，再执行：

```powershell
py -3 -m pip install -e ".[ai]"
```

### 3. 配 `.env`

把 `.env.example` 复制成 `.env`，然后至少填这些：

```text
BOT_TOKEN=你的Telegram机器人Token
RUN_MODE=polling
ADMIN_GROUP_CHAT_ID=你的客服超级群ID
ADMIN_USER_IDS=你的Telegram用户ID
```

如果要 AI，再填：

```text
OPENAI_API_KEY=你的中转站key
OPENAI_BASE_URL=你的中转站地址
OPENAI_MODEL=你的模型名
```

### 4. 启动程序

```powershell
py -3 -m telegram_private_bot_webhook
```

看到 `Application started` 就说明程序起来了。

### 5. 先发这几条测试

在 Telegram 里发给机器人：

1. `/start`
2. `/help`
3. `esim`
4. `返佣`
5. `双向`

如果有回复，就说明功能是通的。

## 第二部分：VPS 上怎么部署

下面以 Ubuntu VPS 为例。

### 1. 登录服务器

用 SSH 登录你的 VPS。

如果你已经拿到类似 `ubuntu@VM-0-9-ubuntu` 的提示符，就说明已经登录成功了。

### 2. 安装基础环境

```bash
sudo apt update
sudo apt install -y python3 python3-pip python3-venv git
```

如果你想顺手升级一下 pip，也可以执行：

```bash
python3 -m pip install --upgrade pip
```

### 3. 把代码放到服务器

如果你用 Git：

```bash
git clone 你的仓库地址
cd telegram-private-bot-webhook
```

如果你是手动上传，就把整个项目文件夹上传到服务器。

### 4. 建虚拟环境

```bash
python3 -m venv .venv
source .venv/bin/activate
```

如果命令前面出现 `(.venv)`，说明虚拟环境已经生效。

### 5. 安装项目

```bash
pip install -e .
```

如果要 AI：

```bash
pip install -e ".[ai]"
```

### 6. 配 `.env`

把 `.env.example` 复制成 `.env`，然后填：

```text
BOT_TOKEN=你的Telegram机器人Token
RUN_MODE=polling
ADMIN_GROUP_CHAT_ID=你的客服超级群ID
ADMIN_USER_IDS=你的Telegram用户ID
```

如果你暂时还没有客服群 ID，也可以先只填 `BOT_TOKEN` 和 `RUN_MODE=polling`，等群建好后再补。

### 7. 先手动跑一次

```bash
python3 -m telegram_private_bot_webhook
```

如果正常显示 `Application started`，说明这台 VPS 没问题。

如果这里报错，先不要急着上 systemd，先把错误修掉。

### 8. 让它常驻运行

推荐用 systemd。项目里有模板：

- `deploy/telegram-private-bot-polling.service`

你把里面的路径改成你服务器上的真实路径即可，然后执行：

```bash
sudo systemctl daemon-reload
sudo systemctl enable telegram-private-bot-polling
sudo systemctl start telegram-private-bot-polling
sudo systemctl status telegram-private-bot-polling
```

如果你想看日志，执行：

```bash
journalctl -u telegram-private-bot-polling -f
```

## 第三部分：以后怎么更新代码

如果你是用 Git 部署的，更新时就做这三步：

1. 进入项目目录
2. 执行 `git pull`
3. 重新安装依赖：`pip install -e .`
4. 重启 systemd 服务

命令通常是：

```bash
git pull
pip install -e .
sudo systemctl restart telegram-private-bot-polling
```

如果你还装了 AI 依赖，再补一次：

```bash
pip install -e ".[ai]"
```

## 第四部分：Cloudflare 要不要加

你现在**没有域名**，所以 Cloudflare 不是必须。

先把 `polling` 跑稳，再考虑别的。

### 什么时候需要 Cloudflare

- 你以后想用固定域名
- 你以后想用 webhook
- 你想把本机临时暴露出去测试

### 现在最简单的结论

- 本地测试：不用 Cloudflare，也能先跑 `polling`
- VPS 常驻：不用 Cloudflare，直接 `polling`
- 以后有域名：再考虑 webhook + Cloudflare

## 第五部分：常见报错

### 1. `pip` 找不到

不要直接敲 `pip`，用：

```powershell
py -3 -m pip install -e .
```

### 2. 提示没设置 `BOT_TOKEN`

说明 `.env` 还没填机器人 Token，或者文件位置不对。

### 3. AI 报 `openai` 没安装

执行：

```powershell
py -3 -m pip install -e ".[ai]"
```

### 4. AI 报 401 或 403

一般是中转站 key、Base URL、模型名写错了。

### 5. 双向模式不工作

检查：

- `ADMIN_GROUP_CHAT_ID` 是否正确
- 机器人是否在超级群里
- 超级群是否开了论坛主题
- 机器人是否有创建话题权限
- `ADMIN_USER_IDS` 是否包含你自己

## 最后提醒你一句

你现在没有域名，**就把 `RUN_MODE=polling` 当成默认方案**。

等以后你真的有了域名，再把 `RUN_MODE` 改成 `webhook` 就行。
