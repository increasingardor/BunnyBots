from discord.ext import commands
import dotenv
import os
import checks

# Commands to load and unload other cogs/extensions
# This way we can work on just a single module and then reload it without impacting the rest of the bot

class ControlCogsCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        dotenv.load_dotenv(dotenv.find_dotenv())
        self.roles = os.environ["MOD_ROLES"]
    
    # Loads a cog/extension - `cog` parameter must be a dot-separated path, e.g. cogs.gifs
    @commands.command(name='load', hidden=True)
    @checks.has_role_in_list(os.environ["MOD_ROLES"])
    async def ext_load(self, ctx, *, cog: str):
        try:
            self.bot.load_extension(cog)
        except Exception as e:
            await ctx.send(f'**`ERROR:`** {type(e).__name__} - {e}')
        else:
            await ctx.send('**`SUCCESS`**')
            print(f"Module {cog} loaded successfully\n")

    # Unloads cog/extension
    @commands.command(name='unload', hidden=True)
    @checks.has_role_in_list(os.environ["MOD_ROLES"])
    async def ext_unload(self, ctx, *, cog: str):
        try:
            self.bot.unload_extension(cog)
        except Exception as e:
            await ctx.send(f'**`ERROR:`** {type(e).__name__} - {e}')
        else:
            await ctx.send('**`SUCCESS`**')
            print(f"Module {cog} unloaded successfully\n")

    # Reloads a cog/extension
    @commands.command(name='reload', hidden=True)
    @checks.has_role_in_list(os.environ["MOD_ROLES"])
    async def ext_reload(self, ctx, *, cog: str):
        """Command which Reloads a Module.
        Remember to use dot path. e.g: cogs.owner"""

        try:
            self.bot.unload_extension(cog)
            self.bot.load_extension(cog)
        except Exception as e:
            await ctx.send(f'**`ERROR:`** {type(e).__name__} - {e}')
        else:
            await ctx.send('**`SUCCESS`**')
            print(f"Module {cog} reloaded successfully\n")

    # Gets list of current loaded extensions
    @commands.command(name='extensions', hidden=True)
    @checks.has_role_in_list(os.environ["MOD_ROLES"])
    async def ext_get(self, ctx):
        cogs_list = "**Current Loaded Extensions**\n"
        try:
            for cog in self.bot.extensions:
                cogs_list = cogs_list + f"{cog}\n"
        except Exception as e:
            await ctx.send(f'**`ERROR:`** {type(e).__name__} - {e}')
        else:
            await ctx.send(cogs_list)

def setup(bot):
    bot.add_cog(ControlCogsCog(bot))
