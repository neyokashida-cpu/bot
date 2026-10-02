# Cache do cliente Bedrock e JSON UI (server_form) — pesquisa web

Contexto: mesma versão de pack, mesmo build do jogo, às vezes renderiza a UI custom
(override de `server_form`) e às vezes volta pro form vanilla, sem editar nada entre
as tentativas. Pesquisa feita via WebSearch/WebFetch em 2026-08-31.

Nota de método: `bugs.mojang.com` hoje serve um SPA (React) que não renderiza conteúdo
para fetch simples/curl — a chamada direta só devolve o shell HTML vazio (confirmado
baixando a página crua: 19 linhas, só `<div id="root">`). Para extrair tickets reais
usei snapshots do Wayback Machine (`web.archive.org/web/2022id_/...`), que preservam o
HTML server-side-rendered do Jira antigo. Isso está marcado explicitamente abaixo.
Reddit (`reddit.com`) está bloqueado tanto para WebSearch (domain filter rejeitado pela
API) quanto para WebFetch nesta sessão — não há requests bem-sucedidos ao Reddit ou ao
old.reddit.com aqui; qualquer afirmação sobre "consenso da comunidade em r/BedrockAddons"
abaixo é inferência, não citação direta de um post específico.

---

## 1) Reload de JSON UI: sair/entrar do mundo vs. reiniciar o app inteiro

**Confirmado por fonte** — Bedrock Wiki, página *Project Setup*:

> "When you make changes within these folders [`development_behavior_packs` e
> `development_resource_packs`], you can exit and re-enter a world with the packs
> applied, to automatically reload the content. This allows you to quickly test your
> add-on without reloading Minecraft."
> ("A quicker shortcut for reloading a world is the `/reload all` command.")

Fonte: https://wiki.bedrock.dev/guide/project-setup
(texto verificado na fonte crua: https://raw.githubusercontent.com/Bedrock-OSS/bedrock-wiki/wiki/docs/guide/project-setup.md)

Ou seja: para packs em pastas `development_*`, sair/reentrar no mundo (ou `/reload all`)
já recarrega o conteúdo — **não precisa fechar o app**. Isso vale para conteúdo em geral
(inclui JSON UI, já que é só mais um arquivo do resource pack).

**Contraponto confirmado por fonte** — a mesma wiki, página *Troubleshooting*, recomenda
como primeira linha de defesa:

> "First, you should always reload Minecraft. That means fully closing the game and then
> reopening it. This can catch many errors, especially those related to assets that are
> accessed via a filepath, such as textures or loot tables."

Fonte: https://wiki.bedrock.dev/guide/troubleshooting
(fonte crua: https://raw.githubusercontent.com/Bedrock-OSS/bedrock-wiki/wiki/docs/guide/troubleshooting.md)

**Inferência minha**: a wiki não separa explicitamente "JSON UI" como categoria com
comportamento de reload diferente de outros assets — trata tudo sob o guarda-chuva de
"pack caching". Não encontrei nenhuma fonte que documente JSON UI como um caso especial
(compilado à parte, cacheado separadamente do resto do resource pack).

---

## 2) Cache de UI compilada / packcache — onde fica no Windows

**Confirmado por fonte** — Minecraft Wiki, página *Bedrock Edition cache files*, lista o
diretório `packcache`:

> "packcache: Contains downloaded Marketplace content similar to `premium_cache` in
> com.mojang. — resource: Resource packs."

Fonte: https://minecraft.wiki/w/Bedrock_Edition_cache_files

**Confirmado por fonte** (ticket Mojira, ver seção 4 abaixo) — o mesmo diretório
`packcache` também é usado para armazenar em cache resource packs **baixados de um
servidor** (não só conteúdo de Marketplace): o bug MCPE-153925 descreve explicitamente
pastas dentro de `/packcache` sendo criadas por download de pack de servidor, e que
apagar um pack cacheado em `Settings > Storage` remove a pasta correspondente em
`/packcache`.

Fonte: https://bugs.mojang.com/browse/MCPE-153925 (conteúdo recuperado via
https://web.archive.org/web/2022id_/https://bugs.mojang.com/browse/MCPE-153925 —
snapshot de 2022, ticket ainda "Awaiting Response"/não resolvido nessa versão)

**Caminhos no Windows** (via WebSearch, não confirmado por fetch direto — tratar como
plausível/secundário, não como citação literal de uma página oficial única):
- `%LOCALAPPDATA%\Temp\Minecraft Bedrock\minecraftpe` (build de preview/algumas
  instalações)
- `C:\Users\<user>\AppData\Local\Packages\Microsoft.MinecraftUWP_8wekyb3d8bbwe\LocalCache\minecraftpe\packcache\resource`
  (build UWP/Store, o caminho mais comum)

**Não existe um "cache de JSON UI compilado" separado e documentado** — não encontrei
nenhuma fonte (oficial, wiki de criadores, ou bug tracker) que descreva um artefato
binário/compilado de JSON UI cacheado à parte do resource pack em si. O que existe e É
documentado é cache do **pack inteiro** (o .zip/pasta baixado e processado), não um
cache específico do subsistema de UI.

**Como limpar** (confirmado por fonte, via resumo da mesma página da Minecraft Wiki):
limpar em `Settings > Storage` no próprio jogo (Marketplace/download cache), que remove
as pastas de UUID aleatório de forma automática.

---

## 3) Bump de versão no manifest.json força recarga — sozinho é suficiente?

**Confirmado por fonte** (Bedrock Wiki, *Troubleshooting*, já citado acima): o problema
de "pack caching" — editar arquivo mas o jogo continuar usando o antigo — é atribuído
pela wiki a **não usar as pastas `development_*`**, e a solução recomendada é usar essas
pastas + sair/reentrar no mundo, não bump de versão.

**Inferência/secundário** (múltiplas fontes de terceiros, sem uma página oficial única
que eu tenha conseguido confirmar literalmente): para packs entregues **por um servidor**
via `world_resource_packs.json`, subir o número de `version` no `header` do
`manifest.json` (e casar esse número também na entrada do `world_resource_packs.json`)
é o mecanismo que sinaliza ao cliente "isto é uma versão diferente, não reaproveite o
cache anterior". Isso aparece de forma consistente em vários guias de hosting
(gameserverkings, oxygenserv, xgamingserver), mas nenhum deles é uma fonte
primária/Mojang — trate como prática de comunidade bem estabelecida, não como
especificação oficial confirmada.

**Resposta direta**: bump de versão sozinho tende a resolver o caso de "servidor
empurrando pack pro cliente" (força redownload/reprocessamento). Ele **não** é o
mecanismo relevante para o cenário de pack instalado manualmente/local (dev folders ou
`.mcpack` importado) — nesse caso o achado confirmado pela wiki é que o problema é de
pasta (`resource_packs`/`behavior_packs` "estáveis" vs `development_*`), não de número
de versão. Reinstalar o pack (remover e reimportar) é o fallback de força-bruta citado
por vários guias de hosting quando bump de versão não resolve — mas isso é inferência
consolidada de fontes secundárias, não uma citação única e literal.

---

## 4) Comportamento intermitente conhecido e documentado

**Confirmado por fonte — este é o achado mais forte da pesquisa.**

Ticket Mojira **MCPE-153925** — "*Client can overwrite/corrupt resource packs when
caching from host*" (criado 2022-01-11, tipo Bug, Affects Version 1.18.12 Hotfix,
Confirmation Status "Plausible", Resolution "Awaiting Response" no snapshot
consultado):

> "Steps to reproduce: ... If the error does not appear, clear Test A and Test B from
> cache and retry 3 (**the bug is timing related and thus unpredictable**)."
>
> "Probable cause: When caching resource packs, the game seems to use a Base64 encoded
> 8-byte timestamp ... as a string for the pack's cache folder name. ... if two packs
> complete the download at roughly the same time, both packs will be unzipped into the
> same folder due to time-based naming. This causes a race condition for overwriting
> duplicate files like the important 'manifest.json' ... Now, the game's resource pack
> cache list in memory and on the filesystem is out of sync."
>
> "Workaround: One can try to join the server once more. **The error will probably not
> appear and packs will load.**"

Fonte: https://bugs.mojang.com/browse/MCPE-153925
(conteúdo recuperado via https://web.archive.org/web/2022id_/https://bugs.mojang.com/browse/MCPE-153925,
pois a página ao vivo hoje é um SPA que não expõe o ticket a fetch automatizado)

Isso é evidência direta e documentada de que: (a) existe uma race condition real e
reconhecida pelo próprio tracker da Mojang no pipeline de cache de resource pack no
cliente Bedrock; (b) o sintoma documentado é **exatamente** "às vezes falha, às vezes
funciona, no mesmo cliente, sem mudar nada" — o próprio relator descreve como
"unpredictable"; (c) o cache em memória e o cache em disco podem ficar dessincronizados.

**Ressalva importante**: este ticket é especificamente sobre packs **baixados de um
host/servidor** (multiplayer), não sobre packs instalados localmente via dev folder.
Se o pack de vocês está em `development_resource_packs` local (sem vir de um servidor
dedicado empurrando o pack), esse ticket específico não se aplica tecnicamente — mas
serve como prova de que o Bedrock client tem histórico real e reconhecido de bugs de
race condition/timing no subsistema de cache de packs, o que sustenta a hipótese de
cache como causa raiz do sintoma relatado.

Também localizado, mas **menos relevante** (não é sobre cache, é sobre pack não conter
texturas novas de uma atualização do jogo):
- MCPE-85706 — "Resource Pack not updating new blocks, weapons, and tools added in
  1.16", Resolution "Incomplete". https://bugs.mojang.com/browse/MCPE-85706
  (via https://web.archive.org/web/2022id_/https://bugs.mojang.com/browse/MCPE-85706)

**Não confirmado / não localizado**: não encontrei um GitHub issue em
`Mojang/bedrock-samples` nem em `Bedrock-OSS/bedrock-wiki` tratando especificamente de
JSON UI com comportamento intermitente. Não encontrei threads de Reddit
(`r/BedrockAddons`) sobre o tema — Reddit está bloqueado para as ferramentas de busca/
fetch usadas nesta sessão (erro explícito da API ao tentar restringir por domínio, e
`old.reddit.com` recusou o fetch). Isso é uma lacuna de cobertura, não uma ausência
confirmada do fenômeno na comunidade.

**Inferência minha**: pedidos recorrentes na Feedback Hub da Mojang por um "botão de
reload/refresh" para resource/behavior packs (sem precisar sair do mundo ou reiniciar o
app) sugerem que a comunidade sente a falta de um mecanismo confiável de invalidação de
cache sob demanda — reforça indiretamente que o cache "gruda" de forma imprevisível:

- https://feedback.minecraft.net/hc/en-us/community/posts/360043131592-Add-an-option-to-Reload-Refresh-for-behavior-resource-packs-Feature-Request
- https://feedback.minecraft.net/hc/en-us/community/posts/4414505064845-Reload-Textures-In-game-Hotkey-in-Bedrock-Edition
- https://feedback.minecraft.net/hc/en-us/community/posts/360010846792--Bedrock-Be-Able-to-Move-Cached-Resources-to-Global-Resources

(Não consegui abrir o conteúdo completo do primeiro link — 403 ao fazer fetch — então
cito apenas o título/existência do pedido, não o teor dos comentários.)

---

## 5) Checklist de "força bruta" contra cache — recomendado por fontes de criadores

**Confirmado por fonte** (Bedrock Wiki, *Troubleshooting* + *Project Setup*, combinando
as duas páginas):

1. Ative o **Content Log** em `Settings > Creator` (mostra erros de path errado,
   componente com nome errado, JSON inválido a cada load do mundo). Atenção: "errors are
   not cleared between world loads" — um erro antigo pode continuar aparecendo mesmo
   depois de corrigido, então não confie em erro "sumido" sem recarregar de fato.
   Fonte: https://wiki.bedrock.dev/guide/troubleshooting
2. Confirme que o pack está em `development_resource_packs` / `development_behavior_packs`
   (não em `resource_packs`/`behavior_packs` "estáveis") — só assim sair/reentrar no
   mundo recarrega de verdade. Fonte: https://wiki.bedrock.dev/guide/project-setup
3. Use `/reload all` como atalho mais rápido que sair/reentrar no mundo inteiro.
   Mesma fonte acima.
4. Se o Content Log e o `/reload all` não resolverem, **feche o aplicativo Minecraft
   completamente e reabra** — a wiki chama isso de primeiro passo do troubleshooting
   geral, especialmente para bugs ligados a assets referenciados por filepath.
   Fonte: https://wiki.bedrock.dev/guide/troubleshooting
5. Valide o JSON com um linter (a wiki recomenda jsonlint.com) antes de assumir que é
   cache — JSON malformado é indistinguível de "não recarregou" só olhando o sintoma.
   Mesma fonte.

**Inferência consolidada de fontes secundárias de hosting** (gameserverkings,
oxygenserv, xgamingserver — não são fonte primária, tratar como prática de comunidade):
para pack entregue por servidor, bump de `version` no manifest **e** na entrada
correspondente de `world_resource_packs.json`, e como último recurso remover a entrada
do pack em `world_resource_packs.json` + apagar a pasta cacheada correspondente antes de
testar de novo.

**Inferência minha, apoiada pelo achado da seção 4**: como o MCPE-153925 mostra que o
próprio nome da pasta de cache pode colidir por causa de timing, um teste único que
"funcionou" ou "não funcionou" não é prova de nada — o procedimento correto de
força-bruta é repetir o join/reload **pelo menos 2-3 vezes seguidas** antes de concluir
se uma mudança pegou ou não, e preferir sempre reiniciar o app completo (não só sair do
mundo) quando o teste está inconclusivo.

---

## Resumo de confiabilidade das fontes usadas

| Fonte | Tipo | Confiabilidade |
|---|---|---|
| wiki.bedrock.dev (Project Setup, Troubleshooting) | Wiki de criadores, mantida pela comunidade Bedrock-OSS | Alta — texto verificado literalmente na fonte raw do GitHub |
| minecraft.wiki (Bedrock Edition cache files) | Wiki comunitária | Média-alta — conteúdo específico, mas não é fonte oficial da Mojang |
| bugs.mojang.com (MCPE-153925, MCPE-85706) | Bug tracker oficial da Mojang | Alta para o conteúdo do ticket (recuperado via Wayback Machine, snapshot 2022) — mas o **status atual/2026** do bug não pôde ser confirmado, pois o site ao vivo não é acessível a fetch automatizado |
| learn.microsoft.com (Pack Manifest reference) | Documentação oficial Microsoft/Mojang | Alta, mas não trata explicitamente de cache/versionamento em texto narrativo (é referência de schema) |
| feedback.minecraft.net | Fórum oficial de feedback | Baixa-média — só confirmei título/existência dos posts, não o conteúdo (403 no fetch) |
| Guias de hosting (gameserverkings, oxygenserv, xgamingserver) | Terceiros, não oficiais | Baixa-média — prática de comunidade consistente entre vários, mas não é fonte primária |
| Reddit (r/BedrockAddons) | Comunidade de criadores | Não acessível nesta sessão — bloqueado para WebSearch e WebFetch |
