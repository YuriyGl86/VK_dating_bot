import requests
from random import choice
from DB.db import calculate_age, get_blocked, get_favorites
import time


class CandidateGenerator:
    """
    Класс предоставляет получение информации о пользователях и их фотографиях. Сначала пишем несколько вспомогательных
    методов, потом в одном главном методе всё объединяем и выдаем результат.
    :param access_token: token c правами доступа пользователя. Для выполнения поиска кандидата и подбора фотографий.
    :type access_token: str
    """

    def __init__(self, access_token, version='5.131'):
        self.token = access_token
        self.version = version
        self.params = {'access_token': self.token, 'v': self.version}

    def get_candidates_list(self, user_json: dict) -> list[dict]:
        """
        Метод, который принимает параметры для поиска и возвращает выборку из кандидатов через метод users.search с
        параметрами для поиска age_from, age_to, has_photo, sex, city и count=50 или больше. В дополнительном задании
        вообще сказано подумать как обойти ограничение в 1000. Т.е. выборка может быть большой.
        Возвращает СПИСОК из кандидатов (видимо список из словарей)
        :param user_json: словарь с данными пользователя содержащий как минимум ключи id, bdate, city, sex, first_name,
        last_name и другие.
        :type user_json: dict

        :return: список, содержащий словари с данными кандидатов.
        """

        user_age = calculate_age(user_json['bdate'])  # считаем возраст по дате рождения через функцию Артема
        url = 'https://api.vk.com/method/users.search'  # Метод поиска людей по параметрам
        print('город для поиска = ', user_json['city']['id'], user_json['city']['title'])
        params = {'sex': 1 if user_json['sex'] == 2 else 2,
                  'city_id': user_json['city']['id'],
                  'age_from': user_age - 2,
                  'age_to': user_age + 2,
                  'has_photo': 1,
                  'count': 500,
                  'fields': 'city'
                  }
        response = requests.get(url, params={**self.params, **params})
        print('число записей в выборке', response.json()['response']['count'])
        candidates_list = response.json()['response']['items']  # получаем список из словарей с кандидатами
        print('Число записей в текущем списке кандидатов = ', len(candidates_list))
        return candidates_list

    def get_photos_by_candidate_id(self, candidate_id: str) -> list[dict]:
        """
        Метод, который принимает id ОДНОГО кандидата и через метод photos.get запрашивает все его фотографии.
        Метода возвращает список всех фотографий, даже если их больше 50.
        :param candidate_id: id потенциального кандидата, пользователя ВК.
        :type candidate_id: str

        :return: список словарей, которые содержат информацию по фотографиям и размеры фотографий.
        """
        # url = 'https://api.vk.com/method/photos.getAll'
        # params = {'owner_id': candidate_id, 'extended': 1, 'photo_sizes': 1}
        # response = requests.get(url, params={**self.params, **params})
        # print(response.json())
        # response_photo_list = response.json()['response']['items']  # список словарей с параметрами и размерами фото
        # print('Число фото в выборке = ', len(response_photo_list), 'позиция', )
        # return response_photo_list

        url = 'https://api.vk.com/method/photos.get'
        params = {'owner_id': candidate_id, 'extended': 1, 'photo_sizes': 1, 'album_id': 'profile'}
        response = requests.get(url, params={**self.params, **params})
        print('число фото в профиле', response.json()['response']['count'])
        response_photo_list = response.json()['response']['items']  # список словарей с параметрами и размерами фото
        print('Число фото в выборке = ', len(response_photo_list))
        pages = response.json()['response']['count'] // 50  # число страниц, если фото в профиле больше 50
        print('offsets', pages)
        for page in range(1, pages + 1):
            time.sleep(0.4)  # Задержка, т.к. к ВК API с ключом пользователя можно обращаться не чаще 3 раз в секунду
            add_response = requests.get(url, params={**self.params, **params, 'offset': page * 50}).json()
            add_photos = add_response['response']['items']
            response_photo_list.extend(add_photos)
        print('Число фото в полной выборке = ', len(response_photo_list))
        return response_photo_list

    @staticmethod
    def filter_best_candidate_photos(photos_list: list[dict]) -> list[str]:
        """
        Метод, который принимает на вход список фотографий и возвращает только 3 из них с наибольшим числом лайков в
        наибольшем размере.
        :param photos_list: список словарей, которые содержат информацию по фотографиям и размеры фотографий.
        :type photos_list: list

        :return: список из трех ссылок в формате строк
        """
        sizes = 's, m, x, o, p, q, r, y, z, w'  # размеры фотографий в порядке возрастания
        foto_lst = []
        for foto in photos_list:
            foto_likes = foto['likes']['count']  # получаем число лайков
            best_picture_url = sorted(foto['sizes'], key=lambda x: sizes.find(x['type']))[-1]['url']  # сортируем по
            # возрастанию используя как ключ порядковый индекс из списка размеров, и берем последнюю, т.е. самую большую
            foto_lst.append((foto_likes, best_picture_url))  # Добавляем в список картеж из числа лайков и ссылки
        foto_lst.sort(reverse=True)  # Сортируем картежи по первому элементу, т.е. по лайкам
        best_candidate_photos = [i[1] for i in foto_lst[:3]]  # Из первых трех картежей убираем лайки, оставляем ссылки
        # print(best_candidate_photos)
        return best_candidate_photos

    def get_candidate_for_user(self, user_json: dict) -> dict:
        """ Главный метод по подбору кандидата. Именно этот метод и будет вызывать бот, когда ему надо будет получить
        кандидата. Этот метод на вход получает словарь user_json c данными пользователя, обрабатывает его, используя
        написанные ранее вспомогательные методы и возвращает обратно в то же самое место откуда он был вызван словарь
        с данными кандидата.

        :param user_json: словарь с данными пользователя содержащий как минимум ключи id, bdate, city, sex, first_name,
        last_name и другие.
        :type user_json: dict

        :return: словарь с данными кандидата, содержащий, в том числе список из ссылок на 3 лучшие фотографии.
        """
        candidate_list = self.get_candidates_list(user_json)  # Получаем большой список кандидатов (500)
        black_list = get_blocked(user_json['id'])  # вызываешь функцию получения ЧС, которую напишет Артем
        favorites = get_favorites(user_json['id'])  # вызываешь функцию получения избранного, которую напишет Артем
        ignore_id_list = black_list + favorites  # получаешь общий список id для игнорирования
        while True:
            candidate = choice(candidate_list)  # выбираем рандомно одного кандидата из списка
            if candidate['id'] not in ignore_id_list:
                print('candidate id = ', candidate['id'])
                try:  # Блок try т.к. профиль может быть закрытым и из него будет не достать фото.
                    candidate_photos = self.get_photos_by_candidate_id(candidate['id'])
                except:
                    continue
                best_candidate_photos = self.filter_best_candidate_photos(candidate_photos)
                candidate['photo'] = best_candidate_photos
                try:
                    print('город кандидата: ', candidate['city'])
                except:
                    print('У кандидата нет города')
                print('\n---------------\n')
                return candidate

# user_json = {'id': 82185, 'bdate': '29.3.1986', 'city': {'id': 2, 'title': 'Санкт-Петербург'}, 'sex': 2,
#              'first_name': 'Юрий', 'last_name': 'Глущенко', 'can_access_closed': True, 'is_closed': False}
