# SONHE Bridge (Discord)

Pack **separado** do SonheChat de propósito: se `@minecraft/server-net` não
estiver liberado no seu host, só esse pack fica sem efeito — o SonheChat
(boas-vindas + rank/tag local) continua funcionando normal.

## Antes de instalar
1. Abra `scripts/main.js` e edite as duas constantes marcadas `EDITAR AQUI`:
   - `BRIDGE_URL` — a URL pública do bot no Railway, sem `/` no final.
   - `BRIDGE_SECRET` — precisa ser **idêntico** ao `BRIDGE_SECRET` configurado
     no bot (variável de ambiente no Railway).
2. No painel do seu host Minecraft, confirme que dá pra:
   - Habilitar `@minecraft/server-net` no `permissions.json` do servidor
     (arquivo fora da pasta do mundo — normalmente só acessível por SFTP).
   - Ligar "Beta APIs"/experimental gameplay — esse toggle só pode ser
     ativado **na criação do mundo**, não dá pra ligar depois.
3. Instale num mundo de rascunho primeiro. É um módulo em preview: pode se
   comportar diferente dependendo da versão exata do Bedrock do seu servidor.

## O que ele faz
- Toda mensagem de chat no jogo é enviada por HTTP POST pro bot (`/minecraft-chat`).
- Mortes de jogador viram um embed em `chat-mine` com a causa (queda, lava,
  afogamento, etc — mesmas causas do vanilla).
- Entrada/saída no mundo viram um embed com uma mensagem sorteada (10
  variações cada).
- `!vincular` dentro do jogo gera um código de uso único e mostra só pro
  jogador que digitou — ele usa `/vincular <código>` no Discord pra confirmar
  o vínculo na hora, sem precisar de staff. Se o jogador tiver moedas no
  placar `sonhe_moedas`, elas são somadas ao Statz do Discord nesse momento
  (soma única, feita pelo bot — não é sincronização contínua).
- `/inventario` no Discord: o bot bota o pedido na fila, esse pack lê o
  inventário/equipamento do jogador (se ele estiver online agora) no próximo
  ciclo de polling e responde. Sempre somente leitura — não existe nenhum
  comando aqui que altere item, moeda ou inventário do jogador.
- A cada ~3 segundos (se houver jogador online), busca mensagens novas do
  Discord (`GET /discord-queue`) e mostra no chat do jogo.
- Se o bot estiver fora do ar ou o módulo não estiver habilitado, os erros
  ficam só no console do servidor — o jogo continua normal, sem travar.

## Se não funcionar
Não instale esse pack. O SonheChat_BP/RP não dependem dele pra nada.
