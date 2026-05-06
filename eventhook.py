
import discord
import asyncio

from bot import client
import config as Config
import database as Database
from youtube_api import extract_video_id, add_playlist_video

@client.event
async def on_message(message: discord.Message):
    if message.author.bot:
        return
    if message.channel.id not in Database.get_channels():
        return
    start_update_playlist(message.channel.id)

busy_channels = set()

def start_update_playlist(channel_id: int):
    asyncio.create_task(_update_playlist_wrapper(channel_id))

async def _update_playlist_wrapper(channel_id: int):
    if channel_id in busy_channels:
        return
    busy_channels.add(channel_id)
    try:
        await _update_playlist(channel_id)
    finally:
        busy_channels.remove(channel_id)

async def _update_playlist(channel_id: int):
    playlist_id = Database.get_channel_playlist(channel_id)
    if playlist_id is None:
        print(f'Error @ update_playlist | Playlist not found')
        return
    last_message_id = Database.get_channel_last_message(channel_id)
    after = discord.Object(id=last_message_id) if last_message_id else None
    async for message in client.get_channel(channel_id).history(limit=None, oldest_first=True, after=after):
        if message.author.bot:
            continue
        for word in message.content.split():
            video_id = extract_video_id(word)
            if video_id is not None:
                success, msg = await add_playlist_video(playlist_id, video_id)
                if success:
                    Database.add_playlist_video(channel_id, video_id)
                else:
                    print(msg)
                    return
        Database.update_channel_last_message(channel_id, message.id)
