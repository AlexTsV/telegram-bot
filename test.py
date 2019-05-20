from main import TelegramClient, sync

api_id = 780919
api_hash = '5e4ebadc59ba54fc060dd575a0775b92'

client = TelegramClient('session_name', api_id, api_hash)
client.start()

channel = client.get_participants('t.me/E5vPV0PVJZTSiPhGUCKVLw')
print(channel)

# queryKey = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u',
#             'v', 'w', 'x', 'y', 'z']
# all_participants = []
#
# uids = []
# for key in queryKey:
#     offset = 0
#     limit = 200
#     while True:
#         participants = await client(GetParticipantsRequest(
#             channel, ChannelParticipantsSearch(key), offset, limit,
#             hash=0
#         ))
#         if not participants.users:
#             break
#
#         offset += len(participants.users)
#         print(offset)
#
#         for user in participants.users:
#             uids.append(user.id)
#
# uids = sorted(set(uids))