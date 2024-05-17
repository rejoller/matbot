from aiogram import Bot, Dispatcher, types
import html
from aiogram.fsm.storage.redis import RedisStorage
from config import bot_token, redis_url
import asyncio
import logging


storage = RedisStorage.from_url(redis_url)
#storage = BaseStorage
bot = Bot(bot_token)





async def main():
    
    dp = Dispatcher(storage = storage)
    from handlers import main_router
    dp.include_router(main_router)
    from handlers import initialize_users
    await initialize_users()
   # await on_startup()
    print('Бот запущен и готов к приему сообщений')


  
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types(), parse_mode=html)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    asyncio.run(main())