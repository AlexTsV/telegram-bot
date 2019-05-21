#!/usr/bin/env python
# -*- coding: utf-8 -*-
from telegram import ReplyKeyboardMarkup
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, RegexHandler, ConversationHandler)
import logging
from add_rm_db import Postgres
import test
import asyncio

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

CHOOSING, TYPING_REPLY, Postgres.INSERT_FAQ_TO_DB, Postgres.INSERT_MATERIALS_TO_DB, Postgres.FINISH_FAQ_TO_DB, \
Postgres.FINISH_MATERIALS_TO_DB, Postgres.DELETE_FAQ, Postgres.DELETE_MATERIALS, Postgres.UPDATE_PHONEBOOK = range(9)

reply_keyboard = [['Телефонная книга МСР МО'],
                  ['FAQ', 'Полезные материалы'],
                  ['Пригласить участника', 'Выход']]

markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)


def start(bot, update):
    user_id = update.message.from_user['id']
    member_id_list = asyncio.get_event_loop().run_until_complete(test.get_members_list())
    print(member_id_list)
    if user_id in member_id_list:
        update.message.reply_text(
            "Привет, выбери раздел",
            reply_markup=markup)

        return CHOOSING
    else:
        update.message.reply_text(
            'Извини ты не состоишь в группе ИТ_МСР_МО')

admin_list = ['Alex_tvv']


def add_faq(bot, update, user_data):
    if update.message.from_user['username'] in admin_list:
        if len(user_data) == 0:
            text = update.message.text
            user_data['decision'] = text
            update.message.reply_text(
                "Опиши проблему", )

            return Postgres.FINISH_FAQ_TO_DB
        else:
            text = update.message.text
            user_data['problem'] = text
            update.message.reply_text(
                "Опиши решение", )

            return Postgres.INSERT_FAQ_TO_DB
    else:
        update.message.reply_text('Извини, ты должен быть админом')


def add_materials(bot, update, user_data):
    if len(user_data) == 0:
        text = update.message.text
        user_data['url'] = text
        update.message.reply_text(
            "Введи название материала", )

        return Postgres.FINISH_MATERIALS_TO_DB
    else:
        text = update.message.text
        user_data['description'] = text
        update.message.reply_text(
            "Пришли ссылку на материал", )

        return Postgres.INSERT_MATERIALS_TO_DB


def del_faq(bot, update):
    update.message.reply_text(
        "Введи точное описание проблемы для удаления из базы", )

    return Postgres.DELETE_FAQ


def del_materials(bot, update):
    update.message.reply_text(
        "Введи точное название материала для удаления из базы", )

    return Postgres.DELETE_MATERIALS


def send_invite(bot, update):
    update.message.reply_text(
        'Ссылка-приглашение для новых участников: ', )

    return ConversationHandler.END


def phonebook_choice(bot, update):
    update.message.reply_text(
        'Введи фамилию или имя')

    return TYPING_REPLY


def update_phonebook(bot, update):
    update.message.reply_text(
        "Пришли файл в формате 'CSV(разделители - запятые)'", )

    return Postgres.UPDATE_PHONEBOOK


def done(bot, update, user_data):
    if 'choice' in user_data:
        del user_data['choice']

    update.message.reply_text(
        "До встречи!")

    user_data.clear()
    return ConversationHandler.END


def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)


def main():
    updater = Updater("758306079:AAEAL86jzh6_eowV8Ay6gTQ2cLUmNIrbujk")

    dp = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start),
                      CommandHandler('add_faq', add_faq, pass_user_data=True),
                      CommandHandler('add_mat', add_materials, pass_user_data=True),
                      CommandHandler('del_faq', del_faq, pass_user_data=False),
                      CommandHandler('del_mat', del_materials, pass_user_data=False),
                      CommandHandler('update_pb', update_phonebook, pass_user_data=False)],

        states={
            CHOOSING: [RegexHandler('^(Телефонная книга МСР МО)$', phonebook_choice, pass_user_data=False),
                       RegexHandler('^(FAQ)$', Postgres.faq_choice, pass_user_data=False),
                       RegexHandler('^(Полезные материалы)$', Postgres.materials_choice, pass_user_data=False),
                       RegexHandler('^(Пригласить участника)$', send_invite, pass_user_data=False),
                       ],

            TYPING_REPLY: [MessageHandler(Filters.text,
                                          Postgres.received_contact,
                                          pass_user_data=True,
                                          ),
                           ],

            Postgres.FINISH_MATERIALS_TO_DB: [MessageHandler(Filters.text,
                                                             add_materials,
                                                             pass_user_data=True),
                                              ],

            Postgres.FINISH_FAQ_TO_DB: [MessageHandler(Filters.text,
                                                       add_faq,
                                                       pass_user_data=True),
                                        ],

            Postgres.INSERT_FAQ_TO_DB: [MessageHandler(Filters.text,
                                                       Postgres.insert_faq_to_db,
                                                       pass_user_data=True),
                                        ],

            Postgres.INSERT_MATERIALS_TO_DB: [MessageHandler(Filters.text,
                                                             Postgres.insert_materials_to_db,
                                                             pass_user_data=True),
                                              ],

            Postgres.DELETE_FAQ: [MessageHandler(Filters.text,
                                                 Postgres.delete_faq_from_db_1,
                                                 pass_user_data=True,
                                                 ),
                                  ],

            Postgres.DELETE_MATERIALS: [MessageHandler(Filters.text,
                                                       Postgres.delete_materials_from_db,
                                                       pass_user_data=True,
                                                       ),
                                        ],

            Postgres.UPDATE_PHONEBOOK: [MessageHandler(Filters.document,
                                                       Postgres.download_and_update_phonebook,
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
