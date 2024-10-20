from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup

start_kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Все заданные службы", callback_data="view_services")],
            [InlineKeyboardButton(text="Добавить новую службу", callback_data="add_service")]
        ]
    )