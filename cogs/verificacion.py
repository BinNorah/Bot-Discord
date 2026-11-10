import asyncio
import discord
from discord import app_commands
from discord.ext import commands

import config
from base_datos import db


class BotonVerificacion(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)  # timeout=None = el botón no expira

    @discord.ui.button(label="Verificarme", style=discord.ButtonStyle.green, custom_id="verificacion_boton_persistente")
    async def verificar(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Leer el rol de verificación desde la base de datos
        conf = await db.obtener_configuracion(str(interaction.guild.id))
        if not conf or not conf[2]:
            return await interaction.response.send_message(
                "❌ Este servidor aún no ha configurado el rol de verificación. Avisa a un administrador para que use `/configurar_rol_miembro`.",
                ephemeral=True
            )

        rol = interaction.guild.get_role(int(conf[2]))
        if rol is None:
            return await interaction.response.send_message(
                "❌ No encontré el rol de miembro. Avisa a un administrador.", ephemeral=True
            )

        if rol in interaction.user.roles:
            return await interaction.response.send_message("Ya estás verificado.", ephemeral=True)

        try:
            await interaction.user.add_roles(rol, reason="Verificación por botón")
        except discord.Forbidden:
            return await interaction.response.send_message(
                "❌ No tengo permisos para darte el rol. Asegúrate de que mi rol esté por encima en la jerarquía.", ephemeral=True
            )

        await interaction.response.send_message("✅ ¡Verificación completada! Ya tienes acceso al servidor.", ephemeral=True)


class Verificacion(commands.Cog):
    """Sistema de verificación por botón y gestión de miembros."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        bot.add_view(BotonVerificacion())

    @commands.hybrid_command(
        name="enviarverificacion",
        help="Publica el panel de verificación en el canal configurado o el actual."
    )
    @commands.has_permissions(administrator=True)
    @app_commands.default_permissions(administrator=True)
    async def enviarverificacion(self, ctx: commands.Context):
        # Determinar el canal destino
        conf = await db.obtener_configuracion(str(ctx.guild.id))
        canal_destino = ctx.channel

        if conf and conf[5]:  # canal_verificacion_id está en la posición 5
            canal_configurado = ctx.guild.get_channel(int(conf[5]))
            if canal_configurado:
                canal_destino = canal_configurado

        embed = discord.Embed(
            title="Verificación del servidor",
            description="Lee las reglas del servidor y presiona el botón de abajo para desbloquear todo el contenido.",
            color=config.COLOR_PRINCIPAL,
        )
        await canal_destino.send(embed=embed, view=BotonVerificacion())

        if canal_destino != ctx.channel:
            await ctx.send(f"✅ Panel de verificación publicado en {canal_destino.mention}.", ephemeral=True)
        else:
            await ctx.send("✅ Panel de verificación publicado.", ephemeral=True)

    @commands.hybrid_command(
        name="verificar_todos",
        aliases=["verificar_antiguos"],
        help="Asigna el rol de miembro a todos los usuarios actuales del servidor que no lo tengan."
    )
    @commands.has_permissions(administrator=True)
    @app_commands.default_permissions(administrator=True)
    async def verificar_todos(self, ctx: commands.Context):
        """Otorga masivamente el rol de verificación a todos los miembros que aún no lo tengan."""
        conf = await db.obtener_configuracion(str(ctx.guild.id))
        if not conf or not conf[2]:
            return await ctx.send(
                "❌ Este servidor aún no tiene configurado un rol de verificación. Usa `/configurar_rol_miembro @Rol` primero.",
                ephemeral=True
            )

        rol = ctx.guild.get_role(int(conf[2]))
        if rol is None:
            return await ctx.send("❌ No se encontró el rol configurado en el servidor.", ephemeral=True)

        # Defer para evitar que la interacción expire (3 segundos) mientras procesa miembros
        if ctx.interaction:
            await ctx.interaction.response.defer(ephemeral=True)

        msg_estado = await ctx.send("⏳ Iniciando verificación masiva de miembros antiguos...", ephemeral=True)

        asignados = 0
        fallidos = 0
        ya_tenian = 0

        # Obtener todos los miembros directamente desde Discord
        async for miembro in ctx.guild.fetch_members(limit=None):
            if miembro.bot:
                continue

            if rol in miembro.roles:
                ya_tenian += 1
                continue

            try:
                await miembro.add_roles(rol, reason=f"Verificación masiva solicitada por {ctx.author}")
                asignados += 1
                # Pausa para respetar el rate-limit de Discord
                await asyncio.sleep(0.3)
            except (discord.Forbidden, discord.HTTPException):
                fallidos += 1

        embed = discord.Embed(
            title="✅ Verificación Masiva Completada",
            description=f"Se procesaron todos los miembros del servidor con el rol {rol.mention}.",
            color=config.COLOR_EXITO
        )
        embed.add_field(name="Nuevos verificados", value=f"**{asignados}** personas", inline=True)
        embed.add_field(name="Ya lo tenían", value=f"**{ya_tenian}** personas", inline=True)
        if fallidos > 0:
            embed.add_field(name="Sin permisos", value=f"**{fallidos}** personas", inline=True)

        embed.set_footer(text=f"Ejecutado por {ctx.author.display_name}")

        if ctx.interaction:
            await ctx.interaction.followup.send(embed=embed, ephemeral=True)
        else:
            await msg_estado.edit(content=None, embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(Verificacion(bot))
