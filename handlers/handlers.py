from aiogram import F, Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from dotenv import load_dotenv
import os

import keyboards.keyboards as kb
from middlewares.middlewares import TestMiddleware
from bot_instance import bot 
import dictionary


load_dotenv()

CHANNEL_TOKEN = os.getenv('CHANNEL_TOKEN')

router = Router()

# router.message.middleware(TestMiddleware())

class ConsultationStates(StatesGroup):
    waiting_for_name = State()
    waiting_for_contact = State()
    waiting_for_request_reason = State()

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