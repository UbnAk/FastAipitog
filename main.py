# Задание №2
# Создать веб-приложение на FastAPI, которое будет предоставлять API для
# работы с базой данных пользователей. Пользователь должен иметь
# следующие поля:
# ○ ID (автоматически генерируется при создании пользователя)
# ○ Имя (строка, не менее 2 символов)
# ○ Фамилия (строка, не менее 2 символов)
# ○ Email (строка, валидный email)
# ○ Адрес (строка, не менее 5 символов)
# Погружение в Python
# Задание №2 (продолжение)
# API должен поддерживать следующие операции:
# ○ Добавление пользователя в базу данных
# ○ Получение списка всех пользователей в базе данных
# ○ Получение пользователя по ID
# ○ Обновление пользователя по ID
# ○ Удаление пользователя по ID
# Приложение должно использовать базу данных SQLite3 для хранения
# пользователей.

from datetime import date
import databases
import sqlalchemy
from fastapi import FastAPI
from pydantic import BaseModel, Field, EmailStr, SecretStr
from typing import List
from datetime import date

DATABASE_URL = "sqlite:///mydatabase.db"

database = databases.Database(DATABASE_URL)

metadata = sqlalchemy.MetaData()

users = sqlalchemy.Table(
    "users",
    metadata, # для связи таблиц с базы данных
    sqlalchemy.Column("user_id", sqlalchemy.Integer,
    primary_key=True, autoincrement=True),
    sqlalchemy.Column("first_name", sqlalchemy.String(32)),
    sqlalchemy.Column("last_name", sqlalchemy.String(50)),
    sqlalchemy.Column("email", sqlalchemy.String(50)),
    sqlalchemy.Column("address", sqlalchemy.String(100)),
)

engine = sqlalchemy.create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)
metadata.create_all(engine)
# # Формируем таблице в базе данных



app = FastAPI()

@app.on_event("startup")
async def startup():
    await database.connect()
    #Асихронно подлючись в базе данных

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()
    #Асихронно отключись
    
class User(BaseModel):
    first_name: str = Field(..., min_length=2)
    last_name: str = Field(..., min_length=2)
    email: EmailStr
    address: str = Field(..., min_length=5)


class UserInDB(User):
    user_id: int


@app.get('/users/', response_model=List[User])
async def read_users():
    query = users.select()
    return await database.fetch_all(query)


@app.get('/users/{user_id}', response_model= User)
async def read_user(user_id:int):
    query = users.select().where(users.c.user_id == user_id)
    return await database.fetch_one(query)


@app.post("/users/", response_model=UserInDB)
async def create_user(user: User):
    query = users.insert().values(first_name=user.first_name,
    last_name=user.last_name, email=user.email, address=user.address)
    # query = users.insert().values(**user.model_dump())
    last_record_id = await database.execute(query)
    
    return {**user.model_dump(), "user_id": last_record_id}


@app.put("/users/{user_id}", response_model=User)
async def update_user(user_id: int, new_user: UserInDB):
    query = users.update().where(users.c.user_id ==
    user_id).values(**new_user.dict())
    await database.execute(query)
    return {**new_user.dict(), "id": user_id}


@app.delete("/users/{user_id}")
async def delete_user(user_id: int):
    query = users.delete().where(users.c.user_id == user_id)
    await database.execute(query)
    return {'message': 'User deleted'}

# @app.get("/fake_users/{count}")
# async def temp_user(count: int):
    
#     for i in range(count):
        
#         query = users.insert().values(first_name=f'name{i}',
#                 last_name =f'last_name{i}',
#                 email=f'user_{i}@mail.ru',
#                 address=f'Краснопролетарская д.{i} кв. {i}')
#         #Создаем пользователя
#         await database.execute(query)
#         # добавляем
#     return {'message': f'{count} fake users create'}