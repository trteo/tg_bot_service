from loguru import logger
from sqlalchemy import select

from bot.db.models import ProductCategory, Product
from bot.db.session import async_session


async def get_categories(dialog_manager, **kwargs):
    """Fetch all top-level categories."""
    async with async_session() as session:
        return {"CATEGORIES": [  # TODO move to select items names Enum
            {'id': product_category.id, 'name': product_category.name}  # TODO use Dataclasses
            for product_category in (await session.scalars(
                select(ProductCategory).filter(ProductCategory.parent_category_id.is_(None))
            )).all()
        ]}


async def get_subcategories(dialog_manager, **kwargs):
    """Fetch all subcategories for a given category."""
    category_id = int(
        dialog_manager.current_context().dialog_data.get("selected_category", "")
    )  # TODO declare key somewhere
    logger.info(f'Selected category_id: {category_id}')

    async with async_session() as session:
        return {"SUBCATEGORIES": [  # TODO move to select items names Enum
            {'id': product_subcategory.id, 'name': product_subcategory.name}  # TODO use Dataclasses
            for product_subcategory in (await session.scalars(
                select(ProductCategory).filter(ProductCategory.parent_category_id == category_id)))
            .all()
        ]}


async def get_items(dialog_manager, **kwargs):
    """Fetch all products for a given subcategory."""
    subcategory_id = int(
        dialog_manager.current_context().dialog_data.get("selected_subcategory", "")
    )  # TODO declare key somewhere
    logger.info(f'Selected subcategory_id: {subcategory_id}')

    async with async_session() as session:
        return {"ITEMS": [  # TODO move to select items names Enum
            {'id': item.id, 'name': item.name}  # TODO use Dataclasses
            for item in (await session.scalars(
                select(Product).filter(Product.category_id == subcategory_id)))
            .all()
        ]}


async def get_item(dialog_manager, **kwargs):
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
