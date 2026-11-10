# 📖 Documentación Completa — Bot Norah

> Bot personal de Discord desarrollado por BinNorah.
> Prefijo: `.` | Slash Commands: `/` | Todos los comandos son híbridos (funcionan con ambos).

---

## 📑 Índice

1. [⚙️ Configuración](#️-configuración)
2. [🛡️ Moderación](#️-moderación)
3. [📜 Reglas](#-reglas)
4. [⭐ Niveles y Experiencia](#-niveles-y-experiencia)
5. [ℹ️ Básico](#️-básico)
6. [🎲 Diversión](#-diversión)
7. [📢 Anuncios](#-anuncios)
8. [🎁 Sorteos (Giveaways)](#-sorteos-giveaways)
9. [⏰ Recordatorios](#-recordatorios)
10. [📈 Estadísticas del Servidor](#-estadísticas-del-servidor)
11. [🔇 Anti-Spam / Automod](#-anti-spam--automod)
12. [📋 Logs Avanzados](#-logs-avanzados)
13. [🖼️ Tarjeta de Bienvenida](#️-tarjeta-de-bienvenida)
14. [✅ Verificación](#-verificación)
15. [🐱 Imágenes de Animales](#-imágenes-de-animales)
16. [🧮 Encuestas](#-encuestas)
17. [💬 Confesiones Anónimas](#-confesiones-anónimas)
18. [🎂 Sistema de Cumpleaños](#-sistema-de-cumpleaños)
19. [🏆 Sistema de Logros](#-sistema-de-logros)
20. [📢 Bienvenidas y Despedidas](#-bienvenidas-y-despedidas)

---

## ⚙️ Configuración

> Comandos para configurar los canales, roles y funcionalidades del bot en cada servidor.
> **Permiso requerido:** Administrador

| Comando | Descripción | Ejemplo |
|---------|-------------|---------|
| `/configurar_bienvenida` | Establece el canal de bienvenidas y despedidas | `/configurar_bienvenida #bienvenidas` |
| `/configurar_modlog` | Establece el canal de logs de moderación | `/configurar_modlog #mod-logs` |
| `/configurar_rol_miembro` | Establece el rol que se da al verificarse | `/configurar_rol_miembro @Miembro` |
| `/configurar_recompensa` | Asigna un rol como recompensa por alcanzar un nivel | `/configurar_recompensa 10 @Nivel10` |
| `/configurar_reglas` | Establece el canal donde se publican las reglas | `/configurar_reglas #reglas` |
| `/configurar_verificacion` | Establece el canal del panel de verificación | `/configurar_verificacion #verificacion` |
| `/configurar_logs` | Establece el canal de logs avanzados | `/configurar_logs #logs` |
| `/configurar_confesiones` | Establece el canal de confesiones anónimas | `/configurar_confesiones #confesiones` |
| `/configurar_cumpleaños` | Establece el canal de felicitaciones de cumpleaños | `/configurar_cumpleaños #cumpleaños` |
| `/ver_configuracion` | Muestra toda la configuración actual del servidor | `/ver_configuracion` |

### Detalles de `/configurar_recompensa`

| Parámetro | Tipo | Requerido | Descripción |
|-----------|------|-----------|-------------|
| `nivel` | Entero | ✅ | Nivel mínimo para obtener el rol (≥ 1) |
| `rol` | Rol | ✅ | El rol que se otorgará al alcanzar ese nivel |

### Detalles de `/ver_configuracion`

Muestra en un embed todos los ajustes actuales del servidor:
- 📢 Canal de Bienvenida
- 📋 Canal de Modlog
- 📜 Canal de Reglas
- ✅ Canal de Verificación
- 📝 Canal de Logs Avanzados
- 🤫 Canal de Confesiones
- 🎂 Canal de Cumpleaños
- 🛡️ Rol de Verificación
- 🔇 Estado del Anti-Spam
- 🎖️ Recompensas por Nivel
- 📝 Cantidad de Reglas

---

## 🛡️ Moderación

> Comandos para administrar y moderar el servidor.
> Los moderadores no pueden actuar sobre miembros con roles iguales o superiores.

| Comando | Permiso | Descripción | Ejemplo |
|---------|---------|-------------|---------|
| `/kick` | Expulsar miembros | Expulsa a un miembro del servidor | `/kick @usuario Spam` |
| `/ban` | Banear miembros | Banea permanentemente a un miembro | `/ban @usuario Toxicidad` |
| `/unban` | Banear miembros | Remueve el ban de un usuario por ID o nombre | `/unban 123456789` |
| `/mute` | Moderar miembros | Silencia temporalmente a un miembro (timeout) | `/mute @usuario 30 Flood` |
| `/unmute` | Moderar miembros | Quita el silencio a un miembro | `/unmute @usuario` |
| `/clear` | Gestionar mensajes | Elimina una cantidad de mensajes del canal | `/clear 20` |
| `/warn` | Expulsar miembros | Registra una advertencia formal en la base de datos | `/warn @usuario Lenguaje inapropiado` |
| `/historial` | Moderar miembros | Muestra el historial de advertencias de un usuario | `/historial @usuario` |

### Detalles de `/kick`

| Parámetro | Tipo | Requerido | Descripción |
|-----------|------|-----------|-------------|
| `miembro` | Miembro | ✅ | El usuario a expulsar |
| `razon` | Texto | ❌ | Motivo de la expulsión (por defecto: "No especificada") |

### Detalles de `/ban`

| Parámetro | Tipo | Requerido | Descripción |
|-----------|------|-----------|-------------|
| `miembro` | Miembro | ✅ | El usuario a banear |
| `razon` | Texto | ❌ | Motivo del baneo (por defecto: "No especificada") |

### Detalles de `/mute`

| Parámetro | Tipo | Requerido | Descripción |
|-----------|------|-----------|-------------|
| `miembro` | Miembro | ✅ | El usuario a silenciar |
| `minutos` | Entero | ✅ | Duración del silencio en minutos (> 0) |
| `razon` | Texto | ❌ | Motivo del silencio (por defecto: "No especificada") |

### Detalles de `/clear`

| Parámetro | Tipo | Requerido | Descripción |
|-----------|------|-----------|-------------|
| `cantidad` | Entero | ❌ | Cantidad de mensajes a eliminar (1–100, por defecto: 5) |

### Detalles de `/warn`

| Parámetro | Tipo | Requerido | Descripción |
|-----------|------|-----------|-------------|
| `miembro` | Miembro | ✅ | El usuario a advertir |
| `razon` | Texto | ❌ | Motivo de la advertencia |

> **Nota:** Las advertencias se almacenan permanentemente en la base de datos. El usuario recibe un DM con la notificación (si tiene DMs abiertos). Todas las acciones de moderación se registran en el canal de modlog si está configurado.

---

## 📜 Reglas

> Sistema de reglas por servidor almacenadas en la base de datos.
> **Permiso requerido:** Administrador (excepto `/ver_reglas` que necesita Gestionar mensajes)

| Comando | Descripción | Ejemplo |
|---------|-------------|---------|
| `/agregar_regla` | Agrega una nueva regla al servidor | `/agregar_regla "Respeto mutuo" "Trata a todos con respeto..."` |
| `/eliminar_regla` | Elimina una regla por número (renumera automáticamente) | `/eliminar_regla 3` |
| `/editar_regla` | Edita el título y contenido de una regla existente | `/editar_regla 1 "Nuevo título" "Nuevo contenido"` |
| `/ver_reglas` | Previsualización de reglas para admins (efímero) | `/ver_reglas` |
| `/publicar_reglas` | Publica todas las reglas en el canal configurado | `/publicar_reglas` |

### Detalles de `/agregar_regla`

| Parámetro | Tipo | Requerido | Descripción |
|-----------|------|-----------|-------------|
| `titulo` | Texto | ✅ | Título corto de la regla |
| `contenido` | Texto | ✅ | Descripción completa de la regla |

### Placeholders en reglas

Al publicar reglas con `/publicar_reglas`, puedes usar estos placeholders en el contenido:
- `{Moderador}` → Se reemplaza por la mención del rol "Moderador"
- `{Administrador}` → Se reemplaza por la mención del rol "Administrador"

---

## ⭐ Niveles y Experiencia

> Sistema automático de experiencia, niveles y perfiles de usuario.

| Comando | Descripción | Ejemplo |
|---------|-------------|---------|
| `/perfil` | Muestra tu tarjeta de perfil con nivel, XP y monedas | `/perfil` o `/perfil @usuario` |

### ¿Cómo funciona?

- Cada mensaje que envías otorga **15–25 XP aleatorios**
- Hay un **enfriamiento de 60 segundos** entre ganancia de XP (anti-spam)
- La fórmula de XP para subir de nivel: `5 × nivel² + 50 × nivel + 100`
- Al subir de nivel, recibes una notificación en el canal
- Si hay roles de recompensa configurados, se asignan automáticamente

### Detalles de `/perfil`

| Parámetro | Tipo | Requerido | Descripción |
|-----------|------|-----------|-------------|
| `miembro` | Miembro | ❌ | Usuario del que ver el perfil (por defecto: tú mismo) |

**El perfil muestra:**
- Nivel actual
- Barra de progreso visual (🟩⬛)
- XP actual / XP necesaria
- Monedas acumuladas

---

## ℹ️ Básico

> Comandos generales de información y utilidad.

| Comando | Descripción | Ejemplo |
|---------|-------------|---------|
| `/ping` | Muestra la latencia actual del bot en milisegundos | `/ping` |
| `/uptime` | Muestra el tiempo transcurrido desde que el bot inició sesión | `/uptime` |
| `/info` | Información general sobre el bot (servidores, usuarios, actividad) | `/info` |
| `/avatar` | Muestra el avatar de un usuario en tamaño completo | `/avatar @usuario` |
| `/perfil` | Muestra la tarjeta de perfil, antigüedad y roles de un usuario | `/perfil @usuario` |
| `/limpiar_dm` | Elimina los mensajes que el bot te haya enviado a tus mensajes directos (DM) | `/limpiar_dm` |

### Detalles de `/avatar`

| Parámetro | Tipo | Requerido | Descripción |
|-----------|------|-----------|-------------|
| `usuario` | Miembro | ❌ | Usuario del que ver el avatar (por defecto: tú mismo) |

---

## 🎲 Diversión

> Minijuegos y comandos de entretenimiento.

| Comando | Descripción | Ejemplo |
|---------|-------------|---------|
| `/moneda` | Lanza una moneda (Cara o Cruz) | `/moneda` |
| `/dado` | Lanza un dado virtual con las caras que quieras | `/dado 20` |
| `/8ball` | La bola 8 responde aleatoriamente a tus preguntas | `/8ball ¿Aprobaré el examen?` |

### Detalles de `/dado`

| Parámetro | Tipo | Requerido | Descripción |
|-----------|------|-----------|-------------|
| `caras` | Entero | ❌ | Número de caras del dado (mínimo 2, por defecto: 6) |

### Detalles de `/8ball`

| Parámetro | Tipo | Requerido | Descripción |
|-----------|------|-----------|-------------|
| `pregunta` | Texto | ✅ | La pregunta que quieres hacerle a la bola 8 |

---

## 📢 Anuncios

> Sistema de anuncios profesionales con embeds dorados.
> **Permiso requerido:** Administrador

| Comando | Descripción | Ejemplo |
|---------|-------------|---------|
| `/anuncio` | Publica un anuncio con embed profesional mencionando a la comunidad | `/anuncio "Evento" "¡Este sábado hay evento a las 8 PM!"` |

### Detalles de `/anuncio`

| Parámetro | Tipo | Requerido | Descripción |
|-----------|------|-----------|-------------|
| `titulo` | Texto | ✅ | Título del anuncio |
| `contenido` | Texto | ✅ | Contenido y mensaje del anuncio |

*Se publica automáticamente en el canal configurado con `/configurar_anuncios` (o en el canal actual), mencionando a todos los roles inferiores a Admin o Mod.*

**El embed incluye:**
- Título con emoji 📢
- Contenido del mensaje
- Thumbnail del icono del servidor
- Footer con el nombre y avatar del autor
- Timestamp automático
- Mención del rol (si se especifica)

---

## 🎁 Sorteos (Giveaways)

> Sistema completo de sorteos con reacciones, selección automática de ganadores y persistencia en base de datos.
> **Permiso requerido:** Gestionar servidor

| Comando | Descripción | Ejemplo |
|---------|-------------|---------|
| `/sorteo` | Crea un nuevo sorteo con temporizador | `/sorteo 2h Nitro` |
| `/re_sorteo` | Repite un sorteo con nuevos ganadores aleatorios | `/re_sorteo 123456789012345678` |

### Detalles de `/sorteo`

| Parámetro | Tipo | Requerido | Descripción |
|-----------|------|-----------|-------------|
| `duracion` | Texto | ✅ | Duración del sorteo |
| `premio` | Texto | ✅ | Lo que se sortea |
| `ganadores` | Entero | ❌ | Cantidad de ganadores (1–20, por defecto: 1) |

**Formatos de duración válidos:**
| Formato | Significado |
|---------|-------------|
| `30s` | 30 segundos |
| `10m` | 10 minutos |
| `2h` | 2 horas |
| `1d` | 1 día |

### ¿Cómo funciona?

1. El bot crea un embed con la información del sorteo
2. Agrega una reacción 🎉 al mensaje
3. Los usuarios reaccionan con 🎉 para participar
4. Un **task loop** revisa cada 30 segundos si algún sorteo ha terminado
5. Al finalizar, selecciona ganadores aleatorios y los menciona
6. El mensaje original se edita para mostrar que terminó
7. Los sorteos **persisten entre reinicios** del bot (almacenados en BD)

### Detalles de `/re_sorteo`

| Parámetro | Tipo | Requerido | Descripción |
|-----------|------|-----------|-------------|
| `mensaje_id` | Texto | ✅ | ID del mensaje del sorteo original |

---

## ⏰ Recordatorios

> Sistema de recordatorios personales que se envían por DM.

| Comando | Descripción | Ejemplo |
|---------|-------------|---------|
| `/recordar` | Programa un recordatorio personal | `/recordar 2h Revisar el servidor` |

### Detalles de `/recordar`

| Parámetro | Tipo | Requerido | Descripción |
|-----------|------|-----------|-------------|
| `tiempo` | Texto | ✅ | Cuándo recordarte |
| `mensaje` | Texto | ✅ | Qué quieres que te recuerde |

**Formatos de tiempo válidos:**
| Formato | Significado |
|---------|-------------|
| `30s` | 30 segundos |
| `10m` | 10 minutos |
| `2h` | 2 horas |
| `1d` | 1 día |
| `1h30m` | 1 hora y 30 minutos (combinado) |
| `2d12h` | 2 días y 12 horas (combinado) |

> **Tiempo máximo:** 30 días

### ¿Cómo funciona?

1. El recordatorio se guarda en la base de datos
2. Un **task loop** revisa cada 30 segundos los recordatorios pendientes
3. Cuando llega la hora, el bot te envía un **DM** con el mensaje
4. Si tienes los DMs cerrados, te menciona en el canal original como fallback
5. Los recordatorios **sobreviven reinicios** del bot

---

## 📈 Estadísticas del Servidor

> Muestra información completa y detallada del servidor.

| Comando | Descripción | Ejemplo |
|---------|-------------|---------|
| `/stats` | Muestra todas las estadísticas del servidor | `/stats` |

### Información que muestra:

| Sección | Datos |
|---------|-------|
| 👥 **Miembros** | Total, humanos, bots, en línea |
| 💬 **Canales** | Texto, voz, categorías, foros |
| 🏷️ **Servidor** | Roles, emojis, stickers, nivel de verificación |
| 💎 **Boosts** | Nivel (con barra visual), cantidad de boosts, boosters |
| 📅 **Información** | Dueño, fecha de creación (con timestamps de Discord), antigüedad |
| 🔑 **ID** | ID numérico del servidor |

---

## 🔇 Anti-Spam / Automod

> Sistema automático de detección y eliminación de spam.
> **Permiso requerido para configurar:** Administrador
> **Exento de detección:** Usuarios con permiso "Gestionar mensajes"

| Comando | Descripción | Ejemplo |
|---------|-------------|---------|
| `/antispam activar` | Activa el sistema anti-spam | `/antispam activar` |
| `/antispam desactivar` | Desactiva el sistema anti-spam | `/antispam desactivar` |

### Filtros de detección

| Filtro | Condición | Acción |
|--------|-----------|--------|
| 🚫 **Flood** | 5+ mensajes en 5 segundos | Eliminar + advertencia |
| 🔗 **Links no permitidos** | URLs fuera de la whitelist | Eliminar + advertencia |
| 🔁 **Texto repetido** | 3+ mensajes idénticos consecutivos | Eliminar + advertencia |
| 📢 **Menciones masivas** | 5+ menciones en un solo mensaje | Eliminar + advertencia |

### Sistema de strikes

| Strike | Acción |
|--------|--------|
| 1/3 | Mensaje eliminado + advertencia visible (se borra en 8s) |
| 2/3 | Mensaje eliminado + advertencia visible |
| 3/3 | **Mute automático de 10 minutos** + notificación |

### Whitelist de links por defecto

Los siguientes dominios están permitidos por defecto:
`discord.gg`, `discord.com`, `tenor.com`, `giphy.com`, `youtube.com`, `youtu.be`, `twitch.tv`, `twitter.com`, `x.com`, `instagram.com`, `reddit.com`, `github.com`, `spotify.com`

### Funcionamiento interno

- Cache en memoria para rendimiento (no consulta la BD por cada mensaje)
- Cache de configuración con expiración de 60 segundos
- Todas las infracciones se registran en el canal de **modlog** si está configurado

---

## 📋 Logs Avanzados

> Sistema de registro automático de eventos del servidor.
> **Permiso requerido para configurar:** Administrador

| Comando | Descripción | Ejemplo |
|---------|-------------|---------|
| `/configurar_logs` | Establece el canal para los logs avanzados | `/configurar_logs #logs` |

### Eventos registrados

| Evento | Emoji | Color | Información registrada |
|--------|-------|-------|----------------------|
| Mensaje editado | ✏️ | 🔵 Azul | Autor, canal, contenido antes/después |
| Mensaje eliminado | 🗑️ | 🔴 Rojo | Autor, canal, contenido, archivos adjuntos |
| Cambio de apodo | 📝 | 🟡 Amarillo | Usuario, apodo anterior/nuevo |
| Cambio de roles | 🏷️ | 🟣 Morado | Usuario, roles agregados/removidos |
| Entrada a canal de voz | 🔊 | 🟢 Verde | Usuario, canal al que se unió |
| Salida de canal de voz | 🔇 | ⚪ Gris | Usuario, canal que dejó |
| Cambio de canal de voz | 🔀 | 🟢 Verde | Usuario, canal origen/destino |
| Usuario baneado | 🔨 | 🔴 Rojo | Usuario baneado, avatar, ID |
| Usuario desbaneado | 🔓 | 🟢 Verde | Usuario desbaneado, ID |

> **Nota:** Los mensajes de bots son ignorados automáticamente para evitar spam de logs.

---

## 🖼️ Tarjeta de Bienvenida

> Sistema automático — no requiere comandos.

### ¿Cómo funciona?

Cuando un miembro se une al servidor (y el canal de bienvenida está configurado), el bot genera automáticamente una **imagen personalizada** que incluye:

| Elemento | Detalle |
|----------|---------|
| **Fondo** | Gradiente oscuro elegante (tonos morados) |
| **Línea superior** | Gradiente rosa a morado decorativo |
| **Avatar** | Circular con borde rosa, 130×130px |
| **Título** | "¡Bienvenido/a!" en blanco |
| **Nombre** | Nombre del usuario en rosa |
| **Subtexto** | "Eres el miembro #N" |
| **Servidor** | "en [nombre del servidor]" |
| **Partículas** | 30 puntos decorativos aleatorios |

**Dimensiones de la tarjeta:** 900 × 300 píxeles

### Requisitos

- **Pillow** debe estar instalado (`pip install Pillow`)
- Si Pillow no está disponible, se usa el **modo fallback** (GIF + embed original)
- Si no hay GIF disponible, se envía solo el embed de texto

---

## ✅ Verificación

> Sistema de verificación por botón para desbloquear el acceso al servidor.
> **Permiso requerido:** Administrador

| Comando | Descripción | Ejemplo |
|---------|-------------|---------|
| `/enviarverificacion` | Publica el panel de verificación | `/enviarverificacion` |
| `/verificar_todos` | Asigna el rol de verificación masivamente a todos los miembros que aún no lo tengan | `/verificar_todos` |

### ¿Cómo funciona?

1. Un admin ejecuta `/enviarverificacion`
2. El bot publica un embed con un botón verde "✅ Verificarme"
3. Los nuevos miembros presionan el botón
4. El bot les asigna el rol configurado con `/configurar_rol_miembro`
5. El botón es **persistente** (sobrevive reinicios del bot)

---

## 🐱 Imágenes de Animales

> Imágenes aleatorias de animales usando APIs gratuitas.

| Comando | API utilizada | Descripción |
|---------|---------------|-------------|
| `/gato` | TheCatAPI | Envía una imagen aleatoria de un gato 🐱 |
| `/perro` | Dog CEO API | Envía una imagen aleatoria de un perro 🐶 |
| `/zorro` | RandomFox | Envía una imagen aleatoria de un zorro 🦊 |

> **Timeout:** Las peticiones tienen un timeout de 10 segundos. Si la API no responde, muestra un mensaje de error amigable.

---

## 🧮 Encuestas

> Sistema de encuestas con reacciones automáticas.

| Comando | Descripción | Ejemplo |
|---------|-------------|---------|
| `/encuesta` | Crea una encuesta con hasta 10 opciones | `/encuesta "¿Mejor día?" "Lunes" "Viernes" "Sábado"` |
| `/encuesta_si_no` | Crea una encuesta rápida de Sí/No | `/encuesta_si_no ¿Hacemos evento este finde?` |

### Detalles de `/encuesta`

| Parámetro | Tipo | Requerido | Descripción |
|-----------|------|-----------|-------------|
| `pregunta` | Texto | ✅ | La pregunta de la encuesta |
| `opcion1` | Texto | ✅ | Primera opción |
| `opcion2` | Texto | ✅ | Segunda opción |
| `opcion3` a `opcion10` | Texto | ❌ | Opciones adicionales (hasta 10 total) |

**Emojis de opciones:** 1️⃣ 2️⃣ 3️⃣ 4️⃣ 5️⃣ 6️⃣ 7️⃣ 8️⃣ 9️⃣ 🔟

---

## 💬 Confesiones Anónimas

> Sistema de mensajes anónimos hacia un canal dedicado.

| Comando | Permiso | Descripción | Ejemplo |
|---------|---------|-------------|---------|
| `/confesar` | Ninguno | Envía una confesión anónima | `/confesar Creo que las pizzas con piña son buenas` |
| `/configurar_confesiones` | Administrador | Configura el canal de confesiones | `/configurar_confesiones #confesiones` |

### Detalles de `/confesar`

| Parámetro | Tipo | Requerido | Descripción |
|-----------|------|-----------|-------------|
| `mensaje` | Texto | ✅ | Tu confesión anónima |

### ¿Cómo funciona?

1. El usuario ejecuta `/confesar` (slash command = automáticamente efímero)
2. Si usó prefijo (`.confesar`), el bot **elimina el mensaje original** para proteger el anonimato
3. El bot envía un embed anónimo numerado al canal de confesiones
4. El usuario recibe una confirmación efímera
5. **Nadie puede saber quién envió la confesión** (ni siquiera en los logs del bot)

### Diseño del embed

- Título: "🤫 Confesión #N"
- Color: Gris oscuro (0x2C2F33)
- Footer: "Confesión anónima • Usa /confesar para enviar la tuya"
- Timestamp automático

---

## 🎂 Sistema de Cumpleaños

> Registro de fechas de cumpleaños con felicitaciones automáticas diarias.

| Comando | Permiso | Descripción | Ejemplo |
|---------|---------|-------------|---------|
| `/cumpleaños` | Ninguno | Registra tu fecha de cumpleaños | `/cumpleaños 15 8` (15 de agosto) |
| `/mi_cumpleaños` | Ninguno | Consulta tu fecha registrada | `/mi_cumpleaños` |
| `/proximos_cumpleaños` | Ninguno | Lista los próximos 10 cumpleaños del servidor | `/proximos_cumpleaños` |
| `/configurar_cumpleaños` | Administrador | Configura el canal de felicitaciones | `/configurar_cumpleaños #cumpleaños` |

### Detalles de `/cumpleaños`

| Parámetro | Tipo | Requerido | Descripción |
|-----------|------|-----------|-------------|
| `dia` | Entero | ✅ | Día de tu cumpleaños (1–31) |
| `mes` | Entero | ✅ | Mes de tu cumpleaños (1–12) |

> La fecha se valida para evitar fechas imposibles (ej: 31 de febrero).

### Felicitación automática

- Un **task loop** se ejecuta todos los días a las **7:00 AM UTC**
- Revisa la base de datos buscando cumpleaños que coincidan con la fecha actual
- Envía un embed festivo con mención al cumpleañero
- **Canal de felicitación:** Se usa el canal configurado con `/configurar_cumpleaños`, o como fallback el canal de bienvenida

### `/proximos_cumpleaños`

Muestra una lista de los 10 próximos cumpleaños ordenados por proximidad:
```
🎂 NombreUsuario — 25 de Diciembre (en 140 días)
🎂 OtroUsuario — 3 de Enero (en 149 días)
🎂 CumpleHoy — 7 de Agosto (🎉 ¡HOY!)
```

---

## 🏆 Sistema de Logros

> Sistema automático de logros que se desbloquean al cumplir condiciones.

| Comando | Descripción | Ejemplo |
|---------|-------------|---------|
| `/logros` | Muestra los logros desbloqueados de un usuario | `/logros` o `/logros @usuario` |

### Detalles de `/logros`

| Parámetro | Tipo | Requerido | Descripción |
|-----------|------|-----------|-------------|
| `miembro` | Miembro | ❌ | Usuario del que ver logros (por defecto: tú mismo) |

### Lista completa de logros

| Emoji | Nombre | Condición | Tipo |
|-------|--------|-----------|------|
| 🌱 | **Primer Mensaje** | Enviar el primer mensaje | Automático |
| 💬 | **Conversador** | 100 mensajes totales | Automático |
| 🗣️ | **Parlanchín** | 500 mensajes totales | Automático |
| 📚 | **Enciclopedia Viviente** | 1,000 mensajes totales | Automático |
| ⭐ | **Nivel 5** | Alcanzar nivel 5 | Automático |
| 🌟 | **Nivel 10** | Alcanzar nivel 10 | Automático |
| 👑 | **Nivel 25** | Alcanzar nivel 25 | Automático |
| 💎 | **Nivel 50** | Alcanzar nivel 50 | Automático |
| 🎖️ | **Veterano** | 30 días en el servidor | Automático |
| 🏅 | **Leyenda** | 1 año en el servidor | Automático |
| 🦉 | **Noctámbulo** | Enviar un mensaje entre 2 AM y 5 AM (UTC) | Automático |

### ¿Cómo funciona?

- Los logros se verifican automáticamente con cada mensaje enviado
- Al desbloquear un logro **por primera vez**, el bot envía una notificación dorada en el canal
- Los logros no se pueden desbloquear dos veces (constraint UNIQUE en BD)
- El comando `/logros` muestra una barra de progreso y lista todos los logros (desbloqueados ✅ y bloqueados 🔒)

### Visualización de `/logros`

```
🏆 Logros de NombreUsuario
4/11 logros desbloqueados

Progreso: 🟨🟨🟨🟨⬛⬛⬛⬛⬛⬛ (4/11)

🌱 Primer Mensaje    ✅ Enviaste tu primer mensaje — 2026-08-01
💬 Conversador        ✅ Alcanzaste 100 mensajes — 2026-08-05
🗣️ Parlanchín         🔒 Alcanzaste 500 mensajes
📚 Enciclopedia       🔒 Alcanzaste 1,000 mensajes
⭐ Nivel 5            ✅ Alcanzaste el nivel 5 — 2026-08-03
🌟 Nivel 10           🔒 Alcanzaste el nivel 10
...
```

---

## 📢 Bienvenidas y Despedidas

> Sistema automático — no requiere comandos.
> **Requiere:** Canal de bienvenida configurado con `/configurar_bienvenida`

### Evento: Miembro se une

| Elemento | Detalle |
|----------|---------|
| **Mención** | "@usuario Bienvenido a [servidor]!" |
| **Embed** | Título: "¡Bienvenido a [servidor]!" |
| **Imagen** | Tarjeta de bienvenida generada con Pillow (o GIF fallback) |
| **Footer** | "Norah \| Miembros totales: N" |

### Evento: Miembro se va

| Elemento | Detalle |
|----------|---------|
| **Embed** | Título: "¡Hasta pronto!" |
| **Descripción** | "[nombre] ha abandonado el servidor. ¡Ojalá vuelvas pronto!" |
| **Imagen** | GIF de despedida (si existe) |
| **Footer** | "Norah \| Ahora somos N miembros" |

---

## 🗂️ Estructura de la Base de Datos

### Tablas

| Tabla | Propósito |
|-------|-----------|
| `advertencias` | Historial de warns por usuario/servidor |
| `usuarios_rpg` | XP, nivel, monedas, total de mensajes por usuario |
| `configuracion_servidor` | Todos los canales, roles y ajustes por servidor |
| `reglas` | Reglas numeradas por servidor |
| `sorteos` | Sorteos activos/finalizados |
| `recordatorios` | Recordatorios pendientes/completados |
| `cumpleanos` | Fechas de cumpleaños por usuario/servidor |
| `logros_usuarios` | Logros desbloqueados con timestamps |

---

## 📦 Dependencias

| Paquete | Versión mínima | Uso |
|---------|----------------|-----|
| `discord.py` | ≥ 2.4.0 | Framework principal del bot |
| `python-dotenv` | ≥ 1.0.0 | Variables de entorno (.env) |
| `aiosqlite` | — | Base de datos SQLite asíncrona |
| `PyNaCl` | — | Soporte de voz en Discord |
| `Pillow` | ≥ 10.0.0 | Generación de tarjetas de bienvenida |
| `aiohttp` | ≥ 3.9.0 | Peticiones HTTP (APIs de animales) |

---

## 🔧 Guía rápida de configuración inicial

```
1. /configurar_bienvenida #bienvenidas      → Activar bienvenidas/despedidas
2. /configurar_modlog #mod-logs              → Activar logs de moderación
3. /configurar_rol_miembro @Miembro          → Rol para verificación
4. /enviarverificacion                        → Publicar panel de verificación
5. /configurar_reglas #reglas                → Canal de reglas
6. /agregar_regla "Título" "Contenido"       → Agregar reglas
7. /publicar_reglas                           → Publicar reglas
8. /configurar_logs #logs                    → Activar logs avanzados
9. /antispam activar                          → Activar anti-spam
10. /configurar_confesiones #confesiones     → Canal de confesiones
11. /configurar_cumpleaños #cumpleaños       → Canal de cumpleaños
```

> Usa `/ver_configuracion` en cualquier momento para ver el estado actual de toda la configuración.
