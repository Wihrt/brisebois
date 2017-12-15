#!/bin/env python

"""RPG Commands module"""

from discord.ext import commands
import dice


class Rpg(object):
    """Implements RPG commands"""

    def __init__(self, bot):
        self.bot = bot

    # Commands
    # -------------------------------------------------------------------------
    @commands.command()
    async def dice(self, ctx, msg):
        """Roll a dice"""
        result = self._dice(msg)
        await ctx.channel.send("{} Roll {} = {}".format(ctx.author.mention, msg, result))

    # Static methods
    # -------------------------------------------------------------------------
    @staticmethod
    def _dice(msg):
        result = dice.roll(msg)
        if isinstance(result, list):
            result = sum(result)
        return result

def setup(bot):
    """Add RPG commands to the Bot"""
    bot.add_cog(Rpg(bot))
