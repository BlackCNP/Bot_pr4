
import asyncio
import logging
from aiogram import Bot, Dispatcher

from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.default import DefaultBotProperties


from handlers import router


BOT_TOKEN = "7995098009:AAHvvN5T7sIXxaJ1H-HDFfER_ijbVAbRGpY"

async def main():
    
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )
    logging.info("Starting bot...")

    
    storage = MemoryStorage()

    
    default_properties = DefaultBotProperties(
        parse_mode=ParseMode.HTML 
    )
    
    bot = Bot(token=BOT_TOKEN, default=default_properties)
    dp = Dispatcher(storage=storage)

   
    dp.include_router(router)


    await bot.delete_webhook(drop_pending_updates=True)

    
    logging.info("Starting polling...")
    try:
        await dp.start_polling(bot)
    finally:
        
        await bot.session.close()
        logging.info("Bot stopped.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Bot stopped manually.")
    except Exception as e:
        logging.exception("Unhandled exception occurred:")