import logging
from src.model.mensagens import Mensagens

class ControllerObras:

    """
    Remove obras não registradas da lista de obras recebidas.
    Args:
        lista_de_obras_recebidas (list): Lista de obras recebidas.
        dados_unicos_obras (list): Lista de dados únicos das obras registradas.
    Returns:
        list: Lista de obras registradas.
    """
    def remove_obras_nao_registradas(lista_de_obras_recebidas, dados_unicos_obras):
        dados_unicos_obras = set(obra.get('titulo') for obra in dados_unicos_obras)

        obras_registradas = []
        obras_nao_registradas = []

        for obra in lista_de_obras_recebidas:
            if obra.titulo_obra in dados_unicos_obras:
                obras_registradas.append(obra)
            else:
                obras_nao_registradas.append(obra.titulo_obra)
                
        if obras_nao_registradas:
            Mensagens.informa_obras_sem_registro(obras_nao_registradas)
            print(obras_nao_registradas)
                
        return obras_registradas


    """
    Remove obras que não podem ser postadas.
    Args:
        lista_de_obras_para_postar (list): Lista de obras para postar.
        lista_de_obras_nao_permitidas (list): Lista de obras não permitidas.
    Returns:
        list: Lista de obras filtradas, sem as obras não permitidas.
    """
    def remover_obras_que_nao_pode_postar(lista_de_obras_para_postar, lista_de_obras_nao_permitidas):
        titulos_obras_nao_permitidas = [obra['titulo_obra'] for obra in lista_de_obras_nao_permitidas]

        obras_filtradas = [
            obra for obra in lista_de_obras_para_postar
            if obra.titulo_obra not in titulos_obras_nao_permitidas
        ]
        return obras_filtradas


    """
    Validates the list of works and removes chapters that have already been announced.
    Args:
        lista_de_obras (list): The list of works to be validated.
        lista_de_obras_contidas_no_registro (list): The list of works already registered.
    Returns:
        list: The updated list of works after removing announced chapters.
    """
    def valida_lista_obras(lista_de_obras, lista_de_obras_contidas_no_registro):       
        logger_infos = logging.getLogger('logger_infos')
 
        logger_infos.info("\n*******************************************************")
        Mensagens.mensagem_lista_de_obras_para_verificar(lista_de_obras)
        logger_infos.info(lista_de_obras_contidas_no_registro)

        obras_contidas_no_registro_dict = {obra.titulo_obra: obra for obra in lista_de_obras_contidas_no_registro}

        for obra_atual in lista_de_obras:
            obra_contida_no_registro = obras_contidas_no_registro_dict.get(obra_atual.titulo_obra)
            if obra_contida_no_registro:
                capitulos_contidos_no_registro = set(cap.numero_capitulo for cap in obra_contida_no_registro.lista_de_capitulos)
                capitulos_restantes = [cap for cap in obra_atual.lista_de_capitulos if cap.numero_capitulo not in capitulos_contidos_no_registro]
                
                obra_atual.lista_de_capitulos = capitulos_restantes

        lista_de_obras = [obra for obra in lista_de_obras if obra.lista_de_capitulos]

        Mensagens.mensagem_lista_de_obras_para_fazer_anuncio(lista_de_obras)
        logger_infos.info("*******************************************************\n")

        return lista_de_obras