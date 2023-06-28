from myproject.main import cart
def get_product_name(product_id):
    if product_id == '1':
        return "Штаны 1"
    elif product_id == '2':
        return "Штаны 2"
    elif product_id == '3':
        return "Штаны 3"
    elif product_id == '4':
        return "Футболка 1"
    elif product_id == '5':
        return "Футболка 2"
    elif product_id == '6':
        return "Футболка 3"
    elif product_id == '7':
        return "Шорты 1"
    elif product_id == '8':
        return "Шорты 2"
    elif product_id == '9':
        return "Шорты 3"


def calculate_subtotal(product_id, quantity):
    return 100 * quantity


def calculate_total():
    total = 0
    for product_id, quantity in cart.items():
        subtotal = calculate_subtotal(product_id, quantity)
        total += subtotal
    return total


faq_data = {
    "Сроки доставки": "1-3 недели",
    "Возврат": "Вещи вернуть нельзя",
}

