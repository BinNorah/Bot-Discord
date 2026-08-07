import json
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
                    total_mensajes INTEGER DEFAULT 0,
                    PRIMARY KEY (servidor_id, usuario_id)
                )
            ''')

            # TABLA 3: Configuración por servidor (multi-guild)
            await conexion.execute('''
                CREATE TABLE IF NOT EXISTS configuracion_servidor (
                    servidor_id           TEXT PRIMARY KEY,
                    canal_bienvenida_id   TEXT DEFAULT NULL,
                    canal_modlog_id       TEXT DEFAULT NULL,
                    rol_miembro_id        TEXT DEFAULT NULL,
                    roles_recompensa      TEXT DEFAULT '{}',
                    canal_reglas_id       TEXT DEFAULT NULL,
                    canal_verificacion_id TEXT DEFAULT NULL,
                    canal_confesiones_id  TEXT DEFAULT NULL,
                    canal_cumpleanos_id   TEXT DEFAULT NULL,
                    canal_logs_id         TEXT DEFAULT NULL,
                    antispam_activado     INTEGER DEFAULT 0,
                    antispam_config       TEXT DEFAULT '{}'
                )
            ''')

            # TABLA 4: Reglas por servidor
            await conexion.execute('''
                CREATE TABLE IF NOT EXISTS reglas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    servidor_id TEXT NOT NULL,
                    numero INTEGER NOT NULL,
                    titulo TEXT NOT NULL,
                    contenido TEXT NOT NULL
                )
            ''')

            # TABLA 5: Sorteos activos
            await conexion.execute('''
                CREATE TABLE IF NOT EXISTS sorteos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    servidor_id TEXT NOT NULL,
                    canal_id TEXT NOT NULL,
                    mensaje_id TEXT NOT NULL,
                    premio TEXT NOT NULL,
                    organizador_id TEXT NOT NULL,
                    fecha_fin REAL NOT NULL,
                    ganadores_count INTEGER DEFAULT 1,
                    finalizado INTEGER DEFAULT 0
                )
            ''')

            # TABLA 6: Recordatorios
            await conexion.execute('''
                CREATE TABLE IF NOT EXISTS recordatorios (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    usuario_id TEXT NOT NULL,
                    servidor_id TEXT NOT NULL,
                    canal_id TEXT NOT NULL,
                    mensaje TEXT NOT NULL,
                    fecha_recordar REAL NOT NULL,
                    completado INTEGER DEFAULT 0
                )
            ''')

            # TABLA 7: Cumpleaños
            await conexion.execute('''
                CREATE TABLE IF NOT EXISTS cumpleanos (
                    servidor_id TEXT NOT NULL,
                    usuario_id TEXT NOT NULL,
                    dia INTEGER NOT NULL,
                    mes INTEGER NOT NULL,
                    PRIMARY KEY (servidor_id, usuario_id)
                )
            ''')

            # TABLA 8: Logros de usuarios
            await conexion.execute('''
                CREATE TABLE IF NOT EXISTS logros_usuarios (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    servidor_id TEXT NOT NULL,
                    usuario_id TEXT NOT NULL,
                    logro_id TEXT NOT NULL,
                    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(servidor_id, usuario_id, logro_id)
                )
            ''')

            # ─── Migraciones para tablas existentes ───────────────────
            columnas_migracion = [
                ('configuracion_servidor', 'canal_reglas_id', 'TEXT DEFAULT NULL'),
                ('configuracion_servidor', 'canal_verificacion_id', 'TEXT DEFAULT NULL'),
                ('configuracion_servidor', 'canal_confesiones_id', 'TEXT DEFAULT NULL'),
                ('configuracion_servidor', 'canal_cumpleanos_id', 'TEXT DEFAULT NULL'),
                ('configuracion_servidor', 'canal_logs_id', 'TEXT DEFAULT NULL'),
                ('configuracion_servidor', 'antispam_activado', 'INTEGER DEFAULT 0'),
                ('configuracion_servidor', 'antispam_config', "TEXT DEFAULT '{}'"),
                ('usuarios_rpg', 'total_mensajes', 'INTEGER DEFAULT 0'),
            ]

            for tabla, columna, tipo in columnas_migracion:
                try:
                    await conexion.execute(
                        f'ALTER TABLE {tabla} ADD COLUMN {columna} {tipo}'
                    )
                except Exception:
                    pass  # La columna ya existe

            await conexion.commit()

    # ─── Métodos de Advertencias ──────────────────────────────────────

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
    
    # ─── Métodos de Perfiles / Niveles ────────────────────────────────

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

    async def incrementar_mensajes(self, servidor_id: str, usuario_id: str):
        """Incrementa el contador total de mensajes de un usuario."""
        async with aiosqlite.connect(self.ruta) as conexion:
            await conexion.execute('''
                UPDATE usuarios_rpg 
                SET total_mensajes = total_mensajes + 1
                WHERE servidor_id = ? AND usuario_id = ?
            ''', (servidor_id, usuario_id))
            await conexion.commit()

    async def obtener_total_mensajes(self, servidor_id: str, usuario_id: str) -> int:
        """Obtiene el total de mensajes de un usuario."""
        async with aiosqlite.connect(self.ruta) as conexion:
            async with conexion.execute('''
                SELECT total_mensajes FROM usuarios_rpg
                WHERE servidor_id = ? AND usuario_id = ?
            ''', (servidor_id, usuario_id)) as cursor:
                resultado = await cursor.fetchone()
                return resultado[0] if resultado else 0

    # ─── Métodos de Configuración por Servidor (multi-guild) ──────────

    async def obtener_configuracion(self, servidor_id: str):
        """Devuelve la configuración del servidor o None si no existe.
        
        Retorna una tupla con:
        (canal_bienvenida_id, canal_modlog_id, rol_miembro_id, roles_recompensa,
         canal_reglas_id, canal_verificacion_id, canal_confesiones_id,
         canal_cumpleanos_id, canal_logs_id, antispam_activado, antispam_config)
        Índices: 0-bienvenida, 1-modlog, 2-rol, 3-recompensas, 4-reglas,
                 5-verificacion, 6-confesiones, 7-cumpleanos, 8-logs,
                 9-antispam_on, 10-antispam_cfg
        """
        async with aiosqlite.connect(self.ruta) as conexion:
            async with conexion.execute('''
                SELECT canal_bienvenida_id, canal_modlog_id, rol_miembro_id, roles_recompensa,
                       canal_reglas_id, canal_verificacion_id, canal_confesiones_id,
                       canal_cumpleanos_id, canal_logs_id, antispam_activado, antispam_config
                FROM configuracion_servidor
                WHERE servidor_id = ?
            ''', (servidor_id,)) as cursor:
                return await cursor.fetchone()

    async def guardar_canal_bienvenida(self, servidor_id: str, canal_id: str):
        """Guarda o actualiza el canal de bienvenida para un servidor."""
        async with aiosqlite.connect(self.ruta) as conexion:
            await conexion.execute('''
                INSERT INTO configuracion_servidor (servidor_id, canal_bienvenida_id)
                VALUES (?, ?)
                ON CONFLICT(servidor_id) DO UPDATE SET canal_bienvenida_id = excluded.canal_bienvenida_id
            ''', (servidor_id, canal_id))
            await conexion.commit()

    async def guardar_canal_modlog(self, servidor_id: str, canal_id: str):
        """Guarda o actualiza el canal de modlog para un servidor."""
        async with aiosqlite.connect(self.ruta) as conexion:
            await conexion.execute('''
                INSERT INTO configuracion_servidor (servidor_id, canal_modlog_id)
                VALUES (?, ?)
                ON CONFLICT(servidor_id) DO UPDATE SET canal_modlog_id = excluded.canal_modlog_id
            ''', (servidor_id, canal_id))
            await conexion.commit()

    async def guardar_rol_miembro(self, servidor_id: str, rol_id: str):
        """Guarda o actualiza el rol de verificación para un servidor."""
        async with aiosqlite.connect(self.ruta) as conexion:
            await conexion.execute('''
                INSERT INTO configuracion_servidor (servidor_id, rol_miembro_id)
                VALUES (?, ?)
                ON CONFLICT(servidor_id) DO UPDATE SET rol_miembro_id = excluded.rol_miembro_id
            ''', (servidor_id, rol_id))
            await conexion.commit()

    async def guardar_roles_recompensa(self, servidor_id: str, dict_roles: dict):
        """Guarda o actualiza los roles de recompensa por nivel (como JSON)."""
        roles_json = json.dumps(dict_roles)
        async with aiosqlite.connect(self.ruta) as conexion:
            await conexion.execute('''
                INSERT INTO configuracion_servidor (servidor_id, roles_recompensa)
                VALUES (?, ?)
                ON CONFLICT(servidor_id) DO UPDATE SET roles_recompensa = excluded.roles_recompensa
            ''', (servidor_id, roles_json))
            await conexion.commit()

    async def guardar_canal_reglas(self, servidor_id: str, canal_id: str):
        """Guarda o actualiza el canal de reglas para un servidor."""
        async with aiosqlite.connect(self.ruta) as conexion:
            await conexion.execute('''
                INSERT INTO configuracion_servidor (servidor_id, canal_reglas_id)
                VALUES (?, ?)
                ON CONFLICT(servidor_id) DO UPDATE SET canal_reglas_id = excluded.canal_reglas_id
            ''', (servidor_id, canal_id))
            await conexion.commit()

    async def guardar_canal_verificacion(self, servidor_id: str, canal_id: str):
        """Guarda o actualiza el canal de verificación para un servidor."""
        async with aiosqlite.connect(self.ruta) as conexion:
            await conexion.execute('''
                INSERT INTO configuracion_servidor (servidor_id, canal_verificacion_id)
                VALUES (?, ?)
                ON CONFLICT(servidor_id) DO UPDATE SET canal_verificacion_id = excluded.canal_verificacion_id
            ''', (servidor_id, canal_id))
            await conexion.commit()

    async def guardar_canal_confesiones(self, servidor_id: str, canal_id: str):
        """Guarda o actualiza el canal de confesiones anónimas."""
        async with aiosqlite.connect(self.ruta) as conexion:
            await conexion.execute('''
                INSERT INTO configuracion_servidor (servidor_id, canal_confesiones_id)
                VALUES (?, ?)
                ON CONFLICT(servidor_id) DO UPDATE SET canal_confesiones_id = excluded.canal_confesiones_id
            ''', (servidor_id, canal_id))
            await conexion.commit()

    async def guardar_canal_cumpleanos(self, servidor_id: str, canal_id: str):
        """Guarda o actualiza el canal de cumpleaños."""
        async with aiosqlite.connect(self.ruta) as conexion:
            await conexion.execute('''
                INSERT INTO configuracion_servidor (servidor_id, canal_cumpleanos_id)
                VALUES (?, ?)
                ON CONFLICT(servidor_id) DO UPDATE SET canal_cumpleanos_id = excluded.canal_cumpleanos_id
            ''', (servidor_id, canal_id))
            await conexion.commit()

    async def guardar_canal_logs(self, servidor_id: str, canal_id: str):
        """Guarda o actualiza el canal de logs avanzados."""
        async with aiosqlite.connect(self.ruta) as conexion:
            await conexion.execute('''
                INSERT INTO configuracion_servidor (servidor_id, canal_logs_id)
                VALUES (?, ?)
                ON CONFLICT(servidor_id) DO UPDATE SET canal_logs_id = excluded.canal_logs_id
            ''', (servidor_id, canal_id))
            await conexion.commit()

    async def guardar_antispam(self, servidor_id: str, activado: int, config_json: str = None):
        """Guarda o actualiza la configuración anti-spam."""
        async with aiosqlite.connect(self.ruta) as conexion:
            if config_json:
                await conexion.execute('''
                    INSERT INTO configuracion_servidor (servidor_id, antispam_activado, antispam_config)
                    VALUES (?, ?, ?)
                    ON CONFLICT(servidor_id) DO UPDATE SET 
                        antispam_activado = excluded.antispam_activado,
                        antispam_config = excluded.antispam_config
                ''', (servidor_id, activado, config_json))
            else:
                await conexion.execute('''
                    INSERT INTO configuracion_servidor (servidor_id, antispam_activado)
                    VALUES (?, ?)
                    ON CONFLICT(servidor_id) DO UPDATE SET antispam_activado = excluded.antispam_activado
                ''', (servidor_id, activado))
            await conexion.commit()

    # ─── Métodos de Reglas por Servidor ───────────────────────────────

    async def obtener_reglas(self, servidor_id: str) -> list:
        """Obtiene todas las reglas de un servidor, ordenadas por número."""
        async with aiosqlite.connect(self.ruta) as conexion:
            async with conexion.execute('''
                SELECT numero, titulo, contenido FROM reglas
                WHERE servidor_id = ?
                ORDER BY numero ASC
            ''', (servidor_id,)) as cursor:
                return await cursor.fetchall()

    async def obtener_regla(self, servidor_id: str, numero: int):
        """Obtiene una regla específica por su número."""
        async with aiosqlite.connect(self.ruta) as conexion:
            async with conexion.execute('''
                SELECT numero, titulo, contenido FROM reglas
                WHERE servidor_id = ? AND numero = ?
            ''', (servidor_id, numero)) as cursor:
                return await cursor.fetchone()

    async def agregar_regla(self, servidor_id: str, titulo: str, contenido: str) -> int:
        """Agrega una nueva regla al servidor. Devuelve el número asignado."""
        async with aiosqlite.connect(self.ruta) as conexion:
            # Obtener el siguiente número disponible
            async with conexion.execute('''
                SELECT COALESCE(MAX(numero), 0) + 1 FROM reglas
                WHERE servidor_id = ?
            ''', (servidor_id,)) as cursor:
                resultado = await cursor.fetchone()
                nuevo_numero = resultado[0]

            await conexion.execute('''
                INSERT INTO reglas (servidor_id, numero, titulo, contenido)
                VALUES (?, ?, ?, ?)
            ''', (servidor_id, nuevo_numero, titulo, contenido))
            await conexion.commit()
            return nuevo_numero

    async def editar_regla(self, servidor_id: str, numero: int, titulo: str, contenido: str) -> bool:
        """Edita una regla existente. Devuelve True si se encontró y editó."""
        async with aiosqlite.connect(self.ruta) as conexion:
            cursor = await conexion.execute('''
                UPDATE reglas SET titulo = ?, contenido = ?
                WHERE servidor_id = ? AND numero = ?
            ''', (titulo, contenido, servidor_id, numero))
            await conexion.commit()
            return cursor.rowcount > 0

    async def eliminar_regla(self, servidor_id: str, numero: int) -> bool:
        """Elimina una regla y renumera las restantes. Devuelve True si existía."""
        async with aiosqlite.connect(self.ruta) as conexion:
            # Verificar que la regla existe
            async with conexion.execute('''
                SELECT id FROM reglas WHERE servidor_id = ? AND numero = ?
            ''', (servidor_id, numero)) as cursor:
                if not await cursor.fetchone():
                    return False

            # Eliminar la regla
            await conexion.execute('''
                DELETE FROM reglas WHERE servidor_id = ? AND numero = ?
            ''', (servidor_id, numero))

            # Renumerar las reglas restantes para que no queden huecos
            await conexion.execute('''
                UPDATE reglas SET numero = numero - 1
                WHERE servidor_id = ? AND numero > ?
            ''', (servidor_id, numero))

            await conexion.commit()
            return True

    # ─── Métodos de Sorteos ───────────────────────────────────────────

    async def crear_sorteo(self, servidor_id: str, canal_id: str, mensaje_id: str,
                           premio: str, organizador_id: str, fecha_fin: float,
                           ganadores_count: int = 1):
        """Crea un nuevo sorteo activo."""
        async with aiosqlite.connect(self.ruta) as conexion:
            await conexion.execute('''
                INSERT INTO sorteos (servidor_id, canal_id, mensaje_id, premio,
                                     organizador_id, fecha_fin, ganadores_count)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (servidor_id, canal_id, mensaje_id, premio,
                  organizador_id, fecha_fin, ganadores_count))
            await conexion.commit()

    async def obtener_sorteos_activos(self) -> list:
        """Obtiene todos los sorteos que aún no han finalizado."""
        async with aiosqlite.connect(self.ruta) as conexion:
            async with conexion.execute('''
                SELECT id, servidor_id, canal_id, mensaje_id, premio,
                       organizador_id, fecha_fin, ganadores_count
                FROM sorteos WHERE finalizado = 0
            ''') as cursor:
                return await cursor.fetchall()

    async def finalizar_sorteo(self, sorteo_id: int):
        """Marca un sorteo como finalizado."""
        async with aiosqlite.connect(self.ruta) as conexion:
            await conexion.execute('''
                UPDATE sorteos SET finalizado = 1 WHERE id = ?
            ''', (sorteo_id,))
            await conexion.commit()

    async def obtener_sorteo_por_mensaje(self, mensaje_id: str):
        """Obtiene un sorteo por su ID de mensaje."""
        async with aiosqlite.connect(self.ruta) as conexion:
            async with conexion.execute('''
                SELECT id, servidor_id, canal_id, mensaje_id, premio,
                       organizador_id, fecha_fin, ganadores_count
                FROM sorteos WHERE mensaje_id = ?
            ''', (mensaje_id,)) as cursor:
                return await cursor.fetchone()

    # ─── Métodos de Recordatorios ─────────────────────────────────────

    async def crear_recordatorio(self, usuario_id: str, servidor_id: str,
                                  canal_id: str, mensaje: str, fecha_recordar: float):
        """Crea un nuevo recordatorio."""
        async with aiosqlite.connect(self.ruta) as conexion:
            await conexion.execute('''
                INSERT INTO recordatorios (usuario_id, servidor_id, canal_id, mensaje, fecha_recordar)
                VALUES (?, ?, ?, ?, ?)
            ''', (usuario_id, servidor_id, canal_id, mensaje, fecha_recordar))
            await conexion.commit()

    async def obtener_recordatorios_pendientes(self, tiempo_actual: float) -> list:
        """Obtiene los recordatorios que ya deben activarse."""
        async with aiosqlite.connect(self.ruta) as conexion:
            async with conexion.execute('''
                SELECT id, usuario_id, servidor_id, canal_id, mensaje, fecha_recordar
                FROM recordatorios
                WHERE completado = 0 AND fecha_recordar <= ?
            ''', (tiempo_actual,)) as cursor:
                return await cursor.fetchall()

    async def completar_recordatorio(self, recordatorio_id: int):
        """Marca un recordatorio como completado."""
        async with aiosqlite.connect(self.ruta) as conexion:
            await conexion.execute('''
                UPDATE recordatorios SET completado = 1 WHERE id = ?
            ''', (recordatorio_id,))
            await conexion.commit()

    # ─── Métodos de Cumpleaños ────────────────────────────────────────

    async def registrar_cumpleanos(self, servidor_id: str, usuario_id: str, dia: int, mes: int):
        """Registra o actualiza la fecha de cumpleaños de un usuario."""
        async with aiosqlite.connect(self.ruta) as conexion:
            await conexion.execute('''
                INSERT INTO cumpleanos (servidor_id, usuario_id, dia, mes)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(servidor_id, usuario_id) DO UPDATE SET dia = excluded.dia, mes = excluded.mes
            ''', (servidor_id, usuario_id, dia, mes))
            await conexion.commit()

    async def obtener_cumpleanos_hoy(self, dia: int, mes: int) -> list:
        """Obtiene todos los cumpleaños que coinciden con el día y mes dados."""
        async with aiosqlite.connect(self.ruta) as conexion:
            async with conexion.execute('''
                SELECT servidor_id, usuario_id FROM cumpleanos
                WHERE dia = ? AND mes = ?
            ''', (dia, mes)) as cursor:
                return await cursor.fetchall()

    async def obtener_cumpleanos_usuario(self, servidor_id: str, usuario_id: str):
        """Obtiene la fecha de cumpleaños de un usuario."""
        async with aiosqlite.connect(self.ruta) as conexion:
            async with conexion.execute('''
                SELECT dia, mes FROM cumpleanos
                WHERE servidor_id = ? AND usuario_id = ?
            ''', (servidor_id, usuario_id)) as cursor:
                return await cursor.fetchone()

    async def obtener_cumpleanos_servidor(self, servidor_id: str) -> list:
        """Obtiene todos los cumpleaños registrados de un servidor."""
        async with aiosqlite.connect(self.ruta) as conexion:
            async with conexion.execute('''
                SELECT usuario_id, dia, mes FROM cumpleanos
                WHERE servidor_id = ?
                ORDER BY mes ASC, dia ASC
            ''', (servidor_id,)) as cursor:
                return await cursor.fetchall()

    # ─── Métodos de Logros ────────────────────────────────────────────

    async def otorgar_logro(self, servidor_id: str, usuario_id: str, logro_id: str) -> bool:
        """Otorga un logro a un usuario. Devuelve True si es nuevo (no duplicado)."""
        async with aiosqlite.connect(self.ruta) as conexion:
            try:
                await conexion.execute('''
                    INSERT INTO logros_usuarios (servidor_id, usuario_id, logro_id)
                    VALUES (?, ?, ?)
                ''', (servidor_id, usuario_id, logro_id))
                await conexion.commit()
                return True
            except aiosqlite.IntegrityError:
                return False  # Ya tiene este logro

    async def obtener_logros_usuario(self, servidor_id: str, usuario_id: str) -> list:
        """Obtiene todos los logros de un usuario en un servidor."""
        async with aiosqlite.connect(self.ruta) as conexion:
            async with conexion.execute('''
                SELECT logro_id, fecha FROM logros_usuarios
                WHERE servidor_id = ? AND usuario_id = ?
                ORDER BY fecha ASC
            ''', (servidor_id, usuario_id)) as cursor:
                return await cursor.fetchall()

    async def tiene_logro(self, servidor_id: str, usuario_id: str, logro_id: str) -> bool:
        """Verifica si un usuario ya tiene un logro específico."""
        async with aiosqlite.connect(self.ruta) as conexion:
            async with conexion.execute('''
                SELECT 1 FROM logros_usuarios
                WHERE servidor_id = ? AND usuario_id = ? AND logro_id = ?
            ''', (servidor_id, usuario_id, logro_id)) as cursor:
                return await cursor.fetchone() is not None

# Instancia global para importar fácilmente en los cogs
db = GestorBaseDatos()