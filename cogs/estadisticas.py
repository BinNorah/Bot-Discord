import discord
from discord.ext import commands

import config


class Estadisticas(commands.Cog):
    """Muestra estadísticas completas del servidor."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.hybrid_command(
        name="stats",
        description="Muestra estadísticas completas del servidor."
    )
    async def stats(self, ctx: commands.Context):
        guild = ctx.guild

        # Conteos de miembros
        total_miembros = guild.member_count
        bots = sum(1 for m in guild.members if m.bot)
        humanos = total_miembros - bots
        online = sum(1 for m in guild.members if m.status != discord.Status.offline)

        # Conteos de canales
        canales_texto = len(guild.text_channels)
        canales_voz = len(guild.voice_channels)
        categorias = len(guild.categories)
        canales_foro = len([c for c in guild.channels if isinstance(c, discord.ForumChannel)])

        # Información del servidor
        roles = len(guild.roles) - 1  # Excluir @everyone
        emojis = len(guild.emojis)
        stickers = len(guild.stickers)
        fecha_creacion = int(guild.created_at.timestamp())

        # Boosts
        nivel_boost = guild.premium_tier
        boosts = guild.premium_subscription_count or 0
        boosters = len(guild.premium_subscribers)

        # Nivel de verificación
        niveles_verificacion = {
            discord.VerificationLevel.none: "Ninguno",
            discord.VerificationLevel.low: "Bajo",
            discord.VerificationLevel.medium: "Medio",
            discord.VerificationLevel.high: "Alto",
            discord.VerificationLevel.highest: "Máximo",
        }
        verificacion = niveles_verificacion.get(guild.verification_level, "Desconocido")

        # Construir embed
        embed = discord.Embed(
            title=f"  Estadísticas de {guild.name}",
            color=config.COLOR_INFO
        )

        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)

        if guild.banner:
            embed.set_image(url=guild.banner.url)

        # Miembros
        embed.add_field(
            name="  Miembros",
            value=(
                f"**Total:** {total_miembros}\n"
                f"**Humanos:** {humanos}\n"
                f"**Bots:** {bots}\n"
                f"**En línea:** {online}"
            ),
            inline=True
        )

        # Canales
        valor_canales = (
            f"**Texto:** {canales_texto}\n"
            f"**Voz:** {canales_voz}\n"
            f"**Categorías:** {categorias}"
        )
        if canales_foro > 0:
            valor_canales += f"\n**Foros:** {canales_foro}"
        embed.add_field(
            name="  Canales",
            value=valor_canales,
            inline=True
        )

        # Servidor
        embed.add_field(
            name="  Servidor",
            value=(
                f"**Roles:** {roles}\n"
                f"**Emojis:** {emojis}\n"
                f"**Stickers:** {stickers}\n"
                f"**Verificación:** {verificacion}"
            ),
            inline=True
        )

        # Boosts
        barra_boost = "▰" * min(nivel_boost, 3) + "▱" * (3 - min(nivel_boost, 3))
        embed.add_field(
            name="  Boosts",
            value=(
                f"**Nivel:** {nivel_boost} [{barra_boost}]\n"
                f"**Boosts:** {boosts}\n"
                f"**Boosters:** {boosters}"
            ),
            inline=True
        )

        # Dueño y Fecha
        embed.add_field(
            name="  Información",
            value=(
                f"**Dueño:** {guild.owner.mention if guild.owner else 'Desconocido'}\n"
                f"**Creado:** <t:{fecha_creacion}:D>\n"
                f"**Antigüedad:** <t:{fecha_creacion}:R>"
            ),
            inline=True
        )

        # ID
        embed.add_field(
            name="  ID del Servidor",
            value=f"`{guild.id}`",
            inline=True
        )

        embed.set_footer(
            text=f"Norah | Solicitado por {ctx.author.display_name}",
            icon_url=ctx.author.display_avatar.url
        )
        embed.timestamp = discord.utils.utcnow()

        await ctx.send(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(Estadisticas(bot))
