#!/bin/env python
from discord import Color, Embed
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType
from html import unescape
from random import randint, shuffle
from requests import get


class Guess(object):

    def __init__(self, bot):
        self.bot = bot

    @commands.group(pass_context=True,
                    no_pm=True,
                    help="Launch a new guessing game")
    async def guess(self, ctx):
        if ctx.invoked_subcommand is None:
            await self.bot.send_message(
                ctx.message.author,
                "No subcommand specified\n\
Use $help %s to see the list of commands." % ctx.command)
            await self.bot.delete_message(ctx.message)

    @guess.command(pass_context=True,
                   help="Launch a number guessing game")
    @commands.cooldown(1, "30.0", BucketType.user)
    async def number(self, ctx):
        def is_answer(msg):
            return msg.content.isdigit()

        answers, retries = list(), 20
        await self.bot.say("Guess a number between 1 and 100\n\
You have {} tries.".format(retries))
        number = randint(1, 100)
        while retries > 0:
            msg = await self.bot.wait_for_message(check=is_answer)
            if int(msg.content) in answers:
                await self.bot.say("You already proposed this answer !\n\
Proposed answers : {}".format(", ".join(list(map(str, answers)))))
            else:
                retries -= 1
                answers.append(int(msg.content))
                if int(msg.content) > number:
                    await self.bot.say(
                        "Oops ! Too high !\n{0} tries left".format(retries))
                if int(msg.content) < number:
                    await self.bot.say(
                        "Oops ! Too low !\n{0} tries left".format(retries))
                if int(msg.content) == number:
                    await self.bot.say("You found it !")
                    return

        await self.bot.say(
            "You didn't found the number !\nIt was : {}".format(number))
        return

    @guess.command(pass_context=True,
                   help="Launch a hanging man game")
    @commands.cooldown(1, "360.0", BucketType.server)
    async def word(self, ctx):
        def is_answer(msg):
            if len(msg.content) is 1:
                return msg.content.isalpha()

        def word_replace(word, letters):
            for l in letters:
                word = word.replace(l, "?")
            return word.upper()

        payload = dict(len=randint(3, 20))
        word = get("http://setgetgo.com/randomword/get.php",
                   params=payload).text
        letters = list(set(word))
        answers, retries = list(), len(letters) + 5
        await self.bot.say(
            "Word to guess ({0} letters): {1}\nYou have {2} tries".format(
                len(word), word_replace(word, letters), retries))

        while retries > 0:
            msg = await self.bot.wait_for_message(check=is_answer)
            if msg.content.upper() in answers:
                await self.bot.say("You already proposed this answer !\n\
Proposed answers : {}".format(", ".join(answers)))
            else:
                retries -= 1
                answers.append(msg.content.upper())
                if msg.content.lower() in letters:
                    letters.remove(msg.content.lower())
                await self.bot.say(
                    "Word to guess ({0} letters): {1}.\n{2} tries left".format(
                        len(word), word_replace(word, letters), retries))
                if not letters:
                    await self.bot.say("You have found the word !")
                    return
        await self.bot.say(
            "You didn't find the word.\nIt was : {0}".format(word.upper()))
        return

    @guess.command(pass_context=True,
                   help="Give a random trivia question")
    @commands.cooldown(1, "15.0", BucketType.server)
    async def trivia(self, ctx):
        def is_answer(msg):
            return msg.content.isdigit()

        def format_answers(answers):
            message, i = str(), 1
            for a in answers:
                message += "**%s.** %s\n" % (i, a)
                i += 1
            return message

        json = get("https://opentdb.com/api.php?amount=1").json()["results"][0]
        correct_answer = unescape(json["correct_answer"])
        answers = json["incorrect_answers"] + [correct_answer]
        answers = [unescape(a) for a in answers]
        shuffle(answers)

        message = Embed()
        message.add_field(name=unescape(json["question"]),
                          value=format_answers(answers),
                          inline=False)
        await self.bot.send_message(ctx.message.channel, embed=message)

        msg = await self.bot.wait_for_message(check=is_answer,
                                              timeout=15.0)
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
        await self.bot.send_message(ctx.message.channel, embed=message)
        return


def setup(bot):
    bot.add_cog(Guess(bot))
