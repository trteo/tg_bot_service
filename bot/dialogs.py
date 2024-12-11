import json

from aiogram import Dispatcher, Bot
from aiogram import F
from aiogram.filters import Command
from aiogram.types import Message, PreCheckoutQuery
from aiogram_dialog import Dialog, Window, StartMode, DialogManager
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Row, Button, Counter
from aiogram_dialog.widgets.kbd import ScrollingGroup, Select
from aiogram_dialog.widgets.text import Const
from aiogram_dialog.widgets.text import Format
from loguru import logger
from sqlalchemy import update

from bot import handlers
from bot.cart import (
    get_cart_data, on_prev, on_next, on_set_quantity, on_remove_item, remove_item_from_cart_db,
    set_item_in_cart_quantity_db, accept_delivery_address, get_entered_addr, register_order,
    confirm_cart_and_send_invoice
)
from bot.categories import get_product_details, get_subcategories, get_categories, get_items
from bot.db.models import Order, OrderStatusEnum
from bot.db.session import async_session
from bot.faq import get_questions, get_answer
from bot.middleware import SubscriptionMiddleware
from bot.states import StartStates, CatalogStates, FAQStates, CartStates

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
                on_click=lambda c, d, m: m.start(CartStates.VIEW_CART, mode=StartMode.RESET_STACK)
            ),
            Button(
                Const("'❓ FAQ'"),
                id='faq',
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


# Create the dialog
cart_dialog = Dialog(
    Window(
        Const(
            'Cart is empty now.',
            when=F["cart_empty"],
        ),
        Format(
            "🛒 **Item {index}/{total_items}**\n\n"
            "🔹 **Name:** {item[name]}\n"
            "🔢 **Quantity:** {item[quantity]}\n"
            "💲 **Price:** {item[price]:.2f}\n"
            "💰 **Total:** {item[total]:.2f}",
            when=~F["cart_empty"],
        ),
        Row(
            Button(Const("⬅️ Previous"), id="prev", on_click=on_prev),
            Button(Const("📝 Set Quantity"), id="set_quantity", on_click=on_set_quantity),
            Button(Const("🗑 Remove Item"), id="remove_item", on_click=on_remove_item),
            Button(Const("➡️ Next"), id="next", on_click=on_next),
            when=~F["cart_empty"],
        ),
        Row(
            Button(
                Const("⬅️ Back"),
                id="back_to_categories",
                on_click=lambda c, d, m: m.start(StartStates.MAIN, mode=StartMode.RESET_STACK),
            ),
            Button(
                Const("✅ Confirm"),
                id="confirm_cart",
                on_click=lambda c, d, m: m.switch_to(CartStates.ENTER_ADDRESS),
                when=~F["cart_empty"],
            ),

        ),
        state=CartStates.VIEW_CART,
        getter=get_cart_data,
    ),
    Window(
        Const("Enter your delivery address:"),
        MessageInput(accept_delivery_address),
        Button(
            Const("⬅️ Back"),
            id="back_to_categories",
            on_click=lambda c, d, m: m.start(CartStates.VIEW_CART),
        ),
        state=CartStates.ENTER_ADDRESS,
    ),
    Window(
        Format("Deliver to:\n{entered_addr}?"),
        Row(
            Button(
                Const("⬅️ Back"),
                id="back_to_categories",
                on_click=lambda c, d, m: m.switch_to(CartStates.ENTER_ADDRESS),
            ),
            Button(
                Const("✅ Confirm"),
                id="confirm_cart",
                on_click=register_order
            ),
        ),
        state=CartStates.ADDRESS_CONFIRM,
        getter=get_entered_addr,
    ),
    Window(
        Const("Review your cart and confirm payment:"),
        Button(Const("Pay Now"), id="pay_now", on_click=confirm_cart_and_send_invoice),
        state=CartStates.PAYMENT,
    ),
)


def setup_start_handlers(dp: Dispatcher):
    @dp.message(Command('start'))
    async def start(message: Message, dialog_manager: DialogManager):
        logger.info(message)
        await dialog_manager.start(StartStates.MAIN, mode=StartMode.RESET_STACK)

    @dp.pre_checkout_query()
    async def pre_checkout_query_handler(pre_checkout_query: PreCheckoutQuery, bot: Bot):
        await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)

    dp.update.middleware(SubscriptionMiddleware())
    dp.include_router(start_dialog)

    @dp.message(F.successful_payment)
    async def successful_payment_handler(message: Message, dialog_manager: DialogManager):
        payload = json.loads(message.successful_payment.invoice_payload)

        if payload.get('status', '') != "success":
            new_status = OrderStatusEnum.PAY_FAILED
            await message.answer("Sorry, something went wrong")
        else:
            new_status = OrderStatusEnum.PAID
            await message.answer("Thank you! Your payment was successful. Your order is now being processed.")
        async with async_session() as session:
            await session.execute(
                update(Order)
                .where(Order.id == payload.get('order_id'))
                .values(status=new_status.value)
            )
            await session.commit()
        await dialog_manager.start(StartStates.MAIN, mode=StartMode.RESET_STACK)

    @dp.message(lambda message: message.text and message.text.isdigit())
    async def set_quantity_handler(message: Message, dialog_manager: DialogManager):
        if dialog_manager.dialog_data.get("waiting_for_quantity"):
            dialog_manager.dialog_data["waiting_for_quantity"] = False

            new_quantity = int(message.text)
            cart_items = dialog_manager.dialog_data["cart_items"]
            current_index = dialog_manager.dialog_data.get("index", 0)

            if new_quantity <= 0:
                removed_item = cart_items.pop(current_index)
                await remove_item_from_cart_db(cart_product_id=removed_item.get('id'))
                await message.answer("Item removed from the cart due to zero or negative quantity.")
            else:
                cart_items[current_index]["quantity"] = new_quantity
                cart_items[current_index]["total"] = cart_items[current_index]["price"] * new_quantity
                await set_item_in_cart_quantity_db(
                    cart_product_id=cart_items[current_index].get('id'),
                    quantity=new_quantity
                )
                await message.answer(f"Quantity updated to {new_quantity}.")

            await dialog_manager.start(CartStates.VIEW_CART)


def setup_catalog_handlers(dp: Dispatcher):
    dp.include_router(catalog_dialog)


def setup_faq_handlers(dp: Dispatcher):
    dp.include_router(faq_dialog)


def setup_cart_handlers(dp: Dispatcher):
    dp.include_router(cart_dialog)
