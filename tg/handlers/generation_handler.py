from aiogram import Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.state import default_state
from aiogram.filters.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.types import (Message, InlineKeyboardButton,
                           InlineKeyboardMarkup, CallbackQuery)

from tg.lexicon.lexicon import LEXICON
from sklearn_training.response_generation import get_similar_response

generation_router: Router = Router()


# Машина состояния
class FSMUsermessage(StatesGroup):
    user_message = State()

# Активируем машину состояния при вводе команды /generate_response
@generation_router.message(Command(commands='generate_response'), StateFilter(default_state))
async def process_generation_command(message: Message, state: FSMContext):
    await message.answer(LEXICON['/generate_response'])
    await state.set_state(FSMUsermessage.user_message)

# Подбираем ответ от бота пользователю
@generation_router.message(StateFilter(FSMUsermessage.user_message))
async def process_user_message_sent(message: Message, state: FSMContext):
    user_input = message.text.lower()
    response = get_similar_response(user_input)

    # Кнопка под ответом для остановки генерации
    stop_generating_button = InlineKeyboardButton(text='Stop Generating', callback_data='stop_generating')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[stop_generating_button]])

    await message.answer(response, reply_markup=keyboard)
    await state.update_data(user_message=user_input)

# Для вывода из машины состояния
@generation_router.callback_query(lambda c: c.data == 'stop_generating')
async def stop_generating_callback(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.answer()
    await state.clear()
    await callback_query.message.answer(LEXICON['/stop_generating'])
