from telethon import TelegramClient, sync
from telethon.tl.types import ChannelParticipantsAdmins, PeerChat
import asyncio
import config


class Telethon:
    @staticmethod
    async def get_participants():
        async with TelegramClient('session_start', config.TG_API_ID, config.TG_API_HASH) as client:
            await client.start()
            entity = await client.get_entity(config.CHAT_ID)
            admins = client.iter_participants(entity, filter=ChannelParticipantsAdmins)
            users = await client.get_participants(entity)
            admin_list = list()
            user_list = list()
            async for admin in admins:
                admin_list.append(admin.id)
            for user in users:
                user_list.append(user.id)

            all_participants_dict = {'admins': admin_list, 'users': user_list}

            return all_participants_dict


loop = asyncio.get_event_loop()
participants = loop.run_until_complete(Telethon.get_participants())
