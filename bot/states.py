from aiogram.fsm.state import StatesGroup, State


# Dialog States
class CatalogStates(StatesGroup):
    CATEGORY = State()
    SUBCATEGORY = State()
    ITEM = State()


# Dialog States
class StartStates(StatesGroup):
    MAIN = State()


# Dialog States
class FAQStates(StatesGroup):
    FAQ_CATEGORY = State()
    QUESTION = State()
    ANSWER = State()
