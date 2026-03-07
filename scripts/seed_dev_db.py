"""
seed_dev_db.py
==============
Script de setup para ambiente de desenvolvimento local.

Cria as coleções do banco 'DadosPostagem' no MongoDB local com
os índices necessários, espelhando a estrutura usada em produção
pelo AtlasDAO. Nenhum dado de exemplo é inserido.

Uso:
    # Sobe apenas o MongoDB local:
    docker compose up mongo -d

    # Executa o setup:
    python scripts/seed_dev_db.py

Coleções criadas:
    - dadosObras              → catálogo de obras
    - registroObrasPostadas   → controle de capítulos já anunciados
    - obrasPermitidasFB       → whitelist de obras para postagem no Facebook
"""

import os
import sys
import logging
from typing import Any

from pymongo import MongoClient, ASCENDING
from dotenv import load_dotenv

# ---------------------------------------------------------------------------
# Configuração básica de log
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s | %(message)s",
)
logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Funções de setup
# ---------------------------------------------------------------------------

def _criar_indices(db: Any) -> None:
    """
    Cria índices nas coleções para garantir unicidade e performance,
    replicando o comportamento esperado em produção.

    Parameters:
        db: Instância do banco de dados MongoDB.
    """
    db.dadosObras.create_index(
        [("titulo", ASCENDING)], unique=True, name="titulo_unico"
    )
    logger.info("Índice 'titulo_unico' criado em 'dadosObras'.")

    db.registroObrasPostadas.create_index(
        [("titulo_obra", ASCENDING)], unique=True, name="titulo_obra_unico"
    )
    logger.info(
        "Índice 'titulo_obra_unico' criado em 'registroObrasPostadas'."
    )

    db.obrasPermitidasFB.create_index(
        [("titulo_obra", ASCENDING)], unique=True, name="titulo_obra_fb_unico"
    )
    logger.info(
        "Índice 'titulo_obra_fb_unico' criado em 'obrasPermitidasFB'."
    )




def seed(uri: str) -> None:
    """
    Cria as coleções e índices no banco 'DadosPostagem'.

    Conecta ao MongoDB pelo URI fornecido e cria os índices necessários
    nas coleções. As coleções são criadas automaticamente pelo MongoDB
    ao receber o primeiro índice.

    Parameters:
        uri (str): URI de conexão com o MongoDB.
    """
    logger.info("Conectando ao MongoDB: %s", uri)
    client = MongoClient(uri)

    try:
        client.admin.command("ping")
        logger.info("Conexão com MongoDB estabelecida com sucesso.")
    except Exception as exc:
        logger.error("Falha ao conectar com MongoDB: %s", exc)
        sys.exit(1)

    db = client.DadosPostagem

    _criar_indices(db)

    client.close()
    logger.info("Setup concluído.")


# ---------------------------------------------------------------------------
# Ponto de entrada
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    # Carrega o .env.dev se existir; caso contrário usa as variáveis do ambiente
    load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", ".env.dev"))

    mongo_uri = os.getenv("URI_ATLAS", "mongodb://localhost:27017/")
    seed(mongo_uri)
