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
# 2 - изменение учета товаров, получение отчета
# 3 - изменение учета товаров, получение отчета, изменение складов
cur.execute("""CREATE TABLE IF NOT EXISTS storage(
            id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            name TEXT, 
            address TEXT,
            сapacity INT,
            сapacity2 INT)""")
cur.execute("""CREATE TABLE IF NOT EXISTS type_product(
            name TEXT PRIMARY KEY);""")
cur.execute("""CREATE TABLE IF NOT EXISTS products(
            id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            type TEXT, 
            count INT,
            storage TEXT,
            FOREIGN KEY (type) REFERENCES type_product(name),
            FOREIGN KEY (storage) REFERENCES storage(name));""")
first_code = jwt.encode({'code':"1234"}, SECRET_KEY, algorithm='HS256')
# cur.execute("""INSERT INTO users (login, cod, promis) VALUES (?,?,?)""",
#             ("director", first_code, 0, ))
# cur.execute("""ITCLRNSERT INTO users (login, cod, promis) VALUES (?,?,?)""",
#             ("test", first_code, 3, ))
conn.commit()
cur.execute("SELECT * FROM users;")
print(cur.fetchall(), 'users')
cur.execute("SELECT * FROM products;")
print(cur.fetchall(), 'products')
cur.execute("SELECT * FROM type_product;")
print(cur.fetchall(), 'type_product')
cur.execute("SELECT * FROM storage;")
print(cur.fetchall(), 'storage')
conn.close()
