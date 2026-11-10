"""
Configuración centralizada del bot.
Solo contiene datos verdaderamente globales (credenciales, prefijo, colores).
Los IDs de canales y roles de cada servidor se almacenan en SQLite.
"""

import os
import sys
from dotenv import load_dotenv

load_dotenv()

# --- Credenciales ---
def _obtener_token():
    """Obtiene y limpia el token de Discord, tolerando espacios o nombres alternativos."""
    # 1. Búsqueda directa estándar
    token = os.getenv("DISCORD_TOKEN")
    if token and token.strip():
        return token.strip().strip('"').strip("'")
    
    # 2. Búsqueda insensible a mayúsculas/minúsculas y tolerante a espacios accidentales
    for key, val in os.environ.items():
        if key.strip().upper() in ("DISCORD_TOKEN", "DISCORDTOKEN", "TOKEN", "BOT_TOKEN"):
            if val and val.strip():
                return val.strip().strip('"').strip("'")
    return None

DISCORD_TOKEN = _obtener_token()

# --- Prefijo de comandos ---
PREFIJO = os.getenv("BOT_PREFIX") or "."

# --- Colores institucionales para los embeds ---
COLOR_PRINCIPAL = 0x2B2D31
COLOR_EXITO = 0x2ECC71
COLOR_ADVERTENCIA = 0xF1C40F
COLOR_ERROR = 0xE74C3C
COLOR_INFO = 0x3498DB
