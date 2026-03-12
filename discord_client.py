
import discord

class DiscordClient(discord.Client):
    async def setup_hook(self):
        return await super().setup_hook()
    
    async def close(self):
        await super().close()