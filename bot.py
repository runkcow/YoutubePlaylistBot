
from discord import app_commands
import discord

import config
from discord_client import DiscordClient

intents = discord.Intents.default()
intents.guilds = True
intents.message_content = True
# client = discord.Client(intents=intents)
client = DiscordClient(intents=intents)
tree = app_commands.CommandTree(client)

GUILD_LIST = [ discord.Object(id=g) for g in config.DEV_SERVERS ]
