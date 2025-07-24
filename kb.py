from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


def main_kb(user_telegram_id: int):
    kb_list = [
        [
            KeyboardButton(text="Получить последнее"),
        ],
    ]

    keyboard = ReplyKeyboardMarkup(
        keyboard=kb_list,
        resize_keyboard=True,
        input_field_placeholder="Воспользуйтесь меню:",
    )
    return keyboard
