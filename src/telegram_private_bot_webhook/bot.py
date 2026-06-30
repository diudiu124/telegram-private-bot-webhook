from __future__ import annotations

import logging
from functools import partial
from typing import Optional, Tuple

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, User
from telegram.constants import ChatType
from telegram.ext import Application, BasePersistence, CommandHandler, ContextTypes, MessageHandler, filters

from .config import AppConfig
from .rules import match_rule


logger = logging.getLogger(__name__)

MENU_KEYBOARD = InlineKeyboardMarkup(
    [
        [InlineKeyboardButton("出海赚钱从0到1", url="https://otc1888.com")],
        [InlineKeyboardButton("Giffgaff", url="https://flowus.cn/1888otc/share/9175b330-3a80-4ff7-ba16-dda11480ad79")],
        [InlineKeyboardButton("返佣", url="https://flowus.cn/1888otc/share/dad9c973-e1a5-4897-8636-5601ddcac83e")],
        [InlineKeyboardButton("VPN", url="https://x2.xueshan.shop/#/register?code=wihqKLZO")],
        [InlineKeyboardButton("指纹浏览器", url="https://www.adspower.net/share/D8RmqH")],
    ]
)


def _normalize_text(text: str) -> str:
    return text.strip().casefold()


def _menu_keyboard() -> InlineKeyboardMarkup:
    # 欢迎消息下方的网页按钮，点击后直接打开外部链接。
    return MENU_KEYBOARD


WELCOME_TEXT = "欢迎使用百宝工具箱，发送‘双向’开启双向聊天，发送‘单向’结束双向聊天"


def _topic_title(user: User) -> str:
    name = (user.full_name or user.first_name or "User").replace("\n", " ").replace("\r", " ").strip()
    title = f"{name} {user.id}".strip()
    return title[:128] or f"User {user.id}"


def _support_notice(user: User, enabled: bool) -> str:
    if enabled:
        return (
            f"双向会话已开启\n"
            f"用户：{user.full_name}\n"
            f"用户 ID：{user.id}\n"
            f"现在开始，用户发来的消息会进入这个话题；你直接在这里回复，机器人会转回给用户。"
        )
    return f"用户 {user.full_name}（{user.id}）已退出双向模式。"


async def ai_reply(
    text: str, context: ContextTypes.DEFAULT_TYPE, config: AppConfig
) -> Optional[Tuple[str, Optional[str], Optional[str]]]:
    if not config.openai_api_key:
        return None

    try:
        from openai import AsyncOpenAI
    except ImportError:
        return (
            '你已经开启了 AI 模式，但本机还没有安装 openai 依赖。请先运行：py -3 -m pip install -e ".[ai]"',
            None,
            None,
        )

    history = context.user_data.setdefault("history", [])
    messages: list[dict[str, str]] = [{"role": "system", "content": config.system_prompt}]
    messages.extend(history[-10:])
    messages.append({"role": "user", "content": text})

    client = AsyncOpenAI(api_key=config.openai_api_key, base_url=config.openai_base_url)
    try:
        completion = await client.chat.completions.create(model=config.openai_model, messages=messages)
    except Exception as exc:  # pragma: no cover - network/runtime failure path
        logger.exception("AI request failed")
        return f"AI 回复失败：{exc}", None, None

    answer = (completion.choices[0].message.content or "").strip() or "AI 没有返回内容。"
    history.append({"role": "user", "content": text})
    history.append({"role": "assistant", "content": answer})
    return answer, None, None


async def send_payload(update: Update, text: str, photo: Optional[str] = None, caption: Optional[str] = None) -> None:
    message = update.effective_message
    if message is None:
        return

    if photo:
        if len(text) <= 1024 and not caption:
            await message.reply_photo(photo=photo, caption=text)
            return

        if text:
            await message.reply_text(text)
        await message.reply_photo(photo=photo, caption=caption or (text[:1024] if len(text) <= 1024 else None))
        return

    await message.reply_text(text)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_chat and update.effective_chat.type != ChatType.PRIVATE:
        return
    await update.effective_message.reply_text(WELCOME_TEXT, reply_markup=_menu_keyboard())


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.effective_message.reply_text(WELCOME_TEXT, reply_markup=_menu_keyboard())


async def id_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat = update.effective_chat
    user = update.effective_user
    if chat is None or user is None:
        return

    await update.effective_message.reply_text(
        "当前信息：\n"
        f"chat.id = {chat.id}\n"
        f"chat.type = {chat.type}\n"
        f"user.id = {user.id}\n"
        f"user.name = {user.full_name}"
    )


async def _ensure_support_topic(
    update: Update, context: ContextTypes.DEFAULT_TYPE, config: AppConfig
) -> tuple[int | None, str | None]:
    user = update.effective_user
    if user is None:
        return None, "无法读取用户信息。"

    if config.admin_group_chat_id is None:
        return None, "还没有配置 ADMIN_GROUP_CHAT_ID，暂时不能进入双向模式。"

    support_chat_data = context.application.chat_data[config.admin_group_chat_id]
    topic_to_user = support_chat_data.setdefault("handoff_topic_to_user", {})

    topic_id = context.user_data.get("handoff_topic_id")

    if topic_id is None:
        try:
            topic = await context.bot.create_forum_topic(chat_id=config.admin_group_chat_id, name=_topic_title(user))
        except Exception:
            logger.exception("Failed to create support topic")
            return None, "无法创建客服话题，请确认超级群已开启论坛主题，并且机器人有创建主题权限。"

        topic_id = topic.message_thread_id
        topic_to_user[topic_id] = user.id
        context.user_data["handoff_topic_title"] = topic.name

        try:
            await context.bot.send_message(
                chat_id=config.admin_group_chat_id,
                message_thread_id=topic_id,
                text=_support_notice(user, True),
            )
        except Exception:
            logger.exception("Failed to send support notice")
    else:
        topic_to_user[topic_id] = user.id

    context.user_data["handoff_topic_id"] = topic_id
    return topic_id, None


async def _enter_handoff(update: Update, context: ContextTypes.DEFAULT_TYPE, config: AppConfig) -> None:
    topic_id, error = await _ensure_support_topic(update, context, config)
    if error is not None or topic_id is None:
        await update.effective_message.reply_text(error or "无法开启双向模式。")
        return

    context.user_data["handoff_enabled"] = True
    await update.effective_message.reply_text("已切换到人工模式。你后续发来的消息会转给客服。发送‘单向’可以退出。")


async def _exit_handoff(update: Update, context: ContextTypes.DEFAULT_TYPE, config: AppConfig) -> None:
    user = update.effective_user
    if user is None:
        await update.effective_message.reply_text("无法读取用户信息。")
        return

    context.user_data["handoff_enabled"] = False
    topic_id = context.user_data.get("handoff_topic_id")

    if config.admin_group_chat_id is not None and topic_id is not None:
        try:
            await context.bot.send_message(
                chat_id=config.admin_group_chat_id,
                message_thread_id=topic_id,
                text=_support_notice(user, False),
            )
        except Exception:  # pragma: no cover - notification best-effort only
            logger.exception("Failed to send handoff exit notice")

    await update.effective_message.reply_text("已退出人工模式，接下来会恢复自动回复。")


async def _relay_private_message_to_support(update: Update, context: ContextTypes.DEFAULT_TYPE, config: AppConfig) -> None:
    message = update.effective_message
    if message is None:
        return

    topic_id, error = await _ensure_support_topic(update, context, config)
    if error is not None or topic_id is None:
        await message.reply_text(error or "无法转发到客服。")
        return

    try:
        await context.bot.forward_message(
            chat_id=config.admin_group_chat_id,
            from_chat_id=message.chat_id,
            message_id=message.message_id,
            message_thread_id=topic_id,
        )
    except Exception:
        logger.exception("Failed to forward private message to support")
        await message.reply_text("消息转发失败，请稍后再试。")
        return

    await message.reply_text("已转给人工客服。")


async def _reply_to_text(text: str, context: ContextTypes.DEFAULT_TYPE, config: AppConfig) -> tuple[str, Optional[str], Optional[str]]:
    if config.reply_mode == "ai":
        payload = await ai_reply(text, context, config)
        return payload or (config.default_reply, None, None)

    if config.reply_mode == "rules":
        return match_rule(text, config) or (config.default_reply, None, None)

    payload = match_rule(text, config)
    if payload is not None:
        return payload

    payload = await ai_reply(text, context, config)
    return payload or (config.default_reply, None, None)


async def _reply_to_caption(
    caption: str, context: ContextTypes.DEFAULT_TYPE, config: AppConfig
) -> tuple[str, Optional[str], Optional[str]]:
    if config.reply_mode == "ai":
        payload = await ai_reply(caption, context, config)
        return payload or (config.default_reply, None, None)

    if config.reply_mode == "rules":
        return match_rule(caption, config) or (config.default_reply, None, None)

    payload = match_rule(caption, config)
    if payload is not None:
        return payload

    payload = await ai_reply(caption, context, config)
    return payload or (config.default_reply, None, None)


async def handle_private_message(
    update: Update, context: ContextTypes.DEFAULT_TYPE, config: AppConfig
) -> None:
    chat = update.effective_chat
    message = update.effective_message
    if chat is None or message is None or chat.type != ChatType.PRIVATE:
        return

    text = (message.text or "").strip()

    if text and _normalize_text(text) == _normalize_text(config.handoff_keyword):
        await _enter_handoff(update, context, config)
        return

    if text and _normalize_text(text) == _normalize_text(config.handoff_exit_keyword):
        await _exit_handoff(update, context, config)
        return

    if context.user_data.get("handoff_enabled"):
        await _relay_private_message_to_support(update, context, config)
        return

    if message.text:
        payload = await _reply_to_text(message.text, context, config)
        await send_payload(update, *payload)
        return

    if message.photo:
        if message.caption:
            payload = await _reply_to_caption(message.caption, context, config)
            await send_payload(update, *payload)
            return

        await message.reply_text("我收到了图片。你也可以继续发文字，我会继续回复。")
        return

    await message.reply_text(config.default_reply)


async def handle_admin_topic_message(
    update: Update, context: ContextTypes.DEFAULT_TYPE, config: AppConfig
) -> None:
    chat = update.effective_chat
    message = update.effective_message
    if chat is None or message is None or chat.type != ChatType.SUPERGROUP:
        return

    if config.admin_group_chat_id is None or chat.id != config.admin_group_chat_id:
        return

    if message.message_thread_id is None:
        return

    if message.from_user is None or message.from_user.is_bot:
        return

    if config.admin_user_ids and message.from_user.id not in config.admin_user_ids:
        return

    support_chat_data = context.application.chat_data[config.admin_group_chat_id]
    topic_to_user = support_chat_data.setdefault("handoff_topic_to_user", {})
    user_id = topic_to_user.get(message.message_thread_id)
    if user_id is None:
        return

    try:
        await context.bot.copy_message(
            chat_id=user_id,
            from_chat_id=chat.id,
            message_id=message.message_id,
        )
    except Exception:  # pragma: no cover - message delivery failure depends on Telegram side
        logger.exception("Failed to relay admin topic message")
        await message.reply_text("回传到用户失败，可能是对方没开私聊或机器人权限不足。")


def build_application(config: AppConfig, persistence: Optional[BasePersistence] = None) -> Application:
    builder = Application.builder().token(config.bot_token)
    if persistence is not None:
        builder = builder.persistence(persistence)

    application = builder.build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("id", id_command))
    application.add_handler(
        MessageHandler(filters.ChatType.PRIVATE & ~filters.COMMAND, partial(handle_private_message, config=config))
    )
    application.add_handler(
        MessageHandler(filters.ChatType.SUPERGROUP & ~filters.COMMAND, partial(handle_admin_topic_message, config=config))
    )
    return application
