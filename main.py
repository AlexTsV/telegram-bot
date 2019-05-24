#!/usr/bin/env python
# -*- coding: utf-8 -*-
import telegram
from telegram import ReplyKeyboardMarkup
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, RegexHandler, ConversationHandler)
import logging
from db_app import Postgres
import config
import tg_api

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

logger = logging.getLogger(__name__)

CHOOSING, TYPING_REPLY, Postgres.INSERT_FAQ_TO_DB, Postgres.INSERT_MATERIALS_TO_DB, Postgres.FINISH_FAQ_TO_DB, \
Postgres.FINISH_MATERIALS_TO_DB, Postgres.DELETE_FAQ, Postgres.DELETE_MATERIALS, Postgres.UPDATE_PHONEBOOK = range(9)

reply_keyboard = [['Телефонная книга МСР МО'],
                  ['Пригласить участника', 'Полезные материалы'],
                  ['FAQ', 'Выход']]


def add_faq(bot, update, user_data):
    admin_id = update.message.from_user['id']
    admin_list = tg_api.participants['admins']
    if admin_id in admin_list:
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
        update.message.reply_text('***AUTH ADMIN: FAILED***')


def add_materials(bot, update, user_data):
    admin_id = update.message.from_user['id']
    admin_list = tg_api.participants['admins']
    if admin_id in admin_list:
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
    else:
        update.message.reply_text('***AUTH ADMIN: FAILED***')


def del_faq(bot, update):
    admin_id = update.message.from_user['id']
    if admin_id in tg_api.participants['admins']:
        update.message.reply_text(
            "Введи точное описание проблемы для удаления из базы", )

        return Postgres.DELETE_FAQ
    else:
        update.message.reply_text('***AUTH ADMIN: FAILED***')


def del_materials(bot, update):
    admin_id = update.message.from_user['id']
    admin_list = tg_api.participants['admins']
    if admin_id in admin_list:
        update.message.reply_text(
            "Введи *точное* название материала для удаления из базы", parse_mode=telegram.ParseMode.MARKDOWN)

        return Postgres.DELETE_MATERIALS
    else:
        update.message.reply_text('***AUTH ADMIN: FAILED***')


def send_invite(bot, update):
    user_id = update.message.from_user['id']
    participant_list = tg_api.participants['users']
    if user_id in participant_list:
        update.message.reply_text(
            f'*Ссылка-приглашение для новых участников:* {tg_api.invite_link}', parse_mode=telegram.ParseMode.MARKDOWN)

        return ConversationHandler.END
    else:
        update.message.reply_text(
            '***AUTH PARTICIPANT: FAILED***')


def update_phonebook(bot, update):
    admin_id = update.message.from_user['id']
    admin_list = tg_api.participants['admins']
    if admin_id in admin_list:
        update.message.reply_text(
            "Пришли файл в формате *'CSV(разделители - запятые)'*", parse_mode=telegram.ParseMode.MARKDOWN)

        return Postgres.UPDATE_PHONEBOOK
    else:
        update.message.reply_text('***AUTH ADMIN: FAILED***')


def phonebook_choice(bot, update):
    user_id = update.message.from_user['id']
    participant_list = tg_api.participants['users']
    if user_id in participant_list:
        update.message.reply_text(
            'Введи *фамилию* или *имя*', parse_mode=telegram.ParseMode.MARKDOWN)

        return TYPING_REPLY
    else:
        update.message.reply_text(
            '***AUTH PARTICIPANT: FAILED***')


def done(bot, update, user_data):
    if 'choice' in user_data:
        del user_data['choice']

    update.message.reply_text(
        "***Деактивация...***")

    user_data.clear()
    return ConversationHandler.END


def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)


def main():
    updater = Updater(config.BOT_TOKEN)

    dp = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler('add_faq', add_faq, pass_user_data=True),
            CommandHandler('add_mat', add_materials, pass_user_data=True),
            CommandHandler('del_faq', del_faq, pass_user_data=False),
            CommandHandler('del_mat', del_materials, pass_user_data=False),
            CommandHandler('update_pb', update_phonebook, pass_user_data=False),
            RegexHandler('^FAQ$', Postgres.faq_choice, pass_user_data=False),
            RegexHandler('^Телефонная книга МСР МО$', phonebook_choice, pass_user_data=False),
            RegexHandler('^Полезные материалы$', Postgres.materials_choice, pass_user_data=False),
            RegexHandler('^Пригласить участника$', send_invite, pass_user_data=False),
        ],

        states={

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
