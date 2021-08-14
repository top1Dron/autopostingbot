import logging

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery
from aiogram.utils.exceptions import MessageToDeleteNotFound

from filters import BotGroupsFilter
from keyboards import user_menu, chat_callback, frequency_type_menu, type_posting_callback
from loader import dp, bot
from models import MessageQueue, Chat, Group
from schedule import set_frequency_posting
from states.states import AddMessageQueue, FrequencyPostingSettings
from utils import generate_inline_keyboard, get_frequency, get_group, create_group, delete_group


@dp.message_handler(commands=['start'])
async def process_command_user(message: types.Message):
    chat_id = message.chat.id
    group: Group = await get_group(chat_id=chat_id)
    if group is None:
        await create_group(chat_id)
    await message.answer("Запуск", reply_markup=user_menu)


@dp.message_handler(BotGroupsFilter(), commands=['stop'])
async def stop_command(message: types.Message):
    try:
        chat_administrators = [admin.user.id for admin in await message.chat.get_administrators() if not admin.user.is_bot]
    except:
        is_private = True
    if is_private or message.from_user.id in chat_administrators:
        try:
            await delete_group(chat_id=message.chat.id)
            await message.answer("Остановка", reply_markup=types.ReplyKeyboardRemove())
        except:
            pass


@dp.callback_query_handler(text_contains="back_", 
    state=[AddMessageQueue.get_chat, FrequencyPostingSettings.get_chat, 
        FrequencyPostingSettings.get_type_frequency, FrequencyPostingSettings.get_frequency])
async def process_go_back(callback_query: types.CallbackQuery, state: FSMContext):
    '''
    callback for "Отмена" inline button in add message or frequency settings
    '''
    await state.finish()
    try:
        await bot.delete_message(chat_id=callback_query.message.chat.id, 
            message_id=callback_query.message.message_id)
    except MessageToDeleteNotFound:
        pass
    await bot.send_message(chat_id=callback_query.message.chat.id, 
        text=f'Отмена', 
        reply_markup=user_menu)


@dp.message_handler(BotGroupsFilter(), text=['Добавить сообщение в очередь'])
async def add_message_to_queue(message: types.Message):
    menu = await generate_inline_keyboard()
    if menu is None:
        return await message.answer("Чатов не найдено")
    else:
        menu.insert(types.InlineKeyboardButton(text='Отмена', callback_data='back_message'))
    await message.answer("Выберите чат для добавление сообщения", reply_markup=menu)
    await AddMessageQueue.get_chat.set()


@dp.callback_query_handler(chat_callback.filter(), state=AddMessageQueue.get_chat)
async def get_chosen_chat(call: CallbackQuery, callback_data: dict, state: FSMContext):
    await state.update_data(chat_id=int(callback_data.get('chat_id')))
    await call.message.answer("Введите сообщение, которое хотите добавить в очередь")
    await AddMessageQueue.get_message.set()


@dp.message_handler(state=AddMessageQueue.get_message)
async def get_message_for_queue(message: types.Message, state: FSMContext):
    data = await state.get_data()
    await MessageQueue.create(chat=await Chat.get(id=data.get("chat_id")),
                              text=message.text)
    await message.answer("Сообщение добавлено в очередь")
    await state.finish()


@dp.message_handler(BotGroupsFilter(), text=['Настроить частоту постинга'])
async def process_frequency_of_posting(message: types.Message):
    menu = await generate_inline_keyboard()
    if menu is None:
        return await message.answer("Чатов не найдено")
    else:
        menu.insert(types.InlineKeyboardButton(text='Отмена', callback_data='back_frequency'))
        await message.answer("Выберите чат в котором нужно настроить частоту "
                         "постинга", reply_markup=menu)
    await FrequencyPostingSettings.get_chat.set()


@dp.callback_query_handler(chat_callback.filter(), state=FrequencyPostingSettings.get_chat)
async def get_chosen_chat_for_posting_settings(call: CallbackQuery, callback_data: dict, state: FSMContext):
    await state.update_data(chat_id=int(callback_data.get('chat_id')))
    await call.message.answer("Выберите тип частоты постинга", reply_markup=frequency_type_menu)
    await FrequencyPostingSettings.get_type_frequency.set()


@dp.callback_query_handler(type_posting_callback.filter(), state=FrequencyPostingSettings.get_type_frequency)
async def get_chosen_type_frequency_posting(call: CallbackQuery, callback_data: dict, state: FSMContext):
    type_frequency = callback_data.get('type_name')
    await state.update_data(type_frequency=type_frequency)
    await get_frequency(call, type_frequency)
    await FrequencyPostingSettings.get_frequency.set()


@dp.message_handler(state=FrequencyPostingSettings.get_frequency)
async def get_frequency_from_user(message: types.Message, state: FSMContext):
    data = await state.get_data()
    answer = await set_frequency_posting(data.get('chat_id'), data.get('type_frequency'), message.text)
    await message.answer(answer)
    await state.finish()
