from telethon import TelegramClient, sync
from telethon.tl.types import ChannelParticipantsAdmins
import asyncio

api_id = 780919
api_hash = '5e4ebadc59ba54fc060dd575a0775b92'
some_entity = 'https://t.me/joinchat/E5vPV0PVJZTSiPhGUCKVLw'


async def get_admin_list():
    async with TelegramClient('session_name', api_id, api_hash) as client:
        await client.start()
        entity = await client.get_entity(some_entity)
        admins = client.iter_participants(entity, filter=ChannelParticipantsAdmins)
        admin_list = list()
        async for admin in admins:
            admin_list.append(admin.id)

        return admin_list


# async def get_member_list():
#     async with TelegramClient('session_name', api_id, api_hash) as client:
#         await client.start()
#         users = await client.get_participants(some_entity)
#         member_list = list()
#         async for user in users:
#             member_list.append(user.id)
#
#         return member_list



loop = asyncio.get_event_loop()
admin_list = loop.run_until_complete(get_admin_list())
# member_list = loop.run_until_complete(loop.run_until_complete(get_member_list()))
