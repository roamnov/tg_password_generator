import sqlite3
from datetime import datetime

class BotDB:

    def __init__(self, db_file):
        self.conn = sqlite3.connect(db_file)
        self.cursor = self.conn.cursor()

    def user_exists(self, user_id):
        """Проверяем, есть ли юзер в базе"""
        result = self.cursor.execute("SELECT `id` FROM `users` WHERE `user_id` = ?", (user_id,))
        return bool(len(result.fetchall()))

    def get_id(self, id):
        """Достаем user_id юзера в базе по его id"""
        result = self.cursor.execute("SELECT `user_id` FROM `users` WHERE `id` = ?", (id,))
        return result.fetchone()

    def get_user_id(self, user_id):
        """Достаем id юзера в базе по его user_id"""
        result = self.cursor.execute("SELECT `id` FROM `users` WHERE `user_id` = ?", (user_id,))
        return result.fetchone()[0]

    def add_user(self, user_id):
        """Добавляем юзера в базу"""
        self.cursor.execute("INSERT INTO `users` (`user_id`) VALUES (?)", (user_id,))
        return self.conn.commit()

    def add_site(self, user_id, site, login,password):
        """Создаем запись о сайте с его данными"""
        self.cursor.execute("INSERT INTO `sites` (`user_id`, `site`, `login`, `password`) VALUES (?, ?, ?, ?)",  (self.get_user_id(user_id), site, login, password))
        return self.conn.commit()

    def delete_site(self, user_id, site):
        """Удаление записи о сайте"""
        self.cursor.execute("DELETE FROM `sites` WHERE `user_id` = ? AND `site` = ?",  (self.get_user_id(user_id), site,))
        return self.conn.commit()

    def get_data(self, user_id, within = "all"):
        """Получаем все данные, которые сохранял пользователь"""
        result = self.cursor.execute("SELECT * FROM `sites` WHERE `user_id` = ?",
                (self.get_user_id(user_id),))
        return result.fetchall()

    def get_all_data(self, within = "all"):
        """Получаем все данные(для проверки паролей)"""
        result = self.cursor.execute("SELECT * FROM `sites`")
        return result.fetchall()

    def get_sites(self, user_id, within = "all"):
        """Получаем список сайтов у пользователя"""
        result = self.cursor.execute("SELECT `site` FROM `sites` WHERE `user_id` = ?",
                (self.get_user_id(user_id),))
        return result.fetchall()

    def get_dataSite(self, user_id, site, within = "all"):
        """Получаем все данные по сайта у пользователя"""
        result = self.cursor.execute("SELECT * FROM `sites` WHERE `user_id` = ? AND `site` = ?",
                (self.get_user_id(user_id),site,))
        return result.fetchall()

    def update_site(self, id, login, password):
        """Обновляем данные сайта"""
        now = datetime.now()
        nowDate = now.strftime("%Y-%m-%d %H:%M:%S")#Создаем в нужном нам формате дату и время обновления
        self.cursor.execute("UPDATE `sites` SET login = ?, password = ?, updated_date = ?  WHERE id = ?",  (login, password,nowDate,id))
        return self.conn.commit()


    def close(self):
        """Закрываем соединение с БД"""
        self.connection.close()