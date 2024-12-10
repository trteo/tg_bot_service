from aiogram import types
from aiogram_dialog import StartMode, DialogManager
from aiogram_dialog.widgets.kbd import Select, Button
from sqlalchemy import select

from bot.db.models import CartProducts, Product
from bot.db.session import async_session
from bot.states import CatalogStates, FAQStates


# Start on-click routs
async def on_cart(event: types.CallbackQuery, widget, dialog_manager):
    await event.message.answer("Opening Cart...")
    await event.answer()


# Category routing
async def on_category_selected(
        event: types.CallbackQuery,
        widget: Select,
        dialog_manager: DialogManager,
        selected: str
):
    dialog_manager.current_context().dialog_data["selected_category"] = selected
    await dialog_manager.switch_to(CatalogStates.SUBCATEGORY)


async def on_subcategory_selected(
        event: types.CallbackQuery,
        widget: Select,
        dialog_manager: DialogManager,
        selected: str
):
    dialog_manager.current_context().dialog_data["selected_subcategory"] = selected
    await dialog_manager.switch_to(CatalogStates.ITEM)


async def on_item_selected(
        event: types.CallbackQuery,
        widget: Select,
        dialog_manager: DialogManager,
        selected: str
):  # TODO send images
    dialog_manager.current_context().dialog_data["product_id"] = selected
    await dialog_manager.switch_to(CatalogStates.PRODUCT_DETAILS)


# FAQ routing
async def on_faq_category_selected(
        event: types.CallbackQuery,
        widget: Select,
        dialog_manager: DialogManager,
        selected: str
):
    dialog_manager.current_context().dialog_data["selected_faq_category"] = selected
    await dialog_manager.switch_to(FAQStates.QUESTION)


async def on_question_selected(
        event: types.CallbackQuery,
        widget: Select,
        dialog_manager: DialogManager,
        selected: str
):
    dialog_manager.current_context().dialog_data["question_id"] = selected
    await dialog_manager.switch_to(FAQStates.ANSWER)


# Cart
async def on_add_to_cart(
        event: types.CallbackQuery,
        widget: Button,
        dialog_manager: DialogManager,
        # selected: str
):
    user_id = event.from_user.id
    product_id = dialog_manager.current_context().dialog_data["product_id"]
    amount = dialog_manager.current_context().widget_data["amount"]

    async with async_session() as session:
        existing_cart_item = await session.execute(
            select(CartProducts).where(
                CartProducts.client_id == int(user_id),
                CartProducts.product_id == int(product_id)
            )
        )
        existing_cart_item = existing_cart_item.scalars().first()

        if existing_cart_item:
            existing_cart_item.amount += int(amount)
            await session.commit()
            await event.message.answer(
                f"Product already in cart. Updated quantity: {existing_cart_item.amount}."
            )
        else:
            session.add(
                CartProducts(client_id=int(user_id), product_id=int(product_id), amount=int(amount))
            )
            await session.commit()
            await event.message.answer(
                f"Product added to cart (Quantity: {amount})."
            )

    await event.answer()
    await dialog_manager.switch_to(CatalogStates.ITEM)
