import time
import discord
from discord.ext import commands

import config

class VistaEnlaces(discord.ui.View):
    """Componente interactivo para añadir botones personalizados."""
    def __init__(self):
        super().__init__()
       
        self.add_item(
            discord.ui.Button(
                label="Perfil de BinNorah", 
                url="https://discord.com/users/1174495346265706537",  
                style=discord.ButtonStyle.link
            )
        )

class Basico(commands.Cog):
    """Comandos generales de información y estado del bot."""

    def __init__(self, bot):
        self.bot = bot
        self.inicio = time.time()

    @commands.hybrid_command(name="ping", help="Muestra la latencia actual del bot.")
    async def ping(self, ctx):
        latencia = round(self.bot.latency * 1000)
        embed = discord.Embed(
            title="Latencia",
            description=f"`{latencia} ms`",
            color=config.COLOR_INFO,
        )
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="info", help="Muestra información general sobre el bot.")
    async def info(self, ctx):
        embed = discord.Embed(
            title=f"Acerca de {self.bot.user.name}",
            description="Bot Personal Desarrollado Por BinNorah",
            color=config.COLOR_PRINCIPAL,
        )
        embed.add_field(name="Servidores", value=str(len(self.bot.guilds)), inline=True)
        embed.add_field(name="Usuarios", value=str(len(self.bot.users)), inline=True)
        embed.set_thumbnail(url=self.bot.user.display_avatar.url)
        
        vista_interactiva = VistaEnlaces()
        await ctx.send(embed=embed, view=vista_interactiva)

    @commands.hybrid_command(name="avatar", help="Muestra el avatar de un usuario.")
    async def avatar(self, ctx, usuario: discord.Member = None):
        usuario_objetivo = usuario or ctx.author
        embed = discord.Embed(
            title=f"Avatar de {usuario_objetivo.display_name}",
            color=config.COLOR_PRINCIPAL,
        )
        embed.set_image(url=usuario_objetivo.display_avatar.url)
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Basico(bot))