from __future__ import annotations

import asyncio

import disnake
from disnake.ext import commands

from juliaai.misc import MetaSettings
meta_settings: MetaSettings = MetaSettings


class BotReady(commands.Cog):
    def __init__(self, bot: commands.Bot = None) -> None:
        self.bot: commands.Bot = bot

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        # print(f"ready for {len(self.bot.guilds)}")
        if meta_settings.bot_activity_type == "play":
            await self.bot.change_presence(activity=disnake.Game(
                name=meta_settings.bot_activity))
        elif meta_settings.bot_activity_type == "listen":
            await self.bot.change_presence(activity=disnake.Activity(
                type=disnake.ActivityType.listening,
                name=meta_settings.bot_activity))
        elif meta_settings.bot_activity_type == "watch":
            await self.bot.change_presence(activity=disnake.Activity(
                type=disnake.ActivityType.watching,
                name=meta_settings.bot_activity))
            
    @commands.command()
    async def help(self, message_ctx: disnake.Message = None) -> None:
        async with message_ctx.channel.typing():
            await asyncio.sleep(1)
        await message_ctx.reply('**Chatbot Functionality:**\n`/fitnetwork input: str* output: str*` - trains the neural network to respond (output) to a given question (input).\n`/parsechannel channel: discord.TextChannel* amount: integer=2` - parses and trains the model on the specified channel; you can also specify the number of messages (default is 2 messages).\n\n**Visual Functionality:**\n`/bruh memebr: discord.Member* title: string*` - generates a "bruh" meme with the member\'s photo and a custom title.\n`/demotivator member: discord.Member title: string*` - generates a demotivational poster related to the user and a provided theme.\n\n**Testing and Debugging:**\n`/sizeof` - size of the server\'s database.\n`/countof` - number of rows on which the neural network is trained in the database.\n`/sqlin sqlcode: string*` - executes SQL code directly through the bot to retrieve or delete data. *Be cautious, as it can lead to errors on the server or the neural network and potentially break the global database.*')

def setup(bot: commands.Bot = None) -> None:
    bot.add_cog(BotReady(bot))
