"""
This is module interacts with admin panel

The admin panel provides only for users whose have admin access.
Admin access has only in users whose have 1 in is_admin row in database.
So if admin-user write special command /admin, then this module will handle it.
This is happening helps to router which we connect in main file to dispatcher.
Typical usage example:

    from src.bot.admin import admin
    dp = Dispatcher()
    dp.include_routers(admin.router)
"""

from asyncio import sleep
from contextlib import suppress
from datetime import datetime
from aiogram import types, F, Router
from aiogram.filters import Command
from src.bot.keyboards import admin_keyboard, back_admin_keyboard
from src.bot.admin.my_filters import AdminFilter
from src.pgsqldatabase.database import Database
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from src.parser.main import main as parser_main
from src.articles.articles import Articles
from src.agent.main import Agent
import asyncio

router = Router()


class AdminState(StatesGroup):
    """Consist all bot states"""

    newsletter = State()


@router.callback_query(F.data == "admin_panel", AdminFilter())
@router.message(Command("admin"), AdminFilter())
async def admin_cmd(update, state: FSMContext) -> None:
    """Show admin panel if user has admin access

    Attribute:
            update: information that provides from user query (user id and e.t.c.)
            state: consist current bot state
    """
    # Reset state to default
    await state.clear()
    if isinstance(update, types.Message):
        await update.answer("Admin panel", reply_markup=admin_keyboard)
    elif isinstance(update, types.CallbackQuery):
        await update.message.edit_text("Admin panel", reply_markup=admin_keyboard)


@router.callback_query(F.data == "admin_statistic", AdminFilter())
async def admin_statistic(call: types.CallbackQuery) -> None:
    """Provide all information from database about all users if user has admin access

    Attribute:
            call: information that provides from user query (user id and e.t.c.)
    """
    database = Database()
    await call.message.edit_text(
        f"Users: {await database.print_all_users()}\n"
        f"Users count: {await database.count_users()}",
        reply_markup=back_admin_keyboard,
    )


@router.callback_query(F.data == "admin_newsletter", AdminFilter())
async def admin_newsletter(call: types.CallbackQuery, state: FSMContext):
    """Switch bot state ready to take message

    Attribute:
            call: information that provides from user query (user id and e.t.c.)
            state: consist current bot state
    """
    await call.message.edit_text(
        "News letter for all users\n\n" "Input the message:",
        reply_markup=back_admin_keyboard,
    )
    await state.set_state(AdminState.newsletter)


@router.message(AdminState.newsletter, AdminFilter())
async def admin_newsletter_step_2(message: types.Message, state: FSMContext):
    """Get admin message and send it to all users

    Attribute:
            message: information that provides from user query (user id and e.t.c.)
            state: consist current bot state
    """
    database = Database()
    users_id = await database.get_all_users_id()
    await state.update_data(message_newsletter=message)
    for user_id in users_id:
        with suppress():
            await message.send_copy(user_id)
            await sleep(0.3)
    await state.clear()


@router.callback_query(F.data == "admin_parse_articles", AdminFilter())
async def admin_parse_today_articles(call: types.CallbackQuery):
    """Parsing data in manual mode"""
    articles = Articles()
    agent = Agent()
    target_time = datetime.today().strftime("%Y-%m-%d")
    asyncio.create_task(parser_main(target_time))
    asyncio.create_task(articles.clean_old_articles())
    asyncio.create_task(articles.load())
    asyncio.create_task(agent.generate_agent_executor())
