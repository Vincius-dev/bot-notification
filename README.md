# Bot de notificações no Discord

Bot que monitora lançamentos de capítulos em um site de mangás/webtoons e realiza postagens automáticas de anúncio em canais do Discord.

---

## Arquitetura do Projeto

```mermaid
flowchart TD
    MAIN["Main.py\n(Ponto de entrada)"]

    subgraph classes_io ["classes_io"]
        GESTOR["GestorTXT\nLê/grava data anterior\ne modo de teste (TXT)"]
        DOWNLOAD["DownloadImagens\nBaixa imagens das obras\nregistradas no Atlas"]
    end

    subgraph controller ["controller"]
        CTRL_POST["ControllerPostagem\nOrquestra o fluxo\nde postagem"]
        CTRL_OBRA["ControllerObras\nFiltra e valida\nlistas de obras"]
    end

    subgraph dao ["dao"]
        ATLAS["AtlasDAO\nMongoDB Atlas\n(obras registradas,\nanunciadas, etc.)"]
        SCRAPER["WebScreperSite\nWeb scraping dos\ncapítulos diários do site"]
        DISCORD["ConexaoDiscord\nEnvia embeds para\ncanais do Discord"]
        GEMINI["GeminiDAO\nIntegração com\nGoogle Gemini AI"]
    end

    subgraph model ["model"]
        OBRA["Obra"]
        CAPITULO["Capitulo"]
        POST_DC["PostDiscord\nMonta o embed\ndo anúncio"]
        POST_FB["PostFacebook\n(desativado)"]
        MSGS["Mensagens\nLogs e prints"]
        LOGGER["LoggerConfig\nConfiguração de logs"]
    end

    subgraph assets ["assets (volume)"]
        TXT_DATA["registro_horario/\ndata_anterior.txt"]
        TXT_MODE["config/\ntest_mode.txt"]
        IMGS["imagens/\n(cache local de imagens)"]
    end

    MAIN --> GESTOR
    MAIN --> DOWNLOAD
    MAIN --> CTRL_POST
    MAIN --> LOGGER

    GESTOR --> TXT_DATA
    GESTOR --> TXT_MODE

    DOWNLOAD --> ATLAS
    DOWNLOAD --> IMGS

    CTRL_POST --> ATLAS
    CTRL_POST --> SCRAPER
    CTRL_POST --> CTRL_OBRA
    CTRL_POST --> POST_DC
    CTRL_POST --> DISCORD

    SCRAPER --> OBRA
    SCRAPER --> CAPITULO

    POST_DC --> OBRA
    POST_DC --> CAPITULO

    CTRL_OBRA --> OBRA
```

### Fluxo principal

1. **GestorTXT** lê a data da última execução e o modo de teste.
2. **DownloadImagens** sincroniza o cache local de imagens com os dados do MongoDB Atlas.
3. **WebScreperSite** faz scraping do site e retorna a lista de obras com capítulos lançados no dia.
4. **ControllerObras** filtra obras não registradas no Atlas e remove capítulos já anunciados.
5. **ControllerPostagem** itera sobre as obras restantes, monta um `PostDiscord` e envia o embed via **ConexaoDiscord**.
6. O registro de obras anunciadas é persistido no MongoDB Atlas para evitar duplicatas.

### Variáveis de ambiente (`.env`)

| Variável | Descrição |
|---|---|
| `URI_ATLAS` | URI de conexão com o MongoDB Atlas |
| `API_KEY` | Token do bot Discord |
| `CANAL_LANCAMENTOS` | ID do canal de lançamentos |
| `CANAL_TAGS` | ID do canal de tags/cargos |
| `CANAL_TESTES` | ID do canal usado em modo de teste |
| `GEMINI_API` | Chave da API do Google Gemini |

---

## Estrutura de diretórios

```
bot-notification/
├── src/
│   ├── Main.py                      # Ponto de entrada
│   ├── classes_io/
│   │   ├── download_imagens.py      # Download de imagens das obras
│   │   └── gestor_txt.py            # Leitura/escrita de arquivos TXT
│   ├── controller/
│   │   ├── controller_obras.py      # Filtragem e validação de obras
│   │   └── controller_postagem.py   # Orquestração do fluxo de postagem
│   ├── dao/
│   │   ├── atlas_dao.py             # Acesso ao MongoDB Atlas
│   │   ├── conexao_discord.py       # Envio de mensagens ao Discord
│   │   ├── conexao_facebook.py      # Integração Facebook (desativada)
│   │   ├── gemini_dao.py            # Integração Google Gemini AI
│   │   └── web_screper_site.py      # Web scraping do site de mangás
│   ├── endpoint/
│   │   ├── bot_endpoint.py
│   │   └── pagination.py
│   └── model/
│       ├── capitulo.py              # Entidade Capítulo
│       ├── logger_config.py         # Configuração de loggers
│       ├── mensagens.py             # Mensagens de log/console
│       ├── obra.py                  # Entidade Obra
│       └── posts/
│           ├── post_discord.py      # Modelo do embed Discord
│           └── post_facebook.py     # Modelo do post Facebook (desativado)
├── assets/                          # Volume Docker (persistente)
│   ├── config/
│   │   └── test_mode.txt            # "true" para modo de teste
│   ├── imagens/                     # Cache local de capas das obras
│   └── registro_horario/
│       └── data_anterior.txt        # Data da última execução
├── tests/                           # Testes unitários (pytest)
├── Dockerfile
├── Dockerfile-dev
└── requirements.txt
```

---

## Instruções para desenvolvimento

A versão do Python utilizada é: `python:3.10`

Para criar o ambiente, utilize:
```bash
python3 -m venv venv
source venv/bin/activate
```

Para instalar as dependências do projeto:
```bash
pip install -r requirements.txt
```

Para executar os testes:
```bash
pytest
```

---

## Docker

A imagem utiliza volume para persistir os dados em `assets/`. Crie o volume antes de rodar:

```bash
docker volume create <nome-do-volume>
```

Construir a imagem:
```bash
docker build -t bot-notif:<versao-do-bot> .
```

Executar o container:
```bash
docker run -d -v <nome-do-volume>:/home/project/assets bot-notif:<versao-do-bot>
```

Acompanhar a saída do bot:
```bash
docker attach <id-do-container>
```

Encontrar o ID do container:
```bash
docker ps
```