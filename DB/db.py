from sqlalchemy.orm import sessionmaker
from DB.Tables import create_tables, engine, Blacklist, Favorite, User, Viewed
from datetime import date, datetime

Session = sessionmaker(bind=engine)
session = Session()
create_tables(engine)


def calculate_age(bdate):
    '''Функция для вычисления возраста по дате рождения из файла json'''
    birth_date = datetime.strptime(bdate, "%d.%m.%Y").date()
    today = date.today()
    age = today.year - birth_date.year - ((today.month,
                                           today.day) < (birth_date.month, birth_date.day))
    return age


def rec_vk_user(data):
    """Функция для записи данных пользователя в БД. Принимает на вход json"""
    if data['id'] not in get_users_id():
        user = User(user_id=data['id'], first_name=data['first_name'], last_name=data['last_name'],
                    age=calculate_age(data['bdate']), gender=data['sex'], city=data['city']['title'])
        session.add(user)
        session.commit()


def get_users_id():
    """Функция, которая возвращает список из ID всех зарегестрированных пользователей"""
    result = []
    for i in session.query(User.user_id):
        for user_id in i:
            result.append(user_id)
    return result


def rec_favorites(data, user_id):
    """Функция для записи данных, добавленных пользователем в избранное. Принимает на вход json и ID пользователя"""
    if str(data['id']) not in get_favorites(user_id):
        favorite = Favorite(favorite_id=data['id'], user_id=user_id)
        session.add(favorite)
        session.commit()


def rec_blocked(data, user_id):
    """Функция для записи данных, добавленных пользователем в Black list. Принимает на вход json и ID пользователя"""
    if str(data['id']) not in get_blocked(user_id):
        block = Blacklist(block_id=data['id'], user_id=user_id)
        session.add(block)
        session.commit()


def rec_viewed(cand_id, user_id):
    """Функция для записи  кандидатов, просмотренных пользователем. Принимает на вход ID кандидата и ID пользователя"""
    view = Viewed(viewed_id=cand_id, user_id=user_id)
    session.add(view)
    session.commit()


def get_viewed(user_id):
    """Функция, которая возвращает  список просмотренных пользователем кандидатов.
    Принимает ID пользователя"""
    result = []
    for i in session.query(Viewed.viewed_id).filter(Viewed.user_id == user_id):
        for viewed_id in i:
            result.append(viewed_id)
    return result


def get_favorites(user_id):
    """Функция, которая возвращает список из ID кандидатов, добаленных данным пользователем в избранное.
    Принимает ID пользователя"""
    result = []
    for i in session.query(Favorite.favorite_id).filter(Favorite.user_id == user_id):
        for user_id in i:
            result.append(user_id)
    return result


def get_blocked(user_id):
    """Функция, которая возвращает список из ID кандидатов, добаленным данным пользователем в Black list
       Принимает ID пользователя."""
    result = []
    for i in session.query(Blacklist.block_id).filter(Blacklist.user_id == user_id):
        for user_id in i:
            result.append(user_id)
    return result


session.commit()
session.close()
