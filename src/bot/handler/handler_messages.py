from aiogram import types, F, Router, Bot
from src.bot.keyboards import back_keyboard
from src.agent.main import Agent
from src.pgsqldatabase.database import Database

router = Router()
agent = Agent()
database = Database()


@router.callback_query(F.data == "clear_history")
async def contacts_handler(call: types.CallbackQuery) -> None:
    await database.update_user_history(call.from_user.id, None)
    if not await database.get_user_history(call.from_user.id):
        await call.message.answer("История диалога успешно очищена!")
    else:
        await call.message.answer("Что-то пошло не так :(")


@router.callback_query(F.data == "contacts")
async def contacts_handler(call: types.CallbackQuery, bot: Bot) -> None:
    await call.message.edit_text(f"My contacts:{(await bot.get_me()).full_name}",
                                 reply_markup=back_keyboard)


@router.callback_query(F.data == "about_project")
async def about_handler(call: types.CallbackQuery) -> None:
    await call.message.edit_text(f"Some information about project:{call.message.from_user.full_name}",
                                 reply_markup=back_keyboard)


@router.message(F.text)
async def query(message: types.Message):
    print(message.text)
    respond = await agent.answer(message)


