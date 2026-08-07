import datetime
import logging

import discord
from discord import app_commands
from discord.ext import commands, tasks

import config
from base_datos import db

logger = logging.getLogger("bot")

MESES = [
    "", "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
    "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
]


class Cumpleanos(commands.Cog):
    """Sistema de cumpleaños con felicitaciones automáticas."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.revisar_cumpleanos.start()

    def cog_unload(self):
        self.revisar_cumpleanos.cancel()

    @commands.hybrid_command(
        name="cumpleaños",
        description="Registra tu fecha de cumpleaños para recibir una felicitación."
    )
    @app_commands.describe(
        dia="Día de tu cumpleaños (1-31)",
        mes="Mes de tu cumpleaños (1-12)"
    )
    async def cumpleanos(self, ctx: commands.Context, dia: int, mes: int):
        # Validar fecha
        if mes < 1 or mes > 12:
            return await ctx.send("❌ El mes debe estar entre 1 y 12.", ephemeral=True)
        if dia < 1 or dia > 31:
            return await ctx.send("❌ El día debe estar entre 1 y 31.", ephemeral=True)

        # Validar que la fecha sea real
        try:
            datetime.date(2000, mes, dia)  # Año bisiesto para validar 29 Feb
        except ValueError:
            return await ctx.send(
                f"❌ La fecha {dia}/{mes} no es válida.",
                ephemeral=True
            )

        await db.registrar_cumpleanos(str(ctx.guild.id), str(ctx.author.id), dia, mes)

        embed = discord.Embed(
            title="🎂  ¡Cumpleaños registrado!",
            description=(
                f"Tu cumpleaños ha sido registrado como el **{dia} de {MESES[mes]}**.\n\n"
                "Recibirás una felicitación automática ese día. 🥳"
            ),
            color=0xFF69B4
        )
        embed.set_thumbnail(url=ctx.author.display_avatar.url)
        await ctx.send(embed=embed, ephemeral=True)

    @commands.hybrid_command(
        name="mi_cumpleaños",
        description="Consulta tu fecha de cumpleaños registrada."
    )
    async def mi_cumpleanos(self, ctx: commands.Context):
        resultado = await db.obtener_cumpleanos_usuario(str(ctx.guild.id), str(ctx.author.id))

        if not resultado:
            return await ctx.send(
                "❌ No tienes un cumpleaños registrado. Usa `/cumpleaños día mes` para registrarlo.",
                ephemeral=True
            )

        dia, mes = resultado
        embed = discord.Embed(
            title="🎂  Tu cumpleaños",
            description=f"Tu cumpleaños registrado es el **{dia} de {MESES[mes]}**.",
            color=0xFF69B4
        )
        embed.set_thumbnail(url=ctx.author.display_avatar.url)
        await ctx.send(embed=embed, ephemeral=True)

    @commands.hybrid_command(
        name="proximos_cumpleaños",
        description="Muestra los próximos cumpleaños del servidor."
    )
    async def proximos_cumpleanos(self, ctx: commands.Context):
        todos = await db.obtener_cumpleanos_servidor(str(ctx.guild.id))

        if not todos:
            return await ctx.send(
                "❌ No hay cumpleaños registrados en este servidor.",
                ephemeral=True
            )

        hoy = datetime.date.today()

        # Ordenar por proximidad al día de hoy
        def clave_proximidad(entry):
            _, dia, mes = entry
            try:
                fecha = datetime.date(hoy.year, mes, dia)
                if fecha < hoy:
                    fecha = datetime.date(hoy.year + 1, mes, dia)
            except ValueError:
                fecha = datetime.date(hoy.year, mes, min(dia, 28))
            return fecha

        ordenados = sorted(todos, key=clave_proximidad)[:10]

        embed = discord.Embed(
            title=f"🎂  Próximos cumpleaños en {ctx.guild.name}",
            color=0xFF69B4
        )

        lineas = []
        for usuario_id, dia, mes in ordenados:
            miembro = ctx.guild.get_member(int(usuario_id))
            nombre = miembro.display_name if miembro else f"Usuario ({usuario_id})"

            try:
                fecha = datetime.date(hoy.year, mes, dia)
                if fecha < hoy:
                    fecha = datetime.date(hoy.year + 1, mes, dia)
            except ValueError:
                fecha = datetime.date(hoy.year, mes, min(dia, 28))

            dias_restantes = (fecha - hoy).days
            indicador = "🎉 **¡HOY!**" if dias_restantes == 0 else f"en {dias_restantes} días"

            lineas.append(f"🎂 **{nombre}** — {dia} de {MESES[mes]} ({indicador})")

        embed.description = "\n".join(lineas)
        embed.set_footer(text="Usa /cumpleaños día mes para registrarte")
        await ctx.send(embed=embed)

    @commands.hybrid_command(
        name="configurar_cumpleaños",
        description="Establece el canal donde se enviarán las felicitaciones de cumpleaños."
    )
    @commands.has_permissions(administrator=True)
    @app_commands.default_permissions(administrator=True)
    @app_commands.describe(canal="El canal para las felicitaciones de cumpleaños")
    async def configurar_cumpleanos_canal(self, ctx: commands.Context, canal: discord.TextChannel):
        await db.guardar_canal_cumpleanos(str(ctx.guild.id), str(canal.id))

        embed = discord.Embed(
            title="✅  Canal de cumpleaños configurado",
            description=f"Las felicitaciones de cumpleaños se enviarán a {canal.mention}.",
            color=config.COLOR_EXITO
        )
        await ctx.send(embed=embed, ephemeral=True)

    @tasks.loop(time=datetime.time(hour=7, minute=0))  # 7:00 AM UTC
    async def revisar_cumpleanos(self):
        """Revisa diariamente si hay cumpleaños que felicitar."""
        try:
            hoy = datetime.date.today()
            cumpleanos_hoy = await db.obtener_cumpleanos_hoy(hoy.day, hoy.month)

            for servidor_id, usuario_id in cumpleanos_hoy:
                guild = self.bot.get_guild(int(servidor_id))
                if not guild:
                    continue

                miembro = guild.get_member(int(usuario_id))
                if not miembro:
                    continue

                # Obtener canal de cumpleaños o canal de bienvenida como fallback
                conf = await db.obtener_configuracion(servidor_id)
                canal = None

                if conf and conf[7]:  # canal_cumpleanos_id
                    canal = guild.get_channel(int(conf[7]))
                elif conf and conf[0]:  # canal_bienvenida_id como fallback
                    canal = guild.get_channel(int(conf[0]))

                if not canal:
                    continue

                embed = discord.Embed(
                    title="🎂🎉  ¡Feliz Cumpleaños!  🎉🎂",
                    description=(
                        f"¡Hoy es el cumpleaños de {miembro.mention}!\n\n"
                        f"🥳 ¡Toda la comunidad de **{guild.name}** te desea un "
                        f"maravilloso día lleno de alegría! 🎁🎈"
                    ),
                    color=0xFF69B4
                )
                embed.set_thumbnail(url=miembro.display_avatar.url)
                embed.set_footer(text="¡Registra tu cumpleaños con /cumpleaños día mes!")
                embed.timestamp = discord.utils.utcnow()

                try:
                    await canal.send(content=miembro.mention, embed=embed)
                except Exception:
                    logger.exception("Error al felicitar cumpleaños de %s en %s",
                                     usuario_id, servidor_id)

        except Exception:
            logger.exception("Error en el task loop de cumpleaños")

    @revisar_cumpleanos.before_loop
    async def antes_de_revisar(self):
        await self.bot.wait_until_ready()


async def setup(bot: commands.Bot):
    await bot.add_cog(Cumpleanos(bot))
