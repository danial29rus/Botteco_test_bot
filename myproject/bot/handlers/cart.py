from aiogram import types
from aiogram.dispatcher import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from asgiref.sync import sync_to_async

from myproject.bot.handlers.catalog import cart
from myproject.bot.states import QueryForm
from myproject.bot.utils import get_product_name, calculate_total, calculate_subtotal
from myproject.main import Customer, Order


def register_handlers_cart(dp: Dispatcher):
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