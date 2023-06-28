import logging
import os

import django
from aiogram import Bot, Dispatcher
from aiogram import executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from config import TOKEN

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')

django.setup()

from adminpanelforbot.models import Order, Customer

logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
cart = {}



if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
