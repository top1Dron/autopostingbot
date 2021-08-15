import logging
from typing import Iterable, Union
from aiogram import types
from aiogram.dispatcher.filters import BoundFilter
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from tortoise.exceptions import DoesNotExist

import models
from keyboards import chat_callback, create_back_menu
from loader import bot
from models import Chat, Group, MessageQueue
from settings import admin_id


async def set_default_commands(dp):
    await dp.bot.set_my_commands([
        types.BotCommand("start", "Запустить бота"),
        types.BotCommand("stop", "Остановить бота"),
        types.BotCommand("admin", "Админ-панель")
    ])


async def add_chat(chat: types.Chat):
    has_chat = await Chat.get_or_none(id=chat.id)
    chats = await get_all_chats_links() 
    if has_chat is None:
        invite_link = chat.invite_link
        title = chat.title
        type_of_chat = chat.type
        await Chat.create(id=chat.id,
                          invite_link=invite_link,
                          type=type_of_chat,
                          title=title)
        chats = await get_all_chats_links()                  
        return f'Чат успешно добавлен. Все доступные чаты на текущий момент: {chats}'
    else:
        return f'Чат уже есть в списке. Все доступные чаты на текущий момент: {chats}'


async def delete_chat(chat: int):
    chats = await get_all_chats_links() 
    try:
        await MessageQueue.filter(id=chat).delete()
        await Chat.filter(id=chat).delete()
        chats = await get_all_chats_links()
        return f"Чат удален! Все доступные чаты на текущий момент: {chats}"
    except:
        return f"Чат не найден! Все доступные чаты на текущий момент: {chats}"


async def get_all_chats_links():
    chats = await Chat.all()
    links = []
    print(chats)
    if len(chats) != 0:
        for chat in chats:
            links.append([chat.title, chat.invite_link])
        return '\n\n'.join(' - '.join(map(str, row)) for row in links)
    return 'Чатов не найдено'


async def generate_inline_keyboard():
    chats = await Chat.all()
    if len(chats) == 0:
        return None
    generated_menu = InlineKeyboardMarkup(row_width=2)
    for chat in chats:
        generated_menu.insert(InlineKeyboardButton(text=chat.title, callback_data=chat_callback.new(chat_id=chat.id)))
    return generated_menu


async def get_first_message(chat: int):
    chat = await Chat.get_or_none(id=chat)
    if chat is not None:
        message = await MessageQueue.filter(chat_id=chat.id).first()
        if message is None:
            return None
        return message.text


async def push_message(chat: int):
    chat = await Chat.get_or_none(id=chat)
    if chat is not None:
        message = await MessageQueue.filter(chat_id=chat.id).first()
        if message is None:
            return
        await bot.send_message(chat.id, message.text)
        await MessageQueue.filter(id=message.id).delete()


async def send_to_admin(message: str):
    for admin in admin_id:
        return await bot.send_message(admin, message)


async def get_frequency(call: CallbackQuery, type_frequency: str):
    type_frequency_list = {
        'by_period': 'Введите период частоты постинга в формате "число:тип времени. "'
                     'тип времени [секунда, минута, час]',
        'by_day': 'Введите номер дня в который делать постинг',
        'by_date': 'Введите день месяца',
    }
    await call.message.answer(type_frequency_list[type_frequency], reply_markup=create_back_menu('back_get_frequency'))


async def get_chats_statistics():
    chats = await Chat.all()
    if await Chat.all().count() == 0:
        return "Чаты отсутствуют"
    answer = 'Название чата - количество сообщений в ожидании - частота постинга\n'
    for chat in chats:
        posting = ''
        try:
            frequency_object = await models.FrequencyPosting.get(chat_id=chat.id)
            posting_type = frequency_object.type

            if posting_type == 'by_period':
                posting = f'Каждые {frequency_object.count_time} {frequency_object.type_time}'
            elif posting_type == 'by_day':
                days = {
                    1: 'понедельник', 2: 'вторник',
                    3: 'среда', 4: 'четверг', 5: 'пятница',
                    6: 'суббота', 7: 'воскресенье',
                }
                posting = f'Каждый {days[int(frequency_object.day_of_week)]}'
            elif posting_type == 'by_date':
                posting = f'Каждый {frequency_object.day_of_month}-ый день месяца'
        except DoesNotExist:
            posting = 'Постинг не настроен'
        answer += f'{chat.title} - {await chat.messages.all().count()} - {posting}\n'
    return answer

async def get_group(chat_id: Union[int, str]) -> Group:
    return await Group.filter(chat_id=str(chat_id)).first()


async def create_group(chat_id: Union[int, str]) -> Group:
    new_group = await Group.create(chat_id=str(chat_id))
    return new_group


async def get_bot_groups() -> Iterable[int]:
    return [int(group.chat_id) for group in await Group.all()]


async def delete_group(chat_id: Union[int, str]) -> None:
    group = await get_group(chat_id=chat_id)
    await group.delete()
