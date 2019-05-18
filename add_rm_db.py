import psycopg2
from telegram.ext import (ConversationHandler)


class Postgres:
    FINISH_FAQ_TO_DB, FINISH_MATERIALS_TO_DB, INSERT_FAQ_TO_DB, INSERT_MATERIALS_TO_DB, DELETE_MATERIALS, \
    DELETE_FAQ = range(6)

    def add_faq(bot, update, user_data):
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

    def insert_faq_to_db(bot, update, user_data):
        text = update.message.text
        user_data['decision'] = text
        with psycopg2.connect("dbname=telebot user=postgres password=123") as conn:
            with conn.cursor() as cur:
                cur.execute("""INSERT INTO faq (problem, decision) values (%s, %s) returning problem, decision""",
                            (user_data['problem'],
                             user_data['decision']))
                res = cur.fetchall()
                update.message.reply_text(f'Всё ОК!\nПроблема: {res[0][0]}\nРешение: {res[0][1]}')
        user_data.clear()

        return ConversationHandler.END

    def insert_materials_to_db(bot, update, user_data):
        text = update.message.text
        user_data['url'] = text
        with psycopg2.connect("dbname=telebot user=postgres password=123") as conn:
            with conn.cursor() as cur:
                cur.execute("""INSERT INTO materials (description, url) values (%s, %s) returning description, url""",
                            (user_data['description'],
                             user_data['url']))
                res = cur.fetchall()
                update.message.reply_text(f'Всё ОК!\nМатериал: {res[0][0]}\nСсылка: {res[0][1]}')
        user_data.clear()

        return ConversationHandler.END

    def del_faq(bot, update, user_data):
        text = update.message.text
        user_data['choice'] = text
        update.message.reply_text(
            "Введи точное описание проблемы для удаления из базы", )

        return Postgres.DELETE_FAQ

    def del_materials(bot, update, user_data):
        text = update.message.text
        user_data['choice'] = text
        update.message.reply_text(
            "Введи точное название материала для удаления из базы", )

        return Postgres.DELETE_MATERIALS

    def delete_faq_from_db(bot, update, user_data):
        text = update.message.text
        user_data['choice'] = text
        with psycopg2.connect("dbname=telebot user=postgres password=123") as conn:
            with conn.cursor() as cur:
                cur.execute("""DELETE FROM faq WHERE problem = (%s) returning problem""",
                            (user_data['choice'],))
                res = cur.fetchall()
                if len(res) != 0:
                    update.message.reply_text(f'Удалена запись: {res[0][0]}')
                else:
                    update.message.reply_text(f"Проблемы {user_data['choice']} не существует в базе")
        user_data.clear()

        return ConversationHandler.END

    def delete_materials_from_db(bot, update, user_data):
        text = update.message.text
        user_data['choice'] = text
        with psycopg2.connect("dbname=telebot user=postgres password=123") as conn:
            with conn.cursor() as cur:
                cur.execute("""DELETE FROM materials WHERE description = %s returning description""",
                            (user_data['choice'],))
                res = cur.fetchall()
                if len(res) != 0:
                    update.message.reply_text(f'Удалена запись: {res[0][0]}')
                else:
                    update.message.reply_text(f"Материала {user_data['choice']} не существует в базе")
        user_data.clear()

        return ConversationHandler.END
