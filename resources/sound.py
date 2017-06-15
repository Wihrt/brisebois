#!/bin/env python
from asyncio import sleep
from discord.ext import commands
import discord


class Sound(object):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True,
                      help="Play the elevator song")
    async def wait(self, ctx, seconds="10"):
        if ctx.message.author.voice_channel:
            seconds = int(seconds)
            if seconds > 3599:
                return await self.bot.whisper(
                    "Warning ! The number must be between 1 and 3599")
            voice = await self.bot.join_voice_channel(
                ctx.message.author.voice_channel)
            player = voice.create_ffmpeg_player("videos/elevator.mp3")
            player.start()
            await sleep(seconds)
            await voice.disconnect()

    @commands.command(pass_context=True,
                      help="Stop the music")
    async def stop(self, ctx):
        if self.bot.is_voice_connected(ctx.message.server):
            voice = self.bot.voice_client_in(ctx.message.server)
            await voice.disconnect()


def setup(bot):
    bot.add_cog(Sound(bot))
