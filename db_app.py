import psycopg2
import csv

import telegram
from telegram.ext import ConversationHandler

import tg_api

import config


class Postgres:
    FINISH_FAQ_TO_DB, FINISH_MATERIALS_TO_DB, INSERT_FAQ_TO_DB, INSERT_MATERIALS_TO_DB, DELETE_MATERIALS, DELETE_FAQ, \
    UPDATE_PHONEBOOK = range(7)

    def facts_to_str(self, user_data):
        facts = list()
        for key, value in user_data.items():
            facts.append(value)

        return "".join(facts)

    @staticmethod
    def faq_choice(bot, update):
        user_id = update.message.from_user['id']
        participant_list = tg_api.participants['users']
        if user_id in participant_list:
            with psycopg2.connect(f"dbname=telebot user=postgres password={config.PASS}") as conn:
                with conn.cursor() as cur:
                    cur.execute("""SELECT problem, decision FROM faq""")
                    res = cur.fetchall()
                    message = ''
                    for i in enumerate(res):
                        string = f'*{str(i[0] + 1)}.* *Проблема:*  {i[1][0]}\n    *Решение:*  {i[1][1]}\n'
                        message += string
                    update.message.reply_text(message, parse_mode=telegram.ParseMode.MARKDOWN)

            return ConversationHandler.END
        else:
            update.message.reply_text(
                '***AUTH PARTICIPANT: FAILED***')

    @staticmethod
    def materials_choice(bot, update):
        user_id = update.message.from_user['id']
        participant_list = tg_api.participants['users']
        if user_id in participant_list:
            with psycopg2.connect(f"dbname=telebot user=postgres password={config.PASS}") as conn:
                with conn.cursor() as cur:
                    cur.execute("""SELECT description, url FROM materials""")
                    res = cur.fetchall()
                    message = ''
                    for i in enumerate(res):
                        string = f'*\n{str(i[0] + 1)}.* *{i[1][0]}:* {i[1][1]}'
                        message += string
                    update.message.reply_text(message, parse_mode=telegram.ParseMode.MARKDOWN)

            return ConversationHandler.END
        else:
            update.message.reply_text(
                '***AUTH PARTICIPANT: FAILED***')

    @staticmethod
    def received_contact(bot, update, user_data):
        text = update.message.text
        with psycopg2.connect(f"dbname=telebot user=postgres password={config.PASS}") as conn:
            with conn.cursor() as cur:
                cur.execute("""SELECT Подразделение, Должность, ФИО, Телефон, Вн, Почта FROM phonebook 
                               WHERE ФИО ILIKE '%%%s%%'""" % (text,), )
                res = cur.fetchall()
                if len(res) > 3:
                    update.message.reply_text(f'Уточни запрос, найдено записей: {len(res)}')
                elif len(res) != 0:
                    for i in res:
                        update.message.reply_text(f'\n{i[0]}\n{i[1]}\n*{i[2]}*\n{i[3]} доб.{i[4]}\n{i[5]}',
                                                  parse_mode=telegram.ParseMode.MARKDOWN)
                else:
                    update.message.reply_text(
                        f'По запросу "{text}" совпадений не найдено')
                user_data.clear()

        return ConversationHandler.END

    @staticmethod
    def insert_faq_to_db(bot, update, user_data):
        text = update.message.text
        user_data['decision'] = text
        with psycopg2.connect(f"dbname=telebot user=postgres password={config.PASS}") as conn:
            with conn.cursor() as cur:
                cur.execute("""INSERT INTO faq (problem, decision) VALUES (%s, %s) RETURNING problem, decision""",
                            (user_data['problem'],
                             user_data['decision']))
                res = cur.fetchall()
                update.message.reply_text(
                    f'Всё ОК!\nПроблема: {res[0][0]}\nРешение: {res[0][1]}')
        user_data.clear()

        return ConversationHandler.END

    @staticmethod
    def insert_materials_to_db(bot, update, user_data):
        text = update.message.text
        user_data['url'] = text
        with psycopg2.connect(f"dbname=telebot user=postgres password={config.PASS}") as conn:
            with conn.cursor() as cur:
                cur.execute("""INSERT INTO materials (description, url) VALUES (%s, %s) RETURNING description, url""",
                            (user_data['description'],
                             user_data['url']))
                res = cur.fetchall()
                update.message.reply_text(
                    f'Всё ОК!\nМатериал: {res[0][0]}\nСсылка: {res[0][1]}')
        user_data.clear()

        return ConversationHandler.END

    @staticmethod
    def delete_faq_from_db_1(bot, update, user_data):
        text = update.message.text
        user_data['choice'] = text
        with psycopg2.connect(f"dbname=telebot user=postgres password={config.PASS}") as conn:
            with conn.cursor() as cur:
                cur.execute("""DELETE FROM faq WHERE problem = %s RETURNING problem""",
                            (user_data['choice'],))
                res = cur.fetchall()
                if len(res) != 0:
                    update.message.reply_text(
                        f'Удалена запись: {res[0][0]}')
                else:
                    update.message.reply_text(
                        f"Такой проблемы в базе не сущетствует:\n{user_data['choice']}")
        user_data.clear()

        return ConversationHandler.END

    @staticmethod
    def delete_materials_from_db(bot, update, user_data):
        text = update.message.text
        user_data['choice'] = text
        with psycopg2.connect(f"dbname=telebot user=postgres password={config.PASS}") as conn:
            with conn.cursor() as cur:
                cur.execute("""DELETE FROM materials WHERE description = %s RETURNING description""",
                            (user_data['choice'],))
                res = cur.fetchall()
                if len(res) != 0:
                    update.message.reply_text(
                        f'Удалена запись: {res[0][0]}')
                else:
                    update.message.reply_text(
                        f"Такого материала в базе не существует:\n{user_data['choice']}")
        user_data.clear()

        return ConversationHandler.END

    @staticmethod
    def download_and_update_phonebook(bot, update, user_data):
        file_id = update.message.document.file_id
        bot.get_file(file_id).download('MSR_MO_IT.csv')
        contacts_arr = list()
        with open('MSR_MO_IT.csv', 'r', newline='') as file:
            reader = csv.reader(file)
            i = 0
            while i == 0:
                first_symbol = file.readline(1)
                if first_symbol == '№':
                    file.readline()
                    i = 1
            for row in reader:
                str = ''.join(row)
                cur_arr = str.split(';')
                contacts_arr.extend([cur_arr])
        with psycopg2.connect(f"dbname=telebot user=postgres password={config.PASS}") as conn:
            with conn.cursor() as cur:
                cur.execute("""TRUNCATE TABLE phonebook RESTART IDENTITY""")
                count = 0
                for i in contacts_arr:
                    cur.execute("""INSERT INTO phonebook (Подразделение, Должность, ФИО, Телефон, Вн, Комн, Почта)
                                               values (%s, %s, %s, %s, %s, %s, %s) returning ФИО""", tuple(i[3: 10]))
                    res = cur.fetchall()
                    count += len(res)
                update.message.reply_text(
                    f'Загружено контактов: {count}')

        return ConversationHandler.END
