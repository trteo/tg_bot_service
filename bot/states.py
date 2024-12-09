from aiogram.fsm.state import StatesGroup, State


# Dialog States
class CatalogStates(StatesGroup):
    CATEGORY = State()
    SUBCATEGORY = State()
    ITEM = State()


# Dialog States
class StartStates(StatesGroup):
    MAIN = State()

