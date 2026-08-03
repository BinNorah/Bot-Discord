"""
Configuración centralizada del bot.
Solo contiene datos verdaderamente globales (credenciales, prefijo, colores).
Los IDs de canales y roles de cada servidor se almacenan en SQLite.
"""

import os
from dotenv import load_dotenv

load_dotenv()

# --- Credenciales ---
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

# --- Prefijo de comandos ---
PREFIJO = os.getenv("BOT_PREFIX") or "."

# --- Colores institucionales para los embeds ---
COLOR_PRINCIPAL = 0x2B2D31
COLOR_EXITO = 0x2ECC71
COLOR_ADVERTENCIA = 0xF1C40F
COLOR_ERROR = 0xE74C3C
COLOR_INFO = 0x3498DB
