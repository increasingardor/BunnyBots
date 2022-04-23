import discord
from discord.ext import commands
import os
import dotenv
import checks

# Commands to manage settings and environment variables from Discord

class SettingsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.env_file = dotenv.find_dotenv()
        dotenv.load_dotenv(self.env_file)
        print(os.environ["MOD_ROLES"])

    # Creates command group
    @commands.group()
    async def settings(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send("Please use a subcommand. Use `!help settings` for a list.")

    # Add a setting
    @settings.command()
    @checks.has_role_in_list(os.environ["MOD_ROLES"])
    async def add(self, ctx, key, *, value):
        # All environment variable names are uppercase, but we should allow for users to enter in non-uppercase
        key = key.upper()
        # If the key already exists, we can't add it.
        if key in os.environ:
            await ctx.send(f"Setting {key.upper()} already exists. Please use `!settings update` to update a key.")
        else:
            self.set(key, value)
            await ctx.send(f"Setting `{key}` set to `{value}`.")

    # Error handler
    @add.error
    async def add_error(self, ctx, error):
        if isinstance(error, checks.MissingRoleInList):
            message = "You don't have permission to do that."
        else:
            message = f"ERROR: {type(error).__name__} - {error}"
        await ctx.send(message)

    # Update setting
    @settings.command()
    @checks.has_role_in_list(os.environ["MOD_ROLES"])
    async def update(self, ctx, key, *, value):
        key = key.upper()
        # We can only update the setting if it exists in the environment
        if key in os.environ:
            self.set(key, value)
            await ctx.send(f"Setting `{key}` set to `{value}`.")
        else:
            await ctx.send(f"Setting `{key}` does not exist. Please use `!settings add` to add a key.")

    # Sets setting value; this is used in other commands, is not callable directly
    def set(self, key, value):
        os.environ[key] = value
        dotenv.set_key(self.env_file, key, os.environ[key])

    # Get current setting value
    @settings.command()
    @checks.has_role_in_list(os.environ["MOD_ROLES"])
    async def get(self, ctx, key):
        key = key.upper()
        if key in os.environ:
            value = os.environ[key]
            await ctx.send(f"{key} = {value}")
        else:
            await ctx.send(f"Setting {key} does not exist. Please use `!settings add` to add a key.")

def setup(bot):
    bot.add_cog(SettingsCog(bot))
