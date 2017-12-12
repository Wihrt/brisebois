#!/bin/env python

"""Quote Commands module"""

from random import shuffle

from discord import Embed
from discord.ext import commands


class Quote(object):
    """Implements Quote commands"""

    def __init__(self, bot):
        self.bot = bot

    @commands.group(no_pm=True)
    async def quote(self, ctx):
        """Say a random quote"""
        if ctx.invoked_subcommand is None:
            row = self._list_quote(ctx.guild, one=True)
            if row:
                user = await self.bot.get_user_info(row[1])
                message = Embed()
                message.add_field(name="Random Quote", value="\"{}\" - {}".format(row[0], user.mention), inline=False)
                await ctx.channel.send(embed=message)

    @quote.command()
    async def add(self, ctx, quote, quoter=None):
        """Add a quote

        Args:
            quote (str): Message to be quoted
            quoter (str): User to be associated with the quote
        """
        if len(ctx.message.mentions) is 1:
            guild, quoter = ctx.guild, ctx.message.mentions[0]
            result = self._add_quote(guild, quote, quoter)
            if result:
                await ctx.channel.send("Quote added")

    @quote.command(name="del")
    async def delete(self, ctx, message):
        """Delete a quote"""
        if len(ctx.message.mentions) is 1:  # There are mentions in the message
            result = self._del_quote(ctx.guild, user=ctx.message.mentions[0].id)
        else:  # It is a quote
            result = self._del_quote(ctx.guild, quote=message)
        if result:
            await ctx.channel.send("Quote deleted")

    @quote.command(no_pm=True)
    async def list(self, ctx, quoter=None):
        """List all quotes

        Args:
            ctx: Context of the message
            quoter: User to list the quotes

        Returns: None
        """
        title = "Quote from {}".format(ctx.guild.name)
        if quoter:
            if len(ctx.message.mentions) is 1:
                quoter = ctx.message.mentions[0]
                user = await self.bot.get_user_info(quoter)
                title = "Quote from {}".format(user.display_name)
        content = str()
        rows = self._list_quote(ctx.guild, quoter)
        if rows:
            for quote, user in self._list_quote(ctx.guild.name, quoter):
                user = await self.bot.get_user_info(user)
                content += "\"{}\" - {}\n".format(quote, user.mention)
            message = Embed()
            message.add_field(name=title, value=content, inline=False)
            await self.bot.send_message(ctx.message.channel, embed=message)

    # MongoDB methods
    def _add_quote(self, server, quote, user=None):
        quotes = self.bot.mongo.brisebois.quotes
        doc = dict(server=server, user=user, quote=quote)
        result = quotes.insert_one(doc)
        return result.inserted_id

    def _del_quote(self, server, quote=None, user=None):
        quotes = self.bot.mongo.brisebois.quotes
        search = dict(server=server, quote=quote, user=user)
        search = {k: v for k, v in search.items() if v}
        result = quotes.delete_many(search)
        return result.deleted_count

    def _list_quote(self, server, user=None, one=False):
        quotes = self.bot.mongo.brisebois.quotes
        search = dict(server=server, user=user)
        search = {k: v for k, v in search.items() if v}
        results = quotes.find(search)
        if one:
            shuffle(results)
            return results[0]
        return results


def setup(bot):
    bot.add_cog(Quote(bot))
