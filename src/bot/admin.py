from asyncio import sleep
from contextlib import suppress
from datetime import datetime
from aiogram import types, F, Router
from aiogram.filters import Command
from src.bot.keyboards import admin_keyboard, back_admin_keyboard
from src.bot.my_filters import AdminFilter
from src.pgsqldatabase.database import Database
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from src.parser.main import main as parser_main
from src.bot.articles import Articles
from src.agent.main import Agent

router = Router()
database = Database()


class AdminState(StatesGroup):
    newsletter = State()


@router.callback_query(F.data == "admin_panel", AdminFilter())
@router.message(Command("admin"), AdminFilter())
async def admin_cmd(update, state: FSMContext):
    await state.clear()
    if isinstance(update, types.Message):
        await update.answer("Admin panel", reply_markup=admin_keyboard)
    elif isinstance(update, types.CallbackQuery):
        await update.message.edit_text("Admin panel", reply_markup=admin_keyboard)


@router.callback_query(F.data == "admin_statistic", AdminFilter())
async def admin_statistic(call: types.CallbackQuery) -> None:
    await call.message.edit_text(f"Users: {await database.print_all_users()}\n"
                                 f"Users count: {await database.count_users()}", reply_markup=back_admin_keyboard)


@router.callback_query(F.data == 'admin_newsletter', AdminFilter())
async def admin_newsletter(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_text('News letter for all users\n\n'
                                 'Input the message:', reply_markup=back_admin_keyboard)
    await state.set_state(AdminState.newsletter)


@router.message(AdminState.newsletter, AdminFilter())
async def admin_newsletter_step_2(message: types.Message, state: FSMContext):
    users_id = await database.get_all_users_id()
    await state.update_data(message_newsletter=message)
    for user_id in users_id:
        with suppress():
            await message.send_copy(user_id)
            await sleep(0.3)
    await state.clear()


@router.callback_query(F.data == 'admin_parse_articles', AdminFilter())
async def admin_parse_today_articles(call: types.CallbackQuery):
    articles = Articles()
    agent = Agent()
    target_time = datetime.today().strftime('%Y-%m-%d')
    await parser_main(target_time)
    await articles.clean_old_articles()
    await articles.load()
    await agent.generate_agent_executor()




