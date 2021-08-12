from datetime import datetime

import aioschedule as schedule

from models import MessageQueue, FrequencyPosting
from utils import push_message, get_first_message
from proj.tasks import push_message_at_day


async def do_every_seconds(second: int, chat_id):
    schedule.every(second).seconds.do(push_message,
                                      chat=chat_id).tag(str(chat_id))
    await FrequencyPosting.filter(chat_id=chat_id).delete()
    await FrequencyPosting.create(chat_id=chat_id, count_time=second, type_time='секунд', type='by_period')


async def do_every_minutes(minute, chat_id):
    schedule.every(minute).minutes.do(push_message,
                                      chat=chat_id).tag(str(chat_id))
    await FrequencyPosting.filter(chat_id=chat_id).delete()
    await FrequencyPosting.create(chat_id=chat_id, count_time=minute, type_time='минут', type='by_period')


async def do_every_hours(hour, chat_id):
    schedule.every(hour).hours.do(push_message,
                                  chat=chat_id).tag(str(chat_id))
    await FrequencyPosting.filter(chat_id=chat_id).delete()
    await FrequencyPosting.create(chat_id=chat_id, count_time=hour, type_time='часов', type='by_period')


async def set_frequency_posting(chat_id: int, type_frequency: str, frequency: str):
    schedule.clear(str(chat_id))
    if type_frequency == 'by_period':
        frequency_list = frequency.split(":")
        frequency_dict = {
            'секунда': do_every_seconds,
            'минута': do_every_minutes,
            'час': do_every_hours
        }
        try:
            await frequency_dict[frequency_list[1]](int(frequency_list[0]), chat_id)
        except KeyError:
            return 'Неправильный формат число:тип (без пробелов)'
    if type_frequency == 'by_day':
        if 7 < int(frequency) < 1:
            return "Введенное число должно быть в диапазоне от 1 до 7"
        frequency_dict = {
            '1': schedule.every().monday.do(push_message,
                                            chat=chat_id).tag(str(chat_id)),
            '2': schedule.every().tuesday.do(push_message,
                                             chat=chat_id).tag(str(chat_id)),
            '3': schedule.every().wednesday.do(push_message,
                                               chat=chat_id).tag(str(chat_id)),
            '4': schedule.every().thursday.do(push_message,
                                              chat=chat_id).tag(str(chat_id)),
            '5': schedule.every().friday.do(push_message,
                                            chat=chat_id).tag(str(chat_id)),
            '6': schedule.every().saturday.do(push_message,
                                              chat=chat_id).tag(str(chat_id)),
            '7': schedule.every().sunday.do(push_message,
                                            chat=chat_id).tag(str(chat_id)),
        }
        frequency_dict[frequency]
        await FrequencyPosting.filter(chat_id=chat_id).delete()
        await FrequencyPosting.create(chat_id=chat_id, type='by_day', day_of_week=int(frequency))
    if type_frequency == 'by_date':
        try:
            if int(frequency) > 31 and int(frequency) < 1:
                raise ValueError
            push_message_at_day.apply_async((chat_id, await get_first_message(chat_id)),
                                            eta=datetime.today().replace(day=int(frequency)))
            message = await MessageQueue.filter(chat_id=chat_id).first()
            await MessageQueue.filter(id=message.id).delete()
            await FrequencyPosting.filter(chat_id=chat_id).delete()
            await FrequencyPosting.create(chat_id=chat_id, type='by_date', day_of_month=int(frequency))
        except ValueError:
            return "День должен быть в диапазоне от 1 до 31"
    return "Постинг настроен"
