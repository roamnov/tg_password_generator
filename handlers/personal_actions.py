import random
from aiogram import types
from dispatcher import dp
from dispatcher import bot
from bot import BotDB
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher import FSMContext

from datetime import datetime, timedelta
import asyncio

#Конечные автоматы (FSM) - cистема диалогов
#Стейты нужны для диалоговых сообщений
#например Добавить сайт -> Введите сайт -> Введите логин -> Введите пароли
#В них хранится данные, обновляя которые триггерим след. часть послед. сообщения
class Password(StatesGroup):
    password = State()

class SaveForSite(StatesGroup):
    site = State()
    login = State()
    password = State()

class GetSite(StatesGroup):
    site = State()
    choseNext = State()
    login = State()
    password = State()

Defaultkeyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
buttons = ["Создать пароль", "Сохраненные","Добавить данные"]
Defaultkeyboard.add(*buttons)#Стандартная клавиатура для выбора что делать

def getPass(length):#генерация слчайного пароля, получаем размер пароля
    password =''
    for i in range(int(length)):#ходим в цикле и добавляем по 1 символу
        password += random.choice('+-/*!&$#?=@<>abcdefghijklnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890')
    return password

@dp.message_handler(commands = ("start"))#стартовая команда
async def start(message: types.Message):
    if(not BotDB.user_exists(message.from_user.id)):#проверка есть ли пользователь в БД
        BotDB.add_user(message.from_user.id)#если нету, добавляем
        await message.bot.send_message(message.from_user.id, "Добро пожаловать!", reply_markup=Defaultkeyboard)#отправка сообщения с клавиатурой
    else:#если пользователь есть, просто присылаем клавиатуру
        await message.bot.send_message(message.from_user.id, "Выберите действие, используя клавиатуру", reply_markup=Defaultkeyboard)
        # await checkPasswords()

async def checkPasswords(): #это можно удалить, но если хочется более точно увидеть и проверить проверку
    sites = BotDB.get_all_data()
    now = datetime.now()
    user_to_update = {}
    user_to_update_test = {"123":{"sites":"site1,site2"}, "124":{"sites":"site3,site4"}}
    for record in sites:
        print(record)
        user_id = BotDB.get_id(record[1])
        dateUpdate = ParseDate(record[5])
        dateUpdate = datetime(int(dateUpdate[0]), int(dateUpdate[1]), int(dateUpdate[2]),int(dateUpdate[3]), int(dateUpdate[4]), int(dateUpdate[5]))
        fourteen_days_later = dateUpdate + timedelta(days=1)
        print(fourteen_days_later)
        if fourteen_days_later < now:
            print("Посылаем сообщение", record[3],user_id in user_to_update)
            if(user_id in user_to_update):
                user_to_update[user_id].update( {"sites":user_to_update[user_id]["sites"] + ", "+ record[3]  })
            else:
                user_to_update[user_id] = {"sites":record[3]}
            # user_to_update.append(user_id + "," + [record[2]])
            # await bot.send_message(user_id, f"Вам необходимо обновить пароля для сайта:")
    print(user_to_update_test["123"].update( {"sites":user_to_update_test["123"]["sites"] + record[3] + "," }))
    print(user_to_update_test, user_to_update)
    for user in user_to_update:
        print(user_to_update[user]["sites"])
        # MessageSites =""
        MessageSites = user_to_update[user]["sites"]
        await bot.send_message(user[0], f"Вам необходимо обновить пароля для сайта: {MessageSites}")
    await asyncio.sleep(60)

def ParseDate(dateUpdate):#тоже можно удалить
    SplitedDate = dateUpdate.split(" ")
    return SplitedDate[0].split("-") + SplitedDate[1].split(":")

@dp.message_handler(state='*', commands='cancel')#Кнопка и команда отмены, работает даже в последовательных сообщений
@dp.message_handler(Text(equals='Отмена', ignore_case=True), state='*')#всегда пытаемся проверить не смотря на стейты и т д
async def user_chose_site(message: types.Message, state: FSMContext):
    await state.finish()#завершаем любой стейт
    if(not BotDB.user_exists(message.from_user.id)):#проверка есть ли пользователь в БД
        BotDB.add_user(message.from_user.id)#если нету, добавляем
        await message.bot.send_message(message.from_user.id, "Добро пожаловать!", reply_markup=Defaultkeyboard)#отправка сообщения с клавиатурой
    else:
        await message.bot.send_message(message.from_user.id, "Выберите действие, используя клавиатуру", reply_markup=Defaultkeyboard)#присыалем стандартное сообщение

#########################Получить записи и редактировать###########################
@dp.message_handler(lambda message: message.text == "Сохраненные")#если текст сообщения равен Сохраненные
async def user_chose_site(message: types.Message):#принимаем сообщение от пользователя
    Sites =BotDB.get_sites(message.from_user.id)#получаем сайты, которые сохранял пользователь
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)#созадем клавиатуру
    buttons = []#кнопки в клавиатуру
    if(len(Sites)):#если сайты есть
        for site in Sites:#перебираем все сайты
            buttons.append(site[0])#добавлем кнопки, а текст в них - сайты
        keyboard.add(*buttons)
        keyboard.row("Отмена")#добавляем кнопку отмены в отдельную строку
        await message.answer("Что бы увидеть данные, выберите сайт используя клавиатуру ниже", reply_markup=keyboard)#возвращаем с нашими сайтами
        await GetSite.site.set()#переходим дальше, через сейт в выбору
    else:#если сайтов нет
        await message.answer("У вас нет сохраненных данных!")#присылаем сообщение об отсутсвии данных

@dp.message_handler(state=GetSite.site)#если мы получили сообщение с логином await GetSite.site.set() позволяет перейти именно сюда
async def send_site_data(message: types.Message, state: FSMContext):#также передаем стейт, что бы обновлять значения в нем
    Sites =BotDB.get_sites(message.from_user.id)#получаем сайты
    SitesArr = []
    for data in Sites:
        SitesArr.append(data[0])#добавляем сайты в массив
    if message.text not in SitesArr:#если сайт написанный пользователем не был в клавиатуре
        await message.answer("Пожалуйста, выберите сайт, используя клавиатуру ниже ")
        return
    await state.update_data(site=message.text)#обновляем стейт
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = ["Удалить", "Изменить"]
    keyboard.add(*buttons)
    keyboard.row("Отмена")
    SitesAndData =BotDB.get_dataSite(message.from_user.id, message.text)#получаем все сохраненные данные пользователя
    result = ""
    for data in SitesAndData:#перебор одного значения
        result+= f"Сайт: {data[3]}\n"
        result+= f"Логин: `{data[4]}`\n"# если есть `эти кавычки`, и прас мод маркдавн, то на текст можно кликнуть и скопировать
        result+= f"Пароль: `{data[2]}`\n"
    await message.answer(result + "\n" +"Выберите, что сделать с данными", reply_markup=keyboard, parse_mode="MARKDOWN")#присылаем с парс модом MARKDOWN, что бы работал клик на логин или пароль для копирования
    await GetSite.choseNext.set()#к след стейту

@dp.message_handler(state=GetSite.choseNext)
async def user_login_change(message: types.Message, state: FSMContext):
    if message.text.lower() not in ["удалить", "изменить"]:#если мы выбрали не эти кнопки присылаем сообщение с этими же кнопками
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        buttons = ["Удалить", "Изменить"]
        keyboard.add(*buttons)
        await message.answer("Пожалуйста, выберите действие, используя клавиатуру ниже", reply_markup=keyboard)
        return
    if(message.text.lower() == "удалить"):#если удалить
        data = await state.get_data()#получаем данные, которые записывали стейт
        BotDB.delete_site(message.from_user.id, data["site"])#запрос к бд на удаление данных
        await message.answer("Данные успешнно удалены", reply_markup=Defaultkeyboard)
        await state.finish()#завершаем стейт
    else:
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.row("Отмена")
        await state.update_data(id=message.text)#
        await message.answer("Введите логин", reply_markup=keyboard)
        await GetSite.login.set()#переходим к выбору логина

@dp.message_handler(state=GetSite.login)#если начали ставить логин и пользователь прислал сообщение, после выбора логина
async def get_password_generate(message: types.Message, state: FSMContext):
    await state.update_data(login=message.text)
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = ["Сгенерировать"]
    keyboard.add(*buttons)
    keyboard.row("Отмена")
    await message.answer("Введите пароль или нажмите кнопку \"Сгенерировать\"", reply_markup=keyboard)
    await GetSite.password.set()#ставим пароль

@dp.message_handler(state=GetSite.password)
async def add_password(message: types.Message, state: FSMContext):
    if(message.text == "Сгенерировать"):#если нажали кннопку сгенерировать
        password = getPass(12)#создаем пароль из 12 символом
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        buttons = ["Сохранить", "Сгенерировать"]
        keyboard.add(*buttons)
        keyboard.row("Отмена")
        await state.update_data(password=password)#обновляем пароль, если пользователь согласиться его сохранить, мы достанет его отсюда
        await message.answer("Сохранить сгенерированный пароль: " +password +"?", reply_markup=keyboard)#присылаем сообщение с паролем
        return#возвращаемся к установке стейту пароля
    elif(message.text != "Сохранить" and message.text != "Сгенерировать"):#если мы ввели пароль сами
        password = message.text
        await state.update_data(password=password)
    data = await state.get_data()#получем данные
    SiteData = BotDB.get_dataSite(message.from_user.id, data['site'])#получаем айди записи в БД которую необходимо обновить
    BotDB.update_site(SiteData[0][0], data['login'], data['password'])#обновляем
    await message.answer("Данные успешно изменены!", reply_markup=Defaultkeyboard)
    await state.finish()#завершаем

#########################Генерация пароля###########################
@dp.message_handler(lambda message: message.text == "Создать пароль")#
async def user_generate_password(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = ["С сохранением", "Без сохранения"]
    keyboard.add(*buttons)
    keyboard.row("Отмена")
    await message.answer("С сохранением или без?", reply_markup=keyboard)

@dp.message_handler(lambda message: message.text == "Без сохранения")#если без сохранения
async def user_generate_password(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row("Отмена")
    await message.answer("Введите размер пароля", reply_markup=keyboard)
    await Password.password.set()#ставим стейт на генерацию паролей


@dp.message_handler(state=Password.password)#получаем стейт для обновления пароль
async def get_password_generate(message: types.Message, state: FSMContext):
    await state.update_data(password=message.text)
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row("Отмена")
    await message.answer(f"`{getPass(message.text)}`" + "\n" "Moжете дальше генерировать пароли, присылая число, либо воспользуйтесь клавиатурой ниже", reply_markup=keyboard, parse_mode="MARKDOWN")
    await state.finish()
    await Password.password.set()

#########################Добавление нового сайта и С сохранением#########################
@dp.message_handler(lambda message: message.text == "Добавить данные" or "С сохранением")
async def add(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row("Отмена")
    await message.answer("Введите адрес сайта.", reply_markup=keyboard)
    await SaveForSite.site.set()


@dp.message_handler(state=SaveForSite.site)
async def add_site(message: types.Message, state: FSMContext):
    Sites =BotDB.get_sites(message.from_user.id)#получаем сайты пользователя
    for site in Sites:#перебираем сайты
        if(site[0] == message.text):#если сайт существует, присылаем сообщения и ждем когда пользователь напишем сайт которого нет в базе
            await message.answer("Такой сайт уже существует, введите другой")
            return
    if(len(message.text) >= 130):#проверка длины сайта, не больше 130 символов
        await message.answer("Слишком большая длина сайта, введите снова(меньше 130 символов)")
        return
    await state.update_data(site=message.text)
    await message.answer("Введите логин.")
    await SaveForSite.next()

@dp.message_handler(state=SaveForSite.login)
async def add_login(message: types.Message, state: FSMContext):
    await state.update_data(username=message.text)
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = ["Сгенерировать"]
    keyboard.add(*buttons)
    keyboard.row("Отмена")
    await message.answer("Введите пароль или нажмите кнопку \"Сгенерировать\"", reply_markup=keyboard)
    await SaveForSite.password.set()

@dp.message_handler(state=SaveForSite.password)
async def add_password(message: types.Message, state: FSMContext):
    if(message.text == "Сгенерировать"):#см строку 159
        password = getPass(12)
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        buttons = ["Сохранить", "Сгенерировать"]
        keyboard.add(*buttons)
        keyboard.row("Отмена")
        await state.update_data(password=password)
        await message.answer("Сохранить сгенерированный пароль: " +password +" ?", reply_markup=keyboard)
        return
    elif(message.text != "Сохранить" and message.text != "Сгенерировать"):
        password = message.text
        await state.update_data(password=password)
    data = await state.get_data()#получаем введеные пользователем данные
    BotDB.add_site(message.from_user.id, data['site'], data['username'], data['password'])#добавляем сайт
    await message.answer("Данные успешно добавлены!", reply_markup=Defaultkeyboard)
    await state.finish()
