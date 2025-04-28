from aiogram import BaseMiddleware

from aiogram import Bot
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramForbiddenError, TelegramBadRequest
from aiogram.types import TelegramObject, InlineQuery
from loguru import logger
from sqlalchemy import select

from db.models import Client
from db.session import async_session
from settings.config import settings


async def create_client_if_not_exists(chat_id):
    async with async_session() as session:
        client = (await session.scalars(select(Client).filter(Client.chat_id == chat_id))).one_or_none()
        if not client:
            # Create and add the new client
            client = Client(chat_id=chat_id)
            session.add(client)
            await session.commit()
            logger.info(f"Client with chat_id {chat_id} created.")
        else:
            logger.info(f"Client with chat_id {chat_id} already exists.")
        return client


# Subscription Middleware
class SubscriptionMiddleware(BaseMiddleware):
    async def __call__(self, handler, event: TelegramObject, data: dict):
        user_id = event.event.from_user.id

        # Payment start
        if event.pre_checkout_query or isinstance(event.event, InlineQuery):
            return await handler(event, data)

        message = self.__message_extractor(event=event)

        bot: Bot = data['bot']

        await create_client_if_not_exists(chat_id=user_id)

        # Check group subscription
        try:
            group_status = await bot.get_chat_member(chat_id=settings.SUBSCRIBE_GROUP_ID, user_id=user_id)
        except (TelegramForbiddenError, TelegramBadRequest) as e:
            logger.error(f'Failed to get users subscription on group: {e}')
            return
        try:
            channel_status = await bot.get_chat_member(chat_id=settings.SUBSCRIBE_CHANNEL_ID, user_id=user_id)
        except (TelegramForbiddenError, TelegramBadRequest) as e:
            logger.error(f'Failed to get users subscription on channel: {e}')
            return

        if (group_status.status not in [
            'member', 'administrator', 'creator',
        ] or channel_status.status not in [
            'member', 'administrator', 'creator',
        ]):
            await message.answer(
                f'Please subscribe to our [group]({settings.SUBSCRIBE_GROUP_LINK}), '
                f'[channel]({settings.SUBSCRIBE_CHANNEL_LINK}) to use the bot\n'
                f'And try again',
                parse_mode=ParseMode.MARKDOWN
            )
            return
        return await handler(event, data)

    @staticmethod
    def __message_extractor(event: TelegramObject):
        if event.message:
            return event.message

        if event.callback_query:
            return event.callback_query.message