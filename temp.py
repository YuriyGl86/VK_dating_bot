



class Candidate_selection():
    """
    Класс предоставляет получение информации о пользователях и их фотографиях. Сначала пишем несколько вспомогательных
    методов, потом в одном главном методе всё объединяем и выдаем результат.
    """


    def get_candidates_list(self, user_json):
        """
        метод, который принимает параметры для поиска и возвращает выборку из кандидатов через метод users.search с
        праметрами для поиска age_from, age_to, has_photo, sex, city и count=50 или больше. В дополнительном задании
        вообще сказано подумать как обойти ограничение в 1000. Т.е. выборка может быть большой.
        Возвращает СПИСОК из кандидатов (видимо список из словарей)
        """
        # user_age = self.get_user_age_by_bdate(user_json)
        # user_city = user_json['city']['title']
        # user_sex = user_json['sex']
        # ...
        # return candidate_list
        pass

    def get_photos_by_candidate_id(self, candidate_id):
        """
        метод, который принимает id ОДНОГО кандидата и через метод photos.get запрашивает все его фотографии.
        Метода возвращает список всех фотографий.
        """
        pass

    def filter_best_candidate_photos(self, photos_list):
        """
        Метод, который принимает на вход список фотографий и возвращает только 3 из них с наибольшим числом лайков
        """
        pass

    @staticmethod
    def get_user_age_by_bdate(self, user_json):
        """
        Метод для вычисления возраста пользователя по его дате рождения. Но можно не прописывать новую функцию, я точно
        помню, Артем уже написал такую он говорил, и можно просто импортировать его функцию, чтобы не дублировать код.
        Но можно и свою написать, если хочется. Берется из user_json ключ 'bdate' и вычисляется возраст.
        """
        pass

    def get_candidate_for_user(self, user_json):
        """ Главный метод по подбору кандидата. Именно этот метод и будет вызывать бот, когда ему надо будет получить
        кандидата. Этот метод на вход получает словарь user_json c данными пользователя, обрабатывает его, используя
        написанные ранее вспомогательные методы и возвращает обратно в то место откуда вызван словарь с кандидатом.
        """
        candidate_list = self.get_candidates_list(user_json)
        black_list = get_black_list_for_user(user_json)  # вызываешь функцию получения ЧС, которую напишет Артем
        favorites = ... # вызываешь функцию получения избранного, которую напишет Артем
        ignore_id_list = black_list + favorites  # получаешь общий список для игнора
        for candidate in candidate_list:
            if candidate['id'] not in ignore_id_list:
                candodate_photos = self.get_photos_by_candidate_id(candidate)
                best_candidate_photos = self.filter_best_candidate_photos(candodate_photos)
                # дальше соединяешь данные словаря candidate с фотографиями и возвращаешь результат
                return candidate
