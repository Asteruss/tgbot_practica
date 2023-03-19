import telebot
from telebot import types
import requests
import random
from googletrans import Translator

# translate
translator = Translator()

def translate(text):
    return translator.translate(text, dest="ru").text

# api`s
numbers_api = "http://numbersapi.com"
quiz_api = "http://jservice.io/api/random?count=1"

# token
TOKEN = "TOKEN"
bot = telebot.TeleBot(TOKEN)

# keyboard main
reply_keyborad_main = types.ReplyKeyboardMarkup(resize_keyboard=True)
reply_keyborad_main.add(types.KeyboardButton("Расскажи о себе"))
reply_keyborad_main.add(types.KeyboardButton("Узнать о цифре"))
reply_keyborad_main.add(types.KeyboardButton("Хочу загадку"))

answer_dc = {}
categories_people_dc = {}

# категории
categories = ["факт из жизни",
              "математический факт", "дата(день)", "дата(год)"]
categories_dc = {
    categories[0]: "trivia",
    categories[1]: "math",
    categories[2]: "date",
    categories[3]: "year",
    "случайный": ""
}

greetings = ["Привет", "Прив", "Хай", "Добрый день"]
goodbye = ["Пока", "Прощай", "До встречи"]

@bot.message_handler(commands=["start"])
def start(message: types.Message):
    bot.send_message(message.chat.id, "Выбирайте",
                     reply_markup=reply_keyborad_main)


@bot.message_handler(regexp="\d")
def send_number(message: types.Message):
    number = requests.get(numbers_api+f"/{message.text}"+(
        "" if message.from_user.id not in categories_people_dc.keys() else f"/{categories_people_dc[message.from_user.id]}"))
    if number.status_code == 200:
        bot.send_message(message.chat.id, translate(number.text))


@bot.message_handler(content_types=["text"])
def message_handle(message: types.Message):
    if message.text == "Расскажи о себе":
        inf = "Привет!!! Я могу рассказть тебе интересный факт о любом числе или задать тебе самый каверзный вопрос. 😉"
        bot.send_animation(message.chat.id, open(
            f"gifs_hello/{random.randint(1,4)}.gif", "rb"))
        bot.send_message(message.chat.id, inf)
    elif message.text in greetings:
        bot.send_message(message.chat.id, random.choice(greetings))
    elif message.text in goodbye:
        bot.send_message(message.chat.id, random.choice(goodbye))
    elif message.text == "Узнать о цифре":
        reply_keyborad = types.InlineKeyboardMarkup()
        for el in categories:
            reply_keyborad.add(
                types.InlineKeyboardButton(el, callback_data=el))
        bot.send_message(message.chat.id, "Выберите категорию",
                         reply_markup=reply_keyborad, reply_to_message_id=message.id)
    elif message.text == "Хочу загадку":
        reply_keyborad = types.ReplyKeyboardMarkup(resize_keyboard=True)
        reply_keyborad.add(types.KeyboardButton("Узнать ответ"))
        question = requests.get(quiz_api).json()[0]
        question_text = question["question"]
        answer = question["answer"]
        answer_dc[message.from_user.id] = answer
        bot.send_message(message.chat.id, translate(question_text),
                         reply_markup=reply_keyborad)
    elif message.text == "Узнать ответ":
        answer = answer_dc.pop(message.from_user.id)
        bot.send_message(message.chat.id, translate(answer.replace("<i>", "").replace("</i>", "")),
                         reply_markup=reply_keyborad_main)
        bot.send_message(message.chat.id, "Надеюсь вы ответили правильно :-)")


@bot.callback_query_handler(func = lambda call: True)
def callback_query(call: types.CallbackQuery):
    category = categories_dc[call.data]
    categories_people_dc[call.from_user.id] = category
    bot.send_message(call.from_user.id, f"Выбрана категория: {call.data}")
    bot.send_message(call.from_user.id, f"Теперь просто напишите любую цифру - и получите интересный факт ")


if __name__ == '__main__':
    bot.polling(none_stop=True, interval=0)
