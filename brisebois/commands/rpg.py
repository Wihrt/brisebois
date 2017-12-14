#!/bin/env python

"""RPG Commands module"""

from discord.ext import commands
import dice


class Rpg(object):
    """Implements RPG commands"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def dice(self, ctx, msg):
        """Roll a dice"""
        result = dice.roll(msg)
        if isinstance(result, list):
            result = sum(result)
        await ctx.channel.send("{} Roll {} = {}".format(ctx.author.mention, msg, result))

def setup(bot):
    """Add RPG commands to the Bot"""
    bot.add_cog(Rpg(bot))
