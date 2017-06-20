#!/bin/env python
from discord.ext import commands
from random import randint


class Rng(object):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True,
                      help="Roll a dice")
    async def dice(self, ctx, faces=6, number=1):
        value = 0
        for n in range(1, number + 1):
            value += randint(1, faces)
        await self.bot.say("Roll {0}d{1} = {2}".format(number, faces, value))
        return


def setup(bot):
    bot.add_cog(Rng(bot))
