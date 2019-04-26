from telegram import Bot
from telegram import Update
from telegram.ext import Updater
from telegram.ext import CommandHandler
from telegram.ext import MessageHandler
from telegram.ext import Filters

TG_TOKEN = '758306079:AAEAL86jzh6_eowV8Ay6gTQ2cLUmNIrbujk'


def start(bot: Bot, update: Update):
    bot.send_message(chat_id=update.message.chat_id, text='Privet')


def echo(bot: Bot, update: Update):
    text = update.message.text
    bot.send_message(chat_id=update.message.chat_id, text=text)


def main():
    bot = Bot(token=TG_TOKEN)
    updater = Updater(bot=bot)

    start_handler = CommandHandler('start', start)
    messege_handler = MessageHandler(Filters.text, echo)

    updater.dispatcher.add_handler(start_handler)
    updater.dispatcher.add_handler(messege_handler)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
