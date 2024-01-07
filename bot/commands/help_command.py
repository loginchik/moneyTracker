from aiogram import types
from aiogram.fsm.context import FSMContext

from bot_structures import RevenueStates, ExpenseStates
from bot_inner_texts import load_commands_json, load_states_json, load_message_texts_json


commands_descr = load_commands_json()
states_descr = load_states_json()
message_texts  = load_message_texts_json()

bot_commands = (
    (commands_descr['basic']['start']['command'], commands_descr['basic']['start']['descr']),
    (commands_descr['basic']['help']['command'], commands_descr['basic']['help']['descr']), 
    
    (commands_descr['edit_db']['new_expense']['command'], commands_descr['edit_db']['new_expense']['descr']),
    (commands_descr['edit_db']['new_revenue']['command'], commands_descr['edit_db']['new_revenue']['descr']),
    
    (commands_descr['analytics']['get_url']['command'], commands_descr['analytics']['get_url']['descr']),
    
    (commands_descr['export']['expense']['command'], commands_descr['export']['expense']['descr']),
    (commands_descr['export']['revenue']['command'], commands_descr['export']['revenue']['descr']),
    
    (commands_descr['edit_db']['delete_data']['command'], commands_descr['edit_db']['delete_data']['descr']),
    
    (commands_descr['basic']['about']['command'], commands_descr['basic']['about']['descr'])
)

bot_commands_str = '\n'.join([f'/{cmd_tuple[0]} - {cmd_tuple[1].lower()}' for cmd_tuple in bot_commands])
basic_help_text_list = [
    message_texts['basic']['help']['header'], 
    bot_commands_str, 
    message_texts['basic']['help']['bottom'],
]
basic_help_text = '\n\n'.join(basic_help_text_list)


def generage_expenses_help_dict(abort_text: str) -> dict:
    expense_states = [
        ExpenseStates.waiting_for_category_choice, 
        ExpenseStates.waiting_for_new_category_name, 
        ExpenseStates.waiting_for_subcategory_choice, 
        ExpenseStates.waiting_for_new_subcategory_name, 
        ExpenseStates.waiting_for_money_count, 
        ExpenseStates.waiting_for_date_isnow_choice, 
        ExpenseStates.waiting_for_specific_date, 
        ExpenseStates.waiting_for_results_confirmation
    ]
    second_keys = ['category_choice', 'new_category', 'subcategory_choice', 'new_subcategory', 'money', 'is_now', 'specific_date', 'confirm']
    
    dict_to_return = dict()
    for state, second_key in zip(expense_states, second_keys):
        dict_to_return[state] = states_descr['expenses'][second_key] + '\n\n' + abort_text

def generate_revenues_help_dict(abort_text: str) -> dict:
    states = [
        RevenueStates.waiting_for_category_choice, 
        RevenueStates.waiting_for_new_category_name, 
        RevenueStates.waiting_for_type_choice, 
        RevenueStates.waiting_for_new_type_name, 
        RevenueStates.waiting_for_money_count, 
        RevenueStates.waiting_for_date_isnow_choice, 
        RevenueStates.waiting_for_specific_date, 
        RevenueStates.waiting_for_results_confirmation
    ]
    second_keys = ['category_choice', 'new_category', 'type_choice', 'new_type', 'money', 'is_now', 'specific_date', 'confirm']

    dict_to_return = dict()
    for state, second_key in zip(states, second_keys):
        dict_to_return[state] = states_descr['revenue'][second_key] + '\n\n' + abort_text


expense_help = generage_expenses_help_dict(abort_text=message_texts['basic']['help']['abort_text'])
revenue_help = generate_revenues_help_dict(abort_text=message_texts['basic']['help']['abort_text'])


async def help_message(message: types.Message, state: FSMContext) -> None:
    current_state = await state.get_state()
    if current_state is None:
        await message.answer(basic_help_text)
    else:
        if current_state in list(expense_help.keys()):
            message_text = expense_help[current_state]
        elif current_state in list(revenue_help.keys()):
            message_text = revenue_help[current_state]
        else:
            message_text = basic_help_text
        await message.reply(message_text)