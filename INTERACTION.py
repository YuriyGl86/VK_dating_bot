import configparser
import requests
from bot.bot import Bot
import datetime
# from data import rec_blocked_list, rec_favorites_list
# from DB.db import rec_favorites, rec_blocked

config = configparser.ConfigParser()
config.read('new_token.ini')
TOKEN = config['VK_API']['access_token']
KEY = config['VK_API']['key_oauth']

class Candidate_selection():
    '''
    Метод предоставляет получение информации о кандидатах и их фотографий
    user_access_token -- токен авторизации приложения -> str
    version -- версия API VK -> str
    album, extended, rev -- параметры метода photos.get API VK
    '''
    def __init__(
        self,
        user_access_token = TOKEN,
        version = '5.131',
        album = 'profile',
        extended = 1,
        rev = 0
        ):
        self.UAT = user_access_token
        self.V = version
        self.A = album
        self.EX = extended
        self.R = rev      
    
    user_info = {'id': 501244677, 'bdate': '7.3.1993', 'city': {'id': 185, 'title': 'Севастополь'}, 'sex': 2, 'first_name': 'Марк', 'last_name': 'Изотов', 'can_access_closed': True, 'is_closed': False}
   
    def candidate_parametrs(self, user_info: dict) -> dict:
        '''
        Функция, которая по параметрам пользователя подбирает параметры для кандидата
        user_info -- принимает на вход параметры пользователя
        '''
        try:
            if user_info['sex'] == 1:
                natural_sex = 2
            elif user_info['sex'] == 2:
                natural_sex = 1
            else:
                KeyError
        except KeyError:
            return 'Не определён пол'
        candidate_city = user_info['city']['title']
        user_age = datetime.datetime.now().year - int(user_info['bdate'][4:])
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
        '''
        Функция, которая определяет параметры фотографий со страницы кандидата
        '''
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
        '''
        Функция возвращает словарь с тремя самыми поплуярными фотографиями 
        Размеры фотографий наибольшие из представленных
        '''
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
        '''
        Функция соединяет словарь с параметрами кандидата
        и словарь с фотографиями кандидата
        '''
        get_params_info = self.candidate_parametrs(self.user_info).get('response')['items'][0]
        get_params_info.update(self.candidate_photo())
        return get_params_info


# getx = Candidate_selection().candidate_parametrs(Candidate_selection.user_info)
# print(getx)
print(Candidate_selection().unification_info())


