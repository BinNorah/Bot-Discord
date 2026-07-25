import asyncio
import logging
import os

import discord
from discord.ext import commands

import config
from base_datos import db

# --- Logging profesional ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.FileHandler("bot.log", encoding="utf-8"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger("bot")

ID_SERVIDOR = 1235469252874604585  # 👈 ID de "Hub Central" (tomado de tus capturas)

class MiBotProfesional(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True

        super().__init__(
            command_prefix=config.PREFIJO,
            intents=intents,
            help_command=None
        )

    async def setup_hook(self):
        """Este método se ejecuta antes de que el bot se conecte a Discord."""
        # 1. Inicializar la base de datos de forma asíncrona (aiosqlite)
        logger.info("Inicializando base de datos asíncrona...")
        await db.inicializar_tablas()
        logger.info("Base de datos lista.")

        # 2. Cargar todos los cogs dinámicamente
        carpeta_cogs = "./cogs"
        for archivo in os.listdir(carpeta_cogs):
            if archivo.endswith(".py") and archivo != "__init__.py":
                nombre_modulo = f"cogs.{archivo[:-3]}"
                try:
                    await self.load_extension(nombre_modulo)
                    logger.info("Cog cargado correctamente: %s", nombre_modulo)
                except Exception:
                    logger.exception("No se pudo cargar el cog: %s", nombre_modulo)

        # 3. Sincronizamos el árbol de comandos de barra (Slash Commands) solo en tu servidor (instantáneo)
        logger.info("Sincronizando comandos de barra...")
        try:
            guild = discord.Object(id=ID_SERVIDOR)
            self.tree.copy_global_to(guild=guild)
            synced = await self.tree.sync(guild=guild)
            logger.info("¡Comandos de barra sincronizados en guild! Total: %d comandos", len(synced))
        except discord.Forbidden:
            logger.warning(
                "No se pudo sincronizar en guild (falta el scope 'applications.commands'). "
                "Intentando sincronización global (puede tardar hasta 1 hora en Discord)..."
            )
            try:
                synced = await self.tree.sync()
                logger.info("¡Comandos sincronizados globalmente! Total: %d comandos", len(synced))
            except Exception:
                logger.exception("También falló la sincronización global.")
    async def on_ready(self):
        logger.info("Conectado como %s (ID: %s)", self.user, self.user.id)
        actividad = discord.Activity(
            type=discord.ActivityType.watching,
            name="/help"
        )
        await self.change_presence(activity=actividad, status=discord.Status.online)

    async def on_command_error(self, ctx, error):
        """Manejador global de errores para todos los comandos."""
        if isinstance(error, commands.CommandNotFound):
            return

        if isinstance(error, commands.MissingPermissions):
            await ctx.send("❌ No tienes permisos suficientes para usar este comando.", ephemeral=True)
        elif isinstance(error, commands.BotMissingPermissions):
            await ctx.send("❌ No tengo los permisos necesarios en este servidor para hacer eso.")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f"❌ Te faltó incluir un dato. Falta el parámetro: `{error.param.name}`")
        elif isinstance(error, commands.MemberNotFound):
            await ctx.send("❌ No pude encontrar a ese usuario en el servidor.")
        else:
            logger.error("Error no manejado en el comando %s: %s", ctx.command, error)
            await ctx.send("⚠️ Ocurrió un error inesperado al intentar ejecutar el comando.")

bot = MiBotProfesional()

async def main():
    if not config.DISCORD_TOKEN:
        logger.error("No se encontró DISCORD_TOKEN en las variables de entorno.")
        return

    async with bot:
        await bot.start(config.DISCORD_TOKEN)

if __name__ == "__main__":
    asyncio.run(main())
