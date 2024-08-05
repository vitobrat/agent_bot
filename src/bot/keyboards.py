from aiogram import types


back_keyboard_list = [
    [
        types.InlineKeyboardButton(text="Back", callback_data='menu')
    ],
]
back_keyboard = types.InlineKeyboardMarkup(inline_keyboard=back_keyboard_list)

menu_keyboard_list = [
    [types.InlineKeyboardButton(text="Contacts", callback_data="contacts")],
    [types.InlineKeyboardButton(text="About project", callback_data="about_project")],
]
menu_keyboard = types.InlineKeyboardMarkup(inline_keyboard=menu_keyboard_list)

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