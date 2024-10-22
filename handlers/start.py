from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from keyboards import start_kb

router = Router()

@router.message(CommandStart())
async def start_command(message: Message, is_admin: bool) -> None:
    if is_admin:
        await message.answer("Вы администратор. Выберите действие:", reply_markup=start_kb)
    else:
        await message.answer("У вас нет доступа к функционалу бота")