#!/bin/env python

"""RPG Commands module"""

from utils.embed import create_embed

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
        title = "Roll {0} = {1}".format(msg, result)
        message = create_embed(title=title)
        await ctx.channel.send(embed=message)

def setup(bot):
    bot.add_cog(Rpg(bot))
