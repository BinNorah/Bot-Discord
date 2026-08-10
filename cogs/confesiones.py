import logging

import discord
from discord import app_commands
from discord.ext import commands

import config
from base_datos import db

logger = logging.getLogger("bot")


class Confesiones(commands.Cog):
    """Sistema de confesiones anónimas."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        # Contador incremental por servidor (no se persiste, es decorativo)
        self._contadores = {}

    @commands.hybrid_command(
        name="confesar",
        description="Envía un mensaje anónimo al canal de confesiones."
    )
    @app_commands.describe(mensaje="Tu confesión anónima (nadie sabrá quién la envió)")
    async def confesar(self, ctx: commands.Context, *, mensaje: str):
        # Obtener canal de confesiones
        conf = await db.obtener_configuracion(str(ctx.guild.id))
        if not conf or not conf[6]:  # canal_confesiones_id
            return await ctx.send(
                " No se ha configurado un canal de confesiones. "
                "Un administrador debe usar `/configurar_confesiones #canal`.",
                ephemeral=True
            )

        canal = ctx.guild.get_channel(int(conf[6]))
        if not canal:
            return await ctx.send(
                " No encontré el canal de confesiones configurado. "
                "Un administrador debe reconfigurarlo.",
                ephemeral=True
            )

        # Incrementar contador
        guild_id = str(ctx.guild.id)
        if guild_id not in self._contadores:
            self._contadores[guild_id] = 0
        self._contadores[guild_id] += 1
        numero = self._contadores[guild_id]

        # Eliminar el mensaje del comando si es posible (para proteger anonimato)
        if not ctx.interaction:  # Solo si fue por prefijo
            try:
                await ctx.message.delete()
            except discord.Forbidden:
                pass

        # Crear embed anónimo
        embed = discord.Embed(
            title=f"  Confesión #{numero}",
            description=mensaje,
            color=0x2C2F33  # Gris oscuro "misterioso"
        )
        embed.set_footer(text="Confesión anónima • Usa /confesar para enviar la tuya")
        embed.timestamp = discord.utils.utcnow()

        await canal.send(embed=embed)

        # Confirmar al usuario de forma privada
        await ctx.send(
            " Tu confesión fue enviada de forma anónima. ",
            ephemeral=True
        )

    @commands.hybrid_command(
        name="configurar_confesiones",
        description="Establece el canal donde se enviarán las confesiones anónimas."
    )
    @commands.has_permissions(administrator=True)
    @app_commands.default_permissions(administrator=True)
    @app_commands.describe(canal="El canal de texto para las confesiones")
    async def configurar_confesiones(self, ctx: commands.Context, canal: discord.TextChannel):
        await db.guardar_canal_confesiones(str(ctx.guild.id), str(canal.id))

        embed = discord.Embed(
            title="  Canal de confesiones configurado",
            description=(
                f"Las confesiones anónimas se enviarán a {canal.mention}.\n\n"
                "Los miembros pueden usar `/confesar` para enviar mensajes anónimos."
            ),
            color=config.COLOR_EXITO
        )
        await ctx.send(embed=embed, ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(Confesiones(bot))
