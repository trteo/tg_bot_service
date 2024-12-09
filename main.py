import logging

from aiogram import Bot
from aiogram import Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram_dialog.setup import setup_dialogs

from bot.dialogs import setup_start_handlers, setup_catalog_handlers

BOT_TOKEN = "7798934875:AAFonPBFbsx7sPmLrs4GuPcMhzLu8H0B01E"

logging.basicConfig(level=logging.INFO)


def main():
    # Initialize bot and dispatcher
    storage = MemoryStorage()
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(storage=storage)

    # Register all handlers
    setup_start_handlers(dp)
    setup_catalog_handlers(dp)

    setup_dialogs(dp)
    dp.run_polling(bot)


if __name__ == "__main__":
    main()
