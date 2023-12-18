from __future__ import annotations

import json
import random
import asyncio
import sqlite3

from concurrent.futures import ThreadPoolExecutor
from os import path, PathLike
from typing import Union

import disnake
from disnake.ext import commands

from juliabot.memesgen import demotivator_render
from juliaai import JuliaAIAPI, BidirectionalLSTM_EmojiClassifier
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
        self.BidirectionalLSTM_EmojiClassifier: BidirectionalLSTM_EmojiClassifier = BidirectionalLSTM_EmojiClassifier()

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction: disnake.Reaction, user: disnake.Member) -> None:
        emoji = reaction.emoji
        if user.bot:
            return
        print(f'[DEBUG_EMOJI]\tLoaded emoji `{emoji}`\tjulia_api.on_reaction_add')
        if emoji == '🥶':
            emoji_dataset: list[dict] = [{"text": reaction.message.content, "emoji": 1}]
            try:
                with open('emojis.json', 'r', encoding='utf-8') as fileIOemojisR:
                    existing_data = json.load(fileIOemojisR)
            except json.decoder.JSONDecodeError:
                existing_data = []
            existing_data.extend(emoji_dataset)
            with open('emojis.json', 'w', encoding='utf-8') as fileIOemojisW:
                json.dump(existing_data, fileIOemojisW, ensure_ascii=False, indent=4)
        await reaction.message.add_reaction(emoji)

    @commands.Cog.listener()
    async def on_message(self, message: disnake.Message = None) -> None:
        if message.author == self.bot.user:
            return
        
        is_message_reacted = self.BidirectionalLSTM_EmojiClassifier.get_response([message.content])
        if is_message_reacted[0]:
            await message.add_reaction('🥶')
        
        if message.reference:
            referenced_message = await message.channel.fetch_message(message.reference.message_id)
            self.julia_api.train(referenced_message.content, message.content)
        if self.bot.user.mentioned_in(message) or isinstance(message.channel, disnake.DMChannel):
            await message.reply(self.julia_api.response(message.content))
        await self.bot.process_commands(message)

    @commands.slash_command(description="You can write SQL code in Discord, BE CAUTIOUS")
    async def sqlin(self, interaction: disnake.ApplicationCommandInteraction = None,
                           code: str = None) -> None:
        await interaction.response.defer()
        if not code or not interaction.author.guild_permissions.administrator:
            await interaction.edit_original_response('It seems you don\'t have the specified channel, or you don\'t have the permission to parse the Discord channel `channel`\n You can learn more in the `>help` menu')
            return
        async with interaction.channel.typing():
            await asyncio.sleep(1)
        if not path.exists('db.sqlite3'):
            return
        try:
            connection = sqlite3.connect('db.sqlite3')
            cursor = connection.cursor()
            cursor.execute(code)
            execute_output = cursor.fetchone()[0]
        except Exception as e:
            await interaction.edit_original_response(f'*Input SQL code*\n```sql\n{code}```\n*Output*\n```bash\n> {e}\n```')
            cursor.close()
            connection.close()
            return
        cursor.close()
        connection.close()
        await interaction.edit_original_response(f'*Input SQL code*\n```sql\n{code}\n```\n*Output*\n```bash\n> {execute_output}\n```')

    @commands.slash_command(description="You can parse data from the chat with the required number of messages for parsing")
    async def parsechannel(self, interaction: disnake.ApplicationCommandInteraction = None,
                           channel: disnake.TextChannel = None,
                           amount: int = 2) -> None:
        await interaction.response.defer()
        if not channel or not interaction.author.guild_permissions.administrator or amount > 5000:
            await interaction.edit_original_response('It seems you don\'t have the specified channel, or you don\'t have the permission to parse the Discord channel `channel`\n You can learn more in the `>help` menu')
            return
        emoji_dataset: list[dict] = []
        async for message in channel.history(limit=int(amount)):
            has_cold_face_reaction = any(reaction.emoji == '🥶' for reaction in message.reactions)
            emoji_dataset.append({
                "text": message.content,
                "emoji": 1 if has_cold_face_reaction else 0})
            if message.type == disnake.MessageType.reply:
                async with interaction.channel.typing():
                    await asyncio.sleep(2)
                try:
                    replied_message = await channel.fetch_message(message.reference.message_id)
                    self.julia_api.train(replied_message.content, message.content)
                except Exception as e:
                    pass
                await interaction.edit_original_response(content=f'{interaction.user.mention} trained the neural network on the {channel.mention} channel, and now you can communicate as in the channel from `{amount}` messages\nYou can learn more by typing the command `?help` for more information')
        try:
            with open('emojis.json', 'r', encoding='utf-8') as fileIOemojisR:
                existing_data = json.load(fileIOemojisR)
        except json.decoder.JSONDecodeError:
            existing_data = []
        existing_data.extend(emoji_dataset)
        with open('emojis.json', 'w', encoding='utf-8') as fileIOemojisW:
            json.dump(existing_data, fileIOemojisW, ensure_ascii=False, indent=4)

    @commands.slash_command(description="You can create a demotivator for yourself on any topic you want and with any person you like")
    async def demotivator(self, interaction: disnake.ApplicationCommandInteraction = None,
                          member: disnake.Member = None,
                          title: str = None) -> None:
        await interaction.response.defer()
        if not member or not title:
            await interaction.edit_original_response("You did not specify a user or a topic for which you want to create a demotivator\nFor more commands, refer to our menu using `?help`")
            return
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
        cursor.close()
        connection.close()
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
    
    @commands.slash_command(description="You can train the BidirectionalLSTM_EmojiClassifier")
    async def fitemojis(self, interaction: disnake.ApplicationCommandInteraction = None) -> None:
        await interaction.response.defer()
        self.BidirectionalLSTM_EmojiClassifier.build_examlpe()
        await interaction.edit_original_response('You train the model BidirectionalLSTM_EmojiClassifier\nPlease refer to the `?help` menu for more information')

def setup(bot: commands.Bot = None) -> None:
    bot.add_cog(JuliaAPI(bot))
