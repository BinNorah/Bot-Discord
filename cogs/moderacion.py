import datetime
import discord
from discord.ext import commands

import config
from base_datos import db

def _puede_moderar(autor: discord.Member, objetivo: discord.Member) -> bool:
    """Evita que alguien modere a un miembro con rol igual o superior al suyo."""
    if autor.guild.owner_id == autor.id:
        return True
    return autor.top_role > objetivo.top_role

class Moderacion(commands.Cog):
    """Comandos de moderación del servidor con Slash Commands."""

    def __init__(self, bot):
        self.bot = bot

    async def _log(self, ctx, titulo: str, descripcion: str, color: int):
        embed = discord.Embed(title=titulo, description=descripcion, color=color)
        embed.set_footer(text=f"Moderador: {ctx.author}")
        embed.timestamp = discord.utils.utcnow()

        await ctx.send(embed=embed)

        # Leer el canal de modlog desde la base de datos
        conf = await db.obtener_configuracion(str(ctx.guild.id))
        if conf and conf[1]:
            canal = ctx.guild.get_channel(int(conf[1]))
            if canal:
                await canal.send(embed=embed)

    @commands.hybrid_command(name="kick", help="Expulsa a un miembro del servidor.")
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, miembro: discord.Member, *, razon: str = "No especificada"):
        if not _puede_moderar(ctx.author, miembro):
            return await ctx.send("No puedes expulsar a un miembro con un rol igual o superior al tuyo.")

        await miembro.kick(reason=f"{razon} (por {ctx.author})")
        descripcion = f"Usuario: {miembro.mention}\nRazón: {razon}"
        await self._log(ctx, "Miembro expulsado", descripcion, config.COLOR_ADVERTENCIA)

    @commands.hybrid_command(name="ban", help="Banea a un miembro del servidor.")
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, miembro: discord.Member, *, razon: str = "No especificada"):
        if not _puede_moderar(ctx.author, miembro):
            return await ctx.send("No puedes banear a un miembro con un rol igual o superior al tuyo.")

        await miembro.ban(reason=f"{razon} (por {ctx.author})")
        descripcion = f"Usuario: {miembro.mention}\nRazón: {razon}"
        await self._log(ctx, "Miembro baneado", descripcion, config.COLOR_ERROR)

    @commands.hybrid_command(name="unban", help="Remueve el baneo de un usuario por su ID o nombre de usuario.")
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx, *, usuario_identificador: str):
        ban_entries = [ban async for ban in ctx.guild.bans()]
        usuario_a_desbanear = None

        if usuario_identificador.isdigit():
            user_id = int(usuario_identificador)
            for ban_entry in ban_entries:
                if ban_entry.user.id == user_id:
                    usuario_a_desbanear = ban_entry.user
                    break
        else:
            for ban_entry in ban_entries:
                user = ban_entry.user
                nombre_completo = f"{user.name}#{user.discriminator}"
                if usuario_identificador.lower() in user.name.lower() or usuario_identificador.lower() in nombre_completo.lower():
                    usuario_a_desbanear = user
                    break

        if usuario_a_desbanear is None:
            await ctx.send(" No se encontró a ningún usuario baneado con ese nombre o ID en este servidor.")
            return

        try:
            await ctx.guild.unban(usuario_a_desbanear)
            embed = discord.Embed(
                title="Miembro Desbaneado",
                description=f"Usuario: **{usuario_a_desbanear}**",
                color=config.COLOR_EXITO
            )
            embed.set_footer(text=f"Moderador: {ctx.author.display_name}")
            await ctx.send(embed=embed)
        except discord.HTTPException:
            await ctx.send(" Hubo un error al intentar desbanear al usuario.")

    @commands.hybrid_command(name="mute", help="Silencia temporalmente a un miembro.")
    @commands.has_permissions(moderate_members=True)
    async def mute(self, ctx, miembro: discord.Member, minutos: int, *, razon: str = "No especificada"):
        if not _puede_moderar(ctx.author, miembro):
            return await ctx.send("No puedes silenciar a un miembro con un rol igual o superior al tuyo.")
        if minutos <= 0:
            return await ctx.send("La duración debe ser mayor a 0 minutos.")

        duracion = datetime.timedelta(minutes=minutos)
        await miembro.timeout(duracion, reason=f"{razon} (por {ctx.author})")
        descripcion = f"Usuario: {miembro.mention}\nDuración: {minutos} min\nRazón: {razon}"
        await self._log(ctx, "Miembro silenciado", descripcion, config.COLOR_ADVERTENCIA)

    @commands.hybrid_command(name="unmute", help="Quita el silencio a un miembro.")
    @commands.has_permissions(moderate_members=True)
    async def unmute(self, ctx, miembro: discord.Member):
        if not _puede_moderar(ctx.author, miembro):
            return await ctx.send("No tienes permisos de jerarquía sobre este usuario.")
            
        await miembro.timeout(None, reason=f"Desmuteado por {ctx.author}")
        await self._log(ctx, "Silencio removido", f"Usuario: {miembro.mention}", config.COLOR_EXITO)

    @commands.hybrid_command(name="clear", help="Elimina una cantidad de mensajes.")
    @commands.has_permissions(manage_messages=True)
    async def clear(self, ctx, cantidad: int = 5):
        if cantidad < 1 or cantidad > 100:
            return await ctx.send("Indica una cantidad entre 1 y 100.")

        eliminados = await ctx.channel.purge(limit=cantidad + 1)
        msg = await ctx.send(f"Se eliminaron {len(eliminados) - 1} mensajes correctamente.")
        await msg.delete(delay=3)

    @commands.hybrid_command(name="warn", help="Envía una advertencia formal y la guarda.")
    @commands.has_permissions(kick_members=True)
    async def warn(self, ctx, miembro: discord.Member, *, razon: str = "No especificada"):
        await db.registrar_advertencia(
            servidor_id=str(ctx.guild.id),
            usuario_id=str(miembro.id),
            moderador_id=str(ctx.author.id),
            razon=razon
        )

        descripcion = f"Usuario: {miembro.mention}\nRazón: {razon}"
        await self._log(ctx, "Advertencia Registrada", descripcion, config.COLOR_ADVERTENCIA)
        
        try:
            await miembro.send(f"Has recibido una advertencia en **{ctx.guild.name}** por: {razon}")
        except discord.Forbidden:
            pass 

    @commands.hybrid_command(name="historial", help="Muestra el historial de advertencias.")
    @commands.has_permissions(moderate_members=True)
    async def historial(self, ctx, miembro: discord.Member):
        registros = await db.consultar_historial(str(ctx.guild.id), str(miembro.id))

        if not registros:
            return await ctx.send(f"{miembro.mention} no tiene ninguna advertencia registrada.")

        embed = discord.Embed(
            title=f"Historial de Advertencias: {miembro.display_name}",
            description=f"Total de advertencias: **{len(registros)}**",
            color=config.COLOR_INFO
        )
        embed.set_thumbnail(url=miembro.display_avatar.url)

        for i, registro in enumerate(registros, start=1):
            moderador_id, razon, fecha = registro
            fecha_corta = fecha.split()[0] 
            
            embed.add_field(
                name=f"#{i} - {fecha_corta}",
                value=f"**Razón:** {razon}\n**Moderador:** <@{moderador_id}>",
                inline=False
            )

        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Moderacion(bot))