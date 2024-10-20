from aiogram.fsm.state import StatesGroup, State

# Определяем состояния
class AddServiceStates(StatesGroup):
    waiting_for_service_name = State()
    waiting_for_new_service_name = State()