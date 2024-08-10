from aiogram import types, F, Router, Bot
from src.bot.keyboards import back_keyboard, next_prev_page_all, next_prev_page_today
from src.agent.main import Agent
from src.pgsqldatabase.database import Database
from src.bot.articles import Articles

router = Router()
agent = Agent()
database = Database()
articles = Articles()


def join_articles(list_of_articles: list) -> str:
    return "----------\n".join(list_of_articles)


@router.callback_query(F.data.in_({"show_page_article_all",
                                   "show_page_article_all_inline_btn_next", "show_page_article_all_inline_btn_prev"}))
async def page_articles_all_handler(call: types.CallbackQuery) -> None:
    if not articles.list_of_all_pages:
        await articles.generate_all_pages()

    if call.data == "show_page_article_all":
        await articles.page_index_all_start()
        response = join_articles(articles.list_of_all_pages[articles.page_index_all])
        await call.message.answer(response, reply_markup=next_prev_page_all)
        return
    elif call.data == "show_page_article_all_inline_btn_next":
        await articles.page_index_all_next()
    elif call.data == "show_page_article_all_inline_btn_prev":
        await articles.page_index_all_prev()
    try:
        response = join_articles(articles.list_of_all_pages[articles.page_index_all])
        await call.message.edit_text(response, reply_markup=next_prev_page_all)
    except Exception:
        pass


@router.callback_query(F.data.in_({"show_page_article_today",
                                   "show_page_article_today_inline_btn_next",
                                   "show_page_article_today_inline_btn_prev"}))
async def page_articles_today_handler(call: types.CallbackQuery) -> None:
    if not articles.list_of_today_pages:
        await articles.generate_today_pages()
    if not articles.list_of_today_pages:
        await call.message.answer("Сегодня еще не вышла ни одна статья")
        return
    if call.data == "show_page_article_today":
        await articles.page_index_today_start()
        response = articles.list_of_today_pages[articles.page_index_today]
        await call.message.answer(response, reply_markup=next_prev_page_today)
        return
    elif call.data == "show_page_article_today_inline_btn_next":
        await articles.page_index_today_next()
    elif call.data == "show_page_article_today_inline_btn_prev":
        await articles.page_index_today_prev()
    try:
        response = articles.list_of_today_pages[articles.page_index_today]
        await call.message.edit_text(response, reply_markup=next_prev_page_today)
    except Exception:
        pass


@router.callback_query(F.data == "clear_history")
async def clear_history_handler(call: types.CallbackQuery) -> None:
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
