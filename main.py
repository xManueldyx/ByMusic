import discord
import os
from discord.ext import commands
from discord.utils import get
from dotenv import load_dotenv
from pytube import YouTube
import asyncio

# Definir los permisos necesarios
PERMISSIONS = {
    'connect': True,            
    'speak': True,              
    'view_channel': True,       
    'read_message_history': True 
}

# Lista de reproducción y cola de espera
queue = []
canciones_cola = []  # Definir la lista canciones_cola globalmente

# Convertir los permisos en un objeto Permissions
permissions = discord.Permissions(**PERMISSIONS)

# Crear una instancia del cliente de Discord y configurar el prefijo del comando
intents = discord.Intents.all()
bot = commands.Bot(command_prefix='/', intents=intents)

# Mensaje de confirmación cuando el bot está listo
@bot.event
async def on_ready():
    print(f'Bot en línea: {bot.user.name}')

# Definir los comandos del bot
@bot.command()
async def command(ctx):
    response = 'Comandos:\n /command \n /join \n /stop \n /play \n /skip'
    await ctx.send(response)

@bot.command()
async def join(ctx):
    channel = ctx.author.voice.channel
    if channel:
        await channel.connect()
    else:
        await ctx.send("¡No estás en un canal de voz!")

@bot.command()
async def stop(ctx):
    await ctx.voice_client.disconnect()

# Definir la función agregar_url después de la definición de canciones_cola
def agregar_url(url):
    canciones_cola.append(url)
    #print("URL agregado correctamente.")

playing = False  # Bandera para controlar la reproducción de canciones

@bot.command()
async def play(ctx, url: str):
    if not ctx.author.voice or not ctx.author.voice.channel:
        await ctx.send("¡Debes estar en un canal de voz para reproducir música!")
        return

    voice_channel = ctx.author.voice.channel
    voice_client = get(bot.voice_clients, guild=ctx.guild)

    if not voice_client:
        voice_client = await voice_channel.connect()

    try:
        yt = YouTube(url)
        url_video = yt.streams.first().url
        agregar_url(url_video)  # Agregas la URL una vez
        yt_stream = yt.streams.filter(only_audio=True).first()
        filename = f"canciones"
        if yt:
            yt_stream.download(filename)
            #print("cancion creada con exito")
            #print("Lista de URLs almacenados:")
    except Exception as e:
        await ctx.send(f"Error al descargar el video: {e}")
        return
    print(url)
        
    agregar_url(filename)  # Agregas la canción descargada a la lista de reproducción
    if not voice_client.is_playing():
        await reproducir_canciones(ctx)
    else:
        await ctx.send("La canción se ha agregado a la cola de reproducción.")

async def reproducir_canciones(ctx):
    voice_client = get(bot.voice_clients, guild=ctx.guild)
    if voice_client.is_playing():
        await ctx.send("Ya hay una canción reproduciéndose.")
        return

    if not canciones_cola:
        return

    cancion_actual = canciones_cola.pop(0)
    voice_client.play(discord.FFmpegPCMAudio(cancion_actual), after=lambda e: asyncio.run(reproducir_canciones(ctx)))
@bot.command()
async def skip(ctx):
    voice_client = get(bot.voice_clients, guild=ctx.guild)
    if voice_client and voice_client.is_playing():
        voice_client.stop()
        await ctx.send("Skip....")
    else:
        await ctx.send("No hay ninguna canción reproduciéndose.")
# Cargar el token desde el archivo .env
load_dotenv()
bot.run(os.getenv('TOKEN'))