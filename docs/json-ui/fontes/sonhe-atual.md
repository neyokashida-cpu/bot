# Auditoria SonheMenu_RP — estado atual (HEAD, pós 6a347a5)

Cliente alvo: Bedrock 1.26.44. Somente leitura — nenhum arquivo do pack foi alterado por esta auditoria.

Fontes lidas na íntegra: `ui/sonhe_forms.json`, `ui/sonhe_grid.json`, `ui/_ui_defs.json`, `manifest.json`,
`docs/JSON_UI_NOTAS.md`, mais `ADDONS/SonheMenu_BP/scripts/*.js`, `ADDONS/tools/audit_ui.py`,
`ADDONS/ADDONS.zip`, e o corpus vanilla em `c:/Users/Desktop/Documents/Nova pasta/assets/assets/resource_packs/vanilla/ui/`.

---

## 0. Achado de abertura — a causa real não está no JSON, está no deploy

`git diff 26e761f -- ADDONS/SonheMenu_RP` mostra que, entre o commit confirmado funcionando e o HEAD atual
(6a347a5), a única mudança **funcional** em qualquer arquivo carregado pelo jogo é:

```diff
-          "alpha": 0.7,
+          "alpha": 0.9,
```
(`ui/sonhe_grid.json:33`, dentro de `panel_bg`). Fora isso: `manifest.json` só teve a versão incrementada
(35→36, o mesmo padrão de +1 que acontece em **todo commit anterior**, inclusive nos que funcionaram), e
`tools/validar_ui.js` mudou (script de dev, não é carregado pelo engine). Um `alpha` de `image` é um float
sem efeito estrutural — não há mecanismo conhecido do JSON UI pelo qual mudar esse número reverta a tela
inteira pro form vanilla. `ADDONS/ADDONS.zip` também é byte a byte idêntico ao HEAD do repo, então não é
drift de empacotamento.

**Causa real, CONFIRMADA por arquivos deste computador** (não é só o repo — é o próprio Bedrock instalado):
existem dois mundos locais com este pack instalado, e um deles está **travado 26 versões atrás**:

| Mundo (pasta) | `levelname` | `resource_packs/SonheMenu_RP/manifest.json` | `world_resource_packs.json` | Última cópia do pack |
|---|---|---|---|---|
| `minecraftWorlds/k+V-yUhs2RQ=` | **ClaudeAurudoLegal** | `version: [1,0,36]` | pina `[1,0,36]` | 27/ago 12:01 — **em dia com o HEAD** |
| `minecraftWorlds/RCWd1qdM+y4=` | **Server** | `version: [1,0,10]` | pina `[1,0,10]` | 24/ago 13:13 — **26 versões atrasado** |

E o cache de download do cliente
(`AppData/Local/Temp/Minecraft Bedrock/minecraftpe/packcache/resource/44HgOvx85xc=/manifest.json`) também
está em `version: [1,0,10]`, timestamp 24/ago 12:58 — a mesma janela de poucos minutos da cópia parada no
mundo **Server**. `packcache` só é populado quando um cliente **entra como convidado num servidor/mundo
hospedado**, baixando o pack dele — ou seja, esse é exatamente o par cliente↔servidor que ficou parado.

Abri o `ui/sonhe_forms.json` que está de fato instalado no mundo **Server** (v1.0.10) e ele é uma build
**anterior a todos os fixes registrados no `JSON_UI_NOTAS.md`**: usa `"nine_slice_size"` com a grafia errada
(item 3 do checkpoint, documentado como `Unknown property` nesta engine), referencia
`textures/ui/sonhe/panel_frame` diretamente como fundo do `long_form_panel` (o PNG 1254×1254 sem alpha que
o próprio checkpoint describe como "estica feito nuvem"), e tem `main_screen_content` redeclarado com
`size:["100%","100%"]` — nada disso existe mais no HEAD atual. Ou seja: **tudo que foi corrigido entre
24/ago e 27/ago (tile reescrito, tema dark, nine-slice, etc.) nunca chegou no mundo Server** porque o pack
de dentro de `minecraftWorlds/RCWd1qdM+y4=/resource_packs/SonheMenu_RP/` nunca foi re-copiado.

`confidence: confirmado` — se o teste que motivou este relatório foi feito no mundo/servidor **Server** (ou
por um cliente que ainda tem esse pack em cache), a tela "voltar pra lista vanilla" não tem nada a ver com
o `alpha`: é uma build de 3 dias atrás, com bugs já conhecidos e corrigidos no repo, que nunca foi
reinstalada. **Ação recomendada antes de mexer em qualquer JSON de novo**: copiar
`ADDONS/SonheMenu_RP` (conteúdo atual, v1.0.36) por cima de
`minecraftWorlds/RCWd1qdM+y4=/resource_packs/SonheMenu_RP/`, e limpar o `packcache` do cliente que conecta
nesse mundo, antes de reabrir o jogo (ver skill `mcpe-pack-deploy` do próprio projeto).

---

## 1. Árvore de controles — estado atual completo

### 1.1 `ui/sonhe_forms.json` — namespace `server_form` (override do `long_form` vanilla)

```
long_form                                    panel, SEM size/anchor/offset/layer declarados
├─ sonhe_vanilla_form@common_dialogs.main_panel_no_buttons
│    size:[225,200]  layer:2  (anchor_from/anchor_to herdados do base = center/center)
│    $child_control: server_form.long_form_panel (vanilla, não sobrescrito)
│    bindings: [ {#title_text}, {view: NOT contém marcador → #visible} ]
└─ sonhe_custom_form@sonhe_forms.grid_screen
     size:[320,452] herdado do base  anchor:center/center herdado  layer:2
     bindings: [ {#title_text}, {view: contém marcador → #visible} ]
```

Marcador: `§d§r§e§a§m§r`, idêntico em `ADDONS/SonheMenu_BP/scripts/menu.js:26`
(`export const MARCADOR_GRADE = "§d§r§e§a§m§r";`) e em `sonhe_forms.json:24,37`.

### 1.2 `ui/sonhe_grid.json` — namespace `sonhe_forms` (tema grid + fallback lista)

```
grid_screen                                  panel  size:[320,452]  anchor:center/center
├─ panel_edge        image  size:["100%+2px","100%+2px"]  layer:0  texture white_background  alpha .5
├─ panel_bg          image  size:["100%","100%"]           layer:1  texture Black            alpha .9  ← mudou de .7
└─ grid_content@sonhe_forms.grid_stack                     layer:2

grid_stack                                   stack_panel vertical  size:[288,"100%c"]
                                              anchor:top_middle/top_middle  offset:[0,16]
├─ head_title@screen_title
├─ gap_a            panel  size:["100%",4]
├─ head_rule@title_rule
├─ gap_b            panel  size:["100%",8]
├─ head_body@screen_body
├─ gap_c            panel  size:["100%",12]
└─ tiles@tiles_grid

screen_title   label  size:["100%","default"]  offset:[0,-2]  layer:3  font MinecraftTen/UIFont
               bindings: [{#title_text, binding_type:global}]
title_rule     image  size:["100%",1]  layer:3  white_background tint
screen_body    label  size:["100%-8px","default"] max_size:["100%-8px",30]  layer:3
               bindings: [{#form_text}]

tiles_grid     type:grid  size:["100%","default"]  offset:[0,0]  layer:1
               grid_dimensions:[3,4]  grid_item_template:"sonhe_forms.tile" (sem @)
               collection_name:"form_buttons"  — SEM binding de contagem (proposital)

tile                                         panel  size:[96,96]  layer:1
├─ tile_hit@tile_button
├─ icon@tile_icon
└─ tile_name@tile_label

tile_button@common.button   size:[88,88]  anchor:center/center  layer:2
  bindings ordem: [#null collection(anchor), #null collection_details(anchor),
                   #form_button_text(dado), view NOT vazio→#visible]
  default_control/hover_control/pressed_control → face_default/face_hover/face_pressed
  ├─ face_default  panel 100%/100%  layer:1
  │   ├─ fd_bg    image Black  alpha .85  layer:1
  │   └─ fd_edge  image white_background 1px topo  alpha .18  layer:2
  ├─ face_hover    panel 100%/100%  layer:4
  │   ├─ fh_bg    image white_background tint(.16,.15,.20) alpha .95 layer:1
  │   └─ fh_edge  image white_background 1px topo alpha .55 layer:2
  └─ face_pressed  panel 100%/100%  layer:5
      ├─ fp_bg    image white_background tint(.24,.22,.30) alpha 1.0 layer:1
      └─ fp_edge  image white_background 1px topo alpha .75 layer:2

tile_icon   image  size:[32,32]  anchor:top_middle/top_middle  offset:[0,16]  layer:3
            SEM propriedade "texture" (chega por binding_name_override)
            bindings ordem: [#null coll(anchor), #null coll_details(anchor),
                             #form_button_texture→#texture, #form_button_texture_file_system→#texture_file_system,
                             view NOT(vazio ou 'loading')→#visible]

tile_label  label  size:["100%-10px","default"] max_size:["100%-10px",20]
            anchor:bottom_middle/bottom_middle  offset:[0,-10]  layer:3
            bindings ordem: [#null coll(anchor), #null coll_details(anchor),
                             #form_button_text→#form_button_text, view NOT vazio→#visible]

--- fallback não-ativo (comentado como plano B, não referenciado por sonhe_forms.json) ---
list_screen → list_stack → buttons_factory (stack_panel+factory) → row_button → row_icon_holder
  (mesma casca visual, sem cap de 12 itens; troca é manual: "sonhe_forms.grid_screen" → "sonhe_forms.list_screen")
```

Ordem dos bindings de âncora (`#null`) antes dos bindings de dado: **confirmado correto** em `tile_button`,
`tile_icon` e `tile_label` — respeita a regra de escopo/ordem do JSON UI. Não é um ponto frágil hoje.

---

## 2. `long_form` omite `size`? Qual o efeito real?

**Confirmado**: `ui/sonhe_forms.json:8-9` —
```json
"long_form": {
    "type": "panel",
    "controls": [ ... ]
}
```
Não há chave `size` (nem `anchor_from/anchor_to/offset/layer`) neste nó. Isso diverge da própria
`long_form` vanilla (`server_form.json:40`, `"size": [225, 200]`) e do padrão documentado na skill do
projeto (`.claude/skills/mcpe-json-ui`, seção 11), que mostra o wrapper de override do marcador com
`"size": ["100%", "100%"]` explícito — o mesmo que os addons de referência (ui4/ui5) fazem.

**Efeito real dado que `main_screen_content` vanilla é `size:[0,0]`** (`server_form.json:20-22`):
percentual de filho DIRETO de um pai `[0,0]` colapsa pra 0px. Mas isso só se propaga a filhos que usam
`%` **naquele nível**. Os dois ramos dentro de `long_form` não usam `%` ali:
- Ramo 1 herda `size:[225,200]` — pixel absoluto, fixado na própria instanciação.
- Ramo 2 herda `size:[320,452]` do `grid_screen` base via `@` — também pixel absoluto, herdado, não
  reescrito como `%`.

Como `common_dialogs.main_panel_no_buttons` declara `anchor_from`/`anchor_to: center/center` no próprio
base (`ui_template_dialogs.json:207-208`), e um retângulo `0×0` tem seu ponto "center" idêntico ao ponto
"top_left" (é o mesmo ponto, não importa a âncora), o wrapper `long_form` sem `size` acaba se resolvendo
exatamente no mesmo ponto que a árvore vanilla original resolvia — na prática, **inofensivo hoje**.

**Veredito**: omissão **confirmada**, efeito atual **provavelmente inerte** (`confidence: provável`) — não é
a causa de nenhum sumiço observado, porque não há filho `%` direto sob `long_form`. É, no entanto, uma
fragilidade latente: se algum dia alguém pendurar um terceiro filho, um label de debug, etc. direto em
`long_form` usando `%`, ele vai renderizar em 0px sem nenhum log. Ver item 3 da tabela de risco.

---

## 3. Pontos frágeis, ordenados por risco de sumiço silencioso

| # | Risco | Ponto | Evidência | Correção mínima |
|---|-------|-------|-----------|------------------|
| 1 | **ALTO** | Grid tem cap fixo de 12 células (`grid_dimensions:[3,4]`), sem scroll e sem binding de contagem, mas o BP consegue mandar até **13 botões** numa tela real | `ui/sonhe_grid.json:113` (`"grid_dimensions": [3, 4]`) vs `ADDONS/SonheMenu_BP/scripts/auction.js:388-404`: até 10 itens (`ITENS_POR_PAGINA=10`) + "Página anterior" + "Próxima página" + "Voltar" numa página do meio cheia = 13 `form.button()`. O 13º (que é justamente "Voltar", por ser adicionado por último) fica fora das 12 células e some sem erro nenhum — jogador fica sem botão de voltar naquela tela | Baixar `ITENS_POR_PAGINA` pra 9 (deixa espaço pros 3 botões de navegação), OU subir `grid_dimensions` pra `[3,5]` (15 células), OU trocar essa tela específica pro `list_screen` (fallback em coluna única, sem cap) |
| 2 | **ALTO (confirmado)** | Deploy manual sem reinstalação: o mundo **Server** (`minecraftWorlds/RCWd1qdM+y4=`) e o `packcache` do cliente que se conecta nele estão **travados em `version [1,0,10]`** (24/ago), 26 versões atrás do HEAD (`1,0,36`, 27/ago) | `.../RCWd1qdM+y4=/resource_packs/SonheMenu_RP/manifest.json` = `[1,0,10]`; `.../RCWd1qdM+y4=/world_resource_packs.json` pina `[1,0,10]`; `.../packcache/resource/44HgOvx85xc=/manifest.json` = `[1,0,10]`, timestamp 24/ago 12:58 (minutos antes da cópia no mundo, 13:13) — mesma dupla cliente↔servidor parada no tempo. O `ui/sonhe_forms.json` dessa cópia usa `"nine_slice_size"` com grafia errada e referencia `textures/ui/sonhe/panel_frame` direto, bugs já corrigidos no repo há dias. Por comparação, o mundo **ClaudeAurudoLegal** (`k+V-yUhs2RQ=`) está em `[1,0,36]`, em dia | Copiar `ADDONS/SonheMenu_RP` atual por cima de `minecraftWorlds/RCWd1qdM+y4=/resource_packs/SonheMenu_RP/` e limpar o `packcache` do cliente antes do próximo teste. Mais estrutural: nenhum `manifest.json` (RP ou BP) declara `"dependencies"` entre si — o acoplamento é 100% implícito (marcador `§d§r§e§a§m§r` + paths de textura hardcoded), então o engine não avisa quando um lado fica pra trás do outro |
| 3 | **MÉDIO** | `long_form` (o override em si) omite `size`, diferente do vanilla e da própria skill do projeto | `ui/sonhe_forms.json:8-9` (ver seção 2 completa acima) | `"size": ["100%", "100%"]` no nó `long_form`, sem mudar mais nada — corrige a divergência de padrão sem alterar comportamento observável hoje (é rede de segurança pra edições futuras, não um fix de bug ativo) |
| 4 | **MÉDIO** | Dois validadores estáticos no repo se contradizem: `tools/validar_ui.js` (git-tracked, alinhado ao `JSON_UI_NOTAS.md`) roda limpo; `tools/audit_ui.py` (não rastreado, `ADDONS/tools/`) aplica uma regra **já revogada** pela "Rodada 2" de pesquisa | `python ADDONS/tools/audit_ui.py ADDONS/SonheMenu_RP` retorna `ERRO ui/sonhe_grid.json:/tiles_grid: type:grid + collection_name (proibido pela regra do projeto)` — mas `JSON_UI_NOTAS.md` linhas 90-96 documenta que `type:grid` + `grid_dimensions` + `collection_name` **é o padrão que funciona**, e a proibição real é `grid_dimensions` junto de `#maximum_grid_items`. O mesmo script também acusa `binding_name desconhecido '#null'` em 7 lugares — `#null` é o idiom padrão da Mojang pra âncora de collection, não um erro | Apagar `audit_ui.py` ou atualizar a tabela `PROP_PROIBIDA`/`NS_VANILLA` dele pra refletir a Rodada 2; caso contrário, alguém vai "corrigir" o grid de volta pro padrão `stack_panel+#maximum_grid_items` que já foi testado e comprovadamente NÃO popula |
| 5 | **BAIXO** | Subtração de string sobre `#title_text` (`((#title_text - '§d§r§e§a§m§r') = #title_text)`) não tem nenhum precedente no corpus vanilla literal | Grep de padrão de subtração de string (`'...' - '...'`, `#var - '...'`) em todo `resource_packs/vanilla/ui/*.json`: 1 arquivo bate (`ui_common.json:7202`), e é falso-positivo — é um **comentário** sobre quebra de linha de tooltip, não uma expressão. Contagem real de uso do operador: **0** em 208 arquivos vanilla | Nenhuma ação agora — funciona no estado confirmado e é padrão documentado na bedrock-wiki e usado por addon terceiro real (Chest-UI). Só re-testar esse binding se o `min_engine_version` subir |
| 6 | **BAIXO** | `panel_frame.png`/`.json` e `tile_frame.png`/`.json` (~2.1 MB juntos) existem em `textures/ui/sonhe/` mas não são referenciados por nenhum controle atual | `grep "texture"` em `ui/*.json` só retorna `textures/ui/white_background` e `textures/ui/Black` (texturas do engine, não do pack) — nenhuma menção a `sonhe/panel_frame` ou `sonhe/tile_frame`. Tema atual é declaradamente "sem asset custom" (`ui/sonhe_grid.json:4`) | Peso morto, sem risco de sumiço de UI. Remover do pacote, ou manter com nota clara de "não reativar sem re-fatiar nine-slice" (`JSON_UI_NOTAS.md:53-56` já documenta que essas PNGs são 1254×1254 RGB sem alpha e esticam mal) |

---

## 4. Texturas referenciadas vs. existentes em `textures/ui/sonhe/`

Conteúdo real do diretório:

| Arquivo | Tamanho |
|---|---|
| `casa.png` | 630 bytes |
| `panel_frame.json` | 60 bytes |
| `panel_frame.png` | 1.132.170 bytes (~1,08 MB) |
| `placeholder.png` | 882 bytes |
| `tile_frame.json` | 60 bytes |
| `tile_frame.png` | 972.143 bytes (~0,93 MB) |

Nenhum controle em `ui/sonhe_forms.json`/`ui/sonhe_grid.json` referencia `textures/ui/sonhe/*` diretamente
— o ícone do tile (`tile_icon`) é um `image` sem `texture` fixo, alimentado em runtime via
`binding_name_override` (`#form_button_texture → #texture`). As strings reais que populam esse valor vêm do
BP:

```
ADDONS/SonheMenu_BP/scripts/menu.js:33   const ICONE_CASA = "textures/ui/sonhe/casa";
ADDONS/SonheMenu_BP/scripts/menu.js:34   const ICONE_PLACEHOLDER = "textures/ui/sonhe/placeholder";
ADDONS/SonheMenu_BP/scripts/auction.js:23    const ICONE_PLACEHOLDER = "textures/ui/sonhe/placeholder";
ADDONS/SonheMenu_BP/scripts/conquistas.js:12 const ICONE_PLACEHOLDER = "textures/ui/sonhe/placeholder";
```

Ambas (`casa`, `placeholder`) **existem** no diretório. `confidence: confirmado` — **nenhuma textura
referenciada está faltando**. As duas texturas extras que existem no diretório (`panel_frame`, `tile_frame`)
é que estão **sem referência** (item 6 da tabela acima) — situação inversa à perguntada, mas vale registrar.

---

## 5. `manifest.json` declara `dependencies`?

**Não.** Conteúdo integral de `ADDONS/SonheMenu_RP/manifest.json`:

```json
{
    "format_version": 2,
    "header": {
        "name": "SONHE Menu (Recursos)",
        "description": "Ícones do menu central do SONHE (textures/ui/sonhe/*).",
        "uuid": "b71a84eb-d21e-4460-bb7c-eb9758d1ede4",
        "version": [1, 0, 36],
        "min_engine_version": [1, 21, 50]
    },
    "modules": [
        {
            "description": "Texturas e JSON UI dos forms do /menu",
            "type": "resources",
            "uuid": "87eac085-7dca-4c21-9682-0dc8c2717aef",
            "version": [1, 0, 36]
        }
    ]
}
```

Sem chave `dependencies`. `ADDONS/SonheMenu_BP/manifest.json` também não referencia a UUID deste RP — só
declara dependências de módulo de script (`@minecraft/server`, `@minecraft/server-ui`,
`@minecraft/server-net`). Risco avaliado no item 2 da tabela da seção 3.

---

## 6. Resumo do histórico (para rastreabilidade)

```
6a347a5 fix: unifica opacidade do fundo, sobe alpha 0.7 -> 0.9        ← HEAD, "quebrado" relatado
0624580 fix: restaura sonhe_grid.json byte a byte do ultimo confirmado
817852b fix: reverte topologia de altura adaptativa que quebrou em jogo
019da28 refactor: altura adaptativa e contraste, topologia npc_interact
26e761f feat: tema dark sem asset custom + slots vazios ocultos       ← confirmado funcionando
```

`git diff --stat 26e761f -- ADDONS/SonheMenu_RP`:
```
 manifest.json       |  4 +-
 tools/validar_ui.js | 76 +++++++++++++++++++-----------
 ui/sonhe_grid.json  |  4 +-
```
`sonhe_forms.json` e `_ui_defs.json`: **zero diferença**, byte a byte, desde 26e761f.
