from bot_structures import make_binary_keyboard, make_category_keyboard
from aiogram import types


def test_make_binary_keyboard():
    button_texts = ['Да', 'Нет']
    keyboard = make_binary_keyboard(yes_text=button_texts[0], no_text=button_texts[1])
    
    assert isinstance(keyboard, types.InlineKeyboardMarkup)
    
    
def test_male_categorical_keyboard():
    buttons = list('abcdef')
    keyboard = make_category_keyboard(buttons)
    
    assert isinstance(keyboard, types.InlineKeyboardMarkup)