from configparser import MAX_INTERPOLATION_DEPTH
from discord.ext import tasks
import sqlite3
from numpy import number
import requests
import interactions
from interactions.ext.get import get
from interactions.ext.wait_for import wait_for,setup

Token = ""
bot = interactions.Client(token=Token, intents = interactions.Intents.ALL)
setup(bot)

@bot.command(
    name="weather",
    description="天気情報を定期的に通知します",
    options= [
        interactions.Option(
            type=interactions.OptionType.STRING,
            name="area", 
            description="地域設定", 
            required=True,
            choices=[
                interactions.Choice(name="北海道", value="hokkaido"), 
                interactions.Choice(name="宮城県", value="miyagi"),
                interactions.Choice(name="埼玉県", value="saitama"),
                interactions.Choice(name="千葉県", value="chiba"),
                interactions.Choice(name="新潟県", value="niigata"),
                interactions.Choice(name="静岡県", value="shizuoka"),
                interactions.Choice(name="愛知県", value="aichi"),
                interactions.Choice(name="京都府", value="kyoto"),
                interactions.Choice(name="大阪府", value="osaka"),
                interactions.Choice(name="兵庫県", value="hyogo"),
                interactions.Choice(name="岡山県", value="okayama"),
                interactions.Choice(name="広島県", value="hiroshima"),
                interactions.Choice(name="福岡県", value="fukuoka"),
                interactions.Choice(name="熊本県", value="kumamoto"),
                interactions.Choice(name="沖縄県", value="okinawa")
            ], 
        ),
    ],
)
async def weather(ctx: interactions.CommandContext, area:str):
    channel = await ctx.get_channel()
    guild = await ctx.get_guild()
    jma_url = f"http://api.openweathermap.org/data/2.5/weather?q={area}&appid=c545874eedab705e7328f2048ca7a48d&lang=ja&units=metric"
    jma_json = requests.get(jma_url).json()
    jma_weather = jma_json["weather"][0]["description"]
    jma_maxtemp = jma_json["main"]["temp_max"]
    jma_mintemp = jma_json["main"]["temp_min"]
    jma_ken = jma_json["name"]
    if ctx.author.permissions & interactions.Permissions.ADMINISTRATOR:
        try:
            conn = sqlite3.connect(f'panel.db')
            c = conn.cursor()
            c.execute('''
                CREATE TABLE panels (
                id integer primary key,
                channel integer,
                area interger
                )
            ''')
        except:
            pass
        panel_info = [{'id': str(guild.id), 'channel':str(channel.id), 'area':str(area)}]
        conn = sqlite3.connect(f'panel.db')
        c = conn.cursor()
        c.executemany(f'REPLACE INTO panels VALUES (:id, :channel, :area)', panel_info)
        conn.commit()
        conn.close

        embed=interactions.Embed(title="気象情報", color=0x1550c6)
        embed.add_field(name="天気", value=jma_weather, inline=False)
        embed.add_field(name="最高気温", value=str(jma_maxtemp), inline=True)
        embed.add_field(name="最低気温", value=str(jma_mintemp), inline=True)
        embed.add_field(name="測定地域", value=jma_ken, inline=False)
        embed.set_footer(text="情報:OpenWeather｜Produced by mepuru210")
        await ctx.send(embeds=embed)

@tasks.loop(hours=8)
async def wi():
    conn = sqlite3.connect('panel.db')
    c = conn.cursor()
    c.execute("select * from panels")
    list = c.fetchall()
    for i in list:
        jma_url = f"http://api.openweathermap.org/data/2.5/weather?q={i[2]}&appid=c545874eedab705e7328f2048ca7a48d&lang=ja&units=metric"
        jma_json = requests.get(jma_url).json()
        jma_weather = jma_json["weather"][0]["description"]
        jma_maxtemp = jma_json["main"]["temp_max"]
        jma_mintemp = jma_json["main"]["temp_min"]
        jma_ken = jma_json["name"]
        channel = await get(bot, interactions.Channel, channel_id=i[1])
        embed=interactions.Embed(title="気象情報", description=" ", color=0x1550c6)
        embed.add_field(name="天気", value=jma_weather, inline=False)
        embed.add_field(name="最高気温", value=str(jma_maxtemp), inline=True)
        embed.add_field(name="最低気温", value=str(jma_mintemp), inline=True)
        embed.add_field(name="測定地域", value=jma_ken, inline=False)
        embed.set_footer(text="情報:OpenWeather｜Produced by mepuru210")
        await channel.send(embeds=embed)
        print(channel)

@bot.event
async def on_ready():
    wi.start()
bot.start()
