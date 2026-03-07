import logging
import os
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from dotenv import load_dotenv

_TIMEOUT_SEGUNDOS = 30
_MAX_RETRIES = 3


def _criar_sessao_com_retry() -> requests.Session:
    """Cria uma Session com retry automático e backoff exponencial."""
    retry = Retry(
        total=_MAX_RETRIES,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["POST"],
        raise_on_status=False,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session = requests.Session()
    session.mount("https://", adapter)
    return session


class ConexaoFacebook:

    def postar_anuncio_facebook(post_obra):
        """
        Publica uma foto com legenda na página do Facebook via Graph API v25.0.

        Parameters:
            post_obra: objeto com titulo_obra, imagem_obra e método
            retornar_mensagem_post().

        Raises:
            requests.HTTPError: se alguma chamada à Graph API retornar erro.
        """
        logger_infos = logging.getLogger("logger_infos")
        logger_erros = logging.getLogger("logger_erros")

        load_dotenv(override=True)

        # Em modo de teste, usa credenciais de teste se ENABLE_FB_TEST=true
        is_test_mode = (
            os.getenv("ENABLE_FB_TEST", "false").lower() == "true"
        )

        if is_test_mode:
            token_de_acesso_fb = os.getenv("API_TOKEN_PAGINA_TESTE")
            id_pagina_fb = os.getenv("API_ID_PAGINA_FACEBOOK_TESTE")
            if not token_de_acesso_fb or not id_pagina_fb:
                logger_infos.info(
                    "[MODO TESTE] Credenciais de teste ausentes. "
                    "Postagem ignorada."
                )
                return
            logger_infos.info(
                "[MODO TESTE] Usando credenciais de teste do Facebook"
            )
        else:
            token_de_acesso_fb = os.getenv("API_TOKEN_PAGINA")
            id_pagina_fb = os.getenv("API_ID_PAGINA_FACEBOOK")
            if not token_de_acesso_fb or not id_pagina_fb:
                logger_erros.error(
                    "[MODO PRODUÇÃO] Credenciais do Facebook ausentes "
                    "(API_TOKEN_PAGINA / API_ID_PAGINA_FACEBOOK). "
                    "Postagem abortada."
                )
                raise EnvironmentError(
                    "Variáveis API_TOKEN_PAGINA e/ou API_ID_PAGINA_FACEBOOK "
                    "não estão definidas no ambiente."
                )

        logger_infos.info(f"Postando no Facebook: {post_obra.titulo_obra}")

        session = _criar_sessao_com_retry()

        # Passo 1: envia a URL da imagem como foto não publicada → obtém photo_id.
        # Usar URL em vez de upload binário evita criar entradas duplicadas
        # na galeria da página a cada nova postagem da mesma obra.
        url_photos = (
            f"https://graph.facebook.com/v25.0/{id_pagina_fb}/photos"
        )

        response_upload = session.post(
            url_photos,
            params={"access_token": token_de_acesso_fb},
            data={
                "url": post_obra.imagem_obra,
                "published": "false",
            },
            timeout=_TIMEOUT_SEGUNDOS,
        )

        if not response_upload.ok:
            logger_erros.error(
                f"Erro no upload da imagem: "
                f"{response_upload.status_code} — {response_upload.text}"
            )
        response_upload.raise_for_status()

        photo_id = response_upload.json().get("id")
        if not photo_id or not isinstance(photo_id, str):
            logger_erros.error(
                f"Resposta inesperada no upload da imagem "
                f"(photo_id ausente): {response_upload.text}"
            )
            raise ValueError(
                f"photo_id inválido após upload: {photo_id!r}"
            )
        logger_infos.info(f"Imagem enviada. photo_id: {photo_id}")

        # Passo 2: publica no feed com a imagem anexada via photo_id
        url_feed = f"https://graph.facebook.com/v25.0/{id_pagina_fb}/feed"

        response_post = session.post(
            url_feed,
            params={"access_token": token_de_acesso_fb},
            json={
                "message": post_obra.retornar_mensagem_post(),
                "attached_media": [{"media_fbid": photo_id}],
            },
            timeout=_TIMEOUT_SEGUNDOS,
        )

        if not response_post.ok:
            logger_erros.error(
                f"Erro ao publicar post: "
                f"{response_post.status_code} — {response_post.text}"
            )
        response_post.raise_for_status()

        logger_infos.info(
            f"Postagem no Facebook concluída: {post_obra.titulo_obra}"
        )
