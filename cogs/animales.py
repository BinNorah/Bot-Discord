import logging

import aiohttp
import discord
from discord.ext import commands

import config

logger = logging.getLogger("bot")


class Animales(commands.Cog):
    """Imágenes aleatorias de animales usando APIs gratuitas."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.hybrid_command(
        name="gato",
        description="Envía una imagen aleatoria de un gato. 🐱"
    )
    async def gato(self, ctx: commands.Context):
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(
                    "https://api.thecatapi.com/v1/images/search",
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        url_imagen = data[0]["url"]

                        embed = discord.Embed(
                            title="🐱  ¡Miau!",
                            color=0xFFB347
                        )
                        embed.set_image(url=url_imagen)
                        embed.set_footer(text="Powered by TheCatAPI")
                        await ctx.send(embed=embed)
                    else:
                        await ctx.send("😿 No pude encontrar un gato ahora. Intenta de nuevo.", ephemeral=True)
            except (aiohttp.ClientError, TimeoutError):
                await ctx.send("😿 Hubo un error al buscar un gato. Intenta de nuevo.", ephemeral=True)

    @commands.hybrid_command(
        name="perro",
        description="Envía una imagen aleatoria de un perro. 🐶"
    )
    async def perro(self, ctx: commands.Context):
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(
                    "https://dog.ceo/api/breeds/image/random",
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        url_imagen = data["message"]

                        embed = discord.Embed(
                            title="🐶  ¡Guau!",
                            color=0x8B4513
                        )
                        embed.set_image(url=url_imagen)
                        embed.set_footer(text="Powered by Dog CEO API")
                        await ctx.send(embed=embed)
                    else:
                        await ctx.send("🐕 No pude encontrar un perro ahora. Intenta de nuevo.", ephemeral=True)
            except (aiohttp.ClientError, TimeoutError):
                await ctx.send("🐕 Hubo un error al buscar un perro. Intenta de nuevo.", ephemeral=True)

    @commands.hybrid_command(
        name="zorro",
        description="Envía una imagen aleatoria de un zorro. 🦊"
    )
    async def zorro(self, ctx: commands.Context):
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(
                    "https://randomfox.ca/floof/",
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        url_imagen = data["image"]

                        embed = discord.Embed(
                            title="🦊  ¡Ring-ding-ding!",
                            color=0xFF6600
                        )
                        embed.set_image(url=url_imagen)
                        embed.set_footer(text="Powered by RandomFox")
                        await ctx.send(embed=embed)
                    else:
                        await ctx.send("🦊 No pude encontrar un zorro ahora. Intenta de nuevo.", ephemeral=True)
            except (aiohttp.ClientError, TimeoutError):
                await ctx.send("🦊 Hubo un error al buscar un zorro. Intenta de nuevo.", ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(Animales(bot))
