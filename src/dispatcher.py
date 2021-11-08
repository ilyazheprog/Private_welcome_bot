from aiogram import Bot, Dispatcher, types
from environs import Env


env = Env()
env.read_env()

bot = Bot(token=env.str("TOKEN"), parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot)
