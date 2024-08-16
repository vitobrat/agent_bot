"""
This is a store of all keyboard buttons which utilise in bot

Typical usage example:

    from src.bot.keyboards import *
"""
from aiogram import types

commands = [
    types.BotCommand(command="/start", description="Запустить бота"),
    types.BotCommand(command="/help", description="Полезная информация"),
    types.BotCommand(command="/menu", description="Меню")
]


back_keyboard_list = [
    [
        types.InlineKeyboardButton(text="Назад", callback_data='menu')
    ],
]
back_keyboard = types.InlineKeyboardMarkup(inline_keyboard=back_keyboard_list)

menu_keyboard_list = [
    [types.InlineKeyboardButton(text="Показать все статьи", callback_data="show_page_article_all")],
    [types.InlineKeyboardButton(text="Показать сегодняшние статьи", callback_data="show_page_article_today")],
    [types.InlineKeyboardButton(text="Очистить контекст беседы", callback_data="clear_history")],
    [types.InlineKeyboardButton(text="Контакты разработчика", callback_data="contacts")],
    [types.InlineKeyboardButton(text="О проекте", callback_data="about_project")],
]
menu_keyboard = types.InlineKeyboardMarkup(inline_keyboard=menu_keyboard_list)

next_prev_page_all_list = [
    [
        types.InlineKeyboardButton(text="Назад", callback_data="show_page_article_all_inline_btn_prev"),
        types.InlineKeyboardButton(text="Вперед", callback_data="show_page_article_all_inline_btn_next")
    ]
]
next_prev_page_all = types.InlineKeyboardMarkup(inline_keyboard=next_prev_page_all_list)

next_prev_page_today_list = [
    [
        types.InlineKeyboardButton(text="Назад", callback_data="show_page_article_today_inline_btn_prev"),
        types.InlineKeyboardButton(text="Вперед", callback_data="show_page_article_today_inline_btn_next")
    ]
]
next_prev_page_today = types.InlineKeyboardMarkup(inline_keyboard=next_prev_page_today_list)

start_keyboard_list = [
    [types.InlineKeyboardButton(text="Меню", callback_data="menu")],
    [types.InlineKeyboardButton(text="Помощь", callback_data="help")],
]
start_keyboard = types.InlineKeyboardMarkup(inline_keyboard=start_keyboard_list)


admin_keyboard_list = [
    [types.InlineKeyboardButton(text='Статистика', callback_data='admin_statistic')],
    [types.InlineKeyboardButton(text='Новостное уведомление', callback_data='admin_newsletter')],
    [types.InlineKeyboardButton(text='Спарсить сегодняшние статьи', callback_data='admin_parse_articles')]
]
admin_keyboard = types.InlineKeyboardMarkup(inline_keyboard=admin_keyboard_list)

back_admin_keyboard_list = [
    [
        types.InlineKeyboardButton(text="Назад", callback_data='admin_panel')
    ],
]
back_admin_keyboard = types.InlineKeyboardMarkup(inline_keyboard=back_admin_keyboard_list)