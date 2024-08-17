import discord
from discord.ext import commands, tasks
from discord import app_commands
from discord.ui import Button, View, Select, Modal, TextInput
from discord.utils import get
import logging
import pytz
import re
import os
import json
from dotenv import load_dotenv
import asyncio
import sqlite3
from discord.ext import commands
from discord.ext.commands import CooldownMapping, BucketType
import time
from datetime import datetime, timezone, timedelta

# Configurações dos intents
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

#comandos dm e message
AUTHORIZED_ROLES = [1235035964556972095, 1235035964556972099]
LOG_CHANNEL_ID = 1249235583637651507

# IDs do canal de provas e do canal de correção de provas
canal_prova_aluno_id = 1235035966876549126
canal_corrigir_prova_id = 1235035966876549127

# IDs dos cargos que podem visualizar o canal temporário
cargo_visualizacao_1_id = 1235035964556972095
cargo_visualizacao_2_id = 1235035964556972099

# ID do cargo responsável por realizar a prova
cargo_prova_id = 1258746878946709566

# IDs dos cargos
cargo_visualizacao_1_id = 1235035964556972095
cargo_visualizacao_2_id = 1235035964556972099
cargo1_id = 1235035964573880397
cargo2_id = 1242992334640255078  # Funcionário
cargo_para_remover_id = 1258746878946709566

# IDs dos cargos para promoção
cargo_estagiario_id = 1235035964573880397 # Estagiário
cargo_mecanico_id = 1235035964573880398 # Mecânico
cargo_mecanico_senior_id = 1235035964556972094 # Mecânico Sênior

# ID do cargo de devedor
cargo_devedor_id = 1255196288698552321
cargo_devedor_adv_id = 1255196379609825350

# ID do canal de log/relatório de contratação
canal_log_contratacao_id = 1249235893634469888
# ID do canal de log/relatório de promoção
canal_log_promocao_id = 1246992211749503085

#ID do cargo exonerado
cargo_exonerado_id = 1235035964556972093

# Cria um mapeamento de cooldown para limitar as edições de mensagens
cooldown_mapping = CooldownMapping.from_cooldown(1, 4.0, BucketType.guild)  # 1 operação a cada 10 segundos

# Dicionário para armazenar o tempo da última atualização por servidor
last_update_time = {}

# Intervalo de cooldown em segundos
cooldown_interval = 4

# IDs dos cargos de devedores
roles_ids = {
    'adv1': 1235035964556972100,
    'adv2': 1235035964556972101,
    'adv3': 1235035964573880390,
    'adv4': 1255195989778628739,
    'rebaixado': 1235035964556972097,
    'devedor_manutencao': 1255196288698552321,
    'devedor_adv': 1255196379609825350
}

#canal devedores
channel_id_devedores = 1255178131707265066  # id canal devedores
hierarchy_message_id_devedores = None

# URL da thumbnail
thumbnail_url = "https://cdn.discordapp.com/attachments/1235035964624080994/1273292957646327898/4a8075045e92cfa895a6c672fad7d1fa.png?ex=66c0b8f9&is=66bf6779&hm=e0cc82c95d4d8238642196305880f02809359e7f1e4ad5d3847b74239cb0e3fa&"

# IDs dos cargos que você deseja incluir no ranking
cargos_desejados = [
    1235035964573880397, 1235035964573880398, 1235035964556972094,
    1235035964599042090, 1235035964599042091, 1235035964599042094,
    1235035964599042095
]

# Data de início e fim da contagem ~~MENSAL~~
data_inicio = datetime(2024, 8, 1, tzinfo=timezone.utc)  # Define a data de início com fuso horário UTC
data_fim = datetime(2024, 9, 1, tzinfo=timezone.utc)     # Define a data de fim com fuso horário UTC

# Variável para armazenar a mensagem do ranking
mensagem_ranking = None

# Defina o fuso horário
timezone_brasil = pytz.timezone('America/Sao_Paulo')

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

# Data de início e fim da contagem ~~SEMANAL~~
data_inicio_semanal = datetime(2024, 8, 12, tzinfo=timezone.utc)  # Define a data de início com fuso horário UTC
data_fim_semanal = datetime(2024, 8, 18, tzinfo=timezone.utc)     # Define a data de fim com fuso horário UTC

# Variável para armazenar a mensagem do ranking
mensagem_ranking_smnl = None

# Canal de destino para o ranking
canal_ranking_semanal_id = 1273558603256692822 # ID do canal semanal ranking-tunning

# Variável global para armazenar relatórios
relatorios_smnl = {}

# IDs dos cargos com permissão
cargos_permitidos = [1235035964556972099, 1235035964556972095]

# Configurações dos intents
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

# IDs dos canais de voz a serem monitorados
canais_voz_ids = [
    1246984837223419944, 1244164121553932318, 1244170549312098354,
    1244170938355027978, 1244171050397470731, 1244174326949744711,
    1244174420139053077, 1247009675162161162
]

# IDs dos cargos CANAL HIERARQUIA
roles_hierarchy = {
    1235035964624080990: "CEO",
    1235035964624080989: "👑",
    1235035964624080987: "prefeitura",
    1235035964599042095: "chefe",
    1235035964599042094: "sub chefe",
    1235035964599042091: "gerente",
    1235035964599042090: "sub-gerente",
    1235035964556972094: "mecânico senior",
    1235035964573880398: "mecânico",
    1235035964573880397: "estagiário"
}

# ID do canal onde a hierarquia será postada
canal_hierarquia_id = 1250878994346414121 # Substitua pelo ID do canal real

# Mensagem que será editada
mensagem_hierarquia = None

#_______________________________________________________________________________

# fim variáveis, inicio bot de comandos

# ID do canal de consulta
consultar_horas_id = 1246990807140007997

async def has_allowed_role(interaction: discord.Interaction):
    # Lista de IDs dos cargos permitidos
    allowed_roles = [1235035964556972099, 1235035964556972095]

    # Verifica se o usuário tem algum dos cargos permitidos
    for role in interaction.user.roles:
        if role.id in allowed_roles:
            return True
    
    return False

@bot.tree.command(name="consultarelat", description="Consulta relatórios de um usuário em um período.")
@app_commands.describe(user="Usuário a ser consultado", data_inicio="Data de início (DD/MM/YYYY)", data_fim="Data de fim (DD/MM/YYYY)")
async def consultarelat(interaction: discord.Interaction, user: discord.User, data_inicio: str, data_fim: str):
    # Verificar permissões
    if not await has_allowed_role(interaction):
        await interaction.response.send_message("Você não tem permissão para usar este comando.", ephemeral=True)
        return

    try:
        # Converte as datas de string para objetos datetime e aplica o fuso horário do Brasil
        data_inicio_dt = datetime.strptime(data_inicio, "%d/%m/%Y").replace(tzinfo=timezone_brasil)
        data_fim_dt = datetime.strptime(data_fim, "%d/%m/%Y").replace(tzinfo=timezone_brasil)

        # Ajuste para incluir o dia inteiro na busca (até 23:59:59 do data_fim)
        data_fim_dt = data_fim_dt + timedelta(days=1) - timedelta(seconds=1)

    except ValueError:
        await interaction.response.send_message("Formato de data inválido. Use DD/MM/YYYY.", ephemeral=True)
        return

    # Variável para contar os relatórios dentro do período
    total_relatorios = 0

    # Canal #relat-tunning
    canal_relatorios = bot.get_channel(1235035965945413649)

    if not canal_relatorios:
        await interaction.response.send_message("Erro: Canal de relatórios não encontrado.", ephemeral=True)
        return

    # Busca de mensagens no canal dentro do período com os limites inclusivos
    async for message in canal_relatorios.history(after=data_inicio_dt - timedelta(seconds=1), before=data_fim_dt + timedelta(seconds=1), limit=None):
        if message.author == user:
            total_relatorios += 1

    await interaction.response.send_message(f"{user.mention} fez {total_relatorios} relatórios de {data_inicio} a {data_fim}.")


@bot.tree.command(name="tempo", description="Consultar o tempo em serviço de um usuário pelo ID ou menção.")
@app_commands.describe(user="ID ou menção do usuário a ser consultado")
@app_commands.checks.has_any_role(*cargos_permitidos)
async def tempo(interaction: discord.Interaction, user: str):
    try:
        if user.startswith("<@") and user.endswith(">"):
            user_id = int(user[3:-1].replace("!", ""))
        else:
            user_id = int(user)
        
        user = interaction.guild.get_member(user_id)
        if user:
            tempo_total = calcular_tempo_servico(user_id)
            tempo_formatado = formatar_tempo(tempo_total)
            await interaction.response.send_message(f'Usuário {user.mention} tem {tempo_formatado} em serviço.', ephemeral=True)
        else:
            await interaction.response.send_message('Usuário não encontrado.', ephemeral=True)
    except ValueError:
        await interaction.response.send_message('Insira um ID ou menção de usuário válido.', ephemeral=True)

@tempo.error
async def tempo_error(interaction: discord.Interaction, error):
    if isinstance(error, app_commands.MissingAnyRole):
        await interaction.response.send_message("Você não tem permissão para usar este comando.", ephemeral=True)
    else:
        await interaction.response.send_message("Ocorreu um erro ao tentar executar este comando.", ephemeral=True)
        print(f"Erro no comando /tempo: {error}")

tree = bot.tree

# Verifica se o usuário tem um dos cargos autorizados
def check_authorized_roles():
    async def predicate(interaction: discord.Interaction):
        return any(role.id in AUTHORIZED_ROLES for role in interaction.user.roles)
    return app_commands.check(predicate)

#   Comando /mensagem
@tree.command(name="mensagem", description="Enviar mensagem privada para todos os membros de um cargo.")
@app_commands.describe(cargo="Cargo alvo", mensagem="Mensagem a ser enviada")
@check_authorized_roles()
async def mensagem(interaction: discord.Interaction, cargo: discord.Role, mensagem: str):
    log_channel = bot.get_channel(LOG_CHANNEL_ID)
    await interaction.response.send_message(f'Enviando mensagens para todos os membros com o cargo {cargo.mention}.', ephemeral=True)
    for member in cargo.members:
        try:
            await member.send(mensagem)
        except discord.Forbidden:
            await log_channel.send(f'Não foi possível enviar a mensagem para {member.mention}.')
    await log_channel.send(
        f'Usuário {interaction.user.mention} enviou a seguinte mensagem para o cargo {cargo.mention}:\n```\n{mensagem}\n```'
    )

@mensagem.error
async def mensagem_error(interaction: discord.Interaction, error):
    if isinstance(error, app_commands.MissingPermissions):
        await interaction.response.send_message("Você não tem permissão para usar este comando.", ephemeral=True)
    else:
        await interaction.response.send_message("Ocorreu um erro ao tentar executar este comando.", ephemeral=True)
        print(f"Erro no comando /mensagem: {error}")

#   comando /dm
@tree.command(name="dm", description="Enviar mensagem privada para um usuário específico.")
@app_commands.describe(user="Usuário alvo", mensagem="Mensagem a ser enviada")
@check_authorized_roles()
async def dm(interaction: discord.Interaction, user: discord.User, mensagem: str):
    log_channel = bot.get_channel(LOG_CHANNEL_ID)
    try:
        await user.send(mensagem)
        await interaction.response.send_message(f'Mensagem enviada para {user.mention}.', ephemeral=True)
        await log_channel.send(
            f'Usuário {interaction.user.mention} enviou a seguinte mensagem para {user.mention}:\n```\n{mensagem}\n```'
        )
    except discord.Forbidden:
        await interaction.response.send_message(f'Não foi possível enviar a mensagem para {user.mention}.', ephemeral=True)

@dm.error
async def dm_error(interaction: discord.Interaction, error):
    if isinstance(error, app_commands.MissingPermissions):
        await interaction.response.send_message("Você não tem permissão para usar este comando.", ephemeral=True)
    else:
        await interaction.response.send_message("Ocorreu um erro ao tentar executar este comando.", ephemeral=True)
        print(f"Erro no comando /dm: {error}")

# Comando /contratar
@bot.tree.command(name="contratar", description="Contratar um novo membro e dar os cargos especificados.")
@app_commands.describe(nome="Primeiro nome do usuário", id_cidade="ID da cidade", usuario="Usuário a ser contratado")
@app_commands.checks.has_any_role(cargo_visualizacao_1_id, cargo_visualizacao_2_id)
async def contratar(interaction: discord.Interaction, nome: str, id_cidade: str, usuario: discord.User):
    try:
        recrutador = interaction.user
        recrutador_mention = recrutador.mention
        recrutador_id = recrutador.id

        nome_contratado = nome.split()[0]
        id_cidade = id_cidade
        id_discord = usuario.id

        guild = interaction.guild
        contratado = guild.get_member(id_discord)

        if contratado:
            novo_nome = f"🔨・{nome_contratado} | {id_cidade}"
            try:
                await contratado.edit(nick=novo_nome)
                await contratado.add_roles(
                    guild.get_role(cargo1_id),
                    guild.get_role(cargo2_id)
                )

                # Remover o cargo especificado, se o usuário o tiver
                cargo_para_remover = guild.get_role(cargo_para_remover_id)
                if cargo_para_remover in contratado.roles:
                    await contratado.remove_roles(cargo_para_remover)

                canal_log = guild.get_channel(canal_log_contratacao_id)
                data_inicio = datetime.now().strftime("%d/%m/%Y")
                data_exp = (datetime.now() + timedelta(days=3)).strftime("%d/%m/%Y")

                mensagem_log = (
                    f"NOME: {nome_contratado}\n"
                    f"ID: {id_cidade}\n"
                    f"DISCORD: {contratado.mention}\n"
                    f"RECRUTADOR: {recrutador_mention}\n"
                    f"ID RECRUTADOR: ({recrutador_id})\n"
                    f"DATA DE INÍCIO DE CONTRATO: {data_inicio}\n"
                    f"DATA DE PERÍODO DE EXP: {data_exp}"
                )
                await canal_log.send(mensagem_log)
                await interaction.response.send_message(f"Usuário {contratado.mention} contratado com sucesso!", ephemeral=True)
            except discord.errors.Forbidden:
                await interaction.response.send_message("Permissões insuficientes para editar o usuário ou adicionar/remover cargos.", ephemeral=True)
        else:
            await interaction.response.send_message("Usuário não encontrado.", ephemeral=True)
    except Exception as e:
        print(f"Ocorreu um erro: {e}")
        await interaction.response.send_message("Ocorreu um erro ao tentar executar este comando.", ephemeral=True)

@contratar.error
async def contratar_error(interaction: discord.Interaction, error):
    if isinstance(error, app_commands.MissingAnyRole):
        await interaction.response.send_message("Você não tem permissão para usar este comando.", ephemeral=True)
    else:
        await interaction.response.send_message("Ocorreu um erro ao tentar executar este comando.", ephemeral=True)
        print(f"Erro no comando /contratar: {error}")

# Comando /promover
@bot.tree.command(name="promover", description="Promover um estagiário para mecânico.")
@app_commands.describe(usuario="Usuário a ser promovido (menção ou ID)")
@app_commands.checks.has_any_role(cargo_visualizacao_1_id, cargo_visualizacao_2_id)
async def promover(interaction: discord.Interaction, usuario: str):
    try:
        # Verificar se o parâmetro é uma menção ou um ID
        if usuario.startswith("<@") and usuario.endswith(">"):
            id_discord = int(usuario[3:-1].replace("!", ""))  # Extrair ID da menção
        else:
            id_discord = int(usuario)  # Converter para int se for um ID

        promotor = interaction.user
        promotor_mention = promotor.mention
        promotor_id = promotor.id

        guild = interaction.guild
        promovido = guild.get_member(id_discord)

        if promovido:
            nome_contratado = promovido.display_name.split("・")[1].split(" | ")[0]
            id_cidade = promovido.display_name.split(" | ")[1]
            novo_nome = f"🔧・{nome_contratado} | {id_cidade}"

            try:
                await promovido.edit(nick=novo_nome)
                await promovido.add_roles(
                    guild.get_role(cargo_mecanico_id),
                    guild.get_role(cargo2_id)  # Mantém o cargo de funcionário
                )
                await promovido.remove_roles(guild.get_role(cargo_estagiario_id))

                canal_log = guild.get_channel(canal_log_promocao_id)
                
                mensagem_log = (
                    f"⏫ ┃ PROMOÇÃO DE CARGO ┃ ⏫\n\n"
                    f"- CARGO ANTERIOR: <@&{cargo_estagiario_id}>\n"
                    f"- CARGO ATUAL: <@&{cargo_mecanico_id}>\n"
                    f"- PROMOVIDO POR: {promotor_mention}\n"
                    f"- ID DE QUEM PROMOVEU: ({promotor_id})\n"
                    f"- PROMOVIDO: {promovido.mention}"
                )
                await canal_log.send(mensagem_log)
                await interaction.response.send_message(f"Usuário {promovido.mention} promovido com sucesso!", ephemeral=True)
            except discord.errors.Forbidden:
                await interaction.response.send_message("Permissões insuficientes para editar o usuário ou adicionar/remover cargos.", ephemeral=True)
        else:
            await interaction.response.send_message("Usuário não encontrado.", ephemeral=True)
    except Exception as e:
        print(f"Ocorreu um erro: {e}")
        await interaction.response.send_message("Ocorreu um erro ao tentar executar este comando.", ephemeral=True)

@promover.error
async def promover_error(interaction: discord.Interaction, error):
    if isinstance(error, app_commands.MissingAnyRole):
        await interaction.response.send_message("Você não tem permissão para usar este comando.", ephemeral=True)
    else:
        await interaction.response.send_message("Ocorreu um erro ao tentar executar este comando.", ephemeral=True)
        print(f"Erro no comando /promover: {error}")

# Comando /devedores
@bot.tree.command(name="devedores", description="Adicionar o cargo de devedor e o emoji de devedor no nome dos usuários.")
@app_commands.describe(cargo="Cargo a ser verificado (mec, estag ou todos).")
@app_commands.checks.has_any_role(cargo_visualizacao_1_id, cargo_visualizacao_2_id)
async def devedores(interaction: discord.Interaction, cargo: str = None):
    try:
        guild = interaction.guild
        cargo_devedor = guild.get_role(cargo_devedor_id)
        cargo_devedor_adv = guild.get_role(cargo_devedor_adv_id)

        # Determina os cargos participantes
        if cargo is None or cargo.lower() == "todos":
            cargos_participantes = [cargo_mecanico_id, cargo_mecanico_senior_id, cargo_estagiario_id]
        elif cargo.lower() == "mec":
            cargos_participantes = [cargo_mecanico_id, cargo_mecanico_senior_id]  # Inclui os dois cargos aqui
        elif cargo.lower() == "estag":
            cargos_participantes = [cargo_estagiario_id]
        else:
            await interaction.response.send_message("Cargo inválido. Use 'mec', 'estag' ou deixe em branco para todos.", ephemeral=True)
            return

        for cargo_id in cargos_participantes:
            cargo_participante = guild.get_role(cargo_id)
            for member in cargo_participante.members:
                await member.add_roles(cargo_devedor)
                nome_contratado = member.display_name.split("・")[1].split(" | ")[0]
                id_cidade = member.display_name.split(" | ")[1]
                
                if cargo_id == cargo_mecanico_id:
                    novo_nome = f"🔧👎🏻・{nome_contratado} | {id_cidade}"
                    if cargo_devedor_adv in member.roles:
                        novo_nome = f"🔧👎🏻❌・{nome_contratado} | {id_cidade}"
                elif cargo_id == cargo_mecanico_senior_id:  # Verifica para o cargo mecânico sênior
                    novo_nome = f"🏆👎🏻・{nome_contratado} | {id_cidade}"
                    if cargo_devedor_adv in member.roles:
                        novo_nome = f"🏆👎🏻❌・{nome_contratado} | {id_cidade}"
                else:
                    novo_nome = f"🔨👎🏻・{nome_contratado} | {id_cidade}"
                    if cargo_devedor_adv in member.roles:
                        novo_nome = f"🔨👎🏻❌・{nome_contratado} | {id_cidade}"
                        
                await member.edit(nick=novo_nome)

        await interaction.response.send_message("Os devedores foram marcados com sucesso.", ephemeral=True)
    except Exception as e:
        print(f"Ocorreu um erro: {e}")
        await interaction.response.send_message("Ocorreu um erro ao tentar executar este comando.", ephemeral=True)

@devedores.error
async def devedores_error(interaction: discord.Interaction, error):
    if isinstance(error, app_commands.MissingAnyRole):
        await interaction.response.send_message("Você não tem permissão para usar este comando.", ephemeral=True)
    else:
        await interaction.response.send_message("Ocorreu um erro ao tentar executar este comando.", ephemeral=True)
        print(f"Erro no comando /devedores: {error}")

# Comando /pago
@bot.tree.command(name="pago", description="Remover o emoji de devedor do nome do usuário.")
@app_commands.describe(usuario="Usuário a ser atualizado (menção ou ID)")
@app_commands.checks.has_any_role(cargo_visualizacao_1_id, cargo_visualizacao_2_id)
async def pago(interaction: discord.Interaction, usuario: str):
    try:
        # Verificar se o parâmetro é uma menção ou um ID
        if usuario.startswith("<@") and usuario.endswith(">"):
            id_discord = int(usuario[3:-1].replace("!", ""))  # Extrair ID da menção
        else:
            id_discord = int(usuario)  # Converter para int se for um ID

        guild = interaction.guild
        devedor = guild.get_member(id_discord)
        cargo_devedor_adv = guild.get_role(cargo_devedor_adv_id)

        if devedor:
            nome_contratado = devedor.display_name.split("・")[1].split(" | ")[0]
            id_cidade = devedor.display_name.split(" | ")[1]

            if any(role.id == cargo_mecanico_id for role in devedor.roles):
                novo_nome = f"🔧✅・{nome_contratado} | {id_cidade}"
                if cargo_devedor_adv in devedor.roles:
                    novo_nome = f"🔧✅❌・{nome_contratado} | {id_cidade}"
            elif any(role.id == cargo_mecanico_senior_id for role in devedor.roles):
                novo_nome = f"🏆✅・{nome_contratado} | {id_cidade}"
                if cargo_devedor_adv in devedor.roles:
                    novo_nome = f"🏆✅❌・{nome_contratado} | {id_cidade}"
            elif any(role.id == cargo_estagiario_id for role in devedor.roles):
                novo_nome = f"🔨✅・{nome_contratado} | {id_cidade}"
                if cargo_devedor_adv in devedor.roles:
                    novo_nome = f"🔨✅❌・{nome_contratado} | {id_cidade}"
            else:
                await interaction.response.send_message("Usuário não possui o cargo de mecânico ou estagiário.", ephemeral=True)
                return

            cargo_devedor = guild.get_role(cargo_devedor_id)
            await devedor.remove_roles(cargo_devedor)
            await devedor.edit(nick=novo_nome)

            await interaction.response.send_message(f"Usuário {devedor.mention} teve o status de devedor removido com sucesso.", ephemeral=True)
        else:
            await interaction.response.send_message("Usuário não encontrado.", ephemeral=True)
    except Exception as e:
        print(f"Ocorreu um erro: {e}")
        await interaction.response.send_message("Ocorreu um erro ao tentar executar este comando.", ephemeral=True)

@pago.error
async def pago_error(interaction: discord.Interaction, error):
    if isinstance(error, app_commands.MissingAnyRole):
        await interaction.response.send_message("Você não tem permissão para usar este comando.", ephemeral=True)
    else:
        await interaction.response.send_message("Ocorreu um erro ao tentar executar este comando.", ephemeral=True)
        print(f"Erro no comando /pago: {error}")

# Comando /limpar
@bot.tree.command(name="limpar", description="Retornar os usuários para seus nomes padrões.")
@app_commands.checks.has_any_role(cargo_visualizacao_1_id, cargo_visualizacao_2_id)
async def limpar(interaction: discord.Interaction):
    try:
        guild = interaction.guild
        cargo_estagiario = guild.get_role(cargo_estagiario_id)
        cargo_mecanico = guild.get_role(cargo_mecanico_id)
        cargo_mecanico_senior = guild.get_role(cargo_mecanico_senior_id)  # Adicionado o cargo_mecanico_senior_id
        cargo_devedor_adv = guild.get_role(cargo_devedor_adv_id)
        
        # Adiciona os membros com os cargos mecânico, mecânico sênior ou estagiário à lista de membros para limpar
        membros_para_limpar = [
            m for m in guild.members 
            if cargo_estagiario in m.roles or cargo_mecanico in m.roles or cargo_mecanico_senior in m.roles
        ]

        for membro in membros_para_limpar:
            nome_contratado = membro.display_name.split("・")[1].split(" | ")[0]
            id_cidade = membro.display_name.split(" | ")[1]

            if cargo_mecanico in membro.roles:
                novo_nome = f"🔧・{nome_contratado} | {id_cidade}"
                if cargo_devedor_adv in membro.roles:
                    novo_nome = f"🔧❌・{nome_contratado} | {id_cidade}"
            elif cargo_mecanico_senior in membro.roles:  # Adicionada verificação para mecânico sênior
                novo_nome = f"🏆・{nome_contratado} | {id_cidade}"
                if cargo_devedor_adv in membro.roles:
                    novo_nome = f"🏆❌・{nome_contratado} | {id_cidade}"
            elif cargo_estagiario in membro.roles:
                novo_nome = f"🔨・{nome_contratado} | {id_cidade}"
                if cargo_devedor_adv in membro.roles:
                    novo_nome = f"🔨❌・{nome_contratado} | {id_cidade}"
            else:
                continue

            await membro.edit(nick=novo_nome)

        await interaction.response.send_message("Os nomes dos usuários foram limpos com sucesso.", ephemeral=True)
    except Exception as e:
        print(f"Ocorreu um erro: {e}")
        await interaction.response.send_message("Ocorreu um erro ao tentar executar este comando.", ephemeral=True)

# Comando /exonerar
@bot.tree.command(name="exonerar", description="Remover todos os cargos do usuário e adicionar o cargo de exonerado.")
@app_commands.describe(ids="IDs ou menções dos usuários a serem exonerados, separados por vírgula")
@app_commands.checks.has_any_role(cargo_visualizacao_1_id, cargo_visualizacao_2_id)
async def exonerar(interaction: discord.Interaction, ids: str):
    try:
        guild = interaction.guild
        cargo_exonerado = guild.get_role(cargo_exonerado_id)
        
        ids_discord = []
        for id_str in ids.split(","):
            id_str = id_str.strip()
            if id_str.startswith("<@") and id_str.endswith(">"):
                ids_discord.append(int(id_str[3:-1].replace("!", "")))  # Extract user ID from mention
            else:
                ids_discord.append(int(id_str))  # Convert to int if it's a plain user ID

        for id_discord in ids_discord:
            membro = guild.get_member(id_discord)
            if membro:
                nome_contratado = membro.display_name.split("・")[1].split(" | ")[0]
                id_cidade = membro.display_name.split(" | ")[1]
                novo_nome = f"[EX]・{nome_contratado} | {id_cidade}"

                # Remover todos os cargos e adicionar o cargo exonerado
                await membro.edit(roles=[cargo_exonerado], nick=novo_nome)

        await interaction.response.send_message(f"Usuários exonerados com sucesso.", ephemeral=True)
    except Exception as e:
        print(f"Ocorreu um erro: {e}")
        await interaction.response.send_message("Ocorreu um erro ao tentar executar este comando.", ephemeral=True)

@exonerar.error
async def exonerar_error(interaction: discord.Interaction, error):
    if isinstance(error, app_commands.MissingAnyRole):
        await interaction.response.send_message("Você não tem permissão para usar este comando.", ephemeral=True)
    else:
        await interaction.response.send_message("Ocorreu um erro ao tentar executar este comando.", ephemeral=True)
        print(f"Erro no comando /exonerar: {error}")

# Fim do código dos comandos /slash


# Questões do exame // --------------------------- FIM DOS COMANDOS /SLASH ---------------------------------

#---------------------------------------------------------------PROVA--------------------------------------------------------

questoes_abertas = [
    "Por que quer ser mecânico?",
    "Seu nome na cidade?",
    "Idade em Nárnia?",
    "ID na cidade?",
    "ID de quem o recrutou?"
]

questoes_fechadas = [
    {"pergunta": "Para ser promovido de ESTAGIARIO para MECÂNICO terá que cumprir quais requisitos?",
     "opcoes": ["03 DIAS e 6 HORAS TRABALHADAS", "6 DIAS e 3 HORAS TRABALHADAS", "3 HORAS ou 6 DIAS TRABALHADAS"],
     "correta": 0},
    {"pergunta": "Quando precisar ficar AFK (indisponível por um breve período, como devo agir?",
     "opcoes": ["Posso ficar em serviço, afinal retorno logo", "Avisar na rádio e depois retornar", "Sair do serviço, sair da rádio, tirar roupa de mecânico e sair da call 🧰 | ᴇᴍ sᴇʀᴠɪçᴏ, pois se for pego em serviço AFK serei advertido."],
     "correta": 2},
    {"pergunta": "Caso precise se ausentar na vida real como deve solicitar um atestado?",
     "opcoes": ["Se precisar me ausentar, solicito um atestado no canal 📅┃ᴄᴏʟᴏᴄᴀʀ-ᴀᴛᴇsᴛᴀᴅᴏ. Se não cumpri as metas conseguirei pedir meu atestado.",
                "Se precisar me ausentar, solicito um atestado no canal ❌┃ʀᴇᴍᴏᴠᴇʀ-ᴀᴛᴇsᴛᴀᴅᴏ. Se não cumpri as metas não conseguirei pedir meu atestado.",
                "Se precisar me ausentar, solicito um atestado no canal 📅┃ᴄᴏʟᴏᴄᴀʀ-ᴀᴛᴇsᴛᴀᴅᴏ. Se não cumpri as metas não conseguirei pedir meu atestado."],
     "correta": 2},
    {"pergunta": "Como entrar em serviço corretamente?",
     "opcoes": ["Ao iniciar o trabalho, ativar o comando toogle, entrar na call 🧰 | ᴇᴍ sᴇʀᴠɪçᴏ, colocar o uniforme e entrar na rádio na frequência 66.",
                "Ao iniciar o trabalho, entrar na call 🧰 | ᴇᴍ sᴇʀᴠɪçᴏ, ativar o comando toogle e entrar na rádio na frequência 66.",
                "Ao iniciar o trabalho, colocar o uniforme, entrar na call 🧰 | ᴇᴍ sᴇʀᴠɪçᴏ e ativar o comando toogle."],
     "correta": 0},
    {"pergunta": "Qual o modo correto de uso dos veículos da mecânica a seguir?",
     "opcoes": ["É permitido usar os veículos da Mecânica para uso pessoal, desde que estejam no estacionamento sem uso.",
                "É proibido usar os veículos da Mecânica para uso pessoal, mesmo que estejam no estacionamento sem uso",
                "É proibido usar os veículos da Mecânica para uso pessoal. Se encontrar algum no estacionamento sem uso, guarde-o no Blip."],
     "correta": 2},
    {"pergunta": "Quais os valores do reparo?",
     "opcoes": ["Dentro da Mecânica: R$ 4.000, Fora: R$5,000",
                "Dentro da Mecânica: R$ 8.000, Fora: R$10,000",
                "Dentro da Mecânica: R$ 5.000, Fora: R$4,000"],
     "correta": 0},
    {"pergunta": "Qual a forma correta de desvirar e consertar um carro?",
     "opcoes": ["Mentalizar F9 e procurar no menu a opção desvirar e consertar o carro",
                "Apenas escrever desvirar e consertar no F8 ou /desvirar e /consertar",
                "Escrever consertar no F8"],
     "correta": 1}
]

# Evento para registrar o clique no botão "REALIZAR PROVA"
class ProvaView(View):
    def __init__(self, bot, user):
        super().__init__()
        self.bot = bot
        self.user = user

    @discord.ui.button(label="Realizar Prova", style=discord.ButtonStyle.green)
    async def realizar_prova(self, interaction: discord.Interaction, button: Button):
        await interaction.response.send_message("Iniciando sua prova!", ephemeral=True)
        # Cria um canal temporário para a prova
        overwrites = {
            interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False),
            interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            interaction.guild.get_role(cargo_visualizacao_1_id): discord.PermissionOverwrite(read_messages=True),
            interaction.guild.get_role(cargo_visualizacao_2_id): discord.PermissionOverwrite(read_messages=True),
            interaction.guild.get_role(cargo_prova_id): discord.PermissionOverwrite(read_messages=False)  # Não permite leitura do cargo_prova
        }
        channel = await interaction.guild.create_text_channel(f"prova-{interaction.user.display_name}", overwrites=overwrites)
        await iniciar_prova(interaction.user, channel)

# Função para iniciar a prova
async def iniciar_prova(user, channel):
    respostas = {}
    pontuacao = 0

    for questao in questoes_abertas:
        embed = discord.Embed(title="Questão Aberta", description=f"{questao}", color=discord.Color.light_grey())
        await channel.send(embed=embed)
        try:
            msg = await bot.wait_for('message', timeout=180.0, check=lambda m: m.author == user)
            respostas[questao] = msg.content
        except asyncio.TimeoutError:
            respostas[questao] = "não respondida"
            await channel.send("Tempo esgotado! Você precisará iniciar outra prova.")
            await asyncio.sleep(10)
            await channel.delete()
            return
        await channel.purge(limit=100)

    for questao in questoes_fechadas:
        opcoes_str = "\n".join([f"{i+1}. {opcao}" for i, opcao in enumerate(questao['opcoes'])])
        embed = discord.Embed(title="Questão Fechada", description=f"{questao['pergunta']}\n\n{opcoes_str}", color=discord.Color.light_grey())
        await channel.send(embed=embed)

        class RespostaView(View):
            def __init__(self, bot):
                super().__init__()
                self.bot = bot
                self.resposta_usuario = None

            @discord.ui.select(placeholder="Selecione sua resposta", options=[discord.SelectOption(label=f"Opção {i+1}", description=opcao[:100], value=str(i)) for i, opcao in enumerate(questao['opcoes'])])
            async def select_callback(self, interaction: discord.Interaction, select: Select):
                self.resposta_usuario = int(select.values[0])
                await interaction.response.send_message(f"Você selecionou: {questao['opcoes'][self.resposta_usuario]}", ephemeral=True)
                self.stop()

        view = RespostaView(bot)
        await channel.send("Selecione sua resposta:", view=view)

        try:
            await view.wait()
            respostas[questao['pergunta']] = view.resposta_usuario
            if view.resposta_usuario == questao['correta']:
                pontuacao += 1
        except asyncio.TimeoutError:
            respostas[questao['pergunta']] = "não respondida"
            await channel.send("Tempo esgotado! Você precisará iniciar outra prova.")
            await asyncio.sleep(10)
            await channel.delete()
            return
        await channel.purge(limit=100)

    _corrigir_prova = bot.get_channel(canal_corrigir_prova_id)
    if _corrigir_prova:
        embed = discord.Embed(title="Relatório de Prova", color=discord.Color.light_grey())
        embed.add_field(name="Prova realizada por", value=f"{user.mention} | {user.id}", inline=False)
        embed.add_field(name="Pontuação", value=f"{pontuacao}/{len(questoes_fechadas)}", inline=False)

        for questao in questoes_abertas:
            embed.add_field(name=questao, value=f"R: {respostas.get(questao, 'não respondida')}", inline=False)

        for questao in questoes_fechadas:
            resposta_usuario = respostas.get(questao['pergunta'], "não respondida")
            resposta_correta = questao['opcoes'][questao['correta']]
            resposta_usuario_str = f"{int(resposta_usuario)+1}. {questao['opcoes'][int(resposta_usuario)]}" if resposta_usuario != "não respondida" else "não respondida"
            embed.add_field(name=questao['pergunta'], value=f"Resposta do Usuário: {resposta_usuario_str}\nResposta Correta: {questao['correta']+1}. {resposta_correta}", inline=False)

        embed.set_thumbnail(url="https://media.discordapp.net/attachments/1137047344903372941/1238973673671622666/marvel_gif_2.gif")
        await _corrigir_prova.send(embed=embed)

    await channel.send("Prova concluída! Contate um gerente. O canal será fechado em 10 segundos.")
    await asyncio.sleep(10)
    await channel.delete()

# Função para enviar ou editar a mensagem inicial
async def enviar_ou_editar_mensagem_inicial():
    canal_prova_aluno = bot.get_channel(canal_prova_aluno_id)
    if canal_prova_aluno:
        # Procurar a mensagem inicial anterior
        mensagem_inicial = None
        async for message in canal_prova_aluno.history(limit=10):
            if message.author == bot.user and message.embeds and message.embeds[0].title == "Benny's Originals: Prova":
                mensagem_inicial = message
                break

        embed = discord.Embed(title="Benny's Originals: Prova", description="Você terá 3 minutos para iniciar a prova após clicar no botão.", color=discord.Color.light_grey())
        embed.set_thumbnail(url="https://media.discordapp.net/attachments/1137047344903372941/1238973673671622666/marvel_gif_2.gif")
        embed.set_image(url="https://media.discordapp.net/attachments/1144673895299952700/1225200092634550312/SEJABEMVINDO-ezgif.com-video-to-gif-converter.gif?width=815&height=140")
        embed.set_footer(text="Faça sua parte e se junte a maior mecânica da cidade!")

        view = ProvaView(bot, None)

        if mensagem_inicial:
            await mensagem_inicial.edit(embed=embed, view=view)
        else:
            await canal_prova_aluno.send(embed=embed, view=view)

@tasks.loop(minutes=2)
async def verificar_interacao():
    await enviar_ou_editar_mensagem_inicial()
#-----------------------------------------------------------------FIM PROVA------------------------------------------------------------------

# -------------------------------------------RANKING RELATÓRIOS---------------------------------------------------

async def buscar_mensagem_ranking(canal):
    async for mensagem in canal.history(limit=100):
        if mensagem.author == bot.user and mensagem.embeds and mensagem.embeds[0].title == "👑 Ranking de Relatórios de Tunning Mensal":
            return mensagem
    return None

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
    membros_por_id1 = {membro.id: membro for membro in message.guild.members}

    # Procura por números na mensagem que são IDs inteiros (não partes de outros números)
    for id_match in re.finditer(r"\b\d+\b", message.content):
        user_id = int(id_match.group(0))
        for membro in membros_por_id1.values():
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

    # Obter o horário atual no fuso horário de São Paulo
    current_time = datetime.now(timezone_brasil).strftime('%H:%M:%S')

    # Criar o embed do ranking
    embed = discord.Embed(title="👑 Ranking de Relatórios de Tunning Mensal", description=ranking_str, color=0xffa500)
    embed.set_thumbnail(url=channel.guild.icon.url)
    embed.add_field(name="\u200b", value=f"**📬 Total de relatórios: {sum(relatorios.values())}**", inline=False)
    embed.set_footer(text=f"📅 Desde\n`{data_inicio.strftime('%d %B')}` \n\n ⏰ Última atualização: {current_time}")

    # Editar a mensagem existente ou enviar uma nova
    try:
        if mensagem_ranking:
            # Tentativa de editar a mensagem existente
            await mensagem_ranking.edit(embed=embed)
        else:
            # Enviar uma nova mensagem se mensagem_ranking não existir
            mensagem_ranking = await channel.send(embed=embed)
    except discord.errors.NotFound:
        # Enviar uma nova mensagem se a mensagem existente não for encontrada (foi deletada)
        mensagem_ranking = await channel.send(embed=embed)
    except discord.errors.HTTPException as e:
        print(f"Erro ao atualizar o ranking: {e}")

# Evento para registrar relatórios
@bot.event
async def on_message(message):
    if message.channel.id == 1235035965945413649:  # Canal #relat-tunning
        # Converter a data da mensagem para offset-aware (UTC) e ajustar para o fuso horário de São Paulo
        message_created_at_aware = message.created_at.replace(tzinfo=timezone.utc).astimezone(timezone_brasil)
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
    membros_por_id1 = {membro.id: membro for membro in message.guild.members}

    # Procura por números na mensagem que são IDs inteiros (não partes de outros números)
    for id_match in re.finditer(r"\b\d+\b", message.content):
        user_id = int(id_match.group(0))
        for membro in membros_por_id1.values():
            if str(user_id) == membro.display_name.split()[-1]:  # Verifica se o nome de exibição termina com o ID
                if any(cargo.id in cargos_desejados for cargo in membro.roles):
                    relatorios[membro.id] = relatorios.get(membro.id, 0) - 1
                    if relatorios[membro.id] < 0:
                        relatorios[membro.id] = 0  # Garante que a contagem não seja negativa
                    print(f"Relatório removido: {membro.display_name} agora tem {relatorios[membro.id]} relatórios")
                break
        else:
            print(f"Erro: ID {user_id} não encontrado na lista de membros.")  # Mensagem de erro para ID não encontrado

    await exibir_ranking()  # Atualiza o ranking imediatamente

# RANKING RELATÓRIOS SEMANAL

async def buscar_mensagem_ranking_smnl(canal):
    async for mensagem in canal.history(limit=100):
        if mensagem.author == bot.user and mensagem.embeds and mensagem.embeds[0].title == "👑 Ranking de Relatórios de Tunning Semanal":
            return mensagem
    return None

async def carregar_relatorios_antigos(channel):
    global relatorios_smnl
    print(f"Carregando relatórios antigos entre {data_inicio_semanal} e {data_fim_semanal}...")
    async for message in channel.history(after=data_inicio_semanal, before=data_fim_semanal, limit=None):  # Busca todas as mensagens dentro do período
        print(f"Processando mensagem antiga: {message.content}")
        await processar_relatorio(message, atualizacao_antiga=True)
    print("Carregamento de relatórios antigos concluído.")

# Função para processar um relatório (novo ou antigo)
async def processar_relatorio(message, atualizacao_antiga=False):
    global relatorios_smnl

    # Criar dicionário de membros por ID (uma vez, no início da função)
    membros_por_id1 = {membro.id: membro for membro in message.guild.members}

    # Procura por números na mensagem que são IDs inteiros (não partes de outros números)
    for id_match in re.finditer(r"\b\d+\b", message.content):
        user_id = int(id_match.group(0))
        for membro in membros_por_id1.values():
            if str(user_id) == membro.display_name.split()[-1]:  # Verifica se o nome de exibição termina com o ID
                if any(cargo.id in cargos_desejados for cargo in membro.roles):
                    relatorios_smnl[membro.id] = relatorios_smnl.get(membro.id, 0) + 1
                    print(f"Relatório adicionado: {membro.display_name} agora tem {relatorios_smnl[membro.id]} relatórios")
                break
        else:
            print(f"Erro: ID {user_id} não encontrado na lista de membros.")  # Mensagem de erro para ID não encontrado

    if not atualizacao_antiga:
        await exibir_ranking()  # Atualiza o ranking imediatamente se não for uma atualização antiga

# Função para atualizar o ranking
async def exibir_ranking():
    global relatorios_smnl
    global mensagem_ranking_smnl

    # Buscar o canal correto para o ranking
    channel = bot.get_channel(canal_ranking_semanal_id)

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
    membros_validos.sort(key=lambda membro: relatorios_smnl.get(membro.id, 0), reverse=True)

    # Criar o ranking em formato de texto
    ranking_str = ""
    for i, membro in enumerate(membros_validos, start=1):
        posicao = "🏆`º`" if i == 1 else f"`{i}º`"
        total_relatorios_smnl = relatorios_smnl.get(membro.id, 0)  # Obter o total de relatórios do membro
        ranking_str += f"{posicao} - {membro.mention}: {total_relatorios_smnl} relatórios\n"

    # Obter o horário atual no fuso horário de São Paulo
    current_time = datetime.now(timezone_brasil).strftime('%H:%M:%S')

    # Criar o embed do ranking
    embed = discord.Embed(title="👑 Ranking de Relatórios de Tunning\n", description=ranking_str, color=0xffa500)
    embed.set_thumbnail(url=channel.guild.icon.url)
    embed.add_field(name="\u200b", value=f"**📬 Total de relatórios: {sum(relatorios_smnl.values())}**", inline=False)
    embed.set_footer(text=f"📅 De `{data_inicio_semanal.strftime('%d %B')}` a `{data_fim_semanal.strftime('%d %B')}` \n\n ⏰ Última atualização: {current_time}")

    # Editar a mensagem existente ou enviar uma nova
    try:
        if mensagem_ranking_smnl:
            # Tentativa de editar a mensagem existente
            await mensagem_ranking_smnl.edit(embed=embed)
        else:
            # Enviar uma nova mensagem se mensagem_ranking_smnl não existir
            mensagem_ranking_smnl = await channel.send(embed=embed)
    except discord.errors.NotFound:
        # Enviar uma nova mensagem se a mensagem existente não for encontrada (foi deletada)
        mensagem_ranking_smnl = await channel.send(embed=embed)
    except discord.errors.HTTPException as e:
        print(f"Erro ao atualizar o ranking: {e}")

# Evento para registrar relatórios
@bot.event
async def on_message(message):
    if message.channel.id == 1235035965945413649:  # Canal #relat-tunning
        # Converter a data da mensagem para offset-aware (UTC) e ajustar para o fuso horário de São Paulo
        message_created_at_aware = message.created_at.replace(tzinfo=timezone.utc).astimezone(timezone_brasil)
        if data_inicio_semanal <= message_created_at_aware < data_fim_semanal:
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
    global relatorios_smnl

    # Criar dicionário de membros por ID (uma vez, no início da função)
    membros_por_id1 = {membro.id: membro for membro in message.guild.members}

    # Procura por números na mensagem que são IDs inteiros (não partes de outros números)
    for id_match in re.finditer(r"\b\d+\b", message.content):
        user_id = int(id_match.group(0))
        for membro in membros_por_id1.values():
            if str(user_id) == membro.display_name.split()[-1]:  # Verifica se o nome de exibição termina com o ID
                if any(cargo.id in cargos_desejados for cargo in membro.roles):
                    relatorios_smnl[membro.id] = relatorios_smnl.get(membro.id, 0) - 1
                    if relatorios_smnl[membro.id] < 0:
                        relatorios_smnl[membro.id] = 0  # Garante que a contagem não seja negativa
                    print(f"Relatório removido: {membro.display_name} agora tem {relatorios_smnl[membro.id]} relatórios")
                break
        else:
            print(f"Erro: ID {user_id} não encontrado na lista de membros.")  # Mensagem de erro para ID não encontrado

    await exibir_ranking()  # Atualiza o ranking imediatamente

@bot.event
async def on_ready():
    # Carregar relatórios antigos e exibir o ranking inicial
    try:
        canal_relatorios = bot.get_channel(1235035965945413649)  # Canal #relat-tunning
        if canal_relatorios:
            await bot.wait_until_ready()  # Esperar o bot estar pronto
            await carregar_relatorios_antigos(canal_relatorios)  # Carregar relatórios antigos
            await exibir_ranking()  # Exibir o ranking inicial
    except discord.errors.NotFound:
        print("Erro: Canal de relatórios não encontrado.")
    except discord.errors.Forbidden:
        print("Erro: O bot não tem permissão para ler o histórico de mensagens do canal.")
    
    # Buscar canais necessários
    channel_ranking_semanal = bot.get_channel(canal_ranking_semanal_id)

        # Criar um dicionário de membros por ID
    global membros_por_id
    membros_por_id = {membro.id: membro for membro in bot.get_all_members()}

# ------------------------------------------------------------------------------FIM RANK RELATÓRIOS---------------------------------------
# Tarefa para salvar dados periodicamente
@tasks.loop(minutes=5)  # Ajuste o intervalo conforme necessário
async def salvar_dados():
    with open(relatorios_path, 'w') as f:
        json.dump(relatorios, f)

# Evento para registrar saídas de membros
@bot.event
async def on_member_remove(member):
    guild = member.guild
    channel_id = 1235035965391765566  # Substitua pelo ID do seu canal

    embed = discord.Embed(title="Um membro saiu!", color=discord.Color.red())
    embed.set_thumbnail(url=member.display_avatar.url)

    embed.add_field(name="DISCORD:", value=member.mention, inline=False)
    embed.add_field(name="ID DISCORD:", value=member.id, inline=False)
    embed.add_field(name="Nome:", value=member.display_name, inline=False)  # Usa o nickname

    roles = ", ".join([role.name for role in member.roles if role.name != '@everyone'])
    embed.add_field(name="Cargos Antes da Saída:", value=roles, inline=False)

    embed.set_footer(text=f"{member.guild.name}")

    channel = guild.get_channel(channel_id)
    if channel:
        await channel.send(embed=embed)

# Função para verificar se o guild está em cooldown
def is_rate_limited(guild_id):
    current_time = time.time()
    last_time = last_update_time.get(guild_id, 0)
    
    if current_time - last_time < cooldown_interval:
        return True, cooldown_interval - (current_time - last_time)
    
    last_update_time[guild_id] = current_time
    return False, None

# Função para construir a hierarquia de devedores
async def build_hierarchy(guild):
    embed = discord.Embed(
        title="⛔ Hierarquia: Devedores",
        color=discord.Color.dark_red()
    )
    embed.set_thumbnail(url=thumbnail_url)

    for role_name, role_id in roles_ids.items():
        role = get(guild.roles, id=role_id)
        members_with_role = role.members
        member_mentions = "\n".join([member.mention for member in members_with_role])
        embed.add_field(name=f"{role.name}: ```{len(members_with_role)}```", value=member_mentions if member_mentions else "\n", inline=False)

    return embed

# Função para encontrar a mensagem existente
async def find_existing_message(channel):
    async for message in channel.history(limit=100):
        if message.author == bot.user and message.embeds:
            embed = message.embeds[0]
            if embed.title == "⛔ Hierarquia: Devedores":
                return message
    return None

# Evento on_member_update para atualizar a hierarquia dinamicamente
@bot.event
async def on_member_update(before, after):
    global hierarchy_message_id_devedores
    guild = after.guild
    channel = bot.get_channel(channel_id_devedores)
    
    # Verifica o cooldown para o servidor
    rate_limited, retry_after = is_rate_limited(guild.id)
    if rate_limited:
        print(f"Rate limited! Waiting {retry_after:.2f} seconds before next attempt.")
        return
    
    if before.roles != after.roles:
        embed = await build_hierarchy(guild)

        # Buscar mensagem existente e atualizar somente se o conteúdo mudou
        if hierarchy_message_id_devedores is not None:
            try:
                message = await channel.fetch_message(hierarchy_message_id_devedores)
                if message.embeds[0].to_dict() != embed.to_dict():  # Verifica se o conteúdo realmente mudou
                    await message.edit(embed=embed)
            except discord.errors.NotFound:
                message = await channel.send(embed=embed)
                hierarchy_message_id_devedores = message.id
        else:
            message = await find_existing_message(channel)
            if message:
                hierarchy_message_id_devedores = message.id
                await message.edit(embed=embed)
            else:
                message = await channel.send(embed=embed)
                hierarchy_message_id_devedores = message.id

    #~~~~~~~~~~~~~~~~~~~~---------------------------BOT DE HORAS-----------------------------~~~~~~~~~~~~~~~~~~~~

def create_table():
    conn = sqlite3.connect('horas_servico.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS horas_servico (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    user_name TEXT,
                    canal_id INTEGER,
                    tempo_servico INTEGER,
                    data_inicio TIMESTAMP,
                    data_fim TIMESTAMP)''')
    conn.commit()
    conn.close()

def salvar_dados_em_arquivo():
    conn = sqlite3.connect('horas_servico.db')
    c = conn.cursor()
    c.execute('SELECT * FROM horas_servico')
    registros = c.fetchall()
    conn.close()

    with open('backup_horas_servico.json', 'w') as f:
        json.dump(registros, f)

@tasks.loop(minutes=1)
async def atualizar_horas_servico():
    conn = sqlite3.connect('horas_servico.db')
    c = conn.cursor()
    for guild in bot.guilds:
        for canal_id in canais_voz_ids:
            canal = guild.get_channel(canal_id)
            if canal:
                for membro in canal.members:
                    c.execute('SELECT * FROM horas_servico WHERE user_id=? AND canal_id=? AND data_fim IS NULL', (membro.id, canal_id))
                    registro = c.fetchone()
                    if registro:
                        tempo_servico = int((datetime.now(timezone.utc) - datetime.fromisoformat(registro[5]).replace(tzinfo=timezone.utc)).total_seconds())
                        c.execute('UPDATE horas_servico SET tempo_servico=? WHERE id=?', (tempo_servico, registro[0]))
                    else:
                        c.execute('INSERT INTO horas_servico (user_id, user_name, canal_id, tempo_servico, data_inicio) VALUES (?, ?, ?, ?, ?)', 
                                  (membro.id, str(membro), canal_id, 0, datetime.now(timezone.utc).isoformat()))
                    conn.commit()
    conn.close()

def calcular_tempo_servico(user_id):
    conn = sqlite3.connect('horas_servico.db')
    c = conn.cursor()
    c.execute('SELECT SUM(tempo_servico) FROM horas_servico WHERE user_id=?', (user_id,))
    tempo_total = c.fetchone()[0]
    conn.close()
    return tempo_total if tempo_total else 0

def calcular_posicao_ranking(user_id):
    conn = sqlite3.connect('horas_servico.db')
    c = conn.cursor()
    c.execute('SELECT user_id, SUM(tempo_servico) as total_tempo FROM horas_servico GROUP BY user_id ORDER BY total_tempo DESC')
    ranking = c.fetchall()
    conn.close()
    for posicao, (id_usuario, tempo_total) in enumerate(ranking, start=1):
        if id_usuario == user_id:
            return posicao
    return None

def formatar_tempo(segundos):
    horas = segundos // 3600
    minutos = (segundos % 3600) // 60
    segundos = segundos % 60
    return f"{horas}h {minutos}m {segundos}s"

# Botões de consulta de horas e ranking
class ConsultaView(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="⏰ CONSULTAR HORAS", style=discord.ButtonStyle.primary)
    async def consultar_horas(self, interaction: discord.Interaction, button: Button):
        user_id = interaction.user.id
        tempo_total = calcular_tempo_servico(user_id)
        ranking = calcular_posicao_ranking(user_id)
        tempo_formatado = formatar_tempo(tempo_total)
        
        embed = discord.Embed(title="⏰ | Consulta horas - 🛠️・Benny's - Originals", color=discord.Color.orange())
        embed.description = (
            f"🪪 **Usuário:** {interaction.user.mention}\n"
            f"⏰ **Tempo Total:** `{tempo_formatado}`\n"
            f"🔌 **Conectado Agora:** {'`Sim`' if interaction.user.voice else '`Não Conectado!`'}\n"
            f"📊 **Posição no ranking:** {'`#`' + str(ranking) if ranking else '`N/A`'}\n\n"
        )
        embed.set_footer(text="© Copyright |🛠・Benny's - Originals")
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @discord.ui.button(label="📊 CONSULTAR RANKING", style=discord.ButtonStyle.primary)
    async def consultar_ranking(self, interaction: discord.Interaction, button: Button):
        conn = sqlite3.connect('horas_servico.db')
        c = conn.cursor()
        c.execute('SELECT user_id, SUM(tempo_servico) as total_tempo FROM horas_servico GROUP BY user_id ORDER BY total_tempo DESC LIMIT 15')
        top_15 = c.fetchall()
        conn.close()
        
        ranking_str = "⏰ | Rank Top 15 - 🛠️・Benny's - Originals\n\n"
        for idx, (user_id, tempo_total) in enumerate(top_15, start=1):
            user = interaction.guild.get_member(user_id)
            tempo_formatado = formatar_tempo(tempo_total)
            ranking_str += f"`{idx}`. {user.mention}: **{tempo_formatado}**\n"
        
        embed = discord.Embed(description=ranking_str, color=discord.Color.orange())
        embed.set_footer(text="© Copyright |🛠・Benny's - Originals")
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

async def buscar_mensagem_consulta(canal):
    async for mensagem in canal.history(limit=100):
        if mensagem.author == bot.user and "Consulta horas" in mensagem.embeds[0].title:
            return mensagem
    return None

# Início da mensagem de consulta
async def enviar_mensagem_consulta():
    channel = bot.get_channel(consultar_horas_id)
    embed = discord.Embed(title="⏰ | Consulta horas - 🛠️・Benny's - Originals", color=discord.Color.orange())
    embed.description = (
        "Para consultar as horas basta clicar no botão abaixo \"CONSULTAR HORAS\".\n\n"
        "⏰ **Consulta** horas Totais.\n"
        "📊 **Consulta** sua posição no ranking.\n"
        "📊 **Consulta** Top 15 em horas.\n\n"
    )
    embed.set_footer(text="© Copyright |🛠・Benny's - Originals")
    
    view = ConsultaView()

    # Buscar a mensagem existente ou enviar uma nova
    mensagem_consulta = await buscar_mensagem_consulta(channel)
    if mensagem_consulta:
        await mensagem_consulta.edit(embed=embed, view=view)
    else:
        await channel.send(embed=embed, view=view)

@tasks.loop(minutes=10)
async def salvar_dados():
    salvar_dados_em_arquivo()

def carregar_dados_de_arquivo():
    try:
        with open('backup_horas_servico.json', 'r') as f:
            registros = json.load(f)

        conn = sqlite3.connect('horas_servico.db')
        c = conn.cursor()
        c.executemany('INSERT OR REPLACE INTO horas_servico VALUES (?, ?, ?, ?, ?, ?, ?)', registros)
        conn.commit()
        conn.close()
    except FileNotFoundError:
        print("Nenhum backup encontrado. Iniciando sem dados de backup.")

# Função para atualizar CANAL DA HIERARQUIA
async def atualizar_hierarquia(guild):
    global mensagem_hierarquia

    hierarquia_str = ""
    
    # Construindo a string da hierarquia
    for role_id, role_name in roles_hierarchy.items():
        role = guild.get_role(role_id)
        if role:
            members = [member.mention for member in role.members]
            if members:
                hierarquia_str += f"# <@&{role_id}>\n"  # Usando menção real ao cargo
                hierarquia_str += "\n".join(members)
                hierarquia_str += "\n\n"  # Espaço entre os cargos
    
    # Encontrar o canal de hierarquia
    channel = guild.get_channel(canal_hierarquia_id)
    
    if not channel:
        print("Erro: Canal de hierarquia não encontrado.")
        return
    
    # Se já existir uma mensagem, edite-a, senão, envie uma nova mensagem
    if mensagem_hierarquia:
        try:
            await mensagem_hierarquia.edit(content=hierarquia_str)
        except discord.errors.NotFound:
            mensagem_hierarquia = await channel.send(hierarquia_str)
    else:
        mensagem_hierarquia = await channel.send(hierarquia_str)

# Eventos para monitorar mudanças de cargo
@bot.event
async def on_member_update(before, after):
    if before.roles != after.roles:  # Se os cargos mudaram
        await atualizar_hierarquia(after.guild)

@bot.event
async def on_guild_role_update(before, after):
    await atualizar_hierarquia(before.guild)

# Evento on_ready para enviar a prova, a mensagem inicial da hierarquia, carregar comandos slash e o bot de horas
@bot.event
async def on_ready():
    #canal hierarquia
    guild = bot.guilds[0]  # Supondo que o bot esteja em um único servidor
    await atualizar_hierarquia(guild)

    # Criar a tabela no banco de dados
    create_table()

    # Sincronizar os comandos do bot
    await bot.tree.sync()

    # Enviar a mensagem inicial de consulta de horas
    await enviar_mensagem_consulta()

    # Iniciar tarefas de atualização de horas e salvamento de dados
    if not atualizar_horas_servico.is_running():
        atualizar_horas_servico.start()
    if not salvar_dados.is_running():
        salvar_dados.start()

    # Carregar dados de arquivo
    carregar_dados_de_arquivo()

    #CANAL ~~DEVEDORES
    global hierarchy_message_id_devedores
    guild = bot.guilds[0]
    channel = bot.get_channel(channel_id_devedores)
    
    try:
        await bot.tree.sync()
        print("Sincronização de comandos concluída.")
    except Exception as e:
        print(f"Erro ao sincronizar comandos: {e}")

    embed = await build_hierarchy(guild)

    # Procurar por mensagem existente no canal
    message = await find_existing_message(channel)
    if message:
        hierarchy_message_id_devedores = message.id
        await message.edit(embed=embed)
    else:
        message = await channel.send(embed=embed)
        hierarchy_message_id_devedores = message.id

    # Criar um dicionário de membros por ID ~~RANKING
    global membros_por_id
    membros_por_id = {membro.id: membro for membro in bot.get_all_members()}

    # Carregar relatórios antigos e exibir o ranking inicial
    try:
        canal_relatorios = bot.get_channel(1235035965945413649)  # Canal #relat-tunning
        if canal_relatorios:
            await bot.wait_until_ready()  # Esperar o bot estar pronto
            await carregar_relatorios_antigos(canal_relatorios)  # Carregar relatórios antigos
            await exibir_ranking()  # Exibir o ranking inicial
    except discord.errors.NotFound:
        print("Erro: Canal de relatórios não encontrado.")
    except discord.errors.Forbidden:
        print("Erro: O bot não tem permissão para ler o histórico de mensagens do canal.")
    
    # Enviar ou editar a mensagem inicial (relacionada à hierarquia ou outra funcionalidade)
    await enviar_ou_editar_mensagem_inicial()

    # Iniciar a verificação de interação
    if not verificar_interacao.is_running():
        verificar_interacao.start()

    print(f'Bot conectado como {bot.user}')
    
load_dotenv()
# Rodar o bot com o token do ambiente
bot.run(os.getenv("DISCORD_TOKEN"))
update_hierarchy.start()
