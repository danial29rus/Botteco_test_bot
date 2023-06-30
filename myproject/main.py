import logging
import os

import django
from aiogram import Bot, Dispatcher
from aiogram import executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from bot.handlers.cart import register_handlers_cart
from bot.handlers.catalog import register_handlers_catalog
from bot.handlers.faq import register_handlers_faq
from bot.handlers.start import register_handlers_start
from config import TOKEN

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')

django.setup()

from adminpanelforbot.models import Order, Customer

logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

register_handlers_start(dp)
register_handlers_catalog(dp)
register_handlers_cart(dp)
register_handlers_faq(dp)

if __name__ == '__main__':
    from aiogram import executor

    executor.start_polling(dp, skip_updates=True)

