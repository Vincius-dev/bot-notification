from dotenv import load_dotenv
from src.dao.atlas_dao import AtlasDAO
from src.model.obra import Obra
from src.model.capitulo import Capitulo
from src.controller.controller_obras import ControllerObras
from src.dao.web_screper_site import WebScreperSite

load_dotenv()

class TestPostagem:
    def test_verifica_remocao_obras_nao_registradas(self):
        atlas_dao = AtlasDAO()
        web_screper = WebScreperSite()

        obras_site = web_screper.recebe_capitulos_diarios()

        [print(obra) for obra in obras_site ]

        #Recebe obras postadas no site e remove as que não estão registradas
        lista_de_obras = ControllerObras.remove_obras_nao_registradas(
            obras_site,
            atlas_dao.receber_obras()
            )
        
        lista_de_obras_recebida = atlas_dao.receber_obras_anunciadas()

        if(len(lista_de_obras_recebida) > 0):
            #Verifica se existe registro de anúncios anteriores
            lista_de_obras_atualizada = ControllerObras.valida_lista_obras(
                lista_de_obras, 
                lista_de_obras_recebida
                )
        
        [print(obra) for obra in lista_de_obras_atualizada ]

        assert True
        

