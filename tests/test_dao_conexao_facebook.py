import os
import pytest
from unittest.mock import patch, MagicMock
from dotenv import load_dotenv
from src.dao.conexao_facebook import ConexaoFacebook
from src.dao.atlas_dao import AtlasDAO
from src.controller.controller_obras import ControllerObras
from src.model.capitulo import Capitulo
from src.model.obra import Obra
from src.model.posts.post_facebook import PostFacebook


class TestRegraDeNegocioFacebook:
    """
    Testes de regra de negócio para postagem no Facebook (whitelist).
    Estes testes não fazem chamadas à API — sempre executam.
    """

    def test_somente_obras_permitidas_sao_retornadas(self):
        """
        Apenas obras cujo título consta na whitelist devem ser retornadas.
        """
        lista_para_postar = [
            Obra("Obra A", "http://img.com/a.png", "http://site.com/a"),
            Obra("Obra B", "http://img.com/b.png", "http://site.com/b"),
            Obra("Obra C", "http://img.com/c.png", "http://site.com/c"),
        ]
        permitidas = [
            {"titulo_obra": "Obra A"},
        ]

        resultado = ControllerObras.filtrar_obras_permitidas_fb(
            lista_para_postar, permitidas
        )

        assert len(resultado) == 1
        assert resultado[0].titulo_obra == "Obra A"

    def test_whitelist_vazia_retorna_lista_vazia(self):
        """
        Com a whitelist vazia, nenhuma obra deve ser retornada.
        """
        lista_para_postar = [
            Obra("Obra A", "http://img.com/a.png", "http://site.com/a"),
            Obra("Obra B", "http://img.com/b.png", "http://site.com/b"),
        ]

        resultado = ControllerObras.filtrar_obras_permitidas_fb(
            lista_para_postar, []
        )

        assert len(resultado) == 0

    def test_todas_obras_permitidas_retorna_lista_completa(self):
        """
        Se todas as obras estiverem na whitelist, todas devem ser retornadas.
        """
        lista_para_postar = [
            Obra("Obra A", "http://img.com/a.png", "http://site.com/a"),
            Obra("Obra B", "http://img.com/b.png", "http://site.com/b"),
        ]
        permitidas = [
            {"titulo_obra": "Obra A"},
            {"titulo_obra": "Obra B"},
        ]

        resultado = ControllerObras.filtrar_obras_permitidas_fb(
            lista_para_postar, permitidas
        )

        assert len(resultado) == 2

    def test_obra_nao_listada_na_whitelist_e_removida(self):
        """
        Obra ausente da whitelist não deve aparecer no resultado,
        mesmo que não esteja em nenhuma lista de bloqueio.
        """
        lista_para_postar = [
            Obra("Obra Permitida", "http://img.com/p.png", "http://site.com/p"),
            Obra("Obra Sem Permissao", "http://img.com/s.png", "http://site.com/s"),
        ]
        permitidas = [{"titulo_obra": "Obra Permitida"}]

        resultado = ControllerObras.filtrar_obras_permitidas_fb(
            lista_para_postar, permitidas
        )

        assert len(resultado) == 1
        assert resultado[0].titulo_obra == "Obra Permitida"


class TestFlagEnableFbTest:
    """
    Testes que validam o comportamento da flag ENABLE_FB_TEST.

    Quando true sem credenciais de teste: não posta em lugar nenhum.
    Quando true com credenciais de teste: posta na página de teste.
    """

    def test_sem_credenciais_de_teste_nao_faz_chamada_api(
        self, monkeypatch
    ):
        """
        Quando ENABLE_FB_TEST=true mas as variáveis de ambiente da
        página de teste estão ausentes, nenhuma chamada à API deve
        ser feita.
        """
        monkeypatch.setenv("ENABLE_FB_TEST", "true")
        monkeypatch.delenv("API_TOKEN_PAGINA_TESTE", raising=False)
        monkeypatch.delenv("API_ID_PAGINA_FACEBOOK_TESTE", raising=False)

        obra = Obra("Teste", "http://img.com/a.png", "http://site.com/a")
        post_facebook = PostFacebook(obra, [])
        capitulo = Capitulo("1", "http://site.com/cap1", "março 7, 2026")
        post_facebook.lista_de_capitulos.append(capitulo)

        with patch("src.dao.conexao_facebook.requests.post") as mock_post:
            with patch("src.dao.conexao_facebook.load_dotenv"):
                ConexaoFacebook.postar_anuncio_facebook(post_facebook)

        assert mock_post.call_count == 0


class TestWhitelistFluxoPostagem:
    """
    Testes que validam o fluxo completo: whitelist do Atlas → postagem.

    Simula o trecho do ControllerPostagem que consulta a whitelist e
    chama ConexaoFacebook, garantindo que apenas obras autorizadas
    chegam à API do Facebook.
    """

    def _simular_fluxo_fb(
        self,
        lista_obras: list,
        whitelist: list,
        mock_fb,
    ) -> list:
        """
        Reproduz o trecho de postagem do FB de execucao_principal,
        retornando os títulos das obras que foram efetivamente postadas.
        """
        obras_postadas = []

        obras_permitidas = ControllerObras.filtrar_obras_permitidas_fb(
            lista_obras, whitelist
        )

        for obra in obras_permitidas:
            post = PostFacebook(obra, [])
            cap = Capitulo("1", "http://site.com/cap1", "março 7, 2026")
            post.lista_de_capitulos.append(cap)
            mock_fb(post)
            obras_postadas.append(obra.titulo_obra)

        return obras_postadas

    def test_obra_fora_da_whitelist_nao_e_postada(self):
        """
        Obra ausente da whitelist do Atlas não deve gerar chamada ao
        Facebook, mesmo que tenha capítulos novos.
        """
        lista_obras = [
            Obra("Obra Sem Permissao", "http://img.com/s.png", "http://site.com/s"),
        ]
        whitelist = []  # Atlas retorna vazio — nenhuma obra autorizada

        mock_fb = MagicMock()
        postadas = self._simular_fluxo_fb(lista_obras, whitelist, mock_fb)

        assert mock_fb.call_count == 0
        assert postadas == []

    def test_obra_na_whitelist_e_postada(self):
        """
        Obra presente na whitelist do Atlas deve ser postada no Facebook.
        """
        lista_obras = [
            Obra("Obra Permitida", "http://img.com/p.png", "http://site.com/p"),
        ]
        whitelist = [{"titulo_obra": "Obra Permitida"}]

        mock_fb = MagicMock()
        postadas = self._simular_fluxo_fb(lista_obras, whitelist, mock_fb)

        assert mock_fb.call_count == 1
        assert postadas == ["Obra Permitida"]

    def test_apenas_obras_da_whitelist_sao_postadas(self):
        """
        Com múltiplas obras, apenas as presentes na whitelist devem
        ser postadas; as demais devem ser ignoradas.
        """
        lista_obras = [
            Obra("Obra A", "http://img.com/a.png", "http://site.com/a"),
            Obra("Obra B", "http://img.com/b.png", "http://site.com/b"),
            Obra("Obra C", "http://img.com/c.png", "http://site.com/c"),
        ]
        # Apenas A e C estão autorizadas
        whitelist = [
            {"titulo_obra": "Obra A"},
            {"titulo_obra": "Obra C"},
        ]

        mock_fb = MagicMock()
        postadas = self._simular_fluxo_fb(lista_obras, whitelist, mock_fb)

        assert mock_fb.call_count == 2
        assert "Obra A" in postadas
        assert "Obra C" in postadas
        assert "Obra B" not in postadas


class TestConexaoFacebook:
    """
    Testes para postagem no Facebook.

    Por padrão, os testes estão DESABILITADOS para evitar postagens acidentais.
    Para habilitar, defina ENABLE_FB_TEST=true no .env e execute:
        pytest tests/test_dao_conexao_facebook.py
    """

    def test_postagem_facebook_esta_funcionando(self):
        """
        Testa a postagem de dois capítulos no Facebook.
        Requer ENABLE_FB_TEST=true no .env para executar.
        """
        load_dotenv(override=True)
        if os.getenv("ENABLE_FB_TEST", "false").lower() != "true":
            pytest.skip("ENABLE_FB_TEST não está true no .env")
        atlas_dao = AtlasDAO()

        # Cria uma obra de teste
        obra = Obra(
            "Teste de Postagem",
            "https://tsundoku.com.br/wp-content/uploads/2022/02/Gosu_The_Master1.png",
            "https://tsundoku.com.br/manga/teste-de-postagem/"
        )

        post_facebook = PostFacebook(obra, atlas_dao.receber_obras())

        # Adiciona capítulos de teste
        capitulo_um = Capitulo(
            "9998",
            "https://tsundoku.com.br/teste-cap-9998/",
            "março 4, 2026"
        )

        capitulo_dois = Capitulo(
            "9999",
            "https://tsundoku.com.br/teste-cap-9999/",
            "março 4, 2026"
        )

        post_facebook.lista_de_capitulos += [capitulo_um, capitulo_dois]

        # Executa a postagem
        ConexaoFacebook.postar_anuncio_facebook(post_facebook)

        # Se chegou aqui sem exceção, o teste passou
        assert True

    def test_postagem_facebook_um_capitulo(self):
        """
        Testa a postagem de um único capítulo no Facebook.
        Requer ENABLE_FB_TEST=true no .env para executar.
        """
        load_dotenv(override=True)
        if os.getenv("ENABLE_FB_TEST", "false").lower() != "true":
            pytest.skip("ENABLE_FB_TEST não está true no .env")
        atlas_dao = AtlasDAO()

        obra = Obra(
            "Teste de Postagem",
            "https://tsundoku.com.br/wp-content/uploads/2022/02/Gosu_The_Master1.png",
            "https://tsundoku.com.br/manga/teste-de-postagem/"
        )

        post_facebook = PostFacebook(obra, atlas_dao.receber_obras())

        capitulo = Capitulo(
            "100",
            "https://tsundoku.com.br/teste-cap-100/",
            "março 4, 2026"
        )

        post_facebook.lista_de_capitulos.append(capitulo)

        # Executa a postagem
        ConexaoFacebook.postar_anuncio_facebook(post_facebook)

        assert True
