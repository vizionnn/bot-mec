import discord
from discord.ext import commands, tasks
import os
from dotenv import load_dotenv
import json
import re
import time
import asyncio
from datetime import datetime, timedelta, timezone
import pytz

load_dotenv()

# Configurações dos intents
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

# IDs dos cargos que você deseja incluir no ranking
cargos_desejados = [
    1235035964573880397, 1235035964573880398, 1235035964556972094,
    1235035964599042090, 1235035964599042091, 1235035964599042094,
    1235035964599042095
]

# Data de início e fim da contagem
data_inicio = datetime(2024, 7, 1, tzinfo=timezone.utc)  # Define a data de início com fuso horário UTC
data_fim = datetime(2024, 8, 1, tzinfo=timezone.utc)     # Define a data de fim com fuso horário UTC

# Variável para armazenar a mensagem do ranking
mensagem_ranking = None

# Defina o fuso horário
timezone = pytz.timezone('America/Sao_Paulo')

# Canal de destino para o ranking
canal_ranking_id = 1246991184593948764  # ID do canal ranking-tunning

# Caminho para o arquivo de relatórios
relatorios_path = 'relatorios.json'

# Carregar dados de relatórios
relatorios = {}
if os.path.exists(relatorios_path):
    try:
        with open(relatorios_path, 'r') as f:
            relatorios = json.load(f)
    except FileNotFoundError:
        pass  # Se o arquivo não existir, o dicionário já está vazio

@bot.event
async def on_ready():
    print(f'Bot está pronto. Logado como {bot.user}')

    global membros_por_id  # Declarar a variável global
    membros_por_id = {membro.id: membro for membro in bot.get_all_members()}  # Criar o dicionário aqui

    try:
        # Certifique-se de que estamos carregando o histórico do canal correto
        canal_relatorios = bot.get_channel(1235035965945413649)  # Canal #relat-tunning
        if canal_relatorios:
            await bot.wait_until_ready()  # Espera o bot estar pronto
            await carregar_relatorios_antigos(canal_relatorios)  # Carrega relatórios antigos
            await exibir_ranking()  # Exibe o ranking inicial no canal correto
    except discord.errors.NotFound:
        print("Erro: Canal de relatórios não encontrado.")
    except discord.errors.Forbidden:
        print("Erro: O bot não tem permissão para ler o histórico de mensagens do canal.")
    
    # Iniciar a tarefa de salvar dados periodicamente
    salvar_dados.start()

# Função para carregar relatórios antigos
async def carregar_relatorios_antigos(channel):
    global relatorios
    print(f"Carregando relatórios antigos entre {data_inicio} e {data_fim}...")
    async for message in channel.history(after=data_inicio, before=data_fim, limit=None):  # Busca todas as mensagens dentro do período
        print(f"Processando mensagem antiga: {message.content}")
        await processar_relatorio(message, atualizacao_antiga=True)
    print("Carregamento de relatórios antigos concluído.")

# Função para processar um relatório (novo ou antigo)
async def processar_relatorio(message, atualizacao_antiga=False):
    global relatorios

    # Criar dicionário de membros por ID (uma vez, no início da função)
    membros_por_id = {membro.id: membro for membro in message.guild.members}

    # Procura por números na mensagem que são IDs inteiros (não partes de outros números)
    for id_match in re.finditer(r"\b\d+\b", message.content):
        user_id = int(id_match.group(0))
        for membro in membros_por_id.values():
            if str(user_id) == membro.display_name.split()[-1]:  # Verifica se o nome de exibição termina com o ID
                if any(cargo.id in cargos_desejados for cargo in membro.roles):
                    relatorios[membro.id] = relatorios.get(membro.id, 0) + 1
                    print(f"Relatório adicionado: {membro.display_name} agora tem {relatorios[membro.id]} relatórios")
                break
        else:
            print(f"Erro: ID {user_id} não encontrado na lista de membros.")  # Mensagem de erro para ID não encontrado

    if not atualizacao_antiga:
        await exibir_ranking()  # Atualiza o ranking imediatamente se não for uma atualização antiga

# Função para atualizar o ranking
async def exibir_ranking():
    global relatorios
    global mensagem_ranking

    # Buscar o canal correto para o ranking
    channel = bot.get_channel(canal_ranking_id)

    if not channel:
        print("Erro: Canal de ranking não encontrado.")
        return

    # Buscar membros com os cargos desejados e seus totais de relatórios
    membros_validos = []
    for role_id in cargos_desejados:
        role = channel.guild.get_role(role_id)
        if role:
            membros_validos.extend(role.members)

    # Ordenar os membros pelo total de relatórios (decrescente)
    membros_validos.sort(key=lambda membro: relatorios.get(membro.id, 0), reverse=True)

    # Criar o ranking em formato de texto
    ranking_str = ""
    for i, membro in enumerate(membros_validos, start=1):
        posicao = "🏆`º`" if i == 1 else f"`{i}º`"
        total_relatorios = relatorios.get(membro.id, 0)  # Obter o total de relatórios do membro
        ranking_str += f"{posicao} - {membro.mention}: {total_relatorios} relatórios\n"

    # Criar o embed do ranking
    embed = discord.Embed(title="👑 Ranking de Relatórios de Tunning", description=ranking_str, color=0xffa500)
    embed.set_thumbnail(url=channel.guild.icon.url)
    embed.add_field(name="\u200b", value=f"**📬 Total de relatórios: {sum(relatorios.values())}**", inline=False)
    embed.set_footer(text=f"📅 Desde\n`{data_inicio.strftime('%d %B')}` \n\n ⏰ Última atualização: {current_time}")

    # Editar a mensagem existente ou enviar uma nova
    try:
        if mensagem_ranking:
            await mensagem_ranking.edit(embed=embed)
        else:
            mensagem_ranking = await channel.send(embed=embed)
    except discord.errors.HTTPException as e:
        print(f"Erro ao atualizar o ranking: {e}")

# Evento para registrar relatórios
@bot.event
async def on_message(message):
    if message.channel.id == 1235035965945413649:  # Canal #relat-tunning
        # Converter a data da mensagem para offset-aware (UTC) e ajustar para o fuso horário de Recife (-03:00)
        message_created_at_aware = message.created_at.replace(tzinfo=timezone.utc) - timedelta(hours=3)
        if data_inicio <= message_created_at_aware < data_fim:
            await processar_relatorio(message)

    await bot.process_commands(message)

# Evento para reduzir a contagem de relatórios se a mensagem for apagada
@bot.event
async def on_message_delete(message):
    if message.channel.id == 1235035965945413649:  # Canal #relat-tunning
        await processar_relatorio_remocao(message)

# Evento para atualizar a contagem de relatórios se a mensagem for editada
@bot.event
async def on_message_edit(before, after):
    if before.channel.id == 1235035965945413649:  # Canal #relat-tunning
        await processar_relatorio_remocao(before)
        await processar_relatorio(after)

# Função para processar a remoção de um relatório
async def processar_relatorio_remocao(message):
    global relatorios

    # Criar dicionário de membros por ID (uma vez, no início da função)
    membros_por_id = {membro.id: membro for membro in message.guild.members}

    # Procura por números na mensagem que são IDs inteiros (não partes de outros números)
    for id_match in re.finditer(r"\b\d+\b", message.content):
        user_id = int(id_match.group(0))
        for membro in membros_por_id.values():
            if str(user_id) == membro.display_name.split()[-1]:  # Verifica se o nome de exibição termina com o ID
                if any(cargo.id in cargos_desejados for cargo in membro.roles):
                    relatorios[membro.id] = relatorios.get(membro.id, 0) - 1
                    if relatorios[membro.id] <= 0:
                        del relatorios[membro.id]  # Remove o membro do dicionário se o total for zero ou negativo
                    print(f"Relatório removido: {membro.display_name} agora tem {relatorios.get(membro.id, 0)} relatórios")
                break

    await exibir_ranking()  # Atualiza o ranking após a remoção

# Salvar os dados de relatórios periodicamente
@tasks.loop(minutes=5)
async def salvar_dados():
    global relatorios
    with open(relatorios_path, 'w') as f:
        json.dump(relatorios, f)
    print("Dados de relatórios salvos.")

# Evento para registrar saídas de membros
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
        await channel.send(embed=embed)

bot.run(os.getenv('DISCORD_TOKEN'))