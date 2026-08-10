import json
import time
import random
import discord
from discord.ext import commands

from base_datos import db
import config

def calcular_xp_necesaria(nivel: int) -> int:
    """Fórmula para calcular cuánta XP total se necesita para el siguiente nivel."""
    return 5 * (nivel ** 2) + 50 * nivel + 100

class Niveles(commands.Cog):
    """Sistema de Experiencia, Niveles y Perfiles de Usuario."""

    def __init__(self, bot):
        self.bot = bot
        self.enfriamiento = 60.0  

    @commands.Cog.listener()
    async def on_message(self, mensaje: discord.Message):
        if mensaje.author.bot or mensaje.guild is None or mensaje.content.startswith(config.PREFIJO):
            return

        servidor_id = str(mensaje.guild.id)
        usuario_id = str(mensaje.author.id)
        tiempo_actual = time.time()

        xp, nivel, monedas, ultimo_mensaje = await db.obtener_perfil(servidor_id, usuario_id)

        if (tiempo_actual - ultimo_mensaje) < self.enfriamiento:
            return

        xp_ganada = random.randint(15, 25)
        xp += xp_ganada
        nuevo_ultimo_mensaje = tiempo_actual

        xp_necesaria = calcular_xp_necesaria(nivel)
        subio_nivel = False

        if xp >= xp_necesaria:
            nivel += 1
            subio_nivel = True

        await db.actualizar_perfil(servidor_id, usuario_id, xp, nivel, monedas, nuevo_ultimo_mensaje)

        if subio_nivel:
            embed = discord.Embed(
                title="¡Subida de Nivel!",
                description=f"¡Felicidades {mensaje.author.mention}! Has alcanzado el **Nivel {nivel}**.",
                color=config.COLOR_EXITO
            )
            await mensaje.channel.send(embed=embed)

            # Leer los roles de recompensa desde la base de datos
            conf = await db.obtener_configuracion(servidor_id)
            if conf and conf[3]:
                roles_recompensa = json.loads(conf[3])
                # Las keys del JSON son siempre strings, comparar con str(nivel)
                rol_id_str = roles_recompensa.get(str(nivel))
                if rol_id_str:
                    rol = mensaje.guild.get_role(int(rol_id_str))
                    if rol:
                        try:
                            await mensaje.author.add_roles(rol, reason=f"Alcanzó el nivel {nivel}")
                            await mensaje.channel.send(f" {mensaje.author.mention} ha desbloqueado el rol: **{rol.name}**")
                        except discord.Forbidden:
                            pass 

    @commands.hybrid_command(name="perfil", help="Muestra tu tarjeta de perfil, nivel y monedas.")
    async def perfil(self, ctx, miembro: discord.Member = None):
        usuario = miembro or ctx.author
        
        if usuario.bot:
            return await ctx.send("Los bots no tienen perfiles de experiencia.")

        xp, nivel, monedas, _ = await db.obtener_perfil(str(ctx.guild.id), str(usuario.id))
        xp_siguiente = calcular_xp_necesaria(nivel)
        
        porcentaje = min(int((xp / xp_siguiente) * 10), 10)
        barra_progreso = "" * porcentaje + "" * (10 - porcentaje)

        embed = discord.Embed(title=f"Perfil de {usuario.display_name}", color=config.COLOR_PRINCIPAL)
        embed.set_thumbnail(url=usuario.display_avatar.url)
        
        embed.add_field(name="Nivel", value=f"**{nivel}**", inline=True)
        embed.add_field(name="Experiencia", value=f"{xp} / {xp_siguiente} XP\n{barra_progreso}", inline=True)
        embed.add_field(name="Economía", value=f" {monedas} Monedas", inline=False)
        
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Niveles(bot))