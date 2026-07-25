"""
Configuración centralizada del bot.
Todas las constantes (IDs de canales, colores de embeds) viven aquí.
"""

import os
from dotenv import load_dotenv

load_dotenv()

# --- Credenciales ---
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

# --- Canales ---
# ID del canal #Bienvenido
CANAL_BIENVENIDA_ID = int(os.getenv("CANAL_BIENVENIDA_ID") or "1529957933947818135")
CANAL_MODLOG_ID = int(os.getenv("CANAL_MODLOG_ID") or "0") or None

# --- Prefijo de comandos ---
PREFIJO = os.getenv("BOT_PREFIX") or "."

# --- Configuración de Roles y Bienvenidas ---
# ID del rol que se asigna automáticamente al entrar al servidor (〈 Miembro 〉)
ROL_MIEMBRO_ID = int(os.getenv("ROL_MIEMBRO_ID") or "1235637700812607539")  # <--- Reemplaza el "0" por el ID real de tu rol o ponlo directo aquí

# --- Configuración de Niveles ---
# Diccionario de recompensas (Nivel: ID_Del_Rol)
ROLES_RECOMPENSA = {
    5: 111111111111111111,
    10: 222222222222222222,
    20: 333333333333333333
}

# --- Colores institucionales para los embeds ---
COLOR_PRINCIPAL = 0x2B2D31
COLOR_EXITO = 0x2ECC71
COLOR_ADVERTENCIA = 0xF1C40F
COLOR_ERROR = 0xE74C3C
COLOR_INFO = 0x3498DB
