from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery

from keyboards import user_menu, chat_callback, frequency_type_menu, type_posting_callback
from loader import dp
from models import MessageQueue, Chat
from schedule import set_frequency_posting
from states.states import AddMessageQueue, FrequencyPostingSettings
from utils import generate_inline_keyboard, get_frequency


@dp.message_handler(commands=['start'])
async def process_command_user(message: types.Message):
    print('user')
    await message.answer("start", reply_markup=user_menu)


@dp.message_handler(text=['Добавить сообщение в очередь'])
async def add_message_to_queue(message: types.Message):
    menu = await generate_inline_keyboard()
    if menu is None:
        return await message.answer("Чатов не найдено")
    await message.answer("Выберите чат для добавление сообщения", reply_markup=menu)
    await AddMessageQueue.get_chat.set()


@dp.callback_query_handler(chat_callback.filter(), state=AddMessageQueue.get_chat)
async def get_chosen_chat(call: CallbackQuery, callback_data: dict, state: FSMContext):
    print(callback_data)
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


@dp.message_handler(text=['Настроить частоту постинга'])
async def process_frequency_of_posting(message: types.Message):
    menu = await generate_inline_keyboard()
    if menu is None:
        return await message.answer("Чатов не найдено")
    await message.answer("Выберите чат в котором нужно настроить частоту"
                         "постинга", reply_markup=menu)
    await FrequencyPostingSettings.get_chat.set()


@dp.callback_query_handler(chat_callback.filter(), state=FrequencyPostingSettings.get_chat)
async def get_chosen_chat_for_posting_settings(call: CallbackQuery, callback_data: dict, state: FSMContext):
    print(callback_data)
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
