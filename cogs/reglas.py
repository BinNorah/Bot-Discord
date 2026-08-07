import os

import discord
from discord import app_commands
from discord.ext import commands

import config
from base_datos import db

# Ruta absoluta al GIF de reglas (se mantiene como recurso visual)
DIRECTORIO_BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RUTA_GIF_REGLAS = os.path.join(DIRECTORIO_BASE, "gif", "reglas.gif")


class Reglas(commands.Cog):
    """Sistema de reglas por servidor almacenadas en la base de datos."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # ─── /agregar_regla ───────────────────────────────────────────────

    @commands.hybrid_command(
        name="agregar_regla",
        description="Agrega una nueva regla al servidor."
    )
    @commands.has_permissions(administrator=True)
    @app_commands.default_permissions(administrator=True)
    @app_commands.describe(
        titulo="Título corto de la regla (ej: Respeto mutuo)",
        contenido="Descripción completa de la regla"
    )
    async def agregar_regla(self, ctx: commands.Context, titulo: str, *, contenido: str):
        numero = await db.agregar_regla(str(ctx.guild.id), titulo, contenido)

        embed = discord.Embed(
            title="✅ Regla agregada",
            description=f"**Regla #{numero} — {titulo}**\n{contenido}",
            color=config.COLOR_EXITO
        )
        embed.set_footer(text="Usa /publicar_reglas para publicarlas en el canal de reglas.")
        await ctx.send(embed=embed, ephemeral=True)

    # ─── /eliminar_regla ──────────────────────────────────────────────

    @commands.hybrid_command(
        name="eliminar_regla",
        description="Elimina una regla por su número."
    )
    @commands.has_permissions(administrator=True)
    @app_commands.default_permissions(administrator=True)
    @app_commands.describe(numero="El número de la regla a eliminar")
    async def eliminar_regla(self, ctx: commands.Context, numero: int):
        eliminada = await db.eliminar_regla(str(ctx.guild.id), numero)

        if not eliminada:
            return await ctx.send(
                f"❌ No existe una regla con el número **{numero}**. Usa `/ver_reglas` para ver las reglas actuales.",
                ephemeral=True
            )

        embed = discord.Embed(
            title="🗑️ Regla eliminada",
            description=f"La regla **#{numero}** fue eliminada y las demás se renumeraron automáticamente.",
            color=config.COLOR_ADVERTENCIA
        )
        await ctx.send(embed=embed, ephemeral=True)

    # ─── /editar_regla ────────────────────────────────────────────────

    @commands.hybrid_command(
        name="editar_regla",
        description="Edita una regla existente por su número."
    )
    @commands.has_permissions(administrator=True)
    @app_commands.default_permissions(administrator=True)
    @app_commands.describe(
        numero="El número de la regla a editar",
        titulo="Nuevo título de la regla",
        contenido="Nueva descripción de la regla"
    )
    async def editar_regla(self, ctx: commands.Context, numero: int, titulo: str, *, contenido: str):
        editada = await db.editar_regla(str(ctx.guild.id), numero, titulo, contenido)

        if not editada:
            return await ctx.send(
                f"❌ No existe una regla con el número **{numero}**. Usa `/ver_reglas` para ver las reglas actuales.",
                ephemeral=True
            )

        embed = discord.Embed(
            title="✏️ Regla editada",
            description=f"**Regla #{numero} — {titulo}**\n{contenido}",
            color=config.COLOR_EXITO
        )
        await ctx.send(embed=embed, ephemeral=True)

    # ─── /ver_reglas ──────────────────────────────────────────────────

    @commands.hybrid_command(
        name="ver_reglas",
        description="Muestra las reglas del servidor (previsualización para admins)."
    )
    @commands.has_permissions(manage_messages=True)
    @app_commands.default_permissions(manage_messages=True)
    async def ver_reglas(self, ctx: commands.Context):
        reglas = await db.obtener_reglas(str(ctx.guild.id))

        if not reglas:
            embed = discord.Embed(
                title="📜 Reglas del Servidor",
                description="Este servidor aún no tiene reglas configuradas.\nUsa `/agregar_regla` para empezar.",
                color=config.COLOR_INFO
            )
            return await ctx.send(embed=embed, ephemeral=True)

        embed = discord.Embed(
            title=f"📜 Reglas de {ctx.guild.name}",
            description=f"Total: **{len(reglas)}** reglas configuradas",
            color=discord.Color.from_rgb(255, 182, 213)
        )

        for numero, titulo, contenido in reglas:
            embed.add_field(
                name=f"#{numero} — {titulo}",
                value=contenido,
                inline=False
            )

        embed.set_footer(text="Vista previa — usa /publicar_reglas para publicarlas.")
        await ctx.send(embed=embed, ephemeral=True)

    # ─── /publicar_reglas ─────────────────────────────────────────────

    @commands.hybrid_command(
        name="publicar_reglas",
        description="Publica las reglas en el canal configurado (o el actual)."
    )
    @commands.has_permissions(administrator=True)
    @app_commands.default_permissions(administrator=True)
    async def publicar_reglas(self, ctx: commands.Context):
        reglas = await db.obtener_reglas(str(ctx.guild.id))

        if not reglas:
            return await ctx.send(
                "❌ No hay reglas configuradas. Usa `/agregar_regla` para añadir reglas primero.",
                ephemeral=True
            )

        # Determinar el canal destino
        conf = await db.obtener_configuracion(str(ctx.guild.id))
        canal_destino = ctx.channel  # Por defecto, el canal actual

        if conf and conf[4]:  # canal_reglas_id está en la posición 4
            canal_configurado = ctx.guild.get_channel(int(conf[4]))
            if canal_configurado:
                canal_destino = canal_configurado

        # Construir el embed de reglas
        embed = discord.Embed(
            title=f"📜 Reglas de {ctx.guild.name}",
            description="Lee atentamente las siguientes reglas. Al permanecer en el servidor, aceptas cumplirlas.",
            color=discord.Color.from_rgb(255, 182, 213)  # rosa pastel
        )

        for numero, titulo, contenido in reglas:
            # Soporte para menciones inteligentes
            rol_mod = next((r for r in ctx.guild.roles if "Moderador" in r.name), None)
            rol_admin = next((r for r in ctx.guild.roles if "Administrador" in r.name), None)
            mention_mod = rol_mod.mention if rol_mod else "@Moderador"
            mention_admin = rol_admin.mention if rol_admin else "@Administrador"

            contenido_formateado = contenido.replace("{Moderador}", mention_mod).replace("{Administrador}", mention_admin)

            embed.add_field(
                name=f"#{numero} — {titulo}",
                value=contenido_formateado,
                inline=False
            )

        embed.set_footer(text=f"Norah | {ctx.guild.name}")

        # Enviar con GIF si existe
        if os.path.exists(RUTA_GIF_REGLAS):
            archivo = discord.File(RUTA_GIF_REGLAS, filename="reglas.gif")
            embed.set_image(url="attachment://reglas.gif")
            await canal_destino.send(embed=embed, file=archivo)
        else:
            await canal_destino.send(embed=embed)

        # Confirmar al admin si se publicó en otro canal
        if canal_destino != ctx.channel:
            await ctx.send(
                f"✅ Las reglas fueron publicadas en {canal_destino.mention}.",
                ephemeral=True
            )
        else:
            # Si se publicó en el canal actual, enviar confirmación efímera
            await ctx.send("✅ Reglas publicadas.", ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(Reglas(bot))