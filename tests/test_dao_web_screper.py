import locale
import datetime
import logging

from dotenv import load_dotenv
from src.dao.web_screper_site import WebScreperSite

load_dotenv()

MESES_PORTUGUES = [
    'janeiro', 'fevereiro', 'março', 'abril', 'maio', 'junho',
    'julho', 'agosto', 'setembro', 'outubro', 'novembro', 'dezembro'
]


class TestWebScreper:
    def test_valida_se_esta_recebendo_dados_obras(self):
        web_screper = WebScreperSite()
        dados_obra = web_screper.receber_conteudo(5)

        [print(dado) for dado in dados_obra]

        assert len(dados_obra[0]) > 0
        assert len(dados_obra[1]) > 0
        assert len(dados_obra[2]) > 0
        assert len(dados_obra[3]) > 0
        assert len(dados_obra[4]) > 0

    def test_valida_se_esta_recebendo_capitulos_obras(self):
        web_screper = WebScreperSite()
        dados_obra = web_screper.recebe_capitulos_diarios()

        [print(obra) for obra in dados_obra]

        assert len(dados_obra) > 0

    def test_verifica_se_data_esta_em_portugues(self):
        """
        Verifica se as datas retornadas pelo scraper estão no formato
        em português (ex: 'março 7, 2026').
        Usa lista fixa de meses para não depender do locale do sistema.
        """
        web_screper = WebScreperSite()
        datas = web_screper.receber_datas()

        logger_infos = logging.getLogger('logger_infos')
        logger_infos.info(datas)

        for data in datas:
            partes = data.split()
            assert len(partes) >= 1, f"Formato de data inesperado: {data}"
            mes = partes[0].lower().rstrip(',')
            assert mes in MESES_PORTUGUES, (
                f"Mês '{mes}' não está em português na data '{data}'"
            )