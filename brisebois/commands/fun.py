#!/bin/env python

"""Fun Commands module"""

# Imports
from logging import info
from random import randint

from utils.embed import create_embed

from bs4 import BeautifulSoup
from discord.ext import commands
from requests import get, post


class Fun(object):
    """Implements Fun commands"""

    def __init__(self, bot):
        self.bot = bot
        self._giphy_api_key = self.bot.get_api_key("giphy")

    # Commands
    # -------------------------------------------------------------------------
    @commands.command(name="9gag")
    async def gag(self, ctx):
        """Send a random 9gag"""
        response = get("https://9gag.com/random")
        await ctx.channel.send(response.url)

    @commands.command(aliases=["dtc"])
    async def danstonchat(self, ctx):
        """Send random anecdocte from Dans Ton Chat"""
        content = self._danstonchat("https://danstonchat.com/random.html")
        message = create_embed(fields=[content], thumbnail="https://pbs.twimg.com/profile_images/686583650708811776/0ApBhP7G.png")
        await ctx.channel.send(embed=message)

    @commands.command(aliases=["fml"])
    async def fuckmylife(self, ctx):
        """Send random anecdocte from Fuck My Life"""
        content = self._fuckmylife("FML", "https://www.fmylife.com/random")
        message = create_embed(fields=[content], thumbnail="https://99clonescripts.com/wp-content/uploads/2014/05/fml-logo.jpg")
        await ctx.channel.send(embed=message)

    @commands.command(aliases=["gif"])
    async def giphy(self, ctx, *search):
        """Send a random GIF"""
        title, url = self._giphy("http://api.giphy.com/v1/gifs/random", self._giphy_api_key, search)
        message = create_embed(title=title, url=url)
        await ctx.channel.send(embed=message)

    @commands.command(aliases=["ljdc"])
    async def lesjoiesducode(self, ctx):
        """Send a random GIF from Les Joies du Code"""
        title, url = self._lesjoiesducode("http://lesjoiesducode.fr/random")
        message = create_embed(title=title, url=url)
        await ctx.channel.send(embed=message)

    @commands.command()
    async def quote(self, ctx):
        """Send a random quote"""
        quote, author = self._quote("http://api.forismatic.com/api/1.0/")
        message = create_embed(footer=author, fields=[quote])
        await ctx.channel.send(embed=message)

    @commands.command(aliases=["vdm"])
    async def viedemerde(self, ctx):
        """Send random anecdocte from Vie de Merde"""
        content = self._fuckmylife("VDM", "https://www.viedemerde.fr/aleatoire")
        message = create_embed(fields=[content], thumbnail="https://upload.wikimedia.org/wikipedia/commons/f/fc/Logo_vdm.png")
        await ctx.channel.send(embed=message)

    @commands.command()
    async def xkcd(self, ctx):
        """Send a random XKCD"""
        title, url = self._xkcd("https://c.xkcd.com/random/comic/")
        message = create_embed(title=title, url=url)
        await ctx.channel.send(embed=message)

    # Static methods
    # -------------------------------------------------------------------------
    @staticmethod
    def _danstonchat(url):
        response = get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")
        quote = soup.find_all("div", class_="item-content")[randint(1, 25) - 1]
        content = str()
        for elem in quote.a.contents:
            if elem.name == "span":
                content += "`" + elem.getText() + "`"
            if elem.name == "br":
                content += "\n"
            if not elem.name and elem != " ":
                content += elem
        return dict(name="Random DTC", value=content, inline=False)

    @staticmethod
    def _fuckmylife(name, url):
        response = get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")
        tag = soup.find_all("p", class_="block")[0]
        return dict(name="Random {}".format(name.upper()), value=tag.a.getText(), inline=False)

    @staticmethod
    def _giphy(url, api_key, search):
        payload = dict(api_key=api_key)
        title = "Random GIF"
        if search:
            title = "Random \"{}\" GIF".format(" ".join(search))
            payload["tag"] = " ".join(search)
        response = get(url, params=payload)
        r_json = response.json()
        return title, r_json["data"]["image_url"]

    @staticmethod
    def _lesjoiesducode(url):
        response = get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")
        title = soup.find_all("h1", class_="blog-post-title")[0].getText().strip().capitalize()
        img = soup.find_all("div", class_="blog-post-content")[0].find_all("img")[0]["src"]
        return title, img

    @staticmethod
    def _quote(url):
        payload = dict(method="getQuote", format="text", lang="en")
        response = post(url, params=payload)
        response.raise_for_status()
        quote, author = response.text.rstrip(")").split("(")
        return dict(name="Random quote", value=quote, inline=False), dict(text=author)

    @staticmethod
    def _xkcd(url):
        response = get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")
        img = soup.find_all("div", id="comic")[0].find_all("img")[0]
        return img["title"], "https:" + img["src"]


def setup(bot):
    """Add commands to the Bot"""
    bot.add_cog(Fun(bot))
