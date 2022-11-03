import requests
from io import BytesIO

from vk_api.utils import get_random_id
import vk_api
from vk_api import VkUpload
from vk_api.longpoll import VkLongPoll
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.longpoll import VkEventType

# from DB.db import get_favorites


class Bot:
    """
    Класс, описывающий работу бота для чата в ВК
    :param key: - token c правами для доступа к сообщениям и фотографиям сообщества ВК
    :type key: str
    """

    def __init__(self, key: str):
        self.authorize = vk_api.VkApi(token=key)  # Авторизуемся в ВК для управления нашей группой, используя token
        self.longpoll = VkLongPoll(self.authorize)  # Выбираем тип используемого API - Long Poll API
        self.upload = VkUpload(self.authorize)  # Загрузчик изображений на сервер в ВК
        self.VkEventType = VkEventType  # Для проверки типа произошедешего события в группе ( что пришло новое сооьщение)

    @staticmethod
    def __get_keyboard_for_bot() -> dict:
        """
        Метод создает клавиатуру (кнопки) для бота
        :return: json клавиатуры, который можно прикрепить к отправляемому сообщению
        """
        keyboard = VkKeyboard(one_time=False)  # создаем клавиатуру для бота
        keyboard.add_button('Начать', color=VkKeyboardColor.PRIMARY)  # добавляем кнопку
        keyboard.add_line()
        keyboard.add_button('Предложить кандидата', color=VkKeyboardColor.PRIMARY)  # добавляем кнопку
        keyboard.add_line()  # добавляем перенос на следующую строку
        keyboard.add_button('В избранное', color=VkKeyboardColor.POSITIVE)
        keyboard.add_button('В черный список', color=VkKeyboardColor.NEGATIVE)
        keyboard.add_line()
        keyboard.add_button('Список избранных', color=VkKeyboardColor.SECONDARY)
        keyboard_for_bot = keyboard.get_keyboard()
        return keyboard_for_bot

    def write_message(self, sender: int, message: str, attachment: str = None) -> None:
        """
        Метод для отправки сообщения ботом от имени сообщества.
        Параметры:
        :param sender: id пользователя, в беседу с которым отправляем сообщение.
        :type sender: int

        :param message: текст сообщения
        :type message: str

        :param attachment: если указан, то в сообщение будет прикреплены вложения. Должен быть указан в специальном
        формате в соответствии с документацией https://dev.vk.com/method/messages.send
        :type attachment: str
        """

        self.authorize.method('messages.send',
                              {'user_id': sender, 'message': message, 'random_id': get_random_id(),
                               'attachment': attachment,
                               'keyboard': self.__get_keyboard_for_bot()})

    def upload_photo(self, url: str) -> str:
        """
        Метод для загрузки одного изображения, доступного по ссылке, на сервер ВК. Возвращает параметры загруженного на
        сервер файла в виде строки в специальном формате, которые необходимы, чтобы прикрепить загруженный файл к
        сообщению.
        :param url: прямая ссылка на фотографию.
        :type url: str
        """
        img = requests.get(url).content  # Получаем фото по ссылке в байтовом виде
        f = BytesIO(img)  # Загружаем фото в оперативную память, чтобы не сохранять на диске

        response = self.upload.photo_messages(f)[0]  # Загружаем фото на сервер ВК, получаем json c параметрами загрузки

        owner_id = response['owner_id']
        photo_id = response['id']
        access_key = response['access_key']
        attachment = f'photo{owner_id}_{photo_id}'  # Собираем параметры загруженного файла в нужный формат в виде строки
        return attachment

    def get_attachment(self, photo_link_list: list[str]) -> str:
        """
        Метод загружает фотографии из списка на сервер ВК
        :param photo_link_list: список ссылок на фотографии.
        :type photo_link_list: list
        :return: Строка в формате <type><owner_id>_<media_id> с параметрами всех загруженных изображений через запятую
        """
        attachment_list = []
        for link in photo_link_list:
            uploaded_photo = self.upload_photo(link)
            attachment_list.append(uploaded_photo)
        attachment_info = ','.join(attachment_list)
        return attachment_info

    def get_user_info(self, user_id: int) -> dict:
        """
        Метод получает информацию о пользователе ВК по его id
        :param user_id: id пользователя ВК
        :type user_id: int
        :return: словарь, содержащий ключи id, bdate, city, sex, first_name, last_name и другие.
        """
        user_info = self.authorize.method('users.get', {"user_ids": user_id, 'fields': 'city, bdate, sex'})[0]
        return user_info

    def send_candidate(self, user: dict) -> dict:
        """
        Метод, который будет генерировать кандидата для знакомства и отправлять его пользователю в чат.
        :param user: словарь с данными пользователя, содержащий в т.ч. ключ с id.
        :type user: dict
        :return: данные кандидата
        """
        # candidate = get_candidate(user)вызываем функцию подбора кандидата от Марка, получаем данные кандидата и ссылки
        candidate = {'id': 31539255, 'city': {'id': 185, 'title': 'Севастополь'}, 'first_name': 'Виктория',
                     'last_name': 'Александровна', 'can_access_closed': True, 'is_closed': False,
                     'photo': ['https://sun9-north.userapi.com/sun9-80/s/v1/if1/6_IfSpt0bV6fC3fnFOf3djs7zZW0kW-FYajV5zXYplYW5N-9T4mH4qkhG88SdPNq4CdG-u9K.jpg?size=720x1080&quality=96&type=album',
                               'https://sun9-north.userapi.com/sun9-85/s/v1/if1/8RjXNZ07stMRMZTtpVlH5Y0WAfNP9pfK9anL9LzaWDXYN2fZPqBWKJcAL3zM4RDsVO2xbw.jpg?size=476x1080&quality=96&type=album',
                               'https://sun9-east.userapi.com/sun9-25/s/v1/ig2/ID35QRwSB4YXQBTUVggmZ-Aib008MgooF0Zgx5yUbvWrlBkZ-5z1ObOwemQvZlZJc1FT4bmv37eAApZXgJhnxjYE.jpg?size=510x680&quality=95&type=album'
                               ]}
        candidate_id = candidate['id']
        fio = candidate['first_name'] + ' ' + candidate['last_name']
        link = 'https://vk.com/id' + str(candidate_id)
        photo_list = candidate['photo']
        attachment_photos = self.get_attachment(photo_list)
        self.write_message(user['id'], f'Вот отличный кандидат:\n{fio}\n{link}', attachment=attachment_photos)
        return candidate

    def send_favorites_list(self, sender: int) -> None:
        """
        Метод получает список избранного для указанного пользователя и отправляет в чат с пользователем в нужном формате.
        :param sender: id ткущего пользователя, который общается с ботом.
        :type sender: int
        """
        # favorites_list = get_favorites(sender) здесь будет вызов функции от Артёма, для получения списка избранного для данного user
        favorites_list = ['82185', '82186', '82187']
        for candidate_id in favorites_list:
            link = 'https://vk.com/id' + str(candidate_id)
            self.write_message(sender, link)
