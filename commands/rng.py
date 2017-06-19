#!/bin/env python
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType
from random import randint


class RNG(object):

    def __init__(self, bot):
        self.bot = bot
        self.number = None

    @commands.command(pass_context=True,
                      help="Roll a dice")
    async def dice(self, ctx, faces=6, number=1):
        value = 0
        for n in range(1, number + 1):
            value += randint(1, faces)
        await self.bot.say("Roll {0}d{1} = {2}".format(number, faces, value))

    # Commands
    # -------------------------------------------------------------------------
    @commands.group(pass_context=True,
                    help="Launch a new guessing game")
    async def guess(self, ctx):
        if ctx.invoked_subcommand is None:
            await self.bot.say("No subcommand specified")

    # Number guess
    # -------------------------------------------------------------------------
    @guess.command(pass_context=True,
                   name="number",
                   help="Launch a number guessing game")
    @commands.cooldown(1, "30.0", BucketType.user)
    async def _number(self, ctx, retries=100):
        def is_answer(msg):
            return msg.content.isdigit()

        await self.bot.say("Guess a number between 1 and 100")
        number = randint(1, 100)
        for i in range(0, retries):
            i += 1
            msg = await self.bot.wait_for_message(author=ctx.message.author,
                                                  check=is_answer)
            if int(msg.content) > number:
                await self.bot.say("Oops ! Too high !")
            if int(msg.content) < number:
                await self.bot.say("Oops ! Too low")
            if int(msg.content) == number:
                await self.bot.say("You found it !")
                return


def setup(bot):
    bot.add_cog(RNG(bot))
