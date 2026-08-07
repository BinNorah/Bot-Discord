import json
import discord
from discord import app_commands
from discord.ext import commands

import config
from base_datos import db


class Configuracion(commands.Cog):
    """Comandos administrativos para configurar el bot en cada servidor."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # ─── /configurar_bienvenida ───────────────────────────────────────

    @commands.hybrid_command(
        name="configurar_bienvenida",
        description="Establece el canal donde se enviarán las bienvenidas y despedidas."
    )
    @commands.has_permissions(administrator=True)
    @app_commands.default_permissions(administrator=True)
    @app_commands.describe(canal="El canal de texto para los mensajes de bienvenida")
    async def configurar_bienvenida(self, ctx: commands.Context, canal: discord.TextChannel):
        await db.guardar_canal_bienvenida(str(ctx.guild.id), str(canal.id))

        embed = discord.Embed(
            title="✅ Canal de bienvenida configurado",
            description=f"Las bienvenidas y despedidas se enviarán a {canal.mention}.",
            color=config.COLOR_EXITO
        )
        await ctx.send(embed=embed, ephemeral=True)

    # ─── /configurar_modlog ───────────────────────────────────────────

    @commands.hybrid_command(
        name="configurar_modlog",
        description="Establece el canal donde se registrarán las acciones de moderación."
    )
    @commands.has_permissions(administrator=True)
    @app_commands.default_permissions(administrator=True)
    @app_commands.describe(canal="El canal de texto para los logs de moderación")
    async def configurar_modlog(self, ctx: commands.Context, canal: discord.TextChannel):
        await db.guardar_canal_modlog(str(ctx.guild.id), str(canal.id))

        embed = discord.Embed(
            title="✅ Canal de modlog configurado",
            description=f"Los registros de moderación se enviarán a {canal.mention}.",
            color=config.COLOR_EXITO
        )
        await ctx.send(embed=embed, ephemeral=True)

    # ─── /configurar_rol_miembro ──────────────────────────────────────

    @commands.hybrid_command(
        name="configurar_rol_miembro",
        description="Establece el rol que se otorga al verificarse un nuevo miembro."
    )
    @commands.has_permissions(administrator=True)
    @app_commands.default_permissions(administrator=True)
    @app_commands.describe(rol="El rol que se asignará al verificarse")
    async def configurar_rol_miembro(self, ctx: commands.Context, rol: discord.Role):
        await db.guardar_rol_miembro(str(ctx.guild.id), str(rol.id))

        embed = discord.Embed(
            title="✅ Rol de verificación configurado",
            description=f"Al verificarse, los miembros recibirán el rol {rol.mention}.",
            color=config.COLOR_EXITO
        )
        await ctx.send(embed=embed, ephemeral=True)

    # ─── /configurar_recompensa ───────────────────────────────────────

    @commands.hybrid_command(
        name="configurar_recompensa",
        description="Asigna un rol como recompensa al alcanzar cierto nivel."
    )
    @commands.has_permissions(administrator=True)
    @app_commands.default_permissions(administrator=True)
    @app_commands.describe(nivel="El nivel requerido para obtener el rol", rol="El rol de recompensa")
    async def configurar_recompensa(self, ctx: commands.Context, nivel: int, rol: discord.Role):
        if nivel < 1:
            return await ctx.send("❌ El nivel debe ser mayor o igual a 1.", ephemeral=True)

        # Leer las recompensas existentes
        conf = await db.obtener_configuracion(str(ctx.guild.id))
        if conf and conf[3]:
            roles_dict = json.loads(conf[3])
        else:
            roles_dict = {}

        # Actualizar con la nueva recompensa (las keys del JSON son siempre strings)
        roles_dict[str(nivel)] = str(rol.id)
        await db.guardar_roles_recompensa(str(ctx.guild.id), roles_dict)

        embed = discord.Embed(
            title="✅ Recompensa de nivel configurada",
            description=f"Al alcanzar el **Nivel {nivel}**, los miembros recibirán el rol {rol.mention}.",
            color=config.COLOR_EXITO
        )
        await ctx.send(embed=embed, ephemeral=True)

    # ─── /configurar_reglas ───────────────────────────────────────────

    @commands.hybrid_command(
        name="configurar_reglas",
        description="Establece el canal donde se publicarán las reglas del servidor."
    )
    @commands.has_permissions(administrator=True)
    @app_commands.default_permissions(administrator=True)
    @app_commands.describe(canal="El canal de texto para las reglas")
    async def configurar_reglas(self, ctx: commands.Context, canal: discord.TextChannel):
        await db.guardar_canal_reglas(str(ctx.guild.id), str(canal.id))

        embed = discord.Embed(
            title="✅ Canal de reglas configurado",
            description=f"Las reglas se publicarán en {canal.mention}.",
            color=config.COLOR_EXITO
        )
        await ctx.send(embed=embed, ephemeral=True)

    # ─── /configurar_verificacion ─────────────────────────────────────

    @commands.hybrid_command(
        name="configurar_verificacion",
        description="Establece el canal donde se publicará el panel de verificación."
    )
    @commands.has_permissions(administrator=True)
    @app_commands.default_permissions(administrator=True)
    @app_commands.describe(canal="El canal de texto para la verificación")
    async def configurar_verificacion(self, ctx: commands.Context, canal: discord.TextChannel):
        await db.guardar_canal_verificacion(str(ctx.guild.id), str(canal.id))

        embed = discord.Embed(
            title="✅ Canal de verificación configurado",
            description=f"El panel de verificación se publicará en {canal.mention}.",
            color=config.COLOR_EXITO
        )
        await ctx.send(embed=embed, ephemeral=True)

    # ─── /ver_configuracion ──────────────────────────────────────────

    @commands.hybrid_command(
        name="ver_configuracion",
        description="Muestra la configuración actual del bot en este servidor."
    )
    @commands.has_permissions(administrator=True)
    @app_commands.default_permissions(administrator=True)
    async def ver_configuracion(self, ctx: commands.Context):
        conf = await db.obtener_configuracion(str(ctx.guild.id))

        embed = discord.Embed(
            title=f"⚙️ Configuración de {ctx.guild.name}",
            color=config.COLOR_INFO
        )

        if not conf:
            embed.description = "Este servidor aún no tiene ninguna configuración guardada.\nUsa los comandos `/configurar_*` para empezar."
            return await ctx.send(embed=embed, ephemeral=True)

        # Índices: 0-bienvenida, 1-modlog, 2-rol, 3-recompensas, 4-reglas,
        #          5-verificacion, 6-confesiones, 7-cumpleanos, 8-logs,
        #          9-antispam_on, 10-antispam_cfg

        # Función auxiliar para mostrar canales
        def _canal_valor(idx, nombre_no_config="*No configurado*"):
            if conf[idx]:
                canal = ctx.guild.get_channel(int(conf[idx]))
                return canal.mention if canal else f"ID: {conf[idx]} (no encontrado)"
            return nombre_no_config

        # Canal de bienvenida
        embed.add_field(name="📢 Canal de Bienvenida", value=_canal_valor(0), inline=False)

        # Canal de modlog
        embed.add_field(name="📋 Canal de Modlog", value=_canal_valor(1), inline=False)

        # Canal de reglas
        embed.add_field(name="📜 Canal de Reglas", value=_canal_valor(4), inline=False)

        # Canal de verificación
        embed.add_field(name="✅ Canal de Verificación", value=_canal_valor(5), inline=False)

        # Canal de logs avanzados
        embed.add_field(name="📝 Canal de Logs Avanzados", value=_canal_valor(8), inline=False)

        # Canal de confesiones
        embed.add_field(name="🤫 Canal de Confesiones", value=_canal_valor(6), inline=False)

        # Canal de cumpleaños
        embed.add_field(name="🎂 Canal de Cumpleaños", value=_canal_valor(7), inline=False)

        # Rol de verificación
        if conf[2]:
            rol = ctx.guild.get_role(int(conf[2]))
            embed.add_field(name="🛡️ Rol de Verificación", value=rol.mention if rol else f"ID: {conf[2]} (no encontrado)", inline=False)
        else:
            embed.add_field(name="🛡️ Rol de Verificación", value="*No configurado*", inline=False)

        # Anti-spam
        antispam_estado = "✅ Activado" if conf[9] else "❌ Desactivado"
        embed.add_field(name="🔇 Anti-Spam", value=antispam_estado, inline=False)

        # Roles de recompensa
        if conf[3]:
            roles_dict = json.loads(conf[3])
            if roles_dict:
                lineas = []
                for nivel_str, rol_id_str in sorted(roles_dict.items(), key=lambda x: int(x[0])):
                    rol = ctx.guild.get_role(int(rol_id_str))
                    nombre_rol = rol.mention if rol else f"ID: {rol_id_str}"
                    lineas.append(f"Nivel **{nivel_str}** → {nombre_rol}")
                embed.add_field(name="🎖️ Recompensas por Nivel", value="\n".join(lineas), inline=False)
            else:
                embed.add_field(name="🎖️ Recompensas por Nivel", value="*No configuradas*", inline=False)
        else:
            embed.add_field(name="🎖️ Recompensas por Nivel", value="*No configuradas*", inline=False)

        # Cantidad de reglas
        reglas = await db.obtener_reglas(str(ctx.guild.id))
        embed.add_field(
            name="📝 Reglas del Servidor",
            value=f"**{len(reglas)}** reglas configuradas" if reglas else "*Sin reglas — usa `/agregar_regla`*",
            inline=False
        )

        await ctx.send(embed=embed, ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(Configuracion(bot))
