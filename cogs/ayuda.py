import discord
from discord.ext import commands
import config

class MenuAyuda(discord.ui.Select):
    def __init__(self, bot):
        self.bot = bot
        opciones = [
            discord.SelectOption(label="Configuración", description="Comandos para configurar canales y roles.", emoji="⚙️", value="configuracion"),
            discord.SelectOption(label="Moderación", description="Comandos para administrar el servidor.", emoji="🛡️", value="moderacion"),
            discord.SelectOption(label="Reglas", description="Gestión de reglas del servidor.", emoji="📜", value="reglas"),
            discord.SelectOption(label="Niveles", description="Sistema de experiencia y economía.", emoji="⭐", value="niveles"),
            discord.SelectOption(label="Básico", description="Comandos de información y utilidad.", emoji="ℹ️", value="basico"),
            discord.SelectOption(label="Diversión", description="Minijuegos y comandos de azar.", emoji="🎲", value="diversion"),
        ]
        super().__init__(placeholder="Selecciona una categoría de comandos...", min_values=1, max_values=1, options=opciones)

    async def callback(self, interaction: discord.Interaction):
        # Mapeo de categorías con sus descripciones
        categorias = {
            "configuracion": (
                "⚙️ Comandos de Configuración",
                "`.configurar_bienvenida`, `.configurar_modlog`, `.configurar_reglas`, `.configurar_verificacion`, `.configurar_rol_miembro`, `.configurar_recompensa`, `.ver_configuracion`"
            ),
            "moderacion": (
                "🛡️ Comandos de Moderación",
                "`.kick`, `.ban`, `.unban`, `.mute`, `.unmute`, `.clear`, `.warn`, `.historial`"
            ),
            "reglas": (
                "📜 Gestión de Reglas",
                "`.agregar_regla`, `.eliminar_regla`, `.editar_regla`, `.ver_reglas`, `.publicar_reglas`"
            ),
            "niveles": ("⭐ Sistema de Niveles", "`.perfil`"),
            "basico": ("ℹ️ Comandos Básicos", "`.ping`, `.info`, `.avatar`"),
            "diversion": ("🎲 Comandos de Diversión", "`.moneda`, `.dado`, `.8ball`"),
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
            description="¡Hola! Soy asistente de Norah. Por favor, selecciona una categoría en el menú desplegable de abajo para ver mis comandos.",
            color=config.COLOR_PRINCIPAL
        )
        embed.set_thumbnail(url=self.bot.user.display_avatar.url)
        
        vista = VistaAyuda(self.bot)
        await ctx.send(embed=embed, view=vista)

async def setup(bot):
    await bot.add_cog(Ayuda(bot))

