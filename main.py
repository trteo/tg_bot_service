import asyncio
import logging

from aiogram.fsm.storage.base import DefaultKeyBuilder
from redis import asyncio as aioredis

from aiogram import Bot
from aiogram import Dispatcher
from aiogram.fsm.storage.redis import RedisStorage
from aiogram_dialog.setup import setup_dialogs
from loguru import logger

from bot.entrypoint import setup_handlers
from settings.config import settings
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from workers.mailing import MailingWorker

logging.basicConfig(level=logging.INFO)


async def main():
    # Initialize bot and dispatcher
    # storage = RedisStorage.from_url(f'redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}')

    redis = await aioredis.from_url(f'redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}')
    storage = RedisStorage(redis=redis, key_builder=DefaultKeyBuilder(with_destiny=True))
    logger.info(f'Bot token: {settings.BOT_TOKEN.get_secret_value()}')

    bot = Bot(token=settings.BOT_TOKEN.get_secret_value())
    dp = Dispatcher(storage=storage)

    # Register all handlers
    setup_handlers(dp)
    setup_dialogs(dp)

    await run_mailing_cron(bot=bot)
    await dp.start_polling(bot)


async def run_mailing_cron(bot: Bot):
    scheduler = AsyncIOScheduler()
    scheduler.add_job(MailingWorker(bot=bot).send_mailings, "interval", seconds=10)  # Check every minute
    scheduler.start()
    logger.info('Started mailing corn')


if __name__ == "__main__":
    asyncio.run(main())
