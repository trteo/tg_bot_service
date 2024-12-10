from aiogram import Dispatcher
from aiogram.filters import Command
from aiogram.types import Message
from aiogram_dialog import Dialog, Window, StartMode, DialogManager
from aiogram_dialog.widgets.kbd import Row, Button, Counter
from aiogram_dialog.widgets.kbd import ScrollingGroup, Select
from aiogram_dialog.widgets.text import Const
from aiogram_dialog.widgets.text import Format
from loguru import logger

from bot import handlers
from bot.cart import get_product_details
from bot.categories import get_subcategories, get_categories, get_items
from bot.faq import get_questions, get_answer
from bot.middleware import SubscriptionMiddleware
from bot.states import StartStates, CatalogStates, FAQStates

# Start
start_dialog = Dialog(
    Window(
        Const('Welcome to the bot! Choose an option:'),
        Row(
            Button(
                Const("'🛒 Catalog'"),
                id='catalog',
                on_click=lambda c, d, m: m.start(CatalogStates.CATEGORY, mode=StartMode.RESET_STACK)
            ),
            Button(
                Const("'🛍️ Cart'"),
                id='cart',
                on_click=handlers.on_cart
            ),
            Button(
                Const("'❓ FAQ'"),
                id='faq',
                # on_click=lambda c, d, m: m.start(FAQStates.FAQ_CATEGORY, mode=StartMode.RESET_STACK)
                on_click=lambda c, d, m: m.start(FAQStates.QUESTION, mode=StartMode.RESET_STACK)
            ),
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
                Format("{item[name]}"),
                id="categories",
                items="CATEGORIES",
                item_id_getter=lambda item: item.get('id'),
                on_click=handlers.on_category_selected,
            ),
            width=1,
            height=3,
            id="category_scroll",
        ),
        Row(Button(
            Const("⬅️ Back"),
            id="back_to_categories",
            on_click=lambda c, d, m: m.start(StartStates.MAIN, mode=StartMode.RESET_STACK),
        )),
        getter=get_categories,
        state=CatalogStates.CATEGORY,
    ),
    Window(
        Const("Select a subcategory:"),
        ScrollingGroup(
            Select(
                Format("{item[name]}"),
                id="subcategories",
                items="SUBCATEGORIES",
                item_id_getter=lambda item: item.get('id'),
                on_click=handlers.on_subcategory_selected,
            ),
            width=1,
            height=3,
            id="subcategory_scroll",
        ),
        Row(Button(
            Const("⬅️ Back"),
            id="back_to_categories",
            on_click=lambda c, d, m: m.switch_to(CatalogStates.CATEGORY),
        )),
        getter=get_subcategories,
        state=CatalogStates.SUBCATEGORY,
    ),
    Window(
        Const("Select an item:"),
        ScrollingGroup(
            Select(
                Format("{item[name]}"),
                id="items",
                items="ITEMS",
                item_id_getter=lambda item: item.get('id'),
                on_click=handlers.on_item_selected,
            ),
            width=1,
            height=3,
            id="item_scroll",
        ),
        Row(Button(
            Const("⬅️ Back"),
            id="back_to_categories",
            on_click=lambda c, d, m: m.switch_to(CatalogStates.SUBCATEGORY),
        )),
        getter=get_items,
        state=CatalogStates.ITEM,
    ),
    Window(
        Format("{product_details}"),
        Counter(
            id="amount",
            min_value=1,
            max_value=99,
            default=1
        ),
        Row(
            Button(
                Const("🛒 Add to Cart"),
                id="add_to_cart",
                on_click=handlers.on_add_to_cart,
            ),
            Button(
                Const("⬅️ Back"),
                id="back_to_items",
                on_click=lambda c, d, m: m.switch_to(CatalogStates.ITEM),
            ),
        ),
        getter=get_product_details,
        state=CatalogStates.PRODUCT_DETAILS,
    ),
)

# FAQ
faq_dialog = Dialog(
    Window(
        Const("❓ Select a question:"),
        ScrollingGroup(
            Select(
                Format("{item[question]}"),
                id="questions",
                items="QUESTIONS",
                item_id_getter=lambda item: item.get('id'),
                on_click=handlers.on_question_selected,
            ),
            width=1,
            height=5,
            id="faq_question_scroll",
        ),
        Row(Button(
            Const("⬅️ Back"),
            id="back_to_categories",
            on_click=lambda c, d, m: m.start(StartStates.MAIN, mode=StartMode.RESET_STACK)
        )),
        getter=get_questions,
        state=FAQStates.QUESTION,
    ),
    Window(
        Format("💡 {ANSWER}"),
        Row(Button(
            Const("⬅️ Back"),
            id="back_to_questions",
            on_click=lambda c, d, m: m.switch_to(FAQStates.QUESTION)
        )),
        state=FAQStates.ANSWER,
        getter=get_answer,
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


def setup_faq_handlers(dp: Dispatcher):
    dp.include_router(faq_dialog)
