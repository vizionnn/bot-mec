import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import json
import re
import schedule
import time

load_dotenv()
intents = discord.Intents.default()
intents.members = True
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event # bot de saída
async def on_ready():
    print(f'Bot está pronto. Logado como {bot.user}')

@bot.event
async def on_member_remove(member):
    guild = member.guild
    channel_id = 1235035965391765566  # Substitua pelo ID do seu canal

    embed = discord.Embed(title="Um membro saiu!", color=discord.Color.red())
    embed.set_thumbnail(url=member.display_avatar.url)

    embed.add_field(name="DISCORD:", value=member.mention, inline=False)
    embed.add_field(name="ID DISCORD:", value=member.id, inline=False)
    embed.add_field(name="Nome:", value=member.name, inline=False)

    roles = ", ".join([role.name for role in member.roles if role.name != '@everyone'])
    embed.add_field(name="Cargos Antes da Saída:", value=roles, inline=False)

    embed.set_footer(text=f"{member.guild.name}")

    channel = guild.get_channel(channel_id)
    if channel:
        await channel.send(embed=embed) # término do bot de sessão de saída

# Carregar dados de relatórios (inicialmente vazio)
try:
    with open('relatorios.json', 'r') as f:
        relatorios = json.load(f)
except FileNotFoundError:
    relatorios = {}

# Função para atualizar o ranking
async def atualizar_ranking():
    channel = bot.get_channel(1246991184593948764)  # Canal #ranking-tunning
    if channel:
        ranking = sorted(relatorios.items(), key=lambda item: item[1], reverse=True)

        embed = discord.Embed(title="Ranking de Relatórios de Tunning", color=discord.Color.blue())

        for i, (user_id, total) in enumerate(ranking, start=1):
            user = await bot.fetch_user(user_id)
            embed.add_field(name=f"{i}º - {user.name}", value=f"**ID:** {user_id}\n**Relatórios:** {total}", inline=False)

        embed.set_footer(text=f"Última atualização: {time.strftime('%d/%m/%Y %H:%M:%S')}")
        await channel.send(embed=embed)

# Reiniciar ranking manualmente
@bot.command(name='reiniciar-ranking')
async def reiniciar_ranking(ctx):
    global relatorios
    relatorios = {}
    with open('relatorios.json', 'w') as f:
        json.dump(relatorios, f)
    await ctx.send("Ranking de relatórios reiniciado com sucesso!")

# Evento para registrar relatórios
@bot.event
async def on_message(message):
    if message.channel.id == 1235035965945413649:  # Canal #relat-tunning
        if message.content.startswith("Meu ID:"):
            id_match = re.search(r"Meu ID:\s*(\d+)", message.content)
            if id_match:
                user_id = int(id_match.group(1))
                relatorios[user_id] = relatorios.get(user_id, 0) + 1
                with open('relatorios.json', 'w') as f:
                    json.dump(relatorios, f)
                await atualizar_ranking()

    await bot.process_commands(message)  # Processar outros comandos

# Agendar atualização automática do ranking
schedule.every(1).minutes.do(atualizar_ranking)

@bot.event
async def on_ready():
    print(f'Bot está pronto. Logado como {bot.user}')
    while True:
        schedule.run_pending()
        time.sleep(1)

bot.run(os.getenv('DISCORD_TOKEN'))
