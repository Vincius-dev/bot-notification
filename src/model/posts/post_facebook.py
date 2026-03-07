import logging

class PostFacebook:

    def __init__(self, obra, dados_unicos_obras):
        self.logger_infos = logging.getLogger('logger_infos')

        self.titulo_obra = obra.titulo_obra
        self.imagem_obra = obra.imagem_obra
        self.url_obra = obra.url_obra

        self.lista_de_capitulos = obra.lista_de_capitulos

        # Itera sobre a lista de obras (mesmo padrão do PostDiscord) em vez de
        # indexar como dict, o que causaria TypeError pois dados_unicos_obras é list.
        obra_encontrada = None
        for dados_obra in dados_unicos_obras:
            if dados_obra.get('titulo') == self.titulo_obra:
                obra_encontrada = dados_obra
                break

        if obra_encontrada:
            self.imagem_obra = obra_encontrada['url_imagem']
        else:
            self.logger_infos.warning(
                f"Obra '{self.titulo_obra}' não encontrada em dados_unicos_obras."
            )

        self.logger_infos.info(f"Construindo Post {self.titulo_obra}...")

    
    def retornar_mensagem_post(self):
        if len(self.lista_de_capitulos) == 1:

            self.logger_infos.info("postando: " + str(self.lista_de_capitulos))
            capitulo = self.lista_de_capitulos[0]

            mensagem_facebook = f'''
            
            Capítulo fresquinho para Todos!

            {self.titulo_obra}
            -- {capitulo.numero_capitulo}

            {capitulo.link_capitulo}

            Aproveita e passa lá no Discord para conversar com a gente:
            https://discord.gg/x4MyhMn3TQ

            Boa leitura a todos
            
            '''

        elif len(self.lista_de_capitulos) == 2:
            self.logger_infos.info("postando: " + str(self.lista_de_capitulos))
            
            primeiro_capitulo = self.lista_de_capitulos[1]
            segundo_capitulo = self.lista_de_capitulos[0]

            mensagem_facebook = f'''
            
            Capítulo fresquinho para Todos!

            {self.titulo_obra}
            -- {primeiro_capitulo.numero_capitulo} &
            -- {segundo_capitulo.numero_capitulo}

            {primeiro_capitulo.link_capitulo}

            Aproveita e passa lá no Discord para conversar com a gente:
            https://discord.gg/x4MyhMn3TQ

            Boa leitura a todos
            
            '''
        
        elif len(self.lista_de_capitulos) == 3:
            self.logger_infos.info("postando: " + str(self.lista_de_capitulos))
            
            primeiro_capitulo = self.lista_de_capitulos[2]
            segundo_capitulo = self.lista_de_capitulos[1]
            terceiro_capitulo = self.lista_de_capitulos[0]

            mensagem_facebook = f'''
            
            Capítulo fresquinho para Todos!

            {self.titulo_obra}
            -- {primeiro_capitulo.numero_capitulo} &
            -- {segundo_capitulo.numero_capitulo} &
            -- {terceiro_capitulo.numero_capitulo}

            {primeiro_capitulo.link_capitulo}

            Aproveita e passa lá no Discord para conversar com a gente:
            https://discord.gg/x4MyhMn3TQ

            Boa leitura a todos
            
            '''

        elif len(self.lista_de_capitulos) > 3:
            self.logger_infos.info("postando: " + str(self.lista_de_capitulos))
            
            primeiro_capitulo = self.lista_de_capitulos[0]
            ultimo_capitulo = self.lista_de_capitulos[-1]
    

            mensagem_facebook = f'''
            Capítulo fresquinho para Todos!

            {self.titulo_obra}
            Postados capítulos de:{ultimo_capitulo.numero_capitulo} -
            Até: {primeiro_capitulo.numero_capitulo}

            {ultimo_capitulo.numero_capitulo}

            Aproveita e passa lá no Discord para conversar com a gente:
            https://discord.gg/x4MyhMn3TQ

            Boa leitura a todos
            
            
            '''

        return mensagem_facebook