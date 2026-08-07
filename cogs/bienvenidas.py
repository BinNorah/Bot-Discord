import io
import logging
import os

import discord
from discord.ext import commands

import config
from base_datos import db

logger = logging.getLogger("bot")

# Intentar importar Pillow para las tarjetas de bienvenida
try:
    from PIL import Image, ImageDraw, ImageFont, ImageFilter
    PILLOW_DISPONIBLE = True
except ImportError:
    PILLOW_DISPONIBLE = False
    logger.warning("Pillow no está instalado. Las tarjetas de bienvenida usarán el modo simple (embed + GIF).")

# Ruta absoluta a la carpeta gif/, relativa a la ubicación de este archivo,
# para que funcione sin importar desde dónde se ejecute el bot (local o Railway).
DIRECTORIO_BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RUTA_GIF_BIENVENIDA = os.path.join(DIRECTORIO_BASE, "gif", "bienvenida.gif")
RUTA_GIF_DESPEDIDA = os.path.join(DIRECTORIO_BASE, "gif", "despedida.gif")


async def _generar_tarjeta_bienvenida(miembro: discord.Member) -> discord.File:
    """Genera una imagen de bienvenida personalizada con Pillow."""
    # Dimensiones de la tarjeta
    ancho, alto = 900, 300

    # Crear fondo con gradiente
    img = Image.new("RGBA", (ancho, alto))
    draw = ImageDraw.Draw(img)

    # Gradiente oscuro elegante (de izquierda a derecha)
    for x in range(ancho):
        ratio = x / ancho
        r = int(30 + (45 - 30) * ratio)
        g = int(30 + (35 - 30) * ratio)
        b = int(50 + (80 - 50) * ratio)
        draw.line([(x, 0), (x, alto)], fill=(r, g, b, 255))

    # Línea decorativa superior (rosa/morado)
    for x in range(ancho):
        ratio = x / ancho
        r = int(255 * (1 - ratio) + 138 * ratio)
        g = int(105 * (1 - ratio) + 43 * ratio)
        b = int(180 * (1 - ratio) + 226 * ratio)
        draw.line([(x, 0), (x, 4)], fill=(r, g, b, 255))

    # Descargar y colocar avatar
    try:
        avatar_bytes = await miembro.display_avatar.with_size(128).read()
        avatar_img = Image.open(io.BytesIO(avatar_bytes)).convert("RGBA").resize((130, 130))

        # Crear máscara circular para el avatar
        mascara = Image.new("L", (130, 130), 0)
        draw_mascara = ImageDraw.Draw(mascara)
        draw_mascara.ellipse([0, 0, 130, 130], fill=255)

        # Borde del avatar
        borde_size = 136
        borde = Image.new("RGBA", (borde_size, borde_size), (0, 0, 0, 0))
        draw_borde = ImageDraw.Draw(borde)
        draw_borde.ellipse([0, 0, borde_size, borde_size], fill=(255, 105, 180, 255))

        # Posicionar borde y avatar
        pos_avatar_x = 60
        pos_avatar_y = (alto - borde_size) // 2
        img.paste(borde, (pos_avatar_x, pos_avatar_y), borde)
        img.paste(avatar_img, (pos_avatar_x + 3, pos_avatar_y + 3), mascara)
    except Exception:
        logger.warning("No se pudo procesar el avatar para la tarjeta de bienvenida.")

    # Textos
    draw = ImageDraw.Draw(img)
    texto_x = 220

    # Intentar cargar una fuente, si no, usar la por defecto
    try:
        fuente_titulo = ImageFont.truetype("arial.ttf", 32)
        fuente_nombre = ImageFont.truetype("arialbd.ttf", 28)
        fuente_sub = ImageFont.truetype("arial.ttf", 18)
    except (OSError, IOError):
        try:
            fuente_titulo = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 32)
            fuente_nombre = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 28)
            fuente_sub = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 18)
        except (OSError, IOError):
            fuente_titulo = ImageFont.load_default()
            fuente_nombre = ImageFont.load_default()
            fuente_sub = ImageFont.load_default()

    # "¡Bienvenido/a!"
    draw.text((texto_x, 60), "¡Bienvenido/a!", fill=(255, 255, 255, 255), font=fuente_titulo)

    # Nombre del usuario
    nombre = miembro.display_name
    if len(nombre) > 25:
        nombre = nombre[:22] + "..."
    draw.text((texto_x, 110), nombre, fill=(255, 105, 180, 255), font=fuente_nombre)

    # "Eres el miembro #N"
    draw.text(
        (texto_x, 155),
        f"Eres el miembro #{miembro.guild.member_count}",
        fill=(180, 180, 200, 255),
        font=fuente_sub
    )

    # Nombre del servidor
    guild_name = miembro.guild.name
    if len(guild_name) > 35:
        guild_name = guild_name[:32] + "..."
    draw.text(
        (texto_x, 190),
        f"en {guild_name}",
        fill=(140, 140, 160, 255),
        font=fuente_sub
    )

    # Partículas decorativas (pequeños puntos)
    import random
    for _ in range(30):
        px = random.randint(0, ancho)
        py = random.randint(0, alto)
        alpha = random.randint(20, 80)
        size = random.randint(1, 3)
        draw.ellipse([px, py, px + size, py + size], fill=(255, 255, 255, alpha))

    # Guardar en buffer
    buffer = io.BytesIO()
    img.save(buffer, format="PNG", quality=95)
    buffer.seek(0)

    return discord.File(buffer, filename="bienvenida.png")


class Bienvenidas(commands.Cog):
    """Cog para gestionar los mensajes automáticos de bienvenida y despedida."""

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, miembro: discord.Member):
        # --- Obtener el canal de bienvenida desde la base de datos ---
        conf = await db.obtener_configuracion(str(miembro.guild.id))
        if not conf or not conf[0]:
            # El servidor no ha configurado un canal de bienvenida
            return

        canal_id = int(conf[0])
        canal = miembro.guild.get_channel(canal_id)
        if canal is None:
            logger.warning(
                "No se encontró el canal de bienvenida %s en el servidor %s.",
                canal_id,
                miembro.guild.id,
            )
            return

        embed = discord.Embed(
            title=f"¡Bienvenido a {miembro.guild.name}!",
            description="¡Llegaste en hora buena, espero disfrutes del servidor! Durante tu estadía, recuerda cumplir con las reglas.",
            color=config.COLOR_EXITO,
        )

        embed.set_footer(text=f"Norah | Miembros totales: {miembro.guild.member_count}")

        # Intentar generar tarjeta con Pillow
        if PILLOW_DISPONIBLE:
            try:
                archivo = await _generar_tarjeta_bienvenida(miembro)
                embed.set_image(url="attachment://bienvenida.png")
                await canal.send(
                    content=f"Bienvenido {miembro.mention} a {miembro.guild.name}!",
                    file=archivo,
                    embed=embed
                )
                return
            except Exception:
                logger.exception("Error al generar tarjeta de bienvenida, usando fallback.")

        # Fallback: GIF original
        if os.path.exists(RUTA_GIF_BIENVENIDA):
            archivo = discord.File(RUTA_GIF_BIENVENIDA, filename="bienvenida.gif")
            embed.set_image(url="attachment://bienvenida.gif")
            await canal.send(content=f"Bienvenido {miembro.mention} a {miembro.guild.name}!", file=archivo, embed=embed)
        else:
            await canal.send(content=f"Bienvenido {miembro.mention} a {miembro.guild.name}!", embed=embed)

    @commands.Cog.listener()
    async def on_member_remove(self, miembro: discord.Member):
        # --- Obtener el canal de bienvenida desde la base de datos ---
        conf = await db.obtener_configuracion(str(miembro.guild.id))
        if not conf or not conf[0]:
            return

        canal_id = int(conf[0])
        canal = miembro.guild.get_channel(canal_id)
        if canal is None:
            return

        embed = discord.Embed(
            title="¡Hasta pronto!",
            description=f"**{miembro.name}** ha abandonado el servidor. ¡Ojalá vuelvas pronto!",
            color=config.COLOR_ERROR,
        )

        embed.set_footer(text=f"Norah | Ahora somos {miembro.guild.member_count} miembros")

        if os.path.exists(RUTA_GIF_DESPEDIDA):
            archivo = discord.File(RUTA_GIF_DESPEDIDA, filename="despedida.gif")
            embed.set_image(url="attachment://despedida.gif")
            await canal.send(file=archivo, embed=embed)
        else:
            await canal.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Bienvenidas(bot))

