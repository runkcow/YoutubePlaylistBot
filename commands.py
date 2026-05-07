
import discord 
from discord import app_commands

from bot import GUILD_LIST, tree, client
import database as Database
from youtube_api import create_playlist
from eventhook import start_update_playlist

def construct_playlist_url (playlist_id: str) -> str:
    return f"https://www.youtube.com/playlist?list={playlist_id}"

async def channel_auto_complete(interaction: discord.Interaction, current: str) -> list[app_commands.Choice]:
    search = current.lower()
    choices = []
    for cid in Database.get_channels():
        ch = interaction.guild.get_channel(cid)
        if not ch:
            continue
        if search in ch.name.lower():
            choices.append(app_commands.Choice(name=ch.name, value=str(cid)))
        if len(choices) >= 25:
            break
    return choices

@tree.command(name="addchannel", description="Add channel to tracking", guilds=GUILD_LIST)
@discord.app_commands.describe(
    channel="Channel to add"
)
async def add_channel(interaction: discord.Interaction, channel: discord.TextChannel):
    # TODO: create playlist and add to database
    playlist_id = Database.get_channel_playlist(channel.id)
    if playlist_id is None:
        success, playlist_id = await create_playlist(f'{channel.name} | {channel.guild.name}', f'{channel.name} | {channel.guild.name}')
        if not success:
            print(playlist_id)
            await interaction.response.send_message(playlist_id, ephemeral=True)
            return
    if not Database.add_channel(channel.id, playlist_id):
        await interaction.response.send_message(f'Channel {channel.name} already added: {playlist_id}', ephemeral=True)
    else:
        await interaction.response.send_message(f'Channel {channel.name} added: {playlist_id}', ephemeral=True)
    start_update_playlist(channel.id)

@tree.command(name="removechannel", description="Remove channel from tracking", guilds=GUILD_LIST)
@app_commands.autocomplete(channel_id_str=channel_auto_complete)
@discord.app_commands.describe(channel_id_str="Channel to remove")
async def remove_channel(interaction: discord.Interaction, channel_id_str: str):
    channel_id = int(channel_id_str)
    channel = client.get_channel(channel_id)
    if Database.remove_channel(channel_id):
        await interaction.response.send_message(f'Channel {channel.name} has been removed from tracking', ephemeral=True)
    else:
        await interaction.response.send_message(f'Failed to remove channel {channel.name} from tracking', ephemeral=True)

# TODO: add playlist rebuild for a channel
#       not implementing because it is a heavy load on the quota
#       and technically unnecessary

@tree.command(name="getchannelplaylist", description="Send channel's playlist url", guilds=GUILD_LIST)
@app_commands.autocomplete(channel_id_str=channel_auto_complete)
@discord.app_commands.describe(channel_id_str="Channel")
async def get_channel_playlist(interaction: discord.Interaction, channel_id_str: str):
    channel_id = int(channel_id_str)
    channel = client.get_channel(channel_id)
    start_update_playlist(channel_id)
    await interaction.response.send_message(f'Channel {channel.name} playlist: {construct_playlist_url(Database.get_channel_playlist(channel_id))}', ephemeral=True)
