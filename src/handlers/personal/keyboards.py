from aiogram.utils.deep_linking import get_startgroup_link
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData

callback_back = CallbackData("confirm", "begin")
callbacks = CallbackData("confirm", "level", "chosen", "values")
callback_chats = CallbackData("confirm", "chat")
callback_del_chats = CallbackData("confirm", "chat")


async def remove(chats):
    keyboard = InlineKeyboardMarkup(row_width=2)
    btns = [InlineKeyboardButton(text=c[1], callback_data=callback_del_chats.new(chat=c[0])) for c in chats]
    keyboard.add(*btns)
    keyboard.add(
        InlineKeyboardButton(text="Назад", callback_data=callback_del_chats.new(chat=" "))
    )
    return keyboard


async def back():
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        InlineKeyboardButton(text="Назад", callback_data=callback_back.new(begin=" "))
    )
    return keyboard


async def gen_markup():
    button_text = ['Добавить чат', "Удалить чат", "Все чаты"]
    keyboard = InlineKeyboardMarkup(row_width=3)
    keyboard.add(
        InlineKeyboardButton(text=button_text[0], url=await get_startgroup_link('test')),
        InlineKeyboardButton(text=button_text[1], callback_data=callbacks.new(level="menu",
                                                                              chosen="delete_chat",
                                                                              values=" ")),
        InlineKeyboardButton(text=button_text[2], callback_data=callbacks.new(level="menu",
                                                                              chosen="show_all_chats",
                                                                              values=" "))

    )
    return keyboard