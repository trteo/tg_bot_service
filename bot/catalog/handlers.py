from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.kbd import Button, Select
from loguru import logger
from sqlalchemy import select

from bot.db.models import ProductCategory, Product, CartProducts
from bot.db.session import async_session
from bot.states import CatalogStates


async def get_categories(dialog_manager: DialogManager, **kwargs) -> dict:
    """Fetch all top-level categories."""
    async with async_session() as session:
        response = {"CATEGORIES": [  # TODO move to select items names Enum
            {'id': product_category.id, 'name': product_category.name}  # TODO use Dataclasses
            for product_category in (await session.scalars(
                select(ProductCategory).filter(ProductCategory.parent_category_id.is_(None))
            )).all()
        ]}
        logger.info(f'Selected categories: {response}')
        return response


async def get_subcategories(dialog_manager: DialogManager, **kwargs) -> dict:
    """Fetch all subcategories for a given category."""
    category_id = int(
        dialog_manager.current_context().dialog_data.get("selected_category", "")
    )  # TODO declare key somewhere
    logger.info(f'Selected category_id: {category_id}')

    async with async_session() as session:
        response = {"SUBCATEGORIES": [  # TODO move to select items names Enum
            {'id': product_subcategory.id, 'name': product_subcategory.name}  # TODO use Dataclasses
            for product_subcategory in (await session.scalars(
                select(ProductCategory).filter(ProductCategory.parent_category_id == category_id)))
            .all()
        ]}
        logger.info(f'Selected subcategories: {response}')
        return response


async def get_items(dialog_manager: DialogManager, **kwargs) -> dict:
    """Fetch all products for a given subcategory."""
    subcategory_id = int(
        dialog_manager.current_context().dialog_data.get("selected_subcategory", "")
    )  # TODO declare key somewhere
    logger.info(f'Selected subcategory_id: {subcategory_id}')

    async with async_session() as session:
        response = {"ITEMS": [  # TODO move to select items names Enum
            {'id': item.id, 'name': item.name}  # TODO use Dataclasses
            for item in (await session.scalars(
                select(Product).filter(Product.category_id == subcategory_id)))
            .all()
        ]}
        logger.info(f'Items selected: {response}')
        return response


async def get_item(dialog_manager: DialogManager, **kwargs):
    """Fetch products by id."""
    product_id = int(
        dialog_manager.current_context().dialog_data.get("selected_product", "")
    )  # TODO declare key somewhere
    logger.info(f'Selected product_id: {product_id}')

    async with async_session() as session:
        return {"ITEMS": [  # TODO move to select items names Enum
            {'id': item.id, 'name': item.name}  # TODO use Dataclasses
            for item in (await session.scalars(
                select(Product).filter(Product.id == product_id)))
            .all()
        ]}


async def get_product_by_id(product_id: str):
    """Fetch a product by its ID."""
    async with async_session() as session:
        return (
            await session.scalars(select(Product).filter(Product.id == int(product_id)))
        ).one()


async def get_product_details(dialog_manager: DialogManager, **kwargs) -> dict:
    product_id = dialog_manager.current_context().dialog_data.get("product_id")
    product = await get_product_by_id(product_id)
    res = {
        "product_details": (
            f"Name: {product.name}\n"
            f"Description: {product.description}\n"
            f"Price: {product.price}\n"
        )
    }
    logger.info(f'Product details: {res}')
    return res


async def on_category_selected(
        event: CallbackQuery,
        widget: Select,
        dialog_manager: DialogManager,
        selected: str
):
    dialog_manager.current_context().dialog_data["selected_category"] = selected
    await dialog_manager.switch_to(CatalogStates.SUBCATEGORY)


async def on_subcategory_selected(
        event: CallbackQuery,
        widget: Select,
        dialog_manager: DialogManager,
        selected: str
):
    dialog_manager.current_context().dialog_data["selected_subcategory"] = selected
    await dialog_manager.switch_to(CatalogStates.ITEM)


async def on_item_selected(
        event: CallbackQuery,
        widget: Select,
        dialog_manager: DialogManager,
        selected: str
):  # TODO send images
    dialog_manager.current_context().dialog_data["product_id"] = selected
    await dialog_manager.switch_to(CatalogStates.PRODUCT_DETAILS)


async def on_add_to_cart(
        event: CallbackQuery,
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

    await event.answer()
    await dialog_manager.switch_to(CatalogStates.ITEM)  # TODO redo to start with passing context