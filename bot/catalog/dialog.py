from aiogram_dialog import Dialog, Window, StartMode
from aiogram_dialog.widgets.kbd import Row, Button, Counter
from aiogram_dialog.widgets.kbd import ScrollingGroup, Select
from aiogram_dialog.widgets.text import Const
from aiogram_dialog.widgets.text import Format

from bot.catalog.handlers import get_product_details, get_subcategories, get_categories, get_items, \
    on_category_selected, on_subcategory_selected, on_item_selected, on_add_to_cart
from bot.states import StartStates, CatalogStates

catalog_dialog = Dialog(
    Window(
        Const("Select a category:"),
        ScrollingGroup(
            Select(
                Format("{item[name]}"),
                id="categories",
                items="CATEGORIES",
                item_id_getter=lambda item: item.get('id'),
                on_click=on_category_selected,
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
                on_click=on_subcategory_selected,
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
                on_click=on_item_selected,
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
                on_click=on_add_to_cart,
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
