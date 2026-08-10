import discord
from discord.ext import commands
import config

class MenuAyuda(discord.ui.Select):
    def __init__(self, bot):
        self.bot = bot
        opciones = [
            discord.SelectOption(label="Configuración", description="Comandos para configurar canales y roles.", value="configuracion"),
            discord.SelectOption(label="Moderación", description="Comandos para administrar el servidor.", value="moderacion"),
            discord.SelectOption(label="Niveles", description="Sistema de experiencia y economía.", value="niveles"),
            discord.SelectOption(label="Básico", description="Comandos de información y utilidad.", value="basico"),
            discord.SelectOption(label="Diversión", description="Minijuegos y comandos de azar.", value="diversion"),
            discord.SelectOption(label="Anuncios", description="Publica anuncios con embeds.", value="anuncios"),
            discord.SelectOption(label="Sorteos", description="Crea sorteos con reacciones.", value="sorteos"),
            discord.SelectOption(label="Recordatorios", description="Programa recordatorios por DM.", value="recordatorios"),
            discord.SelectOption(label="Estadísticas", description="Información del servidor.", value="estadisticas"),
            discord.SelectOption(label="Encuestas", description="Crea encuestas con reacciones.", value="encuestas"),
            discord.SelectOption(label="Social", description="Confesiones, cumpleaños y logros.", value="social"),
            discord.SelectOption(label="Protección", description="Anti-spam y logs avanzados.", value="proteccion"),
        ]
        super().__init__(placeholder="Selecciona una categoría de comandos...", min_values=1, max_values=1, options=opciones)

    async def callback(self, interaction: discord.Interaction):
        # Mapeo de categorías con sus descripciones
        categorias = {
            "configuracion": (
                " Comandos de Configuración",
                "`.configurar_bienvenida`, `.configurar_modlog`, `.configurar_reglas`, `.configurar_verificacion`, `.configurar_rol_miembro`, `.configurar_recompensa`, `.configurar_logs`, `.configurar_confesiones`, `.configurar_cumpleaños`, `.ver_configuracion`"
            ),
            "moderacion": (
                " Comandos de Moderación",
                "`.kick`, `.ban`, `.unban`, `.mute`, `.unmute`, `.clear`, `.warn`, `.historial`"
            ),
            "niveles": (" Sistema de Niveles", "`.perfil`"),
            "basico": (" Comandos Básicos", "`.ping`, `.info`, `.avatar`"),
            "diversion": (" Comandos de Diversión", "`.moneda`, `.dado`, `.8ball`"),
            "anuncios": (
                " Sistema de Anuncios",
                "`.anuncio #canal título mensaje` — Publica un anuncio con embed profesional. Opcionalmente menciona un rol."
            ),
            "sorteos": (
                " Sorteos (Giveaways)",
                "`.sorteo duración premio` — Crea un sorteo con .\n`.re_sorteo mensaje_id` — Repite un sorteo con nuevos ganadores."
            ),
            "recordatorios": (
                " Recordatorios",
                "`.recordar tiempo mensaje` — El bot te envía un DM cuando pase el tiempo.\nFormatos: `30m`, `2h`, `1d`, `1h30m`"
            ),
            "estadisticas": (
                " Estadísticas del Servidor",
                "`.stats` — Miembros, canales, roles, boosts, fecha de creación y más."
            ),
            "encuestas": (
                " Encuestas",
                "`.encuesta pregunta opción1 opción2 ...` — Encuesta con hasta 10 opciones.\n`.encuesta_si_no pregunta` — Encuesta rápida de Sí/No."
            ),
            "social": (
                " Social",
                "**Confesiones:**\n`.confesar mensaje` — Envía una confesión anónima.\n`.configurar_confesiones #canal` — Configura el canal.\n\n"
                "**Logros:**\n`.logros [usuario]` — Ve los logros desbloqueados."
            ),
            "proteccion": (
                " Protección del Servidor",
                "**Anti-Spam:**\n`.antispam activar/desactivar` — Toggle del sistema.\nDetecta: flood, links, texto repetido, menciones masivas.\n\n"
                "**Logs Avanzados:**\n`.configurar_logs #canal` — Registra ediciones, eliminaciones, cambios de nick/roles, voz, baneos."
            ),
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
