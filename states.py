user_states = {}

def get_state(user_id: str):
    """
    Геттер, получающий состояние
    :param user_id: int
    :return: str
    """
    return user_states.get(user_id, {}).get('state')

def set_state(user_id: int, state: str, data=None):
    """
    Сеттер, изменяющий состояние
    :param user_id: int
    :param state: str
    :param data: dict or None
    :return:
    """
    user_states[user_id] = {'state': state, 'data': data or {}}

def get_data(user_id: int) -> dict:
    """
    # Геттер, получающий данные
    :param user_id: int
    :return: str
    """
    return user_states.get(user_id, {}).get('data', {})

def clear_state(user_id: int):
    """
    Очищает состояние
    :param user_id: int
    :return:
    """
    user_states.pop(user_id, None)

# Состояния:
STATE_NEW_PRODUCT_TITLE = 'new_product_title'
STATE_PRODUCT_MAKE_DONE = 'new_make_done'