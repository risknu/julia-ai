from __future__ import annotations

import random
import asyncio
import sqlite3

from concurrent.futures import ThreadPoolExecutor
from os import path, PathLike
from typing import Union

import disnake
from disnake.ext import commands

from juliabot.memesgen import demotivator_render
from juliaai import JuliaAIAPI
from juliaai.misc import MetaSettings
meta_settings: MetaSettings = MetaSettings

def get_file_size(file_path: Union[str, PathLike] = None) -> tuple:
    if not file_path or not path.exists(file_path):
        return 0, 0
    size_in_bytes = path.getsize(file_path)
    size_in_kb = size_in_bytes / 1024
    return size_in_bytes, size_in_kb


class JuliaAPI(commands.Cog):
    def __init__(self, bot: commands.Bot = None) -> None:
        self.bot: commands.Bot = bot
        self.julia_api: JuliaAIAPI = JuliaAIAPI()

    @commands.slash_command(description="parsechannel")
    async def parsechannel(self, interaction: disnake.ApplicationCommandInteraction = None,
                           channel: disnake.TextChannel = None,
                           amount: int = 2) -> None:
        await interaction.response.defer()
        if not channel or not interaction.author.guild_permissions.administrator or amount > 5000:
            await interaction.edit_original_response('It seems you don\'t have the specified channel, or you don\'t have the permission to parse the Discord channel `channel`\n You can learn more in the `>help` menu')
            return
        async for message in channel.history(limit=int(amount)):
            if message.type == disnake.MessageType.reply:
                async with interaction.channel.typing():
                    asyncio.sleep(2)
                replied_message = await channel.fetch_message(message.reference.message_id)
                self.julia_api.train(replied_message.content, message.content)
                await interaction.edit_original_response(content=f'I trained the neural network on the {channel.mention} channel, and now you can communicate as in the channel from `{amount}` messages\nYou can learn more by typing the command `?help` for more information')

    @commands.slash_command(description="You can create a demotivator for yourself on any topic you want and with any person you like")
    async def demotivator(self, interaction: disnake.ApplicationCommandInteraction = None,
                          member: disnake.Member = None,
                          title: str = None) -> None:
        await interaction.response.defer()
        if not member or not title:
            await interaction.edit_original_response("You did not specify a user or a topic for which you want to create a demotivator\nFor more commands, refer to our menu using `?help`")
        async with interaction.channel.typing():
            await asyncio.sleep(2)
        with ThreadPoolExecutor() as executor:
            image_bytesio = await self.bot.loop.run_in_executor(executor, demotivator_render, member.avatar.url, f'{title}\n{self.julia_api.response(title)}')
        await interaction.edit_original_response(file=disnake.File(image_bytesio, filename=f'{random.randint(100000, 999999)}_demotivator.png'))

    @commands.slash_command(description="You can specify the size of the database in megabytes (MB), gigabytes (GB), or kilobytes (KB)")
    async def sizeof(self, interaction: disnake.ApplicationCommandInteraction = None) -> None:
        await interaction.response.defer()
        async with interaction.channel.typing():
            await asyncio.sleep(1)
        size_in_bytes, size_in_kb = get_file_size('db.sqlite3')
        await interaction.edit_original_response(f'The server database weighs around `{size_in_bytes}B` or `{size_in_kb}KB`\nFor more commands, refer to our menu using `?help`')

    @commands.slash_command(description="You can specify the number of rows for training the neural network")
    async def countof(self, interaction: disnake.ApplicationCommandInteraction = None) -> None:
        await interaction.response.defer()
        async with interaction.channel.typing():
            await asyncio.sleep(1)
        if not path.exists('db.sqlite3'):
            return
        connection = sqlite3.connect('db.sqlite3')
        cursor = connection.cursor()
        query: str = f"SELECT COUNT(*) FROM statement;"
        cursor.execute(query)
        row_count = cursor.fetchone()[0]
        await interaction.edit_original_response(f'The amount of data for training the chatbot is `{row_count}`\nUse our help command `?help` for other commands')

    @commands.slash_command(description="You can train the neural network on your data that you can provide to us")
    async def fitnetwork(self, interaction: disnake.ApplicationCommandInteraction = None,
                         input_sentence: str = None,
                         output_sentence: str = None) -> None:
        await interaction.response.defer()
        if not input_sentence or not output_sentence:
            async with interaction.channel.typing():
                await asyncio.sleep(1)
            await interaction.edit_original_response(f'{interaction.user.mention}, You did not specify one of the parameters for the neural network settings. Please review them and correct your command\nUse the help menu with :: `?help`')
            return
        train_code: bool = self.julia_api.train(input_sentence, output_sentence)
        if not train_code:
            async with interaction.channel.typing():
                await asyncio.sleep(1)
            await interaction.edit_original_response(f'{interaction.user.mention}, You did not specify one of the parameters for the neural network settings. Please review them and correct your command\nUse the help menu with :: `?help`')
            return
        async with interaction.channel.typing():
            await asyncio.sleep(1)
        await interaction.edit_original_response(f'{interaction.user.mention}, You have successfully trained the neural network to respond `{output_sentence}` to the input `{input_sentence}`\nFor more commands, use :: `?help`')
    

def setup(bot: commands.Bot = None) -> None:
    bot.add_cog(JuliaAPI(bot))
