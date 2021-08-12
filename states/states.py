from aiogram.dispatcher.filters.state import StatesGroup, State


class ChatsSettings(StatesGroup):
    add_chat = State()
    delete_chat = State()


class AddMessageQueue(StatesGroup):
    get_chat = State()
    get_message = State()


class FrequencyPostingSettings(StatesGroup):
    get_chat = State()
    get_type_frequency = State()
    get_frequency = State()
