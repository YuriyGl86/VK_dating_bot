'''
Модуль INTERACTION содержит класс, который осуществляет взаимодействие между
API ВКонтакте и БД. Модуль импортируется в модуль bot. Получив на вход
данные пользователя, производит подбор кандидатуры, затем выборку фотографий и,
наконец, компонует данные в один словарь.
'''

import configparser
import requests
import datetime
from DB.db import get_viewed, rec_viewed

config = configparser.ConfigParser()
config.read('new_token.ini')
TOKEN = config['VK_API']['vk_access_token']

class Candidate_selection():
    '''
    Метод предоставляет получение информации о кандидатах и их фотографий
    user: на вход принимает данные пользователя -> dict
    token: токен авторизации приложения -> str
    version: версия VK API - str
    '''
    def __init__(self, user, vk_user_token):
        self.user = user
        self.token = vk_user_token
        self.version = '5.131'

    def candidate_parametrs(self) -> dict:
        '''
        Функция, которая по параметрам пользователя подбирает параметры кандидата,
        а так же фильрует профиля с закрытыми страницами
        '''
        try:
            if self.user['sex'] == 1:
                natural_sex = 2
            elif self.user['sex'] == 2:
                natural_sex = 1
            else:
                KeyError
        except KeyError:
            return 'Пол пользователя не определён'
        candidate_city = self.user['city']['title'] # подбираем город поиска кандидата
        user_year = self.user['bdate'].split('.')[2] # определяем год рождения пользователя
        user_age = datetime.datetime.now().year - int(user_year) # определяем возраст пользователя
        url = 'https://api.vk.com/method/users.search'
        candidate_count = len(get_viewed(self.user['id'])) # переменная int, определяет параметр offset
        response = requests.get(
            url,
            params = {
                'access_token': self.token,
                'fields': 'city, bdate, sex',
                'age_from': user_age - 3,
                'age_to': user_age + 3,
                'hometown': candidate_city,
                'sex': natural_sex,
                'v': self.version,
                'offset': candidate_count,
                'count': 1
            }
        )
        result = response.json()['response']
        if result['items'][0]['is_closed'] == True: # обход закрытых профилей
            rec_viewed(result['items'][0]['id'], self.user['id']) # но с записью в БД
            return self.candidate_parametrs() # если параметр подтвердился - то производится новая итерация,
        return result                         # пока параметр 'is_closed' не станет False
    
    def candidate_photo(self) -> dict:
        '''
        Функция возвращает словарь с тремя самыми поплуярными фотографиями 
        Размеры фотографий наибольшие из представленных
        '''
        candidat_id = self.candidate_parametrs()['items'][0]['id']
        url = 'https://api.vk.com/method/photos.get'
        response = requests.get(
            url,
            params = {
            'access_token': self.token,
            'owner_id': candidat_id,
            'v': self.version,
            'album_id': 'profile',
            'extended': 1,
            'rev': 0,
            }
        )
        get_json = response.json()
        list_likes = []
        list_info = []
        url_list = []
        best_photo = []
        for item in get_json.values(): # метод выборки фотографий с наибольшей популярностью
            for inside_params in item['items']:
                list_likes.append(inside_params['likes'].get('count')) # находим в словаре необходимые данные о количестве лайков под фото
                list_info.append(inside_params['sizes']) # находим параметр размеров фотографий
                info_photo_likes = sorted(dict(zip(list_likes, list_info)).items(), reverse=True)[:3] # сортируем по количеству лайков с конца
            for items in info_photo_likes:                                                            # и берём три фотографии с наибольшим количеством лайков
                for i in items[1]:
                    best_photo.append(i)
                    url = i['url']
                url_list.append(url) # определяем через итерацию наибольшие форматы фотографий
        return {'photo': url_list} # формируем словарь

    def get_candidate_for_user(self) -> dict:
        '''
        Функция соединяет словарь с параметрами кандидата
        и словарь с фотографиями кандидата
        '''
        candidat = self.candidate_parametrs()['items'][0]
        candidat.update(self.candidate_photo())
        return candidat