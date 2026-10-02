# Fonte: addon "JSON UI #2" (stack_panel horizontal)

Origem: `c:/Users/Desktop/Downloads/ADDONS EXEMPLOS/ui2/`
Metadata do proprio pack: `"url": "https://youtu.be/CWm-KU5ALOQ"` (`ui2/BP/manifest.json`)
Data da leitura: 2026-08-28. Corpus vanilla usado para conferencia: `c:/Users/Desktop/Documents/Nova pasta/assets/assets/resource_packs/vanilla/ui/` (188 arquivos).

---

## 1. Resumo

O addon inteiro cabe em **um unico arquivo de UI**:

```
ui2/BP/manifest.json
ui2/BP/pack_icon.png
ui2/BP/scripts/main.js
ui2/RP/manifest.json
ui2/RP/pack_icon.png
ui2/RP/ui/server_form.json      <- 8229 bytes, o unico arquivo de UI
```

Nao existe `_ui_defs.json`. Nao existe pasta `textures/`. Nao existe tema.
Toda a customizacao e: redefinir `server_form.long_form` como um `panel` com **dois filhos irmaos mutuamente exclusivos por view binding no `#title_text`**, e o ramo custom aponta para um `stack_panel horizontal` com `factory` que produz tiles de 80x80.

O que ele **prova** (e o que mais interessa pro nosso problema de falha silenciosa):

- Override de `server_form` funciona **sem `_ui_defs.json` no pack**, so colocando o arquivo em `ui/server_form.json`.
- O merge e **por def, nao por arquivo**: o pack redefine so 3 defs (`long_form`, `my_super_custom_panel`, `custom_button`) e continua conseguindo referenciar `server_form.long_form_panel`, que existe **so no vanilla**.
- O caminho de tile com icone + label proprios usa `image` **sem propriedade `texture`**, recebendo a textura por `binding_name_override`.

---

## 2. Tabela de padroes

| Aspecto | O que o ui2 faz | Vanilla faz | Confidence |
|---|---|---|---|
| Registro do arquivo | nenhum `_ui_defs.json` no RP; so `ui/server_form.json` | vanilla `_ui_defs.json:142` ja lista `"ui/server_form.json"` | confirmado |
| Escopo do override | redefine **3 defs**, herda o resto do vanilla | — | confirmado |
| Ponto de entrada | redefine `long_form` de `@common_dialogs.main_panel_no_buttons` para `type: "panel"` puro | `long_form@common_dialogs.main_panel_no_buttons` | confirmado |
| Chave de troca de tela | `#title_text` exato: `(#title_text = 'Custom Form')` | nao existe | confirmado |
| Ramo vanilla | recria o `main_panel_no_buttons` a mao e aponta `$child_control` para `server_form.long_form_panel` (def do vanilla) | idem sem bindings | confirmado |
| Container da colecao | `type: "stack_panel"`, `orientation: "horizontal"`, `size: ["100%c", 80]` | `stack_panel` vertical `["100% - 4px","100%c"]` | confirmado |
| Fabrica | `"factory": { "name": "buttons", "control_name": "server_form.custom_button" }` | `"factory": { "name":"buttons", "control_ids": { "button":…, "label":…, "header":…, "divider":… } }` | confirmado |
| Contagem da colecao | `#form_button_length` -> `#collection_length` | `#form_button_contents` -> `#collection_length` | confirmado (divergencia) |
| Item | `panel` **pixel fixo** `[80,80]`, filho `[64,64]` | `stack_panel` `["100%", 32]` | confirmado |
| Icone | `type: "image"` **sem `texture`**, `#form_button_texture` -> `#texture` + `#form_button_texture_file_system` -> `#texture_file_system` | identico | confirmado |
| Botao clicavel | `@common_buttons.light_text_button` com `$button_text: "#null"` | mesmo template com `$button_text: "#form_button_text"` | confirmado |
| Rotulo | `label` proprio, `text: "#form_button_text"`, `color: [0,0,0]` | o proprio botao desenha o texto | confirmado |
| Ancora de colecao no item | `collection_details` **so no botao**; icone/label so `collection` | identico ao vanilla | confirmado |
| Tema | **nenhum** — zero textura custom, zero cor de fundo | — | confirmado |
| Scroll | **nao tem** | `common.scrolling_panel` | confirmado |

---

## 3. Regras extraidas (com evidencia)

### R1 — Override de `server_form` NAO exige `_ui_defs.json` no seu pack
**Confidence: confirmado.**
Listagem completa do RP (`find ui2 -type f`):

```
ui2/RP/manifest.json
ui2/RP/pack_icon.png
ui2/RP/ui/server_form.json
```

Nao ha `_ui_defs.json`. O vanilla ja registra o caminho:

`vanilla/ui/_ui_defs.json:142`
```json
    "ui/server_form.json",
```

Ou seja: para **arquivos que o vanilla ja registra**, basta reproduzir o caminho. `_ui_defs.json` no seu pack e necessario apenas para **arquivos novos** (o nosso `ui/sonhe_grid.json`).

### R2 — O merge do override e por DEF, nao por ARQUIVO
**Confidence: confirmado.**
O arquivo do ui2 tem exatamente estas chaves de topo (verificado por parse):

```
['namespace', '$schema', 'long_form', 'my_super_custom_panel', 'custom_button']
```

E ainda assim o ramo 1 referencia:

`ui2/RP/ui/server_form.json`
```json
"$child_control": "server_form.long_form_panel",
```

`server_form.long_form_panel` **nao esta no arquivo do pack** — so no vanilla (`vanilla/ui/server_form.json:47`). Logo, defs nao redefinidas continuam vindo do vanilla. Corolario direto para nos: **redefinir uma def parcialmente (sem `type` e sem `@base`) a apaga**, e nao ha erro — a tela vira um controle sem tipo.

### R3 — A chave de tela e um par de view bindings sobre `#title_text`, e o par do ui2 tem BURACO
**Confidence: confirmado (o codigo), suspeita (a consequencia em jogo).**

Ramo vanilla:
```json
{
  "binding_type": "view",
  "source_property_name": "((#title_text - 'Custom Form') = #title_text)",
  "target_property_name": "#visible"
}
```
Ramo custom:
```json
{
  "binding_type": "view",
  "source_property_name": "(#title_text = 'Custom Form')",
  "target_property_name": "#visible"
}
```

As duas expressoes **nao sao complementares**. A primeira e "o titulo NAO contem a substring". A segunda e "o titulo E EXATAMENTE a string". Titulo `"Custom Form - Loja"` cai no buraco: contem a substring (ramo vanilla invisivel) e nao e igual (ramo custom invisivel) => **dialogo vazio, sem nenhum erro**. Esse e literalmente um modo de falha silenciosa.

O par correto e o que ja usamos em `sonhe_forms.json`: a segunda expressao tem que ser o `not` da primeira.

### R4 — Os dois ramos carregam `{ "binding_name": "#title_text" }` sem `binding_type` antes do view binding
**Confidence: confirmado.**
```json
"bindings": [
  { "binding_name": "#title_text" },
  {
    "binding_type": "view",
    "source_property_name": "((#title_text - 'Custom Form') = #title_text)",
    "target_property_name": "#visible"
  }
]
```
O binding de dado **vem primeiro** e serve de ancora: sem ele, `#title_text` nao esta no escopo do controle e o view binding le vazio. Padrao identico ao nosso `sonhe_forms.json`.

### R5 — `#form_button_length` nao aparece em nenhum arquivo vanilla
**Confidence: confirmado (a ausencia). Provavel que seja um alias real da engine.**
```
grep -rn 'form_button_length'  vanilla/ui/  ->  0 hits
grep -rn 'form_button_contents' vanilla/ui/ ->  1 hit (server_form.json:140)
```
`vanilla/ui/server_form.json:138-142`
```json
    "collection_name": "form_buttons",
    "bindings": [
      {
        "binding_name": "#form_button_contents",
        "binding_name_override": "#collection_length"
      }
    ]
```
ui2 usa:
```json
    "collection_name": "form_buttons",
    "bindings": [
      {
        "binding_name": "#form_button_length",
        "binding_name_override": "#collection_length"
      }
    ]
```
Os dois addons de terceiros (ui2 e ui3) usam `#form_button_length`; a Mojang usa `#form_button_contents`. Como um binding_name inexistente resolve para vazio **sem erro**, este e outro candidato classico a "sumiu e nao logou nada". **Regra pratica: usar `#form_button_contents`.**

### R6 — O item da colecao e PIXEL FIXO nos dois niveis
**Confidence: confirmado.**
```json
"custom_button": {
    "type": "panel",
    "size": [80, 80],
    "controls": [
        { "main_ui": { "type": "panel", "size": [64, 64], ... } }
    ]
}
```
e o pai:
```json
"size": ["100%c", 80],
```
Pai `%c` no eixo X + filho em px = **ciclo fechado**. Se o item fosse `["100%", 80]` dentro de um pai `100%c`, a dependencia seria circular e a engine resolveria pra 0px em silencio. Confere com a regra ja anotada em `SonheMenu_RP/docs/JSON_UI_NOTAS.md`.

### R7 — O icone e um `image` SEM `texture`
**Confidence: confirmado.** Copia literal do vanilla `server_form.dynamic_button`.
```json
"image": {
    "type": "image",
    "layer": 200,
    "size": [32, 32],
    "offset": [0, -5],
    "bindings": [
        { "binding_name": "#form_button_texture",             "binding_name_override": "#texture",             "binding_type": "collection", "binding_collection_name": "form_buttons" },
        { "binding_name": "#form_button_texture_file_system",  "binding_name_override": "#texture_file_system", "binding_type": "collection", "binding_collection_name": "form_buttons" },
        { "binding_type": "view", "source_property_name": "(not ((#texture = '') or (#texture = 'loading')))", "target_property_name": "#visible" }
    ]
}
```
Ordem obrigatoria: os dois `binding_name_override` **antes** do view binding que le `#texture`. O view binding le a propriedade **ja escrita** pelos bindings anteriores no mesmo controle.

### R8 — Esconder a moldura vazia se faz com `resolve_sibling_scope` apontando pro filho
**Confidence: confirmado.**
```json
"panel_name": {
    "type": "panel",
    "size": [64, 64],
    "bindings": [
        {
            "binding_type": "view",
            "source_control_name": "image",
            "resolve_sibling_scope": true,
            "source_property_name": "(not (#texture = ''))",
            "target_property_name": "#visible"
        }
    ],
    "controls": [ { "image": { ... } } ]
}
```
Note: `source_control_name: "image"` + `resolve_sibling_scope: true` — apesar do nome, aqui `image` e **filho**, nao irmao. Padrao copiado tal e qual do vanilla (`vanilla/ui/server_form.json:158-166`).

### R9 — O botao vira "casca clicavel": `$button_text: "#null"`
**Confidence: confirmado.**
```json
"form_button@common_buttons.light_text_button": {
    "$pressed_button_name": "button.form_button_click",
    "anchor_from": "top_left",
    "anchor_to": "top_left",
    "size": [64, 64],
    "$button_text": "#null",
    "$button_text_binding_type": "collection",
    "$button_text_grid_collection_name": "form_buttons",
    "$button_text_max_size": ["100%", 20],
    "bindings": [
        { "binding_type": "collection_details", "binding_collection_name": "form_buttons" }
    ]
}
```
Diferencas contra o vanilla (`vanilla/ui/server_form.json:212-227`): so `size` (`["fill",32]` -> `[64,64]`) e `$button_text` (`"#form_button_text"` -> `"#null"`). Tudo o mais e copia. **`$pressed_button_name": "button.form_button_click"` e o que devolve o indice pro ActionFormData** — sem isso o clique nao resolve a Promise do script.

### R10 — `collection_details` fica SO no botao
**Confidence: confirmado.** No `custom_button` inteiro, `collection_details` aparece exatamente uma vez, dentro de `form_button`. Icone e label usam so `binding_type: "collection"`. E o mesmo reparto do vanilla.

### R11 — Layers desencontrados: `image` layer 200, `label` layer 32, botao layer 1
**Confidence: confirmado.**
`"layer": 200` no icone e `"layer": 32` no label. O `common_buttons.light_text_button` usa `layer: 1/4/5` nos estados (`vanilla/ui/ui_template_buttons.json`, `light_text_button@light_button_assets`). Valores altos garantem que icone e texto ficam **acima** de qualquer estado do botao. Esse e o truque que faz o tile ter cara propria sem tocar nas texturas do botao.

### R12 — Chave `$schema` no topo do arquivo e inofensiva
**Confidence: provavel.**
```json
{
    "namespace": "server_form",
    "$schema": "https://kalmemarq.github.io/Bugrock-JSON-UI-Schemas/ui.schema.json",
```
Chave iniciada por `$` na raiz do arquivo e tratada como definicao de variavel, nao como control def, entao nao gera `Type not specified`. O addon esta em producao com ela.

### R13 — Sem scroll: overflow horizontal e silencioso
**Confidence: provavel.**
`my_super_custom_panel` e um `panel ["100%","100%"]` e dentro dele um `stack_panel horizontal ["100%c", 80]`. O dialogo tem `"size": [360, 150]`, com `$panel_indent_size` default `["100% - 16px", "100% - 31px"]` (`vanilla/ui/ui_template_dialogs.json:205-210`), ou seja ~344px uteis. 4 botoes x 80px = 320px cabe. **O 5o botao passa de 400px e simplesmente sai da tela**, sem erro e sem scroll. O `main.js` do ui2 tem exatamente 4 botoes — o layout foi calibrado a mao pro conteudo.

---

## 4. JSON literal — `ui2/RP/ui/server_form.json` (integral)

```json
{
    "namespace": "server_form",
    "$schema": "https://kalmemarq.github.io/Bugrock-JSON-UI-Schemas/ui.schema.json",

    "long_form": {
        "type": "panel",
        "size": ["100%", "100%"],
        "controls": [
            {
                "long_form@common_dialogs.main_panel_no_buttons": {
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
                "long_form@common_dialogs.main_panel_no_buttons": {
                    "$title_panel": "common_dialogs.standard_title_label",
                    "$title_size": ["100% - 14px", 10],
                    "size": [360, 150],
                    "$text_name": "#title_text",
                    "$title_text_binding_type": "none",
                    "$child_control": "server_form.my_super_custom_panel",
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
    "my_super_custom_panel": {
        "type": "panel",
        "size": ["100%", "100%"],
        "controls": [
            {
                "long_form_dynamic_buttons_panel": {
                    "type": "stack_panel",
                    "size": ["100%c", 80],
                    "orientation": "horizontal",
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
                            "binding_name_override": "#collection_length"
                        }
                    ]
                }
            }
        ]
    },
    "custom_button": {
        "type": "panel",
        "size": [80, 80],
        "controls": [
            {
                "main_ui": {
                    "type": "panel",
                    "size": [64, 64],
                    "controls": [
                        {
                            "panel_name": {
                                "type": "panel",
                                "size": [64, 64],
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
                                            "layer": 200,
                                            "size": [32, 32],
                                            "offset": [0, -5],
                                            "bindings": [
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
                                        "text": {
                                            "type": "label",
                                            "text": "#form_button_text",
                                            "layer": 32,
                                            "color": [0, 0, 0],
                                            "offset": [0, -8],
                                            "anchor_from": "bottom_middle",
                                            "bindings": [
                                                {
                                                    "binding_name": "#form_button_text",
                                                    "binding_type": "collection",
                                                    "binding_collection_name": "form_buttons"
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
                                "size": [64, 64],
                                "$button_text": "#null",
                                "$button_text_binding_type": "collection",
                                "$button_text_grid_collection_name": "form_buttons",
                                "$button_text_max_size": ["100%", 20],
                                "bindings": [
                                    {
                                        "binding_type": "collection_details",
                                        "binding_collection_name": "form_buttons"
                                    }
                                ]
                            }
                        }
                    ]
                }
            }
        ]
    }
}
```

## 5. JSON/JS literal — lado do script

`ui2/BP/scripts/main.js`
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
    .button("Skins", "textures/ui/icon_hangar");

world.afterEvents.itemUse.subscribe((event) => {
    const { source, itemStack } = event
    switch (itemStack.typeId) {
        case "minecraft:compass": ui.show(source); break;
        case "minecraft:clock": customUi.show(source); break;
    }
})
```

Observacoes:
- `.body("")` esta presente nos dois forms. O ramo custom **nao desenha `#form_text` em lugar nenhum** — o body e descartado silenciosamente. Se o body fosse usado, o texto sumiria sem aviso.
- Marcador = titulo literal `"Custom Form"`, sem codigo `§`. Isso vaza pro jogador: o titulo aparece na tela como esta.

`ui2/RP/manifest.json`
```json
{
    "format_version": 2,
    "header": {
        "name": "JSON UI Example #2",
        "description": "JSON UI Example",
        "uuid": "3d67c42e-2de7-4e75-9f4e-c1a400e5d107",
        "version": [0, 0, 1],
        "min_engine_version": [1, 20, 0]
    },
    "modules": [
        {
            "type": "resources",
            "uuid": "529d3fa5-015c-4a0d-b83f-b0f40c9768a0",
            "version": [1, 0, 0]
        }
    ]
}
```

---

## 6. Referencias vanilla citadas (para conferencia)

`vanilla/ui/server_form.json:36-45` — o `long_form` original que estamos substituindo:
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
Repare: ui2 **suprime `$title_max_size`** e muda `$title_size` de `"100% - 15px"` para `"100% - 14px"`. Sem `$title_max_size`, titulo longo nao e clampado.

`vanilla/ui/ui_template_dialogs.json:205` — o template que ambos os ramos herdam:
```json
  "main_panel_no_buttons": {
    "type": "panel",
    "anchor_from": "center",
    "anchor_to": "center",
    "$text_name|default": "",
    "$panel_indent_size|default": [ "100% - 16px", "100% - 31px" ],
    "$custom_background|default": "dialog_background_hollow_3",
    "controls": [
      { "common_panel@common.common_panel": { "$dialog_background": "$custom_background" } },
      { "title_label@common_dialogs.title_label": {} },
      {
        "panel_indent": {
          "type": "panel",
          "size": "$panel_indent_size",
          "offset": [ 0, 23 ],
          "anchor_from": "top_middle",
          "anchor_to": "top_middle",
          "controls": [ { "inside_header_panel@$child_control": {} } ]
        }
      }
    ]
  },
```
Duas coisas uteis pra nos: (a) existe `$custom_background` — da pra trocar a moldura do dialogo por `$custom_background` sem reescrever o template; (b) o conteudo entra em `panel_indent`, que tem `offset [0,23]` e altura `100% - 31px`, entao **o `$child_control` NUNCA ocupa a tela toda** — 31px vao pro titulo.

`vanilla/ui/server_form.json:212-227` — o `form_button` original, base do R9:
```json
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
            { "binding_type": "collection_details", "binding_collection_name": "form_buttons" }
          ]
        }
```

---

## 7. Aplicacao no SonheMenu

Estado atual do nosso pack (`ADDONS/SonheMenu_RP/ui/sonhe_forms.json` + `ui/sonhe_grid.json`).

### 7.1 O que ja estamos fazendo igual ou melhor

| Ponto | ui2 | SonheMenu | Veredito |
|---|---|---|---|
| Override so de `long_form` | sim | sim (`sonhe_forms.json`, comentario `"//"`) | empate |
| Par de view bindings no titulo | **tem buraco** (R3) | complementar de verdade: `((… - '§d§r§e§a§m§r') = #title_text)` vs `(not ((… - '§d§r§e§a§m§r') = #title_text))` | **nosso e melhor** |
| Marcador visivel pro jogador | `"Custom Form"` literal | `§d§r§e§a§m§r` (codigos de formatacao, invisiveis) | **nosso e melhor** |
| Contagem da colecao | `#form_button_length` (nao existe no vanilla) | `grid_dimensions` fixo, sem binding de contagem; fallback usa `#form_button_contents` | **nosso e melhor** |
| Item pixel fixo | `[80,80]` | `[96,96]` | empate (mesma regra) |
| Icone sem `texture` | sim | sim (`sonhe_forms.tile_icon`) | empate |
| `collection_details` no botao | sim | sim (`sonhe_forms.tile_button`) | empate |
| Corpo do form (`#form_text`) | **descartado** | desenhado em `sonhe_forms.screen_body` | **nosso e melhor** |
| Tema | nenhum | dark completo sem asset custom | **nosso e melhor** |

### 7.2 O que vale copiar do ui2

**(A) `resolve_sibling_scope` para esconder a moldura do icone.**
Hoje o nosso `tile_icon` se auto-oculta pelo view binding proprio, mas nao existe um wrapper que suma junto. Se um dia voltarmos a ter um contorno/placeholder atras do icone, o padrao correto e o do ui2 (R8): o **pai** olha o `#texture` do **filho** via `source_control_name` + `resolve_sibling_scope: true`. Isso e vanilla puro, existe em `vanilla/ui/server_form.json:158-166` e no nosso proprio fallback `sonhe_forms.row_icon_holder`.

**(B) `layer` alto no conteudo do tile.**
ui2 usa `layer: 200` no icone e `layer: 32` no label. Nosso `tile_icon` e `tile_label` estao em `"layer": 3`, e os estados do botao em `layer 1/4/5` (`face_default` 1, `face_hover` 4, `face_pressed` 5). **Isso significa que ao passar o mouse, `face_hover` (layer 4) fica ACIMA do icone (layer 3).** Se o hover parece "engolir" o icone, e exatamente isso. Correcao de 2 caracteres: subir `tile_icon` e `tile_label` para `"layer": 10`.
*Confidence: provavel* — a leitura dos layers e confirmada; o efeito visual e inferencia.

**(C) `$button_text: "#null"` continua sendo a forma canonica de ter botao mudo.**
Nosso `tile_button@common.button` nao usa `common_buttons.light_text_button`, entao nao precisa disso hoje. Mas se algum dia trocarmos para `light_text_button` (para ganhar as 4 texturas de estado prontas), o par obrigatorio e `$button_text: "#null"` + `$button_pressed_offset: [0,0]`.

**(D) `$custom_background` do `main_panel_no_buttons`.**
O ramo vanilla do nosso `sonhe_forms.json` herda `common_dialogs.main_panel_no_buttons` sem tocar em `$custom_background`. Se quisermos que **tambem o form vanilla** fique dark sem reescrever nada, basta passar `"$custom_background": "<outra_textura_de_dialogo>"` nesse no. Nao mexe em topologia, logo baixo risco.

### 7.3 O que NAO copiar

- **`#form_button_length`.** Nossos proprios testes (`SonheMenu_RP/docs/JSON_UI_NOTAS.md`, item 5) e a varredura do corpus (0 ocorrencias) apontam para `#form_button_contents`. Trocar seria regressao.
- **`stack_panel horizontal` de linha unica.** Nao quebra linha; com 5+ botoes o excedente sai da tela sem erro (R13). Nosso `grid` com `grid_dimensions [3,4]` resolve isso.
- **Comparacao por igualdade exata no marcador.** R3 — cria buraco onde as duas telas ficam invisiveis.
- **`long_form` como nome de um filho dentro do proprio def `long_form`.** ui2 chama os dois filhos de `long_form`:
  ```json
  "long_form": { "type": "panel", "controls": [
      { "long_form@common_dialogs.main_panel_no_buttons": { … } },
      { "long_form@common_dialogs.main_panel_no_buttons": { … } } ] }
  ```
  Dois irmaos com o **mesmo nome** dentro do mesmo `controls`, e ambos com o nome do def pai. Nossas notas registram isso como causa de quebra silenciosa. Nosso `sonhe_forms.json` usa `sonhe_vanilla_form` / `sonhe_custom_form` — nomes distintos. **Manter assim.**
  *Confidence: provavel* — o ui2 aparentemente funciona assim, entao nomes duplicados podem ser tolerados quando ha `@base` distinto; mas nao vale o risco.

### 7.4 Checklist de diagnostico derivado do ui2

Quando a tela custom sumir sem log, checar nesta ordem:

1. O par de view bindings e **complementar**? (R3)
2. O binding de dado `{ "binding_name": "#title_text" }` vem **antes** do view binding? (R4)
3. O `.json` foi salvo em **UTF-8 sem BOM**? (`§` vira `0xA7` solto com `Set-Content` do PowerShell — ja anotado em `JSON_UI_NOTAS.md`)
4. Algum binding usa `#form_button_length` em vez de `#form_button_contents`? (R5)
5. Pai `%c` com filho `%`/`fill` no mesmo eixo? (R6)
6. Alguma def foi redefinida sem `type` e sem `@base`, apagando a versao vanilla? (R2)
