#!/bin/env python
from discord.ext import commands


class Modo(object):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True,
                      no_pm=True,
                      help="Change nickname of a member")
    @commands.bot_has_permissions(manage_nicknames=True)
    async def nick(self, ctx, member, nickname=None):
        for m in ctx.message.server.members:
            if m.mentioned_in(ctx.message):
                if m.bot:
                    await self.bot.say("You can't rename a bot !")
                    return
                if m == ctx.message.author:
                    await self.bot.change_nickname(m, nickname)
                    return
                if m != ctx.message.author:
                    for r in ctx.message.author.roles:
                        if r.name in ["Admin", "Modo"]:
                            await self.bot.change_nickname(m, nickname)
                            return


def setup(bot):
    bot.add_cog(Modo(bot))
