import logging
from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from filters import IsOwnerFilter, IsAdminFilter, MemberCanRestrictFilter
import config

# Обычная конфигурация логина
logging.basicConfig(level=logging.INFO)

# Проверка на токен
if not config.BOT_TOKEN:
    exit("Введите токен")

# Инициализация бота
bot = Bot(token=config.BOT_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())
# aАктивация фильтров
dp.filters_factory.bind(IsOwnerFilter)
dp.filters_factory.bind(IsAdminFilter)
dp.filters_factory.bind(MemberCanRestrictFilter)