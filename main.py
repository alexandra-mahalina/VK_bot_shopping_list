import random
from dotenv import load_dotenv
load_dotenv()
import os
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from peewee import IntegrityError
from keyboards import create_keyboard
from models import User, Product, create_models
from states import get_state, get_data, set_state, clear_state
from states import STATE_PRODUCT_MAKE_DONE, STATE_NEW_PRODUCT_TITLE
BOT_TOKEN = os.getenv('BOT_TOKEN')

vk_session = vk_api.VkApi(token=BOT_TOKEN)
vk = vk_session.get_api()
longpoll = VkLongPoll(vk_session)

create_models()

def send(user_id: int, message: str, keyboard: None):
    """
    Метод, отправляющий сообщение пользователю
    :param user_id: int
    :param message: str
    :param keyboard: VkKeyboard or None
    :return:
    """
    vk.messages.send(user_id=user_id,
                     message=message,
                     keyboard=keyboard,
                     random_id=random.randint(0, 2**31)
                     )

def handle_start(user_id: int, first_name: str, last_name: str):
    """
    Метод, осуществляющий регистрацию пользователя
    :param user_id: int
    :param first_name: str
    :param last_name: str
    :return:
    """
    try:
        User.create(
            user_id=user_id,
            first_name=first_name,
            last_name=last_name
        )
        send(user_id, (f'Добро пожаловать в писок покупок, {first_name}\n\n'
                       'Выбери действие.'),
                       keyboard=create_keyboard(user_id),
                        )
    except IntegrityError:
        send(user_id, f'Рады снова видеть вас, {first_name}!',
             keyboard=create_keyboard(user_id))

def handle_new_product(user_id: int):
    """
       Обработчик команды add_product. Спрашивает у пользователя название продукта.
       Меняет состояние на "ожидание названия продукта"
       :param user_id: int
       :param text: str
       :return:
       """
    if User.get_or_none(User.user_id == user_id) is None:
        send(user_id, 'Вы не зарегистрированы. Выберите команду start',
             keyboard=create_keyboard(user_id))
        return
    send(user_id, 'Введите название продукта:', keyboard=create_keyboard(user_id))
    set_state(user_id, STATE_NEW_PRODUCT_TITLE, data={'user_id': user_id})

def process_product_save(user_id: int, text: str):
    """
    Сохраняет продукт, обнуляет состояние.
    :param user_id: int
    :param text: str
    :return:
    """
    user = User.get_or_none(User.user_id == user_id)
    max_pos = (Product.select(Product.position)
               .where(Product.user == user)
               .order_by(Product.position.desc()).first())
    data = get_data(user_id)
    data['title'] = text
    data['position'] = (max_pos.position + 1) if max_pos else 1
    new_product = Product(**data)
    new_product.save()
    clear_state(user_id)
    send(user_id, f'Продукт добавлен:\n{new_product}', keyboard=create_keyboard(user_id))

def handle_products(user_id: int):
    """
    Обработчик команды product_list. Паказывает пользователю список покупок с отметками "сделано".
    Меняет состояние на "ожидание номера продукта"
    :param user_id: int
    :return:
    """
    user = User.get_or_none(User.user_id == user_id)
    if user is None:
        send(user_id, 'Вы не зарегистрированы. Выберите команду start',
             keyboard=create_keyboard(user_id))
        return
    products = user.products.order_by(Product.position)
    result = list(map(str, list(products)))
    if not result:
        send(user_id, 'Ваш список товаров пуст.', keyboard=create_keyboard(user_id))
        return
    result.append('\nВведите номер продукта, чтобы изменить ее статус.')
    send(user_id, '\n'.join(result), keyboard=create_keyboard(user_id))
    set_state(user_id, STATE_PRODUCT_MAKE_DONE)

def process_product_done(user_id: int, text: str):
    """
    Метод, изменяющий статус покупки. Очищает состояние.
    :param user_id: int
    :param text: str
    :return:
    """
    try:
        position = int(text)
    except ValueError:
        send(user_id, 'Введите числовой номер товара', keyboard=create_keyboard(user_id))
        return
    product = Product.get_or_none(Product.position == position, Product.user_id == user_id)
    if product is None:
        send(user_id, 'Товара с таким номером не существует.', keyboard=create_keyboard(user_id))
        return
    product.is_done = not product.is_done
    product.save()
    clear_state(user_id)
    send(user_id, f'Статус обновлен:\n{product}', keyboard=create_keyboard(user_id))

def clear_list(user_id: int) -> int:
    """
    Метод, очищающий список покупок пользователя
    :param user_id: int
    :return: int
    """
    user = User.get_or_none(User.user_id == user_id)
    send(user_id, 'Данные успешно удалены. Ваш список товаров пуст.',
         keyboard=create_keyboard(user_id))
    return (
        Product
            .delete()
            .where(Product.user == user)
            .execute()
    )

# Основной цикл
print('Бот запущен...')

for event in longpoll.listen():
    if event.type == VkEventType.MESSAGE_NEW and event.to_me:
        user_id = event.user_id
        text = event.text.strip().lower()
        user_info = vk.users.get(user_ids=user_id)[0]
        first_name = user_info['first_name']
        last_name = user_info.get('last_name')
        state = get_state(user_id)
        if text == 'start':
            handle_start(user_id, first_name, last_name)
        elif text == 'add_product':
            handle_new_product(user_id)
        elif text == 'product_list':
            handle_products(user_id)
        elif text == 'clear_list':
            clear_list(user_id)
        elif state == STATE_NEW_PRODUCT_TITLE: #####
            process_product_save(user_id, text)
        elif state == STATE_PRODUCT_MAKE_DONE:
            process_product_done(user_id, text)
        else:
            send(user_id, (
                'Неизвестная команда. Выбери кнопку:'), keyboard=create_keyboard(user_id),
            )
