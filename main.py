from nba_api.stats.endpoints import commonplayerinfo
from nba_api.live.nba.endpoints import scoreboard
from nba_api.stats.static import players
from discord.ext import commands
from dotenv import load_dotenv
from io import BytesIO
from PIL import Image
import pandas as pd
import requests
import discord
import cairosvg


ACESS_TOKEN="YOUR_TOKEN_HERE"

load_dotenv()
permissions = discord.Intents.all()

bot = commands.Bot(command_prefix='!', intents=permissions)

# HELPERS
def height_in_meters(altura_str):
    try:
        pes, polegadas = map(int, altura_str.split('-'))
        metros = (pes * 0.3048) + (polegadas * 0.0254)
        return round(metros, 2)
    except ValueError:
        return "Formato inválido. Use o formato 'PÉS-POLEGADAS'"
    
def weight_in_kg(weight):
    try:
        lbs = float(weight.strip())
        kg = lbs * 0.45359237
        return round(kg, 2)
    except ValueError:
        return "Formato inválido. Forneça o peso em libras como número"

def format_game_clock(clock: str) -> str:
    """Converte 'PT01M58.00S' para '1:58'."""
    if not clock:
        return ""
    try:
        clock = clock.replace("PT", "").replace("S", "")
        minutes, seconds = clock.split("M")
        minutes = int(minutes)
        seconds = int(float(seconds))
        return f"{minutes}:{seconds:02d}"
    except Exception:
        return clock

def merge_logos(home_id: int, away_id: int) -> discord.File | None:
    try:
        home_png = cairosvg.svg2png(url=f"https://cdn.nba.com/logos/nba/{int(home_id)}/global/L/logo.svg", output_width=128, output_height=128)
        away_png = cairosvg.svg2png(url=f"https://cdn.nba.com/logos/nba/{int(away_id)}/global/L/logo.svg", output_width=128, output_height=128)

        home_img = Image.open(BytesIO(home_png)).convert("RGBA")
        away_img = Image.open(BytesIO(away_png)).convert("RGBA")

        combined = Image.new("RGBA", (256, 128))
        combined.paste(away_img, (0, 0))
        combined.paste(home_img, (128, 0))

        output = BytesIO()
        combined.save(output, format="PNG")
        output.seek(0)
        return discord.File(fp=output, filename="logos.png")
    except Exception as e:
        print(f"Erro ao juntar logos: {e}")
        return None

@bot.event
async def on_ready():
    print('-=' * 20 + '-')
    print(f'Running {bot.user.name} - {bot.user.id}')
    print('-=' * 20 + '-')
    
@bot.command()
async def ping(ctx):
    await ctx.send('Pong!')

@bot.command()
async def player(ctx: commands.Context):
    player_name = ctx.message.content.replace('!player ', '').strip()
    embed = discord.Embed(title=f"NBA Infos 🤓", color=discord.Color.red())
    try:
        player = players.find_players_by_full_name(player_name)
        if not player:
            await ctx.send(f"Jogador {player_name} não encontrado.")
            return
        player_id = player[0]["id"]
        player_data = commonplayerinfo.CommonPlayerInfo(player_id=player_id)
        infos = player_data.get_dict()
        common_info = infos['resultSets'][0]
        info_values = common_info['rowSet'][0]
        info_headers = common_info['headers']
        info_dict = dict(zip(info_headers, info_values))
        
        altura = height_in_meters(info_dict['HEIGHT'])
        peso = weight_in_kg(info_dict['WEIGHT'])
        
        embed.add_field(name="Nome", value=info_dict['DISPLAY_FIRST_LAST'], inline=True)
        embed.add_field(name="Posição", value=info_dict['POSITION'], inline=True)
        embed.add_field(name="Time", value=f"{info_dict['TEAM_NAME']} ({info_dict['TEAM_ABBREVIATION']})", inline=True)
        embed.add_field(name="Altura", value=f"{altura} m", inline=True)
        embed.add_field(name="Peso", value=f"{peso} kg", inline=True)
        embed.add_field(name="Universidade", value=info_dict['SCHOOL'], inline=True)
        embed.add_field(name="Ano de Draft", value=info_dict['DRAFT_YEAR'], inline=True)
        embed.add_field(name="Rodada/Pick", value=f"{info_dict['DRAFT_ROUND']}ª / {info_dict['DRAFT_NUMBER']}º", inline=True)
        
        url_imagem = f"https://cdn.nba.com/headshots/nba/latest/1040x760/{player_id}.png"
        response = requests.get(url_imagem)
        
        if response.status_code == 200:
            image = Image.open(BytesIO(response.content))
            image_bytes = BytesIO()
            image.save(image_bytes, format="PNG")
            image_bytes.seek(0)
            image_file = discord.File(fp=image_bytes, filename="player.png")
            embed.set_image(url="attachment://player.png")
        else:
            await ctx.send(f"Imagem de {player_name} não encontrada.")
            
        stats = player_data.player_headline_stats.get_dict()
        status_json = stats['data'][0]
        embed.add_field(name="\u200b", value="\u200b", inline=False)
        embed.add_field(name="SEASON", value=f"{status_json[2]}", inline=False)
        embed.add_field(name="PTS", value=f"{status_json[3]}", inline=True)
        embed.add_field(name="AST", value=f"{status_json[4]}", inline=True)
        embed.add_field(name="REB", value=f"{status_json[5]}", inline=True)
        await ctx.send(embed=embed, file=image_file)
    except Exception as e:
        await ctx.send(f"Erro ao buscar dados de {player_name}.")
        print(e)
@bot.command()
async def jogos(ctx: commands.Context,  tricode: str = None):
    scorelive = scoreboard.ScoreBoard()
    data = scorelive.get_dict()
    games = data['scoreboard']['games']
    rows = []

    for game in games:
        home_team = game['homeTeam']
        away_team = game['awayTeam']
        rows.append({
            'home_team':    home_team['teamName'],
            'home_city':    home_team['teamCity'],
            'home_tricode': home_team['teamTricode'],
            'home_team_id': home_team['teamId'],
            'home_score':   home_team['score'],
            'home_wins':    home_team['wins'],
            'home_losses':  home_team['losses'],
            'away_team':    away_team['teamName'],
            'away_city':    away_team['teamCity'],
            'away_tricode': away_team['teamTricode'],
            'away_team_id': away_team['teamId'],
            'away_score':   away_team['score'],
            'away_wins':    away_team['wins'],
            'away_losses':  away_team['losses'],
            'status':       game['gameStatusText'],
            'period':       game['period'],
            'gameClock':    game['gameClock'],
        })

    df = pd.DataFrame(rows)

    if tricode:
        tricode = tricode.upper()
        mask = (
            (df['home_tricode'] == tricode) |
            (df['away_tricode'] == tricode) |
            (df['home_team'].str.upper() == tricode) |
            (df['away_team'].str.upper() == tricode)
        )
        df = df[mask]

        if df.empty:
            await ctx.send(f"❌ Nenhum jogo encontrado para **{tricode}** hoje.")
            return

    for _, row in df.iterrows():
        logos_file = merge_logos(row['home_team_id'], row['away_team_id'])

        files = [logos_file] if logos_file else []

        if row['period'] > 0 and row['gameClock']:
            clock = format_game_clock(row['gameClock'])
            status_str = f"🟢 {clock} — Q{row['period']}"
        elif row['period'] > 0:
            status_str = f"🟡 Intervalo — Q{row['period']}"
        else:
            status_str = f"🕐 {row['status']}"

        embed = discord.Embed(
            title=f"{row['away_city']} {row['away_team']}  ×  {row['home_city']} {row['home_team']}",
            description=status_str,
            color=0x1d428a
        )

        embed.add_field(
            name=f"{row['away_tricode']}",
            value=f"**{row['away_score']}**\n{row['away_wins']}W - {row['away_losses']}L",
            inline=True
        )
        embed.add_field(name="​", value="**VS**", inline=True)
        embed.add_field(
            name=f"{row['home_tricode']} 🏠",
            value=f"**{row['home_score']}**\n{row['home_wins']}W - {row['home_losses']}L",
            inline=True
        )

        embed.set_image(url="attachment://logos.png")
        embed.set_footer(text=f"{row['away_tricode']} vs {row['home_tricode']}")

        await ctx.send(files=files, embed=embed)
bot.run(ACESS_TOKEN)