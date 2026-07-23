import random
import discord
from discord.ext import commands

import config

class Diversion(commands.Cog):
    """Comandos de entretenimiento y juegos de azar con prefijos."""

    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="moneda", help="Lanza una moneda al aire para decidir entre Cara o Cruz.")
    async def moneda(self, ctx):
        resultado = random.choice(["Cara", "Cruz"])
        await ctx.send(f"🪙 La moneda ha caído en: **{resultado}**")

    @commands.hybrid_command(name="dado", help="Lanza un dado virtual.")
    async def dado(self, ctx, caras: int = 6):
        if caras < 2:
            return await ctx.send("El dado debe tener al menos 2 caras.")
        resultado = random.randint(1, caras)
        await ctx.send(f"🎲 Has lanzado un dado de {caras} caras y salió: **{resultado}**")

    @commands.hybrid_command(name="8ball", help="Responde aleatoriamente a tus dudas.")
    async def ocho_ball(self, ctx, *, pregunta: str):
        respuestas = [
            "Sí, definitivamente.", "Es cierto.", "Sin duda.", 
            "Sí.", "Tal vez.", "Pregunta de nuevo más tarde.", 
            "No puedo predecirlo ahora.", "No cuentes con ello.", 
            "Mis fuentes dicen que no.", "Muy dudoso."
        ]
        respuesta = random.choice(respuestas)
        
        embed = discord.Embed(title="🎱 Bola 8", color=config.COLOR_PRINCIPAL)
        embed.add_field(name="Pregunta", value=pregunta, inline=False)
        embed.add_field(name="Respuesta", value=respuesta, inline=False)
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Diversion(bot))