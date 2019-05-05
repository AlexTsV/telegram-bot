TOKEN = '758306079:AAEAL86jzh6_eowV8Ay6gTQ2cLUmNIrbujk'
import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)


def start(bot, update):
    keyboard = [[InlineKeyboardButton("FAQ", callback_data='1'),
                 InlineKeyboardButton("Полезные материалы", callback_data='2')],
                [InlineKeyboardButton("Телефонный справочник МСР МО", callback_data='3')]]

    reply_markup = InlineKeyboardMarkup(keyboard)

    update.message.reply_text('Выбери раздел:', reply_markup=reply_markup)


def button(bot, update):
    query = update.callback_query
    if query.data == '1':
        bot.edit_message_text(text="FAQ",
                              chat_id=query.message.chat_id,
                              message_id=query.message.message_id)
    if query.data == '2':
        bot.edit_message_text(text="Links",
                              chat_id=query.message.chat_id,
                              message_id=query.message.message_id)
    if query.data == '3':
        bot.edit_message_text(text="Введи фамилию для поиска",
                              chat_id=query.message.chat_id,
                              message_id=query.message.message_id)





def help(bot, update):
    update.message.reply_text("Используй /start для работы с ботом.")


def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)


def main():
    # Create the Updater and pass it your bot's token.
    updater = Updater(TOKEN)

    updater.dispatcher.add_handler(CommandHandler('start', start))
    updater.dispatcher.add_handler(CallbackQueryHandler(button))
    updater.dispatcher.add_handler(CommandHandler('help', help))
    updater.dispatcher.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until the user presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT
    updater.idle()


if __name__ == '__main__':
    main()