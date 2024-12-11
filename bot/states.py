from aiogram.fsm.state import StatesGroup, State


class CatalogStates(StatesGroup):
    CATEGORY = State()
    SUBCATEGORY = State()
    ITEM = State()
    PRODUCT_DETAILS = State()


class StartStates(StatesGroup):
    MAIN = State()


class FAQStates(StatesGroup):
    QUESTION = State()
    ANSWER = State()


class CartStates(StatesGroup):
    VIEW_CART = State()
    ENTER_ADDRESS = State()
    PAYMENT = State()
