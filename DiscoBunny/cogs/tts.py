import discord
from discord.ext import commands
import os
from gtts import gTTS
import collections

# TTS commands

class TtsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.queue = collections.deque([])

    # Base !tts command. The only real difference between the various commands is the domain extension gTTS uses
    # to contact Google Translate
    @commands.command()
    async def tts(self, ctx, *, text):
        if text is None:
            raise commands.MissingRequiredArgument
        await self.speak(ctx, text, "com")

    # !ttsie
    @commands.command()
    async def ttsie(self, ctx, *, text):
        await self.speak(ctx, text, "ie")

    # !ttsuk
    @commands.command()
    async def ttsuk(self, ctx, *, text):
        await self.speak(ctx, text, "co.uk")

    # !ttsau
    @commands.command()
    async def ttsau(self, ctx, *, text):
        await self.speak(ctx, text, "com.au")

    # Command to leave a channel
    @commands.command(name="tts-leave")
    async def tts_leave(self, ctx):
        if ctx.voice_client is None:
            await ctx.send("Not currently connected to a voice channel.")
        else:
            await ctx.voice_client.disconnect()
     
    # Speak function used by commands
    async def speak(self, ctx, text, domain):
        # Only functions in #tts
        if ctx.channel.name == "tts":
            # Check if user is in voice channel
            if ctx.author.voice is None:
                await ctx.send("Please join a voice channel.")
                return
            # Set filename for later saving
            filename = f"{ctx.message.id}.mp3"

            # Check if bot is connected to voice and connect if not
            voice = ctx.voice_client
            if not voice or not voice.is_connected():
                await ctx.author.voice.channel.connect()
                voice = ctx.voice_client

            # Prevent the bot from channel switching
            if voice.channel != ctx.author.voice.channel:
                await ctx.send("The bot appears to be in use in another voice channel right now.")
            else:
                # Appends user's name to text
                to_speak = f"{ctx.author.display_name} says: {text}"
                # Requests TTS from Google and saves to file
                tts = gTTS(text=to_speak, lang="en", tld=domain)
                tts.save(filename)
                # Adds file to queue and attempts to play
                self.queue.append(filename)
                self.play(voice)

    # Play function. 
    def play(self, voice):
        # If already playing a file, we're done
        if voice.is_playing():
            return
        # Grab the next file from the queue and play
        next_tts = self.queue.popleft()
        voice.play(discord.FFmpegPCMAudio(next_tts))
        # Keep looping while playing the file
        while voice.is_playing():
            continue
        # Once done with the file, delete it, check for the next file and play if it exists
        else:
            os.remove(next_tts)
            if len(self.queue) > 0:
                self.play(voice)

    # Error handler
    @tts.error
    async def _tts_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Please provide some text to speak")
        else:
            print(error)

def setup(bot):
    bot.add_cog(TtsCog(bot))
