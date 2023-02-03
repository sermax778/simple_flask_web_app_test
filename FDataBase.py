import sqlite3
import math
import time

class FDataBase:
    def __init__(self, db):
        self.__db = db
        self.__cur = db.cursor()

    def getList(self):
        sql = '''SELECT * FROM items ORDER BY time DESC'''
        try:
            self.__cur.execute(sql)
            res = self.__cur.fetchall()
            if res:
                return res
        except:
            print("Read error")
        return []

    def addItem(self, title, price, description, image_url):
        try:
            tm = math.floor(time.time())
            self.__cur.execute("INSERT INTO items VALUES (NULL, ?, ?, ?, NULL, 1, ?)", (title, price, description, tm))
            self.__cur.execute(f"SELECT id FROM items WHERE title LIKE '{title}' AND time == {tm}")
            that_item = self.__cur.fetchone()
            print('that item ', that_item[0])
            self.__cur.execute(f"UPDATE items SET image_url = '{image_url[0]+str(that_item[0])+'.'+image_url[1]}' WHERE id = {that_item[0]};")
            self.__db.commit()
        except sqlite3.Error as e:
            print('DB add error1' + str(e))
            return False
        return True

    def getItem(self, itemID):
        try:
            self.__cur.execute(f"SELECT title, price, description, image_url, isActive FROM items WHERE id = {itemID} LIMIT 1")
            res = self.__cur.fetchone()
            if res:
                return res
        except sqlite3.Error as e:
            print('DB add error2' + str(e))

        return (False, False)

    def getImage(self):
        try:
            self.__cur.execute(f"SELECT image_url FROM items ORDER BY time DESC LIMIT 1")
            res = self.__cur.fetchone()
            if res:
                return res
        except sqlite3.Error as e:
            print('DB add error3' + str(e))

        return (False, False)

    def getRecentItems(self):
        try:
            self.__cur.execute("SELECT * FROM items ORDER BY time DESC LIMIT 6")
            res = self.__cur.fetchall()
            if res:
                return res
        except sqlite3.Error as e:
            print('DB read error4' + str(e))

        return []


    def addUser(self, login, email, password):
        try:
            self.__cur.execute(f"SELECT COUNT() as `count` FROM users WHERE email LIKE '{email}' OR login LIKE '{login}'")
            res = self.__cur.fetchone()
            if res['count'] > 0:
                print('Email or login already in use')
                return False

            tm = math.floor(time.time())
            self.__cur.execute("INSERT INTO users VALUES (NULL, ?, ?, ?, ?)", (login, email, password, tm))
            self.__db.commit()
        except sqlite3.Error as e:
            print('DB add error5' + str(e))
            return False

        return True


    def getUser(self, user_id):
        try:
            self.__cur.execute(f"SELECT id FROM users WHERE id = {user_id} LIMIT 1")
            res = self.__cur.fetchone()
            if not res:
                print('User unknown')
                return False
            return res

        except sqlite3.Error as e:
            print('DB add error6' + str(e))

        return False


    def getUserByLogin(self, login):
        try:
            self.__cur.execute(f"SELECT * FROM users WHERE login LIKE '{login}' LIMIT 1")
            res = self.__cur.fetchone()
            if not res:
                print('User unknown')
                return False
            return res

        except sqlite3.Error as e:
            print('DB add error7' + str(e))

        return False
