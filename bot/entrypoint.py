from aiogram import Dispatcher, Bot
from aiogram import F
from aiogram.filters import Command
from aiogram.types import Message, PreCheckoutQuery, InlineQuery
from aiogram_dialog import Dialog, Window, StartMode, DialogManager
from aiogram_dialog.widgets.kbd import Row, Button
from aiogram_dialog.widgets.text import Const

from bot.cart.dialog import cart_dialog
from bot.cart.handlers import receive_quantity, handle_payment
from bot.catalog.dialog import catalog_dialog
from bot.faq.dialog import faq_dialog
from bot.faq.handlers import process_inline_input
from bot.middleware import SubscriptionMiddleware
from bot.states import StartStates, CatalogStates, FAQStates, CartStates

# Start
start_dialog = Dialog(
    Window(
        Const('Welcome to the bot! Choose an option:'),
        Row(
            Button(
                Const("🛒 Catalog"),
                id='catalog',
                on_click=lambda c, d, m: m.start(CatalogStates.CATEGORY, mode=StartMode.RESET_STACK)
            ),
            Button(
                Const("🛍️ Cart"),
                id='cart',
                on_click=lambda c, d, m: m.start(CartStates.VIEW_CART, mode=StartMode.RESET_STACK)
            ),
            Button(
                Const("❓ FAQ"),
                id='faq',
                on_click=lambda c, d, m: m.start(FAQStates.QUESTION, mode=StartMode.RESET_STACK)
            ),
        ),
        state=StartStates.MAIN,
    )
)


def setup_handlers(dp: Dispatcher):
    dp.update.middleware(SubscriptionMiddleware())

    @dp.message(Command('start'))
    async def start(message: Message, dialog_manager: DialogManager):
        await dialog_manager.start(StartStates.MAIN, mode=StartMode.RESET_STACK)

    # payment
    @dp.pre_checkout_query()
    async def pre_checkout_query_handler(pre_checkout_query: PreCheckoutQuery, bot: Bot):
        await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)

    @dp.message(F.successful_payment)
    async def successful_payment_handler(message: Message, dialog_manager: DialogManager):
        await handle_payment(message=message, dialog_manager=dialog_manager)

    # Cart edit
    @dp.message(lambda message: message.text and message.text.isdigit())  # TODO redo into MessageInput
    async def set_quantity_handler(message: Message, dialog_manager: DialogManager):
        if dialog_manager.dialog_data.get("waiting_for_quantity"):
            await receive_quantity(message=message, dialog_manager=dialog_manager)

    @dp.inline_query()
    async def faq_inline_handler(inline_query: InlineQuery):
        await process_inline_input(inline_query=inline_query)

    dp.include_router(start_dialog)
    dp.include_router(catalog_dialog)
    dp.include_router(faq_dialog)
    dp.include_router(cart_dialog)
