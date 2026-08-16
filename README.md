# SONHE — Bot

Bot do Discord do projeto SONHE (Team ANÚBIS). Discord.py + aiosqlite, com um
servidor HTTP embutido pra fazer ponte com o addon do Minecraft.

## O que já faz
- **Onboarding** (`greet.py`, `verification.py`, `regras.py`): recebe quem chega,
  libera acesso depois da leitura das diretrizes.
- **Tickets** (`tickets.py`): abertura por categoria, roteamento por cargo, SLA de 48h.
- **Sugestões** (`sugestoes.py`): auto-upvote em post novo no fórum.
- **Economia** (`economia.py`): XP/Statz por mensagem, `/perfil`, `/daily`, `/casar`.
- **Mines** (`mines.py`): jogo de apostas com multiplicador de odds justas.
- **Chat com IA** (`chat.py` + `persona.py`): Madotsuki, rodando em Claude Sonnet 5.
- **Status** (`status.py`): ping externo (RakNet) do servidor Bedrock a cada 5 min.
- **Vinculação Minecraft ↔ Discord** (`vinculacao.py`): `/vincular`, `/desvincular`,
  `/admin link`, `/admin unlink` — confirmação manual por staff (ver nota abaixo).
- **Bridge de chat** (`bridge.py`): servidor HTTP embutido que recebe mensagens do
  addon do Minecraft e repassa pro Discord, e vice-versa.

## Por que a vinculação e a bridge não são 100% automáticas ainda
O addon só consegue falar HTTP com o bot através de `@minecraft/server-net`, que em
ago/2026 ainda é um módulo pré-lançamento e só é ativado depois de liberado no
`permissions.json` do servidor Bedrock (fora da pasta do mundo — normalmente
acessível só via SFTP). Enquanto isso não estiver confirmado funcionando no seu
host, a vinculação fica manual (staff confirma com `/admin link`) e a bridge de
chat simplesmente não recebe nada do lado do jogo — mas também não quebra nada.

## Setup local

1. Crie o bot em https://discord.com/developers/applications
   - Ative os **Privileged Gateway Intents** → `SERVER MEMBERS INTENT` e
     `MESSAGE CONTENT INTENT` (esse último é necessário pro `chat.py` e pro `bridge.py`).
   - Copie o Token.
2. Pegue uma chave de API em https://console.anthropic.com (usada pela Madotsuki).
3. Instale as dependências:
   ```
   pip install -r requirements.txt
   ```
4. Copie `.env.example` para `.env` e preencha:
   ```
   cp .env.example .env
   ```
   - `BOT_TOKEN` — token do Discord.
   - `ANTHROPIC_API_KEY` — chave da Anthropic.
   - `BRIDGE_SECRET` — qualquer string aleatória longa (ex: `python -c "import secrets; print(secrets.token_hex(32))"`).
     Precisa ser **o mesmo valor** colado no `BRIDGE_SECRET` do `SonheBridge_BP/scripts/main.js`.
5. Preencha os IDs em `config.py` (guild, canais, cargos) — já vem preenchido com os
   IDs reais do servidor SONHE.
6. Rode:
   ```
   python main.py
   ```

## Deploy no Railway
1. Suba este código para um repositório Git (GitHub) e conecte o repositório ao Railway.
2. Nas variáveis de ambiente do serviço no Railway, defina `BOT_TOKEN`,
   `ANTHROPIC_API_KEY` e `BRIDGE_SECRET` (os mesmos valores do seu `.env` local —
   **não** suba o `.env` real pro Git).
3. Start command: `python main.py`.
4. O Railway define `PORT` automaticamente — o `bridge.py` já lê essa variável
   sozinho pra saber em qual porta escutar. Depois do deploy, anote a URL pública
   que o Railway gerar (Settings → Networking → Generate Domain): é o `BRIDGE_URL`
   que vai no addon.
5. `GET /health` na URL pública deve responder `{"status": "ok"}` — use isso como
   health check do serviço no Railway, se for configurar um.

## Addon do Minecraft
Duas pastas em `ADDONS/`:
- `SonheChat_BP` + `SonheChat_RP` — boas-vindas e chat com Rank/Tag local. **Não
  depende de internet**, instala normal em qualquer host.
- `SonheBridge_BP` — a ponte com o Discord. Depende de `@minecraft/server-net`
  (ver nota acima). Antes de instalar:
  1. Abra `SonheBridge_BP/scripts/main.js` e edite as duas constantes marcadas
     `EDITAR AQUI`: `BRIDGE_URL` (a URL do Railway) e `BRIDGE_SECRET` (igual ao do bot).
  2. Confirme no painel do seu host que dá pra habilitar `@minecraft/server-net`
     no `permissions.json` e que o mundo tem "Beta APIs"/experimental ligado.
  3. Instale o pack e teste num mundo de rascunho antes do servidor principal,
     já que é um módulo preview.

Se o passo 2 não for possível no seu host, não instale o `SonheBridge_BP` — o
`SonheChat_BP`/`RP` continuam funcionando normalmente sem ele.

## Teste antes de abrir ao público
1. Entre com uma conta secundária → confirme onboarding, cargo e embeds.
2. `/vincular <nome>` → confirme o código gerado → `/admin link` com outra conta
   de staff → confirme que `/perfil` mostra o vínculo.
3. Se instalou o `SonheBridge_BP`: mande uma mensagem no jogo → confirme que
   aparece em 💬・sala-de-estar. Mande uma mensagem em 💬・sala-de-estar →
   confirme que aparece no jogo em até ~3s.

## Próximos módulos (ainda não implementados)
- Conquistas e estatísticas (tempo jogado, blocos, mortes — o que o host expuser).
- Comandos de staff `/admin rank`, `/admin tag`, `/admin money`, `/admin xp`.
- Notificações automáticas (rank up, servidor on/off já existe via `status.py`).
- Infraestrutura de "fenômenos" (estrutura de dados, sem gerar conteúdo automático).
- Log estruturado de ações administrativas.

Cada um vira um novo cog em `cogs/`, sem tocar no que já existe.
