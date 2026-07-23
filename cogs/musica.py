import discord
from discord.ext import commands
import wavelink

import config

class BotonMusica(discord.ui.View):
    """Panel de botones interactivos para controlar la reproducción de música."""
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Pausar", style=discord.ButtonStyle.secondary, emoji="⏸️")
    async def pausar(self, interaccion: discord.Interaction, boton: discord.ui.Button):
        reproductor: wavelink.Player = interaccion.guild.voice_client
        if not reproductor or not reproductor.playing:
            return await interaccion.response.send_message("No hay nada reproduciéndose.", ephemeral=True)

        if reproductor.paused:
            await reproductor.pause(False)
            boton.label = "Pausar"
            boton.emoji = "⏸️"
            boton.style = discord.ButtonStyle.secondary
            await interaccion.response.edit_message(view=self)
            await interaccion.followup.send("▶️ Música reanudada.", ephemeral=True)
        else:
            await reproductor.pause(True)
            boton.label = "Reanudar"
            boton.emoji = "▶️"
            boton.style = discord.ButtonStyle.success
            await interaccion.response.edit_message(view=self)
            await interaccion.followup.send("⏸️ Música pausada.", ephemeral=True)

    @discord.ui.button(label="Saltar", style=discord.ButtonStyle.primary, emoji="⏭️")
    async def saltar(self, interaccion: discord.Interaction, boton: discord.ui.Button):
        reproductor: wavelink.Player = interaccion.guild.voice_client
        if not reproductor or not reproductor.playing:
            return await interaccion.response.send_message("No hay nada que saltar.", ephemeral=True)

        await reproductor.skip(force=True)
        await interaccion.response.send_message("⏭️ Canción saltada.", ephemeral=True)

    @discord.ui.button(label="Detener", style=discord.ButtonStyle.danger, emoji="⏹️")
    async def detener(self, interaccion: discord.Interaction, boton: discord.ui.Button):
        reproductor: wavelink.Player = interaccion.guild.voice_client
        if not reproductor:
            return await interaccion.response.send_message("No estoy conectado a ningún canal.", ephemeral=True)

        reproductor.queue.clear()
        await reproductor.disconnect()
        await interaccion.message.edit(view=None)
        await interaccion.response.send_message("⏹️ Reproducción detenida y bot desconectado.", ephemeral=True)

    @discord.ui.button(label="Loop", style=discord.ButtonStyle.secondary, emoji="🔁")
    async def bucle(self, interaccion: discord.Interaction, boton: discord.ui.Button):
        reproductor: wavelink.Player = interaccion.guild.voice_client
        if not reproductor or not reproductor.playing:
            return await interaccion.response.send_message("No hay nada reproduciéndose.", ephemeral=True)

        if reproductor.queue.mode == wavelink.QueueMode.loop:
            reproductor.queue.mode = wavelink.QueueMode.normal
            boton.style = discord.ButtonStyle.secondary
            await interaccion.response.edit_message(view=self)
            await interaccion.followup.send("🔁 Bucle desactivado.", ephemeral=True)
        else:
            reproductor.queue.mode = wavelink.QueueMode.loop
            boton.style = discord.ButtonStyle.success
            await interaccion.response.edit_message(view=self)
            await interaccion.followup.send("🔁 Bucle activado para la canción actual.", ephemeral=True)

    @discord.ui.button(label="Me gusta", style=discord.ButtonStyle.secondary, emoji="❤️")
    async def megusta(self, interaccion: discord.Interaction, boton: discord.ui.Button):
        await interaccion.response.send_message(f"❤️ ¡A {interaccion.user.mention} le gusta esta canción!", ephemeral=False)


class Musica(commands.Cog):
    """Sistema de música avanzado conectado a Lavalink con Interfaz de Botones y Miniaturas."""

    def __init__(self, bot):
        self.bot = bot

    async def cog_load(self):
        nodos = [
            wavelink.Node(
                uri="http://127.0.0.1:2333", 
                password="youshallnotpass"
            )
        ]
        await wavelink.Pool.connect(nodes=nodos, client=self.bot, cache_capacity=100)

    @commands.Cog.listener()
    async def on_wavelink_node_ready(self, payload: wavelink.NodeReadyEventPayload):
        print(f"🎵 Nodo Lavalink conectado: {payload.node.identifier}")

    @commands.Cog.listener()
    async def on_wavelink_track_end(self, payload: wavelink.TrackEndEventPayload):
        reproductor = payload.player
        if not reproductor:
            return

        if not reproductor.queue.is_empty:
            siguiente_pista = reproductor.queue.get()
            await reproductor.play(siguiente_pista)

            canal = getattr(reproductor, "home", None)
            if canal:
                embed = discord.Embed(
                    title="Reproduciendo Ahora", 
                    description=f"[{siguiente_pista.title}]({siguiente_pista.uri})", 
                    color=config.COLOR_EXITO
                )
                embed.add_field(name="Autor", value=siguiente_pista.author, inline=True)
                embed.add_field(name="Duración", value=f"{int(siguiente_pista.length / 1000)}s", inline=True)
                
                # Extracción robusta de la miniatura para la versión actual del plugin
                imagen_url = getattr(siguiente_pista, "artwork", None) or getattr(siguiente_pista, "thumb", None)
                if not imagen_url and "youtube.com" in str(siguiente_pista.uri):
                    # Fallback directo a la miniatura oficial de YouTube usando el ID del video
                    import re
                    match = re.search(r'(?:v=|\/)([0-9A-Za-z_-]{11}).*', siguiente_pista.uri)
                    if match:
                        imagen_url = f"https://img.youtube.com/vi/{match.group(1)}/hqdefault.jpg"

                if imagen_url:
                    embed.set_thumbnail(url=imagen_url)
                
                vista = BotonMusica()
                await canal.send(embed=embed, view=vista)

    @commands.command(name="play", help="Reproduce una canción o la añade a la cola.")
    async def play(self, ctx, *, busqueda: str):
        if not ctx.author.voice:
            return await ctx.send("Debes estar en un canal de voz.")

        async with ctx.typing():
            if not ctx.voice_client:
                reproductor = await ctx.author.voice.channel.connect(cls=wavelink.Player)
            else:
                reproductor = ctx.voice_client

            reproductor.home = ctx.channel

            pistas = await wavelink.Playable.search(busqueda)
            if not pistas:
                return await ctx.send("No se encontraron resultados para tu búsqueda.")

            pista = pistas[0]

            if reproductor.playing:
                reproductor.queue.put(pista)
                await ctx.send(f"📋 **{pista.title}** se ha añadido a la cola en la posición #{reproductor.queue.count}.")
            else:
                await reproductor.play(pista)
                
                embed = discord.Embed(
                    title="Reproduciendo Ahora", 
                    description=f"[{pista.title}]({pista.uri})", 
                    color=config.COLOR_EXITO
                )
                embed.add_field(name="Autor", value=pista.author, inline=True)
                embed.add_field(name="Duración", value=f"{int(pista.length / 1000)}s", inline=True)
                
                # Extracción robusta de la miniatura para la versión actual del plugin
                imagen_url = getattr(pista, "artwork", None) or getattr(pista, "thumb", None)
                if not imagen_url and "youtube.com" in str(pista.uri):
                    import re
                    match = re.search(r'(?:v=|\/)([0-9A-Za-z_-]{11}).*', pista.uri)
                    if match:
                        imagen_url = f"https://img.youtube.com/vi/{match.group(1)}/hqdefault.jpg"

                if imagen_url:
                    embed.set_thumbnail(url=imagen_url)
                
                vista = BotonMusica()
                await ctx.send(embed=embed, view=vista)

    @commands.command(name="skip", help="Salta a la siguiente canción en la cola.")
    async def skip(self, ctx):
        reproductor: wavelink.Player = ctx.voice_client
        if not reproductor or not reproductor.playing:
            return await ctx.send("No hay ninguna canción reproduciéndose ahora mismo.")

        await reproductor.skip(force=True)
        await ctx.send("⏭️ Canción saltada.")

    @commands.command(name="pause", help="Pausa la canción actual.")
    async def pause(self, ctx):
        reproductor: wavelink.Player = ctx.voice_client
        if not reproductor or not reproductor.playing:
            return await ctx.send("No hay nada sonando.")

        await reproductor.pause(True)
        await ctx.send("⏸️ Música pausada.")

    @commands.command(name="resume", help="Reanuda la canción pausada.")
    async def resume(self, ctx):
        reproductor: wavelink.Player = ctx.voice_client
        if not reproductor or not reproductor.paused:
            return await ctx.send("La música no está pausada.")

        await reproductor.pause(False)
        await ctx.send("▶️ Música reanudada.")

    @commands.command(name="stop", help="Detiene la música, limpia la cola y desconecta al bot.")
    async def stop(self, ctx):
        reproductor: wavelink.Player = ctx.voice_client
        if not reproductor:
            return await ctx.send("No estoy en un canal de voz.")

        reproductor.queue.clear()
        await reproductor.disconnect()
        await ctx.send("⏹️ Música detenida. ¡Me desconecto!")

    @commands.command(name="queue", help="Muestra las canciones en la cola actual.")
    async def queue(self, ctx):
        reproductor: wavelink.Player = ctx.voice_client
        if not reproductor or ctx.voice_client is None or reproductor.queue.is_empty:
            return await ctx.send("La cola de reproducción está vacía.")

        descripcion = ""
        for indice, pista in enumerate(reproductor.queue, start=1):
            descripcion += f"**{indice}.** {pista.title}\n"
            if indice >= 10:
                descripcion += f"*... y {reproductor.queue.count - 10} más.*"
                break

        embed = discord.Embed(title="Cola de Reproducción", description=descripcion, color=config.COLOR_INFO)
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Musica(bot))