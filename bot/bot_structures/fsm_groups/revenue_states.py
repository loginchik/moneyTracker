from aiogram.fsm.state import State, StatesGroup


class RevenueStates(StatesGroup):
    waiting_for_category_choice = State()
    waiting_for_new_category_name = State()
    
    waiting_for_type_choice = State()
    waiting_for_new_type_name = State()
    
    waiting_for_money_count = State()
    
    waiting_for_date_isnow_choice = State()
    waiting_for_specific_date = State()
    
    waiting_for_results_confirmation = State()