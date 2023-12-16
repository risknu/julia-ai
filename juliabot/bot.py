from __future__ import annotations

from os import listdir

import disnake
from disnake.ext import commands

from juliaai.misc import MetaSettings, ENV
env: ENV = ENV
meta_settings: MetaSettings = MetaSettings

intents = disnake.Intents.all()
intents.messages = True

bot = commands.Bot(
    intents=intents,
    command_prefix=meta_settings.command_prefix,
    help_command=None)

def run_bot_starter() -> None:
    for filename in listdir('juliabot/cogs'):
        if filename.endswith('.py'):
            bot.load_extension(f'juliabot.cogs.{filename[:-3]}')
            print(f'[INFO]\tLoaded new `cog`\tjuliabot.cogs.{filename[:-3]}')
    bot.run(env.TOKEN)
