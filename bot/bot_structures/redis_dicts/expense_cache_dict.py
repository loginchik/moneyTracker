from bot_structures import ExpenseStates


expenses_redis_prefixes = {
    ExpenseStates.waiting_for_category_choice: 'cat_choice',
    ExpenseStates.waiting_for_subcategory_choice: 'subcat_choice',
    ExpenseStates.waiting_for_money_count: 'money_c',
    ExpenseStates.waiting_for_date_isnow_choice: 'isnow',
    ExpenseStates.waiting_for_results_confirmation: 'confirm',
}