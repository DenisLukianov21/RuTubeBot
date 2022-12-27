import os
import discord
from Download import Downloader
from discord.ext import commands

TOKEN = 'MTA1NzAwMTczNTY2ODg5MTczNw.GXZQ-A.xPpyaHbY0NBiWoJkHs2EoH9nn3nvwUDd0i2i5c'

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)


def delete():
    file_dir = os.listdir('Audio')
    for file in file_dir:
        os.remove(f'Audio\\{file}')


@bot.command(name='join', help='Tells the bot to join the voice channel')
async def join(ctx):
    if not ctx.message.author.voice:
        await ctx.send("{} is not connected to a voice channel".format(ctx.message.author.name))
        return
    else:
        channel = ctx.message.author.voice.channel
    await channel.connect()


@bot.command(name='leave', help='To make the bot leave the voice channel')
async def leave(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_connected():
        await voice_client.disconnect()
        delete()
    else:
        await ctx.send("The bot is not connected to a voice channel.")


@bot.command(name='play_song', help='To play song')
async def play(ctx, url):
    server = ctx.message.guild
    voice_channel = server.voice_client
    source = discord.FFmpegPCMAudio(
        source=Downloader(url).download())
    async with ctx.typing():
        voice_channel.play(source)
    await ctx.send('**Now playing:** {}'.format('test song'))


@bot.command(name='stop', help='Stops the song')
async def stop(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_playing():
        await voice_client.stop()
    else:
        await ctx.send("The bot is not playing anything at the moment.")

bot.run(TOKEN)
