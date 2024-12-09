from aiogram.fsm.state import StatesGroup, State


class CatalogStates(StatesGroup):
    CATEGORY = State()
    SUBCATEGORY = State()
    ITEM = State()


class StartStates(StatesGroup):
    MAIN = State()


class FAQStates(StatesGroup):
    FAQ_CATEGORY = State()
    QUESTION = State()
    ANSWER = State()
