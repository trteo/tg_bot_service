from aiogram import types
from aiogram_dialog import StartMode, DialogManager
from aiogram_dialog.widgets.kbd import Select

from bot.states import CatalogStates, FAQStates


# Start routing
async def on_catalog(event: types.CallbackQuery, widget, dialog_manager):
    await event.message.answer("Opening Catalog...")
    await event.answer()
    await dialog_manager.start(CatalogStates.CATEGORY, mode=StartMode.RESET_STACK)


async def on_cart(event: types.CallbackQuery, widget, dialog_manager):
    await event.message.answer("Opening Cart...")
    await event.answer()


async def on_faq(event: types.CallbackQuery, widget, dialog_manager):
    await event.message.answer("Opening FAQ...")
    await event.answer()
    await dialog_manager.start(FAQStates.FAQ_CATEGORY, mode=StartMode.RESET_STACK)


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
):
    await event.message.answer(f"You selected: product with id: {selected}")
    await event.answer()


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
    dialog_manager.current_context().dialog_data["selected_question"] = selected
    await dialog_manager.switch_to(FAQStates.ANSWER)
