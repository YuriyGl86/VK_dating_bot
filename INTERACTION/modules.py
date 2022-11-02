import json
import requests
class Interaction():
    
    # def __init__(
    #     self,
    #     user_access_token,
    #     user_id,
    #     user_name,
    #     user_surname,
    #     user_link,
    #     user_age,
    #     user_sex,
    #     user_city,
    #     version = '5.131',
    #     album = 'profile',
    #     extendet = False,
    #     rev = True,
    #     count = 3
    #     ):
    #     self.UAT = user_access_token
    #     self.UID = user_id
    #     self.UN = user_name
    #     self.USN = user_surname
    #     self.UL = user_link
    #     self.UA = user_age
    #     self.US = user_sex
    #     self.UC = user_city
    #     self.V = version
    #     self.A = album
    #     self.EX = extendet
    #     self.R = rev
    #     self.CNT = count
        
    def get_params():
    # функция, которая берёт json со страницы
        url = 'https://api.vk.com/method/photos.get'
        # вызываем и вводим параметры вызова
        response = requests.get(
            url,
            params = {
            'access_token': 'vk1.a.xV9SUyov3GT2KqLJny5H1LEaJ1fkmWY5w29S1sfEzXsJ8wbjy1rUX4IPBgsj_QGfJ24tu-F62FB-qDpzm8kGNRcd2YRaX5S5n2I7zUW0B6PljetGcH7hTnCl14aLd8YWCR4-KUlIuBdiMePiWWtKD_xsS88Xm1ZBvPveM-uFuisOJksyZq1Ra6bQdc1GMrlr8-_aQ0zcjSLv44x1AdRLeg',#self.UAT,
            'owner_id': '31723805',
            'v': '5.131',#self.V,
            'album_id': 'profile',#self.A,
            'extended': True,#self.EX,
            'rev': False,#self.R,
            # 'count': 77#self.CNT
            })
        return response.json()

    def candidate_photo():
        # метод выборки фотографий с наибольшей популярностью
        list_likes = []
        list_info = []
        url_list = []
        best_photo = []
        for item in Interaction.get_params().values():
            for inside_params in item['items']:
                list_likes.append(inside_params['likes'].get('count'))
                list_info.append(inside_params['sizes'])
                # вот на этом моменте выделяется фотография со всеми размерами и ссылками по наибольшему количеству лайков
                # в дальнейшем нет нужны фильтровать размеры фотографий, так как через return возвращаем автоматически
                # наибольшее значение (главное расположить строку "url_list.append(url)" в нужном столбце)
                info_photo_likes = sorted(dict(zip(list_likes, list_info)).items(), reverse=True)[:3]
            for items in info_photo_likes:
                for i in items[1]:
                    best_photo.append(i)
                    url = i['url']
                url_list.append(url)
        return {'photo': url_list}
    
    def candidat_info():
        url = 'https://api.vk.com/method/users.get'
        response = requests.get(
            url,
            params = {
                'access_token': 'vk1.a.xV9SUyov3GT2KqLJny5H1LEaJ1fkmWY5w29S1sfEzXsJ8wbjy1rUX4IPBgsj_QGfJ24tu-F62FB-qDpzm8kGNRcd2YRaX5S5n2I7zUW0B6PljetGcH7hTnCl14aLd8YWCR4-KUlIuBdiMePiWWtKD_xsS88Xm1ZBvPveM-uFuisOJksyZq1Ra6bQdc1GMrlr8-_aQ0zcjSLv44x1AdRLeg',
                'user_ids': '31723805',
                'fields': ['bdate', 'sex', 'city'],
                'v': '5.131'
            })
        return response.json().get('response')

def func():
    for i in Interaction.candidat_info():
        i.update(Interaction.candidate_photo())
        return json.dumps(i)
    
print(func())
    

    