from aiogram import Dispatcher
from aiogram.filters import Command
from aiogram.types import Message
from aiogram_dialog import Dialog, Window, StartMode, DialogManager
from aiogram_dialog.widgets.kbd import Row, Button
from aiogram_dialog.widgets.kbd import ScrollingGroup, Select
from aiogram_dialog.widgets.text import Const
from aiogram_dialog.widgets.text import Format
from loguru import logger

from bot import handlers
from bot.db import get_subcategories, get_categories, get_items
from bot.middleware import SubscriptionMiddleware
from bot.states import StartStates, CatalogStates

# Start
start_dialog = Dialog(
    Window(
        Const('Welcome to the bot! Choose an option:'),
        Row(
            Button(Const("'🛒 Catalog'"), id='catalog', on_click=handlers.on_catalog),
            Button(Const("'🛍️ Cart'"), id='cart', on_click=handlers.on_cart),
            Button(Const("'❓ FAQ'"), id='faq', on_click=handlers.on_faq),
        ),
        state=StartStates.MAIN,
    )
)


# Catalogs
catalog_dialog = Dialog(
    Window(
        Const("Select a category:"),
        ScrollingGroup(
            Select(
                Format("{item}"),
                id="categories",
                items="CATEGORIES",
                item_id_getter=lambda item: item,
                on_click=handlers.on_category_selected,
            ),
            width=1,
            height=3,
            id="category_scroll",
        ),
        getter=get_categories,
        state=CatalogStates.CATEGORY,
    ),
    Window(
        Const("Select a subcategory:"),
        ScrollingGroup(
            Select(
                Format("{item}"),
                id="subcategories",
                items="SUBCATEGORIES",
                item_id_getter=lambda item: item,
                on_click=handlers.on_subcategory_selected,
            ),
            width=1,
            height=3,
            id="subcategory_scroll",
        ),
        getter=get_subcategories,
        state=CatalogStates.SUBCATEGORY,
    ),
    Window(
        Const("Select an item:"),
        ScrollingGroup(
            Select(
                Format("{item}"),
                id="items",
                items="ITEMS",
                item_id_getter=lambda item: item,
                on_click=handlers.on_item_selected,
            ),
            width=1,
            height=3,
            id="item_scroll",
        ),
        getter=get_items,
        state=CatalogStates.ITEM,
    ),
)


def setup_start_handlers(dp: Dispatcher):
    @dp.message(Command('start'))
    async def start(message: Message, dialog_manager: DialogManager):
        logger.info(message)
        await dialog_manager.start(StartStates.MAIN, mode=StartMode.RESET_STACK)

    dp.update.middleware(SubscriptionMiddleware())
    dp.include_router(start_dialog)


def setup_catalog_handlers(dp: Dispatcher):
    dp.include_router(catalog_dialog)
