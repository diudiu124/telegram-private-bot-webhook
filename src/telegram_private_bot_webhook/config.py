from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Tuple, Union


ChatId = Union[int, str]


@dataclass(frozen=True)
class AppConfig:
    bot_token: str
    run_mode: str = "polling"
    webhook_url: Optional[str] = None
    webhook_listen: str = "127.0.0.1"
    webhook_port: int = 8080
    webhook_path: str = "telegram"
    webhook_secret_token: Optional[str] = None
    persistence_path: str = "bot_state.pickle"
    admin_group_chat_id: Optional[ChatId] = None
    admin_user_ids: Tuple[int, ...] = ()
    handoff_keyword: str = "双向"
    handoff_exit_keyword: str = "单向"
    reply_mode: str = "hybrid"
    default_reply: str = "收到，我在。"
    openai_api_key: Optional[str] = None
    openai_base_url: Optional[str] = None
    openai_model: str = "gpt-4.1-mini"
    system_prompt: str = "You are a concise, helpful Telegram bot."
    image_path: Optional[str] = None
    menu_image: Optional[str] = None
    price_image: Optional[str] = None
    location_image: Optional[str] = None
    support_image: Optional[str] = None


def _normalize_path(value: Optional[str]) -> Optional[str]:
    if not value:
        return None
    path = Path(value).expanduser()
    return str(path) if path.exists() else None


def _parse_int(name: str, default: int) -> int:
    raw = os.getenv(name)
    if not raw:
        return default
    try:
        return int(raw)
    except ValueError as exc:
        raise RuntimeError(f"{name} must be an integer") from exc


def _parse_chat_id(raw: Optional[str]) -> Optional[ChatId]:
    if not raw:
        return None

    value = raw.strip()
    if not value:
        return None

    try:
        return int(value)
    except ValueError:
        return value


def _parse_int_list(raw: Optional[str]) -> Tuple[int, ...]:
    if not raw:
        return ()

    values = []
    for chunk in raw.split(","):
        item = chunk.strip()
        if not item:
            continue
        try:
            values.append(int(item))
        except ValueError as exc:
            raise RuntimeError("ADMIN_USER_IDS must be a comma-separated list of integers") from exc
    return tuple(values)


def load_config() -> AppConfig:
    token = os.getenv("BOT_TOKEN")
    if not token:
        raise RuntimeError("Please set BOT_TOKEN.")

    webhook_url = os.getenv("WEBHOOK_URL") or None

    run_mode = os.getenv("RUN_MODE", "").strip().lower()
    if run_mode:
        if run_mode not in {"polling", "webhook"}:
            raise RuntimeError("RUN_MODE must be either 'polling' or 'webhook'.")
    else:
        run_mode = "webhook" if webhook_url else "polling"

    if run_mode == "webhook" and not webhook_url:
        raise RuntimeError("Please set WEBHOOK_URL when RUN_MODE=webhook.")

    return AppConfig(
        bot_token=token,
        run_mode=run_mode,
        webhook_url=webhook_url,
        webhook_listen=os.getenv("WEBHOOK_LISTEN", "127.0.0.1"),
        webhook_port=_parse_int("WEBHOOK_PORT", 8080),
        webhook_path=os.getenv("WEBHOOK_PATH", "telegram").lstrip("/"),
        webhook_secret_token=os.getenv("WEBHOOK_SECRET_TOKEN") or None,
        persistence_path=os.getenv("PERSISTENCE_PATH", "bot_state.pickle"),
        admin_group_chat_id=_parse_chat_id(os.getenv("ADMIN_GROUP_CHAT_ID")),
        admin_user_ids=_parse_int_list(os.getenv("ADMIN_USER_IDS")),
        handoff_keyword=os.getenv("HANDOFF_KEYWORD", "双向"),
        handoff_exit_keyword=os.getenv("HANDOFF_EXIT_KEYWORD", "单向"),
        reply_mode=os.getenv("REPLY_MODE", "hybrid").lower(),
        default_reply=os.getenv("DEFAULT_REPLY", "收到，我在。"),
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        openai_base_url=os.getenv("OPENAI_BASE_URL"),
        openai_model=os.getenv("OPENAI_MODEL", "gpt-4.1-mini"),
        system_prompt=os.getenv("SYSTEM_PROMPT", "You are a concise, helpful Telegram bot."),
        image_path=_normalize_path(os.getenv("IMAGE_PATH")),
        menu_image=_normalize_path(os.getenv("MENU_IMAGE")),
        price_image=_normalize_path(os.getenv("PRICE_IMAGE")),
        location_image=_normalize_path(os.getenv("LOCATION_IMAGE")),
        support_image=_normalize_path(os.getenv("SUPPORT_IMAGE")),
    )
