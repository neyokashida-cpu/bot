# Arquitetura de Auction House — Addon SONHE

> **Nota de premissa:** o termo "Cloudful" citado em pedidos anteriores não existe neste projeto — é resíduo de um prompt genérico. Este documento usa apenas os componentes reais: `SonheChat_BP`, `SonheBridge_BP` (HTTP via `aiohttp`, `cogs/bridge.py`), `SonheMenu_BP` (`/menu`, ActionFormData) e o SQLite do bot Discord (`database.py`, tabela `perfis`, colunas `xp`/`statz`).

**Status: proposta de arquitetura, aguardando aprovação. Nenhum código de transação foi escrito ainda.**

---

## Arquitetura

A Auction House (AH) é dividida em duas responsabilidades que **nunca se misturam**:

| Responsabilidade | Onde vive | Por quê |
|---|---|---|
| O item em si (escrow) | Minecraft — Dynamic Properties do **mundo** (`SonheMenu_BP`, via Script API `@minecraft/server`) | O bot Discord/SQLite não tem como representar um `ItemStack` real (encantamentos, durabilidade, NBT-like data). |
| O dinheiro (Statz) | Bot Discord — SQLite (`database.py`), tabela `perfis` | É a única economia real do projeto; scoreboard `sonhe_moedas` é local e não sincronizado, não serve como saldo oficial. |

Fluxo de rede: Minecraft → Bridge é **POST HTTP síncrono** (o addon espera a resposta na hora, igual ao padrão já usado em `/minecraft-vincular-solicitar`). Bridge → Minecraft continua só por **polling** (fila em memória, ~3s) — a AH não depende desse canal para nenhuma operação crítica, porque toda decisão de dinheiro é resolvida na mesma chamada síncrona que o addon já faz.

Para fechar um gap de segurança (ver seção *Sistema de segurança*), a Bridge passa a manter um **espelho leve dos anúncios** (`ah_anuncios`): apenas `listing_id`, vendedor, preço e status — nunca o item. Isso permite à Bridge validar o preço de forma independente, sem nunca guardar o `ItemStack`.

Componentes novos propostos:
- `SonheMenu_BP`: telas de AH (ActionFormData/ModalFormData), leitura/escrita de Dynamic Properties do mundo, rotina periódica de expiração (`system.runInterval`).
- `cogs/bridge.py`: 5 endpoints novos (listados em *Fluxos*/*Sistema de transações*).
- `database.py`: 2 tabelas novas (`ah_anuncios`, `ah_transacoes`), usando as funções já existentes `obter_vinculo_confirmado_por_nome` e `ajustar_statz`.

---

## Estrutura de dados

### 1. Item em escrow (Dynamic Property do **mundo**, uma por anúncio)

Chave: `sonhe_ah_item_<listingId>` (string, JSON serializado).

```json
{
  "listingId": "a1b2c3d4-e5f6-47a8-9b0c-1d2e3f4a5b6c",
  "vendedorNomeMinecraft": "Fulano123",
  "vendedorDiscordId": "111222333444555666",
  "criadoEm": 1755600000,
  "expiraEm": 1755686400,
  "item": {
    "typeId": "minecraft:diamond_sword",
    "amount": 1,
    "nameTag": "Espada do Fulano",
    "lore": ["Forjada em batalha", "+5 Sharpness"],
    "encantamentos": [{ "tipo": "sharpness", "nivel": 5 }],
    "durabilidade": { "dano": 10, "maxDurabilidade": 1561 }
  }
}
```

### 2. Índice de anúncios ativos (Dynamic Property do mundo, única)

Chave: `sonhe_ah_index` — necessária porque a Script API **não documenta um método para listar todas as dynamic properties existentes**; é preciso manter o índice manualmente.

```json
{ "ativos": ["a1b2c3d4-...", "f9e8d7c6-..."] }
```

### 3. Correio de itens pendentes (Dynamic Property por jogador, mundo)

Chave: `sonhe_ah_correio_<xuid>` — usado quando expiração/cancelamento não conseguem entregar o item direto no inventário.

```json
{
  "pendentes": [
    { "origem": "expiracao", "listingId": "a1b2c3d4-...", "item": { "...": "mesmo formato do item acima" } }
  ]
}
```

### 4. `ah_anuncios` (espelho de preço/status na Bridge, SQLite)

```sql
CREATE TABLE ah_anuncios (
  listing_id             TEXT PRIMARY KEY,
  vendedor_discord_id    TEXT NOT NULL,
  vendedor_nome_mc       TEXT NOT NULL,
  preco                  INTEGER NOT NULL,
  status                 TEXT NOT NULL DEFAULT 'ATIVO', -- ATIVO | VENDIDO | CANCELADO | EXPIRADO
  criado_em              TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  expira_em              TIMESTAMP NOT NULL,
  finalizado_em          TIMESTAMP
);
```

### 5. `ah_transacoes` (idempotência das transações de dinheiro, SQLite)

```sql
CREATE TABLE ah_transacoes (
  transaction_id         TEXT PRIMARY KEY,   -- UUID gerado no Minecraft
  listing_id             TEXT NOT NULL,
  comprador_discord_id   TEXT NOT NULL,
  vendedor_discord_id    TEXT NOT NULL,
  valor                  INTEGER NOT NULL,
  status                 TEXT NOT NULL DEFAULT 'PENDENTE', -- PENDENTE | CONCLUIDA | FALHOU
  criado_em              TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  concluido_em           TIMESTAMP
);
```

`transaction_id PRIMARY KEY` é o mecanismo de idempotência: um retry de rede com o mesmo `transactionId` nunca gera um segundo débito/crédito.

---

## Fluxo de compra

1. Jogador abre AH → lista é construída a partir do **índice local** (Dynamic Properties do mundo) — exibição apenas, não é fonte de verdade de preço.
2. Confirma compra de um `listingId`. Addon gera `transactionId` (UUID) e faz **POST síncrono** `/ah/comprar-confirmar` com `{ transactionId, listingId, compradorNome }`.
3. Bridge busca `listingId` em `ah_anuncios`:
   - Não existe ou `status != 'ATIVO'` → responde `"anuncio_indisponivel"`.
4. Bridge confirma vínculo do comprador via `obter_vinculo_confirmado_por_nome` — se `minecraft_status != 'confirmado'` → `"comprador_sem_vinculo"`.
5. Checagem de idempotência: se `transactionId` já existe em `ah_transacoes` com `status='CONCLUIDA'` → repete a mesma resposta de sucesso, sem novo débito.
6. Transação SQL atômica (tudo ou nada):
   - `UPDATE ah_anuncios SET status='VENDIDO' WHERE listing_id=? AND status='ATIVO'` (afeta 0 ou 1 linha — resolve corrida entre dois compradores simultâneos: quem afeta 0 linhas recebe `"ja_vendido"`);
   - `ajustar_statz` negativo no comprador, **condicionado a saldo ≥ preço**;
   - `ajustar_statz` positivo no vendedor;
   - `INSERT` em `ah_transacoes` com `status='CONCLUIDA'`.
7. Resposta síncrona `{ status: "ok", preco, vendedorNome }`.
8. Só ao receber `"ok"`: addon remove o item do escrow, reconstitui `nameTag`/`lore`/encantamentos/durabilidade/`amount`/`typeId` e entrega ao inventário do comprador; remove `listingId` do índice.
9. Qualquer erro → nada muda no lado Minecraft; item permanece em escrow, listagem continua visível.

⚠️ **NÃO CONCLUÍDO**: se a resposta de sucesso se perder na rede *depois* do commit (dinheiro já trocou de mãos, item ainda em escrow), o addon precisa reenviar a mesma requisição (mesmo `transactionId`) para completar a entrega. Essa lógica de retry no lado Minecraft ainda não existe e precisa ser implementada e testada antes de produção.

---

## Fluxo de anúncio

1. Jogador abre AH → "Anunciar item", segurando o item na mão (ActionFormData não lê inventário arbitrário — ver *Estrutura de UI*).
2. Define preço (ModalFormData) e duração.
3. Addon gera `listingId` localmente.
4. **POST síncrono** `/ah/anuncio-criar` com `{ listingId, vendedorNome, preco, expiraEm }` — **antes de tocar no inventário**.
5. Bridge confirma vínculo do vendedor (`minecraft_status='confirmado'`); se não vinculado → `"sem_vinculo"`, addon aborta, item nunca saiu do inventário.
6. Se ok, Bridge insere linha `ATIVO` em `ah_anuncios`, responde `"ok"`.
7. Só então o addon remove o item do inventário, serializa em JSON e grava a Dynamic Property de escrow (`sonhe_ah_item_<listingId>`), adicionando `listingId` ao índice.
8. Confirmação visual ao jogador.

⚠️ **NÃO CONCLUÍDO**: existe uma janela entre o passo 6 (mirror `ATIVO` criado na Bridge) e o passo 7 (escrow gravado no mundo). Uma queda do servidor Bedrock exatamente nesse intervalo deixaria um anúncio "fantasma" no mirror sem item correspondente no escrow. Não há hoje uma rotina de reconciliação entre os dois lados — precisa ser desenhada antes de produção.

---

## Fluxo de cancelamento

1. Vendedor abre "Minhas vendas", seleciona anúncio próprio com `status` local ATIVO.
2. **POST síncrono** `/ah/anuncio-cancelar` com `{ listingId, vendedorNome }` — marca `ah_anuncios.status='CANCELADO'` (nenhum Statz envolvido).
3. Só após confirmação da Bridge, addon devolve o item ao inventário do vendedor (reconstituído do escrow) e remove a listagem do índice/escrow.
4. Se a devolução ao inventário falhar (inventário cheio), o item vai para o correio (`sonhe_ah_correio_<xuid>`) em vez de se perder.

⚠️ **NÃO CONCLUÍDO**: a política exata de "inventário cheio no momento do cancelamento" (dropar no chão vs. correio vs. bloquear o cancelamento) ainda não foi decidida — proposta é usar o correio, mas isso depende do fluxo de expiração abaixo estar implementado primeiro.

---

## Fluxo de expiração

1. Rotina periódica no addon (`system.runInterval`, ex. a cada poucos minutos) percorre `sonhe_ah_index`.
2. Para cada anúncio, compara `expiraEm` (do JSON de escrow) com o tempo atual.
3. Se expirado: **POST síncrono** `/ah/anuncio-expirar` com `{ listingId }` → Bridge marca `ah_anuncios.status='EXPIRADO'` (sem Statz envolvido).
4. Após confirmação, addon tenta devolver o item:
   - Vendedor online no mundo → entrega direta no inventário.
   - Vendedor offline → grava em `sonhe_ah_correio_<xuid>`, entregue no próximo `playerSpawn`.
5. Remove `listingId` do índice de ativos e do escrow.

⚠️ **NÃO CONCLUÍDO**: o mecanismo de correio (`sonhe_ah_correio_<xuid>` + entrega em `playerSpawn`) ainda não existe no addon hoje — é peça nova necessária para este fluxo e para o de cancelamento com inventário cheio.

---

## Sistema de escrow

- Escrow é **100% Minecraft**, nunca SQLite — o bot não representa `ItemStack`.
- Serialização cobre exatamente os campos confirmados na Script API: `typeId`, `amount` (bounds [1,255]), `nameTag` (≤255 chars), `lore` (≤20 linhas, ≤50 chars/linha), encantamentos (via `ItemEnchantableComponent`), durabilidade (via `ItemDurabilityComponent`, "só se aplica a itens data-driven").
- Persistência garantida pela documentação oficial: Dynamic Properties de mundo "são retidas entre reinícios do servidor".

⚠️ **NÃO CONCLUÍDO — limite de volume**: a documentação oficial **não define um número exato** de bytes máximos por propriedade/entidade/mundo (só existe `getDynamicPropertyTotalByteCount()`, descrito como ferramenta de diagnóstico, sem limite numérico). O único limite numérico documentado (1KB) é de `BlockDynamicPropertiesComponent`, uma classe diferente — não se aplica aqui. Comunidade relata informalmente ~10KB por propriedade, mas isso não está confirmado em fonte oficial. **Recomendação**: impor um teto artificial de anúncios simultâneos (ex. 200) até haver teste empírico real de quanto o mundo suporta sem degradar performance.

---

## Sistema de persistência

| Dado | Onde | Confirmação de persistência |
|---|---|---|
| Item em escrow, índice, correio | Dynamic Properties do **mundo** (Minecraft) | Documentado oficialmente: retidas entre reinícios do servidor. |
| Statz (saldo real) | SQLite, tabela `perfis` | Já existente, fonte única de verdade. |
| Espelho de anúncio (preço/status) | SQLite, tabela nova `ah_anuncios` | Novo, mas mesmo motor já usado pelo bot. |
| Transações (idempotência) | SQLite, tabela nova `ah_transacoes` | Novo. |
| Scoreboard `sonhe_moedas` | **Não usado pela AH** | Comentário explícito no código confirma que não é sincronizado continuamente — não é saldo oficial. |

Regra dura: **nunca duplicar fonte de verdade**. Preço e status oficiais do anúncio vivem em `ah_anuncios`; o item em si vive só no escrow Minecraft.

---

## Sistema de transações

Toda movimentação de Statz passa por uma única transação SQL atômica na Bridge, envolvendo três operações que só confirmam juntas (tudo ou nada):
1. `UPDATE ah_anuncios ... WHERE status='ATIVO'` (linha ganha a corrida de compra).
2. Débito condicional no comprador + crédito no vendedor via `ajustar_statz`.
3. `INSERT` em `ah_transacoes` com o resultado final.

Fluxos sem dinheiro (anunciar, cancelar, expirar) **não tocam `ah_transacoes`** — só atualizam `status` em `ah_anuncios`.

### Endpoints novos propostos em `cogs/bridge.py`

| Endpoint | Verbo | Payload | Resposta (sucesso) |
|---|---|---|---|
| `/ah/vinculo-status` | GET | query `?nome=<mcName>` | `{ vinculado: bool, discordId }` |
| `/ah/anuncio-criar` | POST | `{ listingId, vendedorNome, preco, expiraEm }` | `{ status: "ok" }` |
| `/ah/anuncio-cancelar` | POST | `{ listingId, vendedorNome }` | `{ status: "ok" }` |
| `/ah/anuncio-expirar` | POST | `{ listingId }` | `{ status: "ok" }` |
| `/ah/comprar-confirmar` | POST | `{ transactionId, listingId, compradorNome }` | `{ status: "ok", preco, vendedorNome }` |

Todos usam `obter_vinculo_confirmado_por_nome` para validar vínculo e `ajustar_statz` para mover saldo — nenhuma função nova de baixo nível é necessária em `database.py`, só as duas tabelas.

---

## Sistema de recuperação

Cenários de falha mapeados:

**a) Crash da Bridge durante a transação SQL de compra.** Como as 3 operações do passo "Sistema de transações" ficam dentro de uma única transação SQLite, um crash a meio nunca deixa `ah_transacoes` em `PENDENTE` de forma persistida — ou commitou tudo, ou nada. ⚠️ **NÃO CONCLUÍDO**: isso depende de a transação SQL ser implementada corretamente (BEGIN/COMMIT explícito envolvendo os três statements); precisa ser testado com kill controlado do processo antes de confiar em produção.

**b) Resposta de sucesso perdida na rede (dinheiro já trocou, item não entregue).** Resolvido por idempotência: addon reenvia com o mesmo `transactionId`; Bridge reconhece `CONCLUIDA` e responde `"ok"` de novo, permitindo completar a entrega sem duplicar débito/crédito.

**c) Queda do processo Minecraft entre marcar item como removido do escrow e efetivamente dar ao comprador.** ⚠️ **NÃO CONCLUÍDO**: não existe hoje um mecanismo de "write-ahead" do lado Minecraft. Mitigação proposta (não implementada): antes de tentar entregar, gravar o item pendente no correio do comprador (`sonhe_ah_correio_<xuid>`) e só depois remover do escrow ativo — assim, se a entrega falhar, o item nunca se perde, só fica pendente de entrega.

**d) Anúncio "fantasma"** (mirror criado na Bridge sem escrow correspondente, ou vice-versa) — ver ⚠️ no *Fluxo de anúncio*. Sem rotina de reconciliação hoje.

---

## Sistema de segurança

Validações que a Bridge **deve** fazer, nunca confiando no addon Minecraft como fonte de verdade de dinheiro:
- Revalidar vínculo confirmado (`minecraft_status='confirmado'`) do comprador em toda compra e do vendedor em todo anúncio — nunca aceitar um `discordId` enviado cru pelo addon sem cruzar pelo nome via `obter_vinculo_confirmado_por_nome`.
- **Preço e status do anúncio vêm sempre de `ah_anuncios` (mirror na Bridge), nunca de um valor enviado pelo addon no momento da compra.** Esse é o ponto que fecha o principal risco: sem o mirror, a Bridge teria de confiar num "valor" enviado pelo Minecraft, que — mesmo o addon correndo dentro do processo do servidor dedicado (não código de cliente) — ainda é um processo separado, sujeito a bug ou exploit local.
- Validar `valor > 0`, saldo suficiente antes de debitar, formato de `listingId`/`transactionId`.
- `nameTag`/`lore` já ficam limitados pelos próprios limites nativos do item (255 chars / 20×50 chars) — reduz superfície de abuso via string gigante.
- Rate-limit por jogador nos endpoints de anúncio/compra (não especificado no código atual — ⚠️ **NÃO CONCLUÍDO**, recomenda-se adicionar).

**Regra de vínculo — pode comprar sem vínculo confirmado?**
**Não.** A pergunta original só cobria venda, mas a mesma restrição vale para compra, pela mesma razão raiz: Statz só existe atrelado a um perfil Discord vinculado (`perfis`, acessado via vínculo). Um jogador sem `minecraft_status='confirmado'` não tem de onde debitar — criar um saldo "anônimo" paralelo no lado Minecraft duplicaria a fonte de verdade da economia (proibido pela regra de persistência acima) e recriaria o mesmo problema do `sonhe_moedas`, que já existe e sabidamente não é confiável. Portanto: **navegar/ver anúncios é livre; comprar e vender exigem vínculo confirmado.**

---

## Estrutura de UI

Reaproveitando o padrão `ActionFormData`/`ModalFormData` já usado em `SonheMenu_BP`:

- **Menu AH** (ActionFormData): "Ver anúncios" / "Anunciar item" / "Minhas vendas".
- **Ver anúncios** (ActionFormData paginado): um botão por anúncio (nome do item + preço + vendedor), com paginação "Próxima página"/"Anterior" — ActionFormData tem limite prático de botões por tela.
- **Detalhe do anúncio** (MessageFormData): texto reconstruído do JSON (nome, lore, encantamentos) + botões "Comprar" / "Voltar".
- **Anunciar item**: como ActionFormData/ModalFormData não renderizam o inventário, o padrão é o jogador **segurar o item na mão** antes de abrir "Anunciar"; ModalFormData pede preço (TextField) e duração (Dropdown/Slider).
- **Minhas vendas** (ActionFormData): lista dos próprios anúncios ATIVOS com botão "Cancelar" por item.
- Toda ação irreversível (comprar, cancelar) passa por confirmação via MessageFormData (sim/não).

⚠️ **NÃO CONCLUÍDO**: exibir a textura real do item (ícone) nas telas exigiria UI customizada via `json_ui` no resource pack — fora do padrão atual (`ActionFormData` só mostra texto), não pesquisado nem confirmado como viável neste projeto.

---

## Por que essa arquitetura é segura?

- **O item nunca existe em dois lugares ao mesmo tempo**: sai do inventário só depois que a Bridge confirma o vínculo do vendedor (fluxo de anúncio); só entra no inventário do comprador depois que a Bridge confirma o pagamento (fluxo de compra). Se a Bridge responder erro, nada muda no lado Minecraft.
- **Dinheiro só se move dentro de uma transação SQL atômica**, com idempotência garantida por `transactionId` como `PRIMARY KEY` — um retry de rede nunca duplica débito/crédito.
- **Corrida entre dois compradores** é resolvida pelo padrão `UPDATE ... WHERE status='ATIVO'`: só um comprador consegue afetar a linha; o outro recebe `"ja_vendido"` sem qualquer efeito colateral.
- **Preço e status oficiais do anúncio vivem na Bridge** (`ah_anuncios`), não no que o addon envia — fecha o gap de confiar em valor client-enviado, mesmo o addon rodando server-side.
- **Vínculo Discord confirmado é pré-requisito simétrico** para comprar e vender, porque ambos exigem Statz, que só existe atrelado a um perfil vinculado — evita recriar uma economia paralela não confiável (como já é o caso do scoreboard `sonhe_moedas`).
- **Pontos que restam como risco residual estão explicitamente marcados com ⚠️ NÃO CONCLUÍDO** (retry de entrega no Minecraft, reconciliação mirror↔escrow, correio de itens pendentes, limite real de Dynamic Properties, rate-limit) — nenhum deles é assumido como resolvido; todos exigem decisão e teste antes de qualquer linha de código de produção.
