import asyncio
import discord
from discord import app_commands
from discord.ext import commands

import config

class AnuncioDurationSelect(discord.ui.Select):
    def __init__(self, mensaje_anuncio: discord.Message):
        self.mensaje_anuncio = mensaje_anuncio
        options = [
            discord.SelectOption(label="1 Hora", value="3600"),
            discord.SelectOption(label="12 Horas", value="43200"),
            discord.SelectOption(label="1 Día", value="86400"),
            discord.SelectOption(label="1 Semana", value="604800"),
            discord.SelectOption(label="Infinito", value="0"),
        ]
        super().__init__(placeholder="¿Cuánto tiempo debe durar el anuncio?", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        duracion = int(self.values[0])
        if duracion == 0:
            await interaction.response.edit_message(content=" Anuncio configurado para durar indefinidamente.", view=None)
            return

        label_seleccionado = next(opt.label for opt in self.options if opt.value == self.values[0])
        await interaction.response.edit_message(content=f" El anuncio se eliminará automáticamente en {label_seleccionado}.", view=None)
        
        async def eliminar_luego():
            await asyncio.sleep(duracion)
            try:
                await self.mensaje_anuncio.delete()
            except discord.NotFound:
                pass

        asyncio.create_task(eliminar_luego())

class AnuncioDurationView(discord.ui.View):
    def __init__(self, mensaje_anuncio):
        super().__init__(timeout=None)
        self.add_item(AnuncioDurationSelect(mensaje_anuncio))


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
            title=f"  {titulo}",
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

        # Contenido de mención (hace ping a @everyone por defecto)
        contenido_mencion = "@everyone"
        if rol:
            contenido_mencion += f" {rol.mention}"

        msg = await canal.send(content=contenido_mencion, embed=embed)

        vista = AnuncioDurationView(msg)
        await ctx.send(" Anuncio publicado. Selecciona su duración:", view=vista, ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(Anuncios(bot))
