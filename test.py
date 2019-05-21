from telethon import TelegramClient, sync
from telethon.tl.types import ChannelParticipantsAdmins
import psycopg2


def get_members_list():
    api_id =
    api_hash = ''

    with TelegramClient('session_name', api_id, api_hash) as client:
        client.start()
        entity = client.get_entity('ИТ_МСР_МО')
        users = client.get_participants(entity)
        admins = client.iter_participants(entity, filter=ChannelParticipantsAdmins)
        admin_list = list()
        for admin in admins:
            admin_list.append(admin.id)
        for user in users:
            with psycopg2.connect("dbname=telebot user=postgres password=123") as conn:
                with conn.cursor() as cur:
                    if user.id in admin_list:
                        cur.execute("""INSERT INTO members (user_id, user_role) values (%s, %s)""",
                                    (user.id, 'admin'))
                    else:
                        cur.execute("""INSERT INTO members (user_id, user_role) values (%s, %s)""",
                                    (user.id, 'user'))



get_members_list()




