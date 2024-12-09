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
    CATEGORY = State()
    QUESTION = State()
    ANSWER = State()
