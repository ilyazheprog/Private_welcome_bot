from aiogram.utils import executor

from src import *

if __name__ == '__main__':
    from src.handlers import dp
    executor.start_polling(dp, skip_updates=True)