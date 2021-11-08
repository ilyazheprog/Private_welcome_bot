from aiogram.dispatcher.filters import ChatTypeFilter

from .keyboards import *
from src.dispatcher import *
from src.BD import *


@dp.callback_query_handler(ChatTypeFilter(chat_type=types.ChatType.PRIVATE), callback_del_chats.filter())
async def remove_chat(call, callback_data: dict):
    """
    Удаление чата
    :param call: Тип объекта CallbackQuery, который прилетает в хендлер
    :param callback_data: Словарь с данными, которые хранятся в нажатой кнопке
    """
    id_chat = callback_data.get("chat")
    if id_chat == " ":
        await call.message.edit_text(text='Меню', reply_markup=await gen_markup())
    else:
        try_create()
        cursor.execute(f"DELETE FROM chats WHERE chat_id='{id_chat}'")
        db.commit()
        s = []
        for row in cursor.execute(f"SELECT * FROM chats"):
            s += [[row[0], row[1]]]
        await call.message.edit_text(text="Удалить чаты", reply_markup=await remove(s))
        await bot.leave_chat(id_chat)


async def delete_chat(call):
    """
    Кнопки с чатами, доступными для удаления
    :param call: Тип объекта CallbackQuery, который прилетает в хендлер
    """
    try_create()
    s = []
    for row in cursor.execute(f"SELECT * FROM chats"):
        s += [[row[0], row[1]]]
    await call.message.edit_text(text="Удалить чаты", reply_markup=await remove(s))


async def show_all_chat(call):
    """
    Навигация в меню
    :param call: Тип объекта CallbackQuery, который прилетает в хендлер
    """
    try_create()
    s = 'Список чатов\n\n'
    for row in cursor.execute(f"SELECT * FROM chats"):
        s += f'Чат: {row[1]}\nБот добавлен: {str(row[2])[:str(row[2]).rfind(":") + 3]}\n'
    await call.message.edit_text(text=s, reply_markup=await back())


@dp.callback_query_handler(ChatTypeFilter(chat_type=types.ChatType.PRIVATE), callback_back.filter())
async def _back(call):
    """
    Кнопка назад
    :param call: Тип объекта CallbackQuery, который прилетает в хендлер
    """
    await call.message.edit_text(text='Меню', reply_markup=await gen_markup())


@dp.message_handler(ChatTypeFilter(chat_type=types.ChatType.PRIVATE), commands=['menu'])
async def menu(message):
    env_vars = Env()
    env_vars.read_env()
    admins = env_vars.list("ADMIN_LIST")
    if str(message.from_user.id) in admins:
        await bot.send_message(message.from_user.id, 'Меню', reply_markup=await gen_markup())
    else:
        await bot.send_message(message.from_user.id,
                               f"Приветствую, {message.from_user.first_name} {message.from_user.last_name}. "
                               f"Вам запрещено добавлять меня в чат!")


@dp.message_handler(ChatTypeFilter(chat_type=types.ChatType.PRIVATE), commands=['startbot'])
async def start(message):
    env_var = Env()
    env_var.read_env()
    admins = env_var.list("ADMIN_LIST")
    if str(message.from_user.id) in admins:
        await bot.send_message(message.from_user.id,
                               f"Приветствую, {message.from_user.first_name} {message.from_user.last_name}\n"
                               f"Используй /menu для управления ботом")
    else:
        await bot.send_message(message.from_user.id,
                               f"Приветствую, {message.from_user.first_name} {message.from_user.last_name}."
                               f"Вам запрещено добавлять меня в чат!")


@dp.callback_query_handler(ChatTypeFilter(chat_type=types.ChatType.PRIVATE), callbacks.filter())
async def navigate(call, callback_data: dict):
    """
    Навигация в меню
    :param call: Тип объекта CallbackQuery, который прилетает в хендлер
    :param callback_data: Словарь с данными, которые хранятся в нажатой кнопке
    """
    # Выбраная кнопка
    chosen = callback_data.get("chosen")

    # Прописываем "уровни" в которых будут отправляться новые кнопки пользователю
    levels = {
        "menu":menu,
        "delete_chat":delete_chat,
        "show_all_chats":show_all_chat
    }

    # Забираем нужную функцию для выбранного уровня
    current_level_function = levels[chosen]

    # Выполняем нужную функцию и передаем туда параметры, полученные из кнопки
    await current_level_function(call)
