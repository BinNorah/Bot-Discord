import aiosqlite

class GestorBaseDatos:
    """Clase para manejar las conexiones y operaciones asíncronas de SQLite3."""
    
    def __init__(self, ruta_archivo="datos_bot.db"):
        self.ruta = ruta_archivo

    async def inicializar_tablas(self):
        """Crea las tablas necesarias si no existen."""
        async with aiosqlite.connect(self.ruta) as conexion:
            # TABLA 1: Advertencias
            await conexion.execute('''
                CREATE TABLE IF NOT EXISTS advertencias (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    servidor_id TEXT NOT NULL,
                    usuario_id TEXT NOT NULL,
                    moderador_id TEXT NOT NULL,
                    razon TEXT NOT NULL,
                    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # TABLA 2: Economía y Niveles
            await conexion.execute('''
                CREATE TABLE IF NOT EXISTS usuarios_rpg (
                    servidor_id TEXT,
                    usuario_id TEXT,
                    xp INTEGER DEFAULT 0,
                    nivel INTEGER DEFAULT 0,
                    monedas INTEGER DEFAULT 0,
                    ultimo_mensaje REAL DEFAULT 0.0,
                    PRIMARY KEY (servidor_id, usuario_id)
                )
            ''')
            await conexion.commit()

    async def registrar_advertencia(self, servidor_id: str, usuario_id: str, moderador_id: str, razon: str):
        """Guarda una nueva advertencia en la base de datos."""
        async with aiosqlite.connect(self.ruta) as conexion:
            await conexion.execute('''
                INSERT INTO advertencias (servidor_id, usuario_id, moderador_id, razon)
                VALUES (?, ?, ?, ?)
            ''', (servidor_id, usuario_id, moderador_id, razon))
            await conexion.commit()

    async def consultar_historial(self, servidor_id: str, usuario_id: str) -> list:
        """Obtiene todas las advertencias de un usuario específico en el servidor."""
        async with aiosqlite.connect(self.ruta) as conexion:
            async with conexion.execute('''
                SELECT moderador_id, razon, fecha FROM advertencias
                WHERE servidor_id = ? AND usuario_id = ?
                ORDER BY fecha DESC
            ''', (servidor_id, usuario_id)) as cursor:
                return await cursor.fetchall()
    
    async def obtener_perfil(self, servidor_id: str, usuario_id: str):
        """Obtiene o crea el perfil de un usuario."""
        async with aiosqlite.connect(self.ruta) as conexion:
            async with conexion.execute('''
                SELECT xp, nivel, monedas, ultimo_mensaje 
                FROM usuarios_rpg 
                WHERE servidor_id = ? AND usuario_id = ?
            ''', (servidor_id, usuario_id)) as cursor:
                resultado = await cursor.fetchone()
            
            if not resultado:
                # Si el usuario no existe, lo creamos con valores por defecto
                await conexion.execute('''
                    INSERT INTO usuarios_rpg (servidor_id, usuario_id) 
                    VALUES (?, ?)
                ''', (servidor_id, usuario_id))
                await conexion.commit()
                resultado = (0, 0, 0, 0.0)
                
            return resultado

    async def actualizar_perfil(self, servidor_id: str, usuario_id: str, xp: int, nivel: int, monedas: int, ultimo_mensaje: float):
        """Actualiza los datos del usuario en la base de datos."""
        async with aiosqlite.connect(self.ruta) as conexion:
            await conexion.execute('''
                UPDATE usuarios_rpg 
                SET xp = ?, nivel = ?, monedas = ?, ultimo_mensaje = ?
                WHERE servidor_id = ? AND usuario_id = ?
            ''', (xp, nivel, monedas, ultimo_mensaje, servidor_id, usuario_id))
            await conexion.commit()

# Instancia global para importar fácilmente en los cogs
db = GestorBaseDatos()