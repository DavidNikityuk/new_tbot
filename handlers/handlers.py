from aiogram import F, Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from dotenv import load_dotenv
from datetime import datetime
import os
import keyboards.keyboards as kb
from middlewares.middlewares import TestMiddleware
from bot_instance import bot 
import dictionary
from bot_calendar.calendar import get_calendar_selection_keyboard, get_calendar_keyboard, get_time_slots_keyboard, get_time_slots_text

load_dotenv()
CHANNEL_TOKEN = os.getenv('CHANNEL_TOKEN')
router = Router()

class ConsultationStates(StatesGroup):
    waiting_for_name = State()
    waiting_for_contact = State()
    waiting_for_request_reason = State()
    waiting_for_date_selection = State()

@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer(dictionary.start_text, reply_markup=kb.start_button)

@router.message(F.text == 'как происходит первая консультация?')
async def cmd_howItWillBe(message: Message):
    await message.answer(dictionary.howItWillBe_text, reply_markup=kb.main_button)

@router.message(F.text == 'отмена')
async def cmd_cancel(message: Message, state: FSMContext):
    await message.answer(dictionary.cancel_text, reply_markup=kb.start_button)
    await state.clear()

@router.message(F.text == 'записаться на консультацию')
async def cmd_consultation(message: Message, state: FSMContext):
    await state.set_state(ConsultationStates.waiting_for_name)
    await message.answer('отлично! пожалуйста, напиши мне свое имя', reply_markup=kb.cancel_button)

@router.message(ConsultationStates.waiting_for_name)
async def contact_state(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    data = await state.get_data()
    await state.set_state(ConsultationStates.waiting_for_contact)
    await message.answer(f"{data['name']}, " + dictionary.name_text)

@router.message(ConsultationStates.waiting_for_contact)
async def requestReason_state(message: Message, state: FSMContext):
    await state.update_data(contact=message.text)
    await state.set_state(ConsultationStates.waiting_for_request_reason)
    await message.answer(dictionary.contact_text)

@router.message(ConsultationStates.waiting_for_request_reason)
async def finish_request(message: Message, state: FSMContext):
    await state.update_data(request=message.text)
    data = await state.get_data()
    await message.answer(dictionary.final_text, reply_markup=kb.start_button)
    await message.answer(dictionary.social_text, reply_markup=kb.socialMeadia_inlineButton)
    await bot.send_message(CHANNEL_TOKEN, f'Имя: {data["name"]}\n\nКонтакт: {data["contact"]}\n\nЗапрос: {data["request"]}')
    await state.clear()
    # await message.answer(dictionary.calendar_selection_text, reply_markup=get_calendar_selection_keyboard())


# Calendar
@router.callback_query(F.data.startswith("calendar_month_"))
async def process_calendar_month_selection(callback: CallbackQuery):
    _, _, year, month = callback.data.split("_")
    year, month = int(year), int(month)
    now = datetime.now()
    selected_date = datetime(year, month, 1)
    if selected_date.date() < now.date().replace(day=1):
        await callback.answer("❌ Нельзя выбрать прошедший месяц!", show_alert=True)
        return
    calendar_kb = get_calendar_keyboard(year, month)
    await callback.message.edit_text(dictionary.calendar_selection_text, reply_markup=calendar_kb)
    await callback.answer()

@router.callback_query(F.data.startswith("calendar_prev_"))
async def process_calendar_prev_month(callback: CallbackQuery):
    _, _, year, month = callback.data.split("_")
    year, month = int(year), int(month)
    now = datetime.now()
    selected_date = datetime(year, month, 1)
    if selected_date.date() < now.date().replace(day=1):
        await callback.answer("❌ Нельзя выбрать прошедший месяц!", show_alert=True)
        return
    calendar_kb = get_calendar_keyboard(year, month)
    await callback.message.edit_reply_markup(reply_markup=calendar_kb)
    await callback.answer()

@router.callback_query(F.data.startswith("calendar_next_"))
async def process_calendar_next_month(callback: CallbackQuery):
    _, _, year, month = callback.data.split("_")
    year, month = int(year), int(month)
    calendar_kb = get_calendar_keyboard(year, month)
    await callback.message.edit_reply_markup(reply_markup=calendar_kb)
    await callback.answer()

@router.callback_query(F.data.startswith("calendar_date_"))
async def process_calendar_date_selection(callback: CallbackQuery):
    _, _, year, month, day = callback.data.split("_")
    year, month, day = int(year), int(month), int(day)
    time_slots_text = get_time_slots_text(year, month, day)
    time_slots_kb = get_time_slots_keyboard(year, month, day)
    await callback.message.edit_text(time_slots_text, reply_markup=time_slots_kb)
    await callback.answer()

@router.callback_query(F.data == "calendar_cancel")
async def process_calendar_cancel(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await bot.send_message(
        CHANNEL_TOKEN, 
        f'📝 Новая запись на консультацию\n\n'
        f'Имя: {data["name"]}\n'
        f'Контакт: {data["contact"]}\n'
        f'Запрос: {data["request"]}\n\n'
        f'❌ Пользователь отказался от выбора даты'
    )
    await callback.message.delete()
    await callback.answer("Выбор даты отменен")
    await callback.message.answer(dictionary.final_text, reply_markup=kb.start_button)
    await callback.message.answer(dictionary.social_text, reply_markup=kb.socialMeadia_inlineButton)
    await state.clear()

@router.callback_query(F.data.startswith("time_slot_"))
async def process_time_slot_selection(callback: CallbackQuery, state: FSMContext):
    _, _, year, month, day, time_slot = callback.data.split("_")
    year, month, day = int(year), int(month), int(day)
    selected_date = f"{day:02d}.{month:02d}.{year}"
    data = await state.get_data()
    await bot.send_message(
        CHANNEL_TOKEN, 
        f'📝 Новая запись на консультацию\n\n'
        f'Имя: {data["name"]}\n'
        f'Контакт: {data["contact"]}\n'
        f'Запрос: {data["request"]}\n\n'
        f'📅 Предпочтительная дата: {selected_date}\n'
        f'🕐 Предпочтительное время: {time_slot}'
    )
    await callback.message.answer(
        f"📅 Запись подтверждена!\n\n"
        f"Дата: {selected_date}\n"
        f"Время: {time_slot}\n\n"
        f"{dictionary.time_slot_selected_text}"
    )
    await callback.message.delete()
    await callback.answer()
    await callback.message.answer(dictionary.final_text, reply_markup=kb.start_button)
    await callback.message.answer(dictionary.social_text, reply_markup=kb.socialMeadia_inlineButton)
    await state.clear()

@router.callback_query(F.data == "calendar_error")
async def process_calendar_error(callback: CallbackQuery):
    await callback.answer("❌ Нельзя выбрать прошедшую дату!", show_alert=True)

@router.callback_query(F.data.in_(["calendar_info", "calendar_weekday", "calendar_empty", "calendar_past"]))
async def process_calendar_info(callback: CallbackQuery):
    await callback.answer()