import configparser
import requests
from bot.bot import Bot
from bot.bot_token import key
import datetime
from DB.db import rec_favorites, rec_blocked

config = configparser.ConfigParser()
config.read('token.ini')
TOKEN = config['VK_API']['access_token']

class Candidate_selection():
    '''
    Класс предоставляет получение информации о пользователях и их фотографий
    '''
    def __init__(
        self,
        user_access_token = TOKEN,
        version = '5.131',
        album = 'profile',
        extended = int(True),
        rev = int(False)
        ):
        self.UAT = user_access_token
        self.V = version
        self.A = album
        self.EX = extended
        self.R = rev
        
    def take_user_all_info(self) -> int:
        '''
        Метод берёт всю информацию о пользователе, который воспользовался ботом
        '''
        user_info = Bot(key).get_user_info(Bot().get_user_info())
        return user_info        
        
    def candidate_parametrs(self) -> dict:
        try:
            if self.take_user_all_info()['sex'] == 1:
                natural_sex = 2
            elif self.take_user_all_info()['sex'] == 2:
                natural_sex = 1
            else:
                KeyError
        except KeyError:
            return 'Не определён пол'
        candidate_city = self.take_user_all_info()['city']['title']
        user_age = datetime.datetime.now().year - int(self.take_user_all_info()['bdate'][4:])
        url = 'https://api.vk.com/method/users.search'
        response = requests.get(
            url,
            params = {
                'is_closed': False,
                'can_access_closed': False,
                'access_token': self.UAT,
                'fields': 'city, bdate, sex',
                'age_from': user_age - 3,
                'age_to': user_age + 3,
                'hometown': candidate_city,
                'sex': natural_sex,
                'v': self.V,
                'count': 1
            }
        )
        return response.json()
     
    def get_parametrs_to_search(self) -> dict:
        for own_id in self.candidate_parametrs().values():
            candidat_id = own_id['items'][0]['id']
        url = 'https://api.vk.com/method/photos.get'
        # вызываем и вводим параметры вызова
        response = requests.get(
            url,
            params = {
            'access_token': self.UAT,
            'owner_id': candidat_id,
            'v': self.V,
            'album_id': self.A,
            'extended': self.EX,
            'rev': self.R,
            }
        )
        return response.json()

    def candidate_photo(self) -> dict:
        # метод выборки фотографий с наибольшей популярностью
        list_likes = []
        list_info = []
        url_list = []
        best_photo = []
        for item in self.get_parametrs_to_search().values():
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

    def unification_info(self) -> dict:
        get_params_info = self.candidate_parametrs().get('response')['items'][0]
        get_params_info.update(self.candidate_photo())
        return get_params_info

# print(Candidate_selection().unification_info())

class Checking_for_id():
    def __init__(
        self,
        ignore_list = rec_blocked(),
        favorite_list = rec_favorites(),
        candidate_id = Candidate_selection.unification_info()['id']
        ):
        self.IL = ignore_list
        self.FL = favorite_list
        self.CID = candidate_id
    
    def checking_lists(self):
        if self.CID not in self.IL and self.FL:
            return Candidate_selection().unification_info()
        
# print(Checking_for_id().checking_lists())


import configparser

config = configparser.ConfigParser()
config.read('token.ini')
TOKEN = config['VK_API']['access_token']