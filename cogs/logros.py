import asyncio
import logging

import discord
from discord.ext import commands

import config
from base_datos import db

logger = logging.getLogger("bot")

# Definición de todos los logros
LOGROS = {
    "primer_mensaje": {
        "emoji": "",
        "nombre": "Primer Mensaje",
        "descripcion": "Enviaste tu primer mensaje en el servidor."
    },
    "100_mensajes": {
        "emoji": "",
        "nombre": "Conversador",
        "descripcion": "Alcanzaste 100 mensajes en el servidor."
    },
    "500_mensajes": {
        "emoji": "",
        "nombre": "Parlanchín",
        "descripcion": "Alcanzaste 500 mensajes en el servidor."
    },
    "1000_mensajes": {
        "emoji": "",
        "nombre": "Enciclopedia Viviente",
        "descripcion": "Alcanzaste 1,000 mensajes en el servidor."
    },
    "nivel_5": {
        "emoji": "",
        "nombre": "Nivel 5",
        "descripcion": "Alcanzaste el nivel 5."
    },
    "nivel_10": {
        "emoji": "",
        "nombre": "Nivel 10",
        "descripcion": "Alcanzaste el nivel 10."
    },
    "nivel_25": {
        "emoji": "",
        "nombre": "Nivel 25",
        "descripcion": "Alcanzaste el nivel 25."
    },
    "nivel_50": {
        "emoji": "",
        "nombre": "Nivel 50",
        "descripcion": "Alcanzaste el nivel 50."
    },
    "veterano_30d": {
        "emoji": "",
        "nombre": "Veterano",
        "descripcion": "Llevas 30 días en el servidor."
    },
    "veterano_365d": {
        "emoji": "",
        "nombre": "Leyenda",
        "descripcion": "Llevas 1 año en el servidor."
    },
    "noctambulo": {
        "emoji": "",
        "nombre": "Noctámbulo",
        "descripcion": "Enviaste un mensaje entre las 2 AM y 5 AM."
    },
}


class Logros(commands.Cog):
    """Sistema de logros automáticos por actividad en el servidor."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def _otorgar_y_notificar(self, canal: discord.TextChannel,
                                    miembro: discord.Member,
                                    logro_id: str):
        """Intenta otorgar un logro y notifica si es nuevo."""
        servidor_id = str(miembro.guild.id)
        usuario_id = str(miembro.id)

        nuevo = await db.otorgar_logro(servidor_id, usuario_id, logro_id)
        if nuevo and logro_id in LOGROS:
            logro = LOGROS[logro_id]
            embed = discord.Embed(
                title=f"{logro['emoji']}  ¡Logro desbloqueado!",
                description=(
                    f"**{miembro.display_name}** ha desbloqueado:\n\n"
                    f"**{logro['emoji']} {logro['nombre']}**\n"
                    f"*{logro['descripcion']}*"
                ),
                color=0xFFD700  # Dorado
            )
            embed.set_thumbnail(url=miembro.display_avatar.url)
            embed.set_footer(text="Usa /logros para ver todos tus logros")

            try:
                msg = await canal.send(embed=embed)
                # Borrar automáticamente el logro después de 30 segundos
                await asyncio.sleep(30)
                await msg.delete()
            except Exception:
                pass

    @commands.Cog.listener()
    async def on_message(self, mensaje: discord.Message):
        if mensaje.author.bot or not mensaje.guild:
            return

        servidor_id = str(mensaje.guild.id)
        usuario_id = str(mensaje.author.id)

        # Asegurar que el perfil existe
        await db.obtener_perfil(servidor_id, usuario_id)

        # Incrementar contador de mensajes
        await db.incrementar_mensajes(servidor_id, usuario_id)
        total = await db.obtener_total_mensajes(servidor_id, usuario_id)

        # ─── Logros por mensajes ──────────────────────────────────
        if total == 1:
            await self._otorgar_y_notificar(mensaje.channel, mensaje.author, "primer_mensaje")
        elif total == 100:
            await self._otorgar_y_notificar(mensaje.channel, mensaje.author, "100_mensajes")
        elif total == 500:
            await self._otorgar_y_notificar(mensaje.channel, mensaje.author, "500_mensajes")
        elif total == 1000:
            await self._otorgar_y_notificar(mensaje.channel, mensaje.author, "1000_mensajes")

        # ─── Logro: Noctámbulo (2 AM - 5 AM hora del mensaje) ────
        hora = mensaje.created_at.hour  # UTC
        if 2 <= hora < 5:
            await self._otorgar_y_notificar(mensaje.channel, mensaje.author, "noctambulo")

        # ─── Logros por nivel (leer el nivel actual) ──────────────
        xp, nivel, _, _ = await db.obtener_perfil(servidor_id, usuario_id)
        umbrales_nivel = {5: "nivel_5", 10: "nivel_10", 25: "nivel_25", 50: "nivel_50"}
        for umbral, logro_id in umbrales_nivel.items():
            if nivel >= umbral:
                # Otorgar silenciosamente (no notificar si ya lo tiene)
                await db.otorgar_logro(servidor_id, usuario_id, logro_id)

        # ─── Logro: Veterano (30 días / 365 días) ─────────────────
        if mensaje.author.joined_at:
            dias = (discord.utils.utcnow() - mensaje.author.joined_at).days
            if dias >= 30:
                await self._otorgar_y_notificar(mensaje.channel, mensaje.author, "veterano_30d")
            if dias >= 365:
                await self._otorgar_y_notificar(mensaje.channel, mensaje.author, "veterano_365d")

    @commands.hybrid_command(
        name="logros",
        description="Muestra los logros desbloqueados de un usuario."
    )
    async def logros(self, ctx: commands.Context, miembro: discord.Member = None):
        usuario = miembro or ctx.author

        if usuario.bot:
            return await ctx.send("Los bots no tienen logros.", ephemeral=True)

        logros_usuario = await db.obtener_logros_usuario(str(ctx.guild.id), str(usuario.id))

        logros_ids = {l[0] for l in logros_usuario}
        total_disponibles = len(LOGROS)
        total_desbloqueados = len(logros_ids)

        embed = discord.Embed(
            title=f"  Logros de {usuario.display_name}",
            description=f"**{total_desbloqueados}/{total_disponibles}** logros desbloqueados",
            color=0xFFD700 if total_desbloqueados > 0 else config.COLOR_INFO
        )
        embed.set_thumbnail(url=usuario.display_avatar.url)

        # Barra de progreso
        porcentaje = int((total_desbloqueados / total_disponibles) * 10) if total_disponibles > 0 else 0
        barra = "" * porcentaje + "" * (10 - porcentaje)
        embed.add_field(
            name="Progreso",
            value=f"{barra} ({total_desbloqueados}/{total_disponibles})",
            inline=False
        )

        # Listar logros
        for logro_id, logro_info in LOGROS.items():
            if logro_id in logros_ids:
                # Buscar la fecha
                fecha = next((l[1] for l in logros_usuario if l[0] == logro_id), "")
                fecha_str = f" — *{fecha.split()[0]}*" if fecha else ""
                valor = f" {logro_info['descripcion']}{fecha_str}"
            else:
                valor = f" *{logro_info['descripcion']}*"

            embed.add_field(
                name=f"{logro_info['emoji']}  {logro_info['nombre']}",
                value=valor,
                inline=True
            )

        await ctx.send(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(Logros(bot))
