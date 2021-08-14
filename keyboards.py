from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData


type_posting_callback = CallbackData("type", "type_name")


admin_menu = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text='Управление чатами'),
        ],
        [
            KeyboardButton(text='Статистика каналов/чатов'),
        ],
        [
            KeyboardButton(text='Закрыть меню'),
        ]
    ],
    resize_keyboard=True,
    selective=True,
)


user_menu = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text='Добавить сообщение в очередь'),
        ],
        [
            KeyboardButton(text='Настроить частоту постинга')
        ],
        [
            KeyboardButton(text='Закрыть меню'),
        ]
    ],
    resize_keyboard=True,
    selective=True,
)


chat_settings_menu = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text='Добавить чат/канал', callback_data="add_chat"),
            InlineKeyboardButton(text='Удалить чат/канал', callback_data="delete_chat"),
        ],
    ]
)

def create_back_menu(callback_data) -> InlineKeyboardMarkup:
    chat_settings_menu_back = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text='Отмена', callback_data=callback_data),
            ],
        ]
    )
    return chat_settings_menu_back

frequency_type_menu = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text='Постинг через указанный период',
                                 callback_data=type_posting_callback.new(type_name='by_period'))
        ],
        [
            InlineKeyboardButton(text='Постинг каждый день недели',
                                 callback_data=type_posting_callback.new(type_name='by_day'))
        ],
        [
            InlineKeyboardButton(text='Постинг каждый месяц в выбраный день',
                               callback_data=type_posting_callback.new(type_name='by_date'))
        ],
        [
            InlineKeyboardButton(text='Отмена', callback_data='back_frequency_choose'),
        ],
    ]
)


chat_callback = CallbackData("chosen_chat", "chat_id")


