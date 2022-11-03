import configparser
import requests

config = configparser.ConfigParser()
config.read('token.ini')
TOKEN = config['VK_API']['access_token']

class Candidate_Selection():
    
    def __init__(
        self,
        user_age,
        user_sex,
        user_city,
        user_access_token = TOKEN,
        version = '5.131',
        album = 'profile',
        extended = int(True),
        rev = int(False)
        ):
        self.UA = user_age
        self.US = user_sex
        self.UC = user_city
        self.UAT = user_access_token
        self.V = version
        self.A = album
        self.EX = extended
        self.R = rev
        
    def candidate_parametrs(self):
        url = 'https://api.vk.com/method/users.search'
        response = requests.get(
            url,
            params = {
                'is_closed': False,
                'can_access_closed': False,
                'access_token': self.UAT,
                'fields': 'city, bdate',
                'age_from': self.UA - 3,
                'age_to': self.UA + 3,
                'hometown': self.UC,
                'sex': int(not(self.US)),
                'v': '5.131',
                'count': 1
            }
        )
        return response.json()

        
    def get_parametrs_to_search(self):
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

    def candidate_photo(self):
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

    def unification_info(self):
        get_params_info = self.candidate_parametrs().get('response')['items'][0]
        get_params_info.update(self.candidate_photo())
        return get_params_info

print(Candidate_Selection(18, bool(0), 'Севастополь').unification_info())