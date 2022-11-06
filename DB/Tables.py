import sqlalchemy as sq
from sqlalchemy.orm import declarative_base, relationship
import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())
DSN = os.getenv('DSN')
engine = sq.create_engine(DSN)

Base = declarative_base()


class User(Base):
    __tablename__ = 'user'

    user_id = sq.Column(sq.Integer, primary_key=True, unique=True, nullable=False)
    first_name = sq.Column(sq.String(length=60), nullable=False)
    last_name = sq.Column(sq.String(length=60), nullable=False)
    age = sq.Column(sq.Integer)
    gender = sq.Column(sq.String(length=15))
    city = sq.Column(sq.String(length=60), nullable=False)


class Favorite(Base):
    __tablename__ = 'favorite'

    favorite_id = sq.Column(sq.Integer, primary_key=True, unique=True)
    user_id = sq.Column(sq.Integer, sq.ForeignKey('user.user_id'), unique=False, nullable=False)
    user = relationship(User, backref='favorite')


class Blacklist(Base):
    __tablename__ = 'black_list'

    block_id = sq.Column(sq.Integer, primary_key=True, unique=True)
    user_id = sq.Column(sq.Integer, sq.ForeignKey('user.user_id'), unique=False, nullable=False)
    user = relationship(User, backref='black_list')


class Viewed(Base):
    __tablename__ = 'viewed'
    id = sq.Column(sq.Integer, primary_key=True, unique=True)
    viewed_id = sq.Column(sq.Integer, nullable=False, unique=False)
    user_id = sq.Column(sq.Integer, sq.ForeignKey('user.user_id'), unique=False, nullable=False)
    user = relationship(User, backref='viewed')


def create_tables(engine):
    """ Функция для создания\удаления всех таблиц в БД"""
    # Base.metadata.drop_all(engine)  # Удаление всех таблиц
    Base.metadata.create_all(engine)  # Создание таблиц

