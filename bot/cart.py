from aiogram_dialog import DialogManager
from sqlalchemy import select

from bot.db.models import Product
from bot.db.session import async_session


async def get_product_by_id(product_id):
    """Fetch a product by its ID."""
    async with async_session() as session:
        return (
            await session.scalars(select(Product).filter(Product.id == int(product_id)))
        ).one()


async def get_product_details(dialog_manager: DialogManager, **kwargs):
    product_id = dialog_manager.current_context().dialog_data.get("product_id")
    product = await get_product_by_id(product_id)
    res = {
        "product_details": (
            f"Name: {product.name}\n"
            f"Description: {product.description}\n"
            f"Price: {product.price}\n"
        )
    }
    print(res)
    return res
