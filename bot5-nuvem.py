import discord
from discord.ext import commands, tasks
from discord import Embed, app_commands
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
from typing import List

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
canal_log_exoneracao_id = 1249236243448070306  # Canal onde o log será enviado


# IDs dos cargos que você deseja incluir no ranking
cargos_desejados = [
    1235035964573880397, 1235035964573880398, 1235035964556972094,
    1235035964599042090, 1235035964599042091, 1235035964599042094,
    1235035964599042095
]

# Data de início e fim da contagem ~~MENSAL~~
data_inicio = datetime(2024, 11, 1, tzinfo=timezone.utc)  # Define a data de início com fuso horário UTC
data_fim = datetime(2024, 12, 1, tzinfo=timezone.utc)     # Define a data de fim com fuso horário UTC

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

# IDs dos cargos com permissão
cargos_permitidos = [1235035964556972099, 1235035964556972095]

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

# IDs dos cargos e canais
CARGO_IDS = {
    "ADV1": 1235035964556972100,
    "ADV2": 1235035964556972101,
    "ADV3": 1235035964573880390,
    "ADV4": 1255195989778628739,
    "REBAIXADO": 1235035964556972097,
    "DEVEDOR_MANUTENCAO": 1255196288698552321,
    "DEVEDOR_ADV": 1255196379609825350,
    "EXONERADO": 1235035964556972093
}

# ID do canal "devedores"
CANAL_DEVEDORES_ID = 1255178131707265066

# IDs dos cargos de advertência
CARGOS_ADVERTENCIA = {
    "devedor adv": 1255196379609825350,
    "devedor man": 1255196288698552321,
    "adv4": 1255195989778628739,
    "adv3": 1235035964573880390,
    "adv2": 1235035964556972101,
    "adv1": 1235035964556972100,
    "adv verbal": 1235035964556972098,
    "rebaixado": 1235035964556972097
}

# ID do canal de log de advertências
CANAL_LOG_ADVERTENCIA_ID = 1303200083772440577

#_______________________________________________________________________________

# fim variáveis, inicio bot de comandos

# Comando /adv
@bot.tree.command(name="adv", description="Adicionar advertência(s) a um ou mais usuários.")
@app_commands.describe(
    ids="IDs dos usuários, separados por vírgula", 
    advs="Tipos de advertência (ex.: adv1, devedor adv, devedor manutenção)", 
    motivo="Motivo da advertência"
)
@app_commands.checks.has_any_role(cargo_visualizacao_1_id, cargo_visualizacao_2_id)  # IDs de cargos autorizados
async def adv(interaction: discord.Interaction, ids: str, advs: str, motivo: str):
    try:
        # Convertendo IDs e tipos de advertência para listas
        ids = [int(id.strip()) for id in ids.split(",")]
        advs = [adv.strip().lower() for adv in advs.split(",")]

        guild = interaction.guild
        autor = interaction.user.mention  # Quem aplicou a advertência

        # Validar os tipos de advertência fornecidos
        cargos_adicionar = [CARGOS_ADVERTENCIA[adv] for adv in advs if adv in CARGOS_ADVERTENCIA]
        
        if not cargos_adicionar:
            await interaction.response.send_message("Nenhum tipo de advertência válido foi especificado.", ephemeral=True)
            return

        # Canal de log
        canal_log = guild.get_channel(CANAL_LOG_ADVERTENCIA_ID)

        # Processar cada ID de usuário
        for id_usuario in ids:
            membro = guild.get_member(id_usuario)
            if not membro:
                await interaction.response.send_message(f"Usuário com ID {id_usuario} não encontrado.", ephemeral=True)
                continue

            # Adicionar os cargos de advertência
            cargos_atuais = []
            for cargo_id in cargos_adicionar:
                cargo = guild.get_role(cargo_id)
                if cargo:
                    await membro.add_roles(cargo)
                    cargos_atuais.append(cargo.name)

            # Criar embed de log
            embed_advertencia = Embed(title="Advertência 🚨", color=0xFF0000)
            embed_advertencia.add_field(name="Quem aplicou", value=autor, inline=False)
            embed_advertencia.add_field(name="Advertido", value=membro.mention, inline=False)
            embed_advertencia.add_field(name="Nome", value=membro.display_name, inline=False)
            embed_advertencia.add_field(name="Tipo de Advertência", value=", ".join(cargos_atuais), inline=False)
            embed_advertencia.add_field(name="Motivo", value=motivo, inline=False)

            # Enviar log para o canal de advertências e mensagem privada para o usuário advertido
            if canal_log:
                await canal_log.send(embed=embed_advertencia)

            try:
                await membro.send(embed=embed_advertencia)
            except discord.Forbidden:
                print(f"Não foi possível enviar mensagem para {membro.display_name} ({membro.id}) no privado.")

        await interaction.response.send_message("Advertência(s) aplicada(s) com sucesso!", ephemeral=True)

    except Exception as e:
        print(f"Ocorreu um erro: {e}")
        await interaction.response.send_message("Ocorreu um erro ao tentar executar este comando.", ephemeral=True)

@adv.error
async def adv_error(interaction: discord.Interaction, error):
    if isinstance(error, app_commands.MissingAnyRole):
        await interaction.response.send_message("Você não tem permissão para usar este comando.", ephemeral=True)
    else:
        await interaction.response.send_message("Ocorreu um erro ao tentar executar este comando.", ephemeral=True)
        print(f"Erro no comando /adv: {error}")

#consultarelat
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

# Função de verificação de autorização
def check_authorized_roles():
    async def predicate(interaction: discord.Interaction):
        return any(role.id in [123456, 654321] for role in interaction.user.roles)  # IDs de cargos autorizados
    return app_commands.check(predicate)

# Comando /mensagem
@bot.tree.command(name="mensagem", description="Enviar mensagem privada para todos os membros de um cargo.")
@app_commands.describe(cargo="Cargo alvo", mensagem="Mensagem a ser enviada")
@check_authorized_roles()
async def mensagem(interaction: discord.Interaction, cargo: discord.Role, mensagem: str):
    log_channel = bot.get_channel(LOG_CHANNEL_ID)
    await interaction.response.send_message(f'Enviando mensagens para todos os membros com o cargo {cargo.mention}.', ephemeral=True)
    
    # Enviar a mensagem privada para cada membro com o cargo
    for member in cargo.members:
        try:
            await member.send(mensagem)
        except discord.Forbidden:
            await log_channel.send(f'Não foi possível enviar a mensagem para {member.mention}.')
    
    # Registrar o log no canal
    await log_channel.send(
        f'Usuário {interaction.user.mention} enviou a seguinte mensagem para o cargo {cargo.mention}:\n```\n{mensagem}\n```'
    )

# Tratamento de erros específico para o comando /mensagem
@mensagem.error
async def mensagem_error(interaction: discord.Interaction, error):
    if isinstance(error, app_commands.MissingPermissions):
        await interaction.response.send_message("Você não tem permissão para usar este comando.", ephemeral=True)
    else:
        await interaction.response.send_message("Ocorreu um erro ao tentar executar este comando.", ephemeral=True)
        print(f"Erro no comando /mensagem: {error}")

# Comando /dm
@bot.tree.command(name="dm", description="Enviar mensagem privada para um usuário específico.")
@app_commands.describe(user="Usuário alvo", mensagem="Mensagem a ser enviada")
@check_authorized_roles()
async def dm(interaction: discord.Interaction, user: discord.User, mensagem: str):
    log_channel = bot.get_channel(LOG_CHANNEL_ID)
    try:
        await user.send(mensagem)
        await interaction.response.send_message(f'Mensagem enviada para {user.mention}.', ephemeral=True)
        
        # Log da mensagem no canal especificado
        if log_channel:
            await log_channel.send(
                f'Usuário {interaction.user.mention} enviou a seguinte mensagem para {user.mention}:\n```\n{mensagem}\n```'
            )
    except discord.Forbidden:
        await interaction.response.send_message(f'Não foi possível enviar a mensagem para {user.mention}.', ephemeral=True)

# Tratamento de erros do comando /dm
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

                # Criar o embed de contratação com a cor verde
                embed_contratacao = discord.Embed(
                    title="🔨 ┃ CONTRATAÇÃO ┃ 🔨",
                    color=discord.Color.green()  # Verde
                )
                embed_contratacao.add_field(name="NOME", value=nome_contratado, inline=False)
                embed_contratacao.add_field(name="ID", value=id_cidade, inline=False)
                embed_contratacao.add_field(name="DISCORD", value=contratado.mention, inline=False)
                embed_contratacao.add_field(name="RECRUTADOR", value=recrutador_mention, inline=False)
                embed_contratacao.add_field(name="ID RECRUTADOR", value=f"({recrutador_id})", inline=False)
                embed_contratacao.add_field(name="DATA DE INÍCIO DE CONTRATO", value=data_inicio, inline=False)
                embed_contratacao.add_field(name="DATA DE PERÍODO DE EXP", value=data_exp, inline=False)

                # Enviar o embed no canal de log
                await canal_log.send(embed=embed_contratacao)
                await interaction.response.send_message(f"Usuário {contratado.mention} contratado com sucesso!", ephemeral=True)
            except discord.errors.Forbidden:
                await interaction.response.send_message("Permissões insuficientes para editar o usuário ou adicionar/remover cargos.", ephemeral=True)
        else:
            await interaction.response.send_message("Usuário não encontrado.", ephemeral=True)
    except Exception as e:
        print(f"Ocorreu um erro: {e}")
        await interaction.response.send_message("Ocorreu um erro ao tentar executar este comando.", ephemeral=True)

# Tratamento de erros específico para o comando /contratar
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

        # Definir os cargos
        cargo_estagiario = guild.get_role(cargo_estagiario_id)
        cargo_mecanico = guild.get_role(cargo_mecanico_id)

        # Armazenar os nomes dos cargos
        cargo_estagiario_name = cargo_estagiario.name
        cargo_mecanico_name = cargo_mecanico.name

        if promovido:
            nome_contratado = promovido.display_name.split("・")[1].split(" | ")[0]
            id_cidade = promovido.display_name.split(" | ")[1]
            novo_nome = f"🔧・{nome_contratado} | {id_cidade}"

            try:
                await promovido.edit(nick=novo_nome)
                await promovido.add_roles(
                    cargo_mecanico,
                    guild.get_role(cargo2_id)  # Mantém o cargo de funcionário
                )
                await promovido.remove_roles(cargo_estagiario)

                canal_log = guild.get_channel(canal_log_promocao_id)

                # Criar o embed de promoção com a cor azul claro
                embed_promocao = discord.Embed(
                    title="⏫ ┃ PROMOÇÃO DE CARGO ┃ ⏫",
                    color=discord.Color.from_str("#00bfff")  # Azul claro
                )
                embed_promocao.add_field(name="Cargo Anterior", value=cargo_estagiario_name, inline=False)
                embed_promocao.add_field(name="Cargo Atual", value=cargo_mecanico_name, inline=False)
                embed_promocao.add_field(name="Promovido Por", value=promotor_mention, inline=False)
                embed_promocao.add_field(name="ID de Quem Promoveu", value=f"({promotor_id})", inline=False)
                embed_promocao.add_field(name="Promovido", value=promovido.mention, inline=False)

                # Enviar o embed no canal de log
                await canal_log.send(embed=embed_promocao)
                await interaction.response.send_message(f"Usuário {promovido.mention} promovido com sucesso!", ephemeral=True)
            except discord.errors.Forbidden:
                await interaction.response.send_message("Permissões insuficientes para editar o usuário ou adicionar/remover cargos.", ephemeral=True)
        else:
            await interaction.response.send_message("Usuário não encontrado.", ephemeral=True)
    except Exception as e:
        print(f"Ocorreu um erro: {e}")
        await interaction.response.send_message("Ocorreu um erro ao tentar executar este comando.", ephemeral=True)

# Tratamento de erros específico para o comando /promover
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
@app_commands.describe(ids="IDs ou menções dos usuários a serem exonerados, separados por vírgula", motivo="Motivo da exoneração")
@app_commands.checks.has_any_role(cargo_visualizacao_1_id, cargo_visualizacao_2_id)
async def exonerar(interaction: discord.Interaction, ids: str, motivo: str):
    try:
        guild = interaction.guild
        cargo_exonerado = guild.get_role(cargo_exonerado_id)
        executor = interaction.user.mention

        ids_discord = []
        for id_str in ids.split(","):
            id_str = id_str.strip()
            if id_str.startswith("<@") and id_str.endswith(">"):
                ids_discord.append(int(id_str[3:-1].replace("!", "")))  # Extrai o ID do usuário da menção
            else:
                ids_discord.append(int(id_str))  # Converte para int se for um ID direto

        for id_discord in ids_discord:
            membro = guild.get_member(id_discord)
            if membro:
                # Ajustar o nome de exibição do membro exonerado
                if "・" in membro.display_name and " | " in membro.display_name:
                    nome_contratado = membro.display_name.split("・")[1].split(" | ")[0]
                    id_cidade = membro.display_name.split(" | ")[1]
                    novo_nome = f"[EX]・{nome_contratado} | {id_cidade}"
                else:
                    novo_nome = f"[EX]・{membro.display_name}"

                # Remover todos os cargos e adicionar o cargo exonerado
                await membro.edit(roles=[cargo_exonerado], nick=novo_nome)

                # Criar embed para a mensagem de exoneração
                embed = discord.Embed(title="Exoneração 🚨", color=discord.Color.red())
                embed.add_field(name="Quem exonerou:", value=executor, inline=False)
                embed.add_field(name="Exonerado:", value=membro.mention, inline=False)
                embed.add_field(name="Nome:", value=membro.display_name, inline=False)
                embed.add_field(name="Motivo:", value=motivo, inline=False)

                # Enviar embed no privado do usuário exonerado
                try:
                    await membro.send(embed=embed)
                except discord.Forbidden:
                    print(f"Não foi possível enviar mensagem para {membro.display_name} ({membro.id}) no privado.")

                # Enviar embed de log no canal específico
                canal_log = guild.get_channel(1249236243448070306)
                if canal_log:
                    await canal_log.send(embed=embed)

        await interaction.response.send_message("Usuários exonerados com sucesso.", ephemeral=True)

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
    {"pergunta": "Qual a forma correta de desvirar e reparar um carro?",
     "opcoes": ["Mentalizar F9 e procurar no menu a opção desvirar e reparar o carro",
                "Apenas escrever desvirar e reparar no F8 ou /desvirar e /reparar",
                "Escrever reparar no F8"],
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

#-----------------------------------------------------------------FIM PROVA---------------------------------------
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
                    # Subtrair 1 do total de relatórios
                    if membro.id in relatorios:
                        relatorios[membro.id] = max(relatorios.get(membro.id, 0) - 1, 0)
                        print(f"Relatório removido: {membro.display_name} agora tem {relatorios.get(membro.id, 0)} relatórios")
                break
        else:
            print(f"Erro: ID {user_id} não encontrado na lista de membros.")  # Mensagem de erro para ID não encontrado

    # Atualiza o ranking imediatamente
    await exibir_ranking()

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

# Função para buscar a mensagem de hierarquia existente no canal
async def buscar_mensagem_hierarquia(channel):
    async for mensagem in channel.history(limit=100):
        if mensagem.author == bot.user and mensagem.content.startswith("# <@&"):
            return mensagem
    return None

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

    # Buscar a mensagem existente, se ainda não foi armazenada
    if not mensagem_hierarquia:
        mensagem_hierarquia = await buscar_mensagem_hierarquia(channel)

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

# Função para atualizar a embed
async def atualizar_embed_devedores(guild):
    canal = bot.get_channel(CANAL_DEVEDORES_ID)
    if canal is None:
        print("Canal de devedores não encontrado.")
        return

    embed = discord.Embed(title="Hierarquia: Devedores", color=discord.Color.red())
    
    # Montando a hierarquia com base nos cargos
    for cargo_nome, cargo_id in CARGO_IDS.items():
        cargo = guild.get_role(cargo_id)
        if cargo is None:
            continue
        
        membros_com_cargo = [membro.mention for membro in guild.members if cargo in membro.roles]
        membros_texto = '\n'.join(membros_com_cargo) if membros_com_cargo else "0"
        
        embed.add_field(name=f"{cargo.name}:", value=membros_texto, inline=False)
    
    # Editar ou enviar a mensagem no canal
    mensagem_existente = None
    async for mensagem in canal.history(limit=100):
        if mensagem.author == bot.user and mensagem.embeds:
            mensagem_existente = mensagem
            break
    
    if mensagem_existente:
        await mensagem_existente.edit(embed=embed)
    else:
        await canal.send(embed=embed)

# Evento para atualizar a hierarquia quando o membro receber ou perder um cargo
@bot.event
async def on_member_update(before, after):
    # Verificar se algum cargo relacionado foi adicionado ou removido
    cargos_anteriores = set(before.roles)
    cargos_atualizados = set(after.roles)
    
    cargos_adicionados = cargos_atualizados - cargos_anteriores
    cargos_removidos = cargos_anteriores - cargos_atualizados
    
    if any(cargo.id in CARGO_IDS.values() for cargo in cargos_adicionados) or \
       any(cargo.id in CARGO_IDS.values() for cargo in cargos_removidos):
        await atualizar_embed_devedores(after.guild)

# Evento on_ready para enviar a prova, a mensagem inicial da hierarquia, carregar comandos slash e o bot de horas
@bot.event
async def on_ready():
    #iniciar canal devedores
    for guild in bot.guilds:
        await atualizar_embed_devedores(guild)

    # Canal hierarquia
    guild = bot.guilds[0]  # Supondo que o bot esteja em um único servidor
    await atualizar_hierarquia(guild)

    # Sincronizar os comandos do bot
    await bot.tree.sync()

        # Criar um dicionário de membros por ID ~~RANKING mensal
    global membros_por_id1
    membros_por_id1 = {membro.id: membro for membro in bot.get_all_members()}

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