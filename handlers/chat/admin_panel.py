import logging

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery, ReplyKeyboardRemove
from aiogram.utils.exceptions import ChatNotFound, MessageToDeleteNotFound

from filters import BotGroupsFilter
from keyboards import admin_menu, chat_settings_menu, create_back_menu
from loader import dp, bot
from states.states import ChatsSettings
from utils import add_chat, get_all_chats_links, generate_inline_keyboard, delete_chat, get_chats_statistics


@dp.message_handler(BotGroupsFilter(), commands=['admin'])
async def process_command_admin(message: types.Message):
    await message.answer("Панель администратора", reply_markup=admin_menu)


@dp.message_handler(BotGroupsFilter(), text=['Управление чатами'])
async def show_inline_chats_settings_menu(message: types.Message):
    chats = await get_all_chats_links()
    await message.answer(f"Управление чатами. Все доступные чаты на текущий момент: {chats}", reply_markup=chat_settings_menu)


# @dp.callback_query_handler(text_contains="back")
# async def back_to_main_menu(call: CallbackQuery):
#     chats = await get_all_chats_links()
#     await call.message.edit_text(f"Управление чатами. Все доступные чаты на текущий момент: {chats}", reply_markup=chat_settings_menu)


@dp.callback_query_handler(text_contains="back_chat", state=[ChatsSettings.add_chat, ChatsSettings.delete_chat])
async def process_go_back(callback_query: types.CallbackQuery, state: FSMContext):
    '''
    callback for "Отмена" inline button in add/delete chat
    '''
    chats = await get_all_chats_links()
    await state.finish()
    try:
        await bot.delete_message(chat_id=callback_query.message.chat.id, 
            message_id=callback_query.message.message_id)
    except MessageToDeleteNotFound:
        pass
    await bot.send_message(chat_id=callback_query.message.chat.id, 
        text=f'Управление чатами.\nВсе доступные чаты на текущий момент:\n{chats}', 
        reply_markup=chat_settings_menu)


@dp.callback_query_handler(text_contains="add_chat", state='*')
async def enter_chat_for_add(call: CallbackQuery):
    await call.message.edit_text("Введите название ссылки на канал или группу, начиная с @", reply_markup=create_back_menu('back_chat'))
    await ChatsSettings.add_chat.set()


@dp.callback_query_handler(text_contains="delete_chat")
async def choose_chat_for_delete(call: CallbackQuery):
    menu = await generate_inline_keyboard()
    if menu is not None:
        menu.insert(types.InlineKeyboardButton(text='Отмена', callback_data='back_chat'))
        await ChatsSettings.delete_chat.set()
        await call.message.edit_text("Выберите чат, который вы хотите удалить", reply_markup=menu)
    else:
        await call.message.edit_text("Чатов не найдено.", reply_markup=chat_settings_menu)


@dp.message_handler(state=ChatsSettings.add_chat)
async def add_chat_to_db(message: types.Message, state: FSMContext):
    try:
        chat = types.chat.Chat(id=message.text)
        chat = await bot.get_chat(chat.id)
    except ChatNotFound:
        if not message.text.startswith('@'):
            await message.answer('Неправильный ввод', reply_markup=chat_settings_menu)
        else:
            await message.answer("Чат не найден", reply_markup=chat_settings_menu)
        await state.finish()
        return
    answer_add_chat = await add_chat(chat)
    await message.answer(answer_add_chat, reply_markup=chat_settings_menu)
    await state.finish()


@dp.callback_query_handler(state=ChatsSettings.delete_chat)
async def delete_chat_from_db(call: CallbackQuery, state: FSMContext):
    chat = int(call.data.replace('chosen_chat:', ''))
    await call.message.edit_text(await delete_chat(chat), reply_markup=chat_settings_menu)
    await state.finish()


@dp.message_handler(BotGroupsFilter(), text=['Статистика каналов/чатов'])
async def show_statistics(message: types.Message):
    message_text = await get_chats_statistics()
    await message.answer(message_text)


@dp.message_handler(BotGroupsFilter(), text=['Закрыть меню'])
async def close_menu(message: types.Message):
    await message.answer("Закрыть меню", reply_markup=ReplyKeyboardRemove())