import json
import time
import logging
import datetime
from collections import defaultdict

import discord
from discord import app_commands
from discord.ext import commands

import config
from base_datos import db

logger = logging.getLogger("bot")

# Expresión regular para detectar URLs
import re
URL_REGEX = re.compile(
    r'https?://[^\s<>"{}|\\^`\[\]]+',
    re.IGNORECASE
)


class AntiSpam(commands.Cog):
    """Sistema anti-spam y automod para proteger el servidor."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        # Cache en memoria: {guild_id: {user_id: [timestamps]}}
        self._mensajes_recientes = defaultdict(lambda: defaultdict(list))
        # Cache de mensajes para detectar repetidos: {guild_id: {user_id: [contenidos]}}
        self._contenidos_recientes = defaultdict(lambda: defaultdict(list))
        # Strikes por usuario: {guild_id: {user_id: int}}
        self._strikes = defaultdict(lambda: defaultdict(int))
        # Cache de configuración: {guild_id: (activado, config)}
        self._config_cache = {}

    async def _obtener_config(self, guild_id: str) -> tuple:
        """Obtiene la config anti-spam (con cache de 60s)."""
        ahora = time.time()
        if guild_id in self._config_cache:
            datos, timestamp = self._config_cache[guild_id]
            if ahora - timestamp < 60:
                return datos

        conf = await db.obtener_configuracion(guild_id)
        if conf and conf[9]:  # antispam_activado
            try:
                cfg = json.loads(conf[10]) if conf[10] else {}
            except (json.JSONDecodeError, TypeError):
                cfg = {}
            resultado = (True, cfg)
        else:
            resultado = (False, {})

        self._config_cache[guild_id] = (resultado, ahora)
        return resultado

    @commands.Cog.listener()
    async def on_message(self, mensaje: discord.Message):
        if not mensaje.guild or mensaje.author.bot:
            return

        # Verificar si el autor tiene permisos de moderación (no aplicar anti-spam)
        if mensaje.author.guild_permissions.manage_messages:
            return

        guild_id = str(mensaje.guild.id)
        activado, cfg = await self._obtener_config(guild_id)
        if not activado:
            return

        usuario_id = str(mensaje.author.id)
        ahora = time.time()
        infraccion = None

        # ─── Detección 1: Flood (5+ mensajes en 5 segundos) ──────
        if cfg.get("flood", True):
            timestamps = self._mensajes_recientes[guild_id][usuario_id]
            timestamps.append(ahora)
            # Limpiar mensajes antiguos (más de 5 segundos)
            self._mensajes_recientes[guild_id][usuario_id] = [
                t for t in timestamps if ahora - t < 5
            ]
            if len(self._mensajes_recientes[guild_id][usuario_id]) >= 5:
                infraccion = "🚫 **Flood detectado** — Estás enviando mensajes demasiado rápido."
                self._mensajes_recientes[guild_id][usuario_id].clear()

        # ─── Detección 2: Links no permitidos ─────────────────────
        if not infraccion and cfg.get("links", True):
            whitelist = cfg.get("whitelist_links", [
                "discord.gg", "discord.com", "tenor.com", "giphy.com",
                "youtube.com", "youtu.be", "twitch.tv", "twitter.com",
                "x.com", "instagram.com", "reddit.com", "github.com",
                "spotify.com"
            ])
            urls = URL_REGEX.findall(mensaje.content)
            for url in urls:
                permitida = any(dominio in url.lower() for dominio in whitelist)
                if not permitida:
                    infraccion = "🔗 **Link no permitido detectado** — No puedes compartir ese enlace aquí."
                    break

        # ─── Detección 3: Texto repetido (3+ mensajes idénticos) ──
        if not infraccion and cfg.get("repetidos", True):
            contenidos = self._contenidos_recientes[guild_id][usuario_id]
            contenidos.append(mensaje.content.lower().strip())
            # Mantener solo los últimos 5
            if len(contenidos) > 5:
                self._contenidos_recientes[guild_id][usuario_id] = contenidos[-5:]
            contenidos = self._contenidos_recientes[guild_id][usuario_id]
            if len(contenidos) >= 3 and all(c == contenidos[-1] for c in contenidos[-3:]):
                infraccion = "🔁 **Mensaje repetido detectado** — No envíes el mismo mensaje varias veces."
                self._contenidos_recientes[guild_id][usuario_id].clear()

        # ─── Detección 4: Mentions masivas (5+ en un mensaje) ─────
        if not infraccion and cfg.get("menciones", True):
            total_mentions = len(mensaje.mentions) + len(mensaje.role_mentions)
            if total_mentions >= 5:
                infraccion = "📢 **Exceso de menciones** — No puedes mencionar a tantas personas/roles a la vez."

        # ─── Acción: eliminar mensaje + advertencia ───────────────
        if infraccion:
            try:
                await mensaje.delete()
            except discord.Forbidden:
                pass

            self._strikes[guild_id][usuario_id] += 1
            strikes = self._strikes[guild_id][usuario_id]

            # Notificar al usuario
            embed = discord.Embed(
                title="⚠️  Anti-Spam",
                description=f"{infraccion}\n\n**Advertencia {strikes}/3**",
                color=config.COLOR_ADVERTENCIA
            )
            embed.set_footer(text="Al llegar a 3 advertencias serás silenciado temporalmente.")

            try:
                aviso = await mensaje.channel.send(
                    content=mensaje.author.mention,
                    embed=embed
                )
                await aviso.delete(delay=8)
            except Exception:
                pass

            # Al 3er strike: mute temporal (10 minutos)
            if strikes >= 3:
                self._strikes[guild_id][usuario_id] = 0
                try:
                    duracion = datetime.timedelta(minutes=10)
                    await mensaje.author.timeout(
                        duracion,
                        reason="Anti-spam: 3 infracciones automáticas"
                    )

                    embed_mute = discord.Embed(
                        title="🔇  Silencio automático",
                        description=(
                            f"{mensaje.author.mention} ha sido silenciado por **10 minutos** "
                            f"por infracciones repetidas de anti-spam."
                        ),
                        color=config.COLOR_ERROR
                    )
                    await mensaje.channel.send(embed=embed_mute)
                except discord.Forbidden:
                    pass

            # Log al canal modlog
            conf = await db.obtener_configuracion(guild_id)
            if conf and conf[1]:
                canal_log = mensaje.guild.get_channel(int(conf[1]))
                if canal_log:
                    embed_log = discord.Embed(
                        title="🛡️  Anti-Spam — Infracción",
                        description=(
                            f"**Usuario:** {mensaje.author.mention}\n"
                            f"**Canal:** {mensaje.channel.mention}\n"
                            f"**Razón:** {infraccion}\n"
                            f"**Strike:** {strikes}/3\n"
                            f"**Contenido:** {mensaje.content[:200] if mensaje.content else '*sin texto*'}"
                        ),
                        color=config.COLOR_ADVERTENCIA
                    )
                    embed_log.timestamp = discord.utils.utcnow()
                    try:
                        await canal_log.send(embed=embed_log)
                    except Exception:
                        pass

    @commands.hybrid_command(
        name="antispam",
        description="Activa o desactiva el sistema anti-spam del servidor."
    )
    @commands.has_permissions(administrator=True)
    @app_commands.default_permissions(administrator=True)
    @app_commands.describe(accion="Activar o desactivar el anti-spam")
    @app_commands.choices(accion=[
        app_commands.Choice(name="Activar", value="activar"),
        app_commands.Choice(name="Desactivar", value="desactivar"),
    ])
    async def antispam(self, ctx: commands.Context, accion: str):
        guild_id = str(ctx.guild.id)
        activar = accion == "activar"

        config_defecto = json.dumps({
            "flood": True,
            "links": True,
            "repetidos": True,
            "menciones": True,
            "whitelist_links": [
                "discord.gg", "discord.com", "tenor.com", "giphy.com",
                "youtube.com", "youtu.be", "twitch.tv", "twitter.com",
                "x.com", "instagram.com", "reddit.com", "github.com",
                "spotify.com"
            ]
        })

        await db.guardar_antispam(guild_id, 1 if activar else 0, config_defecto)

        # Invalidar cache
        if guild_id in self._config_cache:
            del self._config_cache[guild_id]

        estado = "✅ activado" if activar else "❌ desactivado"
        embed = discord.Embed(
            title=f"🛡️  Anti-Spam {estado}",
            description=(
                "**Filtros activos:**\n"
                "• 🚫 Flood (5+ msgs en 5s)\n"
                "• 🔗 Links no permitidos\n"
                "• 🔁 Mensajes repetidos\n"
                "• 📢 Menciones masivas (5+)\n\n"
                "**Acción:** Eliminar mensaje + advertencia\n"
                "**3 strikes** → Silencio de 10 minutos"
            ) if activar else "El sistema anti-spam ha sido desactivado.",
            color=config.COLOR_EXITO if activar else config.COLOR_ADVERTENCIA
        )
        await ctx.send(embed=embed, ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(AntiSpam(bot))
