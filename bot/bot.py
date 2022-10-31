import requests
from io import BytesIO

from vk_api.utils import get_random_id
import vk_api
from vk_api import VkUpload
from vk_api.longpoll import VkLongPoll
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.longpoll import VkEventType


class Bot:

    def __init__(self, key):
        self.authorize = vk_api.VkApi(token=key)  # Авторизуемся в ВК для управления нашей группой, используя token
        self.longpoll = VkLongPoll(self.authorize)  # Выбираем тип используемого API - Long Poll API
        self.upload = VkUpload(self.authorize)  # Загрузчик изображений на сервер в ВК
        self.VkEventType = VkEventType

    @staticmethod
    def __get_keyboard_for_bot():
        keyboard = VkKeyboard(one_time=False)  # создаем клавиатуру для бота
        keyboard.add_button('К следующему', color=VkKeyboardColor.PRIMARY)
        keyboard.add_line()
        keyboard.add_button('В избранное', color=VkKeyboardColor.POSITIVE)
        keyboard.add_button('В черный список', color=VkKeyboardColor.NEGATIVE)
        keyboard.add_line()
        keyboard.add_button('Список избранных', color=VkKeyboardColor.SECONDARY)
        keyboard_for_bot = keyboard.get_keyboard()
        return keyboard_for_bot

    def write_message(self, sender, message, attachment=None):
        self.authorize.method('messages.send',
                              {'user_id': sender, 'message': message, 'random_id': get_random_id(),
                               'attachment': attachment,
                               'keyboard': self.__get_keyboard_for_bot()})

    def upload_photo(self, url):
        img = requests.get(url).content
        f = BytesIO(img)

        response = self.upload.photo_messages(f)[0]

        owner_id = response['owner_id']
        photo_id = response['id']
        access_key = response['access_key']
        attachment = f'photo{owner_id}_{photo_id}'  # _{access_key}
        return attachment

    def get_attachment(self, photo_link_list: list):
        attachment_list = []
        for link in photo_link_list:
            uploaded_photo = self.upload_photo(link)
            attachment_list.append(uploaded_photo)
        attachment_info = ','.join(attachment_list)
        return attachment_info

    def get_user_info(self, user_id):
        user_info = self.authorize.method('users.get', {"user_ids": user_id, 'fields': 'city, bdate, sex'})[0]
        return user_info['first_name'], user_info['last_name'], user_info['city']['title'], user_info['bdate'], user_info['sex']

    def send_candidate(self, sender):
        # вызываем функцию подборакандидата, получаем данные и ссылки
        photo_list = ['https://vdp.mycdn.me/getImage?id=411588037337&idx=0&thumbType=32',
                      'https://www.mam4.ru/media/upload/user/5422/19/6170.jpg',
                      'https://avatanplus.com/files/resources/mid/5ab5736f0579416254cae9ae.png',
                      ]
        candidate_id = 'candidate_id'
        fio = "fio"
        link = "link"
        attachment_photos = self.get_attachment(photo_list)
        self.write_message(sender, f'Вот отличный кандидат:\n{fio}\n{link}', attachment=attachment_photos)
        return candidate_id, fio, link, photo_list
