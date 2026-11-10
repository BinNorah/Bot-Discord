import discord
from discord import app_commands
from discord.ext import commands

import config
from base_datos import db


class Anuncios(commands.Cog):
    """Sistema de anuncios simplificado con embeds profesionales y mención a roles de miembros."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    def _obtener_roles_comunidad(self, guild: discord.Guild) -> list:
        """Obtiene todos los roles inferiores a Administrador y Moderador (miembros de la comunidad)."""
        roles_comunidad = []
        for rol in guild.roles:
            # 1. Ignorar @everyone
            if rol.is_default():
                continue
            # 2. Ignorar roles automáticos de bots o integraciones
            if rol.managed:
                continue
            # 3. Ignorar si tiene permisos de administración o moderación
            perms = rol.permissions
            if (perms.administrator or perms.manage_guild or perms.ban_members or
                    perms.kick_members or perms.manage_messages or perms.moderate_members):
                continue
            # 4. Ignorar por palabras clave de staff
            nombre_lower = rol.name.lower()
            if any(palabra in nombre_lower for palabra in ["admin", "mod", "staff", "owner", "soporte", "developer"]):
                continue

            roles_comunidad.append(rol)

        return roles_comunidad

    @commands.hybrid_command(
        name="anuncio",
        description="Publica un anuncio mencionando automáticamente a los roles de la comunidad."
    )
    @commands.has_permissions(administrator=True)
    @app_commands.default_permissions(administrator=True)
    @app_commands.describe(
        titulo="Título del anuncio",
        contenido="Texto y contenido del anuncio"
    )
    async def anuncio(self, ctx: commands.Context, titulo: str, *, contenido: str):
        # Determinar el canal de destino (canal oficial configurado con /configurar_anuncios o el canal actual)
        conf = await db.obtener_configuracion(str(ctx.guild.id))
        canal_destino = ctx.channel

        if conf and conf[4]:  # canal_anuncios_id
            canal_configurado = ctx.guild.get_channel(int(conf[4]))
            if canal_configurado:
                canal_destino = canal_configurado

        # Obtener los roles de la comunidad (inferiores a Admin y Mod)
        roles_comunidad = self._obtener_roles_comunidad(ctx.guild)
        if roles_comunidad:
            menciones = " ".join(r.mention for r in roles_comunidad)
        else:
            menciones = "@everyone"

        embed = discord.Embed(
            title=f"📢  {titulo}",
            description=contenido,
            color=0xFFD700  # Dorado elegante
        )

        if ctx.guild.icon:
            embed.set_thumbnail(url=ctx.guild.icon.url)

        embed.set_footer(
            text=f"Anuncio por {ctx.author.display_name} • {ctx.guild.name}",
            icon_url=ctx.author.display_avatar.url
        )
        embed.timestamp = discord.utils.utcnow()

        # Enviar el anuncio
        await canal_destino.send(
            content=menciones,
            embed=embed,
            allowed_mentions=discord.AllowedMentions(roles=True, everyone=True)
        )

        # Confirmación para el administrador
        if canal_destino != ctx.channel:
            await ctx.send(f"✅ Anuncio publicado exitosamente en {canal_destino.mention}.", ephemeral=True)
        else:
            await ctx.send("✅ Anuncio publicado exitosamente.", ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(Anuncios(bot))
