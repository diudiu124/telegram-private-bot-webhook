from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Tuple

from .config import AppConfig


@dataclass(frozen=True)
class ReplyRule:
    keywords: tuple[str, ...]
    text: str
    photo_attr: Optional[str] = None
    caption: Optional[str] = None


RULES: tuple[ReplyRule, ...] = (
    ReplyRule(
        ("esim",),
        "详情链接：（打开此链接请关闭VPN代理）https://flowus.cn/1888otc/share/9175b330-3a80-4ff7-ba16-dda11480ad79\n"
        "Giffgaff\n"
        "①小白卡未充值 70元包邮\n"
        "②已充值10英镑（活动期间到账15英镑）185元包邮\n"
        "以上为单个价格 批发价格请联系Tg：@GeekOTC",
    ),
    ReplyRule(
        ("返佣",),
        "详情链接：（打开此链接请关闭VPN代理）https://flowus.cn/1888otc/share/dad9c973-e1a5-4897-8636-5601ddcac83e\n"
        "\n"
        "币安：https://www.bsmkweb.cc/register?ref=1888OTC\n"
        "\n"
        "Bybit：https://www.bybitglobal.com/invite?ref=5EQ0ZG&medium=referral&utm_campaign=evergreen\n"
        "\n"
        "欧意：https://www.promoohivex.com/join/17811059\n"
        "\n"
        "火币：https://www.htx.com.ph/invite/zh-cn/1f?invite_code=2ggic223\n"
        "\n"
        "Bitget：https://www.nlviwq.cn/zh-CN/referral/register?clacCode=UXZAZGBP&from=%2Fzh-CN%2Fevents%2Freferral-all-program&source=events&utmSource=PremierInviter\n"
        "\n"
        "Gate：https://www.gate.com/zh/referral/earn-together/invite/AVDCVW9A?ref=AVDCVW9A&ref_type=103&utm_cmp=rXJBDjtJ&activity_id=1781161013843",
    ),
)


def match_rule(text: str, config: AppConfig) -> Optional[Tuple[str, Optional[str], Optional[str]]]:
    normalized = text.strip().lower()

    # 常见问候语直接按规则回复，不走 AI。
    if normalized in {"hi", "hello", "你好", "在吗"}:
        return "在的。你可以继续发消息，我会自动回复。", None, None

    for rule in RULES:
        if any(keyword.lower() in normalized for keyword in rule.keywords):
            photo = getattr(config, rule.photo_attr) if rule.photo_attr else None
            if photo is None:
                photo = config.image_path
            if photo:
                return rule.text, photo, rule.caption
            return rule.text, None, None

    return None
