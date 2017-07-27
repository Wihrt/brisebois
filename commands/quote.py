#!/bin/env python

"""Quote Commands module"""

from random import shuffle

from discord import Embed
from discord.ext import commands
from pymongo import MongoClient


class Quote(object):
    """Implements Quote commands"""

    def __init__(self, bot):
        self.bot = bot

    @commands.group(pass_context=True, no_pm=True)
    async def quote(self, ctx):
        """Say a random quote

        Args:
            ctx: Context of the message

        Returns: None
        """
        if ctx.invoked_subcommand is None:
            row = self._list_quote(ctx.message.server.id, one=True)
            if row:
                user = await self.bot.get_user_info(row[1])
                message = Embed()
                message.add_field(
                    name="Random Quote",
                    value="\"{}\" - {}".format(row[0], user.mention),
                    inline=False)
                await self.bot.send_message(ctx.message.channel, embed=message)
        return

    @quote.command(pass_context=True)
    async def add(self, ctx, quote, quoter=None):
        """Add a quote

        Args:
            ctx: Context of the message
            quote (str): Message to be quoted
            quoter (str): User to be associated with the quote

        Returns: None
        """
        if len(ctx.message.mentions) is 1:
            server, quoter = ctx.message.server.id, ctx.message.mentions[0].id
            result = self._add_quote(server, quote, quoter)
            if result:
                await self.bot.say("Quote added")

    @quote.command(pass_context=True, name="del")
    async def delete(self, ctx, message):
        """Delete a quote

        Args:
            ctx: Context of the message
            message (str): Quote or quote associated to the user to be deleted

        Returns: None
        """
        server = ctx.message.server.id
        if len(ctx.message.mentions) is 1:  # There are mentions in the message
            result = self._del_quote(server, user=ctx.message.mentions[0].id)
        else:  # It is a quote
            result = self._del_quote(server, quote=message)
        if result:
            await self.bot.say("Quote deleted")

    @quote.command(pass_context=True,
                   no_pm=True,
                   help="List all quotes")
    async def list(self, ctx, quoter=None):
        """List all quotes

        Args:
            ctx: Context of the message
            quoter: User to list the quotes

        Returns: None
        """
        server = ctx.message.server.id
        title = "Quote from {}".format(ctx.message.server.name)
        if quoter:
            if len(ctx.message.mentions) is 1:
                quoter = ctx.message.mentions[0].id
                user = await self.bot.get_user_info(quoter)
                title = "Quote from {}".format(user.display_name)
        content = str()
        rows = self._list_quote(server, quoter)
        if rows:
            for quote, user in self._list_quote(server, quoter):
                user = await self.bot.get_user_info(user)
                content += "\"{}\" - {}\n".format(quote, user.mention)
            message = Embed()
            message.add_field(name=title, value=content, inline=False)
            await self.bot.send_message(ctx.message.channel, embed=message)

    # MongoDB methods
    @staticmethod
    def _add_quote(server, quote, user=None):
        quotes = MongoClient().brisebois.quotes
        doc = dict(server=server, user=user, quote=quote)
        result = quotes.insert_one(doc)
        return result.inserted_id

    @staticmethod
    def _del_quote(server, quote=None, user=None):
        quotes = MongoClient().brisebois.quotes
        search = dict(server=server, quote=quote, user=user)
        search = {k: v for k, v in search.items() if v}
        result = quotes.delete_many(search)
        return result.deleted_count

    @staticmethod
    def _list_quote(server, user=None, one=False):
        quotes = MongoClient().brisebois.quotes
        search = dict(server=server, user=user)
        search = {k: v for k, v in search.items() if v}
        results = quotes.find(search)
        if one:
            shuffle(results)
            return results[0]
        return results


def setup(bot):
    """Add commands to the bot.

    Args:
        bot: Bot which will add the commands

    Returns:
        None
    """
    bot.add_cog(Quote(bot))
