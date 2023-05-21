from datetime import datetime, timedelta
from aiogram import executor
from dispatcher import dp
import asyncio
from dispatcher import bot
import handlers#импрот нужен для работы обработчиков событий

from db import BotDB
BotDB = BotDB('database.db')

async def checkPasswords():
    sites = BotDB.get_all_data()#получаем все записи из таблицы данными
    now = datetime.now()# получаем текущее время
    user_to_update = {}# объект для хранения сайтов, к которым надо будет обновить пароль
    for record in sites:#перебираем все записи
        user_id = BotDB.get_id(record[1])#получаем id пользователя из таблицы users
        dateUpdate = ParseDate(record[5])#получаем последнюю дату обновления/добавления пароля
        dateUpdate = datetime(int(dateUpdate[0]), int(dateUpdate[1]), int(dateUpdate[2]),int(dateUpdate[3]), int(dateUpdate[4]), int(dateUpdate[5]))#ставим последнюю дату обновления в формат для сравнения/складывания
        fourteen_days_later = dateUpdate + timedelta(days=1)#прибавляем к дате обновления 14 дней, что бы сравнивать
        if fourteen_days_later < now:#если 14 дней плюс больше текущей даты
            if(user_id in user_to_update):#если уже в объекте уже есть данные о просроченном пароле
                user_to_update[user_id].update( {"sites":user_to_update[user_id]["sites"] + ", "+ record[3]  })#обновляем данные
            else:#если данных нету, создаем их
                #все будет выглядеть так {Аайди_Юсера{"Сайты":"Тут сайты, к которым необходимо обновить данные к ним прибавляем навые сайты"}}
                user_to_update[user_id] = {"sites":record[3]}
    for user in user_to_update:#ходим по пользователям, к которым необходимо обновить пароль
        MessageSites = user_to_update[user]["sites"]#получаем все сайты в String
        await bot.send_message(user[0], f"Вам необходимо обновить пароля для сайта: {MessageSites}")#отправляем сообщение пользователям у которым есть просрочки
    await asyncio.sleep(10)#асинхронно ничего не делаем(тут ставим время в секундах раз в какое время проверять пароли)
    await checkPasswords()#вызываем себя же

def ParseDate(dateUpdate):#парсим дату в нужным нам формат
    SplitedDate = dateUpdate.split(" ")#разделяем пополам ["Дата","Время"]
    return SplitedDate[0].split("-") + SplitedDate[1].split(":")#["год","месяц","день","часы","минуты","секунды"]

def main():
    # asyncio.ensure_future(checkPasswords())#запускаем проверку паролей
    executor.start_polling(dp, skip_updates=True)#запускаем бота

if __name__ == "__main__":
    main()




