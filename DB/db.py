from sqlalchemy.orm import sessionmaker
from Tables import create_tables, engine, Photo, Black_list, Favorite, User
from datetime import date, datetime


data = {'id': 82185, 'bdate': '29.3.1986', 'city': {'id': 2, 'title': 'Санкт-Петербург'},
        'sex': 2, 'first_name': 'Юрий', 'last_name': 'Глущенко', 'can_access_closed': True, 'is_closed': False}

Session = sessionmaker(bind=engine)
session = Session()
# create_tables(engine)


def calculate_age(bdate): # Функция для вычисления возраста по дате рождения из файла json
    birth_date = datetime.strptime(bdate,"%d.%m.%Y").date()
    today = date.today()
    age = today.year - birth_date.year - ((today.month,
    today.day) < (birth_date.month, birth_date.day))
    return age

def rec_vk_user(data): # Функция для записи данных пользователя в БД
    user = User(user_id=data['id'] , first_name=data['first_name'], last_name=data['last_name'],
                age=calculate_age(data['bdate']), gender=data['sex'], city=data['city']['title'])
    session.add(user)
    session.commit()

def get_users_id(): # Функция, которая возвращает итеррируемый объект с ID всех зарегестрированных пользователей
    subq = session.query(User).all()
    return subq

def rec_favorites(user_id): # Функция для записи данных, добавленных пользователем в избранное

def rec_blocked(user_id): # Функция для записи данных, добавленных пользователем в Black list

def rec_foto(data): # Функция для записи фото профилей, добавленных пользователем в избранное

def get_favorites(user_id): # Функция, которая возвращает итеррируемый объект с ID профилей и их фото,
                            # добаленным данным пользователем в избранное

def get_blocked(user_id):  # Функция, которая возвращает итеррируемый объект с ID профилей,
                           # добаленным данным пользователем в избранное

session.commit()
session.close()