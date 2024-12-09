from aiogram import BaseMiddleware

from aiogram import Bot
from aiogram.exceptions import TelegramForbiddenError, TelegramBadRequest
from aiogram.types import Update, TelegramObject
from loguru import logger


# Subscription Middleware
class SubscriptionMiddleware(BaseMiddleware):
    async def __call__(self, handler, event: TelegramObject, data: dict):
        if not isinstance(event, Update) or not event.message:  # TODO fix buttons click
            return await handler(event, data)

        user_id = event.message.from_user.id
        group_id = -1002489680551  # TODO set from settings
        channel_id = -1001765033775  # TODO set from settings

        bot: Bot = data['bot']

        logger.info(
            f'{user_id}, {group_id}, {channel_id}, {bot}'
        )

        # Check group subscription
        try:
            group_status = await bot.get_chat_member(chat_id=group_id, user_id=user_id)
        except (TelegramForbiddenError, TelegramBadRequest) as e:
            logger.error(f'Failed to get users subscription on group: {e}')
            return
        try:
            channel_status = await bot.get_chat_member(chat_id=channel_id, user_id=user_id)
        except (TelegramForbiddenError, TelegramBadRequest) as e:
            logger.error(f'Failed to get users subscription on channel: {e}')
            return

        if (group_status.status not in [
            'member', 'administrator', 'creator',
        ] or channel_status.status not in [
            'member', 'administrator', 'creator',
        ]):
            await event.message.answer(
                f'Please subscribe to our (group)[{...}] '  # TODO set from settings
                f'and (channel)[{...}] to use the bot.'  # TODO set from settings
            )
            return
        return await handler(event, data)
