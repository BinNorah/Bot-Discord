import discord
from discord import app_commands
from discord.ext import commands

import config

# Emojis de números para las opciones
EMOJIS_NUMEROS = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]


class Encuestas(commands.Cog):
    """Sistema de encuestas con reacciones automáticas."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.hybrid_command(
        name="encuesta",
        description="Crea una encuesta con opciones y reacciones automáticas."
    )
    @app_commands.describe(
        pregunta="La pregunta de la encuesta",
        opcion1="Primera opción",
        opcion2="Segunda opción",
        opcion3="Tercera opción (opcional)",
        opcion4="Cuarta opción (opcional)",
        opcion5="Quinta opción (opcional)",
        opcion6="Sexta opción (opcional)",
        opcion7="Séptima opción (opcional)",
        opcion8="Octava opción (opcional)",
        opcion9="Novena opción (opcional)",
        opcion10="Décima opción (opcional)",
    )
    async def encuesta(self, ctx: commands.Context, pregunta: str,
                       opcion1: str, opcion2: str,
                       opcion3: str = None, opcion4: str = None,
                       opcion5: str = None, opcion6: str = None,
                       opcion7: str = None, opcion8: str = None,
                       opcion9: str = None, opcion10: str = None):
        # Recopilar opciones válidas
        todas = [opcion1, opcion2, opcion3, opcion4, opcion5,
                 opcion6, opcion7, opcion8, opcion9, opcion10]
        opciones = [op for op in todas if op is not None]

        # Construir la descripción con los emojis
        lineas = []
        for i, opcion in enumerate(opciones):
            lineas.append(f"{EMOJIS_NUMEROS[i]}  {opcion}")

        descripcion = "\n\n".join(lineas)

        embed = discord.Embed(
            title=f"📊  {pregunta}",
            description=descripcion,
            color=0x9B59B6  # Morado
        )
        embed.set_footer(
            text=f"Encuesta creada por {ctx.author.display_name} • Reacciona para votar",
            icon_url=ctx.author.display_avatar.url
        )
        embed.timestamp = discord.utils.utcnow()

        msg = await ctx.send(embed=embed)

        # Agregar reacciones automáticamente
        for i in range(len(opciones)):
            await msg.add_reaction(EMOJIS_NUMEROS[i])

    @commands.hybrid_command(
        name="encuesta_si_no",
        description="Crea una encuesta rápida de Sí o No."
    )
    @app_commands.describe(pregunta="La pregunta de la encuesta")
    async def encuesta_si_no(self, ctx: commands.Context, *, pregunta: str):
        embed = discord.Embed(
            title=f"📊  {pregunta}",
            description="✅ Sí\n\n❌ No",
            color=0x3498DB
        )
        embed.set_footer(
            text=f"Encuesta de {ctx.author.display_name}",
            icon_url=ctx.author.display_avatar.url
        )
        embed.timestamp = discord.utils.utcnow()

        msg = await ctx.send(embed=embed)
        await msg.add_reaction("✅")
        await msg.add_reaction("❌")


async def setup(bot: commands.Bot):
    await bot.add_cog(Encuestas(bot))
