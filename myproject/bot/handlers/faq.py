from aiogram import types
from aiogram.dispatcher import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from myproject.bot.utils import faq_data


def register_handlers_faq(dp: Dispatcher):
    @dp.message_handler(lambda message: message.text == "FAQ")
    async def start_faq(message: types.Message):
        keyboard = InlineKeyboardMarkup(row_width=1)
        for question in faq_data.keys():
            keyboard.add(InlineKeyboardButton(question, callback_data=f"faq_{question}"))

        await message.answer("Выберите вопрос:", reply_markup=keyboard)

    @dp.callback_query_handler(lambda query: query.data.startswith('faq_'))
    async def handle_faq_click(query: types.CallbackQuery, state: FSMContext):
        question = query.data.split('_')[1]

        answer = faq_data.get(question)
        if answer:
            await query.message.answer(f"<b>Вопрос:</b> {question}\n\n<b>Ответ:</b> {answer}", parse_mode='HTML')
        else:
            await query.message.answer("Ответ на данный вопрос не найден.")