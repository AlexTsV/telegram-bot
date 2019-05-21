import psycopg2
import csv
from telegram.ext import (ConversationHandler)


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
        with psycopg2.connect("dbname=telebot user=postgres password=123") as conn:
            with conn.cursor() as cur:
                cur.execute("""SELECT * FROM faq""")
                res = cur.fetchall()
                message = ''
                for i in enumerate(res):
                    message = message + str(i[0] + 1) + '. ' + i[1][1] + '\n' + 'Решение: ' + i[1][2] + ' ' + '\n'
                update.message.reply_text(message)

        return ConversationHandler.END

    @staticmethod
    def materials_choice(bot, update):
        with psycopg2.connect("dbname=telebot user=postgres password=123") as conn:
            with conn.cursor() as cur:
                cur.execute("""SELECT * FROM materials""")
                res = cur.fetchall()
                message = ''
                for i in enumerate(res):
                    message = message + str(i[0] + 1) + '. ' + i[1][1] + ':' + ' ' + i[1][2] + ' ' + '\n'
                update.message.reply_text(message)

        return ConversationHandler.END

    @staticmethod
    def received_contact(bot, update, user_data):
        text = update.message.text
        with psycopg2.connect("dbname=telebot user=postgres password=123") as conn:
            with conn.cursor() as cur:
                cur.execute("""SELECT * FROM phonebook WHERE ФИО ILIKE '%%%s%%'""" % (text,), )
                res = cur.fetchall()
                if len(res) > 3:
                    update.message.reply_text(f'Уточни запрос, найдено {len(res)} записей')
                elif len(res) != 0:
                    for i in res:
                        update.message.reply_text(f'\n{i[1]}\n{i[2]}\n{i[3]}\n{i[4]} доб.{i[5]}\n{i[7]}')
                else:
                    update.message.reply_text(
                        f'По запросу "{text}" совпадений не найдено')
                user_data.clear()

        return ConversationHandler.END

    @staticmethod
    def insert_faq_to_db(bot, update, user_data):
        text = update.message.text
        user_data['decision'] = text
        with psycopg2.connect("dbname=telebot user=postgres password=123") as conn:
            with conn.cursor() as cur:
                cur.execute("""INSERT INTO faq (problem, decision) values (%s, %s) returning problem, decision""",
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
        with psycopg2.connect("dbname=telebot user=postgres password=123") as conn:
            with conn.cursor() as cur:
                cur.execute("""INSERT INTO materials (description, url) values (%s, %s) returning description, url""",
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
        with psycopg2.connect("dbname=telebot user=postgres password=123") as conn:
            with conn.cursor() as cur:
                cur.execute("""DELETE FROM faq WHERE problem = %s returning problem""",
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
        with psycopg2.connect("dbname=telebot user=postgres password=123") as conn:
            with conn.cursor() as cur:
                cur.execute("""DELETE FROM materials WHERE description = %s returning description""",
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
        with psycopg2.connect(dbname='telebot', user='postgres', password='123') as conn:
            with conn.cursor() as cur:
                cur.execute("""delete from phonebook""")
                count = 0
                for i in contacts_arr:
                    cur.execute("""insert into phonebook (Подразделение, Должность, ФИО, Телефон, Вн, Комн, Почта)
                                               values (%s, %s, %s, %s, %s, %s, %s) returning ФИО""",
                                (i[3], i[4], i[5], i[6], i[7], i[8], i[9],))
                    res = cur.fetchall()
                    count += len(res)
                update.message.reply_text(
                    f'Загружено контактов: {count}')

        return ConversationHandler.END

    @staticmethod
    def get_members():
        with psycopg2.connect(dbname='telebot', user='postgres', password='123') as conn:
            with conn.cursor() as cur:
                cur.execute("""select user_id from members where user_role = 'user'""")
                res = cur.fetchall()

                return res