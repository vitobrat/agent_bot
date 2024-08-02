from aiogram import types, F, Router, html
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from src.bot.keyboards import menu_keyboard, start_keyboard, back_keyboard
from src.aiopgsqldatabase.database import add_user

router = Router()


@router.message(Command("start"))
async def start_command(message: types.Message) -> None:
    """
    handler of command /start; print some start information
    :param message: obj message, consist information about user
    :return: None
    """
    await message.answer(f"Welcome, <b>{html.quote(message.from_user.full_name)}</b>!",
                         reply_markup=start_keyboard)
    await add_user(message.from_user.id, message.from_user.full_name, message.from_user.username)
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
        await update.answer("This is project about...\n"
                            "There are some useful commands:", reply_markup=back_keyboard)
    elif isinstance(update, types.CallbackQuery):
        await update.message.edit_text("This is project about...\n"
                                       "There are some useful commands:", reply_markup=back_keyboard)


@router.callback_query(F.data == "menu")
@router.message(Command("menu"))
async def menu_command(update) -> None:
    if isinstance(update, types.Message):
        await update.answer(f"Menu:", reply_markup=menu_keyboard)
    elif isinstance(update, types.CallbackQuery):
        await update.message.edit_text(f"Menu:", reply_markup=menu_keyboard)

