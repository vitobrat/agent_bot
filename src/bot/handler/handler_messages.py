"""
This is a method with a handler for all user messages

When user write some message to bot, then this module handle it.
Also, this module handle clicks to buttons by CallbackQuery.
This is happening helps to router which we connect in main file to dispatcher.
Typical usage example:

    from src.bot.handler import handler_messages
    dp = Dispatcher()
    dp.include_routers(handler_messages.router)
"""
from aiogram import types, F, Router, Bot
import asyncio
from src.bot.keyboards import back_keyboard, next_prev_page_all, next_prev_page_today
from src.agent.main import Agent
from src.pgsqldatabase.database import Database
from src.articles.articles import Articles
from src.articles.user import User, UsersIds
from src.bot.handler.handler_strings import CONTACTS_MESSAGE, ABOUT_PROJECT_MESSAGE


router = Router()
users_id = UsersIds()


def join_articles(list_of_articles: list) -> str:
    """Join the list of articles to string separated by ---

    Attributes:
        list_of_articles: news articles which needed to show to user

    Returns:
        text that we show to user
    """
    return "----------\n".join(list_of_articles)


@router.callback_query(F.data.in_({"show_page_article_all",
                                   "show_page_article_all_inline_btn_next", "show_page_article_all_inline_btn_prev"}))
async def page_articles_all_handler(call: types.CallbackQuery) -> None:
    """Show the right page of articles

    When user open or switch page the router decorator take this event call and function handle user query
    (show starts articles or switch it to another)

    Attribute:
        call: information that provides from user query (user id and e.t.c.)
    """
    articles = Articles()
    user = users_id.find_user(call.from_user.id)
    # If user start event in first time then we add him in list and start monitor his index page
    if user is None:
        user = User(call.from_user.id)
        users_id.append(user)
    # If he opens articles from menu then show him articles from index 0
    if call.data == "show_page_article_all":
        response = join_articles(articles.list_of_all_pages[user.page_index_all])
        await call.message.answer(response, reply_markup=next_prev_page_all)
        return
    # If he switches articles to next then change index to next number
    elif call.data == "show_page_article_all_inline_btn_next":
        await user.page_index_all_next()
    # If he switches articles to previous then change index to previous number
    elif call.data == "show_page_article_all_inline_btn_prev":
        await user.page_index_all_prev()

    try:
        response = join_articles(articles.list_of_all_pages[user.page_index_all])
        await call.message.edit_text(response, reply_markup=next_prev_page_all)
    except Exception:
        pass


@router.callback_query(F.data.in_({"show_page_article_today",
                                   "show_page_article_today_inline_btn_next",
                                   "show_page_article_today_inline_btn_prev"}))
async def page_articles_today_handler(call: types.CallbackQuery) -> None:
    """Show the right page of today articles

        When user open or switch page the router decorator take this event call and function handle user query
        (show starts today articles or switch it to another)

        Attribute:
            call: information that provides from user query (user id and e.t.c.)
        """
    articles = Articles()
    user = users_id.find_user(call.from_user.id)
    # If user start event in first time then we add him in list and start monitor his index page
    if user is None:
        user = User(call.from_user.id)
        users_id.append(user)
    # If it hasn't new articles yet
    if not articles.list_of_today_pages:
        await call.message.answer("Сегодня еще не вышла ни одна статья")
        return
    # If he opens articles from menu then show him articles from index 0
    if call.data == "show_page_article_today":
        await user.page_index_today_start()
        response = articles.list_of_today_pages[user.page_index_today]
        await call.message.answer(response, reply_markup=next_prev_page_today)
        return
    # If he switches articles to next then change index to next number
    elif call.data == "show_page_article_today_inline_btn_next":
        await user.page_index_today_next()
    # If he switches articles to previous then change index to previous number
    elif call.data == "show_page_article_today_inline_btn_prev":
        await user.page_index_today_prev()

    try:
        response = articles.list_of_today_pages[user.page_index_today]
        await call.message.edit_text(response, reply_markup=next_prev_page_today)
    except Exception:
        pass


@router.callback_query(F.data == "clear_history")
async def clear_history_handler(call: types.CallbackQuery) -> None:
    """Clear dialog history with LLM

    Attribute:
            call: information that provides from user query (user id and e.t.c.)
    """
    database = Database()
    await database.update_user_history(call.from_user.id, None)
    if not await database.get_user_history(call.from_user.id):
        await call.message.answer("История диалога успешно очищена!")
    else:
        await call.message.answer("Что-то пошло не так :(")


@router.callback_query(F.data == "contacts")
async def contacts_handler(call: types.CallbackQuery) -> None:
    """Provide developer contacts

    Attribute:
            call: information that provides from user query (user id and e.t.c.)
    """
    await call.message.edit_text(CONTACTS_MESSAGE,
                                 reply_markup=back_keyboard)


@router.callback_query(F.data == "about_project")
async def about_handler(call: types.CallbackQuery) -> None:
    """Provide information about this project

    Attribute:
            call: information that provides from user query (user id and e.t.c.)
    """
    await call.message.edit_text(ABOUT_PROJECT_MESSAGE,
                                 reply_markup=back_keyboard)


@router.message(F.text)
async def query(message: types.Message) -> None:
    """LLM response to user query

    When user text any information to bot,
    then RAG agent handle this query and provide response and send this response in message to user

    Attribute:
            message: information that provides from user query (user id and e.t.c.)
    """
    agent = Agent()
    print(message.text)
    asyncio.create_task(agent.answer(message))
