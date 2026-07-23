import discord
from discord.ext import commands
import config

class MenuAyuda(discord.ui.Select):
    def __init__(self, bot):
        self.bot = bot
        opciones = [
            discord.SelectOption(label="Básico", description="Comandos de información y utilidad.", emoji="ℹ️", value="basico"),
            discord.SelectOption(label="Diversión", description="Minijuegos y comandos de azar.", emoji="🎲", value="diversion"),
            discord.SelectOption(label="Moderación", description="Comandos para administrar el servidor.", emoji="🛡️", value="moderacion"),
            discord.SelectOption(label="Música", description="Controles de reproducción y música.", emoji="🎵", value="musica"),
            discord.SelectOption(label="Niveles", description="Sistema de experiencia y economía.", emoji="⭐", value="niveles")
        ]
        super().__init__(placeholder="Selecciona una categoría de comandos...", min_values=1, max_values=1, options=opciones)

    async def callback(self, interaction: discord.Interaction):
        # Mapeo de categorías con sus descripciones
        categorias = {
            "basico": ("ℹ️ Comandos Básicos", "`.ping`, `.info`, `.avatar`"),
            "diversion": ("🎲 Comandos de Diversión", "`.moneda`, `.dado`, `.8ball`"),
            "moderacion": ("🛡️ Comandos de Moderación", "`.kick`, `.ban`, `.unban`, `.mute`, `.unmute`, `.clear`, `.warn`, `.historial`"),
            "musica": ("🎵 Comandos de Música", "`.play`, `.skip`, `.pause`, `.resume`, `.stop`, `.queue`"),
            "niveles": ("⭐ Sistema de Niveles", "`.perfil`")
        }

        seleccion = self.values[0]
        titulo, lista_comandos = categorias[seleccion]

        embed = discord.Embed(title=titulo, description=lista_comandos, color=config.COLOR_INFO)
        embed.set_footer(text="Soporta Slash Commands (/) y prefijo (.)")
        
        await interaction.response.edit_message(embed=embed)

class VistaAyuda(discord.ui.View):
    def __init__(self, bot):
        super().__init__()
        self.add_item(MenuAyuda(bot))

class Ayuda(commands.Cog):
    """Comando de ayuda interactivo."""
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="help", help="Muestra el menú interactivo de ayuda.")
    async def help_command(self, ctx):
        embed = discord.Embed(
            title="Panel de Ayuda de Norah",
            description="¡Hola! Soy Norah. Por favor, selecciona una categoría en el menú desplegable de abajo para ver mis comandos.",
            color=config.COLOR_PRINCIPAL
        )
        embed.set_thumbnail(url=self.bot.user.display_avatar.url)
        
        vista = VistaAyuda(self.bot)
        await ctx.send(embed=embed, view=vista)

async def setup(bot):
    await bot.add_cog(Ayuda(bot))