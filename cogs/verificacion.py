import discord
from discord.ext import commands

import config
from base_datos import db


class BotonVerificacion(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)  # timeout=None = el botón no expira

    @discord.ui.button(label="Verificarme", style=discord.ButtonStyle.green, emoji="✅", custom_id="verificacion_boton_persistente")
    async def verificar(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Leer el rol de verificación desde la base de datos
        conf = await db.obtener_configuracion(str(interaction.guild.id))
        if not conf or not conf[2]:
            return await interaction.response.send_message(
                "⚠️ Este servidor aún no ha configurado el rol de verificación. Avisa a un administrador para que use `/configurar_rol_miembro`.",
                ephemeral=True
            )

        rol = interaction.guild.get_role(int(conf[2]))
        if rol is None:
            return await interaction.response.send_message(
                "⚠️ No encontré el rol de miembro. Avisa a un administrador.", ephemeral=True
            )

        if rol in interaction.user.roles:
            return await interaction.response.send_message("Ya estás verificado.", ephemeral=True)

        try:
            await interaction.user.add_roles(rol, reason="Verificación por botón")
        except discord.Forbidden:
            return await interaction.response.send_message(
                "⚠️ No tengo permisos para darte el rol. Avisa a un administrador.", ephemeral=True
            )

        await interaction.response.send_message("🎉 ¡Verificación completada! Ya tienes acceso al servidor.", ephemeral=True)


class Verificacion(commands.Cog):
    """Sistema de verificación por botón para desbloquear el acceso al servidor."""

    def __init__(self, bot):
        self.bot = bot
        bot.add_view(BotonVerificacion())  # registra el botón como persistente al reiniciar el bot

    @commands.hybrid_command(name="enviarverificacion", help="Publica el panel de verificación en el canal configurado o el actual.")
    @commands.has_permissions(administrator=True)
    async def enviarverificacion(self, ctx):
        # Determinar el canal destino
        conf = await db.obtener_configuracion(str(ctx.guild.id))
        canal_destino = ctx.channel  # Por defecto, el canal actual

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

        # Confirmar al admin
        if canal_destino != ctx.channel:
            await ctx.send(
                f"✅ Panel de verificación publicado en {canal_destino.mention}.",
                ephemeral=True
            )
        else:
            await ctx.send("✅ Panel de verificación publicado.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Verificacion(bot))