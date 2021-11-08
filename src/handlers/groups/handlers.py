import asyncio
from datetime import datetime

from aiogram.utils.exceptions import MessageToDeleteNotFound
from loguru import logger

from .keyboards import *
from src.permissions import *
from src.dispatcher import *
from src.BD import *

logger.add("INFO.log", format="{time} {level} {message}", level="INFO", rotation="1000 KB", compression="zip")

DELAY_DELETE_MESSAGE = 25
members = {}
flags = {'flag':True}


@dp.message_handler(content_types=['left_chat_member'])
async def left(message):
    user = message.left_chat_member
    if int(user.id) == int(bot.id):
        id = message.chat.id
        try_create()
        cursor.execute(f"DELETE FROM chats WHERE chat_id='{id}'")
        db.commit()


@dp.message_handler(content_types=['new_chat_members'])
async def new_member(message):
    env_var = Env()
    env_var.read_env()
    admins = env_var.list("ADMIN_LIST")
    chat = message.chat
    # получаем объект юзера
    user = message.new_chat_members[len(message.new_chat_members) - 1]
    if int(user.id) == int(bot.id) and str(message.from_user.id) in admins:
        try_create()
        cursor.execute(f"SELECT chat_name FROM chats WHERE chat_id = '{chat.id}'")
        if cursor.fetchone() is None:
            cursor.execute(f"INSERT INTO chats (chat_id, chat_name, date) VALUES (?, ?, ?)",
                           (chat.id, chat.title, datetime.now()))
            db.commit()

    elif int(user.id) == int(bot.id) and str(message.from_user.id) not in admins:
        await bot.leave_chat(chat.id)
    else:
        # для управления состоянием кнопок
        flags.update(flag=False)
        # для управления удаления сообщений
        user_join_message_id = message.message_id

        new_members_permissions = set_new_user_permissions()
        await bot.restrict_chat_member(
            chat_id=message.chat.id,
            user_id=user.id,
            permissions=new_members_permissions,
        )

        await message.reply(
            (
                f"{user.get_mention(as_html=True)}, <b>добро пожаловать в чат!\n"
                "Подтверди, что ты не бот, нажатием на одну из кнопок ниже\n"
                "ВРЕМЯ ДЛЯ ОТВЕТА 20 СЕКУНД!</b>\n"

            ),
            reply_markup=generate_confirm_markup(user.id, user_join_message_id)
        )
        logger.info(f"User: {user.username}, has join in chat")
        await asyncio.sleep(20)

        if not flags.get('flag'):
            try:
                # удаление сообщений
                await bot.delete_message(message.chat.id, user_join_message_id)
                await bot.delete_message(message.chat.id, user_join_message_id + 1)
            except MessageToDeleteNotFound:
                print("I get error: MessageToDeleteNotFound")
            # кик пользователя
            await bot.kick_chat_member(message.chat.id, user.id)


@dp.callback_query_handler(user_callback.filter())
async def callback_inline(query: types.CallbackQuery, callback_data: dict):
    begin = callback_data.get("begin")
    # айди пользователя (приходит строкой, поэтому используем int)
    user_id = int(callback_data.get("user_id"))
    # и айди чата, для последнующей выдачи прав
    chat_id = int(query.message.chat.id)

    # блок для только что вошедшого пользователя
    if query.from_user.id != user_id:
        await bot.answer_callback_query(
            query.id,
            text='Сообщение для другого пользователя! (This message for another user!)',
            show_alert=True
        )
        return

    # далее, если пользователь выбрал кнопку "человек" сообщаем ему об этом
    if begin == "human":
        flags.update(flag=True)
        logger.info(f"User: {query.from_user.id}, select human")
        text = str("Вам открыт доступ в чат! You have access in our chat!")
        # всплывающее окно
        await bot.answer_callback_query(query.id, text=text, show_alert=True)
        try:
            await bot.delete_message(chat_id, query.message.message_id)
            await bot.delete_message(chat_id, query.message.message_id + 1)
        except MessageToDeleteNotFound:
            print("I get error: MessageToDeleteNotFound")
    # а если всё-таки бот, тоже отписываем и пропускаем, ибо только юзерботы могут жать на кнопки
    elif begin == "bot":
        flags.update(flag=True)
        logger.info(f"User: {query.from_user.id}, select bot")
        text = str("Вы бот вам закрыт доступ в чат! You are bot and access is closed in our chat!")

        # показываем вспывающее окно
        await bot.answer_callback_query(query.id, text=text, show_alert=True)
        # таймер для прочтения всплывашки
        await asyncio.sleep(2)
        # кик пользователя
        await bot.kick_chat_member(chat_id, user_id)

        try:
            await bot.delete_message(chat_id, query.message.message_id)
            await bot.delete_message(chat_id, query.message.message_id + 1)
        except MessageToDeleteNotFound:
            print("I get error: MessageToDeleteNotFound")

    # не забываем выдать юзеру необходимые права
    await bot.restrict_chat_member(
        chat_id=chat_id,
        user_id=user_id,
        permissions=set_new_user_approved_permissions(),
    )
