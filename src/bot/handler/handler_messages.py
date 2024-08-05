from aiogram import types, F, Router, Bot
from src.bot.keyboards import back_keyboard
from src.agent.main import answer

router = Router()


@router.callback_query(F.data == "contacts")
async def contacts_handler(call: types.CallbackQuery, bot: Bot) -> None:
    await call.message.edit_text(f"My contacts:{(await bot.get_me()).full_name}",
                                 reply_markup=back_keyboard)


@router.callback_query(F.data == "about_project")
async def about_handler(call: types.CallbackQuery) -> None:
    await call.message.edit_text(f"Some information about project:{call.message.from_user.full_name}",
                                 reply_markup=back_keyboard)


@router.message(F.text)
async def print_text(message: types.Message):
    print(message.text)
    response = answer(message.text)
    await message.answer(response)

