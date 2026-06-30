# Telegram 私聊机器人

这是一个可部署到 Windows 或 VPS 的 Telegram 私聊机器人项目，支持：

- 关键词自动回复
- 文案 + 图片回复
- AI 兜底回复
- 双向人工接管
- `polling` 和 `webhook` 两种运行方式

## 你现在最适合用哪种

如果你**没有域名**，直接用 `polling`。

- `polling`：不需要域名，不需要 Cloudflare，最适合 VPS 常驻运行
- `webhook`：需要域名或 Cloudflare Tunnel，适合你以后想接固定公网地址时再用

## 最快启动

1. 安装 Python 3.9+
2. 进入项目目录
3. 执行：

```powershell
py -3 -m pip install -e .
```

如果要启用 AI，再执行：

```powershell
py -3 -m pip install -e ".[ai]"
```

4. 把 `.env.example` 复制成 `.env`
5. 至少填这些：

```text
BOT_TOKEN=你的Telegram机器人Token
RUN_MODE=polling
ADMIN_GROUP_CHAT_ID=你的客服超级群ID
ADMIN_USER_IDS=你的Telegram用户ID
```

6. 启动：

```powershell
py -3 -m telegram_private_bot_webhook
```

如果你是在 VPS 上常驻，建议后面用 `telegram-private-bot-polling` 这个 systemd 服务名。

如果你要直接照着复制命令部署 VPS，先看 [`VPS-QUICK-START.md`](VPS-QUICK-START.md)。

如果你是阿里云新手，先看 [`ALIYUN-STEP-BY-STEP.md`](ALIYUN-STEP-BY-STEP.md)。

## 如果以后你有域名

把 `.env` 改成：

```text
RUN_MODE=webhook
WEBHOOK_URL=https://你的域名/telegram
```

## 你的自动回复逻辑

- `/start` 会发欢迎语并显示菜单按钮
- `/help` 也会显示同样的欢迎语和菜单按钮
- 底部菜单有 5 个网页按钮：`出海赚钱从0到1`、`Giffgaff`、`返佣`、`VPN`、`指纹浏览器`
- `双向` 和 `单向` 继续保留，用来开启和结束人工接管

## 双向人工接管

用户在私聊发送 `双向` 后：

1. 机器人会把这个用户接入客服超级群的专属话题
2. 用户后续消息会转到群里
3. 你在群里直接回复，机器人会转回给用户
4. 用户发 `单向`，退出人工模式

## 后续怎么更新代码

如果你是用 Git 部署的，更新时就做这三步：

1. `git pull`
2. `py -3 -m pip install -e .`
3. 重启机器人

如果你启用了 AI 依赖，更新后再补一次：

```powershell
py -3 -m pip install -e ".[ai]"
```

如果你在 VPS 上是用 systemd 跑的，就重启对应服务，比如：

```bash
sudo systemctl restart telegram-private-bot-polling
```
