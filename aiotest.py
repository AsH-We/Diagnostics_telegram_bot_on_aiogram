import asyncio
from aiogram import Bot, Dispatcher

import diagnostics_process


botToken = "6668396591:AAFm4eJg-UBSVyMjp_KMK_esNtgvc8Rhntg"

bot = Bot(token=botToken)

dp = Dispatcher()

async def main():
    diagnostics_process.set_bot(bot)

    dp.include_routers(diagnostics_process.router)

    await bot.delete_webhook(drop_pending_updates=True)
    print('Bot started')
    await dp.start_polling(bot)


asyncio.run(main())