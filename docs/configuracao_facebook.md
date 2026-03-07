# Configuração da Integração com o Facebook

Este guia cobre o processo completo para criar um app Meta, configurar as permissões necessárias e gerar o Page Access Token para publicações automáticas na página do Facebook.

---

## Pré-requisitos

- Conta no [Meta for Developers](https://developers.facebook.com) (pode usar conta Facebook pessoal)
- Página do Facebook que você **administra** (onde os posts serão publicados)

---

## 1. Criar o App no Meta for Developers

1. Acesse https://developers.facebook.com/apps
2. Clique em **Criar App**
3. Em **Qual é o caso de uso do seu app?**, selecione **"Outros"** e clique em Próximo
4. Selecione o tipo **Business** e clique em Próximo
5. Preencha o **Nome de exibição do app** e o e-mail de contato
6. Clique em **Criar App**

---

## 2. Adicionar o caso de uso "Gerenciar tudo na sua Página"

1. Após criar o app, você será redirecionado para o painel **Adicionar produtos ao seu app**
2. Localize o caso de uso **"Gerenciar tudo na sua Página"** (_Manage everything on your Page_)
3. Clique em **Configurar** nesse caso de uso

---

## 3. Configurar as permissões

1. No menu lateral, vá em **Casos de uso** (ou _Use Cases_)
2. Localize **"Gerenciar tudo na sua Página"** e clique em **Personalizar**
3. Na aba **Permissões**, clique em **Adicionar** para cada uma das permissões abaixo:

   | Permissão | Finalidade |
   |---|---|
   | `pages_show_list` | Listar as páginas gerenciadas pela conta |
   | `pages_read_engagement` | Ler métricas e engajamento da página |
   | `pages_read_user_content` | Ler conteúdo publicado por usuários na página |
   | `pages_manage_posts` | Criar, editar e excluir posts na página |
   | `pages_manage_engagement` | Gerenciar comentários e interações da página |

4. Após adicionar todas as permissões, confirme que as cinco aparecem listadas na seção **Permissões** da personalização do caso de uso

> ℹ️ Não é necessário submeter o app para revisão da Meta enquanto você for **Administrador** da página e estiver testando com contas de desenvolvedor listadas no app.

---

## 4. Gerar o Page Access Token via `/me/accounts`

O token necessário é um **Page Access Token** (não User Token). A forma mais simples de obtê-lo é pela rota `/me/accounts`:

1. Acesse o [Graph API Explorer](https://developers.facebook.com/tools/explorer/?method=GET&path=me%2Faccounts&version=v25.0)
2. No dropdown **"App da Meta"**, selecione o app que você criou
3. Certifique-se de que **"User Token"** está selecionado em **"User or Page"**
4. Certifique-se de que as seguintes permissões estão marcadas no campo **Permissões**:
   - `pages_show_list`
   - `pages_read_engagement`
   - `pages_read_user_content`
   - `pages_manage_posts`
   - `pages_manage_engagement`
5. Clique em **Gerar token de acesso** e autorize no popup
6. O caminho `/me/accounts` já estará preenchido — clique em **Enviar**

### Obtendo o ID e o token da página

O `access_token` e o `id` corretos são os da **página**, não do usuário. Para obtê-los:

1. No [Graph API Explorer](https://developers.facebook.com/tools/explorer/?method=GET&path=me%2Faccounts&version=v25.0), certifique-se de que o **User Access Token** está selecionado (não Page Token)
2. O caminho `/me/accounts` já estará preenchido — clique em **Enviar**
3. A resposta listará todas as páginas que você administra:
   ```json
   {
     "data": [
       {
         "access_token": "EAACxxx...",
         "category": "Entretenimento",
         "name": "Nome da Página",
         "id": "110041288738055",
         "tasks": ["ANALYZE", "ADVERTISE", "MODERATE", "CREATE_CONTENT"]
       }
     ]
   }
   ```
4. Copie o `access_token` e o `id` do objeto correspondente à sua página
   - `id` → valor de `API_ID_PAGINA_FACEBOOK`
   - `access_token` → valor de `API_TOKEN_PAGINA`

> ⚠️ **Importante:** use o `access_token` que vem dentro de `data[]` (token da página), não o User Access Token exibido no topo do Explorer. Tokens de usuário não têm permissão para publicar na página.

---

## 5. Obter token permanente de página (produção)

O token de Usuário gerado pelo Explorer tem validade de **~1 hora**. Para uso em produção você precisa de um **Page Access Token permanente** (sem expiração). Há duas formas de obtê-lo:

### Opção 1: Via chamada OAuth direta

**Passo 1 — Converter o User Token em token de longa duração (~60 dias):**

```
GET https://graph.facebook.com/v25.0/oauth/access_token
  ?grant_type=fb_exchange_token
  &client_id={APP_ID}
  &client_secret={APP_SECRET}
  &fb_exchange_token={TOKEN_CURTA_DURACAO}
```

- `APP_ID` e `APP_SECRET`: encontrados em **Painel do App → Configurações → Básico**
- Substitua `{TOKEN_CURTA_DURACAO}` pelo User Token gerado no Explorer

**Passo 2 — Obter o Page Token permanente a partir do token longo:**

Com o token de 60 dias em mãos, repita a chamada da seção 4 (`GET /me/accounts`) usando esse token no cabeçalho de autorização. O `access_token` retornado dentro de `data[]` para a sua página será **permanente** (sem data de expiração).

Para renovação automática, consulte a [documentação de tokens da Meta](https://developers.facebook.com/docs/facebook-login/guides/access-tokens/get-long-lived/).

---

### Opção 2: Via Ferramenta de Token do Facebook (sem código — mais rápido)

O Facebook possui um botão "escondido" que executa toda a troca OAuth por você direto na interface do Explorador de API.

1. No **Explorador de API do Graph**, gere um User Token curto como descrito na seção 4.
2. Clique no **ícone azul de informação (ⓘ)** que fica logo ao lado do token exibido na caixa azul.
3. No balão que abrir, clique em **"Abrir na Ferramenta de Token de Acesso"**.
4. Uma nova aba será aberta. Role até o final da página e clique no botão azul **"Estender token de acesso"**.
5. O token de 60 dias será gerado na hora — **copie-o**.
6. Volte para o Explorador de API, **cole esse token longo** na caixa azul (substituindo o token antigo).
7. No seletor **"Usuário ou Página"**, escolha a sua Página.
8. O token gerado após a seleção da página é o **Page Access Token permanente** (sem expiração). Copie-o.

> ℹ️ Esse é o mesmo token que a Opção 1 produziria — a ferramenta apenas automatiza a chamada `oauth/access_token` por baixo dos panos.

---

## 6. Atualizar o `.env`

Adicione as variáveis ao arquivo `.env` na raiz do projeto:

```ini
# Facebook — Produção
API_ID_PAGINA_FACEBOOK = "110041288738055"
API_TOKEN_PAGINA = "EAACxxx..."

# Facebook — Testes (opcional, necessário apenas para rodar testes de integração)
API_ID_PAGINA_FACEBOOK_TESTE = "ID_DA_PAGINA_DE_TESTE"
API_TOKEN_PAGINA_TESTE = "EAACxxx..."
ENABLE_FB_TEST = "false"
```

> ⚠️ Nunca commite o `.env` com tokens reais. O arquivo `.env` já está no `.gitignore`.

---

## 7. Testar a integração

Para rodar os testes de integração com Facebook (faz postagens reais na página de teste):

```bash
# No .env, habilite o modo de teste:
ENABLE_FB_TEST = "true"

# Execute apenas os testes de Facebook:
venv/bin/python -m pytest tests/test_dao_conexao_facebook.py -v
```

> Após os testes, retorne `ENABLE_FB_TEST = "false"` para evitar postagens acidentais em execuções futuras do pytest.

---

## Whitelist de obras permitidas no Facebook

Nem todas as obras são postadas no Facebook — apenas as que estiverem na coleção `obrasPermitidasFB` do MongoDB Atlas.

Para adicionar uma obra via bot Discord, use o comando:
```
/adicionar_obra_permitida_fb
```

Para listar as obras atualmente permitidas:
```
/listar_obras_permitidas_fb
```

O nome deve ser **exatamente igual** ao `titulo_obra` registrado no Atlas.
