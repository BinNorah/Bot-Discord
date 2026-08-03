import json
import os

import discord
from discord import app_commands
from discord.ext import commands

# Ruta absoluta al archivo reglas.json
DIRECTORIO_BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RUTA_REGLAS_JSON = os.path.join(DIRECTORIO_BASE, "reglas.json")
RUTA_GIF_REGLAS = os.path.join(DIRECTORIO_BASE, "gif", "reglas.gif")


class Reglas(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.hybrid_command(name="reglas", description="Muestra las reglas del servidor")
    @commands.has_permissions(manage_messages=True)
    @app_commands.default_permissions(manage_messages=True)
    async def reglas(self, ctx: commands.Context):
        # Cargar el contenido de las reglas desde el JSON externo
        with open(RUTA_REGLAS_JSON, "r", encoding="utf-8") as f:
            datos = json.load(f)

        embed = discord.Embed(
            title=datos["titulo"],
            description=datos["descripcion"],
            color=discord.Color.from_rgb(255, 182, 213)  # rosa pastel
        )

        # Buscar roles por coincidencia parcial (funciona aunque tengan caracteres especiales)
        rol_mod = next((r for r in ctx.guild.roles if "Moderador" in r.name), None)
        rol_admin = next((r for r in ctx.guild.roles if "Administrador" in r.name), None)
        mention_mod = rol_mod.mention if rol_mod else "@Moderador"
        mention_admin = rol_admin.mention if rol_admin else "@Administrador"

        # Iterar sobre las reglas del JSON y construir los fields dinámicamente
        for regla in datos["reglas"]:
            valor = regla["valor"]
            # Menciones inteligentes: reemplazar placeholders por menciones reales
            valor = valor.replace("{Moderador}", mention_mod).replace("{Administrador}", mention_admin)

            embed.add_field(
                name=regla["nombre"],
                value=valor,
                inline=False
            )

        # GIF adjunto al embed
        gif_file = discord.File(RUTA_GIF_REGLAS, filename="reglas.gif")
        embed.set_image(url="attachment://reglas.gif")

        # Footer
        embed.set_footer(text=datos["footer"])

        await ctx.send(embed=embed, file=gif_file)


async def setup(bot: commands.Bot):
    await bot.add_cog(Reglas(bot))