# Camadas / Z-order em JSON UI (Bedrock 1.26.44)

Corpus: `assets/resource_packs/vanilla/ui/` (188 arquivos), autoritativo.
Confidence: **confirmado** (visto no código) / **provável** / **suspeita**.

---

## PARTE B — Camadas

### B.1 Faixa de valores de `layer` observada no corpus

Grep de `"layer": <número>` em todo o corpus (todas as telas, milhares de ocorrências) e contagem por valor:

| Faixa | Observação |
|---|---|
| **mínimo: `-10`** | `progress_screen.json:285`, `ui_common.json:3730/5710/5734/5772`, `store_common.json:5433` (`-9`) |
| **valores negativos comuns: `-1` (26x), `-2`, `-3`, `-4`, `-5`, `-8`, `-9`, `-10`** | usados para forçar um controle **atrás** de irmãos no mesmo pai |
| **`0`**: 37x | equivalente a "sem preferência" / fundo de grupo local |
| **`1`–`10`**: a grande maioria (1109 ocorrências de `layer:1` sozinho) | uso típico dentro de um mesmo painel pequeno (fundo=1, conteúdo=2, borda=3...) |
| **dezenas (`15`–`92`)** | usado quando o controle precisa furar por cima de MUITOS irmãos (tooltips, dropdowns, popups locais) |
| **centenas (`100`, `200`, `500`, `600`, `990`)** | "garantir que fique acima de absolutamente tudo nesse container", geralmente com comentário explícito |
| **máximo: `1000`** | `edu_discovery_dialog.json:78` |

Isso já prova, por si só, que **`layer` não é uma escala fixa de "0 a N"** — é um inteiro livre (positivo ou negativo) comparado só entre os controles que competem pelo mesmo espaço.

### B.2 Evidência de que `layer` é comparado entre IRMÃOS (relativo ao pai), não global

Comentário literal do próprio pack, no dropdown de tema/idioma:
```
persona_sdl.json:807
  "layer": 92, // Must be usable on top of skin rotation input panel which has layer of 90
```
O desenvolvedor escolheu `92` **especificamente porque** outro controle irmão (no mesmo escopo) usa `90`. Isso só faz sentido se a comparação for local ao container, não uma tabela global de z-index do jogo inteiro — senão bastaria uma convenção fixa tipo "modais = 9000".

Mais confirmações do mesmo padrão ("escolhi um número grande só pra garantir que fique por cima de tudo *aqui*"):
```
ui_common.json:1136-1137
  // we really want this on top of everything
  "layer": 42,

ui_common.json:6990
  "layer": 200 //This should always be on top, let's ensure that

store_common.json:2442
  "layer": 200, //This should always be on top, let's ensure that

coin_purchase_screen.json:1167
  "layer": 100, // Make this on top

store_search_screen.json:170
  "layer": 4, // Make this on top so the loading bar shows
```

Exemplo de `layer` negativo empurrando algo para trás do próprio conteúdo do pai:
```
anvil_screen.json:297-314
  "cost_label@anvil.generic_label": {
    "layer": 2,
    ...
    "controls": [
      {
        "gray@resource_packs.gray_image": {
          "layer": -1,
          "size": [ "105%", "105%" ],
          "alpha": 0.3
        }
      }
    ]
  },
```
Aqui `gray_image` é FILHO de `cost_label` e usa `layer: -1` para ficar atrás do texto do próprio label — de novo, comparação local (pai/filhos daquele grupo), não um valor absoluto de tela.

**Confidence: confirmado.**

### B.3 Relação entre `layer` e a ordem do array `controls`

Onde dois ou mais controles **não têm `layer` definido** (ou têm o mesmo valor de `layer`), a ordem de desenho segue a ordem em que aparecem no array `"controls": [...]` — quem vem depois é desenhado por cima de quem vem antes. `layer` é o mecanismo para **quebrar** essa ordem implícita sem precisar reordenar o array (útil quando o controle vem de um `@base`/factory e você só quer sobrepor visualmente um item específico).

Exemplo direto do root do HUD (`hud.root_panel`), onde dezenas de elementos são todos filhos diretos do mesmo painel e a maioria não declara `layer` (ficam na ordem do array), enquanto só os que precisam furar por cima da pilha declaram um valor mais alto:
```
hud_screen.json:3160-3348 (hud.root_panel, trecho)
  "layout_customization_reset": { ..., "layer": 50, ... }
  "layout_customization_close_without_saving": { ..., "layer": 50, ... }
  "layout_customization_main_panel@hud.layout_customization_main_panel": {}      // sem layer
  "layout_customization_sub_panel@hud.layout_customization_sub_panel": {}        // sem layer
  "layout_customization_hint_drag_frame": { ..., "layer": 40, ... }
  "layout_customization_hint_deselect_frame": { ..., "layer": 40, ... }
  "layout_customization_hint_saved": { ..., "layer": 40, ... }
  "left_helpers@$left_helpers": {}                                              // sem layer
  "right_helpers@hud.right_helpers": {}                                         // sem layer
  ...
  "chat_stack": { "type": "stack_panel", ... }                                  // sem layer
  ...
```
Os elementos "normais" do HUD (hotbar, chat, helpers) não competem por z-order entre si e não declaram `layer` — a ordem do array já resolve. Só os overlays de customização de layout (`layer:50`) e os hints de drag (`layer:40`) precisam furar por cima de tudo o mais nesse painel.

**Confidence: confirmado.**

### B.4 `hud_screen.json` — estrutura e layers

`hud.root_panel` (linha 3145) é o painel único que contém **todos** os elementos visuais do HUD como filhos diretos ou por `factory`: hotbar, chat, barra de XP, tooltips de item, título/subtítulo, scoreboard, vinheta, etc. Valores de `layer` usados dentro dele:

| Elemento | Layer | Papel |
|---|---|---|
| `vignette_renderer` | `0` | fundo/efeito de tela, mais atrás |
| `hunger_renderer`, `bubbles_renderer`, `mob_effects_renderer`, `camera_renderer` | `1` | renderizadores "base" do HUD |
| `cursor_renderer`, `progress_indicator_renderer` | `4` | cursor e indicador, acima do base |
| `elipses_image` | `30` | acima da maior parte do HUD |
| `hud_title_text` | `31` (`hud_screen.json:2268`) | título/subtítulo, ainda mais acima |
| `layout_customization_hint_*` | `40` | dicas de arrastar durante customização de layout |
| `layout_customization_reset` / `close_without_saving` | `50` | modal de confirmação da customização — topo do HUD inteiro |

Isso mostra uma progressão deliberada: elementos passivos/decorativos ficam em `0–4`, textos que precisam aparecer por cima de ícones ficam em `30–31`, e modais internos do próprio HUD (que precisam tapar TUDO) vão para `40–50`.

**Confidence: confirmado.**

### B.5 `chat_screen.json` — estrutura e layers

`chat_screen.json` é uma **tela separada** (namespace `chat`), não faz parte de `hud_screen.json`. O chat "persistente" (a caixa que aparece sempre, sem abrir nada) é injetado dentro do `hud.root_panel` via `chat_stack` (visto acima, sem `layer` — ordem de array). O `chat_screen.json` cuida da experiência **quando o chat está aberto** (histórico completo, campo de digitação, autocomplete):

```
chat_screen.json:970-974 (controles de topo da tela de chat aberta)
  { "chat_bottom_panel@chat.chat_bottom_panel": { "layer": 2 } },
  { "chat_top_panel@chat.chat_header": { "layer": 2 } },
  { "new_messages_button@chat.new_messages_button": { "layer": 3 } },
  { "autocomplete_commands_panel@chat.commands_panel": { "layer": 4 } },
  { "host_main_panel@host_options.host_panel": { "layer": 5 } },
```
Progressão de `2` a `5`: painéis base do chat primeiro, botão de "novas mensagens" por cima, autocomplete por cima disso, e o painel de host (moderação) no topo de tudo dentro dessa tela.

Outros usos notáveis:
```
chat_screen.json:128   "layer": 200   // botão "new_messages" (estilo), local ao seu próprio pai pequeno
chat_screen.json:789   "layer": 100   // outro elemento que precisa ficar acima de tudo no seu escopo
```
Note que `200` aqui **não conflita** com o `layer:50` do HUD nem com o `layer:1000` de `edu_discovery_dialog.json` — são escopos (pais) diferentes, cada um com sua própria disputa de z-order local.

**Confidence: confirmado.**

### B.6 `layer` é relativo ao pai ou global?

**Relativo ao pai (ao escopo de controles-irmãos mais próximo), confirmado pelas evidências B.2–B.5.** Não existe uma tabela global de z-index no formato JSON UI: cada `panel`/`screen`/controle-com-filhos cria seu próprio grupo de comparação. É por isso que o corpus tem `layer: 1` usado mais de mil vezes (cada uso é local ao seu pai) e também tem `layer: 1000` numa única tela (`edu_discovery_dialog.json`) sem que isso implique "sempre por cima do HUD" — o HUD é uma raiz diferente.

**Consequência prática**: colocar `layer: 1000` num controle **não garante nada em relação a uma tela diferente** (outra screen, ou o HUD). Só garante posição de topo entre os irmãos daquele mesmo painel.

**Confidence: confirmado.**

---

### B.7 Por que uma tela custom pareceria estar "atrás do HUD"?

Com base no mecanismo confirmado acima, os cenários plausíveis, em ordem de probabilidade:

1. **A UI custom foi injetada como filho de `hud.root_panel`** (comum em overlays de RP que mexem no HUD) **sem `layer` competitivo**. Como visto em B.4, o próprio HUD já usa `layer` até `50` para seus elementos internos (customização de layout) e `31` para título/subtítulo. Um controle novo sem `layer` (ou com `layer: 1`) cai **atrás** desses elementos dentro do mesmo `root_panel` — não porque "o HUD está na frente por definição", mas porque, dentro daquele painel específico, ele tem um número de camada menor. **Provável — é a causa mais comum desse sintoma e é diretamente sustentada pelos valores de layer documentados em B.4.**

2. **A UI custom é uma tela separada** (`type: screen` própria, ex. `server_form`) **empilhada por baixo do HUD na pilha de telas** porque foi aberta de um jeito que não a torna a tela "modal" no topo (ex. sem `modal: true` num painel que precisa capturar foco, como no padrão de dropdown: `ui_common.json:1143 "modal": true` junto de `"layer": 42` no mesmo controle). Isso não é bem uma questão de `layer` e sim de como a tela foi empurrada/registrada na pilha de telas do jogo — `layer` não atravessa telas diferentes (B.6). **Provável.**

3. **Tamanho/âncora fazem a UI aparecer "atrás" visualmente** (na real está por cima, mas ocupando pouco espaço, atrás de um elemento HUD que é maior e não está realmente competindo em z-order) — sintoma parecido, causa diferente (layout, não layer). **Suspeita, mas comum de confundir.**

**Não existe, no corpus, nenhum caso de "HUD sempre ganha por definição" — é puramente o valor numérico de `layer` dentro do escopo compartilhado.**

---

### B.8 O que gera um "véu escuro na frente" de uma tela? Cadeia de fundos do `server_form`

Existem **dois mecanismos vanilla distintos** que escurecem a tela, e é importante não confundi-los:

#### (a) `black_tint_image` — véu preto full-screen para popups

```
popup_dialog.json:82-86
  "black_tint_image": {
    "type": "image",
    "texture": "textures/ui/Black",
    "layer": 1
  },

popup_dialog.json:500-506 (uso default, alpha 0.5)
  "controls": [
    {
      "black_tint_image@popup_dialog.black_tint_image": {
        "alpha": 0.5
      }
    }
  ]
```
Reuso com alpha mais forte (o teto vanilla observado, ver `vanilla-alpha.md`):
```
authentication_modals.json:104-121
  "black_tint_image@popup_dialog.black_tint_image": {
    "size": [ "100%c", "100%c" ],
    "alpha": 0.85,
    ...
    "controls": [
      { "content@$dialog_content": { "layer": 1 } }
    ]
  }
```
Esse é o mecanismo clássico de "escurecer tudo atrás de um popup/modal" — uma imagem preta full-screen com alpha entre `0.5` e `0.85` no vanilla.

#### (b) `common_dialogs.full_screen_background` — fundo de tela cheia condicional

```
ui_template_dialogs.json:481-503
  "full_screen_background": {
    "type": "panel",
    "$fill_alpha|default": 0.8,
    "variables": [
      { "requires": "$is_full_screen_layout", "$screen_background_control|default": "common_dialogs.background_image" },
      { "requires": "(not $is_full_screen_layout)", "$screen_background_control|default": "common.empty_panel" }
    ],
    "controls": [
      { "background@$screen_background_control": { "layer": 1, "size": [ "100%", "100%" ], "alpha": "$fill_alpha" } }
    ]
  },
```
Isto só desenha alguma coisa se `$is_full_screen_layout` for `true` — senão o controle de fundo vira `common.empty_panel` (nada). É usado no `common.base_screen` (ver abaixo) como `screen_background`.

#### (c) O fundo "normal" de um diálogo — NÃO é véu de tela cheia

```
ui_template_dialogs.json:339-350 (common_panel)
  "common_panel": {
    "type": "panel",
    "size": [ "100%", "100%c" ],
    "$dialog_background|default": "common.dialog_background_opaque",
    "controls": [
      { "bg_image@$dialog_background": { "layer": 1 } }
    ]
  },

ui_template_dialogs.json:371-416 (dialog_background_hollow_common)
  "dialog_background_hollow_common@common_dialogs.dialog_background_common": {
    "layer": 2,
    "$fill_alpha|default": 0.8,
    "$dialog_background_texture|default": "textures/ui/control",
    ...
    "controls": [
      { "control": { ..., "alpha": "$fill_alpha", ... } }
    ]
  },
```
Esse fundo tem o **tamanho do próprio painel do diálogo** (`"100%", "100%c"` do painel, não da tela), com `alpha` default `0.8`. Escurece só a área do diálogo, não a tela inteira.

#### Cadeia real herdada por `server_form`

```
server_form.json:9
  "third_party_server_screen@common.base_screen": { ... }
```
`common.base_screen` (`ui_common.json:6295`) define:
```
"$screen_bg_content|default": "common.base_screen_empty_panel",   // fundo de trás da tela: VAZIO por padrão
...
"background@$screen_background_control": { ... "alpha": "$fill_alpha" }  // dentro de full_screen_background, só ativo se $is_full_screen_layout
```
E o conteúdo do form (`long_form`/`custom_form`, `server_form.json:36-45,254-263`) usa:
```
"long_form@common_dialogs.main_panel_no_buttons": {
  "$custom_background": "common_dialogs.dialog_background_hollow_3",
  ...
}
```
que cai em `dialog_background_hollow_common` (item **c** acima) — fundo **do tamanho do painel do form**, `alpha` default `0.8`.

**Conclusão da cadeia**: por padrão, `server_form` **não herda nenhum véu preto de tela cheia**. `$screen_bg_content` é vazio, e `full_screen_background` só desenha algo se `$is_full_screen_layout` estiver ligado. O único "escurecimento" que o form tem por padrão é o fundo do próprio painel de diálogo (item c), que cobre só a área do form, com alpha ~0.8.

**Se um "véu escuro na frente" aparece cobrindo mais do que o painel do form**, as causas mais prováveis, em ordem:
1. Um controle customizado (tipo `black_tint_image`/`textures/ui/Black` full-screen) foi adicionado manualmente na árvore do form/tela com `size: ["100%","100%"]` e ficou com `layer` mais alto que o conteúdo — cobrindo tudo à frente. **Provável**, é o padrão vanilla mais comum para esse efeito (item a).
2. `$is_full_screen_layout` foi setado como `true` em algum override, ativando `full_screen_background` (item b) sem intenção.
3. Duas camadas translúcidas do tipo (c) empilhadas (painel dentro de painel, cada um com seu próprio fundo ~0.8) — como documentado em `vanilla-alpha.md` seção A.4, a composição fica mais escura que uma camada isolada, podendo parecer um "véu" mesmo sem ninguém ter adicionado um overlay dedicado.

**Confidence: confirmado** (a cadeia de herança e os defaults, lidos diretamente do código); **provável** (qual das três causas está gerando um véu específico observado em um caso real, sem ver o JSON daquele caso).

---

## Aplicação no SonheMenu

- `ADDONS/SonheMenu_RP/ui/sonhe_grid.json` usa exatamente o padrão vanilla confirmado: `panel_edge` em `layer:0`, `panel_bg` em `layer:1`, `grid_content` em `layer:2` (linhas 16-37) — fundo por baixo, conteúdo por cima, tudo relativo ao mesmo pai (`grid_screen`). Consistente com B.2/B.3.
- O padrão dos 3 estados do botão de tile (`face_default` layer 1, `face_hover` layer 4, `face_pressed` layer 5 — linhas 177, 207, 237) segue o mesmo princípio do `chat_screen.json` (progressão `2→5`) e do próprio comentário do autor ("Layer sobe por estado... pra borda do hover nao ficar sob o tile vizinho") — é exatamente o raciocínio do comentário vanilla em `persona_sdl.json:807` ("Must be usable on top of ... which has layer of 90").
- Se o SonheMenu (form custom via `server_form`) algum dia parecer "atrás do HUD" ou "atrás de outra tela", pelo mecanismo confirmado em B.6/B.7 isso **não é resolvido subindo o `layer` internamente do form** — `layer` não atravessa telas. O que resolve é garantir que a tela do form seja a tela ativa no topo da pilha (mecanismo de abertura da tela, fora do escopo de `layer`).
- Pela cadeia rastreada em B.8, o `server_form` (que o `sonhe_forms` namespace substitui via `custom_form`/`long_form`) **não tem véu preto de tela cheia por padrão** — o único fundo que existe é o do painel do diálogo. Isso é coerente com o `sonhe_grid.json` definir seu próprio `panel_bg`/`panel_edge` do zero (linhas 16-34) em vez de depender de algum overlay herdado — não há overlay global vanilla nesse caminho para entrar em conflito.
- Nenhum valor de `layer` usado em `sonhe_grid.json` (0 a 5) chega perto dos extremos vistos no vanilla (`-10` a `1000`), então não há risco de conflito de faixa — o cuidado real é só garantir que a progressão interna (`0,1,2...5`) continue consistente conforme novos controles forem adicionados, do mesmo jeito que o vanilla comenta explicitamente sempre que sobe um número "para garantir que fique por cima".
