import logging

import discord
from discord import app_commands
from discord.ext import commands

import config
from base_datos import db

logger = logging.getLogger("bot")

# Colores por tipo de evento
COLORES_LOG = {
    "edicion": 0x3498DB,      # Azul
    "eliminacion": 0xE74C3C,  # Rojo
    "nickname": 0xF1C40F,     # Amarillo
    "roles": 0x9B59B6,        # Morado
    "voz": 0x2ECC71,          # Verde
    "ban": 0xE74C3C,          # Rojo
    "unban": 0x2ECC71,        # Verde
}


class LogsAvanzados(commands.Cog):
    """Sistema de logs avanzados que registra eventos del servidor."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def _obtener_canal_logs(self, guild: discord.Guild) -> discord.TextChannel | None:
        """Obtiene el canal de logs avanzados configurado."""
        conf = await db.obtener_configuracion(str(guild.id))
        if conf and conf[8]:  # canal_logs_id
            return guild.get_channel(int(conf[8]))
        return None

    # ─── Edición de mensajes ──────────────────────────────────────────

    @commands.Cog.listener()
    async def on_message_edit(self, antes: discord.Message, despues: discord.Message):
        if not antes.guild or antes.author.bot:
            return
        if antes.content == despues.content:
            return  # Solo cambió un embed o similar

        canal_log = await self._obtener_canal_logs(antes.guild)
        if not canal_log:
            return

        contenido_antes = antes.content[:500] if antes.content else "*vacío*"
        contenido_despues = despues.content[:500] if despues.content else "*vacío*"

        embed = discord.Embed(
            title="  Mensaje editado",
            color=COLORES_LOG["edicion"]
        )
        embed.add_field(name="Autor", value=antes.author.mention, inline=True)
        embed.add_field(name="Canal", value=antes.channel.mention, inline=True)
        embed.add_field(name="Antes", value=contenido_antes, inline=False)
        embed.add_field(name="Después", value=contenido_despues, inline=False)
        embed.set_footer(text=f"ID del mensaje: {antes.id}")
        embed.timestamp = discord.utils.utcnow()

        try:
            await canal_log.send(embed=embed)
        except Exception:
            pass

    # ─── Eliminación de mensajes ──────────────────────────────────────

    @commands.Cog.listener()
    async def on_message_delete(self, mensaje: discord.Message):
        if not mensaje.guild or mensaje.author.bot:
            return

        canal_log = await self._obtener_canal_logs(mensaje.guild)
        if not canal_log:
            return

        contenido = mensaje.content[:800] if mensaje.content else "*sin texto*"

        embed = discord.Embed(
            title="  Mensaje eliminado",
            color=COLORES_LOG["eliminacion"]
        )
        embed.add_field(name="Autor", value=mensaje.author.mention, inline=True)
        embed.add_field(name="Canal", value=mensaje.channel.mention, inline=True)
        embed.add_field(name="Contenido", value=contenido, inline=False)

        # Mostrar archivos adjuntos si los había
        if mensaje.attachments:
            archivos = "\n".join(a.filename for a in mensaje.attachments)
            embed.add_field(name="Archivos adjuntos", value=archivos, inline=False)

        embed.set_footer(text=f"ID del mensaje: {mensaje.id} | ID del autor: {mensaje.author.id}")
        embed.timestamp = discord.utils.utcnow()

        try:
            await canal_log.send(embed=embed)
        except Exception:
            pass

    # ─── Cambios de miembro (nickname, roles) ─────────────────────────

    @commands.Cog.listener()
    async def on_member_update(self, antes: discord.Member, despues: discord.Member):
        if antes.bot:
            return

        canal_log = await self._obtener_canal_logs(antes.guild)
        if not canal_log:
            return

        # Cambio de nickname
        if antes.nick != despues.nick:
            embed = discord.Embed(
                title="  Cambio de apodo",
                color=COLORES_LOG["nickname"]
            )
            embed.add_field(name="Usuario", value=despues.mention, inline=True)
            embed.add_field(name="Antes", value=antes.nick or "*sin apodo*", inline=True)
            embed.add_field(name="Después", value=despues.nick or "*sin apodo*", inline=True)
            embed.set_thumbnail(url=despues.display_avatar.url)
            embed.timestamp = discord.utils.utcnow()
            try:
                await canal_log.send(embed=embed)
            except Exception:
                pass

        # Cambio de roles
        roles_antes = set(antes.roles)
        roles_despues = set(despues.roles)

        roles_agregados = roles_despues - roles_antes
        roles_removidos = roles_antes - roles_despues

        if roles_agregados or roles_removidos:
            embed = discord.Embed(
                title="  Cambio de roles",
                color=COLORES_LOG["roles"]
            )
            embed.add_field(name="Usuario", value=despues.mention, inline=True)

            if roles_agregados:
                embed.add_field(
                    name=" Roles agregados",
                    value=", ".join(r.mention for r in roles_agregados),
                    inline=False
                )
            if roles_removidos:
                embed.add_field(
                    name=" Roles removidos",
                    value=", ".join(r.mention for r in roles_removidos),
                    inline=False
                )

            embed.set_thumbnail(url=despues.display_avatar.url)
            embed.timestamp = discord.utils.utcnow()
            try:
                await canal_log.send(embed=embed)
            except Exception:
                pass

    # ─── Eventos de canales de voz ────────────────────────────────────

    @commands.Cog.listener()
    async def on_voice_state_update(self, miembro: discord.Member,
                                     antes: discord.VoiceState,
                                     despues: discord.VoiceState):
        if miembro.bot:
            return

        canal_log = await self._obtener_canal_logs(miembro.guild)
        if not canal_log:
            return

        embed = None

        if antes.channel is None and despues.channel is not None:
            # Entró a un canal de voz
            embed = discord.Embed(
                title="  Entró a canal de voz",
                description=f"{miembro.mention} se unió a **{despues.channel.name}**",
                color=COLORES_LOG["voz"]
            )
        elif antes.channel is not None and despues.channel is None:
            # Salió de un canal de voz
            embed = discord.Embed(
                title="  Salió de canal de voz",
                description=f"{miembro.mention} dejó **{antes.channel.name}**",
                color=0x95A5A6
            )
        elif antes.channel != despues.channel:
            # Cambió de canal
            embed = discord.Embed(
                title="  Cambió de canal de voz",
                description=(
                    f"{miembro.mention} se movió de **{antes.channel.name}** "
                    f"a **{despues.channel.name}**"
                ),
                color=COLORES_LOG["voz"]
            )

        if embed:
            embed.set_thumbnail(url=miembro.display_avatar.url)
            embed.timestamp = discord.utils.utcnow()
            try:
                await canal_log.send(embed=embed)
            except Exception:
                pass

    # ─── Baneos y desbaneos ───────────────────────────────────────────

    @commands.Cog.listener()
    async def on_member_ban(self, guild: discord.Guild, usuario: discord.User):
        canal_log = await self._obtener_canal_logs(guild)
        if not canal_log:
            return

        embed = discord.Embed(
            title="  Usuario baneado",
            description=f"**{usuario}** ({usuario.mention}) fue baneado del servidor.",
            color=COLORES_LOG["ban"]
        )
        embed.set_thumbnail(url=usuario.display_avatar.url)
        embed.set_footer(text=f"ID: {usuario.id}")
        embed.timestamp = discord.utils.utcnow()

        try:
            await canal_log.send(embed=embed)
        except Exception:
            pass

    @commands.Cog.listener()
    async def on_member_unban(self, guild: discord.Guild, usuario: discord.User):
        canal_log = await self._obtener_canal_logs(guild)
        if not canal_log:
            return

        embed = discord.Embed(
            title="  Usuario desbaneado",
            description=f"**{usuario}** ({usuario.id}) fue desbaneado del servidor.",
            color=COLORES_LOG["unban"]
        )
        embed.set_thumbnail(url=usuario.display_avatar.url)
        embed.set_footer(text=f"ID: {usuario.id}")
        embed.timestamp = discord.utils.utcnow()

        try:
            await canal_log.send(embed=embed)
        except Exception:
            pass

    # ─── Comando de configuración ─────────────────────────────────────

    @commands.hybrid_command(
        name="configurar_logs",
        description="Establece el canal donde se enviarán los logs avanzados del servidor."
    )
    @commands.has_permissions(administrator=True)
    @app_commands.default_permissions(administrator=True)
    @app_commands.describe(canal="El canal de texto para los logs avanzados")
    async def configurar_logs(self, ctx: commands.Context, canal: discord.TextChannel):
        await db.guardar_canal_logs(str(ctx.guild.id), str(canal.id))

        embed = discord.Embed(
            title="  Canal de logs configurado",
            description=(
                f"Los logs avanzados se enviarán a {canal.mention}.\n\n"
                "**Eventos registrados:**\n"
                "•  Ediciones de mensajes\n"
                "•  Eliminaciones de mensajes\n"
                "•  Cambios de apodo\n"
                "•  Cambios de roles\n"
                "•  Entrada/salida de canales de voz\n"
                "•  Baneos y desbaneos"
            ),
            color=config.COLOR_EXITO
        )
        await ctx.send(embed=embed, ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(LogsAvanzados(bot))
