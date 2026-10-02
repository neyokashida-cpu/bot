# Vanilla `common` — controles base (namespace `common`)

Fonte: `c:/Users/Desktop/Documents/Nova pasta/assets/assets/resource_packs/vanilla/ui/ui_common.json`
(7583 linhas). Namespace declarado na linha 2: `"namespace": "common"`.
Cliente alvo: 1.26.44. Corpus lido integralmente por partes (offset/limit).

Convenção de confiança: **confirmado** = trecho JSON literal lido diretamente do arquivo citado.
**provável** = inferido de padrão repetido no corpus mas não citado literalmente aqui.
**suspeita** = dedução sem trecho literal de apoio.

---

## 0. Achado crítico: `common.panel` NÃO EXISTE

confidence: **confirmado**

Busquei `^  "panel([@"])` (chave de topo literal `"panel"`) em `ui_common.json` — zero resultados.
Busquei `@common\.panel` em todo o corpus vanilla `ui/` — zero resultados.

O namespace `common` não define nenhum controle chamado `panel`. O tipo `panel` é um **tipo de
controle nativo do engine** (`"type": "panel"`), não um controle nomeado reutilizável do namespace
`common`. Quem procura "common.panel" provavelmente quer um destes, que são os painéis-base
reais definidos em `ui_common.json`:

| Nome real | Linha | Uso |
|---|---|---|
| `common.empty_panel` | 8 | painel vazio (`type: panel`, sem size) |
| `common.common_panel` | 5853 | painel de diálogo com fundo + close button + divider opcional (o "panel base" de facto usado por telas) |
| `common.root_panel` | 5920 | painel raiz (`type: input_panel`) ao qual todo o resto é parented |
| `common.screen_panel` | 6693 | painel de tela (ver seção 4) |
| `common.base_screen` | 6295 | screen base completa |

Se a tarefa original pressupunha `common.panel` como alias de `common.common_panel`, isso é
**suspeita**, não confirmado — os nomes são distintos e não há alias `panel@common_panel` no arquivo.

---

## 1. `common.common_panel` (o "panel base" de diálogo)

confidence: **confirmado** — `ui_common.json:5853-5917`

```json
"common_panel": {
  "type": "panel",
  "$dialog_background|default": "common.dialog_background_opaque",
  "$show_close_button|default": true,
  "$close_button_visible_binding_name|default": "#close_button_visible",
  "$close_button_offset|default": [ 0, 0 ],
  "$close_button_layer|default": 2,
  "$use_compact_close_button|default": false,
  "$show_divider|default": false,
  "$divider_offset|default": [ "42.5%", "22px" ],
  "$divider_visible_binding_name|default": "",
  "$divider_visible_binding_type|default": "none",
  "$divider_size|default": [ "5px", "100% - 29px" ],
  "controls": [
    { "bg_image@$dialog_background": { "layer": 1 } },
    { "dialog_divider@common.dialog_divider": {
        "visible": "$show_divider",
        "anchor_from": "top_left", "anchor_to": "top_left",
        "offset": "$divider_offset", "size": "$divider_size",
        "bindings": [ { "binding_name": "$divider_visible_binding_name",
          "binding_name_override": "#visible", "binding_type": "$divider_visible_binding_type" } ]
    } },
    { "close_button_holder": {
        "type": "panel", "ignored": "(not $show_close_button)",
        "controls": [
          { "close@common.close_button": { "layer": "$close_button_layer",
              "offset": "$close_button_offset", "ignored": "$use_compact_close_button" } },
          { "compact_close@common.compact_close_button": { "layer": "$close_button_layer",
              "offset": "$close_button_offset", "ignored": "(not $use_compact_close_button)" } }
        ],
        "bindings": [ { "binding_name": "$close_button_visible_binding_name",
            "binding_name_override": "#visible" } ]
    } }
  ]
}
```

### Variáveis expostas (`$var|default`)

| Variável | Default | Efeito |
|---|---|---|
| `$dialog_background` | `common.dialog_background_opaque` | qual imagem de fundo (`common.dialog_background_hollow_1..8`, etc.) |
| `$show_close_button` | `true` | mostra/esconde o botão de fechar |
| `$close_button_visible_binding_name` | `"#close_button_visible"` | binding que controla visibilidade do close |
| `$close_button_offset` | `[0, 0]` | offset do botão de fechar |
| `$close_button_layer` | `2` | layer do botão de fechar |
| `$use_compact_close_button` | `false` | troca `close` por `compact_close` |
| `$show_divider` | `false` | mostra um `dialog_divider` interno |
| `$divider_offset` | `["42.5%", "22px"]` | posição do divisor |
| `$divider_visible_binding_name` | `""` | binding do divisor |
| `$divider_visible_binding_type` | `"none"` | tipo do binding do divisor |
| `$divider_size` | `["5px", "100% - 29px"]` | tamanho do divisor |

### Exemplos literais de uso em outros arquivos vanilla

1. `ui_template_dialogs.json:78` (namespace `common_dialogs`), sobrescrevendo só `$dialog_background`:
```json
"common_panel@common.common_panel": { "$dialog_background": "dialog_background_hollow_6" }
```
Mesmo padrão se repete em `ui_template_dialogs.json:132,177,240,268` com outras texturas
`dialog_background_hollow_1/2/4/5`, e em `ui_template_dialogs.json:214` usando uma variável
repassada: `{ "$dialog_background": "$custom_background" }`.

2. `popup_dialog.json:417-420`, sobrescrevendo `$dialog_background` (via variável) e `$fill_alpha`
   (variável interna da textura de fundo, não do `common_panel` em si, repassada por herança):
```json
"background_with_buttons@common.common_panel": {
  "$dialog_background": "$dialog_background_override",
  "$fill_alpha": 1
}
```

3. `inventory_screen.json:2115-2120`, sobrescrevendo `offset` e desligando o close button:
```json
"common_panel@common.common_panel": {
  "offset": [ 0, 0 ],
  "$show_close_button": false
}
```

Contagem de uso: `@common.common_panel` aparece em ~50 arquivos do corpus (grep), confirmando que
é o painel-base de diálogo mais reutilizado do jogo (inventory, furnace, brewing_stand, chest,
enchanting, trade, loom, stonecutter, smithing_table, anvil, cartography, grindstone, redstone,
horse, popup_dialog, etc).

---

## 2. `common.button`

confidence: **confirmado** — `ui_common.json:44-101`

```json
"button": {
  "type": "button",

  "$focus_id|default": "",
  "$focus_override_down|default": "",
  "$focus_override_up|default": "",
  "$focus_override_left|default": "",
  "$focus_override_right|default": "",
  "focus_identifier": "$focus_id",
  "focus_change_down": "$focus_override_down",
  "focus_change_up": "$focus_override_up",
  "focus_change_left": "$focus_override_left",
  "focus_change_right": "$focus_override_right",
  "$focus_enabled|default": true,
  "focus_enabled": "$focus_enabled",
  "focus_magnet_enabled": true,
  "$focus_wrap_enabled|default": true,
  "focus_wrap_enabled": "$focus_wrap_enabled",

  "$button_focus_precedence|default": 0,
  "default_focus_precedence": "$button_focus_precedence",

  "$button_tts_name|default": "accessibility.button.tts.title",
  "$button_tts_header|default": "",
  "$tts_section_header|default": "",
  "$button_tts_control_type_order_priority|default": 100,
  "$button_tts_index_priority|default": 150,

  "tts_name": "$button_tts_name",
  "tts_control_header": "$button_tts_header",
  "tts_section_header": "$tts_section_header",
  "tts_control_type_order_priority": "$button_tts_control_type_order_priority",
  "tts_index_priority": "$button_tts_index_priority",

  "layer": 1,
  "sound_name": "random.click",
  "sound_volume": 1.0,
  "sound_pitch": 1.0,
  "locked_control": "",
  "default_control": "default",
  "hover_control": "hover",
  "pressed_control": "pressed",
  "button_mappings": [
    { "from_button_id": "button.menu_select", "to_button_id": "$pressed_button_name", "mapping_type": "pressed" },
    { "from_button_id": "button.menu_ok", "to_button_id": "$pressed_button_name", "mapping_type": "focused" }
  ],

  "$button_bindings|default": [],
  "bindings": "$button_bindings"
}
```

### Ponto importante: `common.button` NÃO tem textura própria

`common.button` só define o **esqueleto de comportamento** do controle `type: button`
(foco, som, TTS, mapeamento de botão/gamepad). Os campos `default_control`/`hover_control`/
`pressed_control`/`locked_control` são **nomes literais de sub-controles filhos** (`"default"`,
`"hover"`, `"pressed"`, e locked vazio por default) — é responsabilidade de quem herda de
`common.button` fornecer esses filhos (`controls: [ {"default": {...}}, {"hover": {...}}, ... ]`)
com as texturas reais. Não existem `$default_texture` etc. dentro do próprio `common.button`.

### Variáveis expostas por `common.button`

| Variável | Default |
|---|---|
| `$focus_id` | `""` |
| `$focus_override_down/up/left/right` | `""` cada |
| `$focus_enabled` | `true` |
| `$focus_wrap_enabled` | `true` |
| `$button_focus_precedence` | `0` |
| `$button_tts_name` | `"accessibility.button.tts.title"` |
| `$button_tts_header` | `""` |
| `$tts_section_header` | `""` |
| `$button_tts_control_type_order_priority` | `100` |
| `$button_tts_index_priority` | `150` |
| `$button_bindings` | `[]` |

Campos fixos (não são `$var`, mas costumam ser sobrescritos por quem herda): `layer: 1`,
`sound_name: "random.click"`, `sound_volume/pitch: 1.0`, `locked_control: ""`,
`default_control: "default"`, `hover_control: "hover"`, `pressed_control: "pressed"`.
`$pressed_button_name` é referenciado em `button_mappings` mas **não tem `|default`** dentro de
`common.button` — quem herda precisa fornecê-la, senão fica sem valor.

### Estados (default/hover/pressed/locked)

O tipo `button` nativo troca automaticamente entre os filhos nomeados em `default_control`,
`hover_control`, `pressed_control` (e `locked_control`, se setado) conforme o estado de
interação do mouse/foco. `common.button` mantém `locked_control: ""` — ou seja, por padrão
**não há estado "locked"** a menos que quem herda defina `"locked_control": "locked"` e um
filho `"locked"`.

### Exemplo literal simples — `common.help_button` (dentro do próprio `ui_common.json:3366-3396`)

```json
"help_button@common.button": {
  "size": [ 15, 15 ],
  "layer": 1,

  "$default_texture|default": "textures/ui/how_to_play_button_default_light",
  "$hover_texture|default": "textures/ui/how_to_play_button_hover_light",
  "$pressed_texture|default": "textures/ui/how_to_play_button_pressed_light",

  "$pressed_button_name": "button.help",

  "controls": [
    { "default": { "type": "image", "texture": "$default_texture" } },
    { "hover": { "type": "image", "texture": "$hover_texture" } },
    { "pressed": { "type": "image", "texture": "$pressed_texture" } }
  ]
}
```
Mostra o padrão canônico: herda `common.button`, define `$pressed_button_name` (obrigatória),
e fornece os 3 filhos `default`/`hover`/`pressed` com texturas via variáveis próprias
(não do `common.button`).

### Exemplo literal com estado `locked` — `common_buttons.light_button_assets`
(`ui_template_buttons.json:39-52`, namespace `common_buttons`, outro arquivo do corpus):
```json
"light_button_assets@common.button": {
  "$default_button_texture|default": "textures/ui/button_borderless_light",
  "$default_content_alpha|default": 1,
  "$hover_content_alpha|default": 1,
  "$hover_button_texture|default": "textures/ui/button_borderless_lighthover",
  "$pressed_button_texture|default": "textures/ui/button_borderless_lightpressed",
  "$locked_button_texture|default": "textures/ui/disabledButtonNoBorder",

  "locked_control": "locked",

  "$default_font|default": "default",
  "$font_type": "$default_font",
  "$locked_alpha": 1
}
```
Aqui `locked_control` é sobrescrito de `""` para `"locked"`, habilitando o 4º estado.

### Exemplo literal completo dos 4 filhos de estado — `common_buttons.no_background_content_button`
(`ui_template_buttons.json:962-1058`), que é o `$button_content` usado por `common.back_button`
(`ui_common.json:133-172`, veja `"$button_content": "common.back_button_content"`):
```json
"controls": [
  { "default@$button_state_panel": { "$new_ui_button_texture": "$default_button_texture", ..., "layer": 1 } },
  { "hover@$button_state_panel":   { ..., "$button_image": "common_buttons.background_button_image", "layer": 2 } },
  { "pressed@$button_state_panel": { ..., "$button_offset": "$pressed_button_offset", "layer": 3 } },
  { "locked@$button_state_panel":  { "$new_ui_button_texture": "$locked_button_texture", ..., "layer": 1 } }
]
```
Confirma o mesmo padrão `default`/`hover`/`pressed`/`locked` em escala maior de produção.

### `@common.button` no corpus

`grep -rn '@common\.button'` no diretório `ui/` retorna **80+ ocorrências** em dezenas de arquivos
(`beacon_screen.json`, `book_screen.json`, `chat_screen.json`, `enchanting_screen.json`,
`gamepad_layout_screen.json`, `hud_screen.json`, `pdp_screen.json`, `persona_sdl.json`,
`store_common.json`, `ui_template_buttons.json`, etc.) — confirma que `common.button` é o
controle-base universal de todo botão do jogo (sempre estendido, nunca usado sozinho sem os
filhos de estado).

---

## 3. Outros controles/painéis base reutilizáveis relevantes

confidence: **confirmado** para todos os trechos abaixo (linhas de `ui_common.json`).

### 3.1 `common.empty_panel` / `common.empty_image` (linhas 8-24)
```json
"empty_panel": { "type": "panel" },
"empty_image": { "type": "image" }
```
Placeholders vazios usados como default de slots (`"$button_content|default": "common.empty_panel"`).

### 3.2 `common.horizontal_stack_panel` / `common.vertical_stack_panel` (linhas 26-34)
```json
"horizontal_stack_panel": { "type": "stack_panel", "orientation": "horizontal" },
"vertical_stack_panel": { "type": "stack_panel", "orientation": "vertical" }
```

### 3.3 `common.screen_header_title_panel` (linhas 103-131) — label de título de tela
Variáveis: `$screen_header_title_visible|default: true`, `$screen_header_title|default: "#screen_header_title"`,
`$screen_header_title_binding_type|default: "none"`. Usa `color: "$title_text_color"` (variável global de tema).

### 3.4 `common.back_button` (linhas 133-172) — botão "voltar" padrão
Herda `common_buttons.no_background_content_button`. Variáveis principais:
`$button_text|default: "$back_button_text"`, `$button_content: "common.back_button_content"`,
`$button_tts_header|default: "accessibility.button.back"`,
`$back_button_pressed_button_name|default: "button.menu_exit"`.

### 3.5 `common.chevron_image` (linhas 231-236) — ícone de seta usado em back buttons
```json
"chevron_image": { "type": "image", "layer": 1, "size": [ 4, 7 ], "texture": "$chevron_image_name" }
```

### 3.6 `common.label_hover` (linhas 281-294) — hover overlay reutilizável para labels não-botão
```json
"label_hover": {
  "type": "panel", "size": [ "100%", "100%" ], "$visible_hover|default": true,
  "controls": [ { "hover@common.focus_border_white": { "size": [ "100%", "100%" ], "offset": [ 0, 2 ], "visible": "$visible_hover" } } ]
}
```

### 3.7 `common.checkbox_image` e variantes (linhas 587-701) — ícones de checkbox/radio
`checked_image`, `unchecked_image`, `checked_hover_image`, `unchecked_hover_image`, mais os
`toggle_state_template`-derivados (`checkbox_checked_state`, `checkbox_unchecked_locked_state`,
`radio_toggle_checked_state`, etc.), cada um com `texture` fixa (ex.: `textures/ui/checkbox_check`).

### 3.8 `common.button_text` (linhas 634-639) — label padrão de texto de botão
```json
"button_text": { "type": "label", "color": "$generic_button_text_color", "layer": 1, "shadow": false }
```

### 3.9 `common.new_button_label` (linhas 652-659)
```json
"new_button_label": {
  "$text_color|default": "$light_button_default_text_color",
  "type": "label", "layer": 3, "color": "$text_color", "shadow": false, "font_size": "normal"
}
```

### 3.10 `common.dialog_background_common` e família `dialog_background_hollow_1..8` (linhas 2988-3064)
Painéis de fundo (`type: image`) usados por `$dialog_background` do `common_panel`. Variáveis:
`$fill_alpha|default: 0.8`, `$dialog_background_texture|default: "textures/ui/control"`.

### 3.11 `common.dialog_divider` (linhas 3066-3070)
```json
"dialog_divider": { "type": "image", "texture": "textures/ui/dialog_divider", "layer": 1 }
```

### 3.12 `common.section_heading_label` (linhas 3084-3090) — label de seção
```json
"section_heading_label": { "type": "label", "layer": 1, "anchor_from": "top_left", "anchor_to": "top_left", "color": "$title_text_color" }
```

### 3.13 `common.section_divider` (linhas 3105-3143) — divider vertical em stack_panel
Variáveis: `$top_padding_size|default: ["100%",2]`, `$bottom_padding_size|default: ["100%",2]`,
`$divider_size|default: ["100% - 10px",1]`. Textura interna: `textures/ui/divider2`, `alpha: 0.2`.

### 3.14 `common.close_button` (linhas 3180+) — botão de fechar concreto (não usa `common.button` puro,
implementa `type: button` diretamente com os mesmos nomes `default_control/hover_control/pressed_control`).
Variáveis: `$close_button_offset|default: [-2,2]`, `$close_button_panel_size|default: [15,15]`,
`$close_button_to_button_id|default: "button.menu_exit"`, `$close_button_default_texture|default: "textures/ui/close_button_default"`.

### 3.15 `common.horizontal_divider` / `common.vertical_divider` (linhas 2311-2344)
```json
"horizontal_divider": {
  "type": "panel", "size": [ "100%", "100%c" ], "$image_size|default": [ "100%", 1 ],
  "controls": [ { "divider_image": { "type": "image", "size": "$image_size", "texture": "textures/ui/divider3", "tiled": "x", "alpha": 0.6 } } ]
}
```
Variante vertical análoga com `tiled: "y"` e `$size|default: ["100%c","100%"]`.

### 3.16 `common.underline` (linhas 2346-2357)
```json
"underline": {
  "type": "image", "size": [ "100%", 1 ],
  "$texture|default": "textures/ui/underline",
  "$underline_color|default": "$f_color_format",
  "color": "$underline_color", "texture": "$texture",
  "alpha": 0.6, "tiled": "x", "anchor_from": "bottom_left", "anchor_to": "bottom_left"
}
```

### 3.17 `common.single_line_label` (linhas 2359+) — wrapper de label de uma linha
Variáveis: `$size|default: ["100%c","100%c + 3px"]`, `$single_line_label_offset|default: [2,1]`,
`$single_label_size|default: ["default",10]`, `$underline_control|default: "common.empty_panel"`,
`$font_type|default: "smooth"`, `$font_size|default: "normal"`.

### 3.18 Ícones prontos (linhas 7436-7472) — todos `type: image`
```json
"info_icon": { "type": "image", "texture": "textures/ui/infobulb" },
"error_glyph": { "type": "image", "texture": "textures/ui/ErrorGlyph" },
"creative_icon": { "type": "image", "size": [19,13], "texture": "textures/ui/creative_icon" },
"inventory_icon": { "type": "image", "size": [19,13], "texture": "textures/ui/inventory_icon" },
"recipe_book_icon": { "type": "image", "size": [19,13], "texture": "textures/ui/recipe_book_icon" },
"tab_icon_image": { "layer": -1, "type": "image", "size": [17,17] },
"search_icon@common.tab_icon_image": { "texture": "textures/ui/magnifyingGlass" }
```

### 3.19 `common.root_panel` (linhas 5920-6014) — painel raiz para telas de inventário/HUD
`type: input_panel`, `size: [176,166]`, com `button_mappings` extensos de gamepad/teclado
(scroll, arrow keys, container reset). Base de `center_fold@common.root_panel` e
`player_inventory@common.root_panel` (ver `inventory_screen.json:2110`).

---

## 4. Nota lateral: namespace `common_buttons` (arquivo separado)

confidence: **confirmado**

Assim como `common` vive em `ui_common.json` (não `common.json`), o namespace `common_buttons`
vive em `ui_template_buttons.json:7` (`"namespace": "common_buttons"`) — não em `common_buttons.json`.
É esse namespace que fornece as implementações concretas de botão com textura
(`light_button_assets@common.button`, `dark_button_assets@common.button`,
`no_background_content_button@common.button`) citadas acima como exemplos de `common.button`.
Mencionado aqui porque `common.back_button` (seção 3.4) depende diretamente dele.

---

## 5. Resumo de variáveis expostas (tabela consolidada)

| Controle | Variável | Default |
|---|---|---|
| `common.common_panel` | `$dialog_background` | `common.dialog_background_opaque` |
| `common.common_panel` | `$show_close_button` | `true` |
| `common.common_panel` | `$close_button_visible_binding_name` | `"#close_button_visible"` |
| `common.common_panel` | `$close_button_offset` | `[0,0]` |
| `common.common_panel` | `$close_button_layer` | `2` |
| `common.common_panel` | `$use_compact_close_button` | `false` |
| `common.common_panel` | `$show_divider` | `false` |
| `common.common_panel` | `$divider_offset` | `["42.5%","22px"]` |
| `common.common_panel` | `$divider_visible_binding_name` | `""` |
| `common.common_panel` | `$divider_visible_binding_type` | `"none"` |
| `common.common_panel` | `$divider_size` | `["5px","100% - 29px"]` |
| `common.button` | `$focus_id` | `""` |
| `common.button` | `$focus_override_down/up/left/right` | `""` |
| `common.button` | `$focus_enabled` | `true` |
| `common.button` | `$focus_wrap_enabled` | `true` |
| `common.button` | `$button_focus_precedence` | `0` |
| `common.button` | `$button_tts_name` | `"accessibility.button.tts.title"` |
| `common.button` | `$button_tts_header` | `""` |
| `common.button` | `$tts_section_header` | `""` |
| `common.button` | `$button_tts_control_type_order_priority` | `100` |
| `common.button` | `$button_tts_index_priority` | `150` |
| `common.button` | `$button_bindings` | `[]` |
| `common.screen_header_title_panel` | `$screen_header_title_visible` | `true` |
| `common.screen_header_title_panel` | `$screen_header_title` | `"#screen_header_title"` |
| `common.screen_header_title_panel` | `$screen_header_title_binding_type` | `"none"` |
| `common.close_button` | `$close_button_offset` | `[-2,2]` |
| `common.close_button` | `$close_button_panel_size` | `[15,15]` |
| `common.close_button` | `$close_button_to_button_id` | `"button.menu_exit"` |
| `common.close_button` | `$close_button_default_texture` | `"textures/ui/close_button_default"` |
| `common.section_divider` | `$top_padding_size` | `["100%",2]` |
| `common.section_divider` | `$bottom_padding_size` | `["100%",2]` |
| `common.section_divider` | `$divider_size` | `["100% - 10px",1]` |
| `common.horizontal_divider` | `$image_size` | `["100%",1]` |
| `common.underline` | `$texture` | `"textures/ui/underline"` |
| `common.underline` | `$underline_color` | `"$f_color_format"` |
| `common.single_line_label` | `$size` | `["100%c","100%c + 3px"]` |
| `common.single_line_label` | `$font_type` | `"smooth"` |
| `common.single_line_label` | `$font_size` | `"normal"` |

---

## 6. IMPORTANTE — não editei nada em ADDONS

Nenhum arquivo em `ADDONS/SonheMenu_RP` ou `ADDONS/SonheMenu_BP` foi lido nem modificado nesta
investigação. Este documento cobre exclusivamente o corpus vanilla autoritativo.
