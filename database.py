import sqlite3
import jwt
from constant import *
import os

conn = sqlite3.connect(os.path.join("database/data.db"))
cur = conn.cursor()

cur.execute("""CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            login TEXT,
            cod TEXT, 
            promis INT);""")
# Разрешния пишуться цифрами для простоты использования. Ниже представлен код разрешения и их возможности:
# 0 - полные права
# 1 - создание новых учетных записей
# 2 - добовление нового типа товаров, измениние учета товаров, получение отчета
# 3 - измениние учета товаров, получение отчета, изменине складов
cur.execute("""CREATE TABLE IF NOT EXISTS storage(
            id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            name TEXT, 
            address TEXT,
            сapacity INT)""")
cur.execute("""CREATE TABLE IF NOT EXISTS products(
            id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            type TEXT, 
            count INT,
            img TEXT,
            storage_id INT, 
            FOREIGN KEY (storage_id) REFERENCES storage(id));""")
first_code = jwt.encode({'code':"1234"}, SECRET_KEY, algorithm='HS256')
# cur.execute("""INSERT INTO users (login, cod, promis) VALUES (?,?,?)""",
#             ("director", first_code, 0, ))
# cur.execute("""INSERT INTO users (login, cod, promis) VALUES (?,?,?)""",
#             ("test", first_code, 1, ))
conn.commit()
cur.execute("SELECT * FROM users;")
print(cur.fetchall(), 'users')
cur.execute("SELECT * FROM products;")
print(cur.fetchall(), 'products')
conn.close()


