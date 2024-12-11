import logging

from aiogram import Bot
from aiogram import Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram_dialog.setup import setup_dialogs

from bot.dialogs import setup_start_handlers, setup_catalog_handlers, setup_faq_handlers, setup_cart_handlers
from settings.config import settings

logging.basicConfig(level=logging.INFO)


def main():
    # Initialize bot and dispatcher
    storage = MemoryStorage()
    bot = Bot(token=settings.BOT_TOKEN.get_secret_value())
    dp = Dispatcher(storage=storage)

    # Register all handlers
    setup_start_handlers(dp)
    setup_catalog_handlers(dp)
    setup_faq_handlers(dp)
    setup_cart_handlers(dp)

    setup_dialogs(dp)
    dp.run_polling(bot)


if __name__ == "__main__":
    main()
