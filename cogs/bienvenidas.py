import logging
import os
import discord
from discord.ext import commands

import config
from base_datos import db

logger = logging.getLogger("bot")

# Ruta absoluta a la carpeta gif/, relativa a la ubicación de este archivo,
# para que funcione sin importar desde dónde se ejecute el bot (local o Railway).
DIRECTORIO_BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RUTA_GIF_BIENVENIDA = os.path.join(DIRECTORIO_BASE, "gif", "bienvenida.gif")
RUTA_GIF_DESPEDIDA = os.path.join(DIRECTORIO_BASE, "gif", "despedida.gif")


class Bienvenidas(commands.Cog):
    """Cog para gestionar los mensajes automáticos de bienvenida y despedida."""

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, miembro: discord.Member):
        # --- Obtener el canal de bienvenida desde la base de datos ---
        conf = await db.obtener_configuracion(str(miembro.guild.id))
        if not conf or not conf[0]:
            # El servidor no ha configurado un canal de bienvenida
            return

        canal_id = int(conf[0])
        canal = miembro.guild.get_channel(canal_id)
        if canal is None:
            logger.warning(
                "No se encontró el canal de bienvenida %s en el servidor %s.",
                canal_id,
                miembro.guild.id,
            )
            return

        embed = discord.Embed(
            title=f"¡Bienvenido a {miembro.guild.name}!",
            description="¡Llegaste en hora buena, espero disfrutes del servidor! Durante tu estadía, recuerda cumplir con las reglas.",
            color=config.COLOR_EXITO,
        )

        embed.set_footer(text=f"Norah | Miembros totales: {miembro.guild.member_count}")

        if os.path.exists(RUTA_GIF_BIENVENIDA):
            archivo = discord.File(RUTA_GIF_BIENVENIDA, filename="bienvenida.gif")
            embed.set_image(url="attachment://bienvenida.gif")
            await canal.send(content=f"Bienvenido {miembro.mention} a {miembro.guild.name}!", file=archivo, embed=embed)
        else:
            await canal.send(content=f"Bienvenido {miembro.mention} a {miembro.guild.name}!", embed=embed)

    @commands.Cog.listener()
    async def on_member_remove(self, miembro: discord.Member):
        # --- Obtener el canal de bienvenida desde la base de datos ---
        conf = await db.obtener_configuracion(str(miembro.guild.id))
        if not conf or not conf[0]:
            return

        canal_id = int(conf[0])
        canal = miembro.guild.get_channel(canal_id)
        if canal is None:
            return

        embed = discord.Embed(
            title="¡Hasta pronto!",
            description=f"**{miembro.name}** ha abandonado el servidor. ¡Ojalá vuelvas pronto!",
            color=config.COLOR_ERROR,
        )

        embed.set_footer(text=f"Norah | Ahora somos {miembro.guild.member_count} miembros")

        if os.path.exists(RUTA_GIF_DESPEDIDA):
            archivo = discord.File(RUTA_GIF_DESPEDIDA, filename="despedida.gif")
            embed.set_image(url="attachment://despedida.gif")
            await canal.send(file=archivo, embed=embed)
        else:
            await canal.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Bienvenidas(bot))
