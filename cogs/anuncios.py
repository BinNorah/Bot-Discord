import discord
from discord import app_commands
from discord.ext import commands

import config


class Anuncios(commands.Cog):
    """Sistema de anuncios con embeds profesionales."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.hybrid_command(
        name="anuncio",
        description="Publica un anuncio con un embed profesional en el canal indicado."
    )
    @commands.has_permissions(administrator=True)
    @app_commands.default_permissions(administrator=True)
    @app_commands.describe(
        canal="El canal donde se publicará el anuncio",
        titulo="Título del anuncio",
        mensaje="Contenido del anuncio",
        rol="Rol a mencionar (opcional)"
    )
    async def anuncio(self, ctx: commands.Context, canal: discord.TextChannel,
                      titulo: str, *, mensaje: str, rol: discord.Role = None):
        embed = discord.Embed(
            title=f"📢  {titulo}",
            description=mensaje,
            color=0xFFD700  # Dorado
        )

        if ctx.guild.icon:
            embed.set_thumbnail(url=ctx.guild.icon.url)

        embed.set_footer(
            text=f"Anuncio por {ctx.author.display_name} • {ctx.guild.name}",
            icon_url=ctx.author.display_avatar.url
        )
        embed.timestamp = discord.utils.utcnow()

        # Contenido de mención (fuera del embed para que haga ping)
        contenido_mencion = ""
        if rol:
            contenido_mencion = rol.mention

        await canal.send(content=contenido_mencion or None, embed=embed)

        # Confirmar al admin
        if canal != ctx.channel:
            await ctx.send(
                f"✅ Anuncio publicado en {canal.mention}.",
                ephemeral=True
            )
        else:
            await ctx.send("✅ Anuncio publicado.", ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(Anuncios(bot))
