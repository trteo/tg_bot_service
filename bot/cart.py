import json

from aiogram.exceptions import TelegramBadRequest
from aiogram.types import CallbackQuery, Message, LabeledPrice
from aiogram_dialog import StartMode, DialogManager
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Button
from loguru import logger
from sqlalchemy import delete, update
from sqlalchemy import select

from bot.db.models import CartProducts, Product, Order, OrderProducts, OrderStatusEnum
from bot.db.session import async_session
from bot.states import CartStates
from bot.states import StartStates
from settings.config import settings


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


async def accept_delivery_address(message: Message, message_input: MessageInput, dialog_manager: DialogManager):
    address = message.text
    print(f'Address: {address}')
    dialog_manager.current_context().dialog_data["delivery_address"] = address
    # TODO create order
    await dialog_manager.switch_to(CartStates.ADDRESS_CONFIRM)


async def get_entered_addr(dialog_manager: DialogManager, **kwargs):
    return {'entered_addr': dialog_manager.current_context().dialog_data["delivery_address"]}


async def register_order(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    user_id = dialog_manager.event.from_user.id
    delivery_address = dialog_manager.current_context().dialog_data["delivery_address"]

    # Create Order
    async with async_session() as session:
        order = Order(
            delivery_address=delivery_address,
            client_id=user_id,
            status=OrderStatusEnum.REGISTERED.value,
        )
        session.add(order)
        await session.commit()

    # Create Order Items
    async with async_session() as session:
        cart_items = (await session.execute(
            select(CartProducts, Product)
            .join(Product, CartProducts.product_id == Product.id)
            .filter(CartProducts.client_id == user_id)
        )).all()
        order_products = [
            OrderProducts(
                order_id=order.id,
                product_id=cart_item.product_id,
                amount=cart_item.amount,
                price=product.price,
            )
            for cart_item, product in cart_items
        ]

        session.add_all(order_products)
        await session.commit()

    # Flush users cart
        for cart_item, _ in cart_items:
            await session.delete(cart_item)
        await session.commit()
    dialog_manager.dialog_data['created_order_id'] = order.id
    await dialog_manager.switch_to(CartStates.PAYMENT)


async def confirm_cart_and_send_invoice(
        event: CallbackQuery,
        button: Button,
        dialog_manager: DialogManager,
):
    chat_id = event.from_user.id
    order_id = dialog_manager.dialog_data['created_order_id']

    async with async_session() as session:
        order_items = (await session.execute(
            select(OrderProducts, Product)
            .join(Product, OrderProducts.product_id == Product.id)
            .filter(OrderProducts.id == order_id)
        )).all()

    # Build cart description and total cost
    description = "Your cart items:\n"
    prices = []
    total_price = 0
    for ordered_item, item in order_items:
        item_sun_price = float(item.price) * ordered_item.amount
        description += f"{item.name} (x{ordered_item.amount}): {item_sun_price} RUB\n"
        prices.append(LabeledPrice(label=item.name, amount=int(item_sun_price * 100)))  # Telegram uses cents
        total_price += item_sun_price

    description += f"\nTotal: {total_price} RUB"
    logger.info(f'prices: {prices}')
    try:
        await event.bot.send_invoice(
            chat_id=chat_id,
            title="Your Cart Purchase",
            description=description,
            payload=json.dumps({'order_id': order_id, 'status': 'success'}),
            provider_token=settings.PAYMENT_TOKEN.get_secret_value(),
            currency="RUB",
            prices=prices,
            start_parameter="purchase",
        )
    except TelegramBadRequest:
        await event.message.answer("Something went wrong. Try again later")
        await dialog_manager.switch_to(CartStates.VIEW_CART)
