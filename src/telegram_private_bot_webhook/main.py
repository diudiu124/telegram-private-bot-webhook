from __future__ import annotations

import logging
from pathlib import Path

from telegram import Update
from telegram.ext import PicklePersistence, PersistenceInput

from .bot import build_application
from .config import load_config
from .dotenv_loader import load_dotenv_file


def main() -> None:
    load_dotenv_file()
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=logging.INFO,
    )
    logging.getLogger("httpx").setLevel(logging.WARNING)

    config = load_config()
    persistence = PicklePersistence(
        filepath=Path(config.persistence_path),
        store_data=PersistenceInput(bot_data=False, chat_data=True, user_data=True, callback_data=False),
    )
    application = build_application(config, persistence=persistence)

    if config.run_mode == "webhook":
        application.run_webhook(
            listen=config.webhook_listen,
            port=config.webhook_port,
            url_path=config.webhook_path,
            webhook_url=config.webhook_url,
            secret_token=config.webhook_secret_token,
            allowed_updates=Update.ALL_TYPES,
            drop_pending_updates=True,
        )
        return

    application.run_polling(
        allowed_updates=Update.ALL_TYPES,
        drop_pending_updates=True,
    )


if __name__ == "__main__":
    main()
