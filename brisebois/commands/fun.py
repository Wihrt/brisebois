#!/bin/env python

"""Fun Commands module"""

# Imports
from random import randint

from bs4 import BeautifulSoup
from discord.ext import commands

from utils.embed import create_embed
from utils.api import ApiKey


class Fun(object):
    """Implements Fun commands"""

    def __init__(self, bot):
        self.bot = bot
        self.mongo_client = self.bot.mongo
        self.mongo_session = self.mongo_client.start_session()
        self.giphy_key = ApiKey(self.mongo_client, self.mongo_session, "giphy").value

    # Commands
    # -------------------------------------------------------------------------
    @commands.command(name="9gag")
    @commands.guild_only()
    async def gag(self, ctx):
        """Send a random 9gag"""
        response = await self.bot.session.get("https://9gag.com/random")
        async with response:
            await ctx.channel.send(response.url)

    @commands.command(aliases=["dtc"])
    @commands.guild_only()
    async def danstonchat(self, ctx):
        """Send a random anecdocte from Dans Ton Chat"""
        response = await self.bot.session.get("https://danstonchat.com/random.html")
        async with response:
            content = await response.text()
            soup = BeautifulSoup(content, "html.parser")
            quote = soup.find_all("div", class_="item-content")[randint(1, 25) - 1]
            content = str()
            for elem in quote.a.contents:
                if elem.name == "span":
                    content += "`" + elem.getText() + "`"
                if elem.name == "br":
                    content += "\n"
                if not elem.name and elem != " ":
                    content += elem
            field = dict(name="Random DTC", value=content, inline=False)
            message = create_embed(dict(fields=field, \
thumbnail="https://pbs.twimg.com/profile_images/686583650708811776/0ApBhP7G.png"))
            await ctx.channel.send(embed=message)

    @commands.command(aliases=["fml"])
    @commands.guild_only()
    async def fuckmylife(self, ctx):
        """Send a random anecdocte from Fuck My Life"""
        response = await self.bot.session.get("https://www.fmylife.com/random")
        async with response:
            content = await response.text()
            soup = BeautifulSoup(content, "html.parser")
            tag = soup.find_all("p", class_="block")[0]
            field = dict(name="Random {}".format("FML"), value=tag.a.getText(), inline=False)
            message = create_embed(dict(fields=field, \
thumbnail="https://99clonescripts.com/wp-content/uploads/2014/05/fml-logo.jpg"))
            await ctx.channel.send(embed=message)

    @commands.command(aliases=["gif"])
    @commands.guild_only()
    async def giphy(self, ctx, *, search=None):
        """Send a random GIF
        You can research a specific tag as well"""
        params = dict(api_key=self.giphy_key)
        title = "Random GIF"
        if search:
            params["tag"] = search
            title = "Random \"{}\" GIF".format(search)
        response = await self.bot.session.get("http://api.giphy.com/v1/gifs/random", params=params)
        async with response:
            content = await response.json()
            message = create_embed(dict(title=title, url=content["data"]["image_url"]))
            await ctx.channel.send(embed=message)

    @commands.command(aliases=["ljdc"])
    @commands.guild_only()
    async def lesjoiesducode(self, ctx):
        """Send a random GIF from Les Joies du Code"""
        response = await self.bot.session.get("http://lesjoiesducode.fr/random")
        async with response:
            content = await response.text()
            soup = BeautifulSoup(content, "html.parser")
            title = soup.find_all("h1", class_="blog-post-title")[0].getText().strip().capitalize()
            url = soup.find_all("div", class_="blog-post-content")[0].find_all("img")[0]["src"]
            message = create_embed(dict(title=title, url=url))
            await ctx.channel.send(embed=message)

    @commands.command()
    @commands.guild_only()
    async def quote(self, ctx):
        """Send a random quote"""
        params = dict(method="getQuote", format="text", lang="en")
        response = await self.bot.session.post("http://api.forismatic.com/api/1.0/", params=params)
        async with response:
            content = await response.text()
            quote, author = content.rstrip(")").split("(")
            quote, author = dict(name="Random quote", value=quote, inline=False), dict(text=author)
            message = create_embed(dict(footer=author, fields=quote))
            await ctx.channel.send(embed=message)

    @commands.command(aliases=["vdm"])
    @commands.guild_only()
    async def viedemerde(self, ctx):
        """Send a random anecdocte from Vie de Merde"""
        response = await self.bot.session.get("http://www.viedemerde.fr/aleatoire")
        async with response:
            content = await response.text()
            soup = BeautifulSoup(content, "html.parser")
            tag = soup.find_all("p", class_="block")[0]
            field = dict(name="Random {}".format("VDM"), value=tag.a.getText(), inline=False)
            message = create_embed(dict(fields=field, \
thumbnail="https://upload.wikimedia.org/wikipedia/commons/f/fc/Logo_vdm.png"))
            await ctx.channel.send(embed=message)

    @commands.command()
    @commands.guild_only()
    async def xkcd(self, ctx):
        """Send a random XKCD comic"""
        response = await self.bot.session.get("https://c.xkcd.com/random/comic/")
        async with response:
            content = await response.text()
            soup = BeautifulSoup(content, "html.parser")
            img = soup.find_all("div", id="comic")[0].find_all("img")[0]
            title, url = img["title"], "https:" + img["src"]
            message = create_embed(dict(title=title, url=url))
            await ctx.channel.send(embed=message)


def setup(bot):
    """Add commands to the Bot"""
    bot.add_cog(Fun(bot))
