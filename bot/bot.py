import requests
from io import BytesIO

from vk_api.utils import get_random_id
import vk_api
from vk_api import VkUpload
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor

from DB.db import get_favorites, rec_viewed
from INTERACTION import Candidate_selection
# from temp import CandidateGenerator  # Используется для целей тестирования


class Bot:
    """
    Класс, описывающий работу бота для чата в ВК.
    :param key: token c правами доступа сообщества от имени которого будет отвечать бот, с доступом к сообщениям и
    фотографиям сообщества.
    :type key: str

    :param vk_token: token c правами доступа пользователя. Для выполнения поиска кандидата и подбора фотографий.
    :type vk_token: str

    """

    def __init__(self, key: str, vk_token):
        self.authorize = vk_api.VkApi(token=key)  # Авторизуемся в ВК для управления нашей группой, используя token
        self.longpoll = VkLongPoll(self.authorize)  # Выбираем тип используемого API - Long Poll API
        self.upload = VkUpload(self.authorize)  # Загрузчик изображений на сервер в ВК
        self.VkEventType = VkEventType  # Для проверки типа произошедшего события (что пришло новое сообщение)
        self.vk_token = vk_token  # Храним токен пользователя, через который будем подбирать кандидата.
        self.user_new_vk_token = None  # Аттрибут экземпляра класса, будет хранить пользовательский токен

    @staticmethod
    def __get_keyboard_for_bot() -> dict:
        """
        Метод создает клавиатуру (кнопки) для бота.
        :return: json с параметрами клавиатуры, который можно прикрепить к отправляемому сообщению
        """
        keyboard = VkKeyboard(one_time=False)  # создаем клавиатуру для бота
        keyboard.add_button('Начать', color=VkKeyboardColor.PRIMARY)  # добавляем кнопку
        keyboard.add_button('Свой токен', color=VkKeyboardColor.PRIMARY)
        keyboard.add_line()  # добавляем перенос на следующую строку
        keyboard.add_button('Предложить кандидата', color=VkKeyboardColor.PRIMARY)  # добавляем кнопку
        keyboard.add_line()  # добавляем перенос на следующую строку
        keyboard.add_button('В избранное', color=VkKeyboardColor.POSITIVE)
        keyboard.add_button('В черный список', color=VkKeyboardColor.NEGATIVE)
        keyboard.add_line()
        keyboard.add_button('Список избранных', color=VkKeyboardColor.SECONDARY)
        keyboard_for_bot = keyboard.get_keyboard()
        return keyboard_for_bot

    def write_message(self, user_id: int, message: str, attachment: str = None) -> None:
        """
        Метод для отправки сообщения ботом от имени сообщества в чат с пользователем.
        Параметры:
        :param user_id: id пользователя, в беседу с которым отправляем сообщение.
        :type user_id: int

        :param message: текст сообщения
        :type message: str

        :param attachment: если указан, то в сообщение будут прикреплены предварительно загруженные на сервера ВК
        вложения. Указывается в специальном формате согласно документации: https://dev.vk.com/method/messages.send
        :type attachment: str
        """

        self.authorize.method('messages.send',
                              {'user_id': user_id,
                               'message': message,
                               'random_id': get_random_id(),  # генерирует случайный id сообщения, для избежания дублей
                               'attachment': attachment,
                               'keyboard': self.__get_keyboard_for_bot()})

    def upload_photo(self, url: str) -> str:
        """
        Метод для загрузки одного изображения, доступного по ссылке, на сервер ВК. Возвращает параметры загруженного на
        сервер файла в виде строки в специальном формате согласно документации: https://dev.vk.com/method/messages.send,
        которые необходимы, чтобы прикрепить загруженный файл к сообщению.
        :param url: прямая ссылка на фотографию.
        :type url: str

        :return: Строка в формате <type><owner_id>_<media_id>
        """

        img = requests.get(url).content  # Получаем фото по ссылке в байтовом виде
        f = BytesIO(img)  # Загружаем фото в оперативную память, чтобы не сохранять на диске

        response = self.upload.photo_messages(f)[0]  # Загружаем фото на сервер ВК, получаем json c параметрами загрузки

        owner_id = response['owner_id']
        photo_id = response['id']
        attachment = f'photo{owner_id}_{photo_id}'  # Собираем параметры загруженного файла в нужный формат
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
        Метод получает подробную информацию о пользователе ВК по его id.
        :param user_id: id пользователя ВК
        :type user_id: int

        :return: словарь, содержащий как минимум ключи id, bdate, city, sex, first_name, last_name и другие.
        """

        user_info = self.authorize.method('users.get', {"user_ids": user_id, 'fields': 'city, bdate, sex'})[0]
        return user_info

    def send_candidate(self, user: dict) -> dict:
        """
        Метод, который будет генерировать кандидата для знакомства и отправлять его пользователю в чат.
        :param user: словарь с данными пользователя, содержащий в т.ч. ключ с id.
        :type user: dict

        :return: данные кандидата в виде словаря, содержащего как минимум ключи id, first_name, last_name и ключ photo,
        по которому доступен список из ссылок на фотографии пользователя.
        """

        if self.user_new_vk_token:  # Если пользователь вводил свой токен, то пробуем его использовать
            try:
                candidate = Candidate_selection(user, self.user_new_vk_token).get_candidate_for_user()
                # candidate = CandidateGenerator(self.user_new_vk_token).get_candidate_for_user(user)
            except:
                message = 'Предложенный Вами токен некорректен, далее продолжаем использовать стандартный токен'
                self.user_new_vk_token = None
                self.write_message(user['id'], message=message)
                candidate = Candidate_selection(user, self.vk_token).get_candidate_for_user()
                # candidate = CandidateGenerator(self.vk_token).get_candidate_for_user(user)
        else:  # Если не вводил свой токен, то используем стандартный
            candidate = Candidate_selection(user, self.vk_token).get_candidate_for_user()
            # candidate = CandidateGenerator(self.vk_token).get_candidate_for_user(user)

        candidate_id = candidate['id']  # Добавляем предложенного кандидата в список просмотренных.
        rec_viewed(candidate_id, user['id'])
        fio = candidate['first_name'] + ' ' + candidate['last_name']
        link = 'https://vk.com/id' + str(candidate_id)
        photo_list = candidate['photo']
        attachment_photos = self.get_attachment(photo_list)
        self.write_message(user['id'], f'Вот отличный кандидат:\n{fio}\n{link}', attachment=attachment_photos)
        return candidate

    def send_favorites_list_to_user(self, user_id: int) -> None:
        """
        Метод получает список избранного для указанного пользователя из базы данных и отправляет в чат с пользователем.
        :param user_id: id ткущего пользователя, который общается с ботом.
        :type user_id: int
        """

        favorites_list = get_favorites(user_id)  # функция Артёма, для получения списка избранного из БД
        candidates = ''
        for candidate_id in favorites_list:
            link = 'https://vk.com/id' + str(candidate_id) + '\n'
            candidates += link

        self.write_message(user_id, candidates)



