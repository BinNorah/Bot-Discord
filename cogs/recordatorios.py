import re
import time
import logging

import discord
from discord import app_commands
from discord.ext import commands, tasks

import config
from base_datos import db

logger = logging.getLogger("bot")


class Recordatorios(commands.Cog):
    """Sistema de recordatorios personales por DM."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.revisar_recordatorios.start()

    def cog_unload(self):
        self.revisar_recordatorios.cancel()

    @commands.hybrid_command(
        name="recordar",
        description="El bot te enviará un DM cuando pase el tiempo indicado."
    )
    @app_commands.describe(
        tiempo="Cuándo recordarte (ej: 30m, 2h, 1d, 1h30m)",
        mensaje="Qué quieres que te recuerde"
    )
    async def recordar(self, ctx: commands.Context, tiempo: str, *, mensaje: str):
        segundos = self._parsear_tiempo(tiempo)
        if segundos is None or segundos < 10:
            return await ctx.send(
                "❌ Formato de tiempo inválido. Ejemplos: `30m`, `2h`, `1d`, `1h30m`",
                ephemeral=True
            )

        if segundos > 30 * 86400:  # Máximo 30 días
            return await ctx.send(
                "❌ El tiempo máximo es de 30 días.",
                ephemeral=True
            )

        fecha_recordar = time.time() + segundos
        timestamp_discord = int(fecha_recordar)

        await db.crear_recordatorio(
            usuario_id=str(ctx.author.id),
            servidor_id=str(ctx.guild.id),
            canal_id=str(ctx.channel.id),
            mensaje=mensaje,
            fecha_recordar=fecha_recordar
        )

        embed = discord.Embed(
            title="⏰  Recordatorio creado",
            description=(
                f"Te recordaré **<t:{timestamp_discord}:R>**\n\n"
                f"📝 **Mensaje:** {mensaje}"
            ),
            color=config.COLOR_INFO
        )
        embed.set_footer(text="Recibirás un DM cuando sea la hora.")
        await ctx.send(embed=embed, ephemeral=True)

    @tasks.loop(seconds=30)
    async def revisar_recordatorios(self):
        """Revisa periódicamente si hay recordatorios que activar."""
        try:
            ahora = time.time()
            pendientes = await db.obtener_recordatorios_pendientes(ahora)

            for recordatorio in pendientes:
                rec_id, usuario_id, servidor_id, canal_id, mensaje, fecha_recordar = recordatorio

                await db.completar_recordatorio(rec_id)

                # Intentar enviar DM
                try:
                    usuario = await self.bot.fetch_user(int(usuario_id))
                    if usuario:
                        embed = discord.Embed(
                            title="⏰  ¡Recordatorio!",
                            description=f"📝 {mensaje}",
                            color=0xFFD700
                        )
                        embed.set_footer(text="Recordatorio que habías programado")
                        embed.timestamp = discord.utils.utcnow()
                        await usuario.send(embed=embed)
                except discord.Forbidden:
                    # Si no se puede enviar DM, intentar en el canal original
                    try:
                        guild = self.bot.get_guild(int(servidor_id))
                        if guild:
                            canal = guild.get_channel(int(canal_id))
                            if canal:
                                await canal.send(
                                    content=f"<@{usuario_id}>",
                                    embed=discord.Embed(
                                        title="⏰  ¡Recordatorio!",
                                        description=f"📝 {mensaje}\n\n*No pude enviarte un DM, así que te recuerdo aquí.*",
                                        color=0xFFD700
                                    )
                                )
                    except Exception:
                        pass
                except Exception:
                    logger.exception("Error al enviar recordatorio %d", rec_id)

        except Exception:
            logger.exception("Error al revisar recordatorios")

    @revisar_recordatorios.before_loop
    async def antes_de_revisar(self):
        await self.bot.wait_until_ready()

    @staticmethod
    def _parsear_tiempo(texto: str) -> int | None:
        """Convierte texto como '30m', '2h', '1d', '1h30m' a segundos."""
        texto = texto.strip().lower()
        if not texto:
            return None

        # Soportar formatos combinados: 1h30m, 2d12h, etc.
        patron = re.compile(r'(?:(\d+)d)?(?:(\d+)h)?(?:(\d+)m)?(?:(\d+)s)?')
        match = patron.fullmatch(texto)

        if match and any(match.groups()):
            dias = int(match.group(1) or 0)
            horas = int(match.group(2) or 0)
            minutos = int(match.group(3) or 0)
            segundos = int(match.group(4) or 0)
            total = dias * 86400 + horas * 3600 + minutos * 60 + segundos
            return total if total > 0 else None

        # Formato simple: 30m, 2h, 1d
        multiplicadores = {'s': 1, 'm': 60, 'h': 3600, 'd': 86400}
        unidad = texto[-1]
        if unidad in multiplicadores:
            try:
                cantidad = int(texto[:-1])
                return cantidad * multiplicadores[unidad] if cantidad > 0 else None
            except ValueError:
                return None

        return None


async def setup(bot: commands.Bot):
    await bot.add_cog(Recordatorios(bot))
