import logging
import os
import subprocess
import datetime

import discord
from discord import app_commands
from discord.ext import commands

from dotenv import load_dotenv
from typing import Optional

from src.dao.atlas_dao import AtlasDAO
from src.dao.gemini_dao import GeminiDAO
from src.endpoint.pagination import Pagination
from src.classes_io.gestor_txt import GestorTXT
from src.model.logger_config import LoggerConfig

#Carregando as variaveis de ambiente
load_dotenv()
token = os.getenv('API_KEY')
canal = int(os.getenv('CANAL_TESTES'))

MY_GUILD = discord.Object(id=697958499589554217)
atlas_dao = AtlasDAO()

geminiDAO = GeminiDAO()

logger_config = LoggerConfig()

logger_infos = logging.getLogger('logger_infos')
logger_erros = logging.getLogger('logger_erros')

class MyClient(discord.Client):
    def __init__(self, *, intents: discord.Intents):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        self.tree.copy_global_to(guild=MY_GUILD)
        await self.tree.sync(guild=MY_GUILD)

intents = discord.Intents.default()
client = MyClient(intents=intents)

@client.event
async def on_ready():
    logger_infos.info(f'Logged in as {client.user} (ID: {client.user.id})')
    logger_infos.info('------')


#Adicionar obra no banco
@client.tree.command()
@app_commands.describe(
    titulo='Titulo que esta no site',
    cargo_discord='Cargo discord',
    capa_obra='URL da imagem',
    cor ='Cor em hexadecimal, ex:0xFFFFFF',
    dados_adicionais_mensagem='Alguma informação extra que aparece no final da mensagem ao anúnciar os capítulos'
)
async def adicionar_obra(interaction: discord.Interaction, titulo: str, cargo_discord: str, capa_obra: str, cor: str, dados_adicionais_mensagem: str = ''):
    """Adicione uma obra nova na listagem."""
    try:
        dicionario_obra = {
            titulo: {
                "cargo_discord": cargo_discord,
                "url_imagem": capa_obra,
                "cor": cor,
                "dados_adicionais_mensagem": dados_adicionais_mensagem
            }
        }

        atlas_dao.inserir_obra(dicionario_obra)

        await interaction.response.send_message(f'{titulo} adicionada com sucesso!')
    except Exception as e:
        await interaction.response.send_message(f'Erro ao adicionar {titulo}: {e}')


#Atualizar obra no banco
@client.tree.command()
@app_commands.describe(
    titulo='Titulo que esta no site',
    nova_capa='URL da imagem',
)
async def atualizar_capa_obra(interaction: discord.Interaction, titulo: str, nova_capa: str):
    """Atualize a capa de uma obra."""
    try:
        atlas_dao.atualizar_campo(titulo, 'url_imagem', nova_capa)

        await interaction.response.send_message(f'{titulo} Atualizada com sucesso!')
    except Exception as e:
        await interaction.response.send_message(f'Erro ao atualizar {titulo}: {e}')


@client.tree.command()
@app_commands.describe(
    titulo='Titulo que esta no site',
    nova_cor='Cor do embled',
)
async def atualizar_cor_obra(interaction: discord.Interaction, titulo: str, nova_cor: str):
    """Atualize a capa de uma obra."""
    try:
        atlas_dao.atualizar_campo(titulo, 'cor', nova_cor)

        await interaction.response.send_message(f'{titulo} Atualizada com sucesso!')
    except Exception as e:
        await interaction.response.send_message(f'Erro ao atualizar {titulo}: {e}')


@client.tree.command()
@app_commands.describe(
    titulo='Titulo que esta no site',
    nova_mensagem='Dados adicionais que aparecem no final do anúncio do capítulo',
)
async def atualizar_mensagem_obra(interaction: discord.Interaction, titulo: str, nova_mensagem: str):
    """Atualize os dados adicionais na mensagem de uma obra."""
    try:
        atlas_dao.atualizar_campo(titulo, 'dados_adicionais_mensagem', nova_mensagem)

        await interaction.response.send_message(f'{titulo} Atualizada com sucesso!')
    except Exception as e:
        await interaction.response.send_message(f'Erro ao atualizar {titulo}: {e}')


@client.tree.command()
@app_commands.describe(
    titulo='Titulo que esta no site'
)
async def adicionar_obra_permitida_fb(interaction: discord.Interaction, titulo: str):
    """Obras nessa lista têm permissão explícita para serem postadas no Facebook."""
    try:
        dicionario_obra = {
            "titulo_obra": titulo
        }

        atlas_dao.inserir_obra_permitida_fb(dicionario_obra)

        await interaction.response.send_message(f'{titulo} adicionada à whitelist do FB com sucesso!')
    except Exception as e:
        await interaction.response.send_message(f'Erro ao adicionar {titulo}: {e}')


#Comando para remover obras registrada no banco
@client.tree.command()
@app_commands.describe(
    titulo='Titulo que esta no site'
)
async def remover_obra(interaction: discord.Interaction, titulo: str):
    """Remova uma obra a partir do título."""

    res = atlas_dao.excluir_obra_por_titulo(titulo)

    await interaction.response.send_message(res)


#Comando para listar obras que estão no banco
@client.tree.command()
async def listar_obras(interaction: discord.Interaction):
    """Lista todas as obras registradas no banco."""

    cursor_obras = atlas_dao.receber_obras()  # Recebendo o cursor do MongoDB
    colecao_obras = list(cursor_obras)  # Convertendo o cursor para uma lista de obras

    max_docs_por_pagina = 10

    async def get_page(page: int):
        emb = discord.Embed(title="Obras Registradas", description="Obras que estão salvas no banco de dados.")
        offset = (page - 1) * max_docs_por_pagina

        parte_documentos = colecao_obras[offset:offset + max_docs_por_pagina]

        formatted_collections = "\n".join([f"{index + 1}. {obra}" for index, obra in enumerate(parte_documentos)])
        emb.description = formatted_collections

        total_pages = Pagination.compute_total_pages(len(colecao_obras), max_docs_por_pagina)
        emb.set_footer(text=f"Página {page} de {total_pages}")
        
        return emb, total_pages

    await Pagination(interaction, get_page).navegate()


#Comando para listar obras que estão no banco
@client.tree.command()
async def listar_obras_permitidas_fb(interaction: discord.Interaction):
    """Listar obras com permissão para postagem no FB (whitelist)."""

    colecao_obras = atlas_dao.listar_obras_permitidas_fb()

    max_docs_por_pagina = 10

    async def get_page(page: int):
        emb = discord.Embed(title="Obras Permitidas no FB", description="Obras com permissão explícita de postagem no Facebook.")
        offset = (page - 1) * max_docs_por_pagina

        parte_documentos = colecao_obras[offset:offset + max_docs_por_pagina]

        formatted_collections = "\n".join([f"{index + 1}. {obra}" for index, obra in enumerate(parte_documentos)])
        emb.description = formatted_collections

        total_pages = Pagination.compute_total_pages(len(colecao_obras), max_docs_por_pagina)
        emb.set_footer(text=f"Página {page} de {total_pages}")

        return emb, total_pages

    await Pagination(interaction, get_page).navegate()


#Comando para forçar verificação de novos capitulos
@client.tree.command()
async def forcar_postagem(interaction: discord.Interaction):
    """Força a execução da postagem dos capitulos."""

    subprocess.Popen(["python", "src/Main.py"])

    await interaction.response.send_message(f'Postagem esta sendo iniciada... acompanhe pelo canal de logs')


#Comando para listar obras que estão no banco
@client.tree.command()
async def listar_registro_de_postagem(interaction: discord.Interaction):
    """Lista todas as obras registradas no banco."""

    cursor_obras = atlas_dao.receber_obras_anunciadas()  # Recebendo o cursor do MongoDB
    colecao_obras = list(cursor_obras)  # Convertendo o cursor para uma lista de obras

    max_docs_por_pagina = 10

    async def get_page(page: int):
        emb = discord.Embed(title="Registro de Anúncios", description="Obras e capitulos que foram postados.")
        offset = (page - 1) * max_docs_por_pagina

        parte_documentos = colecao_obras[offset:offset + max_docs_por_pagina]

        formatted_collections = "\n".join([f"{index + 1}. {obra}" for index, obra in enumerate(parte_documentos)])
        emb.description = formatted_collections

        total_pages = Pagination.compute_total_pages(len(colecao_obras), max_docs_por_pagina)
        emb.set_footer(text=f"Página {page} de {total_pages}")
        
        return emb, total_pages

    await Pagination(interaction, get_page).navegate()


#Forçar exclusão dos registros e atualizar data
gestor_TXT = GestorTXT()
@client.tree.command()
async def excluir_registros(interaction: discord.Interaction):
    """Exclui registro das ultimas postagens e reseta a data anterior."""

    data_atual = datetime.datetime.now().date()

    atlas_dao.excluir_registros_de_obras_anunciadas()
    gestor_TXT.atualiza_data_anterior(data_atual)

    await interaction.response.send_message(f'Registros excluídos e data atualizada.')


@client.tree.command()
async def informacoes_postagem(interaction: discord.Interaction):
    """Informações gerais sobre o bot."""

    embed = discord.Embed(
        title="Informações sobre o Bot",
        description="Aqui estão algumas informações sobre este Bot.",
        color=discord.Color.green()
    )

    embed.add_field(name="Horários de verificação", value="12h, 16h, 18h, 20h e 22h", inline=False)
    embed.add_field(name="Adicionar obras novas", value="Use /adicionar_obra(Também atualiza os já adicionados se o título for o mesmo), /listar_obras e /remover_obra.", inline=False)
    embed.add_field(name="Gerenciar Postagem", value="Use /forcar_postagem e /excluir_registros.", inline=False)
    embed.add_field(name="Gerenciar whitelist do FB", value="Use /adicionar_obra_permitida_fb e /listar_obras_permitidas_fb .", inline=False)
    embed.add_field(name="Comandos utilitários", value="/ping, /joined e /informacoes_postagem .", inline=False)
    embed.add_field(name="Versão em execução", value="3.0.0", inline=False)

    await interaction.response.send_message(embed=embed)


#Comando que verifica quando um membro entrou no servidor
@client.tree.command()
@app_commands.describe(member='The member you want to get the joined date from; defaults to the user who uses the command')
async def joined(interaction: discord.Interaction, member: Optional[discord.Member] = None):
    """Diga quando um membro entrou no servidor"""
    # If no member is explicitly provided then we use the command user here
    member = member or interaction.user

    # The format_dt function formats the date time into a human readable representation in the official client
    await interaction.response.send_message(f'{member} entrou {discord.utils.format_dt(member.joined_at)}')


#Teste do banco de dados
@client.tree.command()
async def testar_banco(interaction: discord.Interaction):
    """Verifica conexão com banco de dados."""

    if(atlas_dao.testar_conexao()):
        await interaction.response.send_message(f'Ativo e operante!')
    else:
        await interaction.response.send_message(f'Moio o esquema, abre um chamado aí!')


#Teste conectividade do bot
@client.tree.command()
async def ping(interaction: discord.Interaction):
    """Verificar conectividade do bot."""
    await interaction.response.send_message(f'Olá, Latência: {round(client.latency,3)} ms')


#Habilitar modo de teste
@client.tree.command()
@app_commands.describe(
    boolean='True para ativo ou False para desativado',
)
async def mudar_modo_teste(interaction: discord.Interaction, boolean: bool):
    """Ative ou desative o modo de teste"""
    try:
        gestor_TXT.atualiza_mode(boolean)

        await interaction.response.send_message(f'Modo de teste alterado para: {gestor_TXT.get_mode()} ')
    except Exception as e:
        await interaction.response.send_message(f'Erro ao modificar o arquivo: {e}')


#Verificar o modo de teste
@client.tree.command()
async def verifica_modo_teste(interaction: discord.Interaction):
    """Verifica o estado do modo de teste"""
    try:
        await interaction.response.send_message(f'Modo de teste está: {gestor_TXT.get_mode()} ')
    except Exception as e:
        await interaction.response.send_message(f'Erro ao modificar o arquivo: {e}')

def getResposta(titulo_obra:str):
    return geminiDAO.generate_opniao_obra(titulo_obra)


#Habilitar modo de teste
@client.tree.command()
@app_commands.describe(
    titulo='algo assunto, anime, filme, etc.',
)
async def opniao(interaction: discord.Interaction, titulo: str):
    try:
        await interaction.response.send_message(getResposta(titulo))
    except Exception as e:
        await interaction.response.send_message(f'Erro ao modificar o arquivo: {e}')

client.run(token)