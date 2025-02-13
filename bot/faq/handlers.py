import hashlib

from aiogram.types import CallbackQuery, InlineQuery
from aiogram.types import InlineQueryResultArticle, InputTextMessageContent
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.kbd import Select
from loguru import logger
from sqlalchemy import select

from db.models import FAQ
from db.session import async_session
from bot.states import FAQStates


def get_striped_sentence(sentence: str, max_len: int = 32) -> str:
    if len(sentence) <= max_len:
        return sentence

    truncated = sentence[:max_len]
    last_space_index = truncated.rfind(' ')

    if last_space_index == -1:
        return truncated + "..."

    return truncated[:last_space_index] + "..."


async def get_questions(dialog_manager: DialogManager, **kwargs) -> dict:
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


async def get_answer(dialog_manager: DialogManager, **kwargs) -> dict:
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


async def get_matching_faqs(query: str, limit: int = 5):
    async with async_session() as session:
        return (await session.scalars(select(FAQ).filter(FAQ.question.ilike(f"%{query}%")).limit(limit))).all()


async def process_inline_input(inline_query: InlineQuery):
    query = inline_query.query.strip()
    if not query:
        return
    logger.info(f'Inline query: {query}')

    # Fetch matching questions
    matching_faqs = await get_matching_faqs(query=query)

    results = []
    for faq in matching_faqs:
        # Create unique ID for each inline result
        unique_id = hashlib.md5(f"{faq.id}".encode()).hexdigest()

        # Add each FAQ as an InlineQueryResultArticle
        results.append(
            InlineQueryResultArticle(
                id=unique_id,
                title=faq.question,
                input_message_content=InputTextMessageContent(
                    message_text=f"❓ *Question*: {faq.question}\n\n💡 *Answer*: {faq.answer}",
                    parse_mode="Markdown"
                )
            )
        )

    # Send results to user
    await inline_query.answer(results, cache_time=1)
