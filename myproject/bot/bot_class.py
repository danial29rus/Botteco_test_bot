from aiogram.dispatcher.filters.state import State, StatesGroup


class QueryForm(StatesGroup):
    address = State()


class FAQForm(StatesGroup):
    question = State()
