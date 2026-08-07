import random
import time
import logging

import discord
from discord import app_commands
from discord.ext import commands, tasks

import config
from base_datos import db

logger = logging.getLogger("bot")


class Sorteos(commands.Cog):
    """Sistema de sorteos (giveaways) con reacciones y selección automática de ganadores."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.revisar_sorteos.start()

    def cog_unload(self):
        self.revisar_sorteos.cancel()

    @commands.hybrid_command(
        name="sorteo",
        description="Crea un sorteo con reacciones. Los participantes reaccionan con 🎉."
    )
    @commands.has_permissions(manage_guild=True)
    @app_commands.default_permissions(manage_guild=True)
    @app_commands.describe(
        duracion="Duración del sorteo (ej: 30m, 2h, 1d)",
        premio="Lo que se sortea",
        ganadores="Cantidad de ganadores (por defecto 1)"
    )
    async def sorteo(self, ctx: commands.Context, duracion: str, *, premio: str,
                     ganadores: int = 1):
        # Parsear la duración
        segundos = self._parsear_tiempo(duracion)
        if segundos is None or segundos < 10:
            return await ctx.send(
                "❌ Formato de duración inválido. Usa: `30s`, `10m`, `2h`, `1d`",
                ephemeral=True
            )

        if ganadores < 1 or ganadores > 20:
            return await ctx.send("❌ La cantidad de ganadores debe ser entre 1 y 20.", ephemeral=True)

        fecha_fin = time.time() + segundos
        timestamp_discord = int(fecha_fin)

        embed = discord.Embed(
            title="🎉  ¡SORTEO!  🎉",
            description=(
                f"**Premio:** {premio}\n\n"
                f"**Reacciona con** 🎉 **para participar!**\n\n"
                f"⏰ **Termina:** <t:{timestamp_discord}:R>\n"
                f"🏆 **Ganadores:** {ganadores}\n"
                f"👤 **Organizado por:** {ctx.author.mention}"
            ),
            color=0xFF69B4  # Rosa
        )
        embed.set_footer(text=f"Sorteo de {ctx.guild.name}")
        embed.timestamp = discord.utils.utcnow()

        if ctx.guild.icon:
            embed.set_thumbnail(url=ctx.guild.icon.url)

        msg = await ctx.send(embed=embed)
        await msg.add_reaction("🎉")

        # Guardar en BD
        await db.crear_sorteo(
            servidor_id=str(ctx.guild.id),
            canal_id=str(ctx.channel.id),
            mensaje_id=str(msg.id),
            premio=premio,
            organizador_id=str(ctx.author.id),
            fecha_fin=fecha_fin,
            ganadores_count=ganadores
        )

        logger.info("Sorteo creado: '%s' en servidor %s (termina en %ds)",
                     premio, ctx.guild.id, segundos)

    @commands.hybrid_command(
        name="re_sorteo",
        description="Repite un sorteo ya finalizado con nuevos ganadores."
    )
    @commands.has_permissions(manage_guild=True)
    @app_commands.default_permissions(manage_guild=True)
    @app_commands.describe(mensaje_id="ID del mensaje del sorteo original")
    async def re_sorteo(self, ctx: commands.Context, mensaje_id: str):
        sorteo = await db.obtener_sorteo_por_mensaje(mensaje_id)
        if not sorteo:
            return await ctx.send("❌ No encontré un sorteo con ese ID de mensaje.", ephemeral=True)

        _, servidor_id, canal_id, _, premio, _, _, ganadores_count = sorteo
        canal = ctx.guild.get_channel(int(canal_id))
        if not canal:
            return await ctx.send("❌ No encontré el canal del sorteo original.", ephemeral=True)

        try:
            msg = await canal.fetch_message(int(mensaje_id))
        except discord.NotFound:
            return await ctx.send("❌ No encontré el mensaje del sorteo.", ephemeral=True)

        # Obtener participantes
        participantes = []
        for reaction in msg.reactions:
            if str(reaction.emoji) == "🎉":
                async for user in reaction.users():
                    if not user.bot:
                        participantes.append(user)
                break

        if not participantes:
            return await ctx.send("❌ No hay participantes en este sorteo.", ephemeral=True)

        ganadores_seleccionados = random.sample(
            participantes, min(ganadores_count, len(participantes))
        )
        menciones = ", ".join(g.mention for g in ganadores_seleccionados)

        embed = discord.Embed(
            title="🎉  ¡RE-SORTEO!  🎉",
            description=f"**Premio:** {premio}\n\n🏆 **Nuevos ganadores:** {menciones}",
            color=0xFFD700
        )
        await canal.send(embed=embed)
        await ctx.send("✅ Re-sorteo completado.", ephemeral=True)

    @tasks.loop(seconds=30)
    async def revisar_sorteos(self):
        """Revisa periódicamente si hay sorteos que ya terminaron."""
        try:
            sorteos = await db.obtener_sorteos_activos()
            ahora = time.time()

            for sorteo in sorteos:
                sorteo_id, servidor_id, canal_id, mensaje_id, premio, organizador_id, fecha_fin, ganadores_count = sorteo

                if ahora < fecha_fin:
                    continue  # Aún no termina

                # Finalizar sorteo
                await db.finalizar_sorteo(sorteo_id)

                guild = self.bot.get_guild(int(servidor_id))
                if not guild:
                    continue

                canal = guild.get_channel(int(canal_id))
                if not canal:
                    continue

                try:
                    msg = await canal.fetch_message(int(mensaje_id))
                except discord.NotFound:
                    continue

                # Obtener participantes de la reacción 🎉
                participantes = []
                for reaction in msg.reactions:
                    if str(reaction.emoji) == "🎉":
                        async for user in reaction.users():
                            if not user.bot:
                                participantes.append(user)
                        break

                if not participantes:
                    embed = discord.Embed(
                        title="🎉  Sorteo Finalizado  🎉",
                        description=f"**Premio:** {premio}\n\n😢 No hubo participantes.",
                        color=0x808080
                    )
                    await canal.send(embed=embed)
                    continue

                ganadores_seleccionados = random.sample(
                    participantes, min(ganadores_count, len(participantes))
                )
                menciones = ", ".join(g.mention for g in ganadores_seleccionados)

                embed = discord.Embed(
                    title="🎉  ¡SORTEO FINALIZADO!  🎉",
                    description=(
                        f"**Premio:** {premio}\n\n"
                        f"🏆 **{'Ganadores' if len(ganadores_seleccionados) > 1 else 'Ganador'}:** {menciones}\n\n"
                        f"¡Felicidades! 🥳"
                    ),
                    color=0x2ECC71
                )
                embed.set_footer(text=f"Organizado por ID: {organizador_id}")
                await canal.send(content=menciones, embed=embed)

                # Editar el mensaje original para mostrar que terminó
                try:
                    embed_original = msg.embeds[0] if msg.embeds else discord.Embed()
                    embed_original.title = "🎉  SORTEO FINALIZADO  🎉"
                    embed_original.color = 0x808080
                    embed_original.set_footer(text="Este sorteo ha terminado.")
                    await msg.edit(embed=embed_original)
                except Exception:
                    pass

        except Exception:
            logger.exception("Error al revisar sorteos")

    @revisar_sorteos.before_loop
    async def antes_de_revisar(self):
        await self.bot.wait_until_ready()

    @staticmethod
    def _parsear_tiempo(texto: str) -> int | None:
        """Convierte texto como '30m', '2h', '1d' a segundos."""
        texto = texto.strip().lower()
        multiplicadores = {'s': 1, 'm': 60, 'h': 3600, 'd': 86400}

        if not texto:
            return None

        unidad = texto[-1]
        if unidad not in multiplicadores:
            return None

        try:
            cantidad = int(texto[:-1])
            if cantidad <= 0:
                return None
            return cantidad * multiplicadores[unidad]
        except ValueError:
            return None


async def setup(bot: commands.Bot):
    await bot.add_cog(Sorteos(bot))
