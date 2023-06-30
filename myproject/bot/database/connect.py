from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Создаем подключение к базе данных
engine = create_engine('sqlite:///users.db')
Base = declarative_base(bind=engine)
Session = sessionmaker(bind=engine)
session = Session()