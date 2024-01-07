import datetime
import random

from sqlalchemy.orm import backref
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, ForeignKey
from sqlalchemy import BIGINT, TIMESTAMP, VARCHAR, FLOAT


Base = declarative_base()


def generate_password(password_length: int = 12):
    letters = 'abcdefghigklmnopqrstuvwxyz'
    caps_letters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    numbers = '0123456789'
    letters_choice = random.sample(population=letters, k=random.randint(20, 25))
    letters_caps_choice = random.sample(population=caps_letters, k=random.randint(20, 25))
    numbers_choice = random.sample(population=numbers, k=random.randint(5, 8))

    password_choice = letters_choice + numbers_choice + letters_caps_choice
    password_random_choice = list(random.sample(population=password_choice, k=password_length))
    random.shuffle(password_random_choice)
    password = ''.join(password_random_choice)
    return password


class User(Base):
    __tablename__ = 'users'
    
    # Telegram user id
    user_id = Column(BIGINT, primary_key=True, autoincrement=False)
    password = Column(VARCHAR(24), nullable=False, default=generate_password())
    
    # Autofilled fields
    registration_date = Column(TIMESTAMP, default=datetime.datetime.now())
    last_update_date = Column(TIMESTAMP, onupdate=datetime.datetime.now(), default=datetime.datetime.now())

    def __repr__(self) -> str:
        return f'<User: {self.user_id}>'
    
    def get_id(self) -> int:
        return self.user_id


class Expense(Base):
    __tablename__ = 'expenses'
    __table_args__ = {'schema': 'user-specific'}
    
    id = Column(BIGINT, primary_key=True, autoincrement=True, nullable=False, unique=True)
    user_id = Column(BIGINT, ForeignKey(User.user_id, ondelete='CASCADE'), nullable=False, unique=False)
    
    category = Column(VARCHAR(55), nullable=False)
    subcategory = Column(VARCHAR(55), nullable=False)
    money_count = Column(FLOAT, nullable=False, autoincrement=False)
    datetime_stamp = Column(TIMESTAMP, nullable=False)
    
    date_added = Column(TIMESTAMP, default=datetime.datetime.now())

    def __repr__(self) -> str:
        return f'<Expense: {self.id} by {self.user_id}>'


class Revenue(Base):
    __tablename__ = 'revenues'
    __table_args__ = {'schema': 'user-specific'}
    
    id = Column(BIGINT, primary_key=True, nullable=False, autoincrement=True, unique=True)
    user_id = Column(BIGINT, ForeignKey(User.user_id, ondelete='CASCADE'), unique=False, nullable=False)

    category = Column(VARCHAR(55), nullable=False)
    type_ = Column(VARCHAR(55), nullable=False)
    money_count = Column(FLOAT, nullable=False, autoincrement=False)
    datetime_stamp = Column(TIMESTAMP, nullable=False)
    
    date_added = Column(TIMESTAMP, default=datetime.datetime.now())
    
    def __repr__(self) -> str:
        return f'<Revenue: {self.id} by {self.user_id}>'