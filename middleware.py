from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message
from config import ADMINS

class AdminCheckMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):
        # Проверяем, является ли событие от администратора
        user_id = event.from_user.id if isinstance(event, (CallbackQuery, Message)) else None
        if user_id and user_id in ADMINS:
            data['is_admin'] = True  # Передаем информацию о том, что пользователь админ
        else:
            data['is_admin'] = False

        # Если это CallbackQuery и пользователь не админ, выводим сообщение и блокируем действие
        if isinstance(event, CallbackQuery) and not data['is_admin']:
            await event.answer("У вас нет прав для выполнения этого действия.", show_alert=True)
            return

        # Передаем обработку дальше, если все проверки пройдены
        return await handler(event, data)