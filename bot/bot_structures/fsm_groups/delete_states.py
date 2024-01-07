from aiogram.fsm.state import State, StatesGroup


class DeleteDataStates(StatesGroup):
    waiting_confirmation = State()