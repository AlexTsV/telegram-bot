#!/usr/bin/env python
# -*- coding: utf-8 -*-

from telegram import ReplyKeyboardMarkup
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, RegexHandler,
                          ConversationHandler)
import psycopg2
import logging

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

CHOOSING, TYPING_REPLY, TYPING_CHOICE = range(3)

reply_keyboard = [['FAQ', 'Полезные материалы'],
                  ['Телефонная книга МСР МО'],
                  ['Готово!']]
markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)

faq_reply = [['1C', 'AlterOS'], ['Готово']]
faq_markup = ReplyKeyboardMarkup(faq_reply, one_time_keyboard=True)


def facts_to_str(user_data):
    facts = list()
    for key, value in user_data.items():
        facts.append('{}'.format(value))

    return "".join(facts)


def start(bot, update):
    update.message.reply_text(
        "Привет, выбери раздел",
        reply_markup=markup)

    return CHOOSING


def phonebook_choice(bot, update, user_data):
    text = update.message.text
    user_data['choice'] = text
    update.message.reply_text(
        'Введи фамилию или имя')

    return TYPING_REPLY


def faq_choice(bot, update, user_data):
    update.message.reply_text(
        "Выбери раздел",
        reply_markup=faq_markup)

    return CHOOSING


def faq_alteros_choice(bot, update, user_data):
    text = update.message.text
    user_data['choice'] = text
    with psycopg2.connect("dbname=telebot user=postgres password=123") as conn:
        with conn.cursor() as cur:
            cur.execute("""SELECT * FROM materials""")
            res = cur.fetchall()
            message = ''
            for i in res:
                message = message + str(i[0]) + '. ' + i[1] + ' ' + i[2] + ' ' + '\n'
            update.message.reply_text(message)

    return ConversationHandler.END


def faq_1c_choice(bot, update, user_data):
    text = update.message.text
    user_data['choice'] = text
    with psycopg2.connect("dbname=telebot user=postgres password=123") as conn:
        with conn.cursor() as cur:
            cur.execute("""SELECT * FROM materials""")
            res = cur.fetchall()
            message = ''
            for i in res:
                message = message + str(i[0]) + '. ' + i[1] + ' ' + i[2] + ' ' + '\n'
            update.message.reply_text(message)

    return ConversationHandler.END


def materials_choice(bot, update, user_data):
    text = update.message.text
    user_data['choice'] = text
    with psycopg2.connect("dbname=telebot user=postgres password=123") as conn:
        with conn.cursor() as cur:
            cur.execute("""SELECT * FROM materials""")
            res = cur.fetchall()
            message = ''
            for i in res:
                message = message + str(i[0]) + '. ' + i[1] + ' ' + i[2] + ' ' + '\n'
            update.message.reply_text(message)

    return ConversationHandler.END


def received_contact(bot, update, user_data):
    text = update.message.text
    category = user_data['choice']
    user_data[category] = text
    del user_data['choice']
    with psycopg2.connect("dbname=telebot user=postgres password=123") as conn:
        with conn.cursor() as cur:
            cur.execute("""SELECT * FROM phonebook WHERE ФИО ILIKE '%%%s%%'""" % (facts_to_str(user_data),))
            res = cur.fetchall()
            if len(res) > 3:
                update.message.reply_text(f'Уточни запрос, найдено {len(res)} записей')
            elif len(res) != 0:
                for i in res:
                    update.message.reply_text(f'\n{i[1]}\n{i[2]}\n{i[3]}\n{i[4]} доб.{i[5]}\n{i[7]}')
            else:
                update.message.reply_text(f'По запросу "{facts_to_str(user_data)}" совпадений не найдено')
            user_data.clear()
            return ConversationHandler.END


def done(bot, update, user_data):
    if 'choice' in user_data:
        del user_data['choice']

    update.message.reply_text("До встречи!")

    user_data.clear()
    return ConversationHandler.END


def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)


def main():
    # Create the Updater and pass it your bot's token.
    updater = Updater("758306079:AAEAL86jzh6_eowV8Ay6gTQ2cLUmNIrbujk")

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # Add conversation handler with the states GENDER, PHOTO, LOCATION and BIO
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],

        states={
            CHOOSING: [RegexHandler('^(Телефонная книга МСР МО)$', phonebook_choice, pass_user_data=True),
                       RegexHandler('^(FAQ)$', faq_choice, pass_user_data=True),
                       RegexHandler('^(Полезные материалы)$', materials_choice, pass_user_data=True),
                       RegexHandler('^(AlterOS)$', faq_alteros_choice, pass_user_data=True),
                       RegexHandler('^(1C)$', faq_1c_choice, pass_user_data=True),],

            TYPING_CHOICE: [MessageHandler(Filters.text,
                                           phonebook_choice,
                                           pass_user_data=True),
                            ],

            TYPING_REPLY: [MessageHandler(Filters.text,
                                          received_contact,
                                          pass_user_data=True,
                                          ),
                           ],
        },

        fallbacks=[RegexHandler('^Готово!$', done, pass_user_data=True)]
    )

    dp.add_handler(conv_handler)

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
