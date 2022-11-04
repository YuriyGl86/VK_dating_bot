import requests
from random import choice
from DB.db import calculate_age, get_blocked, get_favorites


class Candidate_selection:
    """
    Класс предоставляет получение информации о пользователях и их фотографиях. Сначала пишем несколько вспомогательных
    методов, потом в одном главном методе всё объединяем и выдаем результат.
    """

    def __init__(self, access_token, version='5.131'):
        self.token = access_token
        self.version = version
        self.params = {'access_token': self.token, 'v': self.version}

    def get_candidates_list(self, user_json):
        """
        метод, который принимает параметры для поиска и возвращает выборку из кандидатов через метод users.search с
        праметрами для поиска age_from, age_to, has_photo, sex, city и count=50 или больше. В дополнительном задании
        вообще сказано подумать как обойти ограничение в 1000. Т.е. выборка может быть большой.
        Возвращает СПИСОК из кандидатов (видимо список из словарей)
        """

        user_age = calculate_age(user_json['bdate'])  # считаем возраст по дате рождения через функцию Артема
        url = 'https://api.vk.com/method/users.search'  # Метод поиска людей по параметрам
        params = {'sex': 1 if user_json['sex'] == 2 else 2,
                  'city': user_json['city']['id'],
                  'age_from': user_age - 2,
                  'age_to': user_age + 2,
                  'has_photo': 1,
                  'count': 500
                  }
        response = requests.get(url, params={**self.params, **params})
        candidates_list = response.json()['response']['items']  # получаем список из словарей с кандидатами
        return candidates_list

    def get_photos_by_candidate_id(self, candidate_id):
        """
        метод, который принимает id ОДНОГО кандидата и через метод photos.get запрашивает все его фотографии.
        Метода возвращает список всех фотографий.
        """
        url = 'https://api.vk.com/method/photos.getAll'
        params = {'owner_id': candidate_id, 'extended': 1, 'photo_sizes': 1}
        response = requests.get(url, params={**self.params, **params})
        response_photo_list = response.json()['response']['items']  # Получаем список из словарей с параметрами и размерами фото
        return response_photo_list

    def filter_best_candidate_photos(self, photos_list):
        """
        Метод, который принимает на вход список фотографий и возвращает только 3 из них с наибольшим числом лайков в
        наибольшем размере
        """
        sizes = 's, m, x, o, p, q, r, y, z, w'  # размеры фотографий в порядке возрастания
        foto_lst = []
        for foto in photos_list:
            foto_likes = foto['likes']['count']  # получаем число лайков
            best_picture_url = sorted(foto['sizes'], key=lambda x: sizes.find(x['type']))[-1]['url'] # сортируем по
            # возрастанию используя как ключ порядковый индекс из списка размеров, и берем последнюю, т.е. самую большую
            foto_lst.append((foto_likes, best_picture_url))
        foto_lst.sort(reverse=True)
        best_candidate_photos = [i[1] for i in foto_lst[:3]]
        print(best_candidate_photos)
        return best_candidate_photos

    def get_candidate_for_user(self, user_json):
        """ Главный метод по подбору кандидата. Именно этот метод и будет вызывать бот, когда ему надо будет получить
        кандидата. Этот метод на вход получает словарь user_json c данными пользователя, обрабатывает его, используя
        написанные ранее вспомогательные методы и возвращает обратно в то место откуда вызван словарь с кандидатом.
        """
        candidate_list = self.get_candidates_list(user_json) # Получаем большой список кандидатов (500)
        black_list = get_blocked(user_json['id'])  # вызываешь функцию получения ЧС, которую напишет Артем
        favorites = get_favorites(user_json['id'])  # вызываешь функцию получения избранного, которую напишет Артем
        ignore_id_list = black_list + favorites  # получаешь общий список для игнора
        while True:
            candidate = choice(candidate_list)  # выбираем рандомно одного кандидата из списка
            if candidate['id'] not in ignore_id_list:
                print(candidate['id'])
                try:  # блок try т.к. профиль может быть закрытым и из него будет не достать фото
                    candidate_photos = self.get_photos_by_candidate_id(candidate['id'])
                except:
                    continue
                best_candidate_photos = self.filter_best_candidate_photos(candidate_photos)
                candidate['photo'] = best_candidate_photos
                return candidate


# user_json = {'id': 82185, 'bdate': '29.3.1986', 'city': {'id': 2, 'title': 'Санкт-Петербург'}, 'sex': 2,
#              'first_name': 'Юрий', 'last_name': 'Глущенко', 'can_access_closed': True, 'is_closed': False}

