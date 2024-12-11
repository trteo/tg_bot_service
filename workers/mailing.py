from datetime import datetime
from typing import List

from aiogram import Bot
from aiogram.types import FSInputFile
from loguru import logger
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from db.models import Mailing, Client
from db.session import async_session


class MailingWorker:
    def __init__(self, bot: Bot):
        self.bot = bot

    @staticmethod
    async def __get_pending_mailings(session: AsyncSession) -> List[Mailing]:
        result = (await session.scalars(
            select(Mailing).where(
                Mailing.is_sent == False,  # Unsent messages
                Mailing.sending_date <= datetime.now()  # Sending date has passed
            )
        )).all()
        logger.info(f'Unsent messages: {result}')
        return result

    @staticmethod
    async def __get_active_clients(session: AsyncSession) -> List[Client]:
        result = (await session.scalars(select(Client).where(Client.is_active == True))).all()
        logger.info(f'Active users: {result}')
        return result

    async def send_mailings(self):
        logger.info('Checking mailings to send')
        async with async_session() as session:
            mailings = await self.__get_pending_mailings(session=session)
            clients = await self.__get_active_clients(session=session)

            for mailing in mailings:
                for client in clients:
                    try:
                        if mailing.message_image:
                            await self.bot.send_photo(
                                chat_id=client.chat_id,
                                photo=FSInputFile(mailing.message_image),
                                caption=mailing.message_text,
                            )
                        else:
                            await self.bot.send_message(
                                chat_id=client.chat_id,
                                text=mailing.message_text,
                            )
                    except Exception as e:
                        print(f"Failed to send to {client.chat_id}: {e}")
                await session.execute(
                    update(Mailing)
                    .where(Mailing.id == mailing.id)
                    .values(is_sent=True)
                )
            await session.commit()
        logger.info(f'Sent {len(mailings)} messages')
