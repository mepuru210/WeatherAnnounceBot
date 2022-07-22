from discord.ext import commands, tasks
import discord
import requests
import schedule

bot = commands.Bot("/") 
bot.remove_command("help")
token = 'TOKEN'

jma_url = "https://www.jma.go.jp/bosai/forecast/data/forecast/[エリアコード].json"
jma_json = requests.get(jma_url).json()

jma_weather = jma_json[0]["timeSeries"][0]["areas"][0]["weathers"][0]
jma_wind = jma_json[0]["timeSeries"][0]["areas"][0]["winds"][0]
jma_wave = jma_json[0]["timeSeries"][0]["areas"][0]["waves"][0]
jma_weather = jma_weather.replace('　', '')
jma_wind = jma_wind.replace('　', '')
jma_wave = jma_wave.replace('　', '')

@bot.event
async def on_ready():
    print(f".start")

@bot.command()
@commands.has_permissions(administrator=True)
async def weather(ctx):
    embed=discord.Embed(title="気象予報", color=0x1550c6)
    embed.add_field(
        name="天気",
        value=jma_weather,
        inline=True
        )
    embed.add_field(
        name="風向き",
        value=jma_wind,
        inline=False
        )
    embed.add_field(
        name="波の高さ",
        value=jma_wave,
        inline=False
        )
    embed.set_footer(text="Produced by mepuru209")
    await ctx.send(embed=embed)

bot.run(token)
