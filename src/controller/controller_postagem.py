import time

from src.dao.web_screper_site import WebScreperSite
from src.dao.conexao_discord import ConexaoDiscord
from src.dao.atlas_dao import AtlasDAO
from src.dao.conexao_facebook import ConexaoFacebook
from src.controller.controller_obras import ControllerObras
from src.model.posts.post_discord import PostDiscord
from src.model.posts.post_facebook import PostFacebook
from src.classes_io.gestor_txt import GestorTXT

from model.mensagens import Mensagens

class ControllerPostagem:

    def execucao_principal():
        atlas_dao = AtlasDAO()
        web_screper = WebScreperSite()
        gestor_TXT = GestorTXT()

        Mensagens.inicializando_validacao_arquivos_antigos()

        #Recebe obras postadas no site e remove as que não estão registradas
        lista_de_obras = ControllerObras.remove_obras_nao_registradas(
            web_screper.recebe_capitulos_diarios(),
            atlas_dao.receber_obras()
            )
        
        lista_de_obras_recebida = atlas_dao.receber_obras_anunciadas()

        if(len(lista_de_obras_recebida) > 0):
            #Verifica se existe registro de anúncios anteriores
            lista_de_obras_atualizada = ControllerObras.valida_lista_obras(
                lista_de_obras, 
                lista_de_obras_recebida
                )

        #Faz validação dos capítulos e depois envia os dados para post
        if len(lista_de_obras_atualizada) > 0:
            Mensagens.conclusao_verificacao()

            Mensagens.post_redes()
            for obra in lista_de_obras_atualizada:
                try:
                    Mensagens.post_discord()

                    atlas_dao.adicionar_obras_anunciadas([obra])

                    post_obra_Discord = PostDiscord(
                        obra,
                        atlas_dao.receber_obras()
                    )
                    
                    Mensagens.mensagen_realizando_post_obra(post_obra_Discord.nome_no_anuncio)
                    ConexaoDiscord.postar_anuncio_discord(
                        post_obra_Discord,
                        gestor_TXT.get_mode()
                    )
                    
                except Exception as e:
                    Mensagens.erro_no_codigo(e)
                    Mensagens.nao_foi_possivel_postar_discord()
                    Mensagens.mensagem_nao_foi_possivel_postar_obra(obra.titulo_obra)
                        
                    atlas_dao.remover_obras_anunciadas([obra])

                time.sleep(10)

            # Postagem do FB
            lista_de_obras_nao_permitidas = atlas_dao.listar_obras_nao_permitidas_fb()

            lista_de_obras_facebook = ControllerObras.remover_obras_que_nao_pode_postar(
                lista_de_obras_atualizada, lista_de_obras_nao_permitidas
            )

            for obra in lista_de_obras_facebook:
                try:
                    Mensagens.post_facebook(obra.titulo_obra)
                    post_obra_Facebook = PostFacebook(obra, atlas_dao.receber_obras())
                    ConexaoFacebook.postar_anuncio_facebook(post_obra_Facebook)

                except Exception as e:
                    Mensagens.erro_no_codigo(e)
                    Mensagens.nao_foi_possivel_postar_facebook()
                    Mensagens.mensagem_nao_foi_possivel_postar_obra(obra.titulo_obra)

                time.sleep(10)
