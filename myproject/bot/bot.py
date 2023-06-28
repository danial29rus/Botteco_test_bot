from myproject.main import bot, dp, cart
from myproject.bot.states import QueryForm
from myproject.bot.utils import get_product_name, calculate_subtotal, calculate_total, faq_data
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from asgiref.sync import sync_to_async


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


@dp.message_handler(lambda message: message.text == "Каталог")
async def catalog(message: types.Message, state: FSMContext):
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


@dp.message_handler(lambda message: message.text == "Корзина")
async def show_cart(message: types.Message, state: FSMContext):
    if cart:
        total = 0
        cart_items = []
        for product_id, quantity in cart.items():
            product_name = get_product_name(product_id)
            subtotal = calculate_subtotal(product_id, quantity)
            total += subtotal
            cart_items.append(f"{product_name} - {quantity} шт. - {subtotal} руб.")

        cart_items.append(f"Итого: {total} руб.")

        cart_text = "\n".join(cart_items)
        keyboard = InlineKeyboardMarkup(row_width=1)
        for product_id in cart.keys():
            keyboard.add(InlineKeyboardButton(f"Удалить {get_product_name(product_id)}",
                                              callback_data=f"delete_{product_id}"))

        keyboard.add(InlineKeyboardButton("Ввод данных для доставки", callback_data="delivery_info"))

        await message.answer(f"Товары в корзине:\n{cart_text}\n\nЧто вы хотите сделать?", reply_markup=keyboard)
    else:
        await message.answer("Корзина пуста.")

        total = calculate_total()

        await message.answer(f"Спасибо! Ваши данные для доставки сохранены.\n"
                             f"Сумма к оплате: {total} руб.\n"
                             f"Оплатить: ссылка на оплату должна быть")
        await state.finish()


@dp.callback_query_handler(lambda query: query.data.startswith('delete_'))
async def handle_delete_from_cart(query: types.CallbackQuery):
    product_id = query.data.split('_')[1]

    if product_id in cart:
        del cart[product_id]
        await query.message.answer("Товар успешно удален из корзины.")
    else:
        await query.message.answer("Товар не найден в корзине.")


@dp.callback_query_handler(lambda query: query.data.startswith('delivery_info'))
async def process_address(query: types.CallbackQuery):
    await query.message.answer("Введите адрес доставки:")
    await QueryForm.address.set()


@sync_to_async
def save_customer(customer):
    customer.save()


@dp.message_handler(state=QueryForm.address)
async def process_address_input(message: types.Message, state: FSMContext):
    address = message.text
    nickname = message.from_user.username
    parts = address.split(',')

    if len(parts) == 4:
        city = parts[0].strip()
        street = parts[1].strip()
        house = parts[2].strip()
        apartment = parts[3].strip()

        await state.update_data(city=city, street=street, house=house, apartment=apartment)

        total = calculate_total()

        customer = Customer(name=nickname, address=address)
        order = Order(customer=customer, amount=total)

        await sync_to_async(customer.save)()
        await sync_to_async(order.save)()

        await message.answer(f"Спасибо! Ваши данные для доставки сохранены.\n"
                             f"Сумма к оплате: {total} руб.\n"
                             f"Оплатить: ссылка на оплату должна быть")
        await state.finish()
    else:
        await message.answer(
            "Некорректный формат адреса. Пожалуйста, введите адрес в формате 'Город, Улица, Дом, Квартира:'")


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
