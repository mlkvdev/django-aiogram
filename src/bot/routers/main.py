from aiogram import Router, types
from aiogram.filters.command import CommandStart, Command

router = Router()


@router.message(CommandStart())
async def on_start_command(message: types.Message):
    await message.reply('Hello, World!')


@router.message(Command('help'))
async def on_help_command(message: types.Message):
    await message.reply('Help!')
