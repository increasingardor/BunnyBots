import discord
from discord.ext import commands
import checks
import requests
import urllib.parse
import os
import dotenv
import validators
from datetime import datetime
import asyncio

# GIF commands

class GifsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        dotenv.load_dotenv(dotenv.find_dotenv())
        self.gif_cooldowns = {}

    # Creates command group; if no subcommand is found in the message, it runs the below
    @commands.group(invoke_without_command=True)
    async def gif(self, ctx, *, gif_name):
        if ctx.invoked_subcommand is None:
            # Manual cooldown check so we can let Bunny spam gifs if she wants to
            if not ctx.author.name in self.gif_cooldowns or (datetime.now() - self.gif_cooldowns[ctx.author.name]).seconds > int(dotenv.get_key(dotenv.find_dotenv(), "GIF_COOLDOWN")) or ctx.author.top_role >= discord.utils.get(ctx.guild.roles, name="Moderator"):
                payload = {'name': gif_name.lower()}
                r = requests.get(f"{os.getenv('GET_GIF_URL')}", params=payload)
                data = r.json()
                if data["url"] == "Gif does not exist!":
                    await ctx.send("We don't have a GIF by that name.")
                else:
                    self.gif_cooldowns[ctx.author.name] = datetime.now()
                    await ctx.send(f"{data['url']}")
            else:
                await ctx.send("You're doing that too frequently. Please wait a minute before doing that again.")

    # Error handler to provide some responses based on error type
    @gif.error
    async def gif_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            message = f"You must provide a GIF name when making a request."
        else:
            message = "We encountered an error, sorry."
        print(error)
        await ctx.send(message)

    @gif.command(name="add")
    @checks.is_level_5("GIF Master")
    async def gif_add(self, ctx, *, text):
        # Only runnable in specific channels, or if the user is Mod level or higher
        if ctx.channel.name.find("bot-commands") > -1 or ctx.channel.name.find("bots-commands") > -1 or ctx.author.top_role >= discord.utils.get(ctx.guild.roles, name="Moderator"):
            # Splits the text provided into separate words; the last "word" is the URL, and we rejoin the rest as the GIF name
            parsed = text.split()
            gif_url = parsed.pop()
            gif_name = " ".join(parsed)

            # Checks for valid URL
            if not validators.url(gif_url):
                await ctx.send(f"`{gif_url}` is not a valid URL. Make sure you're using the correct order: `!gif add gif-name gif-url`.")
            else:
                r = requests.post(f"{os.getenv('ADD_GIF_URL')}name={gif_name.lower()}&url={urllib.parse.quote(gif_url, safe='')}")
                data = r.json()
                if data["response"] == "Gif already exists!":
                    await ctx.send(f"A GIF with the name `{gif_name.lower()}` already exists. Try a different name!")
                else:
                    await ctx.send(f"GIF added by {ctx.author.display_name}!\nName: `{gif_name.lower()}`\nURL: `{gif_url}`\n{gif_url}")
        else:
            await ctx.send("That can only be done in a bot command channel.")

    # Error handler for gif add
    @gif_add.error
    async def gif_add_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            message = "You must be at least Level 5 to do that. If you are and still cannot do that, please contact a mod."
        elif isinstance(error, checks.CreepError):
            message = "No. Creep."
        elif isinstance(error, commands.NoPrivateMessage):
            message = "You can't use that in a DM. Why would you send a bot a GIF, anyway?"
        elif isinstance(error, commands.MissingRequiredArgument):
            message = "You must provide a GIF name and a URL to add a GIF: `!gif <name> <url>`"
        await ctx.send(message)

    # Update GIF URL
    @gif.command(name="update")
    @checks.is_level_5("GIF Master")
    async def gif_update(self, ctx, *, text):
        parsed = text.split()
        gif_url = parsed.pop()
        gif_name = " ".join(parsed)
        if not validators.url(gif_url):
            await ctx.send(f"`{gif_url}` is not a valid URL. Make sure you're using the correct order: `!gif add gif-name gif-url`.")
        else:
            r = requests.post(f"{os.getenv('UPDATE_GIF_UTL')}name={gif_name}&url={urllib.parse.quote(gif_url, safe='')}&update=1")
            data = r.json()
            if data["response"] == "Gif updated!":
                await ctx.send(f"GIF updated!\nName: `{gif_name}`\nNew URL: `{gif_url}`\n{gif_url}")
            else:
                await ctx.send("There was a problem updating that GIF. Maybe we couldn't find one with the name, or some other problem occurred. Please try again.")

    # Delete a GIF by name
    @gif.command(name="delete")
    @checks.is_level_5("GIF Master")
    async def gif_delete(self, ctx, *, gif_name):
        # Used lower to check message content of a response for delete confirmation.
        def check_yes(msg):
            return (msg.content.lower() == "y" or msg.content.lower() == "yes") and msg.author.id == ctx.author.id
       
        gif_name = gif_name.lower()
        payload = {'name': gif_name}

        # First check that the GIF exists by trying to get the GIF
        check = requests.get(f"{os.getenv('GET_GIF_URL')}", params=payload)
        data = check.json()
        if data["url"] == "Gif does not exist!":
            await ctx.send("We don't have a GIF by that name.")
        else:
            # Shows GIF and asks if we want to delete it.
            await ctx.send(f"Name: `{gif_name}`\nURL: `{data['url']}`\n{data['url']}")
            await ctx.send(f"Are you sure you want to delete GIF `{gif_name}? y/n")
            try:
                # Wait 15 seconds for response from user
                msg = await self.bot.wait_for("message", check=check_yes, timeout=15.0)
            except asyncio.TimeoutError:
                # If no response stop waiting
                await ctx.send(f"Since you didn't respond yes, the GIF has not been deleted.")
            else:
                # Sends request to delete GIF
                r = requests.post(f"{os.getenv('DELETE_GIF_URL')}name={gif_name}")
                await ctx.send(f"GIF {gif_name} deleted!")

    # Sends URL to list of all GIFs
    @commands.command(name="gif-list")
    async def gif_list(self, ctx):
        await ctx.send("https://heyitsjustbunny.com/discobunny.html")

def setup(bot):
    bot.add_cog(GifsCog(bot))
