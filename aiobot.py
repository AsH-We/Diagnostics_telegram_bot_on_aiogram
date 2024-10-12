import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.storage.memory import MemoryStorage
import google.generativeai as genai

botToken = "6668396591:AAFlcz4dVMX9adKtOK3bd3sq3YS23G6eL64"
geminiToken= "AIzaSyBCgNXugcet_M9-Gbwe_3gOWGdzHPnpepQ"
sallyId = 935373156

bot = Bot(token=botToken)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

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
        "Я дам тебе кое какую информацию. дай мне краткий отчет по типу скада ума. Аналитический / Творческий (напиши меньее 80-ти слов)",
      ],
    },
    {
      "role": "model",
      "parts": [
        "Хорошо! Давай, делитесь информацией. Расскажите мне, что вы хотите, чтобы я проанализировал, и я постараюсь дать вам краткий отчет в стиле скада ума.",
      ],
    },
  ]
)

user_data = {}
courses = ['Химия', 'Математика', 'Биология', 'Литература', 'Иностранные языки', 'История', 'Физ-ра']
perseverances = ['Я усидчивый, люблю спокойно сидеть и работать', 'Я активный, но могу и спокойно заниматься делами', 'Я гиперактивный, не могу сидеть на месте']
teams = ['Да, мне всегда легче в команде', 'Да, но только в позиции лидера', 'Не совсем, но когда надо, могу подстроиться', 'Нет, мне легче сделать все самой(-му)']


@dp.message(CommandStart())
async def start_message(message: types.Message):
    await message.answer('Привет! Скоро ты узнаешь о себе получше) Можно узнать как тебя зовут?')
    await dp.current_state(user=message.from_user.id).set_state("ask_name")


@dp.message(state="ask_name")
async def ask_name(message: types.Message, state):
    user_data[message.from_user.id] = {'name': message.text}
    await message.answer(f"Приятно познакомиться, {user_data[message.from_user.id]['name']}")

    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    for course in courses:
        markup.add(KeyboardButton(course))

    await message.answer("Можешь выбрать предмет который тебе нравится в школе?", reply_markup=markup)
    await state.set_state("ask_course")


@dp.message(state="ask_course")
async def ask_course(message: types.Message, state):
    user_data[message.from_user.id]['course'] = message.text
    await message.answer("Что тебя в нём больше всего цепляет?", reply_markup=types.ReplyKeyboardRemove())
    await state.set_state("ask_reason")


@dp.message(state="ask_reason")
async def ask_reason(message: types.Message, state):
    user_data[message.from_user.id]['reason'] = message.text

    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    for perseverance in perseverances:
        markup.add(KeyboardButton(perseverance))

    await message.answer("Как ты оцениваешь свою усидчивость?", reply_markup=markup)
    await state.set_state("ask_perseverance")


@dp.message(state="ask_perseverance")
async def ask_perseverance(message: types.Message, state):
    user_data[message.from_user.id]['perseverance'] = message.text

    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    for team in teams:
        markup.add(KeyboardButton(team))

    await message.answer("Можешь ли ты назвать себя командным игроком?", reply_markup=markup)
    await state.set_state("ask_team")


@dp.message(state="ask_team")
async def ask_team(message: types.Message, state):
    user_data[message.from_user.id]['team'] = message.text

    keyboard = ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    reg_button = KeyboardButton(text="Отправить номер телефона", request_contact=True)
    keyboard.add(reg_button)

    await message.answer("Последний шаг.\n Отправь номер и ты узнаешь результат диагностики)", reply_markup=keyboard)
    await state.set_state("final")


@dp.message(content_types=['contact'], state="final")
async def final(message: types.Message, state):
    user_data[message.from_user.id]['number'] = message.contact.phone_number

    info = (
        f"Имя - {user_data[message.from_user.id]['name']}\n"
        f"Предмет - {user_data[message.from_user.id]['course']}\n"
        f"Причина - {user_data[message.from_user.id]['reason']}\n"
        f"Усидчивость - {user_data[message.from_user.id]['perseverance']}\n"
        f"Команда - {user_data[message.from_user.id]['team']}\n"
        f"Номер - {user_data[message.from_user.id]['number']}"
    )

    response = chat_session.send_message(info).text
    await message.answer(response, reply_markup=types.ReplyKeyboardRemove())

    # await bot.send_message(sallyId, response)
    # await bot.send_message(sallyId, info)

    await message.answer("Конец")
    await state.finish()


async def main():
    await dp.start_polling(bot) # await dp.start_polling(bot, mylist=[1, 2, 3])


asyncio.run(main())
