from aiogram.types import (ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton)

main_button = ReplyKeyboardMarkup( keyboard=[
        [KeyboardButton(text='записаться на консультацию')]
], resize_keyboard=True, one_time_keyboard=True, input_field_placeholder='выбери действие...')

start_button = ReplyKeyboardMarkup( keyboard=[
        [KeyboardButton(text='записаться на консультацию')],
        [KeyboardButton(text='как происходит первая консультация?')]
], resize_keyboard=True, one_time_keyboard=True, input_field_placeholder='выбери действие...')

cancel_button = ReplyKeyboardMarkup( keyboard=[
        [KeyboardButton(text='отмена')]
], resize_keyboard=True, one_time_keyboard=True)

socialMeadia_inlineButton = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='tiktok', url='https://www.tiktok.com/@youpsy.space'), InlineKeyboardButton(text='телеграм канал', url='https://t.me/youpsy_space')]
])