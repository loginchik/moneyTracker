__all__ = ['register_user_commands', 'bot_commands', 'register_middleware']


from aiogram import Router
from aiogram.filters.command import Command
from aiogram.filters.state import StateFilter

from .analytics_command import analytics_message
from .start_command import start_message
from .help_command import help_message, bot_commands
from .abort_command import abort_message
from .delete_all_data_command import ask_delete_all_confirmaion, delete_all_data_message
from .export_commands import export_expenses_message, export_revenues_message
from .expenses_commands import *
from .revenue_commands import *

from middleware import UserInDBCheck
from bot_structures import ExpenseStates, RevenueStates, DeleteDataStates
from bot_inner_texts import load_commands_json


commands_dict = load_commands_json()


def register_expenses_commands(router: Router) -> None:
    router.message.register(select_expense_category, Command(commands_dict['edit_db']['new_expense']['command']), StateFilter(None))
    router.callback_query.register(get_expense_category_callback, StateFilter(ExpenseStates.waiting_for_category_choice))
    router.message.register(save_new_category_name, StateFilter(ExpenseStates.waiting_for_new_category_name))
    
    router.callback_query.register(get_expense_subcategory_callback, StateFilter(ExpenseStates.waiting_for_subcategory_choice))
    router.message.register(save_new_expense_subcategory_name, StateFilter(ExpenseStates.waiting_for_new_subcategory_name))
    
    router.message.register(get_expense_money_count, StateFilter(ExpenseStates.waiting_for_money_count))
    
    router.callback_query.register(get_expense_date_is_now_callback, StateFilter(ExpenseStates.waiting_for_date_isnow_choice))
    router.message.register(save_expense_specific_date, StateFilter(ExpenseStates.waiting_for_specific_date))
    
    router.callback_query.register(get_expense_confirmation_callback, StateFilter(ExpenseStates.waiting_for_results_confirmation))


def register_revenue_commands(router: Router) -> None:
    router.message.register(select_revenue_category, Command(commands_dict['edit_db']['new_revenue']['command']), StateFilter(None))
    router.callback_query.register(get_revenue_category_callback, StateFilter(RevenueStates.waiting_for_category_choice))
    router.message.register(save_new_revenue_category_name, StateFilter(RevenueStates.waiting_for_new_category_name))

    router.callback_query.register(get_revenue_type_callback, StateFilter(RevenueStates.waiting_for_type_choice))
    router.message.register(save_new_revenue_type_name, StateFilter(RevenueStates.waiting_for_new_type_name))

    router.message.register(get_revenue_money_count, StateFilter(RevenueStates.waiting_for_money_count))
    
    router.callback_query.register(get_revenue_isnow_callback, StateFilter(RevenueStates.waiting_for_date_isnow_choice))
    router.message.register(save_specific_revenue_date, StateFilter(RevenueStates.waiting_for_specific_date))
    
    router.callback_query.register(get_revenue_confirmation_callback, StateFilter(RevenueStates.waiting_for_results_confirmation))
    
    
def register_middleware(router: Router) -> None:
    router.message.middleware(UserInDBCheck())
    router.callback_query.middleware(UserInDBCheck())
    

def register_abort_command(router: Router) -> None:
    router.message.register(abort_message, Command(commands_dict['edit_db']['abort']['command']), ~StateFilter(None))


def register_user_commands(router: Router) -> None:
    router.message.register(start_message, Command(commands_dict['basic']['start']['command']), StateFilter(None))
    router.message.register(help_message, Command(commands_dict['basic']['help']['command']))
    
    router.message.register(export_expenses_message, Command(commands_dict['export']['expense']['command']), StateFilter(None))
    router.message.register(export_revenues_message, Command(commands_dict['export']['revenue']['command']), StateFilter(None))
    
    register_abort_command(router=router)
    register_expenses_commands(router=router)
    register_revenue_commands(router=router)    
    
    router.message.register(ask_delete_all_confirmaion, Command(commands_dict['edit_db']['delete_data']['command']), StateFilter(None))
    router.message.register(delete_all_data_message, StateFilter(DeleteDataStates.waiting_confirmation))
    
    router.message.register(analytics_message, Command(commands_dict['analytics']['get_url']['command']))