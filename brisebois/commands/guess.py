#!/bin/env python

"""Guess Commands module"""

from html import unescape
from random import randint, shuffle

from discord import Color, Embed
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType
from requests import get


class Guess(object):
    """Implements Guess commands"""

    def __init__(self, bot):
        self.bot = bot

    @commands.group(no_pm=True)
    async def guess(self, ctx):
        """Launch a new guessing game

        Args:
            ctx: Context of the message

        Returns: None
        """
        if ctx.invoked_subcommand is None:
            await ctx.author.send("No subcommand specified\n\
Use $help {} to see the list of commands.".format(ctx.command))
            await ctx.message.delete()

    @guess.command()
    @commands.cooldown(1, "30.0", BucketType.user)
    async def number(self, ctx):
        """Launch a number guessing game

        Args:

        Returns: None
        """
        def _is_answer(msg):
            return msg.content.isdigit()
        answers, retries = list(), 20
        await ctx.channel.send("Guess a number between 1 and 100\n\
You have {} tries.".format(retries))
        number = randint(1, 100)
        while retries > 0:
            msg = await self.bot.wait_for('message', check=_is_answer)
            if int(msg.content) in answers:
                await ctx.channel.send("You already proposed this answer !\n\
Proposed answers : {}".format(", ".join(list(map(str, answers)))))
            else:
                retries -= 1
                answers.append(int(msg.content))
                if int(msg.content) > number:
                    await ctx.channel.send(
                        "Oops ! Too high !\n{0} tries left".format(retries)))
                if int(msg.content) < number:
                    await ctx.channel.send(
                        "Oops ! Too low !\n{0} tries left".format(retries))
                if int(msg.content) == number:
                    await ctx.channel.send("You found it !")
                    return

        await ctx.channel.send(
            "You didn't found the number !\nIt was : {}".format(number))
        return

    @guess.command()
    @commands.cooldown(1, "360.0", BucketType.server)
    async def word(self):
        """Launch a word guessing game

        Args:

        Returns: None
        """
        def _is_answer(msg):
            if len(msg.content) is 1:
                return msg.content.isalpha()

        def _word_replace(word, letters):
            for letter in letters:
                word = word.replace(letter, "?")
            return word.upper()

        payload = dict(len=randint(3, 20))
        word = get("http://setgetgo.com/randomword/get.php",
                   params=payload).text
        letters = list(set(word))
        answers, retries = list(), len(letters) + 5
        await ctx.channel.send(
            "Word to guess ({0} letters): {1}\nYou have {2} tries".format(
                len(word), _word_replace(word, letters), retries))

        while retries > 0:
            msg = await self.bot.wait_for('message', check=_is_answer)
            if msg.content.upper() in answers:
                await ctx.channel.send("You already proposed this answer !\n\
Proposed answers : {}".format(", ".join(answers)))
            else:
                retries -= 1
                answers.append(msg.content.upper())
                if msg.content.lower() in letters:
                    letters.remove(msg.content.lower())
                await ctx.channel.send(
                    "Word to guess ({0} letters): {1}.\n{2} tries left".format(
                        len(word), _word_replace(word, letters), retries))
                if not letters:
                    await ctx.channel.send("You have found the word !")
                    return
        await ctx.channel.send(
            "You didn't find the word.\nIt was : {0}".format(word.upper()))
        return

    @guess.command()
    @commands.cooldown(1, "15.0", BucketType.server)
    async def trivia(self, ctx):
        """Give a random trivia question
        Args:
            ctx: Context of the message

        Returns: None
        """
        def _is_answer(msg):
            return msg.content.isdigit()

        def _format_answers(answers):
            message, i = str(), 1
            for answer in answers:
                message += "**%s.** %s\n" % (i, answer)
                i += 1
            return message

        json = get("https://opentdb.com/api.php?amount=1").json()["results"][0]
        correct_answer = unescape(json["correct_answer"])
        answers = json["incorrect_answers"] + [correct_answer]
        answers = [unescape(a) for a in answers]
        shuffle(answers)

        message = Embed()
        message.add_field(name=unescape(json["question"]),
                          value=_format_answers(answers),
                          inline=False)
        await ctx.channel.send(embed=message)
        msg = await self.bot.wait_for('message', check=_is_answer, timeout=15.0)
        if msg is None:
            message = Embed(color=Color.red())
            message.add_field(name="Sorry !",
                              value="You took too long to answer !",
                              inline=False)
        else:
            if answers[int(msg.content) - 1] != correct_answer:
                message = Embed(color=Color.red())
                message.add_field(name="Incorrect !",
                                  value="La bonne reponse était %s" %
                                  correct_answer,
                                  inline=False)
            else:
                message = Embed(color=Color.green(), title="Correct !")
        await ctx.channel.send(embed=message)
        return


def setup(bot):
    """Add commands to the bot.

    Args:
        bot: Bot which will add the commands

    Returns:
        None
    """
    bot.add_cog(Guess(bot))
