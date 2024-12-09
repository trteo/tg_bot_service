from aiogram_dialog import DialogManager

# Static FAQ Data
FAQ_DATA = {
    "Payments": [
        {"question": "How can I update my payment method?", "answer": "You can update your payment method in the account settings."},
        {"question": "Why was my payment declined?", "answer": "Please check with your bank or ensure your payment method has sufficient funds."}
    ],
    "Technical Issues": [
        {"question": "The app is crashing, what do I do?", "answer": "Try reinstalling the app or clearing its cache from your device settings."},
        {"question": "I can't log in, help!", "answer": "Ensure your username and password are correct. Reset your password if needed."}
    ],
    "Account": [
        {"question": "How do I delete my account?", "answer": "You can delete your account in the profile settings under 'Account Management'."},
        {"question": "How can I change my email?", "answer": "Go to your profile settings and select 'Change Email'."}
    ]
}


# Getters FAQ
async def get_faq_categories(dialog_manager: DialogManager, **kwargs):
    return {"CATEGORIES": list(FAQ_DATA.keys())}


async def get_questions(dialog_manager: DialogManager, **kwargs):
    category = dialog_manager.current_context().dialog_data["selected_faq_category"]
    questions = [faq["question"] for faq in FAQ_DATA[category]]
    return {"QUESTIONS": questions}


async def get_answer(dialog_manager: DialogManager, **kwargs):
    category = dialog_manager.current_context().dialog_data["selected_faq_category"]
    question = dialog_manager.current_context().dialog_data["selected_question"]
    answer = next(
        (faq["answer"] for faq in FAQ_DATA[category] if faq["question"] == question),
        "No answer found."
    )
    return {"ANSWER": answer}
