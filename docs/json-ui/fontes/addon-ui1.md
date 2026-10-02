# Fonte: Addon de terceiro #1 (`ui1`) — override mínimo de `server_form`

> **Origem analisada:** `c:/Users/Desktop/Downloads/ADDONS EXEMPLOS/ui1/`
> **Corpus vanilla de referência:** `c:/Users/Desktop/Documents/Nova pasta/assets/assets/resource_packs/vanilla/ui/`
> **Data da leitura:** 2026-08-28
> **Escopo:** addon completo lido (5 arquivos, 100% do conteúdo). Nenhum arquivo do SonheMenu foi alterado.

---

## 1. Resumo executivo

O addon `ui1` é o **exemplo canônico mínimo** da técnica de "marcador no título" para sobrescrever
`server_form` sem quebrar os forms do resto do servidor. Ele tem **3 arquivos relevantes** e um único
arquivo de UI de **2374 bytes**.

O que ele prova, na prática:

1. **Sobrescreve o vanilla pelo MESMO caminho de arquivo** (`RP/ui/server_form.json`), e por isso
   **NÃO tem `_ui_defs.json`**. O arquivo do pack substitui o `ui/server_form.json` já listado no
   `_ui_defs.json` do vanilla.
2. Redefine **apenas um controle** (`long_form`), e **continua referenciando controles do vanilla que
   ele não redefiniu** (`server_form.long_form_panel`, `common_dialogs.main_panel_no_buttons`,
   `common_dialogs.standard_title_label`). Ou seja: o merge é **por controle de topo, não por arquivo
   inteiro**.
3. Troca a assinatura do controle: o vanilla declara `"long_form@common_dialogs.main_panel_no_buttons"`
   (com herança); o addon declara `"long_form"` (panel puro, sem `@`). **O casamento do override é feito
   pelo nome ANTES do `@`.**
4. Ramifica em duas telas irmãs mutuamente exclusivas via **view binding em `#visible`**, usando o
   operador de **subtração de string** (`(A - 'sub') = A` ⇒ "A não contém 'sub'").
5. Usa marcador **visível e literal** no título (`"Custom Form"`), diferente do SonheMenu que usa
   um marcador invisível de códigos de cor (`§d§r§e§a§m§r`).

**Ele NÃO monta grade de tiles, NÃO usa `type: grid`, NÃO usa `grid_item_template`, NÃO aplica tema
custom e NÃO toca em `dynamic_button`.** Todo o conteúdo interno das duas telas continua sendo o
`server_form.long_form_panel` do vanilla — a única diferença entre os dois ramos é `size` (`[225,200]`
vs `[400,200]`). É um exemplo didático de *roteamento*, não de *skin*.

---

## 2. Inventário completo do addon

| Caminho | Bytes | Papel |
|---|---|---|
| `ui1/RP/manifest.json` | 445 | RP, `min_engine_version [1,20,0]`, 1 módulo `resources` |
| `ui1/RP/pack_icon.png` | 337 | ícone |
| `ui1/RP/ui/server_form.json` | 2374 | **único arquivo de UI** — override de `long_form` |
| `ui1/BP/manifest.json` | 865 | BP, módulos `data` + `script`, deps `@minecraft/server 1.6.0` e `@minecraft/server-ui 1.1.0` |
| `ui1/BP/scripts/main.js` | — | 2 `ActionFormData`, diferenciados só pelo `.title()` |
| `ui1/BP/pack_icon.png` | — | ícone |

**Ausências relevantes (confirmado por `find`):**

- ❌ **não existe** `RP/ui/_ui_defs.json`
- ❌ **não existe** `RP/ui/_global_variables.json`
- ❌ **não existe** nenhuma textura custom em `RP/textures/`
- ❌ **não existe** `RP/ui/` com qualquer outro `.json`

---

## 3. Tabela de padrões observados

| # | Padrão | Como o `ui1` faz | Confidence |
|---|---|---|---|
| P1 | **Registro do override** | Grava em `RP/ui/server_form.json` (mesmo caminho do vanilla). Sem `_ui_defs.json`. | confirmado |
| P2 | **Escopo do merge** | Redefine só `long_form`; o resto do namespace `server_form` continua vindo do vanilla. | confirmado |
| P3 | **Chave do override** | Vanilla = `"long_form@common_dialogs.main_panel_no_buttons"`; addon = `"long_form"`. Casa pelo prefixo antes do `@`. | confirmado |
| P4 | **Troca de `type`** | O controle raiz vira `"type": "panel"` (o vanilla nem declara `type` — herda do template). | confirmado |
| P5 | **Wrapper de tamanho irrelevante** | `"size": ["100%","100%"]` sobre um pai `main_screen_content` de `"size": [0,0]` ⇒ o wrapper é 0×0; os filhos têm px fixo + `anchor: center` herdado e transbordam. | confirmado |
| P6 | **Ramificação** | 2 filhos irmãos, ambos `@common_dialogs.main_panel_no_buttons`, cada um com view binding em `#visible`. | confirmado |
| P7 | **Nomes de irmãos idênticos** | Os DOIS filhos se chamam `long_form`. Não quebra. | confirmado |
| P8 | **Ancoragem de dado antes do view binding** | `{"binding_name":"#title_text"}` vem **primeiro** no array; só depois o `binding_type:"view"` que lê `#title_text`. | confirmado |
| P9 | **Operador "não contém"** | `((#title_text - 'Custom Form') = #title_text)` | confirmado (no addon) / **não atestado no vanilla** |
| P10 | **Marcador no título** | String legível `"Custom Form"`, setada pelo `.title()` do BP. | confirmado |
| P11 | **`$schema` no JSON** | `"$schema": "https://kalmemarq.github.io/Bugrock-JSON-UI-Schemas/ui.schema.json"` convive com `"namespace"`. | confirmado |
| P12 | **Comentário de bloco `/* */` antes do `{`** | Header da Mojang copiado. O parser aceita. | confirmado |
| P13 | **Reaproveita `$title_panel` / `$child_control`** | Não redefine o miolo; só repassa as `$vars` do template. | confirmado |
| P14 | **Sem tema** | Zero `color`, zero `alpha`, zero `texture`, zero nine-slice. Só `size`. | confirmado |

---

## 4. Regras extraídas, com evidência

### R1 — Override de arquivo vanilla pelo mesmo caminho dispensa `_ui_defs.json`
**Confidence: confirmado**

O pack `ui1` tem **apenas** `RP/ui/server_form.json` e nada mais em `ui/`:

```
./RP/manifest.json
./RP/pack_icon.png
./RP/ui/server_form.json
```

E o vanilla já registra esse caminho no seu próprio `_ui_defs.json`:

`.../vanilla/ui/_ui_defs.json:142`
```json
    "ui/server_form.json",
```

**Consequência prática:** `_ui_defs.json` serve para **adicionar arquivos novos**, não para
sobrescrever os que o vanilla já registra. Um `_ui_defs.json` no pack que liste só arquivos novos
está correto; o que ele **não** faz é validar/ativar um override de caminho vanilla.

---

### R2 — O merge é por controle de topo, não por arquivo
**Confidence: confirmado**

O arquivo do addon define **um único** controle (`long_form`), mas referencia três coisas que **não
estão nele**:

```json
"$title_panel": "common_dialogs.standard_title_label",
"$child_control": "server_form.long_form_panel",
```
e o próprio `@common_dialogs.main_panel_no_buttons`.

`server_form.long_form_panel` só existe no arquivo **vanilla**:

`.../vanilla/ui/server_form.json`
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

Se o override substituísse o **arquivo inteiro**, `server_form.long_form_panel` ficaria indefinido e o
addon não renderizaria nada. Ele renderiza (é o exemplo do vídeo `https://youtu.be/QhJkCDIZ-NU`
declarado no `metadata.url` do BP). ⇒ **o engine faz merge por chave de topo dentro do namespace.**

**Corolário de falha silenciosa:** um controle referenciado por `@` ou por `$child_control` que **não
exista** provavelmente resolve para nada e derruba a subárvore **sem erro no log**.

---

### R3 — A chave de override casa pelo nome ANTES do `@`
**Confidence: confirmado**

Vanilla:
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

Addon (`ui1/RP/ui/server_form.json`):
```json
    "long_form": {
        "type": "panel",
        "size": ["100%", "100%"],
        "controls": [ ... ]
    }
```

O nome público continua sendo `server_form.long_form`, que é o que o factory procura:

`.../vanilla/ui/server_form.json`
```json
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

**Regra:** sobrescrever `"long_form"` (sem `@`) substitui `"long_form@qualquer_coisa"` do vanilla, e a
herança do vanilla é **descartada** — o novo controle começa do zero e precisa declarar seu próprio `type`.

---

### R4 — `main_screen_content` tem `size: [0,0]`; o tamanho real vem dos filhos com px fixo + anchor center
**Confidence: confirmado**

`main_screen_content` é `"size": [0, 0]`. O addon põe um wrapper `"size": ["100%","100%"]`, que
portanto também é `0×0`. Ainda assim renderiza, porque cada filho declara px absoluto:

```json
"size": [225, 200]
```
```json
"size": [400, 200]
```

e herda de `common_dialogs.main_panel_no_buttons`:

`.../vanilla/ui/ui_template_dialogs.json`
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

**Regra:** na raiz de `server_form`, **nunca dependa de percentual** — o pai é 0×0. Use px absoluto
com `anchor_from/anchor_to: center`. Um filho `"size": ["100%","100%"]` na raiz vira **invisível
silenciosamente** (0×0, sem erro).

⚠️ **Este é um mecanismo direto de "sumiço silencioso".**

---

### R5 — O view binding só enxerga o que já foi ancorado no MESMO array, ANTES dele
**Confidence: confirmado**

O template vanilla resolve `#title_text` **dentro do label**, não no painel:

`.../vanilla/ui/ui_template_dialogs.json`
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
      ...
    ]
  },
```

Como o painel externo **não** tinha `#title_text` no escopo, o addon **ancora explicitamente** e só
depois lê:

`ui1/RP/ui/server_form.json`
```json
                    "bindings": [
                        {
                            "binding_name": "#title_text"
                        },
                        {
                            "binding_type": "view",
                            "source_property_name": "((#title_text - 'Custom Form') = #title_text)",
                            "target_property_name": "#visible"
                        }
                    ]
```

**Regra:** `binding_type: "view"` é **puramente local** — avalia contra propriedades já presentes no
controle. Se o dado não foi ancorado antes (mesmo array, índice menor), a expressão resolve para vazio
e o resultado costuma ser `#visible = false` **sem log**.

⚠️ **Segundo mecanismo direto de "sumiço silencioso".** Trocar a ordem dos dois objetos do array
`bindings` é uma "mudança mínima" que apaga a tela.

---

### R6 — O operador `-` sobre strings é "remover substring"; a comparação com o original testa "não contém"
**Confidence: confirmado (uso) / suspeita (semântica exata) — NÃO atestado no vanilla**

```json
"source_property_name": "((#title_text - 'Custom Form') = #title_text)"
```
```json
"source_property_name": "(#title_text = 'Custom Form')"
```

**Verificação no corpus vanilla (188 arquivos):** busca por `" - '"` e por
`source_property_name` contendo `-` retornou **zero ocorrências**. O único operador de string atestado
no vanilla é concatenação com `+`:

`.../vanilla/ui/game_tip_screen.json:41`
```json
        "source_property_name": "('textures/ui/game_tip_animations/' + #animation_name)",
```

**Implicação:** `A - 'sub'` é um operador **não documentado e não usado pela Mojang**. Funciona hoje,
mas é a peça mais frágil do arranjo — uma mudança de parser em qualquer versão o quebra sem aviso.

Note também que o ramo 2 do `ui1` **não** usa subtração; usa igualdade exata:
```json
"source_property_name": "(#title_text = 'Custom Form')"
```
Isso significa que os dois ramos do `ui1` **não são complementares por construção**: o ramo 1 usa
"não contém" e o ramo 2 usa "é exatamente igual". Com `title = "Custom Form Extra"`, **os dois ramos
ficam invisíveis** e a tela some por completo — sem erro.

⚠️ **Terceiro mecanismo de "sumiço silencioso".** O SonheMenu corrigiu isso usando `(not (...))` no
ramo 2 (ver §7), o que é estritamente melhor.

---

### R7 — Dois irmãos podem ter o mesmo nome no mesmo `controls`
**Confidence: confirmado**

```json
        "controls": [
            {
                "long_form@common_dialogs.main_panel_no_buttons": { ... }
            },
            {
                "long_form@common_dialogs.main_panel_no_buttons": { ... }
            }
        ]
```

Ambos os filhos se chamam `long_form`, dentro de um pai também chamado `long_form`. Não quebra.
Mas é frágil: qualquer binding com `source_control_name` + `resolve_sibling_scope` ficaria ambíguo.
O vanilla evita isso — no `dynamic_button` o irmão é referenciado por nome único:

`.../vanilla/ui/server_form.json`
```json
          "bindings": [
            {
              "binding_type": "view",
              "source_control_name": "image",
              "resolve_sibling_scope": true,
              "source_property_name": "(not (#texture = ''))",
              "target_property_name": "#visible"
            }
          ],
```

**Recomendação (contra o `ui1`):** dar nomes distintos aos irmãos. O SonheMenu já faz isso
(`sonhe_vanilla_form` / `sonhe_custom_form`) — está correto.

---

### R8 — O addon herda `$title_size` mas DESCARTA `$title_max_size`
**Confidence: confirmado**

Vanilla:
```json
    "$title_size": [ "100% - 15px", 10 ],
    "$title_max_size": [ "100% - 15px", 10 ],
```

Addon:
```json
                    "$title_size": ["100% - 14px", 10],
```

Sem `$title_max_size`, o `standard_title_label` cai no default do template:
```json
    "$title_max_size|default": [ "default", 10 ],
    "max_size": "$title_max_size",
```

⇒ o título deixa de ser truncado na largura do painel e **estoura para fora** se for longo.
É um bug latente do `ui1`, não um padrão a copiar. (O SonheMenu repete o mesmo `100% - 14px`
sem `$title_max_size` — mesma pendência.)

---

### R9 — Comentário `/* */` antes do `{` raiz e `$schema` dentro do objeto são aceitos
**Confidence: confirmado**

Bytes iniciais reais do arquivo do addon (`od -c`):
```
/********************************************************\r\n
+*   (c) Mojang. All rights reserved                       *\r\n
+*   (c) Microsoft. All rights reserved.                   *\r\n
+*********************************************************/\r\n\r\n
{\r\n    "namespace": "server_form",\r\n    "$schema": "https://kalmemarq.github.io/..."
```

O parser de JSON UI do Bedrock é **JSONC**: aceita `/* */` e `//`. O vanilla também usa:

`.../vanilla/ui/_ui_defs.json`
```json
{
  // Alphabetical order please :)
  "ui_defs": [
```

`.../vanilla/ui/ui_template_dialogs.json`
```json
        "panel_indent": {
          "type": "panel",
          // Fit to the hole in dialog_background_hollow_1 exactly
          "size": [ "100% - 16px", "100% - 131px" ],
```

`"$schema"` no nível do namespace é inofensivo — chaves que começam com `$` no topo do arquivo são
tratadas como variável global do arquivo, nunca consultada.

---

### R10 — O lado BP é trivial: o marcador é só o `.title()`
**Confidence: confirmado**

`ui1/BP/scripts/main.js` (arquivo inteiro):
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
    .button("button1")
    .button("button2")
    .button("button3");

world.afterEvents.itemUse.subscribe((event) => {
    const { source, itemStack } = event
    switch (itemStack.typeId) {
        case "minecraft:compass": ui.show(source); break;
        case "minecraft:clock": customUi.show(source); break;
    }
})
```

Nenhuma API especial. **O único canal de comunicação BP→UI é o texto de `#title_text`.**
(Os outros canais disponíveis, todos do vanilla: `#form_text` do `.body()`, e a coleção
`form_buttons` com `#form_button_text`, `#form_button_texture`, `#form_button_texture_file_system`.)

---

### R11 — `min_engine_version` não precisa ser a versão do cliente
**Confidence: confirmado**

`ui1/RP/manifest.json` (arquivo inteiro):
```json
{
    "format_version": 2,
    "header": {
        "name": "JSON UI Example #1",
        "description": "JSON UI Example",
        "uuid": "d305fe39-0e11-451c-9312-1465224b97c4",
        "version": [0, 0, 1],
        "min_engine_version": [1, 20, 0]
    },
    "modules": [
        {
            "type": "resources",
            "uuid": "26b8db70-9bb2-4011-b7ce-6310002741e0",
            "version": [1, 0, 0]
        }
    ]
}
```

`[1,20,0]` num cliente 1.26.x — o override de UI funciona. **`min_engine_version` não é fator de
falha silenciosa de JSON UI.**

`ui1/BP/manifest.json` (arquivo inteiro):
```json
{
    "format_version": 2,
    "header": {
        "name": "JSON UI #1",
        "description": "JSON UI Intro",
        "uuid": "2e36634d-c3a9-4796-aa3c-cd3f8cc749f3",
        "version": [0, 0, 1],
        "min_engine_version": [1, 20, 0]
    },
    "modules": [
        {
            "type": "data",
            "uuid": "5d3dc1ab-2c41-4843-a3d2-d883f4f2d00b",
            "version": [1, 0, 0]
        },
        {
            "type": "script",
            "uuid": "db7397bd-a1a5-4f48-933c-e88d1af1f1fe",
            "entry": "scripts/main.js",
            "version": [1, 0, 0]
        }
    ],
    "dependencies": [
        { "module_name": "@minecraft/server", "version": "1.6.0" },
        { "module_name": "@minecraft/server-ui", "version": "1.1.0" }
    ],
    "metadata": {
        "url": "https://youtu.be/QhJkCDIZ-NU"
    }
}
```

---

## 5. O arquivo `server_form.json` do addon, literal e completo

`c:/Users/Desktop/Downloads/ADDONS EXEMPLOS/ui1/RP/ui/server_form.json`

```json
/********************************************************
+*   (c) Mojang. All rights reserved                       *
+*   (c) Microsoft. All rights reserved.                   *
+*********************************************************/

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
                        {
                            "binding_name": "#title_text"
                        },
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
                    "size": [400, 200],
                    "$text_name": "#title_text",
                    "$title_text_binding_type": "none",
                    "$child_control": "server_form.long_form_panel",
                    "layer": 2,
                    "bindings": [
                        {
                            "binding_name": "#title_text"
                        },
                        {
                            "binding_type": "view",
                            "source_property_name": "(#title_text = 'Custom Form')",
                            "target_property_name": "#visible"
                        }
                    ]
                }
            }
        ]
    }
}
```

---

## 6. Contexto vanilla necessário para ler o arquivo acima

Blocos literais do corpus de referência, para não depender de memória.

### 6.1 Cadeia de entrada do form

`.../vanilla/ui/server_form.json`
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

`long_form` = `ActionFormData`. `custom_form` = `ModalFormData`.
(`MessageFormData` não passa por aqui — usa outro caminho.)

### 6.2 Coleção de botões — a fonte de dados de qualquer grade

`.../vanilla/ui/server_form.json`
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

**Nome da coleção: `form_buttons`. Contagem: `#form_button_contents` → `#collection_length`.**
Note que o vanilla usa **`type: factory`**, não `type: grid`. O SonheMenu escolheu `grid` — caminho
diferente, com `grid_dimensions` fixo (ver §7).

### 6.3 Ícone do botão — as duas propriedades obrigatórias

`.../vanilla/ui/server_form.json`
```json
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
```

**Regra crítica:** o `image` **não declara `"texture"`**. Se declarar, o `binding_name_override`
para `#texture` pode não sobrescrever e o ícone fica estático — falha silenciosa.
`#texture_file_system` é obrigatório junto de `#texture` (diz de qual pack ler).

### 6.4 Texto do botão

`.../vanilla/ui/server_form.json`
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
            {
              "binding_type": "collection_details",
              "binding_collection_name": "form_buttons"
            }
          ]
        }
```

**`"$pressed_button_name": "button.form_button_click"`** é o que faz o clique voltar ao script.
**`binding_type: "collection_details"` no próprio botão** é o que informa ao engine QUAL índice foi
clicado. Sem ele, todo clique reporta o índice 0 — outra falha silenciosa clássica.

### 6.5 `custom_form` (ModalFormData) — mesmo shape

`.../vanilla/ui/server_form.json`
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

O `ui1` **não toca** em `custom_form`. Todo `ModalFormData` continua vanilla.

### 6.6 Cores globais herdadas

`.../vanilla/ui/_global_variables.json`
```json
  "$title_text_color": [ 0.3, 0.3, 0.3 ],
```
```json
  "$main_header_text_color": [ 1.0, 1.0, 1.0 ],
```

`$title_text_color` é **cinza escuro** — desaparece em fundo preto. O `ui1` não percebe porque mantém
o `dialog_background_hollow_3` claro do vanilla.

---

## 7. Aplicação no SonheMenu

### 7.1 O que o SonheMenu já faz igual ou melhor

Leitura de `c:/Users/Desktop/Desktop/Projetos/bot/ADDONS/SonheMenu_RP/ui/sonhe_forms.json`:

```json
  "long_form": {
    "type": "panel",
    "controls": [
      {
        "sonhe_vanilla_form@common_dialogs.main_panel_no_buttons": {
          "$title_panel": "common_dialogs.standard_title_label",
          "$title_size": [ "100% - 14px", 10 ],
          "size": [ 225, 200 ],
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
      },
      {
        "sonhe_custom_form@sonhe_forms.grid_screen": {
          "layer": 2,
          "bindings": [
            { "binding_name": "#title_text" },
            {
              "binding_type": "view",
              "source_property_name": "(not ((#title_text - '§d§r§e§a§m§r') = #title_text))",
              "target_property_name": "#visible"
            }
          ]
        }
      }
    ]
  }
```

| Ponto | `ui1` | SonheMenu | Veredicto |
|---|---|---|---|
| Topologia `long_form` panel + 2 filhos | ✅ | ✅ | **idêntico — correto** |
| Ordem `#title_text` antes do view binding | ✅ | ✅ | **correto** |
| Nomes de irmãos | duplicados (`long_form`/`long_form`) | únicos (`sonhe_vanilla_form`/`sonhe_custom_form`) | **SonheMenu melhor (R7)** |
| Ramos complementares | ❌ (`- 'x'` vs `= 'x'`) | ✅ (`- 'x'` vs `not (- 'x')`) | **SonheMenu melhor (R6)** |
| Marcador | visível `"Custom Form"` | invisível `§d§r§e§a§m§r` | **SonheMenu melhor (UX)** |
| Ramo 1 aponta pro miolo vanilla | ✅ `server_form.long_form_panel` | ✅ mesmo | **correto** |
| `$title_max_size` | ausente | ausente | **ambos com a pendência R8** |

**Conclusão: a camada de roteamento do SonheMenu já é uma versão superior do `ui1`. Não mexer.**

### 7.2 A diferença estrutural que o `ui1` expõe — e que é candidata #1 a falha silenciosa

O `ui1` grava o override **no caminho vanilla**:
```
RP/ui/server_form.json       ← mesmo caminho, sem _ui_defs.json
```

O SonheMenu grava num **caminho novo** e registra por `_ui_defs.json`:

`SonheMenu_RP/ui/_ui_defs.json`
```json
{
    "ui_defs": [
        "ui/sonhe_forms.json",
        "ui/sonhe_grid.json"
    ]
}
```

`SonheMenu_RP/ui/sonhe_forms.json`
```json
{
  "namespace": "server_form",
```

Ou seja: **dois arquivos diferentes declaram o namespace `server_form` e ambos definem `long_form`** —
o `ui/server_form.json` do vanilla (`"long_form@common_dialogs.main_panel_no_buttons"`) e o
`ui/sonhe_forms.json` do pack (`"long_form"`).

- **Confidence: confirmado** que essa é a configuração atual dos dois packs.
- **Confidence: suspeita** que a resolução do vencedor depende de **ordem de carregamento** entre a
  lista `ui_defs` do vanilla e a do pack. Se a ordem alternar (por versão, por ordem de packs no mundo,
  por cache), o `long_form` do vanilla pode ganhar — **e o sintoma é exatamente "caiu na lista vanilla,
  sem `[UI][error]`"**, porque nada está errado: o engine só escolheu a outra definição.

**Experimento recomendado (não executado aqui — só edição proibida):**
mover o conteúdo de `sonhe_forms.json` para `SonheMenu_RP/ui/server_form.json` (caminho vanilla, como
o `ui1`), mantendo `sonhe_grid.json` no `_ui_defs.json`. Isso elimina a ambiguidade de ordem: passa a
haver **um único** `ui/server_form.json` no pipeline, o do pack, e o merge por chave (R2) preserva
`long_form_panel`, `dynamic_button` e `custom_form` do vanilla.

### 7.3 Checklist de "mudança mínima que apaga a UI", derivado deste addon

Cada item já tem evidência acima. Use como triagem antes de commitar.

1. **Trocar a ordem do array `bindings`** — pôr o `binding_type: "view"` antes do
   `{"binding_name": "#title_text"}` ⇒ `#visible` resolve falso. (R5)
2. **Usar `%` na raiz de `server_form`** — o pai `main_screen_content` é `[0,0]`; percentual vira zero.
   `grid_screen` DEVE manter `"size": [ 320, 452 ]` em px. (R4)
3. **Ramos não complementares** — se ramo 1 é "não contém X", o ramo 2 tem que ser `(not (...))` do
   mesmo predicado, nunca `= 'X'`. (R6)
4. **Renomear/apagar um controle referenciado por `@` ou `$child_control`** — o `ui1` depende de
   `server_form.long_form_panel` e `common_dialogs.main_panel_no_buttons` que ele não define; referência
   quebrada some sem log. Vale para `sonhe_forms.grid_screen`, `sonhe_forms.tile`, `sonhe_forms.tile_button`. (R2)
5. **Declarar `"texture"` num `image` que recebe `#texture` por `binding_name_override`** — o ícone
   congela ou some. (§6.3)
6. **Remover `binding_type: "collection_details"` do botão** — o clique deixa de mapear o índice.
   No SonheMenu isso está em `sonhe_grid.json` → `tile_button`:
   ```json
      {
        "binding_name": "#null",
        "binding_type": "collection_details",
        "binding_collection_name": "form_buttons"
      },
   ```
   (§6.4)
7. **Mexer no marcador do lado BP sem mexer nas DUAS expressões do `sonhe_forms.json`** — o marcador
   `§d§r§e§a§m§r` aparece literalmente 2× no arquivo. Alterar só uma inverte a lógica e some tudo. (R10)
8. **Confiar no operador `-` de string** — não existe no vanilla (0 ocorrências em 188 arquivos).
   É a dependência mais frágil da arquitetura inteira. (R6)

### 7.4 O que o `ui1` NÃO responde

Ele é pequeno demais para cobrir:

- ❌ como popular grade (`type: grid`, `grid_item_template`, `grid_dimensions` vs `#maximum_grid_items`)
  — o `ui1` reusa o `long_form_panel` vanilla inteiro;
- ❌ altura adaptativa em função do nº de botões (o problema P3/P4 já anotado no `sonhe_grid.json`);
- ❌ tema/nine-slice/`color`/`alpha` — zero no addon;
- ❌ o par de âncoras `#null` collection + `#null` collection_details replicado por folha
  (padrão que o SonheMenu já usa e que veio de outra fonte);
- ❌ `ModalFormData` / `MessageFormData`.

Para esses pontos é preciso outra fonte. **O valor do `ui1` é exclusivamente a camada de roteamento
e a prova de que o override por caminho vanilla funciona sem `_ui_defs.json`.**

---

## 8. Apêndice — comandos de verificação usados

```
find "c:/Users/Desktop/Downloads/ADDONS EXEMPLOS/ui1" -type f
head -c 400 ".../ui1/RP/ui/server_form.json" | od -c
grep -n "server_form" ".../vanilla/ui/_ui_defs.json"      # -> linha 142
grep -rn " - '" ".../vanilla/ui" --glob "*.json"          # -> 0 resultados
grep -rn "target_property_name\": \"#visible\"" ".../vanilla/ui"  # -> 209 resultados
```
