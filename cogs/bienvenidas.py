import os
import discord
from discord.ext import commands
import config

class Bienvenidas(commands.Cog):
    """Cog para gestionar los mensajes automáticos de bienvenida y despedida."""

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, miembro: discord.Member):
        # --- Envío del mensaje de bienvenida ---
        canal = miembro.guild.get_channel(config.CANAL_BIENVENIDA_ID)
        if canal is None:
            return

        embed = discord.Embed(
            title=f"¡Bienvenido a {miembro.guild.name}!",
            description="¡Llegaste en hora buena, espero disfrutes del servidor! Durante tu estadía, recuerda cumplir con las reglas.",
            color=config.COLOR_EXITO,
        )

        embed.set_footer(text=f"Norah | Miembros totales: {miembro.guild.member_count}")

        # --- Lógica para imagen local ---
        ruta_imagen = r"G:\Mi unidad\Discord\gif\bienvenida.gif"

        if os.path.exists(ruta_imagen):
            archivo = discord.File(ruta_imagen, filename="bienvenida.gif")
            embed.set_image(url="attachment://bienvenida.gif")
            await canal.send(content=f"Bienvenido {miembro.mention} a Hub Central!", file=archivo, embed=embed)
        else:
            await canal.send(content=f"Bienvenido {miembro.mention} a Hub Central!", embed=embed)

    @commands.Cog.listener()
    async def on_member_remove(self, miembro: discord.Member):
        canal = miembro.guild.get_channel(config.CANAL_BIENVENIDA_ID)
        if canal is None:
            return

        embed = discord.Embed(
            title="¡Hasta pronto!",
            description=f"**{miembro.name}** ha abandonado el servidor. ¡Ojalá vuelvas pronto!",
            color=config.COLOR_ERROR,
        )

        embed.set_footer(text=f"Norah | Ahora somos {miembro.guild.member_count} miembros")

        # --- Lógica para imagen local ---
        ruta_imagen = r"G:\Mi unidad\Discord\gif\despedida.gif"

        if os.path.exists(ruta_imagen):
            archivo = discord.File(ruta_imagen, filename="despedida.gif")
            embed.set_image(url="attachment://despedida.gif")
            await canal.send(file=archivo, embed=embed)
        else:
            await canal.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Bienvenidas(bot))