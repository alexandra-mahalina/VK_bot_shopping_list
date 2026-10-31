import vk_api
from vk_api.keyboard import VkKeyboard, VkKeyboardColor

def create_keyboard(user_id: int) -> str:
    """
    Метод, открывающий клавиатуру
    :param user_id: int
    :return: str
    """
    keyboard = VkKeyboard(one_time=True)
    keyboard.add_button("start", color=VkKeyboardColor.PRIMARY)
    keyboard.add_line()
    keyboard.add_button("add_product", color=VkKeyboardColor.SECONDARY)
    keyboard.add_button("product_list", color=VkKeyboardColor.SECONDARY)
    keyboard.add_line()
    keyboard.add_button("clear_list", color=VkKeyboardColor.NEGATIVE)
    return keyboard.get_keyboard()
