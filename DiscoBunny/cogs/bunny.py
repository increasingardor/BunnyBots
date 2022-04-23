import discord
from discord.ext import commands
import gspread
import validators
import pytz
import dotenv
import os
import asyncio
import asyncpraw
import random
import datetime
import time

class BunnyCog(commands.Cog):
    # Various commands related to Bunny
    # `ctx` parameter in commands is Discord Context, includes info about the sender, the message, 
    # the Discord server (called a guild), and methods to interact with them

    def __init__(self, bot):
        # Load local environment variables
        dotenv.load_dotenv(dotenv.find_dotenv())
        self.CLIENT_ID = os.getenv("CLIENT_ID")
        self.CLIENT_SECRET = os.getenv("CLIENT_SECRET")

        # Responses for the !bunny command.
        self.responses = ["We're hunting wabbit...", "Trying to find Bunny...", "Searching for Bunny...", "Picking a random Bunny post..."]
        self.found = ["Found a wabbit, found a wabbit, found a WABBIT!", "Found Bunny!", "Bunny located.", "Here's your random Bunny..."]

    @commands.command()
    async def bunny(self, ctx):
        # Pulls a random post from Bunny's history.

        # Connects to Reddit.
        reddit = asyncpraw.Reddit(
            client_id=self.CLIENT_ID,
            client_secret=self.CLIENT_SECRET,
            user_agent="BunnitBot 1.1",
        )

        # Pulls random response and sends message.
        rand_response = random.randint(0, len(self.responses) - 1)
        await ctx.send(self.responses[rand_response])

        # Reads list of post IDs from file.
        post_list = list()
        with open("/home/aricept/DiscoBunny/posts.txt", "r") as file:
            post_list = file.readlines()

        # Selects a random post, requests from Reddit, and sends message.
        random_post = random.randint(0, len(post_list) - 1)
        selected_post = await reddit.submission(id=f"{post_list[random_post]}")
        await ctx.send(self.found[rand_response])

        # Gets image URL for display in embed, builds embed, sends message, closes Reddit connection
        image_url = self.get_image_url(selected_post)
        embed = self.embed_from_post(ctx, selected_post, image_url)
        await ctx.send(embed=embed)
        await reddit.close()

    def embed_from_post(self, ctx, selected_post, image_url):
        # Builds embed
        embed = discord.Embed(title=selected_post.title, url=f"http://reddit.com{selected_post.permalink}", color=2447966)
        embed.set_author(name="Bunny", url="http://reddit.com/u/heyitsjustbunny")
        if image_url != None:
            embed.set_image(url=image_url)
        embed.timestamp = datetime.datetime.utcfromtimestamp(selected_post.created_utc)
        embed.set_footer(text=f"Posted to {selected_post.subreddit.display_name} • Requested by {ctx.author.display_name}")
        return embed

    def add_to_sheet(self, spreadsheet_id, sheet_name, values):
        # Adds suggestion to spreadsheet for gift suggestions
        gc = gspread.service_account(os.getenv("SERVICE_JSON"))
        spreadsheet = gc.open_by_key(spreadsheet_id)
        sheet = spreadsheet.worksheet(sheet_name)
        sheet.append_row(values)

    def get_image_url(self, post):
        # Parses image URL.
        # Discord can't display Imgur's .gifv files, so we send the .jpg.
        if post.url.find("imgur") > -1:
            return post.url.replace("gifv", "jpg")
        # If post was removed by Reddit we return a placeholder image because the image is not available.
        elif post.title.find("Removed by Reddit") > -1:
            return "https://www.publicdomainpictures.net/pictures/280000/nahled/not-found-image-15383864787lu.jpg"
        # For Reddit galleries we get the first preview image.
        elif post.url.find("gallery") > -1:
            for i in post.media_metadata.items():
                return i[1]["p"][0]["u"]
                break
        # For individual Reddit images we just return the URL
        else:
            try:
                return post.preview["images"][0]["source"]["url"]
            except:
                return None    

    @commands.command()
    async def suggest(self, ctx, url, *, comments=""):
        # The actual !suggest command.
        spreadsheet = os.environ["SUGGEST_SHEET"]
        sheetname = "Main List"
        tz = pytz.timezone('US/Central')

        # Checks that a valid URL was submitted
        if not validators.url(url):
            await ctx.send("Please provide a valid URL.")
        # If valid, We add it to the sheet.
        else:
            values = [url, ctx.author.display_name, datetime.datetime.now(tz).strftime("%m/%d/%Y %H:%M:%S"), comments]
            self.add_to_sheet(spreadsheet, sheetname, values)
            await ctx.send("Suggestion made!")

    @commands.command()
    async def prize(self, ctx, url):
        # pick-a-prize command for suggesting things for Bunny to buy with Throne refunds.
        # Selects the #pick-a-prize channel
        channel = ctx.bot.get_channel(948272967178149948)

        # Validates URL and rejects if invalid
        if not validators.url(url):
            await ctx.send("Please provide a valid URL.")
        # Sends message to correct channel, and responds to sender that it was sent.
        else:
            await channel.send(url)
            await ctx.send(f"Prize link posted in {channel.mention}!")

    @commands.Cog.listener()
    async def on_message(self, message):
        # Adds listener for all messages, but is watching specifically for #are-you-pooping posts

        # Skips if is a DM
        if isinstance(message.channel, discord.DMChannel):
            return
        
        # Waits one second for one of the other bots to delete message
        time.sleep(1)

        # If we're in the right channel and the message is not exactly equal to yes/YES/YeS etc.
        if message.channel.name == "are-you-pooping" and message.content.lower() != "yes":
            # Excludes Bunny from being deleted.
            if not len([role for role in message.author.roles if role.name in os.environ["MOD_ROLES"].split(",")]): 
                try: 
                    # Deletes message
                    msg = await message.channel.fetch_message(message.id)
                    await message.delete()
                except discord.NotFound:
                    # If we can't find the message, it was deleted, so we return
                    return
                # Write other errors to log and DM owner (me)
                except Exception as e:
                    error_msg = f"ERROR: {type(e).__name__}: {e}"
                    print(error_msg)
                    owner = message.guild.get_member_named(os.getenv("NOT_OWNER"))
                    await owner.send(error_msg)

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        # Same as above, but for message edits, which the original bot does not cover
        if isinstance(after.channel, discord.DMChannel):
            return
        if after.channel.name == "are-you-pooping" and after.content.lower() != "yes":
            try:                
                msg = await after.channel.fetch_message(after.id)
                await after.delete()
            except discord.NotFound:
                return
            except Exception as e:
                error_msg = f"ERROR: {type(e).__name__}: {e}"
                print(error_msg)
                owner = after.guild.get_member_named("tkdnate")
                await owner.send(error_msg)

def setup(bot):
    bot.add_cog(BunnyCog(bot))
