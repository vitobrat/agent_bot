"""
This is a method with a handler for all user commands

When user write command as /command_name, then this module handle all this messages.
Also, this module handle clicks to buttons by CallbackQuery.
This is happening helps to router which we connect in main file to dispatcher.
Typical usage example:

    from src.bot.handler import handler_commands
    dp = Dispatcher()
    dp.include_routers(handler_commands.router)
"""
from aiogram import types, F, Router, html
from aiogram.filters import Command
from termcolor import colored

from src.bot.keyboards import menu_keyboard, start_keyboard, back_keyboard
from src.pgsqldatabase.database import Database
from src.bot.handler.handler_strings import START_COMMAND, HELP_COMMAND

router = Router()


@router.message(Command("start"))
async def start_command(message: types.Message) -> None:
    """
    handler of command /start; print some start information
    :param message: obj message, consist information about user
    :return: None
    """
    database = Database()
    await message.answer(START_COMMAND.format(html.quote(message.from_user.full_name)) + HELP_COMMAND,
                         reply_markup=start_keyboard)
    try:
        await database.add_user(message.from_user.id, message.from_user.full_name, message.from_user.username)
    except ValueError as e:
        print(colored(e, "red"))
    print(message.from_user.id, message.from_user.full_name)


@router.callback_query(F.data == "help")
@router.message(Command("help"))
async def help_command(update) -> None:
    """
    handler of command /help; print useful information
    :param update: obj message, consist information about user
    :return: None
    """
    if isinstance(update, types.Message):
        await update.answer(HELP_COMMAND, reply_markup=back_keyboard)
    elif isinstance(update, types.CallbackQuery):
        await update.message.edit_text(HELP_COMMAND, reply_markup=back_keyboard)


@router.callback_query(F.data == "menu")
@router.message(Command("menu"))
async def menu_command(update) -> None:
    if isinstance(update, types.Message):
        await update.answer(f"Menu:", reply_markup=menu_keyboard)
    elif isinstance(update, types.CallbackQuery):
        await update.message.edit_text(f"Menu:", reply_markup=menu_keyboard)

