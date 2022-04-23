import discord
from discord.ext import commands
import os
import dotenv
from discoutils import get_cogs

# This is the file that starts the bot

# Load environment variables
dotenv.load_dotenv(dotenv.find_dotenv())
description = "Custom bot for The Rabbit Hole Discord server"
# Discord API token for bot
TOKEN = os.getenv("TOKEN")
# Cogs/extensions to load
extensions = get_cogs()
# bot object, declare prefix, turn off automatic help commands (I don't like them)
bot = commands.Bot(command_prefix='!', description=description, help_command=None)

# Loads extensions
if __name__ == '__main__':
    for extension in extensions:
        bot.load_extension(extension)

# Writes some stuff to the console or log, letting us know the bot is connected when the on_ready event fires
@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')

# Runs the bot
bot.run(TOKEN)
