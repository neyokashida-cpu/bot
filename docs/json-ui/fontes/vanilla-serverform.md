# Referência vanilla autoritativa — `server_form` + `common_dialogs`

> Documento de referência do override de `server_form` do SonheMenu.
> Alvo: cliente Bedrock **1.26.44**.
> Todo trecho citado abaixo foi **lido literalmente** dos arquivos indicados. Onde não houve leitura direta, o item está marcado como `provável` ou `suspeita`.

## 0. Fontes lidas e onde cada namespace realmente mora

| Namespace | Arquivo | confidence |
|---|---|---|
| `server_form` | `c:/Users/Desktop/Documents/Nova pasta/assets/assets/resource_packs/vanilla/ui/server_form.json` (531 linhas, lido inteiro) | confirmado |
| `common_dialogs` | `.../vanilla/ui/ui_template_dialogs.json` (509 linhas, lido inteiro) | confirmado |
| `common` | `.../vanilla/ui/ui_common.json` (7583 linhas, lido nos trechos relevantes) | confirmado |
| `common_buttons` | `.../vanilla/ui/ui_template_buttons.json` (2186 linhas) | confirmado |
| `settings_common` | `.../vanilla/ui/settings_sections/settings_common.json` (2354 linhas) | confirmado |
| `progress` | `.../vanilla/ui/progress_screen.json` | confirmado |
| globais `$…_color` | `.../vanilla/ui/_global_variables.json` (459 linhas) | confirmado |

**⚠ CORREÇÃO DE PREMISSA:** **não existe** `vanilla/ui/common_dialogs.json`. O namespace `common_dialogs` é declarado dentro de `ui_template_dialogs.json`:

```json
{
  "namespace": "common_dialogs",

  "standard_title_label": {
```
(`ui_template_dialogs.json:6-9`) — confidence: **confirmado** (busca `grep -l '"namespace": *"common_dialogs"' *.json` retornou apenas `ui_template_dialogs.json`).

Registro no `_ui_defs.json` vanilla:
```
ui/server_form.json
```
(`_ui_defs.json:142`) — confidence: **confirmado**.

---

## 1. Árvore de controles completa do namespace `server_form`

Toda a árvore, com o herdeiro (`@base`) de cada nó. `→` = filho declarado em `controls`; `⇒` = filho injetado por `$variável` de template; `⚙` = produzido por `factory`.

```
server_form.third_party_server_screen           @common.base_screen          [SCREEN RAIZ]
└─ $screen_content = "server_form.main_screen_content"
   └─ server_form.main_screen_content            type: panel, size [0,0]
      └─ server_form_factory                     type: factory
         ├─ control_ids.long_form   = "@server_form.long_form"
         └─ control_ids.custom_form = "@server_form.custom_form"

── RAMO A: ActionFormData / MessageFormData ──────────────────────────────
server_form.long_form                            @common_dialogs.main_panel_no_buttons
├─ $title_panel   = common_dialogs.standard_title_label   (NÃO usado, ver §5.4)
├─ $text_name     = "#title_text"
├─ $child_control = "server_form.long_form_panel"
├─ size [225,200], layer 2
└─ (herdado de main_panel_no_buttons)
   ├─ common_panel                @common.common_panel   ($dialog_background = $custom_background
   │  │                                                    default "dialog_background_hollow_3")
   │  ├─ bg_image@$dialog_background      → common_dialogs.dialog_background_hollow_3
   │  │                                     @dialog_background_hollow_common
   │  │                                     texture "textures/ui/dialog_background_hollow_3"
   │  ├─ dialog_divider@common.dialog_divider    (visible: $show_divider, default false)
   │  └─ close_button_holder                     (ignored: (not $show_close_button), default TRUE)
   │     ├─ close@common.close_button            → button.menu_exit
   │     └─ compact_close@common.compact_close_button
   ├─ title_label                 @common_dialogs.title_label      ← AQUI o #title_text
   │  ├─ common_dialogs_0@standard_title_label   (ignored: $use_custom_title_control)
   │  └─ common_dialogs_1@$custom_title_label    (ignored: (not $use_custom_title_control))
   └─ panel_indent                type: panel
      size "$panel_indent_size" default ["100% - 16px","100% - 31px"], offset [0,23]
      └─ inside_header_panel@$child_control  ⇒  server_form.long_form_panel

server_form.long_form_panel                      type: stack_panel, vertical, 100%x100%
└─ scrolling_panel                               @common.scrolling_panel
   ├─ $scrolling_content       = "server_form.long_form_scrolling_content"
   ├─ $scroll_size             = [5, "100% - 4px"]
   ├─ $scrolling_pane_size     = ["100% - 4px","100% - 2px"]
   ├─ $scrolling_pane_offset   = [2,0]
   ├─ $scroll_bar_right_padding_size = [0,0]
   ├─ $show_background         = false
   ├─ scroll_touch@common.scrolling_panel_base   (ignored: (not $touch))
   └─ scroll_mouse@common.scrolling_panel_base   (ignored: $touch)
      └─ $scroll_view_name@common.scroll_view_control   type: scroll_view
         scroll_content = "scrolling_content"

server_form.long_form_scrolling_content          type: stack_panel, vertical
                                                 size ["100% - 4px","100%c"]
├─ label_offset_panel            type: panel, size ["100%","100%c"]
│  └─ main_label                 type: label, text "#form_text",
│                                color "$main_header_text_color" = [1,1,1], offset [2,2]
├─ padding                       type: panel, size ["100%", 4]
└─ wrapping_panel                type: panel, size ["100%","100%c"]
   └─ long_form_dynamic_buttons_panel@server_form.long_form_dynamic_buttons_panel

server_form.long_form_dynamic_buttons_panel      type: stack_panel, vertical
                                                 size ["100% - 4px","100%c"], offset [2,0]
├─ collection_name = "form_buttons"
├─ bindings: #form_button_contents → #collection_length
└─ factory { name: "buttons", control_ids: { … } }               ⚙
   ├─ "button"  : "server_form.dynamic_button"      ← SEM @ (ver §6.2)
   ├─ "label"   : "@server_form.dynamic_label"
   ├─ "header"  : "@server_form.dynamic_header"
   └─ "divider" : "@settings_common.option_group_section_divider"

server_form.dynamic_button                       type: stack_panel, horizontal, ["100%", 32]
├─ panel_name                    type: panel, size [34,"100%c"]
│  │  binding view: source_control_name "image" + resolve_sibling_scope
│  │                (not (#texture = '')) → #visible
│  ├─ image                      type: image, [32,32], layer 2  (SEM propriedade "texture")
│  │     #form_button_texture             → #texture              (collection form_buttons)
│  │     #form_button_texture_file_system → #texture_file_system   (collection form_buttons)
│  │     view: (not ((#texture = '') or (#texture = 'loading'))) → #visible
│  └─ progress@progress.progress_loading_bars   [30,4] offset [-2,16]
│        view (sibling "image"): (#texture = 'loading') → #visible
└─ form_button                   @common_buttons.light_text_button
   ├─ $pressed_button_name = "button.form_button_click"
   ├─ $button_text = "#form_button_text", binding_type "collection",
   │  $button_text_grid_collection_name = "form_buttons"
   ├─ size ["fill", 32], $button_text_max_size ["100%", 20]
   ├─ binding: { binding_type: "collection_details", binding_collection_name: "form_buttons" }
   └─ (herdado) light_button_assets@common.button → 4 estados
      default / hover / pressed / locked  @common_buttons.new_ui_button_panel
      └─ button_content → $button_type_panel = common_buttons.new_ui_binding_button_label (label)

server_form.dynamic_label   @settings_common.option_group_spaced_label
   └─ text@settings_common.option_group_label → text (label, color $main_header_text_color)
server_form.dynamic_header  @settings_common.option_group_spaced_header  ($font_size "large")
   └─ text@settings_common.option_group_label → text

── RAMO B: ModalFormData ─────────────────────────────────────────────────
server_form.custom_form                          @common_dialogs.main_panel_no_buttons
└─ $child_control = "server_form.custom_form_panel"   (mesmo shape do long_form)

server_form.custom_form_panel                    @common.scrolling_panel
└─ $scrolling_content = "server_form.custom_form_scrolling_content"

server_form.custom_form_scrolling_content        type: stack_panel, vertical
├─ generated_form@server_form.generated_contents
└─ submit_button@common_buttons.light_text_button
   $pressed_button_name "button.submit_custom_form", $button_text "#submit_text",
   $button_text_binding_type "global", $button_binding_condition "once",
   binding #submit_button_visible → #visible

server_form.generated_contents                   type: stack_panel, vertical
├─ collection_name = "custom_form"
├─ bindings: #custom_form_length → #collection_length
└─ factory { name: "buttons", control_ids: { … } }               ⚙
   ├─ "label"       : "@server_form.custom_label"
   ├─ "toggle"      : "@server_form.custom_toggle"
   ├─ "slider"      : "@server_form.custom_slider"
   ├─ "step_slider" : "@server_form.custom_step_slider"
   ├─ "dropdown"    : "@server_form.custom_dropdown"
   ├─ "input"       : "@server_form.custom_input"
   ├─ "header"      : "@server_form.custom_header"
   └─ "divider"     : "@settings_common.option_group_section_divider"

server_form.custom_label        @settings_common.option_group_label
server_form.custom_header       @settings_common.option_group_header
server_form.custom_toggle       @settings_common.option_toggle
server_form.custom_slider       @settings_common.option_slider
server_form.custom_step_slider  @server_form.custom_slider        ← herda do PRÓPRIO namespace
server_form.custom_dropdown     type: panel, ["100%","100%c"], layer 2
   └─ dropdown@settings_common.option_dropdown
        $dropdown_content = "server_form.custom_dropdown_content"
server_form.custom_dropdown_content  @settings_common.option_radio_dropdown_group
   └─ $radio_factory { name:"buttons", control_name:"server_form.custom_dropdown_radio" }
      $radio_collection_name = "custom_dropdown"
server_form.custom_dropdown_radio    @settings_common.radio_with_label
server_form.custom_input             @settings_common.option_text_edit
```

**Inventário fechado:** o namespace `server_form` define **exatamente 22 controles nomeados**, nesta ordem no arquivo — confidence: **confirmado** (arquivo lido inteiro):

`third_party_server_screen`, `main_screen_content`, `long_form`, `long_form_panel`, `long_form_scrolling_content`, `long_form_dynamic_buttons_panel`, `dynamic_button`, `dynamic_label`, `dynamic_header`, `custom_form`, `custom_form_panel`, `generated_contents`, `custom_form_scrolling_content`, `custom_label`, `custom_header`, `custom_toggle`, `custom_slider`, `custom_step_slider`, `custom_dropdown`, `custom_dropdown_content`, `custom_dropdown_radio`, `custom_input`.

---

## 2. Blocos JSON literais — `server_form.json`

### 2.1 Raiz da tela

```json
"third_party_server_screen@common.base_screen": {
  "$screen_content": "server_form.main_screen_content",
  "button_mappings": [
    {
      "from_button_id": "button.menu_cancel",
      "to_button_id": "button.menu_exit",
      "mapping_type": "global"
    }
  ]
},

"main_screen_content": {
  "type": "panel",
  "size": [0, 0],
  "controls": [
      {
        "server_form_factory": {
            "type": "factory",
            "control_ids": {
            "long_form": "@server_form.long_form",
            "custom_form": "@server_form.custom_form"
        }
      }
    }
  ]
},
```
confidence: **confirmado** (`server_form.json:9-33`).

Observação estrutural crítica: `main_screen_content` tem **`"size": [0, 0]`**. Ele não é um contêiner de layout — quem define o tamanho real é `long_form` / `custom_form`, que são `anchor_from/anchor_to: "center"` herdados de `main_panel_no_buttons`. Portanto **um override de `long_form` não recebe tamanho do pai; precisa declarar o seu próprio**. confidence: **confirmado**.

### 2.2 `long_form` (o alvo do nosso override)

```json
"long_form@common_dialogs.main_panel_no_buttons": {
  "$title_panel": "common_dialogs.standard_title_label",
  "$title_size": [ "100% - 15px", 10 ],
  "$title_max_size": [ "100% - 15px", 10 ],
  "size": [225, 200],
  "$text_name": "#title_text",
  "$title_text_binding_type": "none",
  "$child_control": "server_form.long_form_panel",
  "layer": 2
},
```
confidence: **confirmado** (`server_form.json:35-44`).

`custom_form` é **idêntico**, trocando apenas `$child_control`:

```json
"custom_form@common_dialogs.main_panel_no_buttons": {
  "$title_panel": "common_dialogs.standard_title_label",
  "$title_size": [ "100% - 15px", 10 ],
  "$title_max_size": [ "100% - 15px", 10 ],
  "size": [225, 200],
  "$text_name": "#title_text",
  "$title_text_binding_type": "none",
  "$child_control": "server_form.custom_form_panel",
  "layer": 2
},
```
confidence: **confirmado** (`server_form.json:245-254`).

### 2.3 `long_form_panel` e `long_form_scrolling_content`

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

"long_form_scrolling_content": {
  "type": "stack_panel",
  "size": [ "100% - 4px", "100%c" ],
  "orientation": "vertical",
  "anchor_from": "top_left",
  "anchor_to": "top_left",

  "controls": [
    {
      "label_offset_panel": {
        "type": "panel",
        "size": ["100%", "100%c"],
        "controls": [
          {
            "main_label": {
              "type": "label",
              "offset": [2,2],
              "color": "$main_header_text_color",
              "size": ["100%", "default"],
              "anchor_from": "top_left",
              "anchor_to": "top_left",
              "text": "#form_text"
            }
          }
        ]
      }
    },
    {
      "padding": {
        "type": "panel",
        "size": [ "100%", 4 ]
      }
    },
    {
      "wrapping_panel": {
        "type": "panel",
        "size": [ "100%", "100%c" ],
        "controls": [
          {
            "long_form_dynamic_buttons_panel@server_form.long_form_dynamic_buttons_panel": {}
          }
        ]
      }
    }
  ]
},
```
confidence: **confirmado** (`server_form.json:46-116`).

### 2.4 A coleção `form_buttons` — o caminho inteiro

```json
"long_form_dynamic_buttons_panel": {
  "type": "stack_panel",
  "size": ["100% - 4px", "100%c"],
  "offset": [2,0],
  "orientation": "vertical",
  "anchor_from": "top_middle",
  "anchor_to": "top_middle",

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
},
```
confidence: **confirmado** (`server_form.json:118-142`).

**O caminho completo, do script até o pixel:**

1. `ActionFormData.button(text, iconPath)` alimenta o engine.
2. O engine publica no escopo da tela: `#form_button_contents` (quantidade) e a coleção nomeada **`form_buttons`**.
3. `long_form_dynamic_buttons_panel` declara `"collection_name": "form_buttons"` e mapeia `#form_button_contents → #collection_length`. Esse é o **único** ponto onde a contagem entra.
4. O `factory` de nome `"buttons"` instancia, por item, um dos 4 `control_ids` conforme o tipo do item (button / label / header / divider).
5. Cada instância recebe um índice implícito. Quem lê esse índice é o binding `collection_details`.
6. Dentro da instância, cada binding com `"binding_type": "collection"` + `"binding_collection_name": "form_buttons"` resolve o campo daquele índice.

confidence dos passos 1-4 e 6: **confirmado** (tudo literal). Passo 5 (semântica de `collection_details`): **provável**.

### 2.5 Template do botão (`dynamic_button`) — literal completo

```json
"dynamic_button": {
  "type": "stack_panel",
  "size": ["100%", 32],
  "orientation": "horizontal",
  "controls":[
    {
      "panel_name": {
        "type": "panel",
        "size": [34, "100%c"],
        "bindings": [
          {
            "binding_type": "view",
            "source_control_name": "image",
            "resolve_sibling_scope": true,
            "source_property_name": "(not (#texture = ''))",
            "target_property_name": "#visible"
          }
        ],

        "controls": [
          {
            "image": {
              "type": "image",
              "layer": 2,
              "size": [32, 32],
              "offset": [0, 0],
              "bindings":[
                {
                  "binding_name": "#form_button_texture",
                  "binding_name_override": "#texture",
                  "binding_type": "collection",
                  "binding_collection_name": "form_buttons"
                },
                {
                  "binding_name": "#form_button_texture_file_system",
                  "binding_name_override": "#texture_file_system",
                  "binding_type": "collection",
                  "binding_collection_name": "form_buttons"
                },
                {
                  "binding_type": "view",
                  "source_property_name": "(not ((#texture = '') or (#texture = 'loading')))",
                  "target_property_name": "#visible"
                }
              ]
            }
          },
          {
            "progress@progress.progress_loading_bars": {
              "size": [30, 4],
              "offset": [-2, 16],
              "bindings":[
                {
                  "binding_type": "view",
                  "source_control_name": "image",
                  "resolve_sibling_scope": true,
                  "source_property_name": "(#texture = 'loading')",
                  "target_property_name": "#visible"
                }
              ]
            }
          }
        ]
      }
    },
    {
      "form_button@common_buttons.light_text_button": {
        "$pressed_button_name": "button.form_button_click",
        "anchor_from": "top_left",
        "anchor_to": "top_left",
        "size": [ "fill", 32 ],
        "$button_text": "#form_button_text",
        "$button_text_binding_type": "collection",
        "$button_text_grid_collection_name": "form_buttons",
        "$button_text_max_size": [ "100%", 20 ],
        "bindings": [
          {
            "binding_type": "collection_details",
            "binding_collection_name": "form_buttons"
          }
        ]
      }
    }
  ]
},
```
confidence: **confirmado** (`server_form.json:144-218`).

**Fatos extraídos, com evidência:**

1. O `image` do ícone **não tem propriedade `"texture"`**. A textura chega 100% por `binding_name_override: "#texture"`. confidence: **confirmado** (a ausência é literal).
2. O ícone lê **dois** bindings: `#form_button_texture` → `#texture` **e** `#form_button_texture_file_system` → `#texture_file_system`. O segundo diz ao engine em que sistema de arquivos procurar (pack local vs. cache de servidor). confidence do código: **confirmado**; da semântica: **provável**.
3. O engine publica o sentinel de string **`'loading'`** em `#texture` enquanto a imagem é baixada — daí `(#texture = 'loading')` acender a barra de progresso. confidence: **confirmado** (a comparação existe literalmente).
4. O botão carrega `{"binding_type": "collection_details", "binding_collection_name": "form_buttons"}` **sem** `binding_name`. É o binding que informa **qual índice** da coleção aquele controle é. confidence da presença: **confirmado**; da semântica: **provável**.
5. O botão de clique é `button.form_button_click` — nome fixo, é assim que o script recebe `selection`. confidence: **confirmado**.
6. O texto do botão passa por **`$button_text`**, não por uma propriedade `"text"` direta — porque `light_text_button` delega o label a `new_ui_binding_button_label`, que faz `"text": "$button_text"` e monta o binding a partir de `$button_text_binding_type` + `$button_text_grid_collection_name`. confidence: **confirmado** (§4.9).

### 2.6 `dynamic_label` / `dynamic_header`

```json
"dynamic_label@settings_common.option_group_spaced_label": {
  "$text": "#form_button_text",
  "$text_bindings": [
    {
      "binding_name": "#form_button_text",
      "binding_type": "collection",
      "binding_collection_name": "form_buttons"
    }
  ]
},

"dynamic_header@settings_common.option_group_spaced_header": {
  "$text": "#form_button_text",
  "$text_bindings": [
    {
      "binding_name": "#form_button_text",
      "binding_type": "collection",
      "binding_collection_name": "form_buttons"
    }
  ]
},
```
confidence: **confirmado** (`server_form.json:220-242`).

`label` e `header` usam **a mesma** binding `#form_button_text` que o `button`. A coleção `form_buttons` é polimórfica: o mesmo campo serve aos 4 tipos de item. confidence: **confirmado**.

### 2.7 `custom_form_scrolling_content` e `generated_contents`

```json
"generated_contents": {
  "type": "stack_panel",
  "size": ["100%", "100%c"],
  "orientation": "vertical",
  "anchor_from": "top_left",
  "anchor_to": "top_left",

  "factory":{
    "name": "buttons",
    "control_ids": {
      "label": "@server_form.custom_label",
      "toggle": "@server_form.custom_toggle",
      "slider": "@server_form.custom_slider",
      "step_slider": "@server_form.custom_step_slider",
      "dropdown": "@server_form.custom_dropdown",
      "input": "@server_form.custom_input",
      "header": "@server_form.custom_header",
      "divider": "@settings_common.option_group_section_divider"
    }
  },

  "collection_name": "custom_form",
  "bindings": [
    {
      "binding_name": "#custom_form_length",
      "binding_name_override": "#collection_length"
    }
  ]
},
```
confidence: **confirmado** (`server_form.json:277-303`).

Note: o `factory` do ModalForm também se chama **`"buttons"`**, mesmo não tendo `control_ids.button`. O nome do factory é fixo do engine, não descritivo. confidence: **confirmado**.

```json
"submit_button@common_buttons.light_text_button": {
  "$pressed_button_name": "button.submit_custom_form",
  "anchor_from": "top_left",
  "anchor_to": "top_left",
  "size": [ "100%", 32 ],
  "$button_text": "#submit_text",
  "$button_text_binding_type": "global",
  "$button_binding_condition": "once",

  "bindings": [
    {
      "binding_name": "#submit_button_visible",
      "binding_name_override": "#visible"
    }
  ]
}
```
confidence: **confirmado** (`server_form.json:319-334`).

---

## 3. Blocos JSON literais — `common_dialogs` (`ui_template_dialogs.json`)

### 3.1 `standard_title_label` — onde `#title_text` é renderizado

```json
"standard_title_label": {
  "type": "label",
  "size": [ "default", 10 ],
  "$title_max_size|default": [ "default", 10 ],
  "max_size": "$title_max_size",
  "color": "$title_text_color",
  "text": "$text_name",
  "layer": 4,
  "shadow": false,
  "property_bag": {
    "#tts_dialog_title": "$text_name"
  },
  "bindings": [
    {
      "binding_type": "$title_text_binding_type",
      "binding_condition": "$title_binding_condition",
      "binding_name": "$text_name",
      "binding_name_override": "$text_name"
    },
    {
      "binding_type": "global",
      "binding_condition": "once",
      "binding_name": "#tts_dialog_title"
    }
  ]
},
```
confidence: **confirmado** (`ui_template_dialogs.json:9-33`).

### 3.2 `title_label` — o wrapper que decide entre padrão e custom

```json
"title_label": {
  "type": "panel",
  "anchor_from": "top_middle",
  "anchor_to": "top_middle",
  "$title_size|default": [ "100%c", 10 ],
  "size": "$title_size",
  "$title_offset|default": [ 0, 9 ],
  "offset": "$title_offset",
  "$use_custom_title_control|default": false,
  "$custom_title_label|default": "common.empty_panel",
  "$title_binding_condition|default": "none",
  "$title_text_binding_type|default": "none",
  "controls": [
    {
      "common_dialogs_0@standard_title_label": {
        "ignored": "$use_custom_title_control"
      }
    },
    {
      "common_dialogs_1@$custom_title_label": {
        "ignored": "(not $use_custom_title_control)"
      }
    }
  ]
},
```
confidence: **confirmado** (`ui_template_dialogs.json:35-58`).

### 3.3 `main_panel_no_buttons` — o pai literal de `long_form` e `custom_form`

```json
"main_panel_no_buttons": {
  "type": "panel",
  "anchor_from": "center",
  "anchor_to": "center",
  "$text_name|default": "",
  "$panel_indent_size|default": [ "100% - 16px", "100% - 31px" ],
  "$custom_background|default": "dialog_background_hollow_3",
  "controls": [
    {
      "common_panel@common.common_panel": { "$dialog_background": "$custom_background" }
    },
    {
      "title_label@common_dialogs.title_label": {}
    },
    {
      "panel_indent": {
        "type": "panel",
        "size": "$panel_indent_size",
        "offset": [ 0, 23 ],
        "anchor_from": "top_middle",
        "anchor_to": "top_middle",
        "controls": [
          { "inside_header_panel@$child_control": {} }
        ]
      }
    }
  ]
},
```
confidence: **confirmado** (`ui_template_dialogs.json:205-231`).

### 3.4 Inventário completo do que `common_dialogs` expõe

Lista fechada dos controles definidos em `ui_template_dialogs.json` — confidence: **confirmado** (arquivo lido inteiro):

| Controle | Tipo | Fundo / âncora de conteúdo |
|---|---|---|
| `standard_title_label` | label | — |
| `title_label` | panel | wrapper do título |
| `main_panel_three_buttons` | panel | `dialog_background_hollow_6`, indent `["100% - 16px","100% - 131px"]` |
| `main_panel_two_buttons` | panel | `dialog_background_hollow_1`, indent `["100% - 16px","100% - 99px"]` |
| `main_panel_one_button` | panel | `dialog_background_hollow_2`, indent `["100% - 16px","100% - 65px"]` |
| **`main_panel_no_buttons`** | panel | `dialog_background_hollow_3`, indent `["100% - 16px","100% - 31px"]` |
| `main_panel_no_title_no_buttons` | panel | `dialog_background_hollow_4`, indent `["100% - 16px","100% - 16px"]`, offset `[0,8]` |
| `main_panel_small_title_one_button` | panel | `dialog_background_hollow_5`, `$title_offset [0,5]`, indent offset `[0,17]` |
| `main_panel` | panel | `modal.modal_background_image`, indent `["100% - 14px","100% - 14px"]` |
| `form_fitting_main_panel_no_buttons` | panel | `size ["100%","100%c"]`, `$custom_background "common_dialogs.dialog_background_hollow_3"` |
| `common_panel` | panel | `$dialog_background\|default "common.dialog_background_opaque"` |
| `dialog_background_common` | image | `textures/ui/dialog_background_hollow_4` |
| `dialog_background_thin` | image | `textures/ui/thin_dialog` |
| `flat_solid_background` | image | `textures/ui/White`, `color "$0_color_format"` |
| `dialog_background_hollow_common` | image | base dos hollow_N; injeta `$child_control`, close button e title |
| `common_close_button_holder` | stack_panel | `visible "$show_close_button"` |
| `dialog_background_opaque` | image | `textures/ui/dialog_background_opaque` |
| `dialog_background_opaque_with_child` | image | `["100%","100%c + 31px"]`, `$fill_alpha 0.0` |
| `dialog_background_hollow_1` | image | `["100%","100%c"]` |
| `dialog_background_hollow_2` | image | `["100%","100%c"]` |
| `dialog_background_hollow_3` | image | `["100%","100%c + 31px"]` ← **o usado por `long_form`** |
| `dialog_background_hollow_4` | image | `["100%","100%c"]` |
| `dialog_background_hollow_6` | image | **nome com typo:** `"dialog_background_hollow_6@common_dialogs.dialog_background_hollow_common:"` (dois-pontos sobrando) |
| `full_screen_background` | panel | `$fill_alpha\|default 0.8` |
| `background_image` | image | `textures/ui/control` |

O `hollow_common` que dá cara aos fundos:

```json
"dialog_background_hollow_common@common_dialogs.dialog_background_common": {
  "layer": 2,
  "$fill_alpha|default": 0.8,
  "$dialog_background_texture|default": "textures/ui/control",
  "controls": [
    {
      "control": {
        "type": "image",
        "texture": "$dialog_background_texture",
        "layer": 1,
        "$common_background_size|default": [ "100% - 16px", "100%c - 27px" ],
        "$close_button_offset|default": [ 6, -21 ],
        "size": "$common_background_size",
        "offset": [ 0, 7 ],
        "alpha": "$fill_alpha",
        "variables": [
          {
            "requires": "($show_close_button and $use_compact_close_button)",
            "$common_background_size": [ "100% - 16px", "100%c - 19px" ],
            "$close_button_offset": [ 6, -13 ]
          },
          {
            "requires": "(not $show_close_button)",
            "$common_background_size": [ "100% - 16px", "100%c - 6px" ]
          }
        ],
        "controls": [
          {
            "inside_header_panel@$child_control": {
            }
          },
          {
            "close_button_holder@common_dialogs.common_close_button_holder": {}
          },
          {
            "title_label@common_dialogs.title_label": {
              "anchor_from": "top_middle",
              "anchor_to": "top_middle",
              "offset": [ 0, -15 ]
            }
          }
        ]
      }
    }
  ]
},
```
confidence: **confirmado** (`ui_template_dialogs.json:361-404`).

**⚠ ARMADILHA — dois `common_panel` diferentes:**
`common_dialogs.dialog_background_hollow_common` injeta um `inside_header_panel@$child_control` **próprio**, mais close button e **um segundo** `title_label`. Mas `main_panel_no_buttons` usa **`common.common_panel`** (de `ui_common.json`), **não** `common_dialogs.common_panel`. E `common.common_panel` monta só `bg_image@$dialog_background` + divider + close button — **não** injeta `$child_control`.

Logo, no caminho `long_form`, o `$child_control` entra **uma única vez**, pelo `panel_indent`. confidence: **confirmado** (os dois `common_panel` foram lidos lado a lado).

Existem, portanto, **dois** controles chamados `common_panel` no vanilla:
- `common.common_panel` — `ui_common.json:5853`
- `common_dialogs.common_panel` — `ui_template_dialogs.json:333`

Confundir os dois num override troca completamente a topologia de onde o conteúdo é injetado. confidence: **confirmado**.

---

## 4. Tabela de `$variáveis` por controle

### 4.1 `$vars` que `server_form.long_form` / `custom_form` **setam**

| `$var` | Valor setado | Consumida por | confidence |
|---|---|---|---|
| `$title_panel` | `"common_dialogs.standard_title_label"` | **ninguém** — `main_panel_no_buttons` não lê `$title_panel` (ver §5.4) | confirmado |
| `$title_size` | `[ "100% - 15px", 10 ]` | `common_dialogs.title_label` → `"size": "$title_size"` | confirmado |
| `$title_max_size` | `[ "100% - 15px", 10 ]` | `standard_title_label` → `"max_size": "$title_max_size"` | confirmado |
| `$text_name` | `"#title_text"` | `standard_title_label` → `"text": "$text_name"` + binding | confirmado |
| `$title_text_binding_type` | `"none"` | `standard_title_label` → `"binding_type": "$title_text_binding_type"` | confirmado |
| `$child_control` | `"server_form.long_form_panel"` | `main_panel_no_buttons` → `inside_header_panel@$child_control` | confirmado |

### 4.2 `$vars` aceitas por `common_dialogs.main_panel_no_buttons`

| `$var` | Default literal | Efeito |
|---|---|---|
| `$text_name` | `""` | texto do título |
| `$panel_indent_size` | `[ "100% - 16px", "100% - 31px" ]` | área útil do conteúdo |
| `$custom_background` | `"dialog_background_hollow_3"` | textura de moldura |
| `$child_control` | **sem default** — obrigatório | conteúdo |

confidence: **confirmado** (`ui_template_dialogs.json:205-212`).

> `$child_control` **não tem `|default`**. Um override de `long_form` que herde `main_panel_no_buttons` e esqueça `$child_control` referencia uma variável não resolvida. Suspeita forte de ser um dos modos de falha silenciosa. confidence da consequência: **suspeita**.

Repassadas ao `common.common_panel` filho (herdadas, não redeclaradas): `$show_close_button`, `$show_divider`, `$close_button_offset`, `$use_compact_close_button` — ver §4.5.
Repassadas ao `common_dialogs.title_label` filho: `$title_size`, `$title_offset`, `$use_custom_title_control`, `$custom_title_label`, `$title_binding_condition`, `$title_text_binding_type`, `$title_max_size`, `$text_name` — ver §4.3 e §4.4.

### 4.3 `$vars` de `common_dialogs.title_label`

| `$var` | Default | Efeito |
|---|---|---|
| `$title_size` | `[ "100%c", 10 ]` | tamanho do painel de título |
| `$title_offset` | `[ 0, 9 ]` | posição a partir de `top_middle` |
| `$use_custom_title_control` | `false` | troca `standard_title_label` por `$custom_title_label` |
| `$custom_title_label` | `"common.empty_panel"` | controle alternativo de título |
| `$title_binding_condition` | `"none"` | `binding_condition` do título |
| `$title_text_binding_type` | `"none"` | `binding_type` do título |

confidence: **confirmado** (`ui_template_dialogs.json:39-50`).

### 4.4 `$vars` de `common_dialogs.standard_title_label`

| `$var` | Default | Uso |
|---|---|---|
| `$title_max_size` | `[ "default", 10 ]` | `max_size` |
| `$title_text_color` | global `[ 0.3, 0.3, 0.3 ]` | `color` — **sem default local**, vem de `_global_variables.json:37` |
| `$text_name` | vem do pai | `text` **e** `binding_name` **e** `binding_name_override` |
| `$title_text_binding_type` | vem do pai | `binding_type` |
| `$title_binding_condition` | vem do pai | `binding_condition` |

confidence: **confirmado**.

### 4.5 `$vars` de `common.common_panel` (`ui_common.json:5853-5915`)

| `$var` | Default |
|---|---|
| `$dialog_background` | `"common.dialog_background_opaque"` |
| `$show_close_button` | `true` |
| `$close_button_visible_binding_name` | `"#close_button_visible"` |
| `$close_button_offset` | `[ 0, 0 ]` |
| `$close_button_layer` | `2` |
| `$use_compact_close_button` | `false` |
| `$show_divider` | `false` |
| `$divider_offset` | `[ "42.5%", "22px" ]` |
| `$divider_visible_binding_name` | `""` |
| `$divider_visible_binding_type` | `"none"` |
| `$divider_size` | `[ "5px", "100% - 29px" ]` |

confidence: **confirmado**.

### 4.6 `$vars` de `common.scrolling_panel` que `long_form_panel` sobrescreve

`common.scrolling_panel` declara **34 `$vars` com default** (`ui_common.json:4627-4675`). As relevantes:

| `$var` | Default vanilla | Setado por `long_form_panel` |
|---|---|---|
| `$scrolling_content` | **sem default** — obrigatório | `"server_form.long_form_scrolling_content"` |
| `$scrolling_pane_size` | `[ "100%", "100%" ]` | `[ "100% - 4px", "100% - 2px" ]` |
| `$scrolling_pane_size_touch` | `[ "100%", "100%" ]` | — |
| `$scrolling_pane_offset` | `[ 0, 0 ]` | `[ 2, 0 ]` |
| `$scroll_view_control_size` | `[ "100%", "100%" ]` | — |
| `$background_size` | `[ "100%", "100%" ]` | — |
| `$background_offset` | `[ 0, 0 ]` | — |
| `$scroll_view_port_size` | `[ "100%", "100%" ]` | — |
| `$scroll_view_port_max_size` | `[ "100%", "100%" ]` | — |
| `$scroll_view_port_offset` | `[ 0, 0 ]` | — |
| `$scroll_bar_left_padding_size` | `[ 2, 0 ]` | — |
| `$scroll_bar_right_padding_size` | `[ 2, 0 ]` | `[ 0, 0 ]` |
| `$view_port_size` | `[ "fill", "100%" ]` | — |
| `$scroll_bar_contained` | `false` | — |
| `$scroll_size` | `[ 4, "100%" ]` | `[ 5, "100% - 4px" ]` |
| `$scroll_box_size` | `[ "100%", "100%" ]` | — |
| `$scroll_box_visible` | `true` | — |
| `$scroll_box_visible_touch` | `false` | — |
| `$use_touch_mode` | `false` | — |
| `$show_background` | `true` | `false` |
| `$wider_scroll_area` | `false` | — |
| `$allow_scrolling_even_when_content_fits` | `true` | — |
| `$scroll_track_image_control` | `"common.scroll_indent_image"` | — |
| `$scroll_background_image_control` | `"common.scroll_indent_image"` | — |
| (touch) `$background_size_touch`, `$background_offset_touch`, `$scroll_view_port_size_touch`, `$scroll_view_port_max_size_touch`, `$scroll_view_port_offset_touch`, `$scroll_bar_left_padding_size_touch` `[0,0]`, `$scroll_bar_right_padding_size_touch` `[0,0]`, `$view_port_size_touch`, `$scroll_bar_contained_touch` `true`, `$scroll_size_touch` `[4,"100%"]` | ver arquivo | — |

confidence: **confirmado**.

> **Comentário literal do vanilla que vale como doc:**
> `// The content you want inside the scrolling viewport must be specified by defining $scrolling_content.` (`ui_common.json:4692-4693`)

E o `scroll_view` de verdade (`common.scroll_view_control`, `ui_common.json:4391+`) declara `"scroll_content": "scrolling_content"` — o **nome literal** do controle filho que ele rola. confidence: **confirmado**.

### 4.7 `$vars` de `common_buttons.light_text_button` (`ui_template_buttons.json:319-403`)

```json
"light_text_button@light_button_assets": {
  "$button_offset|default": [ 0, 0 ],
  "$button_pressed_offset|default": [ 0, 1 ],
  "$button_text|default": "",
  "$button_font_size|default": "normal",
  "$button_font_scale_factor|default": 1.0,
  "$pressed_alpha|default": 1,
  "$default_button_alpha|default": 1,
  "$default_hover_alpha|default": 1,
  "$default_pressed_alpha|default": 1,
  "$default_button_pressed_offset|default": [ 0, 1 ],

  "$default_text_color|default": "$light_button_default_text_color",
  "$hover_text_color|default": "$light_button_hover_text_color",
  "$pressed_text_color|default": "$light_button_pressed_text_color",
  "$locked_text_color|default": "$light_button_locked_text_color",

  // For text bindings
  "$button_text_binding_type|default": "none",
  "$button_binding_condition|default": "none",
  "$button_text_grid_collection_name|default": "",

  "$button_type_panel": "common_buttons.new_ui_binding_button_label",
  "$button_state_panel|default": "common_buttons.new_ui_button_panel",

  "$default_state|default": false,
  "$hover_state|default": false,
  "$pressed_state|default": false,
  "$locked_state|default": false,

  "controls": [
    { "default@$button_state_panel": { … "$default_state": true, "layer": 1 } },
    { "hover@$button_state_panel":   { … "$hover_state": true,   "layer": 4 } },
    { "pressed@$button_state_panel": { … "$pressed_state": true, "layer": 5 } },
    { "locked@$button_state_panel":  { … "$locked_state": true,  "layer": 1 } }
  ]
},
```
confidence: **confirmado**.

Comentário literal do vanilla sobre os layers: `// This is several layers higher than default in case two buttons share a border and that shared border needs to turn with with either button hover/press state`.

Texturas herdadas de `light_button_assets` (`ui_template_buttons.json:38-51`):

| `$var` | Default |
|---|---|
| `$default_button_texture` | `"textures/ui/button_borderless_light"` |
| `$hover_button_texture` | `"textures/ui/button_borderless_lighthover"` |
| `$pressed_button_texture` | `"textures/ui/button_borderless_lightpressed"` |
| `$locked_button_texture` | `"textures/ui/disabledButtonNoBorder"` |
| `$default_content_alpha` | `1` |
| `$hover_content_alpha` | `1` |
| `$default_font` | `"default"` |
| (fixo) | `"locked_control": "locked"`, `"$locked_alpha": 1` |

### 4.8 `$vars` de `common.button` (`ui_common.json:44-101`) — base de **todo** botão

| `$var` | Default |
|---|---|
| `$focus_id` | `""` |
| `$focus_override_down` / `_up` / `_left` / `_right` | `""` |
| `$focus_enabled` | `true` |
| `$focus_wrap_enabled` | `true` |
| `$button_focus_precedence` | `0` |
| `$button_tts_name` | `"accessibility.button.tts.title"` |
| `$button_tts_header` | `""` |
| `$tts_section_header` | `""` |
| `$button_tts_control_type_order_priority` | `100` |
| `$button_tts_index_priority` | `150` |
| `$button_bindings` | `[]` |
| `$pressed_button_name` | **sem default** — obrigatório |

Propriedades fixas relevantes:
```json
"locked_control": "",
"default_control": "default",
"hover_control": "hover",
"pressed_control": "pressed",
"sound_name": "random.click",
"button_mappings": [
  { "from_button_id": "button.menu_select", "to_button_id": "$pressed_button_name", "mapping_type": "pressed" },
  { "from_button_id": "button.menu_ok", "to_button_id": "$pressed_button_name", "mapping_type": "focused" }
]
```
confidence: **confirmado**.

### 4.9 `$vars` de `common_buttons.new_ui_binding_button_label` (o label do botão)

```json
"new_ui_binding_button_label": {
  "type": "label",
  "layer": 2,
  "text": "$button_text",
  "color": "$text_color",
  "$font_type|default": "default",
  "font_type": "$font_type",
  "font_size": "$button_font_size",
  "$button_font_scale_factor|default": 1.0,
  "font_scale_factor": "$button_font_scale_factor",
  "$button_font_size|default": "normal",
  "$new_ui_label_offset|default": "$button_offset",
  "offset": "$new_ui_label_offset",
  "$anchor|default": "center",
  "anchor_from": "$anchor",
  "anchor_to": "$anchor",
  "shadow": false,
  "$button_text_size|default": [ "default", "default" ],
  "size": "$button_text_size",
  "$button_text_max_size|default": [ "100%", 10 ], // Per design buttons are single line text only
  "max_size": "$button_text_max_size",
  "$text_alignment|default": "center",
  "text_alignment": "$text_alignment",
  "$tts_section_header|default": "",
  "tts_section_header": "$tts_section_header",
  "$button_text_collection_details|default": "none",
  "$button_text_collection_prefix|default": "",
  "bindings": [
    {
      "binding_type": "$button_text_collection_details",
      "binding_collection_name": "$button_text_grid_collection_name",
      "binding_collection_prefix": "$button_text_collection_prefix"
    },
    {
      "binding_type": "$button_text_binding_type",
      "binding_condition": "$button_binding_condition",
      "binding_collection_name": "$button_text_grid_collection_name",
      "binding_name": "$button_text",
      "binding_name_override": "$button_text"
    }
  ]
},
```
confidence: **confirmado** (`ui_template_buttons.json:482-523`).

**Isto explica o `dynamic_button`:** o vanilla passa `$button_text_binding_type: "collection"` + `$button_text_grid_collection_name: "form_buttons"`, e o label monta sozinho `binding_name: "#form_button_text"` com `binding_name_override` **igual**. É o mesmo padrão do SonheMenu no `tile_label`, mas escrito à mão em vez de via `$var`. confidence: **confirmado**.

### 4.10 `$vars` de `settings_common` (`settings_sections/settings_common.json:103-182`)

```json
"option_group_label": {
  "type": "panel",
  "size": [ "100%", "100%c + 9px" ],
  "$text|default": "unset $text",
  "$text_bindings|default": [],
  "$font_type|default": "default",
  "$font_scale_factor|default": 1,
  "$font_size|default": "normal",
  "controls": [
    {
      "text": {
        "type": "label",
        "color": "$main_header_text_color",
        "text": "$text",
        "anchor_from": "top_left",
        "anchor_to": "top_left",
        "max_size": [ "100%", "default" ],
        "offset": [ 0, 4 ],
        "locked_alpha": 0.5,
        "bindings": "$text_bindings",
        "font_type": "$font_type",
        "font_size": "$font_size",
        "font_scale_factor": "$font_scale_factor"
      }
    }
  ]
},

"option_group_header": {
  "type": "panel",
  "size": [ "100%", "100%c - 4px" ],
  "$font_size": "large",
  "controls": [
    { "text@settings_common.option_group_label": {} }
  ]
},

// Adds a little space (configurable) before the control.
"option_group_spaced_label": {
  "type": "panel",
  "$text|default": "unset $text",
  "$option_group_spaced_header_size|default": [ "100%", "100%c + 2px" ],
  "$option_group_spaced_header_size_offset|default": [ 0, 2 ],
  "size": "$option_group_spaced_header_size",
  "offset": "$option_group_spaced_header_size_offset",
  "controls": [
    { "text@settings_common.option_group_label": {} }
  ]
},

// Adds a little space (configurable) before the control.
"option_group_spaced_header": {
  "type": "panel",
  "$text|default": "unset $text",
  "$font_size": "large",
  "$option_group_spaced_header_size|default": [ "100%", "100%c" ],
  "$option_group_spaced_header_size_offset|default": [ 0, 4 ],
  "size": "$option_group_spaced_header_size",
  "offset": "$option_group_spaced_header_size_offset",
  "controls": [
    { "text@settings_common.option_group_label": {} }
  ]
},

"option_group_section_divider": {
  "type": "panel",
  "$size|default": [ "100%", "9px" ],
  "size": "$size",
  "controls": [
    {
      "background": {
        "type": "image",
        "size": [ "100%", 1 ],
        "anchor_from": "center",
        "anchor_to": "center",
        "layer": 3,
        "texture": "textures/ui/list_item_divider_line_light"
      }
    }
  ]
},
```
confidence: **confirmado**.

> Um `$text` não fornecido rende literalmente a string **`"unset $text"`** na tela. É o único caso do vanilla onde falta de variável vira sintoma **visível** em vez de silencioso. Útil para diagnóstico.

### 4.11 `$vars` que `custom_form` passa aos controles de `settings_common`

Todos literais em `server_form.json:352-531`. Resumo por controle (todos com `binding_type: "collection"` sobre a coleção `custom_form`, salvo indicado):

| Controle | `$var` chave | Valor |
|---|---|---|
| `custom_label` | `$text` | `"#custom_text"` |
| `custom_header` | `$text` | `"#custom_text"` |
| `custom_toggle` | `$toggle_name` | `"custom_toggle"` |
| | `$toggle_state_binding_name` / `$option_binding_name` | `"#custom_toggle_state"` |
| | `$toggle_enabled_binding_name` | `"#custom_toggle_enabled"` |
| | `$toggle_grid_collection_name` | `"custom_form"` |
| | `$option_tooltip_text_binding_name` | `"#custom_tooltip_text"` |
| | `$option_tooltip_area` | `"inside_header_panel"` |
| `custom_slider` | `$slider_name` | `"custom_slider"` |
| | `$slider_value_binding_name` | `"#custom_slider_value"` |
| | `$slider_tts_text_value` | `"#custom_slider_text_value"` |
| | `$slider_enabled_binding_name` | `"#custom_slider_enabled"` |
| | `$slider_timeout_binding_name` | `"#custom_slider_timeout"` |
| | `$option_label` | `"#custom_slider_text"` |
| | `$slider_collection_name` | `"custom_form"` |
| `custom_step_slider` | `$slider_name` | `"custom_slider_step"` |
| | `$slider_value_binding_name` | `"#custom_slider_step_value"` |
| | `$slider_steps_binding_name` | `"#custom_slider_steps"` |
| | `$option_label` | `"#custom_slider_step_text"` |
| `custom_dropdown` | `$dropdown_name` | `"custom_dropdown"` |
| | `$dropdown_content` | `"server_form.custom_dropdown_content"` |
| | `$options_dropdown_toggle_label_binding` | `"#dropdown_option_text"` |
| | `$dropdown_scroll_content_size` | `[ "100%", "200%" ]` |
| | `$dropdown_area` | `"inside_header_panel"` |
| `custom_dropdown_content` | `$radio_collection_name` | `"custom_dropdown"` |
| | `$radio_factory.control_name` | `"server_form.custom_dropdown_radio"` |
| | `$toggle_focus_id_binding_name` | `"#custom_toggle_focus_id"` |
| | `$radio_buttons` | `[]` |
| | binding | `#custom_dropdown_length` → `#collection_length` (collection `custom_form`) |
| `custom_dropdown_radio` | `$toggle_name` | `"custom_dropdown_radio_toggle"` |
| | `$toggle_state_binding_name` | `"#custom_radio_toggled"` |
| | `$toggle_grid_collection_name` | `"custom_dropdown"` |
| | `$radio_label_text` | `"#custom_radio_text"` |
| `custom_input` | `$text_box_name` | `"custom_input"` |
| | `$text_edit_box_content_binding_name` / `$option_binding_name` | `"#custom_input_text"` |
| | `$option_place_holder_text` | `"#custom_placeholder_text"` |
| | `$text_box_enabled_binding_name` | `"#custom_input_enabled"` |
| | `$text_edit_box_grid_collection_name` | `"custom_form"` |
| | `$max_text_edit_length` | `100` |

confidence: **confirmado**.

---

## 5. Tabela de bindings

### 5.1 Bindings fornecidos pelo engine em `third_party_server_screen`

Verificação: `grep -rn '#form_button_contents\|#form_text\|#submit_text\|#submit_button_visible\|#custom_form_length\|#form_button_texture_file_system'` em **todo** `vanilla/ui/` retorna **apenas** `server_form.json`. São bindings exclusivos desta tela. confidence: **confirmado**.

| Binding | Escopo | Consumido em | `binding_name_override` | `binding_type` |
|---|---|---|---|---|
| `#title_text` | global (screen) | `standard_title_label` via `$text_name` | `"#title_text"` (auto) | `$title_text_binding_type` = `"none"` |
| `#form_text` | global (screen) | `long_form_scrolling_content > main_label` — `"text": "#form_text"` | — (**sem bloco `bindings`!**) | implícito |
| `#form_button_contents` | global (screen) | `long_form_dynamic_buttons_panel` | **`#collection_length`** | default |
| `#form_button_text` | **collection `form_buttons`** | `dynamic_button > form_button` (via `$button_text`), `dynamic_label`, `dynamic_header` | igual ao nome | `collection` |
| `#form_button_texture` | **collection `form_buttons`** | `dynamic_button > panel_name > image` | **`#texture`** | `collection` |
| `#form_button_texture_file_system` | **collection `form_buttons`** | idem | **`#texture_file_system`** | `collection` |
| `#texture` | **view** (propriedade do controle) | `image` (self) e `panel_name`/`progress` (sibling) | `#visible` | `view` |
| `#custom_form_length` | global (screen) | `generated_contents` | **`#collection_length`** | default |
| `#submit_text` | global | `custom_form_scrolling_content > submit_button` | via `$button_text` | `global` + `binding_condition "once"` |
| `#submit_button_visible` | global | `submit_button` | **`#visible`** | default |
| `#custom_text` | collection `custom_form` | `custom_label`, `custom_header`, `custom_toggle`, `custom_dropdown`, `custom_input` | igual | `collection` |
| `#custom_toggle_state` / `#custom_toggle_enabled` / `#custom_toggle_focus_id` | collection `custom_form` | `custom_toggle`, `custom_dropdown_content` | via `$vars` | `collection` |
| `#custom_slider_value` / `_text` / `_text_value` / `_enabled` / `_timeout` | collection `custom_form` | `custom_slider` | via `$vars` | `collection` |
| `#custom_slider_step_value` / `_step_text` / `_step_text_value` / `#custom_slider_steps` | collection `custom_form` | `custom_step_slider` | via `$vars` | `collection` |
| `#custom_dropdown_length` | collection `custom_form` | `custom_dropdown_content` | **`#collection_length`** | `collection` |
| `#custom_radio_toggled` / `#custom_radio_text` | collection `custom_dropdown` | `custom_dropdown_radio` | via `$vars` | `collection` |
| `#custom_input_text` / `#custom_input_enabled` / `#custom_placeholder_text` | collection `custom_form` | `custom_input` | via `$vars` | `collection` |
| `#custom_tooltip_text` | collection `custom_form` | todos os `custom_*` | via `$option_tooltip_text_binding_name` | `collection` |
| `#dropdown_option_text` | collection `custom_form` | `custom_dropdown` | via `$options_dropdown_toggle_label_binding` | `collection` |
| `#close_button_visible` | global | `common.common_panel > close_button_holder` | **`#visible`** | default |
| `#tts_dialog_title` | property_bag | `standard_title_label` | — | `global` + `once` |

### 5.2 Botões (`to_button_id`) que a tela emite

| Botão | Onde | Efeito |
|---|---|---|
| `button.form_button_click` | `dynamic_button > form_button` — `$pressed_button_name` | seleciona item da `form_buttons` |
| `button.submit_custom_form` | `custom_form_scrolling_content > submit_button` | envia ModalForm |
| `button.menu_exit` | `close_button` (`$close_button_to_button_id\|default`) e remapeado de `button.menu_cancel` na raiz | fecha a tela |

confidence: **confirmado**.

### 5.3 `#form_text` sem bloco `bindings` — fato notável

```json
"main_label": {
  "type": "label",
  "offset": [2,2],
  "color": "$main_header_text_color",
  "size": ["100%", "default"],
  "anchor_from": "top_left",
  "anchor_to": "top_left",
  "text": "#form_text"
}
```
Não há `"bindings"`. Só `"text": "#form_text"`. Isso confirma que, para bindings **globais de tela**, o engine resolve `#nome` direto na propriedade `text` sem exigir declaração. confidence: **confirmado**.

Contraste: `standard_title_label` declara binding **e** tem `$title_text_binding_type` setado a `"none"` por `long_form`. Com `binding_type: "none"` o binding declarado é inerte, e o título continua chegando pela mesma resolução implícita de `"text": "$text_name"` → `"#title_text"`. confidence: **provável** (a `"none"` está literal; que o texto ainda apareça é inferência do comportamento vanilla observado em jogo).

### 5.4 `$title_panel` é setado mas **não é lido**

`long_form` e `custom_form` setam `"$title_panel": "common_dialogs.standard_title_label"`. Busca em `ui_template_dialogs.json`: `main_panel_no_buttons` e `title_label` leem `$custom_title_label` e `$use_custom_title_control`, **nunca** `$title_panel`. confidence: **confirmado** — é variável morta no vanilla 1.26.44.

Copiá-la num override é inofensivo, mas **não** é o mecanismo de trocar o título. O mecanismo real é:
```json
"$use_custom_title_control": true,
"$custom_title_label": "meu_ns.meu_titulo"
```

### 5.5 Ordem dos bindings

No `image` vanilla a ordem é:
1. `#form_button_texture` → **escreve** `#texture`
2. `#form_button_texture_file_system` → **escreve** `#texture_file_system`
3. `view` que **lê** `#texture` → escreve `#visible`

O `view` vem **depois** dos que escrevem. confidence: **confirmado** (a ordem é literal).

Generalização (bindings avaliados na ordem declarada; um `view` só enxerga o que já foi escrito): **provável** — consistente com todo o vanilla lido, não provado por experimento.

### 5.6 `resolve_sibling_scope` — o padrão vanilla de "olhar o irmão"

```json
{
  "binding_type": "view",
  "source_control_name": "image",
  "resolve_sibling_scope": true,
  "source_property_name": "(not (#texture = ''))",
  "target_property_name": "#visible"
}
```
Usado **duas vezes** no `dynamic_button`:
- no `panel_name` (que é o **pai** do `image`) — `(not (#texture = ''))` → esconde o slot de 34px inteiro quando não há ícone;
- no `progress` (que é **irmão** do `image`) — `(#texture = 'loading')` → mostra a barra durante o download.

Nos dois casos `source_control_name` é o **nome literal** `"image"`. Renomear o `image` num override quebra ambos, silenciosamente. confidence: **confirmado**.

### 5.7 Sintaxe de expressão observada no vanilla

Operadores confirmados dentro de `source_property_name` / `requires` / `ignored`:

| Forma | Exemplo literal | Onde |
|---|---|---|
| `not` | `"(not (#texture = ''))"` | `server_form.json:157` |
| `or` | `"(not ((#texture = '') or (#texture = 'loading')))"` | `server_form.json:186` |
| `and` | `"($show_close_button and $use_compact_close_button)"` | `ui_template_dialogs.json:375` |
| `=` com literal string | `"(#texture = 'loading')"` | `server_form.json:203` |
| `$var` booleana crua | `"ignored": "$use_custom_title_control"` | `ui_template_dialogs.json:53` |
| `(not $var)` | `"ignored": "(not $use_custom_title_control)"` | `ui_template_dialogs.json:56` |

confidence: **confirmado**. Não há no vanilla nenhum uso do operador `-` (subtração de string) que o SonheMenu emprega no marcador de título — ver §7.1.

---

## 6. Pontos de override seguros

### 6.1 O que um pack pode sobrescrever por **nome simples**

Regra do JSON UI: declarar `"namespace": "server_form"` num arquivo do pack e usar uma chave com o **mesmo nome** de um controle vanilla substitui aquele controle globalmente. Confidence do mecanismo: **confirmado pelo uso** — o `sonhe_forms.json` do projeto já faz exatamente isso e funciona.

| Controle | Override por nome simples | Risco | Nota |
|---|---|---|---|
| `third_party_server_screen` | possível | **ALTO** | é `type: screen`; errar aqui derruba a tela inteira |
| `main_screen_content` | possível | **ALTO** | perder o `type: factory` com `control_ids` mata os dois ramos de uma vez |
| **`long_form`** | possível | **BAIXO** | ✅ **ponto de override recomendado** — folha do factory raiz, ninguém mais o referencia |
| `long_form_panel` | possível | BAIXO | referenciado só por `long_form` via `$child_control` |
| `long_form_scrolling_content` | possível | BAIXO | referenciado só por `long_form_panel` via `$scrolling_content` |
| `long_form_dynamic_buttons_panel` | possível | MÉDIO | referenciado por `long_form_scrolling_content` **com `@`** |
| **`dynamic_button`** | possível | MÉDIO | ⚠ referenciado **sem `@`** no `control_ids` — ver §6.2 |
| `dynamic_label` / `dynamic_header` | possível | BAIXO | folhas do factory |
| `custom_form` + toda a subárvore `custom_*` | possível | BAIXO | independente do `long_form`; não mexer se só o ActionForm interessa |
| `generated_contents` / `custom_form_scrolling_content` | possível | MÉDIO | folhas do ramo B |

**Regra de ouro derivada:** quanto mais **fundo na árvore** e mais **folha**, mais seguro. `long_form` é o nó mais alto que ainda é folha do ponto de vista do factory raiz. confidence: **provável** (dedução a partir da árvore confirmada).

### 6.2 A assimetria `@` vs. sem `@` no `control_ids` — armadilha real

```json
"control_ids": {
  "button": "server_form.dynamic_button",      // <- SEM @
  "label": "@server_form.dynamic_label",       // <- COM @
  "header": "@server_form.dynamic_header",     // <- COM @
  "divider": "@settings_common.option_group_section_divider"
}
```
vs. no factory raiz:
```json
"control_ids": {
  "long_form": "@server_form.long_form",
  "custom_form": "@server_form.custom_form"
}
```
confidence: **confirmado** (ambos lidos literalmente, no mesmo arquivo).

- `"@ns.controle"` = **referência/herança**: o factory instancia um controle que *herda* daquele.
- `"ns.controle"` (sem `@`) = **nome direto do controle**.

Reproduzir essa grafia **exatamente** ao copiar um factory. Trocar `"server_form.dynamic_button"` por `"@server_form.dynamic_button"` (ou vice-versa) muda a resolução do factory. Se o factory não resolve o `control_ids`, a coleção não instancia nada — tela vazia / fallback, **sem erro no ContentLog**. confidence do diagnóstico: **suspeita** (plausível pelo código; não reproduzido aqui).

### 6.3 Contratos que um override de `long_form` **precisa** honrar

**Se o override herda `@common_dialogs.main_panel_no_buttons`**, ele **deve** fornecer:

1. `$child_control` — **sem `|default`** em `main_panel_no_buttons`. Obrigatório.
2. `size` — o pai `main_screen_content` é `[0,0]`; nada de `100%` funciona a partir dele.

**Se o override NÃO herda** (é um `panel` próprio, como no SonheMenu), nada é obrigatório — mas também **nada** é herdado: sem fundo, sem close button, sem title label, sem `anchor: center`. Cada um desses precisa ser reconstruído à mão.

**Se o override monta a própria grade**, ele **deve** fornecer, para o clique funcionar:
- `collection_name: "form_buttons"` no contêiner;
- `$pressed_button_name: "button.form_button_click"` no botão;
- um binding `collection_details` com `binding_collection_name: "form_buttons"` no botão (é o que diz *qual índice* foi clicado).

confidence: **confirmado** (os três estão literais no `dynamic_button` vanilla).

### 6.4 Textura vem de binding, não de propriedade

O ícone vanilla é:
```json
"image": {
  "type": "image",
  "layer": 2,
  "size": [32, 32],
  "offset": [0, 0],
  "bindings":[ … ]
}
```
**Sem `"texture"`.** Um override que adicione `"texture": "textures/ui/algo"` a esse `image` cria uma textura estática que o binding pode ou não sobrepor. confidence: **confirmado** (a ausência é literal).

### 6.5 Nomes literais que **não podem** ser renomeados

| Nome | Onde é referenciado por string | Consequência de renomear |
|---|---|---|
| `"image"` (dentro de `panel_name`) | `source_control_name` em 2 bindings `view` | ícone/progress param de esconder |
| `"scrolling_content"` | `common.scroll_view_control` → `"scroll_content"` | scroll para de funcionar |
| `"default"` / `"hover"` / `"pressed"` / `"locked"` | `common.button` → `default_control` etc. | estados do botão somem |
| `"track"` / `"box"` / `"bar_and_track"` / `"scrolling_view_port"` | `common.scroll_view_control` | scrollbar quebra |
| `"inside_header_panel"` | `$option_tooltip_area` / `$dropdown_area` do ramo B | tooltip/dropdown do ModalForm quebram |
| `"buttons"` (nome do factory) | `"name": "buttons"` nos dois factories | factory não popula |
| `"form_buttons"` / `"custom_form"` / `"custom_dropdown"` | `collection_name` + `binding_collection_name` | coleção não resolve |

confidence: **confirmado** para todos.

### 6.6 Cores globais que valem lembrar (`_global_variables.json`)

```json
"$light_button_default_text_color": [ 0.3, 0.3, 0.3 ],
"$light_button_hover_text_color": [ 1.0, 1.0, 1.0 ],
"$light_button_pressed_text_color": [ 1.0, 1.0, 1.0 ],
"$light_button_locked_text_color": [ 0.3, 0.3, 0.3 ],
"$title_text_color": [ 0.3, 0.3, 0.3 ],
"$main_header_text_color": [ 1.0, 1.0, 1.0 ],
"$sub_header_text_color": [ 1.0, 1.0, 1.0 ],
"$generic_button_text_color": [ 1.0, 1.0, 1.0 ],
```
confidence: **confirmado** (`_global_variables.json:3-8, 37, 40-41`).

> **Consequência direta para tema escuro:** `$title_text_color` é **cinza escuro** `[0.3,0.3,0.3]`. Qualquer título que herde `standard_title_label` **some** sobre fundo preto. Já `$main_header_text_color` é branco `[1,1,1]` — por isso `#form_text` e os `option_group_label` aparecem bem no escuro. Mesma lógica para `$light_button_default_text_color`: o texto do botão vanilla é escuro por padrão e só vira branco no hover.

### 6.7 Ganchos vanilla de baixo risco (mudar aparência sem tocar na topologia)

| Gancho | Evidência | Efeito |
|---|---|---|
| `$use_custom_title_control` + `$custom_title_label` | `ui_template_dialogs.json:43-44, 53-56` | trocar o título **mantendo** toda a herança de `main_panel_no_buttons` |
| `$panel_indent_size` | `ui_template_dialogs.json:210` | ampliar a área útil sem mexer no `$child_control` |
| `$custom_background` | `ui_template_dialogs.json:211` | trocar `dialog_background_hollow_3` por outro fundo |
| `$show_close_button` (default `true`) | `ui_common.json:5856` | esconder o X |
| `$fill_alpha` (default `0.8`) | `ui_template_dialogs.json:363` | escurecer o fundo vanilla **sem** empilhar um `image` próprio |
| `$button_state_panel` | `ui_template_buttons.json:342` | trocar o corpo dos 4 estados de um `light_text_button` numa variável só |
| `$button_text_max_size` | `ui_template_buttons.json:500` | vanilla força 1 linha (`["100%",10]`); o `dynamic_button` já sobe pra `["100%",20]` |
| `$title_offset` (default `[0,9]`) | `ui_template_dialogs.json:41-42` | reposicionar o título |
| `common_dialogs.form_fitting_main_panel_no_buttons` | `ui_template_dialogs.json:320-331` | painel `["100%","100%c"]` que **cresce com o conteúdo** — caminho vanilla para altura adaptativa |

---

## 7. Aplicação no SonheMenu

Arquivos do pack (**leitura apenas; nada foi editado**):
- `c:/Users/Desktop/Desktop/Projetos/bot/ADDONS/SonheMenu_RP/ui/_ui_defs.json`
- `c:/Users/Desktop/Desktop/Projetos/bot/ADDONS/SonheMenu_RP/ui/sonhe_forms.json`
- `c:/Users/Desktop/Desktop/Projetos/bot/ADDONS/SonheMenu_RP/ui/sonhe_grid.json`
- `c:/Users/Desktop/Desktop/Projetos/bot/ADDONS/SonheMenu_RP/manifest.json`

### 7.1 O que o pack faz hoje, confrontado com o vanilla

`sonhe_forms.json` declara `"namespace": "server_form"` e sobrescreve **apenas** `long_form`:

```json
"long_form": {
  "type": "panel",
  "controls": [
    { "sonhe_vanilla_form@common_dialogs.main_panel_no_buttons": { … } },
    { "sonhe_custom_form@sonhe_forms.grid_screen": { … } }
  ]
}
```

**Confronto ponto a ponto:**

| Aspecto | Vanilla | SonheMenu | Veredicto |
|---|---|---|---|
| Nó sobrescrito | `long_form@common_dialogs.main_panel_no_buttons` | `long_form` como `type: panel` puro | ✅ Correto — §6.1 marca `long_form` como o ponto recomendado. O pack **abandona** a herança e vira um panel que hospeda dois ramos. Válido: nada além do factory raiz referencia `long_form`. |
| Ramo vanilla preservado | — | `sonhe_vanilla_form@common_dialogs.main_panel_no_buttons` replica `$title_size`, `$text_name`, `$title_text_binding_type`, `$child_control`, `size`, `layer` | ✅ Fiel. **Divergências:** usa `[ "100% - 14px", 10 ]` (vanilla: `[ "100% - 15px", 10 ]`) e **omite `$title_max_size`** (cai no default `["default",10]`). Cosmético. |
| `$child_control` do ramo vanilla | `"server_form.long_form_panel"` | idem | ✅ Correto **e obrigatório** (§6.3, sem `\|default`). Depende de `long_form_panel` **não** ser sobrescrito. Ele não é. |
| Alternância vanilla/custom | não existe | binding `view` sobre `#title_text` com marcador `'§d§r§e§a§m§r'` e operador `-` de string | ⚠ Padrão **não-vanilla**. O mecanismo (`binding_type: "view"` + `target_property_name: "#visible"`) é exatamente o do `dynamic_button` (§5.6) ✅, mas o operador `-` de subtração de string **não tem nenhum precedente** em `server_form.json` nem em `ui_template_dialogs.json` (§5.7). confidence: **suspeita** — funciona empiricamente no projeto, mas não é sintaxe atestada nas fontes lidas. |
| `size` do ramo custom | `long_form` vanilla tem `size [225,200]` | `grid_screen` tem `size [320,452]` **próprio** + `anchor: center` | ✅ Correto **e necessário** — o `long_form` do pack não declara `size`, e o pai `main_screen_content` é `[0,0]` (§6.3 item 2). O `grid_screen` se ancora sozinho. |
| Coleção | `collection_name: "form_buttons"` + binding `#form_button_contents` → `#collection_length` | `tiles_grid` usa `collection_name: "form_buttons"` **sem** binding de contagem, com `grid_dimensions: [3,4]` | ⚠ Divergência estrutural deliberada (documentada no `//5` do próprio arquivo). **Não há precedente vanilla** de `type: grid` sobre `form_buttons` — todo o vanilla usa `factory` + `stack_panel`. confidence: **suspeita**. Consequência confirmada: altura fixa em 12 slots. |
| Ícone | `image` sem `"texture"`, com `#form_button_texture`→`#texture`, `#form_button_texture_file_system`→`#texture_file_system`, e `view` de `#visible` **por último** | `tile_icon` reproduz os 3 bindings **na mesma ordem**, sem `"texture"` | ✅ **Fiel ao vanilla**, inclusive na ordem (§5.5). O par de âncoras `#null` extra (`collection` + `collection_details`) é adição do pack, **sem precedente vanilla** — o `dynamic_button` põe `collection_details` **só no botão**, não em cada folha. confidence: **suspeita** de ser desnecessário nas folhas; inofensivo. |
| Clique | `$pressed_button_name: "button.form_button_click"` + binding `collection_details` sobre `form_buttons` | `tile_button@common.button` com os dois | ✅ Correto (§6.3). |
| Estados do botão | `light_text_button` → `default`/`hover`/`pressed`/`locked` via `$button_state_panel`, layers 1/4/5/1 | `tile_button` declara `default_control`/`hover_control`/`pressed_control` explícitos + 3 faces com layers 1/4/5 | ✅ Consistente. `common.button` (`ui_common.json:80-84`) **já** define esses três nomes e `locked_control: ""`; redeclarar é redundante mas correto. Os layers 1/4/5 batem exatamente com `light_text_button` (§4.7) — o comentário `//faces` do pack acertou. |
| Título | `standard_title_label` com `color: "$title_text_color"` = `[0.3,0.3,0.3]` | `screen_title` com `color: [1.0,1.0,1.0]` na mão, `font_type "MinecraftTen"` | ✅ **Decisão correta e agora confirmada na fonte** — §6.6 mostra que herdar `$title_text_color` daria cinza escuro invisível sobre preto. O comentário `//` do arquivo estava certo. |
| Corpo | `main_label` com `"text": "#form_text"` e **sem** bloco `bindings` | `screen_body` com `"text": "#form_text"` **e** `bindings: [{"binding_name": "#form_text"}]` | ✅ Ambos funcionam. O vanilla prova que o bloco é dispensável (§5.3); tê-lo é redundância segura. |
| Fallback em lista | `long_form_dynamic_buttons_panel` + `dynamic_button` | `sonhe_forms.buttons_factory` + `row_button` + `row_icon_holder` | ✅ **Cópia estruturalmente fiel**, incluindo `#form_button_contents`→`#collection_length`, o factory de nome `"buttons"`, e o `view` com `resolve_sibling_scope`. E o `control_ids.button` do pack é `"sonhe_forms.row_button"` — **sem `@`**, igual ao vanilla (§6.2). ✅ |
| Nome do controle no `source_control_name` | `"image"` | `"row_icon"` (e o `image` filho **se chama** `row_icon`) | ✅ Renomeado de forma **consistente** nos dois lados. É o jeito certo de renomear (§6.5). |

### 7.2 Hipóteses para "a UI custom some sem `[UI][error]`", ranqueadas pela evidência deste documento

1. **Falha de resolução de `$variável` obrigatória.** `$child_control` (`main_panel_no_buttons`) e `$scrolling_content` (`common.scrolling_panel`) **não têm `|default`**. Uma referência não resolvida vira controle vazio, não erro. confidence da ausência de default: **confirmado**; do sintoma silencioso: **suspeita**.
2. **Grafia `@` no `control_ids` de factory.** §6.2 — a assimetria vanilla é literal, e factory que não resolve não loga. confidence: **suspeita**.
3. **Nome literal em `source_control_name` / `default_control` / `scroll_content`.** §6.5 — são strings, não referências verificadas. Renomear quebra sem log. confidence da dependência por nome: **confirmado**; do silêncio: **suspeita**.
4. **Uso de sintaxe de expressão não atestada** (operador `-` de string no marcador de título, §5.7). Se uma versão do engine mudar o parser, a expressão vira `false` e **os dois ramos** ficam invisíveis ao mesmo tempo — sintoma exatamente igual a "caiu na lista vanilla". confidence: **suspeita**, mas é a hipótese que melhor explica "mudança mínima → some".
5. **`grid` + `grid_dimensions` sobre `form_buttons` sem binding de contagem.** Sem precedente vanilla (§7.1). confidence: **suspeita**.
6. **Herança circular / filho com nome igual ao `@base`.** Listado como proibido no comentário `//3` do `sonhe_grid.json`. Não há evidência nas fontes lidas que confirme ou negue — **suspeita**, herdada da experiência do projeto.

### 7.3 Ganchos vanilla ainda não explorados pelo pack

| Gancho | Evidência | Uso possível no SonheMenu |
|---|---|---|
| `$use_custom_title_control` + `$custom_title_label` | `ui_template_dialogs.json:43-44, 53-56` | trocar só o título do ramo vanilla **mantendo** toda a herança, em vez de reconstruir |
| `common_dialogs.form_fitting_main_panel_no_buttons` | `ui_template_dialogs.json:320-331` | painel `["100%","100%c"]` que **cresce com o conteúdo** — o caminho vanilla para a altura adaptativa que o `//5` do `sonhe_grid.json` diz não ter conseguido |
| `$fill_alpha` do `dialog_background_hollow_common` | `ui_template_dialogs.json:363` | escurecer o fundo vanilla sem empilhar `image` próprio (hoje o pack empilha `panel_bg` alpha 0.9 + `fd_bg` alpha 0.85, que é o que causou a diferença de opacidade cabeçalho vs. tiles descrita no comentário `//` do `panel_bg`) |
| `$button_state_panel` | `ui_template_buttons.json:342` | substituir as 3 faces manuais por uma variável só, mantendo o `light_text_button` inteiro |
| `$panel_indent_size` | `ui_template_dialogs.json:210` | ampliar a área do ramo vanilla |
| `settings_common.option_group_section_divider` | `settings_common.json:167-182` | já é o `divider` do factory; o `title_rule` do pack reimplementa o mesmo com `white_background` |

### 7.4 Checklist antes de tocar em `sonhe_forms.json` / `sonhe_grid.json`

- [ ] O `long_form` sobrescrito continua sendo o **único** nome do namespace `server_form` que o pack redefine? (Hoje: **sim** — `sonhe_grid.json` usa namespace próprio `sonhe_forms`.)
- [ ] O ramo vanilla ainda passa `$child_control` = `"server_form.long_form_panel"`?
- [ ] O ramo custom ainda declara `size` próprio? (`main_screen_content` é `[0,0]`.)
- [ ] Todo controle que lê a coleção tem `collection_name` / `binding_collection_name` grafado **exatamente** `form_buttons`?
- [ ] O botão de tile ainda tem `$pressed_button_name: "button.form_button_click"` **e** um binding `collection_details`?
- [ ] O `image` do ícone continua **sem** propriedade `"texture"`, com `#form_button_texture` **e** `#form_button_texture_file_system`?
- [ ] Os bindings `view` continuam **depois** dos bindings que escrevem a propriedade que eles leem?
- [ ] Nenhum `source_control_name` aponta para um nome que foi renomeado? (Hoje: `row_icon` ↔ `row_icon`, consistente.)
- [ ] Os `control_ids` de factory mantêm a grafia `@` / sem-`@` original?
- [ ] `version` do `manifest.json` foi incrementada (hoje `[1,0,36]`) para furar cache do cliente?

---

## 8. Apêndice — evidências de verificação

### 8.1 `common_dialogs` não é um arquivo

```
$ ls vanilla/ui/common_dialogs.json
No such file or directory

$ grep -l '"namespace": *"common_dialogs"' vanilla/ui/*.json
ui_template_dialogs.json
```
confidence: **confirmado**. Qualquer doc ou prompt do projeto que aponte para `vanilla/ui/common_dialogs.json` deve ser corrigido para `vanilla/ui/ui_template_dialogs.json`.

### 8.2 Onde cada namespace dependente mora

```
$ grep -l '"namespace": *"common_buttons"' vanilla/ui/*.json
ui_template_buttons.json

$ grep -rl '"namespace": *"settings_common"' vanilla/ui/
vanilla/ui/settings_sections/settings_common.json

$ grep -l '"namespace": *"common"' vanilla/ui/*.json
ui_common.json

$ grep -l '"namespace": *"progress"' vanilla/ui/*.json
progress_screen.json
```
confidence: **confirmado**.

### 8.3 Bindings de `server_form` são exclusivos da tela

```
$ grep -rn '#form_button_contents|#form_text|#submit_text|#submit_button_visible|#custom_form_length|#form_button_texture_file_system' vanilla/ui/ --include=*.json | grep -v server_form.json
(nenhum resultado)
```
Só `#title_text` aparece em outras telas (`disconnect_screen.json`, `npc_interact_screen.json`, `add_external_server_screen.json`, `gathering_info_screen.json`, `progress_screen.json`, `persona_popups.json`, `persona_sdl.json`) — é um binding **genérico de diálogo**, não exclusivo do `server_form`. confidence: **confirmado**.

Isso tem uma consequência prática: **`#title_text` não é prova de que a tela é um server_form**. O marcador de título do SonheMenu é a única forma de distinguir. confidence: **confirmado**.

### 8.4 `progress.progress_loading_bars` (usado pelo ícone em carregamento)

```json
"progress_loading_bars": {
  "type": "image",
  "layer": 2,
  "texture": "textures/ui/loading_bar",
  "anchor_from": "center",
  "anchor_to": "center",
  "offset": [ 0, 24 ],
  "size": [ 64, 8 ],
  "uv_size": [ 64, 8 ],
  "uv": "@progress.bar_animation",
  "color": [ 0.7, 0.7, 0.7, 1.0 ],
  "bindings": [
    {
      "binding_name": "#bar_animation_visible",
      "binding_name_override": "#visible"
    }
  ]
},
```
confidence: **confirmado** (`progress_screen.json:541-558`).

Note que ele **já traz** um binding próprio de `#visible` (`#bar_animation_visible`). O `dynamic_button` adiciona um **segundo** binding de `#visible` por cima. Dois bindings escrevendo a mesma propriedade — o vanilla faz isso deliberadamente. confidence: **confirmado**; qual vence: **suspeita** (provavelmente o último declarado).
