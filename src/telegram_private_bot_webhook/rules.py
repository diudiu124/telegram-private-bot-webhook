from __future__ import annotations

from typing import Optional, Tuple

from .config import AppConfig


def match_rule(text: str, config: AppConfig) -> Optional[Tuple[str, Optional[str], Optional[str]]]:
    # 旧的关键词快捷回复已移除，保留这个函数只是为了兼容现有调用。
    return None
