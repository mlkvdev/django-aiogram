import asyncio

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import Update
from django.conf import settings
from loguru import logger

from .helpers import get_bot_webhook_url
from .routers import router
from .utils.storage import DjangoRedisStorage

bot = Bot(
    token=settings.BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)


async def on_startup():
    if settings.DEBUG is False:
        webhook_info = await bot.get_webhook_info()
        if webhook_info.url != get_bot_webhook_url():
            await bot.set_webhook(
                get_bot_webhook_url(), secret_token=settings.BOT_WEBHOOK_SECRET
            )
    else:
        run_polling()


async def on_shutdown():
    await bot.session.close()
    logger.info("Bot shut down")


def init_dispatcher():
    dp = Dispatcher(storage=DjangoRedisStorage())
    dp.include_router(router)
    return dp


aiogram_dispatcher = init_dispatcher()


async def feed_update(update: Update):
    await aiogram_dispatcher.feed_update(bot, update)


async def feed_raw_update(update: dict):
    await aiogram_dispatcher.feed_raw_update(bot, update)


def run_polling():
    asyncio.create_task(aiogram_dispatcher.start_polling(bot, handle_signals=False))
