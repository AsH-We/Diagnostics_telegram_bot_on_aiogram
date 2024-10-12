import telebot
from telebot import types

import google.generativeai as genai

botToken = "6668396591:AAFm4eJg-UBSVyMjp_KMK_esNtgvc8Rhntg"
geminiToken= "AIzaSyBCgNXugcet_M9-Gbwe_3gOWGdzHPnpepQ"
sallyId = 935373156

bot = telebot.TeleBot(botToken)

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
        "Я дам тебе кое какую информацию. дай мне краткий отчет по типу скада ума. Аналитический / Творческий (напиши менее 100-та слов). Опиши вкратце перспективы в IT по данному складу ума",
      ],
    },
    {
      "role": "model",
      "parts": [
        "Хорошо! Давай,  делитесь информацией.  Расскажите мне, что вы хотите, чтобы я проанализировал, и я постараюсь дать вам краткий отчет в стиле скада ума. \n\nСкажите,  что именно вы хотите, чтобы я  проанализировал,  и я постараюсь  определить,  какой  стиль мышления  (аналитический  или  творческий)  будет  более  подходящим  для  этого.\n",
      ],
    },
  ]
)

# response = chat_session.send_message("INSERT_INPUT_HERE")
#
# print(response.text)

user = {}

courses = ['Химия', 'Математика', 'Биология', 'Литература', 'Иностранные языки', 'История', 'Физ-ра']
perseverances = [ 'Я усидчивый, люблю спокойно сидеть и работать', 'Я активный, но могу и спокойно заниматься делами', 'Я гиперактивный, не могу сидеть на месте' ]
teams = [ 'Да, мне всегда легче в команде', 'Да, но только в позиции лидера', 'Не совсем, но когда надо, могу подстроиться', 'Нет, мне легче сделать все самой(-му)' ]

@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id, 'Привет! Скоро ты узнаешь о себе получше) Можно узнать как тебя зовут?')
    bot.register_next_step_handler(message, ask_name)

def ask_name(message):
    user['name'] = message.text
    bot.send_message(message.chat.id, f"Приятно познакомиться, {user['name']}")

    # выборка предметов (types)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for course in courses:
        markup.add(types.KeyboardButton(course))

    bot.send_message(message.chat.id,
                    "Можешь выбрать предмет который тебе нравится в школе?",
                     reply_markup=markup)

    bot.register_next_step_handler(message, ask_course)

def ask_course(message):
    user['course'] = message.text
    bot.send_message(message.chat.id, "Что тебя в нём больше всего цепляет?",
                     reply_markup=types.ReplyKeyboardRemove())
    bot.register_next_step_handler(message, ask_reason)

def ask_reason(message):
    user['reason'] = message.text

    # выборка (types)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for perseverance in perseverances:
        markup.add(types.KeyboardButton(perseverance))

    bot.send_message(message.chat.id,
                     "Как ты оцениваешь свою усидчивость?",
                     reply_markup=markup)

    bot.register_next_step_handler(message, ask_perseverance)

def ask_perseverance(message):
    user['perseverance'] = message.text

    # выборка (types)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for team in teams:
        markup.add(types.KeyboardButton(team))

    bot.send_message(message.chat.id,
                     "Можешь ли ты назвать себя командным игроком?",
                     reply_markup=markup)

    bot.register_next_step_handler(message, ask_team)

def ask_team(message):
    user['team'] = message.text

    # номер телефона
    keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    reg_button = types.KeyboardButton(text="Отправить номер телефона", request_contact=True)
    keyboard.add(reg_button)

    bot.send_message(message.chat.id,
                     "Последний шаг.\nОтправь номер и ты узнаешь результат диагностики)",
                     reply_markup=keyboard)

    bot.register_next_step_handler(message, final)

def final(message):
    user['number'] = message.contact.phone_number

    info = f"Имя - {user['name']}\nПредмет - {user['course']}\nПричина-{user['reason']}\nУсидчивость-{user['perseverance']}\nКоманда - {user['team']} \nНомер - {user['number']}"

    response = chat_session.send_message(info).text
    bot.send_message(message.chat.id, response, reply_markup=types.ReplyKeyboardRemove())

    bot.send_message(sallyId, response)
    bot.send_message(sallyId, info)

    bot.send_message(message.chat.id, "Конец")



bot.polling(non_stop=True)