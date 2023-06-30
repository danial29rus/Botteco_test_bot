from aiogram import types
from aiogram.dispatcher import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command

from ...main import bot


def register_handlers_start(dp: Dispatcher):
    @dp.message_handler(Command('start'))
    async def start(message: types.Message, state: FSMContext):
        chat_id = message.chat.id
        subscribed = await bot.get_chat_member(chat_id=str(chat_id), user_id=message.from_user.id)
        if subscribed.status != types.ChatMemberStatus.LEFT:
            keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
            keyboard.add(types.KeyboardButton(text="Каталог"))
            keyboard.add(types.KeyboardButton(text="Корзина"))
            keyboard.add(types.KeyboardButton(text="FAQ"))

            await message.answer("Привет! Я бот. Чем могу помочь?", reply_markup=keyboard)
        else:
            await message.answer("Привет! Пожалуйста, подпишитесь на наш канал, чтобы использовать бот.")