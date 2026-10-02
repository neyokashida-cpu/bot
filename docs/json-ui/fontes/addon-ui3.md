# Fonte: addon "JSON UI #3" (grid + scrolling_panel)

Origem: `c:/Users/Desktop/Downloads/ADDONS EXEMPLOS/ui3/`
Metadata do proprio pack: `"url": "https://youtu.be/zWecyvsbKHY?si=pua0J1CzVyQWylAe"` (`ui3/BP/manifest.json`)
Data da leitura: 2026-08-28. Corpus vanilla usado para conferencia: `c:/Users/Desktop/Documents/Nova pasta/assets/assets/resource_packs/vanilla/ui/` (188 arquivos).

**Leia junto com `addon-ui2.md`.** O ui3 e o ui2 sao a **mesma base**: o def `custom_button` e **estruturalmente identico** nos dois (verificado por comparacao de arvore JSON: `a['custom_button'] == b['custom_button']` -> `True`). Este documento cobre so o **delta**, que e onde esta o valor: o ui3 troca o `stack_panel horizontal` por um **`type: "grid"`** e embrulha tudo num **`common.scrolling_panel`**.

---

## 1. Resumo

```
ui3/BP/manifest.json
ui3/BP/pack_icon.png
ui3/BP/scripts/main.js
ui3/RP/manifest.json
ui3/RP/pack_icon.png
ui3/RP/ui/server_form.json      <- 5512 bytes, o unico arquivo de UI
```

Sem `_ui_defs.json`. Sem `textures/`. Sem tema. Mesmo esquema de override por def.

Chaves de topo do arquivo (parse):
```
['namespace', '$schema', 'long_form', 'my_super_custom_panel_main', 'my_super_custom_panel', 'custom_button']
```

Cadeia de controles:
```
server_form.long_form (panel, redefinido)
  ├─ default_long_form@common_dialogs.main_panel_no_buttons  [225 x 200]  -> server_form.long_form_panel   (def do VANILLA)
  └─ cutsom_long_form@common_dialogs.main_panel_no_buttons   [360 x 192.5] -> server_form.my_super_custom_panel_main
                                                                                 └─ scrolling_panel@common.scrolling_panel
                                                                                       └─ server_form.my_super_custom_panel (panel 100% / 100%c)
                                                                                             └─ grid  (grid_dimensions [3,3] + factory + #maximum_grid_items)
                                                                                                   └─ server_form.custom_button [80 x 80]
```

O ponto mais importante do ui3 para o nosso projeto: ele **acumula propriedades de grid que o vanilla nunca combina** (`grid_dimensions` + `#maximum_grid_items` + `factory` + `grid_rescaling_type`, tudo no mesmo controle). E um "kitchen sink". Isso e a antitese da nossa regra de topologia — e serve como **contra-exemplo documentado**, nao como modelo.

---

## 2. Tabela de padroes (delta contra o ui2)

| Aspecto | ui2 | ui3 | Vanilla | Confidence |
|---|---|---|---|---|
| Nome dos ramos | ambos `long_form` (duplicado) | `default_long_form` / `cutsom_long_form` (typo preservado) | — | confirmado |
| Tamanho do dialogo custom | `[360, 150]` | `[360, 192.5]` — **float** | inteiros | confirmado |
| Camada intermediaria | nenhuma | `my_super_custom_panel_main` = `stack_panel` vertical com `common.scrolling_panel` | `long_form_panel` faz exatamente isso | confirmado |
| Scroll | **nao tem** | **tem**, copia literal do `server_form.long_form_panel` vanilla | sim | confirmado |
| Container da colecao | `stack_panel` horizontal `["100%c", 80]` | `grid` `["100%", "100%c"]` | `grid` `["100%", "default"]` (45x) | confirmado |
| Dimensao do grid | — | `"grid_dimensions": [3, 3]` **e** binding `#maximum_grid_items` | **nunca os dois juntos** (0 de 144 grids) | confirmado |
| Fabrica dentro do grid | — | `"factory": { "name": "buttons", "control_name": "server_form.custom_button" }` | **0 de 144 grids tem `factory`** | confirmado |
| Preenchimento | — | `"grid_fill_direction": "horizontal"` + `"grid_rescaling_type": "horizontal"` | `grid_rescaling_type` sim (18x), sempre sem `grid_dimensions` | confirmado |
| Item | `[80, 80]` | `[80, 80]` (identico) | pixel fixo | confirmado |
| Contagem | `#form_button_length` -> `#collection_length` | `#form_button_length` -> `#maximum_grid_items` | `#form_button_contents` -> `#collection_length` | confirmado |
| N de botoes no script | 4 | 9 (= 3x3) | — | confirmado |
| Textura de botao | todas vanilla | uma aponta `"textures/customUi/Circle"` — **arquivo que nao existe no RP** | — | confirmado |

---

## 3. Regras extraidas (com evidencia)

### R1 — O corpo do arquivo continua sendo override por def, sem `_ui_defs.json`
**Confidence: confirmado.** Mesma prova do ui2: o pack define 4 defs e ainda referencia `server_form.long_form_panel`, que so existe no vanilla:

`ui3/RP/ui/server_form.json`
```json
"$child_control": "server_form.long_form_panel",
```
`vanilla/ui/_ui_defs.json:142`
```json
    "ui/server_form.json",
```

### R2 — `size` aceita float
**Confidence: confirmado.**
```json
"cutsom_long_form@common_dialogs.main_panel_no_buttons": {
    "size": [360, 192.5],
```
Nao e erro de digitacao acidental: e o unico valor nao-inteiro do arquivo e o addon esta publicado assim. Util quando se quer altura que caia exatamente em `N * item + padding`.

### R3 — O ramo custom recria o `long_form_panel` vanilla, palavra por palavra
**Confidence: confirmado.** Comparacao lado a lado.

ui3, `my_super_custom_panel_main`:
```json
"my_super_custom_panel_main": {
    "type": "stack_panel",
    "size": ["100%", "100%"],
    "orientation": "vertical",
    "layer": 1,
    "anchor_from": "top_left",
    "anchor_to": "top_left",
    "controls": [
        {
            "scrolling_panel@common.scrolling_panel": {
                "anchor_to": "top_left",
                "anchor_from": "top_left",
                "$show_background": false,
                "size": ["100%", "100%"],
                "$scrolling_content": "server_form.my_super_custom_panel",
                "$scroll_size": [5, "100% - 4px"],
                "$scrolling_pane_size": ["100% - 4px", "100% - 2px"],
                "$scrolling_pane_offset": [2, 0],
                "$scroll_bar_right_padding_size": [0, 0]
            }
        }
    ]
}
```

vanilla, `server_form.long_form_panel` (`vanilla/ui/server_form.json:47-70`):
```json
  "long_form_panel" : {
    "type": "stack_panel",
    "size": ["100%", "100%"],
    "orientation": "vertical",
    "layer": 1,
    "anchor_from": "top_left",
    "anchor_to": "top_left",
    "controls": [
      {
        "scrolling_panel@common.scrolling_panel": {
          "anchor_to": "top_left",
          "anchor_from": "top_left",
          "$show_background": false,
          "size": [ "100%", "100%" ],
          "$scrolling_content": "server_form.long_form_scrolling_content",
          "$scroll_size": [ 5, "100% - 4px" ],
          "$scrolling_pane_size": [ "100% - 4px", "100% - 2px" ],
          "$scrolling_pane_offset": [ 2, 0 ],
          "$scroll_bar_right_padding_size": [ 0, 0 ]
        }
      }
    ]
  },
```

**Unica diferenca: `$scrolling_content`.** Esta e a licao de engenharia mais forte dos dois addons: *nao invente topologia — copie o esqueleto vanilla e troque so o `$slot`*. Um `scrolling_panel` funcional depende de 6 variaveis que o `common.scrolling_panel` expoe (`vanilla/ui/ui_common.json:4627+`, dezenas de `$…|default`); errar uma delas nao gera erro, gera area de scroll de 0px.

### R4 — O par pai/filho do scroll: pai `100%` fixo, filho `100%c`
**Confidence: confirmado.**
```json
"my_super_custom_panel": {
    "type": "panel",
    "size": ["100%", "100%c"],
```
O conteudo do scroll tem **altura dirigida pelos filhos** (`100%c`) e **largura dirigida pelo pai** (`100%`). Exatamente a regra "um eixo cada" das nossas notas. O grid dentro dele repete: `["100%", "100%c"]`, e o item e px fixo `[80,80]`. Cadeia:

```
scroll viewport  ["100% - 4px", "100% - 2px"]   <- px/percentual do pai
  panel          ["100%",       "100%c"]        <- X do pai, Y dos filhos
    grid         ["100%",       "100%c"]        <- X do pai, Y dos filhos
      item       [80, 80]                       <- px puro, fecha o ciclo
```
Nenhum eixo e circular. Se o item fosse `["100%", 80]`, o Y do grid (`100%c`) dependeria do item, e o X do item dependeria do grid — que ja depende do pai — e isso ainda funcionaria; o que quebra e o item ser `%` **no mesmo eixo** em que o pai e `%c`.

### R5 — `grid_dimensions` e `#maximum_grid_items` sao familias mutuamente exclusivas — o ui3 usa AS DUAS
**Confidence: confirmado (a varredura). Anti-padrao.**

O bloco do ui3:
```json
"long_form_dynamic_buttons_panel": {
    "type": "grid",
    "size": ["100%", "100%c"],
    "grid_dimensions": [3, 3],
    "grid_item_template": "server_form.custom_button",
    "grid_fill_direction": "horizontal",
    "grid_rescaling_type": "horizontal",
    "anchor_from": "center",
    "anchor_to": "center",

    "factory": {
        "name": "buttons",
        "control_name": "server_form.custom_button"
    },

    "collection_name": "form_buttons",
    "bindings": [
        {
            "binding_name": "#form_button_length",
            "binding_name_override": "#maximum_grid_items"
        }
    ]
}
```

Varredura programatica dos 188 arquivos vanilla (script em scratchpad, parser que tira comentarios `//` e `/* */` e virgulas soltas):

```
total grid controls: 144
controls with BOTH grid_dimensions AND maximum_grid_items: 0
grid controls using maximum_grid_items: 18
grid controls using grid_dimensions only: 37
grids that also declare 'factory': 0
grid_item_template starting with @: 2   (ambos em horse_screen.json)
grid size values (top): 45x ["100%","default"], 24x ["100%","100%c"], 6x ["100%","100%"]
```

As duas familias canonicas do vanilla:

**(a) grid dinamico** — `grid_rescaling_type` + `maximum_grid_items`, **sem** `grid_dimensions`:
`vanilla/ui/expanded_skin_pack_screen.json:510-523`
```json
  "skins_grid": {
    "type": "grid",
    "size": [ "100% - 8px", "default" ],
    "anchor_from": "top_middle",
    "anchor_to": "top_middle",
    "grid_item_template": "expanded_skin_pack.skins_grid_item",
    "grid_rescaling_type": "horizontal",
    "collection_name": "skin_pack_collection",
    "bindings": [
      {
        "binding_name": "#skins_grid_dimensions",
        "binding_name_override": "#maximum_grid_items"
      }
    ]
  },
```
`vanilla/ui/inventory_screen.json:1972-1994`
```json
  "scroll_grid": {
    "type": "grid",
    "size": [ "100%", "default" ],
    "anchor_to": "top_left",
    "anchor_from": "top_left",
    "$binding_condition|default": "visible",
    "$grid_item_precache_count|default": 0,
    "$grid_item_template|default": "crafting.grid_item_for_recipe_book",
    "collection_name": "$collection_name",
    "grid_rescaling_type": "horizontal",
    "grid_item_template": "$grid_item_template",
    "bindings": [
      {
        "binding_name": "#recipe_book_total_items",
        "binding_name_override": "#maximum_grid_items",
        "binding_condition": "$binding_condition",
        "binding_type": "collection",
        "binding_collection_name": "$collection_name"
      }
    ]
  },
```
`vanilla/ui/anvil_screen_pocket.json:208-218` (versao com constante em vez de binding):
```json
  "inventory_grid": {
    "type": "grid",
    "grid_rescaling_type": "horizontal",
    "anchor_to": "top_left",
    "anchor_from": "top_left",
    "size": [ "100%", "default" ],
    "maximum_grid_items": 36,
    "collection_name": "combined_hotbar_and_inventory_items",
    "grid_item_template": "common.pocket_ui_container_item",
    "$item_collection_name": "combined_hotbar_and_inventory_items"
  },
```

**(b) grid estatico** — `grid_dimensions` fixo, sem binding de contagem. E o que o nosso `sonhe_forms.tiles_grid` usa.

O ui3 mistura as duas. **Provavel** que a engine aplique `grid_dimensions` e ignore o resto — o `main.js` do ui3 tem exatamente 9 botoes, encaixando em `[3,3]`, entao o autor nunca testou o caso em que o binding importaria.

### R6 — `factory` dentro de `type: "grid"` nao existe no vanilla
**Confidence: confirmado (a ausencia).**
`grids that also declare 'factory': 0` em 144 grids. Grid usa **`grid_item_template`**; `factory` vive em `stack_panel` / `collection_panel`. O ui3 declara os dois apontando pro mesmo controle — redundancia inofensiva no melhor caso, ruido no pior.

Contraste, `vanilla/ui/server_form.json:130-145`, que e a forma canonica de `factory`:
```json
    "factory":{
      "name": "buttons",
      "control_ids": {
        "button": "server_form.dynamic_button",
        "label": "@server_form.dynamic_label",
        "header": "@server_form.dynamic_header",
        "divider": "@settings_common.option_group_section_divider"
      }
    },
    "collection_name": "form_buttons",
    "bindings": [
      {
        "binding_name": "#form_button_contents",
        "binding_name_override": "#collection_length"
      }
    ]
```
**`control_ids` com 4 chaves** (`button`, `label`, `header`, `divider`) e o que faz `ActionFormData` suportar `.header()` e `.divider()`. Um `factory` com `control_name` unico (ui2/ui3) renderiza **tudo como botao** — headers e dividers viram botoes clicaveis. Isso e uma perda funcional real dos dois addons.

### R7 — `grid_item_template` normalmente vai SEM `@`
**Confidence: confirmado.** Em 144 grids, so 2 usam `@` (`horse_screen.json`, `"@common.container_item"`). O ui3 usa sem `@`, como a maioria. Nosso `sonhe_forms.tiles_grid` tambem: `"grid_item_template": "sonhe_forms.tile"`.

### R8 — Grids do vanilla usam `["100%", "default"]`, nao `["100%", "100%c"]`
**Confidence: provavel.**
Distribuicao: `["100%","default"]` 45x, `["100%","100%c"]` 24x. O ui3 usou `100%c`; nosso `tiles_grid` usa `["100%", "default"]`. As duas aparecem no vanilla, mas `default` e a maioria e e o que aparece nos grids alimentados por collection (`inventory_screen`, `anvil_screen_pocket`, `expanded_skin_pack`). Nao mexer no nosso.

### R9 — O script referencia uma textura que nao existe no pack
**Confidence: confirmado.**
`ui3/BP/scripts/main.js`
```js
    .button("Skins", "textures/customUi/Circle")
```
Listagem completa do `ui3/RP/`: so `manifest.json`, `pack_icon.png`, `ui/server_form.json`. **Nao ha `textures/`.** Ou seja, esse botao aponta pra um caminho morto.

O que salva a tela e o view binding do proprio `image` (herdado do vanilla):
```json
{
    "binding_type": "view",
    "source_property_name": "(not ((#texture = '') or (#texture = 'loading')))",
    "target_property_name": "#visible"
}
```
Textura inexistente nao derruba a tela — o controle so nao aparece. **Regra: caminho de textura errado degrada, nao quebra.** Isso significa que "meu icone sumiu" **nunca** e a explicacao pra "a tela inteira caiu no vanilla".

### R10 — `custom_button` e byte-a-byte o mesmo dos dois addons
**Confidence: confirmado** (comparacao de arvore JSON: `True`).
Consequencia: as regras R6-R11 do `addon-ui2.md` (icone sem `texture`, ordem dos bindings, `resolve_sibling_scope`, `$button_text: "#null"`, `collection_details` so no botao, layers 200/32) valem **identicas** aqui. Nao repito o bloco; veja `addon-ui2.md` secao 4.

### R11 — Typo em nome de controle nao quebra nada
**Confidence: confirmado.**
```json
"cutsom_long_form@common_dialogs.main_panel_no_buttons": {
```
"cutsom". O nome de um filho dentro de `controls` e arbitrario — so importa para `source_control_name` e para colisao com irmaos. Como ninguem referencia esse nome, o typo e inofensivo. **Mas**: se algum dia um view binding tentar `source_control_name: "custom_long_form"`, ele resolve pra vazio **sem erro**. Nomes de controle sao um vetor classico de falha silenciosa.

---

## 4. JSON literal — `ui3/RP/ui/server_form.json` (partes exclusivas do ui3)

O `custom_button` esta omitido aqui por ser identico ao do `addon-ui2.md`.

```json
{
	"namespace": "server_form",
	"$schema": "https://kalmemarq.github.io/Bugrock-JSON-UI-Schemas/ui.schema.json",

	"long_form": {
		"type": "panel",
		"size": ["100%", "100%"],
		"controls": [
			{
				"default_long_form@common_dialogs.main_panel_no_buttons": {
					"$title_panel": "common_dialogs.standard_title_label",
					"$title_size": ["100% - 14px", 10],
					"size": [225, 200],
					"$text_name": "#title_text",
					"$title_text_binding_type": "none",
					"$child_control": "server_form.long_form_panel",
					"layer": 2,
					"bindings": [
						{ "binding_name": "#title_text" },
						{
							"binding_type": "view",
							"source_property_name": "((#title_text - 'Custom Form') = #title_text)",
							"target_property_name": "#visible"
						}
					]
				}
			},
			{
				"cutsom_long_form@common_dialogs.main_panel_no_buttons": {
					"$title_panel": "common_dialogs.standard_title_label",
					"$title_size": ["100% - 14px", 10],
					"size": [360, 192.5],
					"$text_name": "#title_text",
					"$title_text_binding_type": "none",
					"$child_control": "server_form.my_super_custom_panel_main",
					"layer": 2,
					"bindings": [
						{ "binding_name": "#title_text" },
						{
							"binding_type": "view",
							"source_property_name": "(#title_text = 'Custom Form')",
							"target_property_name": "#visible"
						}
					]
				}
			}
		]
	},

	"my_super_custom_panel_main": {
		"type": "stack_panel",
		"size": ["100%", "100%"],
		"orientation": "vertical",
		"layer": 1,
		"anchor_from": "top_left",
		"anchor_to": "top_left",
		"controls": [
			{
				"scrolling_panel@common.scrolling_panel": {
					"anchor_to": "top_left",
					"anchor_from": "top_left",
					"$show_background": false,
					"size": ["100%", "100%"],
					"$scrolling_content": "server_form.my_super_custom_panel",
					"$scroll_size": [5, "100% - 4px"],
					"$scrolling_pane_size": ["100% - 4px", "100% - 2px"],
					"$scrolling_pane_offset": [2, 0],
					"$scroll_bar_right_padding_size": [0, 0]
				}
			}
		]
	},

	"my_super_custom_panel": {
		"type": "panel",
		"size": ["100%", "100%c"],
		"controls": [
			{
				"long_form_dynamic_buttons_panel": {
					"type": "grid",
					"size": ["100%", "100%c"],
					"grid_dimensions": [3, 3],
					"grid_item_template": "server_form.custom_button",
					"grid_fill_direction": "horizontal",
					"grid_rescaling_type": "horizontal",
					"anchor_from": "center",
					"anchor_to": "center",

					"factory": {
						"name": "buttons",
						"control_name": "server_form.custom_button"
					},

					"collection_name": "form_buttons",
					"bindings": [
						{
							"binding_name": "#form_button_length",
							"binding_name_override": "#maximum_grid_items"
						}
					]
				}
			}
		]
	}
}
```

## 5. Lado do script

`ui3/BP/scripts/main.js`
```js
import { world } from "@minecraft/server"
import { ActionFormData } from "@minecraft/server-ui"

const ui = new ActionFormData()
    .title("Form")
    .body("")
    .button("button1")
    .button("button2")
    .button("button3");

const customUi = new ActionFormData()
    .title("Custom Form")
    .body("")
    .button("Rewards", "textures/ui/promo_holiday_gift_small")
    .button("Shop", "textures/ui/icon_deals")
    .button("Ban Tool", "textures/ui/hammer_l")
    .button("Skins", "textures/customUi/Circle")
    .button("Skins", "textures/ui/icon_hangar")
    .button("Skins", "textures/ui/icon_hangar")
    .button("Skins", "textures/ui/icon_hangar")
    .button("Skins", "textures/ui/icon_hangar")
    .button("Skins", "textures/ui/icon_hangar");

world.afterEvents.itemUse.subscribe((event) => {
    const { source, itemStack } = event
    switch (itemStack.typeId) {
        case "minecraft:compass": ui.show(source); break;
        case "minecraft:clock": customUi.show(source); break;
    }
})
```

**9 botoes = exatamente `grid_dimensions [3,3]`.** O layout foi calibrado pro conteudo, nao o contrario. Nenhum dos dois addons resolve o caso "N variavel".

`ui3/RP/manifest.json`
```json
{
    "format_version": 2,
    "header": {
        "name": "JSON UI Example",
        "description": "JSON UI Example",
        "uuid": "9c0aa4cc-63c9-4ada-92b6-56fbad7f1a2f",
        "version": [0, 0, 1],
        "min_engine_version": [1, 20, 0]
    },
    "modules": [
        {
            "type": "resources",
            "uuid": "c3e5ae30-68cd-40b1-adaa-16ef8e7ce66b",
            "version": [1, 0, 0]
        }
    ]
}
```

Nota: `min_engine_version` `[1,20,0]` nos dois addons; o nosso RP declara `[1,21,50]`. Ambos rodam em 1.26.44 — `min_engine_version` nao muda comportamento de JSON UI, so o gate de instalacao.

---

## 6. ui2 vs ui3 — qual abordagem copiar

| Criterio | ui2 (stack horizontal) | ui3 (grid + scroll) | Melhor |
|---|---|---|---|
| N de botoes variavel | quebra em silencio (transborda) | `grid_dimensions` fixo tambem nao adapta, mas o scroll salva o overflow vertical | **ui3** |
| Quebra de linha | nenhuma | sim, 3 por linha | **ui3** |
| Overflow | conteudo sai da tela | scroll | **ui3** |
| Fidelidade ao vanilla | `stack_panel` + `factory` = padrao vanilla de `server_form` | grid com `factory` + duas familias de dimensao = anti-padrao | **ui2** |
| Simplicidade | 3 defs | 4 defs | **ui2** |
| Risco de falha silenciosa | menor (menos props) | maior (props conflitantes) | **ui2** |

Conclusao: **a topologia do ui3 e a certa (grid + scroll), a limpeza do ui2 e a certa.** O nosso `sonhe_grid.json` ja e a versao limpa da topologia do ui3 — grid com `grid_dimensions`, sem `factory`, sem binding de contagem. Falta so o scroll.

---

## 7. Aplicacao no SonheMenu

Estado atual: `ADDONS/SonheMenu_RP/ui/sonhe_forms.json` (override de `long_form`) + `ui/sonhe_grid.json` (namespace `sonhe_forms`, tema dark, `grid_screen` + fallback `list_screen`).

### 7.1 Onde ja estamos alinhados

- `tiles_grid` usa `grid_dimensions [3,4]` **sem** binding de contagem, **sem** `factory`. Isso e o lado correto da R5/R6. O comentario `//3` do `sonhe_grid.json` ja registra `grid_dimensions junto de #maximum_grid_items` como proibido — a varredura de 144 grids confirma: **0 ocorrencias**.
- `grid_item_template` sem `@` (R7).
- Item pixel fixo `[96,96]` (R4).
- `["100%", "default"]` no grid (R8).
- Icone via `binding_name_override`, mesma ordem de bindings (R10).

### 7.2 O que o ui3 nos ensina que ainda NAO aplicamos

**(A) Falta scroll — e essa e a causa provavel do "menu grande demais".**
Nosso `grid_screen` e `size: [320, 452]` fixo com `tiles_grid` de `grid_dimensions [3,4]` = **12 slots no maximo**. Botao 13 em diante **simplesmente nao renderiza**, sem erro. Isso e falha silenciosa por design, ja anotada como P3/P4 nao resolvido em `sonhe_grid.json` (`"//5"`).

O ui3 resolve embrulhando o conteudo em `common.scrolling_panel` — e ele nao inventou nada: copiou o esqueleto de `server_form.long_form_panel`. Aplicacao de baixo risco no nosso caso: inserir uma camada entre `grid_screen` e `grid_stack`, com o `grid_stack` virando `$scrolling_content`:

```json
"grid_scroll@common.scrolling_panel": {
    "anchor_to": "top_left",
    "anchor_from": "top_left",
    "$show_background": false,
    "size": [ "100%", "100%" ],
    "$scrolling_content": "sonhe_forms.grid_stack",
    "$scroll_size": [ 5, "100% - 4px" ],
    "$scrolling_pane_size": [ "100% - 4px", "100% - 2px" ],
    "$scrolling_pane_offset": [ 2, 0 ],
    "$scroll_bar_right_padding_size": [ 0, 0 ]
}
```

**Cuidado obrigatorio:** `common.scrolling_panel` exige que o `$scrolling_content` tenha **altura dirigida pelos filhos**. Nosso `grid_stack` ja e `size: [288, "100%c"]` — compativel. Mas o `tiles_grid` dentro dele e `["100%", "default"]`, e `default` num grid com `grid_dimensions` fixo produz altura de **4 linhas sempre**, mesmo com 3 botoes. Para o scroll fazer sentido, `grid_dimensions` teria que virar `grid_rescaling_type: "horizontal"` + `#maximum_grid_items` — que e a mudanca de familia que o comentario `//5` diz que nao foi validada.
*Confidence: provavel* — a topologia do scroll e confirmada (copia vanilla); o efeito no nosso grid e inferencia.

**(B) `#form_button_contents` -> `#maximum_grid_items` e plausivel, e o ui3 e evidencia parcial.**
O comentario `//5` do `sonhe_grid.json` diz: *"a pesquisa NAO confirmou que `#form_button_contents` alimenta `#maximum_grid_items`"*. O que temos agora:
- ui3 faz `#form_button_length` -> `#maximum_grid_items` num grid alimentado por `form_buttons` (confirmado no codigo).
- vanilla faz `#recipe_book_total_items` -> `#maximum_grid_items` e `#skins_grid_dimensions` -> `#maximum_grid_items` (confirmado).
- vanilla faz `#form_button_contents` -> `#collection_length` (confirmado).
- `binding_name_override` e generico: qualquer contador vira qualquer alvo.

Logo: **`#form_button_contents` -> `#maximum_grid_items` e provavel de funcionar**, com o cuidado de remover `grid_dimensions` no mesmo movimento (R5). Teste sugerido, um so, isolado:
```json
"tiles_grid": {
    "type": "grid",
    "size": [ "100%", "default" ],
    "grid_rescaling_type": "horizontal",
    "grid_item_template": "sonhe_forms.tile",
    "collection_name": "form_buttons",
    "layer": 1,
    "bindings": [
        {
            "binding_name": "#form_button_contents",
            "binding_name_override": "#maximum_grid_items"
        }
    ]
}
```
Numero de colunas passa a ser `floor(largura_do_grid / largura_do_item)` = `floor(288 / 96)` = **3**, mesmo resultado de hoje, mas com numero de **linhas** dinamico. E o unico caminho documentado para altura adaptativa.
*Confidence: provavel.* Se falhar, o rollback e restaurar `grid_dimensions [3,4]` e apagar o binding — duas linhas.

**(C) O `factory` do ui2/ui3 perde `header` e `divider`.**
Nosso fallback `sonhe_forms.buttons_factory` **ja usa `control_ids` com as 4 chaves**, incluindo `"label": "@server_form.dynamic_label"` e `"divider": "@settings_common.option_group_section_divider"`. Isso e mais correto que os dois addons (R6). **Manter.** Mas note: o caminho `grid` (ativo) nao tem factory nenhuma, entao `.header()` e `.divider()` do ActionFormData viram tiles normais na tela custom. Se o BP usar header/divider, o grid vai desenha-los como botoes clicaveis vazios.

**(D) `size` com float e legitimo (R2).**
Se em algum ajuste de altura o numero exato cair em `.5`, pode usar. Nao e causa de falha silenciosa.

**(E) Textura inexistente NAO derruba a tela (R9).**
Isso elimina uma hipotese: se `textures/ui/sonhe/casa.png` ou os `.json` de nineslice estiverem errados, o sintoma e **icone/moldura invisivel**, nunca "caiu na lista vanilla". Quando a tela inteira cai pro vanilla, o problema esta em `sonhe_forms.json` (o override de `long_form` e seus view bindings) ou numa def sem `type`/`@base` — nunca em textura.

### 7.3 O que NAO copiar do ui3

- `grid_dimensions` **junto** de `#maximum_grid_items` (R5) — 0 de 144 grids vanilla.
- `factory` dentro de `type: "grid"` (R6) — 0 de 144.
- `#form_button_length` (nao existe no corpus vanilla; ver `addon-ui2.md` R5).
- Comparacao de titulo por igualdade exata (`(#title_text = 'Custom Form')`) — cria o buraco descrito em `addon-ui2.md` R3. Nosso par com `not` esta certo.
- Marcador visivel (`"Custom Form"` no titulo). Nosso `§d§r§e§a§m§r` e invisivel em jogo.

### 7.4 Sintese das duas fontes para o problema da falha silenciosa

Nenhum dos dois addons produz `[UI][error]`, e nenhum dos dois tem protecao contra os modos de falha abaixo. As causas plausiveis, ranqueadas pelo que as duas fontes + o corpus vanilla suportam:

1. **Def redefinida sem `type` e sem `@base`** — apaga a versao vanilla (ui2 R2). Sintoma: tela inteira quebra ou fica vazia.
2. **View binding do marcador nao complementar** — as duas telas ficam invisiveis (ui2 R3). Sintoma: dialogo vazio ou aparencia de "caiu no vanilla".
3. **`§` corrompido por encoding** (`Set-Content` ANSI) — o match falha, so o ramo vanilla fica visivel. **Sintoma exato do nosso bug: cai na lista vanilla, zero log.**
4. **Binding name inexistente** (`#form_button_length`) — resolve vazio, colecao com 0 itens (ui2 R5).
5. **Dependencia circular de tamanho** — pai `%c` com filho `%`/`fill` no mesmo eixo, resolve pra 0px (ui2 R6, ui3 R4).
6. **`source_control_name` apontando pra nome que nao existe** — resolve vazio (ui3 R11).
7. **Textura inexistente** — degrada so o controle, **nao** derruba a tela (ui3 R9). *Descartar como causa de queda pro vanilla.*
