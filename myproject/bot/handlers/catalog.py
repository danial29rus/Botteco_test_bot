from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command
from aiogram.dispatcher import Dispatcher
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from myproject.bot.database.connect import session
from myproject.bot.database.models import User
from myproject.bot.utils import get_product_name
def save_user(user_data):
    user = User(username=user_data.username,
                first_name=user_data.first_name,
                last_name=user_data.last_name)
    session.add(user)
    session.commit()
cart = {}

def register_handlers_catalog(dp: Dispatcher):
    @dp.message_handler(lambda message: message.text == "Каталог")
    async def catalog(message: types.Message, state: FSMContext):
        save_user(message.from_user)
        keyboard = InlineKeyboardMarkup(row_width=1)
        keyboard.add(
            InlineKeyboardButton("Штаны", callback_data="subcategory_pants"),
            InlineKeyboardButton("Футболки", callback_data="subcategory_tshirts"),
            InlineKeyboardButton("Шорты", callback_data="subcategory_shorts")
        )


        await message.answer("Выберите подкатегорию товаров:", reply_markup=keyboard)

    @dp.callback_query_handler(lambda query: query.data.startswith('subcategory_'))
    async def handle_subcategory_click(query: types.CallbackQuery):
        subcategory = query.data.split('_')[1]  # Получаем выбранную подкатегорию из callback_data

        products_keyboard = InlineKeyboardMarkup(row_width=1)
        if subcategory == 'pants':
            products_keyboard.add(
                InlineKeyboardButton("Штаны 1", callback_data="product_pants_1"),
                InlineKeyboardButton("Штаны 2", callback_data="product_pants_2"),
                InlineKeyboardButton("Штаны 3", callback_data="product_pants_3")
            )
        elif subcategory == 'tshirts':
            products_keyboard.add(
                InlineKeyboardButton("Футболка 1", callback_data="product_tshirt_1"),
                InlineKeyboardButton("Футболка 2", callback_data="product_tshirt_2"),
                InlineKeyboardButton("Футболка 3", callback_data="product_tshirt_3")
            )
        elif subcategory == 'shorts':
            products_keyboard.add(
                InlineKeyboardButton("Шорты 1", callback_data="product_shorts_1"),
                InlineKeyboardButton("Шорты 2", callback_data="product_shorts_2"),
                InlineKeyboardButton("Шорты 3", callback_data="product_shorts_3")
            )

        await query.message.answer(f"Товары в подкатегории '{subcategory}':", reply_markup=products_keyboard)

    @dp.callback_query_handler(lambda query: query.data.startswith('product_'))
    async def handle_product_click(query: types.CallbackQuery, state: FSMContext):
        product_data = query.data.split('_')
        product_id = '_'.join(product_data[2:])

        product_name = get_product_name(product_id)

        await state.update_data(selected_product={"name": product_name, "id": str(product_id)})

        await query.message.answer(f"Вы выбрали товар: {product_name}. Введите количество товара:")

    @dp.message_handler(lambda message: message.text.isdigit(), state="*")
    async def handle_quantity_input(message: types.Message, state: FSMContext):
        data = await state.get_data()
        selected_product = data.get('selected_product')
        product_id = selected_product.get('id') if selected_product else None

        if product_id:
            quantity = int(message.text)

            if quantity > 0:
                if product_id in cart:
                    cart[product_id] += quantity
                else:
                    cart[product_id] = quantity

                await message.answer("Товар успешно добавлен в корзину!")
            else:
                await message.answer("Количество товара должно быть больше 0.")
        else:
            await message.answer("Выберите товар из каталога.")