from telethon import TelegramClient, sync
from telethon.tl import functions
from telethon.tl.types import ChannelParticipantsAdmins
import asyncio
import config
import re


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

    @staticmethod
    async def get_invite_link():
        async with TelegramClient('session_start', config.TG_API_ID, config.TG_API_HASH) as client:
            result = await client(functions.messages.ExportChatInviteRequest(peer=config.CHAT_ID))
            chat_invite_export = result.stringify()
            regex = r"https:\//[a-zA-Z1-90./]+"
            matches = re.search(regex, chat_invite_export)
            invite_link = matches.group()

            return invite_link


loop = asyncio.get_event_loop()
participants = loop.run_until_complete(Telethon.get_participants())
invite_link = loop.run_until_complete(Telethon.get_invite_link())
