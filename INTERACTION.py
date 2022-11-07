
''''''

import configparser
import requests
import datetime
from DB.db import get_viewed

config = configparser.ConfigParser()
config.read('new_token.ini')
TOKEN = config['VK_API']['vk_access_token']

class Candidate_selection():
    '''
    Метод предоставляет получение информации о кандидатах и их фотографий
    user -- на вход принимает данные пользователя -> dict
    token -- токен авторизации приложения -> str
    version -- версия VK API - str
    '''
    def __init__(self, user):
        self.user = user
        self.token = TOKEN
        self.version = '5.131'

    def passing_closed_profile(self):
        try:
            if self.user['sex'] == 1:
                natural_sex = 2
            elif self.user['sex'] == 2:
                natural_sex = 1
            else:
                KeyError
        except KeyError:
            return 'Не определён пол'
        candidate_city = self.user['city']['title']
        user_year = self.user['bdate'].split('.')[2]
        user_age = datetime.datetime.now().year - int(user_year)
        url = 'https://api.vk.com/method/users.search'
        candidate_count = len(get_viewed(self.user['id']))
        response = requests.get(
            url,
            params = {
                'has_photo': 1,
                'access_token': self.token,
                'fields': 'city, bdate, sex',
                'age_from': user_age - 3,
                'age_to': user_age + 3,
                'hometown': candidate_city,
                'sex': natural_sex,
                'v': self.version,
                'offset': candidate_count+1,
                'count': 1
            }
        )
        result = response.json()['response']
        return result
    
    def candidate_parametrs(self) -> dict:
        '''
        Функция, которая по параметрам пользователя подбирает параметры кандидата
        '''
        try:
            if self.user['sex'] == 1:
                natural_sex = 2
            elif self.user['sex'] == 2:
                natural_sex = 1
            else:
                KeyError
        except KeyError:
            return 'Не определён пол'
        candidate_city = self.user['city']['title']
        user_year = self.user['bdate'].split('.')[2]
        user_age = datetime.datetime.now().year - int(user_year)
        url = 'https://api.vk.com/method/users.search'
        candidate_count = len(get_viewed(self.user['id']))
        response = requests.get(
            url,
            params = {
                'has_photo': 1,
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
        while result['items'][0]['is_closed'] == True:
            # return 'пошёл нахуй'
            get_viewed(self.user['id']).append('None')
            return self.candidate_parametrs()
        return result
    
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
        # if get_json.values()['error_code'] == 30: #ошибка закрытого профиля
        #     return self.candidate_parametrs()
        # метод выборки фотографий с наибольшей популярностью
        list_likes = []
        list_info = []
        url_list = []
        best_photo = []
        for item in get_json.values():
            for inside_params in item['items']:
                list_likes.append(inside_params['likes'].get('count'))
                list_info.append(inside_params['sizes'])
                # вот на этом моменте выделяется фотография со всеми размерами и ссылками по наибольшему количеству лайков
                # в дальнейшем нет нужды фильтровать размеры фотографий, так как через return возвращаем автоматически
                # наибольшее значение (главное расположить строку "url_list.append(url)" в нужном столбце)
                info_photo_likes = sorted(dict(zip(list_likes, list_info)).items(), reverse=True)[:3]
            for items in info_photo_likes:
                for i in items[1]:
                    best_photo.append(i)
                    url = i['url']
                url_list.append(url)
        return {'photo': url_list}
    #     # return get_json

    def get_candidate_for_user(self) -> dict:
        '''
        Функция соединяет словарь с параметрами кандидата
        и словарь с фотографиями кандидата
        '''
        candidat = self.candidate_parametrs()['items'][0]
        candidat.update(self.candidate_photo())
        return candidat

# def check_errors():
#     d = {
#     'id': 501244677,
#     'bdate': '7.3.1993',
#     'city': {'id': 185, 'title': 'Севастополь'},
#     'sex': 2,
#     'first_name': 'Марк',
#     'last_name': 'Изотов',
#     'can_access_closed': True,
#     'is_closed': False
#     }
    # print(Candidate_selection(d).candidate_parametrs())
    # print(Candidate_selection(d).candidate_photo())
    # print(Candidate_selection(d).get_candidate_for_user())
    # if Candidate_selection(d).candidate_photo()['error']['error_code']==30:
    #     print('пошёл нахер')
    # else:
    #     print(Candidate_selection(d).candidate_photo())
    
# check_errors()

# 'error': {'error_code': 30, 'error_msg': 'This profile is private', 