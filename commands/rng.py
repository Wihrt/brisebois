#!/bin/env python
from discord.ext import commands
from random import randint
import discord


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

    @commands.group(pass_context=True,
                    help="Launch a new guessing game")
    async def guess(self, ctx):
        if ctx.invoked_subcommand is None:
            await self.bot.say("No subcommand specified")

    @guess.command(pass_context=True,
                   name="number",
                   help="Guess the number !")
    async def _number(self, ctx, retries=100):
        def check(msg):
            return msg.content.startswith("!guess")

        if self.number:
            await self.bot.say("Another guessing game is on. \
Finish it before launching another")
        else:
            self.number = randint(1, 100)
            try:
                retries = int(retries)
                if retries not in range(1, 101):
                    retries = 100
            except ValueError as e:
                retries = 100
            await self.bot.say("Try to guess the number !\n\
Use !guess to propose a number\nYou have {0} tries".format(retries))

            while retries > 0:
                msg = await self.bot.wait_for_message(check=check)
                result = await self.test_number(msg, self.number)
                if result is False:
                    retries -= 1
                    await self.bot.say("Only {0} tries left !".format(retries))
                if result is True:
                    self.number = None
            await self.bot.say(
                "You didn't find it ! The number was : {}".format(self.number))
            self.number = None

    async def test_number(self, msg, number):
        try:
            guess = int(msg.content[len('!guess'):].strip())
            if guess in range(1, 101):
                if guess > number:
                    await self.bot.say("Oops ! Too high !")
                    return False
                if guess < number:
                    await self.bot.say("Oops ! Too low !")
                    return False
                if guess == number:
                    await self.bot.say("Yeaaaah ! You found it !")
                    return True
        except ValueError:
            pass
        return None


def setup(bot):
    bot.add_cog(RNG(bot))
