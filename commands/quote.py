#!/bin/env python
from discord import Embed
from discord.ext import commands
from random import shuffle
import sqlite3


class Quote(object):

    def __init__(self, bot):
        self.bot = bot
        self.db = "db/%s" % "quote.db"
        self._create_table()

    @commands.group(pass_context=True)
    async def quote(self, ctx):
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
        if len(ctx.message.mentions) is 1:
            server, quoter = ctx.message.server.id, ctx.message.mentions[0].id
            result = self._add_quote(server, quote, quoter)
            if result:
                await self.bot.say("Quote added")
        return

    @quote.command(pass_context=True,
                   name="del")
    async def delete(self, ctx, message):
        server = ctx.message.server.id
        # There are mentions in the message
        if len(ctx.message.mentions) is 1:
            result = self._del_quote(server, quoter=ctx.message.mentions[0].id)
        # It is a quote
        else:
            result = self._del_quote(server, quote=message)
        if result:
            await self.bot.say("Quote deleted")
        return

    @quote.command(pass_context=True)
    async def list(self, ctx, quoter=None):
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
        return

    def _create_table(self):
        query = """CREATE TABLE IF NOT EXISTS quotes(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        server VARCHAR(19) NOT NULL,
        quoter VARCHAR(19),
        quote TEXT NOT NULL)"""
        cnx = sqlite3.connect(self.db)
        cursor = cnx.cursor()
        cursor.execute(query)
        cnx.commit()
        cnx.close()

    def _add_quote(self, server, quote, quoter=None):
        output = False
        query = """INSERT INTO quotes (server, quote, quoter)
VALUES(:server, :quote, :quoter)"""
        cnx = sqlite3.connect(self.db)
        cursor = cnx.cursor()
        cursor.execute(query, dict(server=server, quote=quote, quoter=quoter))
        if cursor.rowcount > 0:
            output = True
        cnx.commit()
        cnx.close()
        return output

    def _del_quote(self, server, quote=None, quoter=None):
        output = False
        cnx = sqlite3.connect(self.db)
        cursor = cnx.cursor()
        query = "DELETE FROM quotes WHERE server = :server"
        if quote:
            query += " AND quote LIKE :quote"
        if quoter:
            query += " AND quoter = :quoter"
        cursor.execute(query, dict(server=server, quote=quote, quoter=quoter))
        if cursor.rowcount > 0:
            output = True
        cnx.commit()
        cnx.close()
        return output

    def _list_quote(self, server, quoter=None, one=False):
        query = "SELECT quote, quoter from quotes WHERE server = :server"
        if quoter:
            query += " AND quoter = :quoter"
        cnx = sqlite3.connect(self.db)
        cursor = cnx.cursor()
        cursor.execute(query, dict(server=server, quoter=quoter))
        rows = cursor.fetchall()
        if one:
            shuffle(rows)
            return rows[0]
        return rows


def setup(bot):
    bot.add_cog(Quote(bot))
