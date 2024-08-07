from asyncio import sleep
from contextlib import suppress

from aiogram import types, F, Router
from aiogram.filters import Command
from src.bot.keyboards import admin_keyboard, back_admin_keyboard
from src.bot.my_filters import AdminFilter
from src.pgsqldatabase.database import Database
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

router = Router()
database = Database()


class AdminState(StatesGroup):
    newsletter = State()


async def all_users():
    return "\n".join([f"{i}) ID - {user[0]}; Full name - {user[1]}; User name - {user[2]};"
                      f"Is admin - {user[3]}"for i, user in enumerate(await database.get_all_users())])


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
    await call.message.edit_text(f"Users: {await all_users()}\n"
                                 f"Users count: {await database.count_users()}", reply_markup=back_admin_keyboard)


@router.callback_query(F.data == 'admin_newsletter', AdminFilter())
async def admin_newsletter(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_text('News letter for all users\n\n'
                                 'Input the message:', reply_markup=back_admin_keyboard)
    await state.set_state(AdminState.newsletter)


@router.message(AdminState.newsletter, AdminFilter())
async def admin_newsletter_step_2(message: types.Message, state: FSMContext):
    users_id = [id[0] for id in await database.get_all_users_id()]
    await state.update_data(message_newsletter=message)
    for id in users_id:
        with suppress():
            await message.send_copy(id)
            await sleep(0.3)
    await state.clear()
