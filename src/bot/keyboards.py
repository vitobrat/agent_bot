from aiogram import types


back_keyboard_list = [
    [
        types.InlineKeyboardButton(text="Back", callback_data='menu')
    ],
]
back_keyboard = types.InlineKeyboardMarkup(inline_keyboard=back_keyboard_list)

menu_keyboard_list = [
    [types.InlineKeyboardButton(text="Показать все статьи", callback_data="show_page_article_all")],
    [types.InlineKeyboardButton(text="Показать сегодняшние статьи", callback_data="show_page_article_today")],
    [types.InlineKeyboardButton(text="Очистить контекст беседы", callback_data="clear_history")],
    [types.InlineKeyboardButton(text="Contacts", callback_data="contacts")],
    [types.InlineKeyboardButton(text="About project", callback_data="about_project")],
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
    [types.InlineKeyboardButton(text="Menu", callback_data="menu")],
    [types.InlineKeyboardButton(text="Help", callback_data="help")],
]
start_keyboard = types.InlineKeyboardMarkup(inline_keyboard=start_keyboard_list)


admin_keyboard_list = [
    [
        types.InlineKeyboardButton(text='Statistics', callback_data='admin_statistic'),
        types.InlineKeyboardButton(text='News letter', callback_data='admin_newsletter')
    ]
]
admin_keyboard = types.InlineKeyboardMarkup(inline_keyboard=admin_keyboard_list)

back_admin_keyboard_list = [
    [
        types.InlineKeyboardButton(text="Back", callback_data='admin_panel')
    ],
]
back_admin_keyboard = types.InlineKeyboardMarkup(inline_keyboard=back_admin_keyboard_list)