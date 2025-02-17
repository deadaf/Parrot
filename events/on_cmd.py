from __future__ import annotations

import asyncio
import math
import random
from contextlib import suppress

import discord
from core import Cog, Context, Parrot
from discord.ext import commands
from utilities.exceptions import ParrotCheckFailure

with open("extra/quote.txt") as f:
    quote_ = f.read()

quote = quote_.split("\n")
QUESTION_MARK = "\N{BLACK QUESTION MARK ORNAMENT}"


class ErrorView(discord.ui.View):
    def __init__(self, author_id, *, ctx: Context = None, error: commands.CommandError = None):
        super().__init__(timeout=300.0)
        self.author_id = author_id
        self.ctx = ctx
        self.error = error

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user and interaction.user.id == self.author_id:
            return True
        await interaction.response.send_message(
            "You can't interact with this button", ephemeral=True
        )
        return False

    @discord.ui.button(label="Show full error", style=discord.ButtonStyle.green)
    async def show_full_traceback(self, interaction: discord.Interaction, _: discord.ui.Button):
        await interaction.response.send_message(str(self.error), ephemeral=True)


class Cmd(Cog, command_attrs=dict(hidden=True)):
    """This category is of no use for you, ignore it."""

    def __init__(self, bot: Parrot):
        self.bot = bot
        self.collection = bot.mongo.parrot_db["logging"]

    @Cog.listener()
    async def on_command(self, ctx: Context):
        """This event will be triggered when the command is being completed; triggered by [discord.User]!"""
        if ctx.author.bot:
            return
        collection = self.bot.mongo.parrot_db["cmd_count"]
        await collection.update_one(
            {"_id": ctx.command.qualified_name}, {"$inc": {"count": 1}}, upsert=True
        )

    @Cog.listener()
    async def on_command_completion(self, ctx: Context):
        """Only for logging"""
        if ctx.cog is None:
            return

        if ctx.cog.qualified_name.lower() == "moderator":
            if data := await self.collection.find_one(
                {"_id": ctx.guild.id, "on_mod_commands": {"$exists": True}}
            ):
                webhook: discord.Webhook = discord.Webhook.from_url(
                    data["on_mod_commands"], session=self.bot.http_session
                )
                with suppress(discord.HTTPException):
                    main_content = f"""**On Moderator Command**

`Mod    `: **{ctx.author}**
`Command`: **{ctx.command.qualified_name}**
`Content`: **{ctx.message.content}**
"""
                    await webhook.send(
                        content=main_content,
                        avatar_url=self.bot.user.display_avatar.url,
                        username=self.bot.user.name,
                    )

        elif ctx.cog.qualified_name.lower() == "configuration":
            await self.bot.update_server_config_cache(ctx.guild.id)
            if data := await self.collection.find_one(
                {"_id": ctx.guild.id, "on_config_commands": {"$exists": True}}
            ):
                webhook: discord.Webhook = discord.Webhook.from_url(
                    data["on_config_commands"], session=self.bot.http_session
                )
                with suppress(discord.HTTPException):
                    main_content = f"""**On Config Command**

`Admin  `: **{ctx.author}**
`Command`: **{ctx.command.qualified_name}**
`Content`: **{ctx.message.content}**
"""
                    await webhook.send(
                        content=main_content,
                        avatar_url=self.bot.user.display_avatar.url,
                        username=self.bot.user.name,
                    )

    @Cog.listener()
    async def on_command_error(self, ctx: Context, error: commands.CommandError):
        await self.bot.wait_until_ready()
        # elif command has local error handler, return
        if hasattr(ctx.command, "on_error"):
            return

        # get the original exception
        error = getattr(error, "original", error)

        ignore = (
            commands.CommandNotFound,
            discord.NotFound,
            discord.Forbidden,
            commands.PrivateMessageOnly,
            commands.NotOwner,
        )

        if isinstance(error, ignore):
            return

        ERROR_EMBED = discord.Embed()
        if isinstance(error, commands.BotMissingPermissions):
            missing = [
                perm.replace("_", " ").replace("guild", "server").title()
                for perm in error.missing_permissions
            ]
            if len(missing) > 2:
                fmt = "{}, and {}".format(", ".join(missing[:-1]), missing[-1])
            else:
                fmt = " and ".join(missing)
            ERROR_EMBED.description = (
                f"Please provide the following permission(s) to the bot.```\n{fmt}```"
            )
            ERROR_EMBED.title = f"{QUESTION_MARK} Bot Missing permissions {QUESTION_MARK}"

        elif isinstance(error, commands.CommandOnCooldown):
            ERROR_EMBED.description = (
                f"You are on command cooldown, please retry in **{math.ceil(error.retry_after)}**s"
            )
            ERROR_EMBED.title = f"{QUESTION_MARK} Command On Cooldown {QUESTION_MARK}"

        elif isinstance(error, commands.MissingPermissions):
            missing = [
                perm.replace("_", " ").replace("guild", "server").title()
                for perm in error.missing_permissions
            ]
            if len(missing) > 2:
                fmt = "{}, and {}".format("**, **".join(missing[:-1]), missing[-1])
            else:
                fmt = " and ".join(missing)
            ERROR_EMBED.description = (
                f"You need the following permission(s) to the run the command.```\n{fmt}```"
            )
            ERROR_EMBED.title = f"{QUESTION_MARK} Missing permissions {QUESTION_MARK}"
            ctx.command.reset_cooldown(ctx)

        elif isinstance(error, commands.MissingRole):
            missing = list(error.missing_role)
            if len(missing) > 2:
                fmt = "{}, and {}".format("**, **".join(missing[:-1]), missing[-1])
            else:
                fmt = " and ".join(missing)
            ERROR_EMBED.description = (
                f"You need the the following role(s) to use the command```\n{fmt}```"
            )
            ERROR_EMBED.title = f"{QUESTION_MARK} Missing Role {QUESTION_MARK}"
            ctx.command.reset_cooldown(ctx)

        elif isinstance(error, commands.MissingAnyRole):
            missing = list(error.missing_roles)
            if len(missing) > 2:
                fmt = "{}, and {}".format("**, **".join(missing[:-1]), missing[-1])
            else:
                fmt = " and ".join(missing)
            ERROR_EMBED.description = (
                f"You need the the following role(s) to use the command```\n{fmt}```"
            )
            ERROR_EMBED.title = f"{QUESTION_MARK} Missing Role {QUESTION_MARK}"
            ctx.command.reset_cooldown(ctx)

        elif isinstance(error, commands.NSFWChannelRequired):
            ERROR_EMBED.description = "This command will only run in NSFW marked channel. https://i.imgur.com/oe4iK5i.gif"
            ERROR_EMBED.title = f"{QUESTION_MARK} NSFW Channel Required {QUESTION_MARK}"
            ERROR_EMBED.set_image(url="https://i.imgur.com/oe4iK5i.gif")
            ctx.command.reset_cooldown(ctx)

        elif isinstance(error, commands.BadArgument):
            ctx.command.reset_cooldown(ctx)
            if isinstance(error, commands.MessageNotFound):
                ERROR_EMBED.description = (
                    "Message ID/Link you provied is either invalid or deleted"
                )
                ERROR_EMBED.title = f"{QUESTION_MARK} Message Not Found {QUESTION_MARK}"

            elif isinstance(error, commands.MemberNotFound):
                ERROR_EMBED.description = (
                    "Member ID/Mention/Name you provided is invalid or bot can not see that Member"
                )
                ERROR_EMBED.title = f"{QUESTION_MARK} Member Not Found {QUESTION_MARK}"

            elif isinstance(error, commands.UserNotFound):
                ERROR_EMBED.description = (
                    "User ID/Mention/Name you provided is invalid or bot can not see that User"
                )
                ERROR_EMBED.title = f"{QUESTION_MARK} User Not Found {QUESTION_MARK}"

            elif isinstance(error, commands.ChannelNotFound):
                ERROR_EMBED.description = "Channel ID/Mention/Name you provided is invalid or bot can not see that Channel"
                ERROR_EMBED.title = f"{QUESTION_MARK} Channel Not Found {QUESTION_MARK}"

            elif isinstance(error, commands.RoleNotFound):
                ERROR_EMBED.description = (
                    "Role ID/Mention/Name you provided is invalid or bot can not see that Role"
                )
                ERROR_EMBED.title = f"{QUESTION_MARK} Role Not Found {QUESTION_MARK}"

            elif isinstance(error, commands.EmojiNotFound):
                ERROR_EMBED.description = (
                    "Emoji ID/Name you provided is invalid or bot can not see that Emoji"
                )
                ERROR_EMBED.title = f"{QUESTION_MARK} Emoji Not Found {QUESTION_MARK}"

            ERROR_EMBED.description = f"{error}"
            ERROR_EMBED.title = f"{QUESTION_MARK} Bad Argument {QUESTION_MARK}"

        elif isinstance(
            error,
            (
                commands.MissingRequiredArgument,
                commands.BadUnionArgument,
                commands.TooManyArguments,
            ),
        ):
            command = ctx.command
            ctx.command.reset_cooldown(ctx)
            ERROR_EMBED.description = (
                f"Please use proper syntax.```\n{ctx.clean_prefix}"
                f"{command.qualified_name}{'|' if command.aliases else ''}"
                f"{'|'.join(command.aliases if command.aliases else '')} {command.signature}```"
            )
            ERROR_EMBED.title = f"{QUESTION_MARK} Invalid Syntax {QUESTION_MARK}"

        elif isinstance(error, commands.BadLiteralArgument):
            ERROR_EMBED.description = (
                f"Please use proper Literals."
                f"Literal should be any one of the following: `{'`, `'.join(str(i) for i in error.literals)}`"
            )
            ERROR_EMBED.title = f"{QUESTION_MARK} Invalid Literal(s) {QUESTION_MARK}"

        elif isinstance(error, commands.MaxConcurrencyReached):
            ERROR_EMBED.description = "This command is already running in this server/channel by you. You have wait for it to finish"
            ERROR_EMBED.title = f"{QUESTION_MARK} Max Concurrenry Reached {QUESTION_MARK}"

        elif isinstance(error, ParrotCheckFailure):
            ctx.command.reset_cooldown(ctx)
            ERROR_EMBED.description = f"{error.__str__().format(ctx=ctx)}"
            ERROR_EMBED.title = f"{QUESTION_MARK} Unexpected Error {QUESTION_MARK}"

        elif isinstance(error, commands.CheckAnyFailure):
            ctx.command.reset_cooldown(ctx)
            ERROR_EMBED.description = " or\n".join(
                [error.__str__().format(ctx=ctx) for error in error.errors]
            )
            ERROR_EMBED.title = f"{QUESTION_MARK} Unexpected Error {QUESTION_MARK}"

        elif isinstance(error, asyncio.TimeoutError):
            ERROR_EMBED.description = "Command took too long to respond"
            ERROR_EMBED.title = f"{QUESTION_MARK} Timeout Error {QUESTION_MARK}"

        else:
            ERROR_EMBED.description = f"For some reason **{ctx.command.qualified_name}** is not working. If possible report this error."
            ERROR_EMBED.title = f"{QUESTION_MARK} Well this is embarrassing! {QUESTION_MARK}"

        msg: discord.Message = await ctx.reply(
            random.choice(quote),
            embed=ERROR_EMBED,
        )

        try:
            await ctx.wait_for(
                "message_delete", timeout=10, check=lambda m: m.id == ctx.message.id
            )
        except asyncio.TimeoutError:
            pass
        else:
            await msg.delete(delay=0)
        finally:
            if ERROR_EMBED.title == f"{QUESTION_MARK} Well this is embarrassing! {QUESTION_MARK}":
                raise error


async def setup(bot: Parrot) -> None:
    await bot.add_cog(Cmd(bot))
