# Pesquisa web: causas documentadas de JSON UI custom sumir/falhar sem erro (Bedrock)

Contexto da pesquisa: override de `server_form` (ActionFormData) via JSON UI, cliente Bedrock 1.26.44, bug relatado = UI custom some silenciosamente e cai pra lista vanilla, sem `[UI][error]` no Content Log.

Nenhuma causa abaixo foi inventada — cada uma tem fonte. Onde a fonte não descreve "sem erro" explicitamente, isso é indicado.

---

## 1. Migração de telas para Ore UI (hardcoded, não modificável por resource pack)

**Fonte:** https://minecraft.wiki/w/Ore_UI ; https://wiki.bedrock.dev/json-ui/json-ui-intro ; https://github.com/Mojang/ore-ui/issues/147 ; https://feedback.minecraft.net/hc/en-us/community/posts/42684483199245-Ability-to-disable-Ore-UI-in-favor-for-json-UI-customizability

**Sintoma relatado:** telas que antes aceitavam customização via JSON UI passam a ignorar completamente o resource pack, mostrando a versão padrão nova — sem nenhum erro, porque tecnicamente não há nada "errado": a tela simplesmente não lê mais o JSON UI.

**Causa:** Mojang está migrando telas do JSON UI (legado, moldável por resource pack) para o Ore UI (React/Coherent Gameface, hardcoded). A wiki afirma textualmente: "JSON UI is being deprecated in favor of Ore UI, and any add-on using JSON UI will eventually break" e "Ore UI is hard-coded and cannot be modified by resource packs". A migração acontece tela por tela, silenciosamente, entre updates — não é opt-in nem hoje reversível (pedidos de toggle seguem abertos e recusados, ver issue #147 e o post de feedback).

**Como detectar:** comparar comportamento entre versões do cliente; se a tela nunca aparece customizada em nenhuma condição (não é intermitente por sessão, é por versão do cliente/plataforma), suspeitar de migração de tela para Ore UI nessa build específica.

**Como evitar/mitigar:** não depende do addon — é decisão da Mojang por tela. Mitigação possível: manter fallback funcional via `@minecraft/server-ui` puro (sem overrides visuais) para quando a tela alvo for migrada, e monitorar changelogs de cada versão (seção "User Interface") antes de atualizar o cliente de produção.

---

## 2. Mudança de escala unificada JSON UI + Ore UI na 1.26.0

**Fonte:** https://learn.microsoft.com/en-us/minecraft/creator/documents/update1.26.0?view=minecraft-bedrock-stable (Update Notes oficiais, seção "User Interface > UI Scaling")

**Sintoma relatado:** não há relato de terceiros linkando isso a sumiço de UI (não achei thread de fórum citando isso), mas é uma mudança confirmada oficialmente exatamente na branch de versão do cliente do projeto (1.26.x).

**Causa:** a nota oficial diz: "Consolidated JSON UI and Ore UI under one scaling approach", "Ore UI screens use full-integer scaling", "Revised scaling range: new defaults, new min/max", "Default scale uses DPI-based detection on handheld devices", "Minimum scale set to half the maximum scale value". Qualquer `anchor`/`offset`/`size` calibrado para o comportamento de escala antigo pode passar a renderizar fora da área visível ou com tamanho zero/negativo em certas resoluções — isso não gera `[UI][error]`, só um layout quebrado ou invisível.

**Como detectar:** testar a tela em resoluções/DPIs diferentes (principalmente handheld/mobile, onde a detecção por DPI mudou) e comparar client 1.25.x vs 1.26.x lado a lado.

**Como evitar:** evitar `size`/`offset` em pixels absolutos fixos; preferir unidades relativas (`%`, `sizing.frame_rescaling` etc. conforme wiki.bedrock.dev/json-ui) e testar explicitamente após cada bump de versão maior do cliente.

---

## 3. Binding de correspondência de título (title-text) falhando silenciosamente

**Fonte:** https://wiki.bedrock.dev/json-ui/modifying-server-forms ; https://wiki.bedrock.dev/json-ui/preserve-title-texts.html ; estrutura real em https://github.com/Mojang/bedrock-samples/blob/main/resource_pack/ui/server_form.json

**Sintoma relatado:** é o mecanismo padrão documentado para overrides de `server_form` — não é um "bug" no sentido de defeito, mas é a causa mais provável de fallback silencioso porque é assim que o sistema foi desenhado para funcionar.

**Causa:** a técnica oficial da wiki para diferenciar "meu form custom" do form vanilla é usar subtração de string no `#title_text`/binding, ex.: `(#title_text - 'wiki_form:') = #title_text` para decidir se o marcador está presente. Se o marcador no título não bater exatamente (encoding, espaço, caixa, caractere invisível, ou o título vindo de outro layer/idioma), a condição de binding simplesmente avalia como "não é meu form" e o painel vanilla é exibido — sem qualquer erro, pois do ponto de vista do motor nada falhou.

**Como detectar:** logar/depurar o valor exato de `#title_text` recebido (ex. via um label de debug temporário no JSON UI, ou testando o texto do título salvo no `ActionFormData.title()` byte a byte); testar com título contendo caracteres especiais, acentos ou strings vazias.

**Como evitar:** usar um marcador simples, estável e improvável de colidir (ex. prefixo ASCII fixo), validar em todos os idiomas/localizações usados, e evitar transformações de string (trim, lower-case) entre o JS que define o título e o binding que o lê.

---

## 4. Merge direto em controles vanilla / múltiplos pontos de entrada (colisão de nomes)

**Fonte:** https://wiki.bedrock.dev/json-ui/best-practices (texto espelhado em https://github.com/Bedrock-OSS/bedrock-wiki/blob/wiki/docs/json-ui/best-practices.md)

**Sintoma relatado:** UI customizada quebra depois de um update do Mojang, ou funciona em alguns pontos e não em outros, sem mensagem de erro clara.

**Causa:** a wiki afirma que copiar todo o conteúdo de um arquivo vanilla no pack e alterar pedaços é "fazendo JSON-UI errado" — quando a Mojang renomeia elementos internos, a referência do addon aponta pro nome antigo e simplesmente não casa com nada, then falha silenciosa. Também alerta que múltiplos pontos de injeção (`modify_json_ui` em vários locais) multiplicam o risco de colisão de nome, e que targeting de controles profundamente aninhados por path (`panel/bg_image/label`) quebra se um nome intermediário mudar.

**Como detectar:** revisar diffs do `server_form.json` vanilla entre versões do cliente (bedrock-samples no GitHub) após cada update; procurar por controles referenciados pelo addon que sumiram/mudaram de nome.

**Como evitar:** usar a propriedade `modifications` (insert_front/insert_back/etc.) em vez de sobrescrever o controle inteiro; manter um único ponto de entrada; trabalhar em namespace próprio (ex. `meuaddon:xxx`) em vez de reaproveitar namespace vanilla.

---

## 5. Arquivo/controle não registrado em `_ui_defs.json`

**Fonte:** https://wiki.bedrock.dev/json-ui/json-ui-documentation ; https://wiki.bedrock.dev/json-ui/json-ui-intro

**Sintoma relatado:** controle simplesmente não aparece, sem warning.

**Causa:** todo arquivo `.json` novo de UI precisa estar listado em `_ui_defs.json` do resource pack. Segundo a doc, arquivos vanilla e de outros packs já mesclados não precisam ser listados de novo — mas um arquivo novo do próprio addon que não é listado ali não é carregado pelo motor, e isso não gera erro no Content Log.

**Como detectar:** conferir manualmente se todo arquivo `ui/*.json` novo do pack está listado em `ui/_ui_defs.json`.

**Como evitar:** checklist de PR/build que valida que todo arquivo novo em `ui/` tem entrada correspondente em `_ui_defs.json`.

---

## 6. Cache de pack (produção vs. development folder / versão não incrementada)

**Fonte:** https://wiki.bedrock.dev/guide/troubleshooting ; https://bugs-legacy.mojang.com/browse/MCPE-153925 ("Client can overwrite/corrupt resource packs...")

**Sintoma relatado:** editou o JSON UI, o comportamento não muda (ou volta ao antigo) mesmo após reload — intermitente, dependendo de como o pack foi instalado.

**Causa:** a wiki documenta "pack caching issues" — se o addon está nas pastas normais (`resource_packs`/`behavior_packs`) em vez de `development_resource_packs`/`development_behavior_packs`, o jogo pode continuar usando arquivos antigos mesmo após a edição. Separadamente, o cliente identifica packs por UUID+versão do `manifest.json`; se o conteúdo muda mas a versão não é incrementada, o cliente pode manter uma cópia cacheada da versão anterior.

**Como detectar:** fechar e reabrir o Minecraft completamente após qualquer mudança; comparar timestamp/conteúdo do pack instalado vs. o pack fonte; verificar se o pack está em pasta de desenvolvimento.

**Como evitar:** desenvolver em `development_resource_packs`/`development_behavior_packs` (recarregam automaticamente); sempre incrementar `version` no `manifest.json` a cada mudança publicada em produção, inclusive em `world_resource_packs.json`.

---

## 7. Ordem/prioridade entre múltiplos resource packs no mesmo arquivo de UI

**Fonte:** https://www.mods4minecraft.com/blog/how-to-combine-addons-bedrock/ ; https://minecraft.wiki/w/Resource_pack

**Sintoma relatado:** customização funciona isoladamente mas some quando outro pack (ou pack de outro addon) também está ativo.

**Causa:** quando dois packs mexem no mesmo arquivo/elemento, o pack de maior prioridade na lista (`world_resource_packs.json`) vence integralmente para aquele arquivo — o outro é descartado por completo, não mesclado parcialmente. Isso não gera erro; o pack "perdedor" é simplesmente ignorado para aquele arquivo.

**Como detectar:** testar a UI customizada com apenas o pack do addon ativo, depois reativar os demais um a um, observando em qual combinação ela para de aparecer.

**Como evitar:** usar a propriedade `modifications` (que mescla em vez de substituir) sempre que possível; documentar/gerenciar explicitamente a ordem de prioridade quando o addon for combinado com outros.

---

## 8. Dependência de manifest.json (UUID/versão) incorreta entre behavior pack e resource pack

**Fonte:** https://learn.microsoft.com/en-us/minecraft/creator/reference/content/addonsreference/packmanifest?view=minecraft-bedrock-stable ; discussão comunitária em https://board.aternos.org/thread/95864-minecraft-bedrock-texture-pack-error/

**Sintoma relatado:** a lógica de override (que geralmente vive no behavior pack, via script) simplesmente não roda, e o form cai no comportamento padrão do `@minecraft/server-ui`.

**Causa:** a doc oficial define que uma dependência (`dependencies` no manifest) exige UUID exatamente igual ao `header.uuid` do pack referenciado, e versão compatível. Segundo troubleshooting comunitário, "missing dependency" tipicamente por UUID/versão batendo errado faz o pack dependente ser ignorado — o relato da comunidade indica que isso pode acontecer "silenciosamente" sem uma mensagem óbvia para quem não está olhando o Content Log com atenção.

**Como detectar:** conferir no Content Log entradas de "Pack depends on..." / dependência ausente; validar manualmente que o UUID declarado em `dependencies` no BP bate byte-a-byte com o `header.uuid` do RP, e que a versão declarada bate com a versão publicada.

**Como evitar:** manter script/checklist de build que compara UUIDs e versões entre os `manifest.json` do BP e do RP antes de empacotar.

---

## 9. Bug conhecido: tela de configurações do pack desativando o pack (corrigido na 1.26.20)

**Fonte:** https://learn.microsoft.com/en-us/minecraft/creator/documents/update1.26.20?view=minecraft-bedrock-stable ; changelog oficial https://feedback.minecraft.net/hc/en-us/articles/45400537384333-Minecraft-Bedrock-Edition-26-20-Changelog

**Sintoma relatado:** pack para de funcionar depois que o jogador abre a tela de configurações customizadas do pack (custom pack settings), sem erro visível — reportado e corrigido pela própria Mojang.

**Causa:** bug confirmado pela Mojang: "Fixed a bug where entering custom settings of a behavior pack screen disables the pack" (corrigido só na 1.26.20). Se o cliente de teste estiver numa build afetada, ou se existir uma regressão similar em versão posterior, isso desliga o pack (e toda a lógica de override) sem log de erro.

**Como detectar:** testar explicitamente o fluxo "abrir configurações do pack" antes/depois de reproduzir o bug relatado; verificar no menu de packs se o addon aparece como ativado após esse fluxo.

**Como evitar:** atualizar para 1.26.20+; evitar expor tela de configurações customizadas do pack se não for essencial; sempre re-testar ativação do pack depois de qualquer interação com o menu de packs.

---

## 10. Bindings/controles com falha silenciosa por design do próprio motor JSON UI

**Fonte:** https://wiki.bedrock.dev/json-ui/json-ui-documentation ; https://wiki.bedrock.dev/json-ui/best-practices

**Sintoma relatado:** grid/collection aparece vazio, controle não aparece, foco se perde — tudo sem log.

**Causa:** documentado como comportamento normal (não bug) do motor:
- `binding_type` inválido ou binding pra nome hardcoded inexistente: sem erro, simplesmente não aplica.
- `grid_item_template` inválido ou `collection_name` quebrado: coleção renderiza vazia.
- `visible: false` vs `ignored: true`: `visible:false` esconde mas ainda avalia (pode conflitar com binding que tenta reexibir); `enabled:false` no pai não esconde filhos, só trava interação — fácil de confundir com "sumiu".
- `focus_change_*` apontando pra `focus_identifier` inexistente: perda de foco sem log.
- Controle pai sem array `controls` explícito não exibe filhos.

**Como detectar:** revisão manual de cada binding/condição usada no override, comparando contra a lista de "silent failure points" acima; testar com valores de binding conhecidos e observar se o valor esperado realmente chega (ex. via cor de debug temporária).

**Como evitar:** preferir `ignored` a `visible:false` quando o controle deve realmente sumir da árvore; validar `binding_type` e nomes de coleção/template contra a documentação oficial (https://learn.microsoft.com/en-us/minecraft/creator/reference/content/jsonuireference/); nunca assumir que ausência de erro = binding correto.

---

## Fontes consultadas (lista consolidada)

- https://wiki.bedrock.dev/json-ui/json-ui-intro
- https://wiki.bedrock.dev/json-ui/best-practices
- https://wiki.bedrock.dev/json-ui/json-ui-documentation
- https://wiki.bedrock.dev/json-ui/modifying-server-forms
- https://wiki.bedrock.dev/json-ui/preserve-title-texts.html
- https://wiki.bedrock.dev/scripting/server-forms
- https://wiki.bedrock.dev/guide/troubleshooting
- https://wiki.bedrock.dev/guide/format-version
- https://github.com/Mojang/bedrock-samples/blob/main/resource_pack/ui/server_form.json
- https://github.com/Mojang/ore-ui/issues/147
- https://minecraft.wiki/w/Ore_UI
- https://feedback.minecraft.net/hc/en-us/community/posts/42684483199245-Ability-to-disable-Ore-UI-in-favor-for-json-UI-customizability
- https://learn.microsoft.com/en-us/minecraft/creator/documents/update1.26.0?view=minecraft-bedrock-stable
- https://learn.microsoft.com/en-us/minecraft/creator/documents/update1.26.20?view=minecraft-bedrock-stable
- https://feedback.minecraft.net/hc/en-us/articles/45400537384333-Minecraft-Bedrock-Edition-26-20-Changelog
- https://learn.microsoft.com/en-us/minecraft/creator/reference/content/addonsreference/packmanifest?view=minecraft-bedrock-stable
- https://bugs-legacy.mojang.com/browse/MCPE-153925
- https://www.mods4minecraft.com/blog/how-to-combine-addons-bedrock/
- https://minecraft.wiki/w/Resource_pack
- https://board.aternos.org/thread/95864-minecraft-bedrock-texture-pack-error/

Observação: não foram encontrados threads específicos e citáveis do Reddit (r/BedrockAddons, r/MCPE) nem issues no bugs.mojang.com batendo exatamente com "server_form falls back silently" — as buscas nesses canais retornaram apenas resultados genéricos ou fora do tema. As causas acima vêm de documentação oficial da Mojang/Microsoft e da Bedrock Wiki (comunidade técnica de referência do ecossistema), que é onde esse tipo de comportamento está de fato documentado.
