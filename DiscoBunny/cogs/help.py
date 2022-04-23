import discord
from discord.ext import commands

# Help commands

class HelpCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Creates command group; main help menu.
    @commands.group()
    async def help(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send(
            "`!help bunny`\t\t help on the `!bunny` command\n" +
            "`!help gif`\t\t\t help on the `!gif` command\n" +
            "`!help gif add`\t help on the `!gif-add` command\n" +
            "`!help suggest`\t help on the `!suggest` command\n" +
            "`!help tts`\t\t\t help on the `!tts` command")

    # Help for !bunny
    @help.command(name="bunny")
    async def _bunny(self, ctx):
        await ctx.send("**Command: !bunny**\n" +
            "```Syntax: !bunny\n\n" +
            "Selects and posts a random Bunny post from Reddit.\n" +
            "Note: because of the response time from Reddit, this may sometimes take a few seconds.```")

    # Help for !gif
    @help.command(name="gif")
    async def _gif(self, ctx):
        await ctx.send("**Command: !gif**\n" +
                "```Syntax: !gif gif-name\n" +
                "\tgif-name: [required] the name of the gif you are requesting\n\n"
                "Posts a specific gif to chat. Must have been previously saved with this name.```")

    # Help for !gif add
    @help.command(name="gif add")
    async def _gif_add(self, ctx):
        await ctx.send("**Command: !gif-add**\n" +
                "```Syntax: !gif add gif-name gif-url\n" +
                "\tgif-name: [required] the name this gif will be referenced under. This can be any number of words..\n" +
                "\tgif-url: [required] the URL to the gif. Must start with http or https.\n\n" +
                "Saves gif information to be called later with !gif.\n" +
                "Note: adding gifs is limited to members Level 5 or higher.```")

    # Help for !suggest
    @help.command(name="suggest")
    async def _suggest(self, ctx):
        await ctx.send("**Command: !suggest**\n" +
                "```Syntax: !suggest suggestion-url message\n" +
                "\tsuggestion-url: [required] the URL to the suggested item.\n" +
                "\tmessage: [optional] a message to accompany the suggestion.\n\n" +
                "Send a suggestion for Bunny's wishlist.```")

    # Help for !tts
    @help.command(name="tts")
    async def _tts(self, ctx):
        await ctx.send("**Command: !tts**\n" +
                "```Syntax: !tts text\n" +
                "\ttext: [required] the text to be spoken.\n\n" +
                "Text to speech in a voice channel.\n\n" +
                "Alternate commands:\n" +
                "!ttsau - Australian accent\n" +
                "!ttsie - Irish accent\n" +
                "!ttsuk - British accent```")

def setup(bot):
    bot.add_cog(HelpCog(bot))
