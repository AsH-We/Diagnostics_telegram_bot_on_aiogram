from aiogram import Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from keyboards import for_questions

sallyId = 935373156
mansurId = 1439283980

import google.generativeai as genai

geminiToken= "AIzaSyBCgNXugcet_M9-Gbwe_3gOWGdzHPnpepQ"

genai.configure(api_key=geminiToken)

# Create the model
generation_config = {
  "temperature": 1,
  "top_p": 0.95,
  "top_k": 64,
  "max_output_tokens": 8192,
  "response_mime_type": "text/plain",
}

model = genai.GenerativeModel(
  model_name="gemini-1.5-flash",
  generation_config=generation_config
)

chat_session = model.start_chat(
  history=[
    {
      "role": "user",
      "parts": [
        "Я дам тебе кое какую информацию. дай мне краткий отчет по типу скада ума. Аналитический / Творческий. Опиши вкратце перспективы в IT по данному складу ума",
      ],
    },
    {
      "role": "model",
      "parts": [
        "Хорошо! Давай,  делитесь информацией.  Расскажите мне, что вы хотите, чтобы я проанализировал, и я постараюсь дать вам краткий отчет в стиле скада ума. \n\nСкажите,  что именно вы хотите, чтобы я  проанализировал,  и я постараюсь  определить,  какой  стиль мышления  (аналитический  или  творческий)  будет  более  подходящим  для  этого.\n",
      ],
    },
{
      "role": "user",
      "parts": [
        "Выполни его по шаблону.\nСудя по твоим ответам. Ты имеешь … склад ума. MobyDev рекомендует тебе попробовать {джемини, выбери чтото из ios разработка, android разработка, web разработка,backend на Go, python, что-то подобное}",
      ],
    }
  ]
)


bot = None

def set_bot(bot_instance):
    global bot
    bot = bot_instance

router = Router()

courses = ['Химия', 'Математика', 'Биология', 'Литература', 'Иностранные языки', 'История', 'Физ-ра']
perseverances = ['Я усидчивый, люблю спокойно сидеть и работать', 'Я активный, но могу и спокойно заниматься делами', 'Я гиперактивный, не могу сидеть на месте']
teams = ['Да, мне всегда легче в команде', 'Да, но только в позиции лидера', 'Не совсем, но когда надо, могу подстроиться', 'Нет, мне легче сделать все самой(-му)']


class Diagnostika(StatesGroup):
    choosing_course = State()
    choosing_reason = State()
    choosing_perseverance = State()
    choosing_team = State()
    choosing_number = State()
    wait = State()
    final = State()


@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    await message.answer(
        "Привет! Скоро ты узнаешь о себе получше) Можно узнать как тебя зовут?"
    )

    await state.set_state(Diagnostika.choosing_course)


@router.message(Diagnostika.choosing_course)
async def name_chosen(message: Message, state: FSMContext):
    await state.update_data(name=message.text.lower())

    await message.answer(f"Приятно познакомиться {message.text}")
    await message.answer(
        "Можешь выбрать предмет который тебе нравится в школе?",
        reply_markup=for_questions.foo(courses)
    )

    await state.set_state(Diagnostika.choosing_reason)


@router.message(Diagnostika.choosing_reason)
async def course_chosen(message: Message, state: FSMContext):
    await state.update_data(course=message.text.lower())

    await message.answer(
        "Что тебя в нём больше всего цепляет?",
        reply_markup=ReplyKeyboardRemove()
    )

    await state.set_state(Diagnostika.choosing_perseverance)


@router.message(Diagnostika.choosing_perseverance)
async def reason_chosen(message: Message, state: FSMContext):
    await state.update_data(reason=message.text.lower())

    await message.answer(
        "Как ты оцениваешь свою усидчивость?",
        reply_markup=for_questions.foo(perseverances)
    )

    await state.set_state(Diagnostika.choosing_team)


@router.message(Diagnostika.choosing_team)
async def perseverance_chosen(message: Message, state: FSMContext):
    await state.update_data(perseverance=message.text.lower())

    await message.answer(
        "Можешь ли ты назвать себя командным игроком?",
        reply_markup=for_questions.foo(teams)
    )

    await state.set_state(Diagnostika.choosing_number)


@router.message(Diagnostika.choosing_number)
async def team_chosen(message: Message, state: FSMContext):
    await state.update_data(team=message.text.lower())

    button_phone = types.KeyboardButton(text="Делись!", request_contact=True)

    kb = ReplyKeyboardBuilder()
    kb.row(button_phone)

    await message.answer(text="Последний шаг.\nОтправь номер и ты узнаешь результат диагностики)",
                         reply_markup=kb.as_markup(resize_keyboard=True))

    await state.set_state(Diagnostika.wait)


@router.message(Diagnostika.wait)
async def wait(message: Message, state: FSMContext):
    print('wait')
    await state.update_data(number=message.contact.phone_number)

    await message.answer(
        'Чуть-чуть подожди...',
        reply_markup=ReplyKeyboardRemove()
    )

    await final(message, state)

    # await state.set_state(Diagnostika.final)


# @router.message(Diagnostika.final)
async def final(message: Message, state: FSMContext):
    print('final')
    user = await state.get_data()
    info = f"Имя - {user['name']}\nПредмет - {user['course']}\nПричина-{user['reason']}\nУсидчивость-{user['perseverance']}\nКоманда - {user['team']} \nНомер - {user['number']}"

    response = chat_session.send_message(info).text

    await message.answer(
        response
    )
    await bot.send_message(chat_id=mansurId, text=info)
    await bot.send_message(chat_id=mansurId, text=response)

    await bot.send_message(chat_id=sallyId, text=info)
    await bot.send_message(chat_id=sallyId, text=response)

    await state.clear()


# NOOO===============
# В целом, никто не мешает указывать стейты полностью строками
# Это может пригодиться, если по какой-то причине
# ваши названия стейтов генерируются в рантайме (но зачем?)
# @router.message(StateFilter("OrderFood:choosing_food_name"))
# async def food_chosen_incorrectly(message: Message):
#     await message.answer(
#         text="Я не знаю такого блюда.\n\n"
#              "Пожалуйста, выберите одно из названий из списка ниже:",
#         reply_markup=for_questions.foo(perseverances)
#     )

# Этап выбора размера порции и отображение сводной информации