import discord
from discord import app_commands
from discord.ext import commands


class Reglas(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.hybrid_command(name="reglas", description="Muestra las reglas del servidor")
    @commands.has_permissions(manage_messages=True)
    @app_commands.default_permissions(manage_messages=True)
    async def reglas(self, ctx: commands.Context):
        embed = discord.Embed(
            title="°·˚⋆ Leyes Sagradas del Servidor ⋆˚·°",
            description=(
                "¡Hola miembro nuevo! ✨ Bienvenido/a a nuestra comunidad. "
                "Para mantener una convivencia hermosa, pacífica y llena de buena "
                "energía, te pedimos que sigas detalladamente nuestro reglamento "
                "oficial:"
            ),
            color=discord.Color.from_rgb(255, 182, 213)  # rosa pastel, cambia si quieres
        )

        embed.add_field(
            name="╰┈➤ 1️⃣ Respeto Mutuo",
            value="Trata a todos los miembros con amabilidad. No se tolera el acoso, los insultos ni las actitudes tóxicas.",
            inline=False
        )
        embed.add_field(
            name="╰┈➤ 2️⃣ Contenido Apropiado",
            value="Prohibido el material NSFW, gore o links sospechosos en canales generales. Mantengamos la comunidad limpia.",
            inline=False
        )
        embed.add_field(
            name="╰┈➤ 3️⃣ Temas Sensibles",
            value="Evita hablar de suicidio, autolesiones o asesinatos. Cuidemos la salud mental y la tranquilidad de todos.",
            inline=False
        )
        embed.add_field(
            name="╰┈➤ 4️⃣ No Spam ni Self-Promo",
            value="No satures los chats con flood (mensajes repetitivos), mayúsculas excesivas ni invites a otros servidores sin permiso.",
            inline=False
        )
        embed.add_field(
            name="╰┈➤ 5️⃣ Canales Temáticos",
            value="Utiliza cada canal para el fin con el que fue creado (música, juegos, multimedia, etc.). ¡Mantengamos el orden!",
            inline=False
        )
        embed.add_field(
            name="╰┈➤ 6️⃣ Uso de Comandos",
            value="No abuses de los comandos de los bots ni de los sistemas de interacción para no generar lag o molestar a los demás.",
            inline=False
        )
        embed.add_field(
            name="╰┈➤ 7️⃣ El Staff También Cumple",
            value="Ningún administrador o moderador está por encima de estas leyes. La justicia es igual para todos.",
            inline=False
        )
        # Buscar roles por coincidencia parcial (funciona aunque tengan caracteres especiales)
        rol_mod = next((r for r in ctx.guild.roles if "Moderador" in r.name), None)
        rol_admin = next((r for r in ctx.guild.roles if "Administrador" in r.name), None)
        mention_mod = rol_mod.mention if rol_mod else "@MOD"
        mention_admin = rol_admin.mention if rol_admin else "@Administrador"

        embed.add_field(
            name="╰┈➤ 8️⃣ Dudas y Reportes",
            value=f"Si necesitas apoyo o presencias una injusticia, acude con confianza a {mention_mod} o {mention_admin}.",
            inline=False
        )
        embed.add_field(
            name="╰┈➤ 9️⃣ Configuración de Perfil",
            value="Evita llevar nicks, estados o avatares ofensivos, explícitos o que busquen generar polémica en el servidor.",
            inline=False
        )
        embed.add_field(
            name="╰┈➤ 🔟 Convivencia Sana",
            value=(
                "Al final del día, estamos aquí para pasarla lindo, hacer amigos "
                "y crecer juntos en esta bonita comunidad. ✨"
            ),
            inline=False
        )

        # GIF cerca del final del embed.
        # Coloca el archivo "reglas.gif" en la carpeta "gif"
        # (o ajusta la ruta de abajo). Se sube como adjunto y se referencia
        # con "attachment://reglas.gif" para que aparezca dentro del embed.
        gif_file = discord.File("gif/reglas.gif", filename="reglas.gif")
        embed.set_image(url="attachment://reglas.gif")

        # Footer
        embed.set_footer(text="Gracias por formar parte de nuestra comunidad 💖")

        await ctx.send(embed=embed, file=gif_file)


async def setup(bot: commands.Bot):
    await bot.add_cog(Reglas(bot))
