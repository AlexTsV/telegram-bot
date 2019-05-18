import psycopg2
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, RegexHandler,
                          ConversationHandler)


class Postgres:

    DELETE_MATERIALS, DELETE_FAQ = range(2)

    def del_faq(self, bot, update, user_data):
        text = update.message.text
        user_data['choice'] = text
        update.message.reply_text(
            "Введи точное описание проблемы для удаления из базы", )

        return self.DELETE_MATERIALS

    def del_materials(self, bot, update, user_data):
        text = update.message.text
        user_data['url'] = text
        update.message.reply_text(
            "Введи точное название материала для удаления из базы", )

        return self.DELETE_FAQ

    def delete_faq_from_db(self, bot, update, user_data):
        text = update.message.text
        user_data['choice'] = text
        with psycopg2.connect("dbname=telebot user=postgres password=123") as conn:
            with conn.cursor() as cur:
                cur.execute("""DELETE FROM faq WHERE problem = (%s)""",
                            (user_data['choice']))
                res = cur.fetchall()
                update.message.reply_text(f'Удалена запись: {res[0][0]}')
        user_data.clear()

        return ConversationHandler.END

    def delete_materials_from_db(self, bot, update, user_data):
        text = update.message.text
        user_data['url'] = text
        with psycopg2.connect("dbname=telebot user=postgres password=123") as conn:
            with conn.cursor() as cur:
                cur.execute("""DELETE FROM materials WHERE description = %s""",
                            (user_data['choice'],))
                res = cur.fetchall()
                update.message.reply_text(f'Удалена запись: {res[0][0]}')
        user_data.clear()

        return ConversationHandler.END