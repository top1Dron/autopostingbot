from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery, ReplyKeyboardRemove
from aiogram.utils.exceptions import ChatNotFound

from keyboards import admin_menu, chat_settings_menu, chat_settings_menu_level2, chat_callback
from loader import dp, bot
from states.states import ChatsSettings
from utils import add_chat, get_all_chats_links, generate_inline_keyboard, delete_chat, get_chats_statistics


@dp.message_handler(commands=['admin'])
async def process_command_admin(message: types.Message):
    await message.answer("admin", reply_markup=admin_menu)


@dp.message_handler(text=['управление чатами'])
async def show_inline_chats_settings_menu(message: types.Message):
    await message.answer("Управление чатами", reply_markup=chat_settings_menu)
    print(message)


@dp.callback_query_handler(text_contains="show_chats")
async def show_chats(call: CallbackQuery):
    chats = await get_all_chats_links()
    await call.message.edit_text(chats, reply_markup=chat_settings_menu_level2)


@dp.callback_query_handler(text_contains="back")
async def back_to_main_menu(call: CallbackQuery):
    await call.message.edit_text("Управление чатами", reply_markup=chat_settings_menu)


@dp.callback_query_handler(text_contains="add_chat")
async def enter_chat_for_add(call: CallbackQuery):
    await call.message.answer("Введите идентификатор группы или название канала начина с @")
    await ChatsSettings.add_chat.set()


@dp.callback_query_handler(text_contains="delete_chat")
async def choose_chat_for_delete(call: CallbackQuery):
    menu = await generate_inline_keyboard()
    if menu is not None:
        await call.message.edit_text("Выберите чат, который вы хотите удалить", reply_markup=menu)
        await ChatsSettings.delete_chat.set()
    else:
        await call.message.answer("Чатов не найдено")


@dp.message_handler(state=ChatsSettings.add_chat)
async def add_chat_to_db(message: types.Message, state: FSMContext):
    try:
        chat = types.chat.Chat(id=message.text)
        chat = await bot.get_chat(chat.id)
    except ChatNotFound:
        await message.answer("Чат не найден", reply_markup=chat_settings_menu)
        await state.finish()
        return
    answer_add_chat = await add_chat(chat)
    await message.answer(answer_add_chat, reply_markup=chat_settings_menu)
    await state.finish()


@dp.callback_query_handler(chat_callback.filter(), state=ChatsSettings.delete_chat)
async def delete_chat_from_db(call: CallbackQuery, callback_data: dict, state: FSMContext):
    chat = int(callback_data.get('chat_id'))
    print(chat)
    await call.message.answer(await delete_chat(chat), reply_markup=chat_settings_menu)
    await state.finish()


@dp.message_handler(text=['Статистика каналов/чатов'])
async def show_statistics(message: types.Message):
    message_text = await get_chats_statistics()
    await message.answer(message_text)


@dp.message_handler(text=['закрыть меню'])
async def close_menu(message: types.Message):
    await message.answer("закрыть меню", reply_markup=ReplyKeyboardRemove())


@dp.message_handler()
async def process_message(message: types.Message):
    print(message)
