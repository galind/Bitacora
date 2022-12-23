from discord.ext import commands

from bot import Bitacora


class Owner(commands.Cog):
    """Owner-only commands to manage the extensions."""

    def __init__(self, bot: Bitacora):
        self.bot = bot
        self.delay = 10  # Seconds to wait to delete a message

    async def cog_check(self, ctx: commands.Context) -> bool:
        return await self.bot.is_owner(ctx.author)

    @commands.command(name='load', hidden=True)
    async def load(self, ctx: commands.Context, module: str):
        """Loads a module."""
        try:
            await self.bot.load_extension(f'cogs.{module}')
        except commands.ExtensionError as e:
            await ctx.send(
                f'{e.__class__.__name__}: {e}',
                delete_after=self.delay
            )
        else:
            await ctx.send(
                f'Module \'{module}\' loaded.',
                delete_after=self.delay
            )
        await ctx.message.delete(delay=self.delay)

    @commands.command(name='unload', hidden=True)
    async def unload(self, ctx: commands.Context, module: str):
        """Unloads a module."""
        try:
            await self.bot.unload_extension(f'cogs.{module}')
        except commands.ExtensionError as e:
            await ctx.send(
                f'{e.__class__.__name__}: {e}',
                delete_after=self.delay
            )
        else:
            await ctx.send(
                f'Module \'{module}\' unloaded.',
                delete_after=self.delay
            )
        await ctx.message.delete(delay=self.delay)

    @commands.command(name='reload', hidden=True)
    async def reload(self, ctx: commands.Context, module: str):
        """Reloads a module."""
        try:
            await self.bot.reload_extension(f'cogs.{module}')
        except commands.ExtensionError as e:
            await ctx.send(
                f'{e.__class__.__name__}: {e}',
                delete_after=self.delay
            )
        else:
            await ctx.send(
                f'Module \'{module}\' reloaded.',
                delete_after=self.delay
            )
        await ctx.message.delete(delay=self.delay)

    @commands.command(name='sync', hidden=True)
    async def sync(self, ctx: commands.Context, target: str):
        """Syncs the slash commands."""
        if target == 'global':
            guild = None
        elif target == 'guild':
            guild = ctx.guild
        else:
            return await ctx.send(
                'You need to specify the sync target',
                delete_after=self.delay
            )

        commands = await self.bot.tree.sync(guild=guild)
        await ctx.send(
            f'Successfully synced {len(commands)} commands',
            delete_after=self.delay
        )
        await ctx.message.delete(delay=self.delay)
