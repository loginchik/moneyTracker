from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton


def make_category_keyboard(categories_list):
    inline_keyboard_builder = InlineKeyboardBuilder()

    for category in categories_list:
        this_button = InlineKeyboardButton(text=category, callback_data=category)
        inline_keyboard_builder.add(this_button)

    new_cat_button = InlineKeyboardButton(text='+ Создать', callback_data='new_category')
    inline_keyboard_builder.add(new_cat_button)
    inline_keyboard_builder.adjust(2)

    categories_keyboard = inline_keyboard_builder.as_markup()
    return categories_keyboard