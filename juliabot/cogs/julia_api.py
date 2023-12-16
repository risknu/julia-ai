from __future__ import annotations

import asyncio

import disnake
from disnake.ext import commands

from juliaai import JuliaAIAPI
from juliaai.misc import MetaSettings
meta_settings: MetaSettings = MetaSettings


class JuliaAPI(commands.Cog):
    def __init__(self, bot: commands.Bot = None) -> None:
        self.bot: commands.Bot = bot
        self.julia_api: JuliaAIAPI = JuliaAIAPI()

    @commands.slash_command(description="sizeof")
    async def sizeof(self, interaction: disnake.ApplicationCommandInteraction = None) -> None:
        await interaction.send('sizeof')

    @commands.slash_command(description="countof")
    async def countof(self, interaction: disnake.ApplicationCommandInteraction = None) -> None:
        await interaction.send('countof')

    @commands.slash_command(description="fitnetwork")
    async def fitnetwork(self, interaction: disnake.ApplicationCommandInteraction = None,
                         input_sentence: str = None,
                         output_sentence: str = None) -> None:
        await interaction.response.defer()
        if not input_sentence or not output_sentence:
            async with interaction.channel.typing():
                await asyncio.sleep(1)
            interaction.edit_original_response(f'{interaction.user.mention}, You did not specify one of the parameters for the neural network settings. Please review them and correct your command\nUse the help menu with :: `?help`')
            return
        train_code: bool = self.julia_api.train(input_sentence, output_sentence)
        if not train_code:
            async with interaction.channel.typing():
                await asyncio.sleep(1)
            interaction.edit_original_response(f'{interaction.user.mention}, You did not specify one of the parameters for the neural network settings. Please review them and correct your command\nUse the help menu with :: `?help`')
            return
        async with interaction.channel.typing():
            await asyncio.sleep(1)
        interaction.edit_original_response(f'{interaction.user.mention}, You have successfully trained the neural network to respond `{output_sentence}` to the input `{input_sentence}`\nFor more commands, use :: `?help`')
    

def setup(bot: commands.Bot = None) -> None:
    bot.add_cog(JuliaAPI(bot))
