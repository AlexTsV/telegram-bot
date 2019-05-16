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

CHOOSING, TYPING_REPLY, INSERT_FAQ_TO_DB, INSERT_MATERIALS_TO_DB = range(4)

reply_keyboard = [['Телефонная книга МСР МО'],
                  ['FAQ', 'Полезные материалы'],
                  ['Пригласить участника', 'Выход']]
markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)


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


def send_invite(bot, update):
    update.message.reply_text('Ссылка-приглашение для новых участников: https://t.me/joinchat/CmGDh0PVJZRdJjuqcK5C8A')

    return ConversationHandler.END


def phonebook_choice(bot, update, user_data):
    text = update.message.text
    user_data['choice'] = text
    update.message.reply_text(
        'Введи фамилию или имя')

    return TYPING_REPLY


def faq_choice(bot, update, user_data):
    text = update.message.text
    user_data['choice'] = text
    with psycopg2.connect("dbname=telebot user=postgres password=123") as conn:
        with conn.cursor() as cur:
            cur.execute("""SELECT * FROM faq""")
            res = cur.fetchall()
            message = ''
            for i in res:
                message = message + str(i[0]) + '. ' + i[1] + '\n' + 'Решение: ' + i[2] + ' ' + '\n'
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
                message = message + str(i[0]) + '. ' + i[1] + ':' + ' ' + i[2] + ' ' + '\n'
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


def add_faq(bot, update, user_data):
    text = update.message.text
    user_data['choice'] = text
    update.message.reply_text(
        "Опиши проблему", )

    return INSERT_FAQ_TO_DB


def insert_faq_to_db(bot, update, user_data):
    text = update.message.text
    user_data['choice'] = text
    with psycopg2.connect("dbname=telebot user=postgres password=123") as conn:
        with conn.cursor() as cur:
            cur.execute("""INSERT INTO faq (problem, decision) values (%s, %s)""", (text, 'test'))

    return ConversationHandler.END


def add_materials(bot, update, user_data):
    text = update.message.text
    user_data['choice'] = text
    update.message.reply_text(
        "Отправь краткое описание материала", )

    return INSERT_MATERIALS_TO_DB


def insert_materials_to_db(bot, update, user_data):
    text = update.message.text
    user_data['choice'] = text
    with psycopg2.connect("dbname=telebot user=postgres password=123") as conn:
        with conn.cursor() as cur:
            cur.execute("""INSERT INTO materials (description, url) values (%s, %s)""", (text, 'test'))

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
    updater = Updater("758306079:AAEAL86jzh6_eowV8Ay6gTQ2cLUmNIrbujk")

    dp = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start), CommandHandler('add_faq', add_faq, pass_user_data=True),
                      CommandHandler('add_mat', add_materials, pass_user_data=True)],

        states={
            CHOOSING: [RegexHandler('^(Телефонная книга МСР МО)$', phonebook_choice, pass_user_data=True),
                       RegexHandler('^(FAQ)$', faq_choice, pass_user_data=True),
                       RegexHandler('^(Полезные материалы)$', materials_choice, pass_user_data=True),
                       RegexHandler('^(Пригласить участника)$', send_invite, pass_user_data=False),
                       ],

            INSERT_FAQ_TO_DB: [MessageHandler(Filters.text,
                                              insert_faq_to_db,
                                              pass_user_data=True),
                               ],

            INSERT_MATERIALS_TO_DB: [MessageHandler(Filters.text,
                                                    insert_materials_to_db,
                                                    pass_user_data=True),
                                     ],

            TYPING_REPLY: [MessageHandler(Filters.text,
                                          received_contact,
                                          pass_user_data=True,
                                          ),
                           ],
        },

        fallbacks=[RegexHandler('^Выход$', done, pass_user_data=True)]
    )

    dp.add_handler(conv_handler)

    # log all errors
    dp.add_error_handler(error)

    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()
