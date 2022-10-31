import sqlalchemy as sq
from sqlalchemy.orm import declarative_base, relationship
import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())
DSN = os.getenv('DSN')
# DSN = 'postgresql://postgres:K.,bvfz777@localhost:5432/VKinder'
engine = sq.create_engine(DSN)

Base = declarative_base()


class User(Base):
    __tablename__ = 'user'

    user_id = sq.Column(sq.String(length=60), primary_key=True, unique=True)
    first_name = sq.Column(sq.String(length=60), nullable=False)
    last_name = sq.Column(sq.String(length=60), nullable=False)
    age = sq.Column(sq.Integer)
    gender = sq.Column(sq.String(length=15))
    city = sq.Column(sq.String(length=60), nullable=False)


class Favorite(Base):
    __tablename__ = 'favorite'

    favorite_id = sq.Column(sq.String, primary_key=True, unique=True)
    user_id = sq.Column(sq.String(length=60), sq.ForeignKey('user.user_id'), unique=True, nullable=False)
    user = relationship(User, backref='favorite')


class Black_list(Base):
    __tablename__ = 'black_list'

    block_user_id = sq.Column(sq.String(length=40), primary_key=True, unique=True)
    user_id = sq.Column(sq.String(length=60), sq.ForeignKey('user.user_id'), unique=True, nullable=False)
    user = relationship(User, backref='black_list')


class Photo(Base):
    __tablename__ = 'pop_photo'

    link = sq.Column(sq.String(length=200), primary_key=True, unique=True)
    favorite_id = sq.Column(sq.String, sq.ForeignKey('favorite.favorite_id'), unique=True, nullable=False)
    favorite = relationship(Favorite, backref='pop_photo')


def create_tables(engine):
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)

