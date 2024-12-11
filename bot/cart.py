from aiogram.types import CallbackQuery
from aiogram_dialog import StartMode, DialogManager
from aiogram_dialog.widgets.kbd import Button
from sqlalchemy import delete, update
from sqlalchemy import select

from bot.db.models import CartProducts, Product
from bot.db.session import async_session
from bot.states import CartStates
from bot.states import StartStates


async def load_cart(dialog_manager: DialogManager, **kwargs):
    chat_id = dialog_manager.event.from_user.id

    async with async_session() as session:
        items_in_cart = (await
            session.execute(
                select(CartProducts, Product)
                .join(Product, CartProducts.product_id == Product.id)
                .filter(CartProducts.client_id == chat_id)
            )
        ).all()
    cart_items = [
        {
            "id": cart.id,
            "name": product.name,
            "quantity": cart.amount,
            "price": product.price,
            "total": product.price * cart.amount,
        }
        for cart, product in items_in_cart
    ]

    # Store the items in dialog data
    dialog_manager.dialog_data["cart_items"] = cart_items
    dialog_manager.dialog_data["index"] = 0


# Data getter to provide current cart items
async def get_cart_data(dialog_manager: DialogManager, **kwargs):
    if 'cart_items' not in dialog_manager.dialog_data:
        await load_cart(dialog_manager)

    cart_items = dialog_manager.dialog_data["cart_items"]
    if not cart_items:
        return {'cart_empty': True}

    index = dialog_manager.dialog_data.get("index", 0)
    item = cart_items[index]
    return {"item": item, "index": index + 1, "total_items": len(cart_items), 'cart_empty': False}


# Navigation callbacks handlers
async def on_next(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    cart_items = dialog_manager.dialog_data["cart_items"]
    if not cart_items:
        await dialog_manager.start(StartStates.MAIN, mode=StartMode.RESET_STACK)
        return

    current_index = dialog_manager.dialog_data.get("index", 0)
    new_index = (current_index + 1) % len(cart_items)
    dialog_manager.dialog_data["index"] = new_index
    await dialog_manager.switch_to(CartStates.VIEW_CART)


async def on_prev(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    cart_items = dialog_manager.dialog_data["cart_items"]
    if not cart_items:
        await dialog_manager.start(StartStates.MAIN, mode=StartMode.RESET_STACK)
        return

    current_index = dialog_manager.dialog_data.get("index", 0)
    new_index = (current_index - 1) % len(cart_items)
    dialog_manager.dialog_data["index"] = new_index
    await dialog_manager.switch_to(CartStates.VIEW_CART)


# Editing items
async def remove_item_from_cart_db(cart_product_id: int):
    async with async_session() as session:
        await session.execute(
            delete(CartProducts)
            .where(CartProducts.id == cart_product_id)
        )
        await session.commit()


async def set_item_in_cart_quantity_db(cart_product_id: int, quantity: int):
    async with async_session() as session:
        await session.execute(
            update(CartProducts)
            .where(CartProducts.id == cart_product_id)
            .values(amount=quantity)
        )
        await session.commit()


async def on_remove_item(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    cart_items = dialog_manager.dialog_data["cart_items"]
    if not cart_items:
        await dialog_manager.start(StartStates.MAIN, mode=StartMode.NEW_STACK)
        return
    current_index = dialog_manager.dialog_data.get("index", 0)
    await remove_item_from_cart_db(cart_product_id=int(cart_items.pop(current_index).get('id')))

    if cart_items:
        dialog_manager.dialog_data["index"] = current_index % len(cart_items)
    await dialog_manager.switch_to(CartStates.VIEW_CART)


async def on_set_quantity(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await callback.message.answer("Send me the new quantity for this item.")
    dialog_manager.dialog_data["waiting_for_quantity"] = True
