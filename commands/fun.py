#!/bin/env python

"""Fun Commands module"""

# Imports
from random import randint

from bs4 import BeautifulSoup
from discord import Embed
from discord.ext import commands
from requests import get


class Fun(object):
    """Implements Fun commands"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True)
    async def fml(self, ctx) -> None:
        """Send random anecdocte from Fuck My Life

        Args:
            ctx: Context of the message

        Return:
            None
        """
        response = get("https://www.fmylife.com/random")
        soup = BeautifulSoup(response.content, "html.parser")
        tag = soup.find_all("p", class_="block")[0]
        message = Embed()
        message.set_thumbnail(url="https://99clonescripts.com/wp-content/\
uploads/2014/05/fml-logo.jpg")
        message.add_field(name="Random FML",
                          value=tag.a.getText(),
                          inline=False)
        await self.bot.send_message(ctx.message.channel, embed=message)

    @commands.command(pass_context=True)
    async def vdm(self, ctx) -> None:
        """Send random anecdocte from Vie de Merde

        Args:
            ctx: Context of the message

        Returns:
            None
        """
        response = get("https://www.viedemerde.fr/aleatoire")
        soup = BeautifulSoup(response.content, "html.parser")
        tag = soup.find_all("p", class_="block")[0]
        message = Embed()
        message.set_thumbnail(url="https://upload.wikimedia.org/wikipedia/\
commons/f/fc/Logo_vdm.png")
        message.add_field(name="Random VDM",
                          value=tag.a.getText(),
                          inline=False)
        await self.bot.send_message(ctx.message.channel, embed=message)

    @commands.command(pass_context=True)
    async def dtc(self, ctx) -> None:
        """Send random anecdocte from Dans Ton Chat

        Args:
            ctx : Context of the message

        Returns : None
        """
        response = get("http://danstonchat.com/random.html")
        soup = BeautifulSoup(response.content, "html.parser")
        quote = soup.find_all("p", class_="item-content")[randint(1, 25) - 1]
        content = ""
        for elem in quote.a.contents:
            if elem.name == "span":
                content += "`" + elem.getText() + "`"
            if elem.name == "br":
                content += "\n"
            if not elem.name and elem != " ":
                content += elem

        message = Embed()
        message.set_thumbnail(url="https://pbs.twimg.com/profile_images/\
686583650708811776/0ApBhP7G.png")
        message.add_field(name="Random DTC", value=content, inline=False)
        await self.bot.send_message(ctx.message.channel, embed=message)

    @commands.command(name="9gag", pass_context=True)
    async def gag(self) -> None:
        """Send a random 9gag

        Args:

        Returns:
            None
        """
        response = get("https://9gag.com/random")
        await self.bot.say(response.url)

    @commands.command(pass_context=True)
    async def gif(self, ctx, search=None) -> None:
        """Send a random gif

        Args:
            ctx: Context of the message
            search (str): Word to search

        Returns:
            None
        """
        payload = {"api_key": "dc6zaTOxFJmzC"}
        title = "Random GIF"
        if search:
            title = "Random \"%s\" GIF" % search
            payload["tag"] = search
        response = get("http://api.giphy.com/v1/gifs/random", params=payload)
        r_json = response.json()
        message = Embed(title=title)
        message.set_image(url=r_json["data"]["image_url"])
        await self.bot.send_message(ctx.message.channel, embed=message)

    @commands.command(pass_context=True)
    async def ljdc(self, ctx) -> None:
        """Send a random Les joies du code GIF

        Args:
            ctx: Context of the message

        Returns:
            None
        """
        response = get("http://lesjoiesducode.fr/random")
        soup = BeautifulSoup(response.content, "html.parser")
        title = soup.find_all(
            "h1", class_="blog-post-title")[0].getText().strip()
        img = soup.find_all(
            "div", class_="blog-post-content")[0].find_all("img")[0]["src"]
        message = Embed(title=title)
        message.set_image(url=img)
        await self.bot.send_message(ctx.message.channel, embed=message)

    @commands.command(pass_context=True)
    async def xkcd(self, ctx) -> None:
        """Send a random XKCD

        Args:
            ctx: Context of the message

        Returns:
            None
        """

        response = get("https://c.xkcd.com/random/comic/")
        soup = BeautifulSoup(response.content, "html.parser")
        img = soup.find_all("div", id="comic")[0].find_all("img")[0]
        message = Embed(title=img["title"])
        message.set_image(url="https:" + img["src"])
        await self.bot.send_message(ctx.message.channel, embed=message)


def setup(bot) -> None:
    """Add commands to the bot.

    Args:
        bot: Bot which will add the commands

    Returns:
        None
    """
    bot.add_cog(Fun(bot))
