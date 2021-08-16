import asyncio

from loader import bot
from models import Chat, MessageQueue
from proj.celery import app
from utils import send_to_admin, push_message


async def push_message_without_db(chat: int, message):
        try:
                return await bot.send_message(chat, message)
        except:
                return


@app.task
def push_message_at_day(chat: int, message: str):
    coro = push_message_without_db(chat, message)
    asyncio.run(coro)
