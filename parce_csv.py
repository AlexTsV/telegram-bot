import csv
import psycopg2
arr = []
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
        arr.extend([cur_arr])
with psycopg2.connect(dbname='telebot', user='postgres', password='123') as conn:
    with conn.cursor() as cur:
        for ar in arr:
            print(ar)
            cur.execute("""insert into phonebook (Подразделение, Должность, ФИО, Телефон, Вн, Комн, Почта)
                           values (%s, %s, %s, %s, %s, %s, %s)""", (ar[3], ar[4], ar[5], ar[6], ar[7], ar[8], ar[9],))


