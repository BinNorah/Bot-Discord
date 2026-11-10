import discord
from discord import app_commands
from discord.ext import commands

import config


class Perfil(commands.Cog):
    """Muestra información completa y tarjeta de perfil de los miembros."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.hybrid_command(
        name="perfil",
        description="Muestra la tarjeta de perfil e información de un miembro."
    )
    @app_commands.describe(miembro="El usuario del que deseas ver el perfil (opcional)")
    async def perfil(self, ctx: commands.Context, miembro: discord.Member = None):
        usuario = miembro or ctx.author

        # Color: usar el color del rol más alto si tiene color propio, si no el principal
        color = usuario.color if usuario.color.value != 0 else config.COLOR_PRINCIPAL

        embed = discord.Embed(
            title=f"Perfil de {usuario.display_name}",
            color=color
        )
        embed.set_thumbnail(url=usuario.display_avatar.url)

        # Información general
        embed.add_field(name="Usuario", value=f"{usuario.name}", inline=True)
        embed.add_field(name="ID", value=f"`{usuario.id}`", inline=True)
        embed.add_field(name="Apodo en servidor", value=usuario.nick or "Ninguno", inline=True)

        # Fechas importantes en formato legible de Discord
        creado_ts = int(usuario.created_at.timestamp())
        embed.add_field(
            name="Cuenta creada",
            value=f"<t:{creado_ts}:D> (<t:{creado_ts}:R>)",
            inline=False
        )

        if usuario.joined_at:
            unido_ts = int(usuario.joined_at.timestamp())
            embed.add_field(
                name="Se unió al servidor",
                value=f"<t:{unido_ts}:D> (<t:{unido_ts}:R>)",
                inline=False
            )

        # Roles (excluyendo @everyone y ordenados de mayor a menor)
        roles = [r.mention for r in reversed(usuario.roles) if r.name != "@everyone"]
        if roles:
            if len(roles) <= 15:
                roles_texto = ", ".join(roles)
            else:
                roles_texto = ", ".join(roles[:15]) + f" *y {len(roles) - 15} más...*"
        else:
            roles_texto = "*Sin roles asignados*"

        embed.add_field(
            name=f"Roles ({len(roles)})",
            value=roles_texto,
            inline=False
        )

        # Rol más alto
        if usuario.top_role and usuario.top_role.name != "@everyone":
            embed.add_field(name="Rol más alto", value=usuario.top_role.mention, inline=True)

        # Insignia especial si es admin o bot
        insignias = []
        if usuario.bot:
            insignias.append("Bot")
        if usuario.guild_permissions.administrator:
            insignias.append("Administrador")
        elif usuario.guild_permissions.manage_messages:
            insignias.append("Moderador")
        if usuario.id == ctx.guild.owner_id:
            insignias.append("Dueño del Servidor")

        if insignias:
            embed.add_field(name="Distintivos", value=", ".join(insignias), inline=True)

        embed.set_footer(
            text=f"Solicitado por {ctx.author.display_name}",
            icon_url=ctx.author.display_avatar.url
        )
        embed.timestamp = discord.utils.utcnow()

        await ctx.send(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(Perfil(bot))

