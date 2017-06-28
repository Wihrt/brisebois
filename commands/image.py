#!/bin/env python
from discord import Embed
from discord.ext import commands
from pymongo import MongoClient
from .utils import date_create, date_check, date_range
from .utils import discord_role


class GetDunkedOn(object):

    def __init__(self, bot):
        self.bot = bot

    @commands.group(pass_context=True,
                    no_pm=True,
                    help="Get Dunked On !")
    async def gdo(self, ctx):
        if ctx.invoked_subcommand is None:
            await self.bot.send_message(
                ctx.message.author,
                "No subcommand specified\n\
Use $help %s to see the list of commands." % ctx.command)
            await self.bot.delete_message(ctx.message)

    @gdo.command(pass_context=True,
                 name="register",
                 no_pm=True,
                 help="Register you to submit daily images")
    async def _user_register(self, ctx):
        result = self._get_user(ctx.message.author.id, ctx.message.server.id)
        if result:
            await self.bot.say(
                "{0.mention} already registered".format(ctx.message.author))
        else:
            self._add_user(ctx.message.author.id, ctx.message.server.id)
            await self.bot.add_roles(ctx.message.author,
                                     discord_role(ctx, "GDO"))
            await self.bot.say(
                "{0.mention} registered".format(ctx.message.author))
        return

    # User commands
    @gdo.command(pass_context=True,
                 name="unregister",
                 no_pm=True,
                 help="Unregister you. You cannot submit daily images anymore")
    @commands.has_role("GDO")
    async def _user_unregister(self, ctx):
        await self._unregister(ctx.message.author, ctx)
        return

    @gdo.command(pass_context=True,
                 name="status",
                 help="Give your status about your profile")
    @commands.has_role("GDO")
    async def _user_status(self, ctx):
        result = self._get_user(ctx.message.author.id, ctx.message.server.id)
        await self._status(ctx.message.author, result, ctx)
        return

    @gdo.command(pass_context=True,
                 name="submit",
                 help="Submit a new image")
    @commands.has_role("GDO")
    async def _user_submit(self, ctx):
        def is_submit_image(msg):
            if len(msg.attachments) is 1:
                for a in msg.attachments:
                    if "width" in a.keys() and "height" in a.keys():
                        return msg

        result = self._get_image(ctx.message.author.id, ctx.message.server.id)
        if result.count() > 0:
            await self.bot.say("You have already submitted an image today !")
        else:
            if is_submit_image(ctx.message):
                msg = ctx.message
            else:
                await self.bot.say("Awaiting submission")
                msg = await self.bot.wait_for_message(
                    author=ctx.message.author, check=is_submit_image)
            for a in msg.attachments:
                self._add_image(ctx.message.author.id, ctx.message.server.id,
                                a["url"], msg.timestamp)
                self._update_user(ctx.message.author.id, ctx.message.server.id,
                                  gold=10, streak=1, days=7)
                await self.bot.say("Submission added")
        return

    @gdo.command(pass_context=True,
                 name="delete",
                 help="Remove the daily image")
    @commands.has_role("GDO")
    async def _user_delete(self, ctx):
        self._del_image(ctx.message.author.id, ctx.message.server.id)
        self._update_user(ctx.message.author.id, ctx.message.server.id,
                          gold=-10, streak=-1, days=6)
        await self.bot.say("Submission deleted")

    @gdo.command(pass_context=True,
                 name="extend",
                 help="Extend your streak 1 month. Costs 100 gold")
    @commands.has_role("GDO")
    async def _user_extend(self, ctx):
        result = self._get_user(ctx.message.author.id, ctx.message.server.id)
        if result["gold"] < 100:
            await self.bot.say("You don't have enough gold to do that !")
        else:
            self._update_user(ctx.message.author.id, ctx.message.server.id,
                              gold=-100, months=1)
            await self.bot.say("Your streak has been extend by 1 month")
        return

    # Moderator commands
    @commands.group(pass_context=True,
                    no_pm=True,
                    help="Get Dunked On ! Moderator side")
    @commands.has_role("GDO Modo")
    async def gdom(self, ctx):
        if ctx.invoked_subcommand is None:
            await self.bot.send_message(
                ctx.message.author,
                "No subcommand specified\n\
Use $help %s to see the list of commands." % ctx.command)
            await self.bot.delete_message(ctx.message)

    @gdom.command(pass_context=True,
                  name="unregister",
                  help="Unregister an user")
    async def _moderator_unregister(self, ctx):
        for user in ctx.message.mentions:
            await self._unregister(user, ctx)
        return

    @gdom.command(pass_context=True,
                  name="status",
                  help="Get the status on user")
    async def _moderator_status(self, ctx):
        for user in ctx.message.mentions:
            result = self._get_user(user.id, ctx.message.server.id)
            if not result:
                await self.bot.say(
                    "{0.mention} is not registered".format(user))
            else:
                await self._status(user, result, ctx)
        return

    @gdom.command(pass_context=True,
                  name="delete",
                  help="Remove submission for users")
    async def _moderator_delete(self, ctx, date):
        if self._check_date(date):
            for user in ctx.message.mentions:

                self._del_image(user.id, ctx.message.server.id, date)
                self._update_user(user.id, ctx.message.server.id,
                                  gold=-10, streak=-1)
                await self.bot.say(
                    "{0.mention}'s submission for {1} deleted".format(
                        user, date))

    # Generic methods
    async def _unregister(self, user, ctx):
        self._del_user(user.id, ctx.message.server.id)
        self._del_image(user.id, ctx.message.server.id)
        await self.bot.remove_roles(user, discord_role(ctx, "GDO"))
        await self.bot.say("{0.mention} unregistered".format(user))

    async def _status(self, user, result, ctx):
        message = Embed(title="{0.name} status".format(user))
        message.add_field(name="Gold", value=result["gold"])
        message.add_field(name="Streak", value=result["streak"])
        message.add_field(name="End of Streak", value=result["end_streak"])
        await self.bot.send_message(ctx.message.channel, embed=message)

    # MongoDB methods
    def _get_user(self, user, server):
        users = MongoClient().brisebois.gdo_users
        search = dict(user=user, server=server)
        result = users.find_one(search)
        return result

    def _add_user(self, user, server):
        users = MongoClient().brisebois.gdo_users
        doc = dict(user=user, server=server, gold=0, streak=0,
                   end_streak=date_create(days=7))
        result = users.insert_one(doc)
        return result.inserted_id

    def _del_user(self, user, server):
        users = MongoClient().brisebois.gdo_users
        search = dict(user=user, server=server)
        result = users.delete_many(search)
        return result.deleted_count

    def _update_user(self, user, server, gold=0, streak=0, days=0, months=0):
        users = MongoClient().brisebois.gdo_users
        search = dict(user=user, server=server)
        update = {"$inc": dict(gold=gold, streak=streak),
                  "$set": dict(end_streak=date_create(days, months))}
        result = users.update_one(search, update)
        result.modified_count

    def _get_image(self, user, server, date=None):
        images = MongoClient().brisebois.gdo_images
        start_date, end_date = date_range(date)
        search = dict(user=user, server=server,
                      date={"$gte": start_date, "$lte": end_date})
        result = images.find(search)
        return result

    def _add_image(self, user, server, url, date):
        images = MongoClient().brisebois.gdo_images
        doc = dict(user=user, server=server, url=url, date=date)
        result = images.insert_one(doc)
        return result.inserted_id

    def _del_image(self, user, server, date=None, all=False):
        images = MongoClient().brisebois.gdo_images
        if date:
            if not date_check(date):
                return None
        search = dict(user=user, server=server)
        if not all:
            start_date, end_date = date_range(date)
            search["date"] = {"$gte": start_date, "$lte": end_date}
        result = images.delete_many(search)
        return result.deleted_count


def setup(bot):
    bot.add_cog(GetDunkedOn(bot))
