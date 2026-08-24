---
name: mcpe-custom-server-form
description: Substitui a aparência dos formulários do @minecraft/server-ui (ActionFormData, ModalFormData, MessageFormData) por telas próprias em JSON UI, usando override do namespace server_form e marcador no título pra alternar entre tela custom e padrão. Use quando o pedido for "deixar o form do addon com skin própria", "menu em grid com ícones em vez de lista", "reskinar o ActionFormData", "sobrescrever server_form" ou similar.
---

# Reskin de formulários do @minecraft/server-ui (namespace `server_form`)

Não existe API de layout no `@minecraft/server-ui`. O BP só envia dados (título, corpo, lista de botões, texturas). Todo o visual vem do resource pack, do arquivo vanilla [`resource_pack/ui/server_form.json`](https://raw.githubusercontent.com/Mojang/bedrock-samples/main/resource_pack/ui/server_form.json) — que é o único arquivo do namespace `server_form` (confirmado em [`_ui_defs.json`](https://raw.githubusercontent.com/Mojang/bedrock-samples/main/resource_pack/ui/_ui_defs.json)). Reskinar = redeclarar controles desse namespace num arquivo próprio do RP.

Regra de ouro: **leia a árvore vanilla antes de escrever qualquer coisa.** Quase todo bug de form custom é um binding que não existe ou um controle inventado.

## 1. Estrutura mínima do RP

```
RP/
├── manifest.json
├── ui/
│   ├── _ui_defs.json
│   └── meu_forms.json      (namespace "server_form")
└── textures/ui/meu/...
```

```json
{ "ui_defs": [ "ui/meu_forms.json" ] }
```

Não é preciso (nem recomendado) copiar `ui/server_form.json` inteiro. O merge é por namespace: qualquer controle top-level que você declarar em `server_form` substitui o vanilla de mesmo nome; os que você não declarar continuam vanilla. Se você redeclarar `long_form_panel` e o fundo custom aparecer em jogo, isso já é prova de que o override do namespace está ativo.

Se o layout custom precisar de controles auxiliares, **prefira declará-los no mesmo arquivo**. Um `@outro_namespace.controle` definido num segundo arquivo do `_ui_defs` depende da ordem/resolução de `@extend` entre arquivos, o que não é documentado — se o controle filho não resolver, ele é descartado silenciosamente e você fica caçando um binding que estava certo. (Comportamento não confirmado em jogo; trate como risco, não como fato.)

## 2. Anatomia real do `server_form` vanilla

A cadeia completa, do screen ao botão:

```
third_party_server_screen@common.base_screen
  $screen_content = server_form.main_screen_content
    main_screen_content            (panel, size [0,0])
      server_form_factory          (type factory)
        long_form   -> @server_form.long_form     (ActionFormData)
        custom_form -> @server_form.custom_form   (ModalFormData)
```

```json
{
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
  }
}
```

Atenção ao `size: [0, 0]` do vanilla: qualquer filho com tamanho percentual dentro dele resolve para 0. Se a sua tela custom usa `["70%","75%"]` ancorada em `center`, você **precisa** redeclarar `main_screen_content` com `["100%","100%"]` — senão a tela é instanciada com área zero, indistinguível de "não apareceu".

`long_form` vanilla **não é um panel**: é um control derivado.

```json
{
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

  "long_form_panel": {
    "type": "stack_panel",
    "size": ["100%", "100%"],
    "orientation": "vertical",
    "layer": 1,
    "anchor_from": "top_left",
    "anchor_to": "top_left",
    "controls": [
      {
        "scrolling_panel@common.scrolling_panel": {
          "$show_background": false,
          "$scrolling_content": "server_form.long_form_scrolling_content",
          "$scroll_size": [ 5, "100% - 4px" ],
          "$scrolling_pane_size": [ "100% - 4px", "100% - 2px" ],
          "$scrolling_pane_offset": [ 2, 0 ],
          "$scroll_bar_right_padding_size": [ 0, 0 ]
        }
      }
    ]
  }
}
```

`long_form_scrolling_content` é um `stack_panel` com: `main_label` (`"text": "#form_text"`), um padding e `long_form_dynamic_buttons_panel`. Este último é **quem gera a lista de botões** — e é um `stack_panel` com `factory`, nunca um grid:

```json
{
  "long_form_dynamic_buttons_panel": {
    "type": "stack_panel",
    "size": ["100% - 4px", "100%c"],
    "offset": [2, 0],
    "orientation": "vertical",
    "factory": {
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
      { "binding_name": "#form_button_contents", "binding_name_override": "#collection_length" }
    ]
  }
}
```

Não existe control vanilla top-level chamado `form_button`. O control por-botão é `dynamic_button`; `form_button` é só o nome de um **filho** dele (`form_button@common_buttons.light_text_button`). O ícone é um `image` 32x32 dentro de `panel_name` (34 x `100%c`), irmão do botão:

```json
{
  "dynamic_button": {
    "type": "stack_panel",
    "size": ["100%", 32],
    "orientation": "horizontal",
    "controls": [
      {
        "panel_name": {
          "type": "panel",
          "size": [34, "100%c"],
          "controls": [
            {
              "image": {
                "type": "image",
                "layer": 2,
                "size": [32, 32],
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
            }
          ]
        }
      },
      {
        "form_button@common_buttons.light_text_button": {
          "$pressed_button_name": "button.form_button_click",
          "size": [ "fill", 32 ],
          "$button_text": "#form_button_text",
          "$button_text_binding_type": "collection",
          "$button_text_grid_collection_name": "form_buttons",
          "$button_text_max_size": [ "100%", 20 ],
          "bindings": [
            { "binding_type": "collection_details", "binding_collection_name": "form_buttons" }
          ]
        }
      }
    ]
  }
}
```

Dois detalhes que valem ouro nesse bloco:
- A ordem `[data binding..., view binding]`. O `view` lê `#texture`, o **nome sobrescrito**, não `#form_button_texture`. Bindings são avaliados na ordem do array.
- `button.form_button_click` só clica no índice certo por causa do `{"binding_type": "collection_details", "binding_collection_name": "form_buttons"}` **no próprio nó do botão**. Sem ele, o clique vai pro item errado ou pra nenhum.

`custom_form` (ModalFormData) é simétrico: `custom_form@common_dialogs.main_panel_no_buttons` com `$child_control: "server_form.custom_form_panel"` → `custom_form_scrolling_content` → `generated_contents` (factory `buttons`, `collection_name: "custom_form"`, contagem `#custom_form_length`) + `submit_button`. Se você só quer mexer no ActionFormData, **não toque** em `custom_form` — o modal continua vanilla e isso é o correto.

`MessageFormData` cai em outra tela (não em `long_form`); reskin de Action não afeta Message.

## 3. Bindings que o engine realmente expõe

Globais da tela: `#title_text`, `#form_text`, `#submit_text`, `#submit_button_visible`.

Collection `form_buttons`: `#form_button_text`, `#form_button_texture`, `#form_button_texture_file_system`, e a contagem `#form_button_contents`.

Collections do modal: `custom_form` (`#custom_form_length`), `custom_dropdown` (`#custom_dropdown_length`), e no branch preview `custom_multiselect` (`#custom_multiselect_length`).

**Não existem** `#form_button_length` nem `#maximum_grid_items` fornecidos pelo `server_form`. Grep de `#form_[a-z_]*` em todos os `ui/*.json` do vanilla retorna exatamente cinco nomes: `#form_button_contents`, `#form_button_text`, `#form_button_texture`, `#form_button_texture_file_system`, `#form_text`. `#maximum_grid_items` é propriedade genérica de controls `type: "grid"`, nunca um binding do form.

Binding com `binding_name` inexistente é **no-op silencioso**: nada de erro, o alvo simplesmente nunca é preenchido (fica 0 / vazio).

## 4. A técnica do marcador no título

Objetivo: o mesmo `long_form` serve duas telas — a sua, quando o título carrega um marcador; a vanilla, quando não. O marcador é um prefixo de códigos `§` (invisível no render) colocado pelo BP:

```javascript
// BP: scripts/menu.js
import { ActionFormData } from "@minecraft/server-ui";

export const MARCADOR = "§d§r§e§a§m§r"; // só códigos de formatação: não desenha nada

export function abrirMenu(player) {
    const form = new ActionFormData()
        .title(`${MARCADOR}§dMEU MENU§r`)
        .body("Escolha uma opção")
        .button("Loja", "textures/ui/meu/icone_loja")
        .button("Casa", "textures/ui/meu/icone_casa");
    return form.show(player);
}
```

No RP, `long_form` vira um `panel` com dois filhos mutuamente exclusivos. **Este é o padrão correto — o data binding de `#title_text` vem ANTES do view binding:**

```json
{
  "long_form": {
    "type": "panel",
    "size": ["100%", "100%"],
    "controls": [
      {
        "tela_custom@server_form.minha_tela": {
          "layer": 10,
          "bindings": [
            { "binding_name": "#title_text" },
            {
              "binding_type": "view",
              "source_property_name": "(not ((#title_text - '§d§r§e§a§m§r') = #title_text))",
              "target_property_name": "#visible"
            }
          ]
        }
      },
      {
        "tela_padrao@common_dialogs.main_panel_no_buttons": {
          "$title_panel": "common_dialogs.standard_title_label",
          "$title_size": [ "100% - 15px", 10 ],
          "$title_max_size": [ "100% - 15px", 10 ],
          "size": [225, 200],
          "$text_name": "#title_text",
          "$title_text_binding_type": "none",
          "$child_control": "server_form.long_form_panel",
          "layer": 2,
          "bindings": [
            { "binding_name": "#title_text" },
            {
              "binding_type": "view",
              "source_property_name": "((#title_text - '§d§r§e§a§m§r') = #title_text)",
              "target_property_name": "#visible"
            }
          ]
        }
      }
    ]
  }
}
```

### Por que o data binding é obrigatório

Um `binding_type: "view"` **não lê propriedades globais da tela**. Ele lê apenas o property bag do próprio controle (ou do controle apontado por `source_control_name`). `#title_text` é global: sem `{ "binding_name": "#title_text" }` importando o valor pro escopo local, a expressão avalia contra string vazia:

```
(not (('' - '§d§r§e§a§m§r') = ''))  ->  (not ('' = ''))  ->  (not true)  ->  FALSE
```

Resultado: a tela custom fica `visible: false` **sempre**, e a espelhada `((#title_text - MARC) = #title_text)` dá `TRUE` **sempre** — os dois ramos travados no estado errado, independentemente do que o BP mande. É o bug nº 1 dessa técnica.

A alternativa documentada é declarar o dado no pai e ler via `source_control_name` ([Bedrock Wiki — Modifying Server Forms](https://wiki.bedrock.dev/json-ui/modifying-server-forms)):

```json
{
  "meu_painel_pai": {
    "type": "panel",
    "bindings": [ { "binding_name": "#title_text" } ],
    "controls": [
      {
        "filho": {
          "type": "image",
          "$marcador": "§d§r§e§a§m§r",
          "bindings": [
            {
              "binding_type": "view",
              "source_control_name": "meu_painel_pai",
              "source_property_name": "(not ((#title_text - $marcador) = #title_text))",
              "target_property_name": "#visible"
            }
          ]
        }
      }
    ]
  }
}
```

### Ordem e parênteses

- **Ordem importa.** Data bindings sempre antes do view binding que os consome. Inverter mantém o bug.
- **Parentize a subtração antes da comparação:** `((X - 'sub') = X)`, nunca `(X - 'sub' = X)`. Todos os exemplos oficiais e todos os packs funcionais usam o par interno. Não existe documentação de precedência no parser de expressão do JSON UI, então escrever sem os parênteses é apostar em comportamento indefinido. Isso é convenção com 100% de aderência na prática, não regra provada — mas não há motivo pra desviar.
- Vários marcadores no mesmo control: `(#title_text - 'form_1' - 'form_2' - 'form_3')`.
- `'contém'` = `(not ((X - 'sub') = X))`; `'não contém'` = `((X - 'sub') = X)`.

### Sobre o `§` na expressão

`§` (U+00A7, bytes `C2 A7` em UTF-8) funciona dentro de `source_property_name` — a própria wiki usa `'§z'` como marcador invisível em expressão ([string-to-number](https://raw.githubusercontent.com/Bedrock-OSS/bedrock-wiki/a8f9908938d012a976ac9ee3b2b5b11095fd7570/docs/json-ui/string-to-number.md)). **Mas não há documentação afirmando se `#title_text` chega ao binding com os códigos `§` preservados ou normalizados** — o título renderizar colorido prova que os códigos chegam ao label, não que chegam iguais ao valor comparado pelo binding. Isso **precisa ser confirmado em jogo**. Se um marcador `§` falhar, teste o mesmo fluxo com marcador ASCII (`'meugrid:'`) pra isolar a variável, e escolha ASCII se a diferença aparecer.

### `binding_condition` num control que começa invisível

`always_when_visible` e `visible` só atualizam enquanto o control está visível — deadlock num control que começa invisível e depende do próprio binding pra aparecer. Se só adicionar o data binding não resolver, tente `"binding_condition": "always"` no data binding. Não há default documentado para `binding_condition`, e packs reais funcionam sem declará-lo; trate como tentativa de debug, não como parte do padrão.

## 5. Esconder o título e o marcador

Se a sua tela custom desenha o próprio cabeçalho, não instancie `$title_panel`/`standard_title_label` nela — o marcador só é invisível porque são códigos de formatação puros, mas o resto do título (`MEU MENU`) apareceria duplicado.

Pra desenhar o título dentro da tela custom, use um label com o data binding normal:

```json
{
  "titulo": {
    "type": "label",
    "size": ["100%", "default"],
    "text": "#title_text",
    "bindings": [ { "binding_name": "#title_text" } ]
  }
}
```

Pra remover o marcador do texto exibido, encadeie um view binding que subtrai o marcador (após o data binding):

```json
"bindings": [
  { "binding_name": "#title_text" },
  {
    "binding_type": "view",
    "source_property_name": "(#title_text - '§d§r§e§a§m§r')",
    "target_property_name": "#text"
  }
]
```

Alternativa mais simples e à prova de parser: manter o marcador só como gatilho e enviar o texto visível pelo `body` (`#form_text`), deixando o título custom hardcoded no JSON.

## 6. Grid de botões

Grid e factory são mecanismos **mutuamente exclusivos**:

| mecanismo | onde vive | como conta itens |
|---|---|---|
| `factory` | `stack_panel` / `collection_panel` | `#collection_length` |
| `type: "grid"` | control autônomo | `#maximum_grid_items` |

Varredura dos 208 `ui/*.json` do vanilla: 73 controls `type: "grid"`, **zero** com a chave `factory`. E `factory` usa `control_ids` (mapa), nunca `control_name`.

Padrão vanilla de grid dinâmico, de [`ui_common.json`](https://raw.githubusercontent.com/Mojang/bedrock-samples/main/resource_pack/ui/ui_common.json):

```json
{
  "container_grid": {
    "type": "grid",
    "grid_rescaling_type": "horizontal",
    "size": [ "100%", "default" ],
    "anchor_to": "top_left",
    "anchor_from": "top_left",
    "collection_name": "$item_collection_name",
    "grid_item_template": "$grid_item_template",
    "bindings": [
      {
        "binding_name": "#collection_total_items",
        "binding_name_override": "#maximum_grid_items",
        "binding_condition": "visible",
        "binding_type": "collection",
        "binding_collection_name": "$item_collection_name"
      }
    ]
  }
}
```

Regras que caem do vanilla:
- `grid_dimensions [cols, rows]` (malha estática) e `grid_rescaling_type` (colunas derivadas da largura do item) **nunca aparecem juntos** nos 73 grids vanilla. Escolha um.
- **Itens de grid têm tamanho absoluto em pixels.** `[18,18]` no recipe book, `32x32` nos containers. Item com largura em `%` do grid + `grid_rescaling_type: "horizontal"` é dependência circular (o grid mede pelo item, o item mede pelo grid) → tipicamente 0 colunas / tamanho 0.
- Grid dentro de `common.scrolling_panel`: o vanilla envolve o grid num panel intermediário de `["100%","100%c"]` e deixa o **grid** com `["100%","default"]`. Passar o grid direto como `$scrolling_content` com altura `100%c` e zero itens gerados resolve para altura 0.
- `grid_fill_direction` não existe no schema — é ignorada. Chave desconhecida não derruba o control (o vanilla convive com isso), mas suja o diagnóstico.

### O problema real: contar botões num grid

O `server_form` **não expõe um inteiro** com a quantidade de botões. `#form_button_contents` é o que o vanilla joga em `#collection_length` do factory — e o factory usa esse valor pra escolher o `control_id` por índice, o que indica um **array**, não um int, portanto provavelmente inadequado para `#maximum_grid_items`.

Opções, em ordem de risco:

1. **Grid com `maximum_grid_items` literal** — determinístico. Fixe o teto (ex.: 18) e esconda as células vazias com o view binding de `#form_button_text`:

```json
{
  "grade": {
    "type": "grid",
    "size": [ 156, "default" ],
    "grid_dimensions": [ 3, 6 ],
    "maximum_grid_items": 18,
    "grid_item_template": "server_form.tile_botao",
    "collection_name": "form_buttons"
  },

  "tile_botao": {
    "type": "panel",
    "size": [ 52, 44 ],
    "bindings": [
      {
        "binding_name": "#form_button_text",
        "binding_type": "collection",
        "binding_collection_name": "form_buttons"
      },
      {
        "binding_type": "view",
        "source_property_name": "(not (#form_button_text = ''))",
        "target_property_name": "#visible"
      }
    ],
    "controls": [
      {
        "icone": {
          "type": "image",
          "size": [ 24, 24 ],
          "offset": [ 0, -6 ],
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
            }
          ]
        }
      },
      {
        "rotulo": {
          "type": "label",
          "size": [ "100%", "default" ],
          "anchor_from": "bottom_middle",
          "anchor_to": "bottom_middle",
          "text": "#form_button_text",
          "bindings": [
            {
              "binding_name": "#form_button_text",
              "binding_type": "collection",
              "binding_collection_name": "form_buttons"
            }
          ]
        }
      },
      {
        "botao@common_buttons.light_text_button": {
          "size": [ "100%", "100%" ],
          "$pressed_button_name": "button.form_button_click",
          "$button_text": "",
          "$default_button_texture": "textures/ui/meu/tile_frame",
          "$hover_button_texture": "textures/ui/meu/tile_frame_hover",
          "$pressed_button_texture": "textures/ui/meu/tile_frame_pressed",
          "$locked_button_texture": "textures/ui/meu/tile_frame",
          "$border_visible": false,
          "$default_state_border_visible": false,
          "$hover_state_border_visible": false,
          "$pressed_state_border_visible": false,
          "$locked_state_border_visible": false,
          "bindings": [
            { "binding_type": "collection_details", "binding_collection_name": "form_buttons" }
          ]
        }
      }
    ]
  }
}
```

Nota: "células invisíveis continuam ocupando espaço físico no grid" — logo um teto alto deixa buracos no fim, não some com eles. Escolha o teto perto do número real de botões.

2. **Tentar `{ "binding_name": "#form_button_contents", "binding_name_override": "#maximum_grid_items" }`.** Essa combinação é **inferência**, não confirmada em nenhum vanilla ou pack de terceiros — teste em jogo antes de confiar. Se falhar, volte ao literal.

3. **Abandonar o grid** e usar o mecanismo vanilla: `stack_panel` + `factory` + `#form_button_contents -> #collection_length`, trocando só o `control_ids.button` pelo seu tile. É o caminho que provadamente funciona; o custo é que você fica com lista vertical, sem linhas de N colunas. Um pack real publicado que faz override de `server_form` usa exatamente `stack_panel` com índices fixos, não grid ([skyls ui4](https://skyls.de/samples/ui4/RP/ui/server_form.json)).

## 7. Reskinar o botão de verdade

`common.button` (em `ui_common.json`) é só o esqueleto de input/focus/som — **não tem imagem nenhuma**. A imagem vem de `$button_image` → `texture: "$new_ui_button_texture"`, e cada state panel de `light_text_button` seta `$new_ui_button_texture` a partir de `$default_button_texture` / `$hover_button_texture` / `$pressed_button_texture` / `$locked_button_texture` (defaults em `light_button_assets`, [`ui_template_buttons.json`](https://raw.githubusercontent.com/Mojang/bedrock-samples/main/resource_pack/ui/ui_template_buttons.json)).

`$variáveis` **propagam** do ancestral pro descendente, então definir `$default_button_texture` num panel pai até funciona. Mas o padrão canônico da Mojang passa as **quatro** texturas **no próprio nó `@`** que estende `light_text_button` / `light_content_button`:

```json
{
  "transparent_content_button@common_buttons.light_content_button": {
    "$default_button_texture": "textures/ui/imagetaggedcorner",
    "$hover_button_texture": "textures/ui/imagetaggedcorner",
    "$pressed_button_texture": "textures/ui/imagetaggedcorner",
    "$locked_button_texture": "textures/ui/imagetaggedcorner",
    "$border_visible": false,
    "$default_state_border_visible": false,
    "$hover_state_border_visible": false,
    "$pressed_state_border_visible": false,
    "$locked_state_border_visible": false
  }
}
```

Dois motivos pra fazer assim:
- Esquecer `$locked_button_texture` deixa o estado `locked` com `textures/ui/disabledButtonNoBorder` vanilla.
- **O highlight claro/verde do hover não vem só da textura.** Vem também de um `image` `border@common_buttons.focus_border` (`textures/ui/focus_border_white`) tingido por `$border_color` (`$light_border_hover_color = [1,1,1]`, de `_global_variables.json`). Trocar as texturas **não** apaga essa borda — é preciso `$border_visible: false` e os quatro `$*_state_border_visible: false`.

Se quiser controle total do fundo, passe também `"$button_image": "server_form.meu_image"` com um `image` próprio (nineslice/uv custom).

## 8. Texturas de UI (nineslice)

- A chave correta no schema Sprite é **`nineslice_size`** — sem underscore entre `nine` e `slice`. `nine_slice_size` **não existe** e é ignorada silenciosamente. Erro de digitação clássico e invisível.
- O vanilla **nunca** declara nineslice no UI JSON. Ele usa o arquivo `.json` irmão do PNG: `textures/ui/meu/tile_frame.json` = `{ "nineslice_size": 4, "base_size": [16, 16] }`. Esse é o caminho comprovado — use ele, e crie um `.json` pra **cada** textura de frame (é comum criar pra uma e esquecer a outra, o que faz uma fatiar e a outra esticar).
- `base_size` = dimensões reais do PNG, em pixels. `nineslice_size` na mesma unidade. Se a borda (`nineslice_size * 2`) exceder o tamanho de destino na tela, o render distorce — por isso os frames vanilla são de 4 a 16 px, não de 1254.
- PNG **RGB sem canal alpha** (colortype 2) carrega, mas fica 100% opaco: cantos arredondados e transparência ficam impossíveis. Todo o vanilla de UI é RGBA (colortype 6). Exporte PNG-32.
- Precedência entre o `nineslice_size` do `.json` irmão e a chave no control `image` **não está documentada em nenhuma fonte oficial** — precisa de teste em jogo. Até lá, use só o `.json` irmão.

## 9. Caso trabalhado: o SONHE Menu

BP envia `new ActionFormData().title("§d§r§e§a§m§r§dSONHE§r")`. RP sobrescreve `server_form` pra mostrar um grid de ícones quando o título contém o marcador.

Sintoma em jogo: o form abre com o **ramo padrão** — painel 225x200, título rosa, corpo, botões em lista vertical com ícone 32px e highlight verde vanilla. O grid nunca aparece, nem vazio. O fundo do painel tem a textura roxa custom.

Diagnóstico e o que estava errado:

1. **Bug principal (bloqueia tudo).** Os dois filhos de `long_form` tinham array `bindings` com **apenas** o `binding_type: "view"`, sem `{ "binding_name": "#title_text" }` antes e sem `source_control_name`. `#title_text` resolvia vazio nos dois escopos: grid travado em `false`, ramo padrão travado em `true`. Isso reproduz o screenshot inteiro, os dois lados de uma vez. Ironia: o mesmo pack usava o data binding **corretamente** num label de título dentro da tela custom — o padrão era conhecido e foi esquecido justamente onde importava.

2. **Parênteses.** As expressões eram `(not (#title_text - '§d§r§e§a§m§r' = #title_text))` e `(#title_text - '§d§r§e§a§m§r' = #title_text)`, sem o par interno. Corrigir junto com o item 1, mesmo que provavelmente não seja a causa isolada.

3. **`factory` dentro de `type: "grid"`.** O `grid_content` declarava `grid_item_template` **e** um bloco `factory` — com a chave `control_name`, que não existe (o vanilla usa `control_ids`). Remover o `factory` inteiro.

4. **`#form_button_length`.** O binding de contagem era `{ "binding_name": "#form_button_length", "binding_name_override": "#maximum_grid_items" }`. Esse binding não existe no Bedrock: no-op, `#maximum_grid_items` fica 0, grid com zero células. Mesmo depois de corrigir a visibilidade, o grid apareceria vazio.

5. **`grid_dimensions [3,6]` + `grid_rescaling_type: "horizontal"` juntos**, e item de grid com `size: ["33%", "60%x"]` (percentual do grid) — dependência circular, tiles de área zero.

6. **Grid direto como `$scrolling_content`** com `["100%","100%c"]`, sem o panel intermediário `100%c` do padrão vanilla.

7. **Cosméticos:** `nine_slice_size` (chave inválida) nos dois arquivos; `panel_frame.json` inexistente enquanto `tile_frame.json` existia (uma textura fatia, a outra estica); os dois PNGs 1254x1254 colortype 2, sem alpha, renderizando como retângulo opaco; `nineslice_size: 100` numa textura desenhada em tile de ~44px; texturas de botão no panel pai sem `$locked_button_texture` nem desligar as bordas de foco.

Caminhos falsos descartados na auditoria — não perca tempo com eles antes de checar o item 1:
- "Reinstalar / limpar cache do RP": o pack no cache do cliente era **byte-idêntico** ao do repo, inclusive os bytes `C2 A7`.
- "Outro pack sobrescrevendo `server_form`": varredura de 44 packs, nenhum outro declarava o namespace.
- "Ordem dos resource packs": o fundo roxo custom já provava que o override venceu o vanilla.
- "JSON malformado": os três arquivos passavam no parser, sem BOM, sem chave duplicada.

Duas hipóteses de **ambiente** que sobreviveram e valem sempre checar em setup servidor+cliente:
- **Dessincronia de marcador entre BP e RP.** O BP roda no servidor, o RP no cliente. Renomear o marcador ("§s§o§n§h§e§r" → "§d§r§e§a§m§r") e reimplantar só um dos lados produz **exatamente o mesmo sintoma visual**, sem nenhum bug de JSON. Sempre suba BP e RP juntos, e prefira aceitar os dois marcadores durante a transição: `(not ((#title_text - 'MARC_NOVO' - 'MARC_ANTIGO') = #title_text))`.
- **Duas versões do mesmo pack no `packcache` do cliente** (mesmo UUID, versions diferentes, marcadores diferentes). Se o servidor ainda anuncia a version antiga, o cliente monta a árvore antiga.

## 10. Erros comuns (sintoma → causa)

| Sintoma em jogo | Causa provável |
|---|---|
| Tela custom nunca aparece e a padrão aparece sempre | Falta `{ "binding_name": "#title_text" }` antes do view binding, nos dois filhos de `long_form` |
| Tela custom aparece sobreposta à padrão, sempre | View binding descartado (expressão inválida) → `#visible` cai no default `true`. Revise a expressão/parênteses |
| Tela custom instanciada mas com área zero | `main_screen_content` ainda com `size: [0,0]` do vanilla e filho com tamanho percentual |
| Tela custom aparece (fundo + título) mas sem nenhum tile | Contagem do grid é 0: `binding_name` inexistente, ou `factory` dentro de `type: "grid"`, ou item com tamanho percentual |
| Tiles existem mas com tamanho/coluna errados | `grid_dimensions` + `grid_rescaling_type` juntos, ou item de grid sem tamanho em pixels |
| Área rolável com altura zero | Grid passado direto como `$scrolling_content` com `100%c` e zero itens; falta o panel intermediário `["100%","100%c"]` |
| Clique abre o item errado (ou nenhum) | Falta `{ "binding_type": "collection_details", "binding_collection_name": "form_buttons" }` no nó do botão |
| Ícone do botão não aparece | Falta o par `#form_button_texture` + `#form_button_texture_file_system` com `binding_type: "collection"`, ou o view binding de `#visible` vem antes deles |
| Botão continua com cara vanilla / borda clara no hover | Só as texturas foram trocadas; falta `$locked_button_texture` e desligar `$border_visible` + os quatro `$*_state_border_visible` |
| Frame esticado, cantos não preservados | `nine_slice_size` (chave inválida) em vez de `nineslice_size`, ou falta o `.json` irmão do PNG |
| Frame opaco, sem transparência nos cantos | PNG exportado como RGB (colortype 2) em vez de RGBA |
| Título duplicado na tela custom | A tela custom instancia `$title_panel` e também desenha o próprio label de título |
| Grid funciona com título ASCII mas não com marcador `§` | Suspeite de normalização de `#title_text` (não documentada) ou de encoding no pack instalado. Compare os bytes `C2 A7` nos dois lados |
| Modal (`ModalFormData`) quebrou junto | Você sobrescreveu `custom_form` / `custom_form_panel` sem querer |

## 11. Checklist de debug em jogo

Ative **Content Log** e **Content Log GUI** em Configurações > Criador antes de qualquer coisa: controle rejeitado no parse e `@extend` que não resolveu aparecem lá.

Ordem dos testes — cada um isola uma variável:

1. **O override está ativo?** Redeclare `long_form_panel` com um fundo óbvio (cor sólida). Se o painel padrão muda de aparência, o namespace `server_form` está sendo sobrescrito e o RP está carregado. Isso descarta "reinstalar pack", "ordem dos packs" e "outro pack conflitando".
2. **O seu `long_form` está sendo instanciado?** Ponha um `label` com texto **literal** (`"DEBUG_LONG_FORM"`, sem binding) como primeiro filho de `long_form`. Se aparecer, o override do control venceu. Se não, o problema é de árvore/resolução de `@extend`, e nenhum ajuste de binding vai ajudar.
3. **É problema de expressão ou de instanciação?** Troque temporariamente o binding da tela custom por `"visible": true` fixo, sem binding nenhum. Se a tela custom aparecer, a árvore está OK e o defeito é 100% escopo/expressão. Se não aparecer, é dimensional ou de instanciação.
4. **`#title_text` chega ao escopo?** Dois labels dentro de `long_form`: um com `text: "#title_text"` **e** `bindings: [{ "binding_name": "#title_text" }]`, outro com o mesmo `text` e **sem** o data binding. O primeiro mostra o título, o segundo fica vazio — é essa a diferença que quebra o view binding.
5. **Marcador ASCII.** Troque o marcador por `'meugrid:'` nos **dois** lados (BP e RP) e reimplante junto. Isola encoding e normalização de `§`.
6. **O que o servidor está mandando?** No BP, logue o título antes do `show`: `world.sendMessage(JSON.stringify(titulo))`. Confirma se o marcador que chega é o que o RP procura — pega dessincronia BP/RP na hora.
7. **Cache do cliente.** Apague o diretório `packcache` do cliente, reentre e confirme que só **um** diretório do seu pack é recriado, com a version esperada. Duas versions em cache com marcadores diferentes dão o mesmo sintoma de bug de código.
8. **Só depois** que a tela custom estiver visível, ataque o grid: remova `factory`, troque a contagem por `maximum_grid_items` literal, dê tamanho em pixels ao item. Enquanto a tela não aparece, todos os defeitos do grid são indistinguíveis entre si.
9. **Confirme o tamanho do painel visível.** ~225x200 é o `long_form` padrão; a sua tela custom tem outro tamanho. Isso distingue "tela custom oculta" de "tela custom visível porém vazia" — dois bugs completamente diferentes.
10. **Confirme que o form testado é o certo.** `MessageFormData` e `ModalFormData` sem marcador caem no ramo padrão **por design**. Reproduza só com o `ActionFormData` que carrega o marcador.

## 12. Fontes

- Vanilla: [`ui/server_form.json`](https://raw.githubusercontent.com/Mojang/bedrock-samples/main/resource_pack/ui/server_form.json) (main) e [branch preview](https://raw.githubusercontent.com/Mojang/bedrock-samples/preview/resource_pack/ui/server_form.json) (adiciona `custom_multiselect`)
- Vanilla: [`ui_common.json`](https://raw.githubusercontent.com/Mojang/bedrock-samples/main/resource_pack/ui/ui_common.json), [`ui_template_buttons.json`](https://raw.githubusercontent.com/Mojang/bedrock-samples/main/resource_pack/ui/ui_template_buttons.json), [`inventory_screen.json`](https://raw.githubusercontent.com/Mojang/bedrock-samples/main/resource_pack/ui/inventory_screen.json), [`chest_screen.json`](https://raw.githubusercontent.com/Mojang/bedrock-samples/main/resource_pack/ui/chest_screen.json), [`_global_variables.json`](https://raw.githubusercontent.com/Mojang/bedrock-samples/main/resource_pack/ui/_global_variables.json)
- [Bedrock Wiki — Modifying Server Forms](https://wiki.bedrock.dev/json-ui/modifying-server-forms)
- [Bedrock Wiki — Dynamic Content Generation](https://wiki.bedrock.dev/json-ui/dynamic-content-generation)
- [Bedrock Wiki — JSON UI Documentation](https://wiki.bedrock.dev/json-ui/json-ui-documentation) (tabelas Sprite e Data Binding Array Object)
- [Bedrock Wiki — JSON UI Intro](https://wiki.bedrock.dev/json-ui/json-ui-intro) (operadores, conditional rendering)
- [Bedrock Wiki — Preserve Title Texts](https://wiki.bedrock.dev/json-ui/preserve-title-texts) (`visibility_changed`, subtração de string)
- [skyls.de — JSON UI #4: Advanced Layout](https://skyls.de/samples/ui4/RP/ui/server_form.json) (pack publicado e funcional com `long_form` + dois ramos por marcador)
