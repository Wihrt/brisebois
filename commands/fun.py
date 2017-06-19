#!/bin/env python
from bs4 import BeautifulSoup
from discord import Embed
from discord.ext import commands
from random import randint
from requests import get


class Fun(object):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True,
                      help="Send random anecdocte from Fuck My Life")
    async def fml(self, ctx):
        response = get("https://www.fmylife.com/random")
        soup = BeautifulSoup(response.content, "html.parser")
        tag = soup.find_all("p", class_="block")[0]
        message = Embed()
        message.add_field(name="Random FML", value=tag.a.getText(),
                          inline=False)
        await self.bot.send_message(ctx.message.channel, embed=message)

    @commands.command(pass_context=True,
                      help="Sand random anecdocte from Vie de Merde")
    async def vdm(self, ctx):
        response = get("https://www.viedemerde.fr/aleatoire")
        soup = BeautifulSoup(response.content, "html.parser")
        tag = soup.find_all("p", class_="block")[0]
        message = Embed()
        message.add_field(name="Random VDM", value=tag.a.getText(),
                          inline=False)
        await self.bot.send_message(ctx.message.channel, embed=message)

    @commands.command(pass_context=True,
                      help="Send random anecdocte from Dans Ton Chat")
    async def dtc(self, ctx, number=None):
        if number:
            number = int(number)
            if number not in range(1, 26):
                return await self.bot.say(
                    "Warning ! The number must be between 1 and 25")

        response = get("http://danstonchat.com/random.html")
        soup = BeautifulSoup(response.content, "html.parser")
        if not number:
            number = randint(1, 25)
        tag = soup.find_all("p", class_="item-content")[number - 1]
        content = ""
        for t in tag.a.contents:
            if t.name == "span":
                content += "`" + t.getText() + "`"
            if t.name == "br":
                content += "\n"
            if not t.name and t != " ":
                content += t

        message = Embed()
        message.add_field(name="Random DTC", value=content, inline=False)
        await self.bot.send_message(ctx.message.channel, embed=message)

    @commands.command(pass_context=True,
                      help="Send a random 9gag")
    async def gag(self, ctx):
        response = get("https://9gag.com/random")
        await self.bot.say(response.url)

    @commands.command(pass_context=True,
                      help="Send random gif")
    async def gif(self, ctx, search=None):
        payload = {"api_key": "dc6zaTOxFJmzC"}
        title = "Random GIF"
        if search:
            title = "Random " + search + " GIF"
            payload["tag"] = search
        response = get("http://api.giphy.com/v1/gifs/random", params=payload)
        r_json = response.json()
        message = Embed(title=title)
        message.set_image(url=r_json["data"]["image_url"])
        await self.bot.send_message(ctx.message.channel, embed=message)

    @commands.command(pass_context=True,
                      help="Send a random Les joies du code GIF")
    async def ljdc(self, ctx):
        response = get("http://lesjoiesducode.fr/random")
        soup = BeautifulSoup(response.content, "html.parser")
        title = soup.find_all(
            "h1", class_="blog-post-title")[0].getText().strip()
        img = soup.find_all(
            "div", class_="blog-post-content")[0].find_all("img")[0]["src"]
        message = Embed(title=title)
        message.set_image(url=img)
        await self.bot.send_message(ctx.message.channel, embed=message)


def setup(bot):
    bot.add_cog(Fun(bot))
