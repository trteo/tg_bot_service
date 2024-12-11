from aiogram_dialog import Dialog, Window, StartMode
from aiogram_dialog.widgets.kbd import Row, Button
from aiogram_dialog.widgets.kbd import ScrollingGroup, Select
from aiogram_dialog.widgets.text import Const
from aiogram_dialog.widgets.text import Format

from bot.faq.handlers import get_questions, get_answer, on_question_selected
from bot.states import StartStates, FAQStates

faq_dialog = Dialog(
    Window(
        Const("❓ Select a question:"),
        ScrollingGroup(
            Select(
                Format("{item[question]}"),
                id="questions",
                items="QUESTIONS",
                item_id_getter=lambda item: item.get('id'),
                on_click=on_question_selected,
            ),
            width=1,
            height=5,
            id="faq_question_scroll",
        ),
        Row(Button(
            Const("⬅️ Back"),
            id="back_to_categories",
            on_click=lambda c, d, m: m.start(StartStates.MAIN, mode=StartMode.RESET_STACK)
        )),
        getter=get_questions,
        state=FAQStates.QUESTION,
    ),
    Window(
        Format("💡 {ANSWER}"),
        Row(Button(
            Const("⬅️ Back"),
            id="back_to_questions",
            on_click=lambda c, d, m: m.switch_to(FAQStates.QUESTION)
        )),
        state=FAQStates.ANSWER,
        getter=get_answer,
    ),
)