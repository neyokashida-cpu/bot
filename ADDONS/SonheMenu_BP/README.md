# SONHE Menu

Central de navegação do jogador — o `/menu`. Casa, Perfil, Status,
Conquistas, Diário, Configurações e Inventário já usam dados reais
(dynamic properties por jogador + scoreboard, sem rede, sem banco
externo). A **Auction House é a única exceção** — continua placeholder de
propósito: envolve dinheiro real de jogador, e a arquitetura de segurança
(`AUCTION_HOUSE.md`, na raiz do repo) ainda precisa ser aprovada antes de
qualquer código de transação.

Pack **local**, sem `@minecraft/server-net` — funciona mesmo se o
`SonheBridge_BP` não estiver instalado ou o módulo de rede não estiver
liberado no host.

## Módulos

- `scripts/casa.js` — uma Home por jogador (sem `/tpa`, sem homes
  múltiplas): `definirCasa`, `irParaCasa`, `temCasaDefinida`.
- `scripts/estatisticas.js` — blocos quebrados, mobs derrotados, mortes e
  primeira entrada, contados por eventos reais (`playerBreakBlock`,
  `entityDie`, `playerSpawn`). Auto-registra os listeners ao ser
  importado (ver `main.js`).
- `scripts/conquistas.js` — 6 conquistas calculadas só a partir de
  `estatisticas.js` (nada inventado), com timestamp de desbloqueio
  persistido.
- `scripts/diario.js` — registro cronológico real de marcos do jogador
  (primeira entrada, primeira casa definida), até 30 entradas.
- `scripts/configuracoes.js` — preferências por jogador; hoje só um
  toggle real (dica ao abrir o menu), sem toggles falsos.
- `scripts/inventario_resumo.js` — resumo leve (slots, total de itens,
  top 5 tipos) sem recriar a tela vanilla do inventário.

## ⚠️ Ordem dos packs (obrigatório)

Este pack precisa ficar **antes do `SonheChat_BP`** na ordem dos behavior
packs do mundo.

Motivo: o `SonheChat_BP` cancela toda mensagem de chat incondicionalmente
(`world.beforeEvents.chatSend`). Se ele carregar primeiro, o `!menu` deste
pack nunca chega a ser recebido — foi exatamente o bug que quebrou o
`!vincular` do `SonheBridge_BP` nesta mesma configuração, corrigido só
depois de reordenar os packs (Bridge/Menu antes do Chat).

## Como abrir o menu

- **`!menu`** no chat do jogo — sempre funciona, independe de qualquer
  toggle experimental. Rede de segurança garantida.
- **`/sonhe:menu`** — tentativa de comando real, registrado via
  `customCommandRegistry`. Bedrock não permite registrar um `/menu` "puro"
  (comandos customizados só existem namespaced) e esse recurso depende de
  um toggle experimental ("Custom Commands") que este projeto nunca usou.
  Se não funcionar no seu host, **não é bug** — o `!menu` continua valendo
  sempre. Se aparecer um aviso `[SonheMenu] não consegui registrar
  /sonhe:menu` no console do servidor, é exatamente esse caso.

## O que ele faz

- Tela principal com nome do jogador, Tag (scoreboard `sonhe_tag`, mesma do
  `SonheChat_BP`/`SonheBridge_BP`), moedas locais (`sonhe_moedas`) —
  rotuladas como "moedas locais" porque **não são** o saldo Statz oficial
  do Discord (esse vive só no bot, sem endpoint de consulta pelo jogo
  ainda) — e uma dica curta sorteada (desligável em Configurações).
- Botões: Minha Casa, Meu Perfil, Status, Inventário, Conquistas, Diário e
  Configurações mostram dado real do jogador. **Auction House** continua
  placeholder — ver `AUCTION_HOUSE.md`.
- Sem emoji Unicode nos textos (fonte do Bedrock não renderiza a maioria)
  — só texto puro e o glyph nativo do Minecoin.
- Navegação com "Voltar" em toda página secundária, e "Fechar" (além do X
  nativo do formulário).
- Fechar o menu (X ou "Fechar") nunca gera erro no console.

## Como adicionar um sistema novo no futuro

Em `scripts/menu.js`, o array `PAGINAS` tem um item por botão do menu
principal, cada um com `{ id, texto, aoAbrir(jogador) }`. Pra plugar um
sistema real (ex: Home de verdade), troque o `aoAbrir` do item
correspondente por um handler que chame a implementação real — não precisa
tocar em `abrirMenuPrincipal` nem nos outros botões.

## Se não funcionar

Sem rede nenhuma envolvida — se o pack carregar, `!menu` funciona sempre.
Único ponto de falha isolado é o `/sonhe:menu` (ver acima), e ele já é
tratado sem quebrar o resto.
