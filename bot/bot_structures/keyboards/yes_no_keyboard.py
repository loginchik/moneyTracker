from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton

def make_binary_keyboard(yes_text, no_text):
    yes_no_inline_keyboard = InlineKeyboardBuilder()

    for button_text, button_callback in zip([yes_text, no_text], ['yes', 'no']):
        this_button = InlineKeyboardButton(text=button_text, callback_data=button_callback)
        yes_no_inline_keyboard.add(this_button)
        
    yesNo_keyboard = yes_no_inline_keyboard.as_markup()
    return yesNo_keyboard