import locale
import logging
import requests

from datetime import datetime, timedelta
from babel.dates import format_date
from bs4 import BeautifulSoup

from src.model.capitulo import Capitulo
from src.model.obra import Obra
from src.model.mensagens import Mensagens
from src.classes_io.gestor_txt import GestorTXT
import os


class WebScreperSite:

    def __init__(self):
        logger_infos = logging.getLogger('logger_infos')
        logger_infos.info(" Iniciando Web Screper ")

        # Definir o locale como "pt_BR.UTF-8".
        # Em ambientes sem o locale instalado (ex: WSL sem pt_BR gerado)
        # a configuração é ignorada com um aviso — o Docker tem o locale.
        try:
            locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
        except locale.Error:
            logger_infos.warning(
                "Locale pt_BR.UTF-8 não disponível neste ambiente. "
                "Datas podem não ser formatadas em português."
            )


    def recebe_capitulos_diarios(self):
        Mensagens.recebendo_capitulos_mensagem()

        lista_de_obras = []

        for numero_atual in [5,6,7,8,9,10,11,12]:

            dados_obra = self.receber_conteudo(numero_atual)

            if (dados_obra == []):
                break

            titulo_obra = dados_obra[0]
            imagem_obra = dados_obra[3]
            url_obra = dados_obra[4]

            obra = Obra(titulo_obra, imagem_obra, url_obra)
            lista_de_capitulos = self.receber_capitulos_diarios_obras(url_obra)

            if len(lista_de_capitulos) == 0:
                Mensagens.mensagem_nenhum_post_obra(titulo_obra)
            else:
                Mensagens.mensagem_obra_tem_n_posts(titulo_obra,len(lista_de_capitulos))
                obra.receber_lista_de_capitulos(lista_de_capitulos)
                lista_de_obras.append(obra)

        return lista_de_obras


    def receber_capitulos_diarios_obras(self, url_obra):
        response = requests.get(url_obra)
        soup = BeautifulSoup(response.text, 'html.parser')

        dados_postagem = soup.find('div', {'class': 'eplister'}).find('ul')

        lista_de_capitulos = []

        datas = self.receber_datas()

        for li in dados_postagem.find_all("li"):
            chapterdate = li.find("span", class_="chapterdate").text
            if chapterdate in datas:
                chapternum = li.find("span", class_="chapternum").text
                chapterlink = li.find("a")["href"]
                lista = [chapternum, chapterdate, chapterlink]
                capitulo = Capitulo(lista[0], lista[2], lista[1])
                lista_de_capitulos.append(capitulo) # Adiciona a lista à matriz

        return lista_de_capitulos


    def receber_datas(self):
        logger_infos = logging.getLogger('logger_infos')

        gestor_TXT = GestorTXT()
        data_anterior = gestor_TXT.get_data_anterior()

        data_atual = datetime.now()

        max_dias = 7

        diferenca_dias = data_atual.toordinal() - data_anterior.toordinal()

        dias_permitidos = min(diferenca_dias, max_dias)

        datas = []
        datas.append(format_date(data_atual, "MMMM d, Y", locale='pt_BR'))  # Adiciona a data atual

        for i in range(1, dias_permitidos + 1):  # Começa a partir de 1 para incluir o dia atual
            data = data_atual - timedelta(days=i)
            datas.append(format_date(data, "MMMM d, Y", locale='pt_BR'))

        logger_infos.info(datas)

        return datas


    def receber_conteudo(self, numero_partir_ultimo_capitulo_postado, protocolo_https=True):
        url = self.monta_url_site(protocolo_https)

        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
        except Exception:
            if protocolo_https:
                Mensagens.mensagem_erro_conexao_internet("https")
                Mensagens.mensagem_nova_tentativa_conexao_internet("http")
                return self.receber_conteudo(numero_partir_ultimo_capitulo_postado, False)
            Mensagens.mensagem_erro_conexao_internet("http")
            return []

        soup = BeautifulSoup(response.text, 'html.parser')

        divs_bsx = soup.find_all(name='div', class_='bsx')
        ultima_atualizada = divs_bsx[numero_partir_ultimo_capitulo_postado]

        titulo_obra = ultima_atualizada.select_one('.tt a')['title']
        url_obra = ultima_atualizada.select_one('.tt a')['href']

        url_obra = ultima_atualizada.select_one('.bsx a')['href']

        try:
            url_ultimo_capitulo = ultima_atualizada.select_one('.chfiv a')['href']
        except:
            Mensagens.mensagem_obra_nao_tem_nenhum_capitulo(titulo_obra)
            return []

        numero_ultimo_capitulo = ultima_atualizada.select_one('.chfiv a').text

        response = requests.get(url_obra)
        soup = BeautifulSoup(response.text, 'html.parser')
        imagem_obra = soup.select_one('.thumb img')['src']

        dados_ultima_obra_atualizada = [titulo_obra,numero_ultimo_capitulo,url_ultimo_capitulo,imagem_obra,url_obra]

        return dados_ultima_obra_atualizada

    def monta_url_site(self, https=True):
        url_site = os.getenv('URL_SITE')

        if https:
            return 'https://' + url_site
        else:
            return 'http://' + url_site
