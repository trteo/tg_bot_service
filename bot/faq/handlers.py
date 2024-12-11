from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.kbd import Select
from loguru import logger
from sqlalchemy import select

from bot.db.models import FAQ
from bot.db.session import async_session
from bot.states import FAQStates


def get_striped_sentence(sentence: str, max_len: int = 32) -> str:
    if len(sentence) <= max_len:
        return sentence

    truncated = sentence[:max_len]
    last_space_index = truncated.rfind(' ')

    if last_space_index == -1:
        return truncated + "..."

    return truncated[:last_space_index] + "..."


async def get_questions(dialog_manager: DialogManager, **kwargs):
    async with async_session() as session:
        faq_db_list = (await session.scalars(select(FAQ))).all()

    questions = [
        {
            'id': faq.id,
            'question': get_striped_sentence(faq.question),
        } for faq in faq_db_list
    ]
    logger.info(f"Questions: {questions}")
    return {"QUESTIONS": questions}


async def get_answer(dialog_manager: DialogManager, **kwargs):
    question = dialog_manager.current_context().dialog_data["question_id"]
    response = 'No answer found.'
    async with async_session() as session:
        faq_db_obj = (await session.scalars(select(FAQ).filter(FAQ.id == int(question)))).one_or_none()

    if faq_db_obj:
        response = f"""Question: {faq_db_obj.question}

        Answer: {faq_db_obj.answer}
        """

    return {"ANSWER": response}


async def on_question_selected(
        event: CallbackQuery,
        widget: Select,
        dialog_manager: DialogManager,
        selected: str
):
    dialog_manager.current_context().dialog_data["question_id"] = selected
    await dialog_manager.switch_to(FAQStates.ANSWER)