import aiosqlite
import subprocess
from aiogram import Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery

from functions import get_service_info, get_service_status, is_service_exist
from FSM import AddServiceStates
from handlers.admin_kb import create_service_keyboard

router = Router()

# Обработка действий для выбранной службы
@router.callback_query(F.data.startswith("service_"))
async def handle_service_action(callback_query: CallbackQuery):
    await callback_query.answer()
    service_name = callback_query.data.split("service_")[1]
    service_info = get_service_info(service_name)
    status = get_service_status(service_name)
    status_icon = "✅" if status == "active" else "❌"
    # Сообщение с информацией о службе
    text = (f"Вы выбрали службу {service_name}{status_icon}.\n"
            f"Статус: {service_info['is_active']}\n"
            f"PID: {service_info['pid']}\n"
            f"Память: {service_info['memory']} М\n"
            f"CPU: {service_info['cpu']}s\n"
            f"Выберите действие👇")
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Перезапустить", callback_data=f"restart_{service_name}")],
            [InlineKeyboardButton(text="Включить" if status == "inactive" else "Выключить", callback_data=f"toggle_{service_name}")],
            [InlineKeyboardButton(text="Редактировать", callback_data=f"edit_{service_name}")],
            [InlineKeyboardButton(text="Удалить", callback_data=f"delete_{service_name}")]
        ]
    )
    await callback_query.message.answer(f"{text}", reply_markup=keyboard)

# Перезапуск службы
@router.callback_query(F.data.startswith("restart_"))
async def restart_service(callback_query: CallbackQuery, bot: Bot) -> None:
    await callback_query.answer()
    service_name = callback_query.data.split("restart_")[1]
    # Проверяем, существует ли служба на уровне системы
    if is_service_exist(service_name):
        subprocess.run(["sudo", "systemctl", "restart", service_name], check=True)
        await callback_query.message.answer(f"Служба {service_name} перезапущена")
        # Обновляем статус в базе данных
        async with aiosqlite.connect("database.db") as db:
            await db.execute("UPDATE services SET status = ? WHERE name = ?", ("active", service_name))
            await db.commit()
    else:
        await callback_query.message.answer(f"Служба {service_name} не существует в системе")
    keyboard, _ = await create_service_keyboard()
    await bot.send_message(chat_id=callback_query.from_user.id, text="Cписок служб:", reply_markup=keyboard)

# Включение или выключение службы
@router.callback_query(F.data.startswith("toggle_"))
async def toggle_service(callback_query: CallbackQuery, bot: Bot):
    await callback_query.answer()
    service_name = callback_query.data.split("toggle_")[1]
    # Проверяем, существует ли служба на уровне системы
    if is_service_exist(service_name):
        status = get_service_status(service_name)
        if status == "active":
            # Останавливаем службу
            subprocess.run(["sudo", "systemctl", "stop", service_name], check=True)
            new_status = "inactive"
            await callback_query.message.answer(f"Служба {service_name} выключена")
        else:
            # Запускаем службу
            subprocess.run(["sudo", "systemctl", "start", service_name], check=True)
            new_status = "active"
            await callback_query.message.answer(f"Служба {service_name} включена")
        # Обновляем статус в базе данных
        async with aiosqlite.connect("database.db") as db:
            await db.execute("UPDATE services SET status = ? WHERE name = ?", (new_status, service_name))
            await db.commit()
    else:
        await callback_query.message.answer(f"Служба {service_name} не существует в системе")
    keyboard, _ = await create_service_keyboard()
    await bot.send_message(chat_id=callback_query.from_user.id, text="Cписок служб:", reply_markup=keyboard)

# Функция для редактирования названия службы
@router.callback_query(F.data.startswith("edit_"))
async def edit_service(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.answer()
    service_name = callback_query.data.split("edit_")[1]
    # Сохраняем имя редактируемой службы в состоянии
    await state.update_data(service_name=service_name)
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Назад", callback_data=f"service_{service_name}")]])
    await callback_query.message.answer(f"Введите новое название для службы {service_name}:", reply_markup=keyboard)
    await state.set_state(AddServiceStates.waiting_for_new_service_name)

# Обработчик ввода нового названия службы
@router.message(AddServiceStates.waiting_for_new_service_name)
async def edit_service(message: Message, state: FSMContext):
    data = await state.get_data()
    old_service_name = data.get("service_name")
    new_service_name = message.text
    # Здесь обновляем название службы в базе данных
    async with aiosqlite.connect("database.db") as db:
        async with db.execute("UPDATE services SET name = ? WHERE name = ?", (new_service_name, old_service_name)) as cursor:
            # Проверка, было ли обновлено хотя бы одно значение
            if cursor.rowcount == 0:
                await message.answer(f"Служба с названием {old_service_name} не найдена")
            else:
                await message.answer(f"Служба {old_service_name} переименована в {new_service_name}")
            await db.commit()
    await state.update_data(service_name=None) # Сбрасываем состояние
    keyboard, _ = await create_service_keyboard()
    await message.answer("Cписок служб:", reply_markup=keyboard)

# Функция для удаления службы
@router.callback_query(F.data.startswith("delete_"))
async def delete_service(callback_query: CallbackQuery, bot: Bot):
    await callback_query.answer()
    # Получаем имя службы из callback_data
    service_name = callback_query.data.split("delete_")[1]
    # Проверяем, существует ли служба на уровне системы
    if is_service_exist(service_name):
        try:
            # Останавливаем службу перед удалением
            subprocess.run(["sudo", "systemctl", "stop", service_name], check=True)
        except subprocess.CalledProcessError as e:
            await callback_query.message.answer(f"Не удалось остановить службу {service_name}: {e}")
            return
    # Удаляем службу из базы данных
    async with aiosqlite.connect("database.db") as db:
        async with db.execute("DELETE FROM services WHERE name = ?", (service_name,)) as cursor:
            await db.commit()
            if cursor.rowcount > 0:
                await bot.send_message(callback_query.from_user.id, f"Служба {service_name} удалена")
            else:
                await bot.send_message(callback_query.from_user.id, f"Служба {service_name} не найдена в базе данных")
    keyboard, _ = await create_service_keyboard()
    await bot.send_message(chat_id=callback_query.from_user.id, text="Cписок служб:", reply_markup=keyboard)