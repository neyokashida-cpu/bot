# Fonte: Admin Suite 1.50 — arquitetura completa de `server_form` custom

> **Origem estudada:** `c:/Users/Desktop/Downloads/Estude/RP/ui/` (Admin Suite 1.50, autor "Heraclaus", `min_engine_version [1,21,0]`, RP `version [1,50,0]`).
> **Corpus de comparação vanilla:** `c:/Users/Desktop/Documents/Nova pasta/assets/assets/resource_packs/vanilla/ui/` (188 arquivos, 1.26.x).
> **Data da leitura:** 2026-08-28.
> **Escopo:** lidos integralmente `_ui_defs.json`, `server_form.json`, `list_form.json`, `modal_form.json`, `admin_form.json`; lidos parcialmente (regiões relevantes) `shop_form_new.json`, `member_form.json`, `cosmetic_ui.json`, `customForm/inventory_screen.json`; grep de confirmação no BP obfuscado.

---

## 1. Resumo executivo

O Admin Suite **não escreve uma UI custom dentro do namespace `server_form`**. Ele faz o oposto: mantém a estrutura vanilla de `server_form.json` quase intacta e transforma `server_form.long_form` / `server_form.custom_form` em **roteadores** — painéis que só hospedam "hooks" para telas que moram em **namespaces próprios, em arquivos novos**.

A decisão de qual tela mostrar é tomada por **marcador de texto no título do form**, testado com a aritmética de string do JSON UI (`(#title_text - '§m§a§r§c§a§d§o§r' = #title_text)`), nunca por binding numérico ou índice. Cada hook liga `#visible` ao resultado desse teste, e existe **um ramo de fallback** cuja condição é a conjunção (AND) das negações de todos os outros — é ele que preserva a lista vanilla quando nenhum marcador bate.

Sete telas convivem no mesmo `long_form`/`custom_form` sem se pisarem. É a arquitetura mais escalável que vimos: **adicionar uma tela nova = adicionar um arquivo + uma entrada em `_ui_defs.json` + um hook + um termo no AND do fallback.** Nada mais é tocado.

Achados de maior valor para o SonheMenu, em ordem de impacto:

1. **`main_screen_content` tem `size` `["100%","100%"]` no Admin Suite e `[0,0]` no vanilla.** Toda tela filha dimensionada em `%` colapsa para 0px se esse `size` ficar `[0,0]`. Falha 100% silenciosa: sem erro, sem log, tela em branco ou "sumida".
2. **Item de grid pode ser percentual** (`"25%"`, `"50%"`) — desde que a cadeia inteira de pais até `main_screen_content` tenha tamanho real. O Admin Suite usa `"25%"` e `"50%"` em dois grids diferentes e funciona.
3. **Grid com contagem dinâmica existe e funciona**: `grid_rescaling_type` + `#maximum_grid_items` alimentado por `#form_button_length` (não por `#form_button_contents`).
4. **Guarda `'_' + #form_button_text`** contra o falso-positivo de string vazia em teste de marcador — bug real que o autor tratou explicitamente.
5. **Aritmética de string do JSON UI aceita formatação printf** (`'%.10s' * #form_text`), usada para embutir metadados numéricos no corpo do form.

---

## 2. Mapa da arquitetura

### 2.1 Inventário de arquivos e namespaces

Confirmado por `head -3` em cada arquivo e por checagem de existência no corpus vanilla:

| Arquivo (RP do Admin Suite) | Namespace | Existe no vanilla? | Está em `_ui_defs.json`? |
|---|---|---|---|
| `ui/server_form.json` | `server_form` | **sim** | sim (redundante) |
| `ui/list_form.json` | `list_ui` | não | **sim (obrigatório)** |
| `ui/modal_form.json` | `modal_ui` | não | **sim (obrigatório)** |
| `ui/admin_form.json` | `admin_ui` | não | **sim (obrigatório)** |
| `ui/member_form.json` | `member_ui` | não | **sim (obrigatório)** |
| `ui/cosmetic_ui.json` | `cosmetic_ui` | não | **sim (obrigatório)** |
| `ui/shop_form_new.json` | `split_form` | não | **sim (obrigatório)** |
| `ui/customForm/inventory_screen.json` | `as_invsee` | não | **sim (obrigatório)** |
| `ui/chest_screen.json` | `chest` | sim | sim (redundante) |
| `ui/pocket_containers.json` | `pocket_containers` | sim | sim (redundante) |
| `ui/hud_screen.json` | `hud` | sim | **não** |
| `ui/chat_screen.json` | `chat` | sim | **não** |
| `ui/popup_dialog.json` | `popup_dialog` | sim | **não** |

Isso isola a regra de registro com evidência limpa: **nenhum arquivo de caminho-vanilla precisa estar em `_ui_defs.json`** (hud/chat/popup provam), e **nenhum arquivo novo pode faltar** (todos os 7 novos estão lá).

> Atenção à armadilha de nome: `list_form.json` e `modal_form.json` **soam** vanilla mas são arquivos novos, e seus namespaces são `list_ui` e `modal_ui` — não `server_form`. O nome do arquivo é decoração; o que importa é o campo `"namespace"`.

`ui/_ui_defs.json` literal:

```json
{
  "ui_defs": [
    "ui/customForm/inventory_screen.json",
    "ui/chest_screen.json",
    "ui/pocket_containers.json",
    "ui/admin_form.json",
    "ui/list_form.json",
    "ui/member_form.json",
    "ui/modal_form.json",
    "ui/cosmetic_ui.json",
    "ui/shop_form_new.json",
    "ui/server_form.json"
  ]
}
```

### 2.2 Fluxo de decisão (o roteador)

```
ActionFormData/ModalFormData (script)
        │  .title("…§g§r§i§d§r")   ← marcador embutido no título
        ▼
server_form.third_party_server_screen@common.base_screen
        │  $screen_content = server_form.main_screen_content
        ▼
server_form.main_screen_content   (type: panel, size ["100%","100%"])
        │  type: factory  →  server_form_factory
        ├── long_form   (ActionForm / MessageForm)
        └── custom_form (ModalForm)
                ▼
server_form.long_form (type: panel, 100%x100%)
  ├─ hook_cosmetic_ui@cosmetic_ui.main_panel      layer 10   ← §c§o§s§m§e§t§i§c§r
  ├─ hook_shop_ui@split_form.split_long_form      layer 10   ← §c§u§s§t§o§m
  ├─ hook_member_ui@member_ui.main_screen         layer 10   ← §m§e§m§b§e§r
  ├─ hook_admin_ui@admin_ui.main_screen           layer 10   ← §g§r§i§d§r
  ├─ hook_list_ui@list_ui.main_screen             layer 10   ← §l§i§s§t§r
  └─ default_ui@common_dialogs.main_panel_no_buttons  layer 2 ← NENHUM marcador (AND das negações)

server_form.custom_form (type: panel, 100%x100%)
  ├─ hook_modal_ui@modal_ui.main_screen           layer 10   ← §m§o§d§a§l§r
  └─ default_custom_form@common_dialogs.main_panel_no_buttons layer 2 ← sem §m§o§d§a§l§r
```

### 2.3 Roteamento de segundo nível (dentro de uma tela)

Além do roteamento por título, existe **roteamento por item**: um mesmo `form_buttons` alimenta dois containers diferentes, e cada container filtra os itens por marcador no **texto do botão**.

Em `admin_form.json` a mesma coleção alimenta o grid central e a coluna lateral direita:

- `admin_ui.button_style` (grid central) é visível quando o texto **não** contém `§m§e§m§b§e§r`;
- `admin_ui.right_button_style` (coluna direita) é visível quando o texto **contém** `§m§e§m§b§e§r`.

Em `shop_form_new.json` o mesmo truque separa categorias (`§c§a§t§e§g§o§r§y`) de itens.

Isso significa: **um único `ActionFormData` desenha layouts assimétricos** (grid + sidebar), sem precisar de vários forms.

---

## 3. Tabela de padrões

| # | Padrão | Onde | Confidence |
|---|---|---|---|
| P1 | Um namespace por arquivo; só `server_form` é sobrescrito | todos os arquivos | confirmado |
| P2 | `server_form.long_form` vira `type: panel` roteador (vanilla é `@common_dialogs.main_panel_no_buttons`) | `server_form.json` | confirmado |
| P3 | `main_screen_content.size` de `[0,0]` → `["100%","100%"]` | `server_form.json` | confirmado |
| P4 | Detecção por marcador `§x§y§z` no `#title_text` via subtração de string | `server_form.json` | confirmado |
| P5 | Fallback vanilla com AND de todas as negações | `server_form.long_form` | confirmado |
| P6 | Hooks em `layer: 10`, fallback em `layer: 2` | `server_form.json` | confirmado |
| P7 | Marcador ao mesmo tempo esconde-se do jogador (códigos `§`) e é legível pelo JSON UI | todos | confirmado |
| P8 | Coleção sempre `form_buttons` + `#form_button_contents → #collection_length` (stack) | list/member/split/server | confirmado |
| P9 | Grid usa `#form_button_length → #maximum_grid_items` (nome diferente!) | `admin_form.json`, `shop_form_new.json` | confirmado |
| P10 | Ícone = `image` **sem** `texture`, alimentado por `#form_button_texture → #texture` + `#form_button_texture_file_system → #texture_file_system` | todos | confirmado |
| P11 | Estado `'loading'` do `#texture` tratado à parte (barra de progresso ou oculta) | `server_form.json`, `list_form.json`, `admin_form.json` | confirmado |
| P12 | Dois labels irmãos (`text_with_icon` / `text_only`) alternando por `resolve_sibling_scope` no ícone | list/admin/member/split | confirmado |
| P13 | Botão real = `@common_buttons.light_text_button` com `$button_text: ""` sobre um painel visual próprio | list/admin/member/split | confirmado |
| P14 | `collection_details` sempre no **nó do botão clicável** | todos | confirmado |
| P15 | Guarda `'_' + #form_button_text` contra string vazia em teste de marcador | `admin_form.json` | confirmado |
| P16 | Botão de fechar próprio remapeando `button.menu_select`/`menu_ok` → `button.menu_exit` | list/modal/admin/member/split | confirmado |
| P17 | Metadados numéricos embutidos no `#form_text` e extraídos com `'%.10s' *` | `shop_form_new.json` | confirmado (a sintaxe) |
| P18 | Slot fixo por índice via `collection_name` no pai + `collection_index` no filho | `cosmetic_ui.json`, `inventory_screen.json` | confirmado |
| P19 | Todas as telas custom usam `type: image` + nine-slice `.json` do próprio pack para moldura | todos os arquivos novos | confirmado |
| P20 | Marcadores no script terminam com `§r` extra que o JSON UI não testa | BP `scripts/**` | confirmado |

---

## 4. Regras, com evidência literal

### R1 — `_ui_defs.json`: arquivo novo é obrigatório; override de caminho vanilla é opcional
**Confidence: confirmado.**

`ui/hud_screen.json`, `ui/chat_screen.json` e `ui/popup_dialog.json` existem no pack, têm caminho idêntico ao vanilla, e **não aparecem** na lista de `_ui_defs.json` (bloco literal na §2.1). Já os 7 arquivos de caminho novo aparecem todos.

**Corolário operacional:** se sua UI custom "sumiu" e ela mora num arquivo de nome novo, a primeira coisa a checar é `_ui_defs.json`. Arquivo novo fora do `_ui_defs` **não gera erro** — os namespaces dele simplesmente não existem, e qualquer `@namespace.controle` que aponte para lá vira referência morta. Falha silenciosa clássica.

---

### R2 — `main_screen_content` precisa de tamanho real quando as telas filhas são percentuais
**Confidence: confirmado (diff direto vanilla × Admin Suite).**

Vanilla `resource_packs/vanilla/ui/server_form.json`:

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

Admin Suite `RP/ui/server_form.json`:

```json
"main_screen_content": {
  "type": "panel",
  "size": [ "100%", "100%" ],
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

O vanilla pode usar `[0,0]` porque `long_form@common_dialogs.main_panel_no_buttons` tem `"size": [225, 200]` — **pixel absoluto**, independente do pai. O Admin Suite tem telas em `"70%","70%"`, `"60%","60%"`, `"50%","70%"` — todas medidas contra o pai. Com pai `[0,0]`, `70%` de 0 = 0.

**Regra derivada:** a cadeia inteira de ancestrais até `main_screen_content` precisa ter tamanho não-zero no eixo em que o filho usa `%`. Um único `[0,0]` ou `"100%c"` sem filhos no meio do caminho apaga tudo abaixo, sem erro nenhum.

---

### R3 — Detecção de form por marcador no título usa subtração de string
**Confidence: confirmado.**

A operação `A - B` no JSON UI remove a primeira ocorrência da substring `B` de `A`. Logo:

- `(#title_text - 'MARCADOR' = #title_text)` → **verdadeiro quando o marcador NÃO está presente** (nada foi removido).
- `(not (#title_text - 'MARCADOR' = #title_text))` → **verdadeiro quando o marcador ESTÁ presente**.

Literal, hook do grid:

```json
{
  "hook_admin_ui@admin_ui.main_screen": {
    "layer": 10,
    "bindings": [
      {
        "binding_type": "view",
        "source_property_name": "(not (#title_text - '§g§r§i§d§r' = #title_text))",
        "target_property_name": "#visible"
      }
    ]
  }
}
```

**Por que `§g§r§i§d§r` e não `grid`:** cada `§x` é um código de formatação; o cliente **não desenha** esses caracteres, mas eles continuam presentes na string entregue ao binding. O marcador é invisível para o jogador e visível para a UI. Note também que `§m§e§m§b§e§r` é literalmente a palavra "member" com `§` antes de cada letra — o padrão é uniforme.

Marcadores catalogados no Admin Suite:

| Marcador testado no JSON | Tela | Arquivo |
|---|---|---|
| `§g§r§i§d§r` | grid 3×N + sidebar | `admin_form.json` (`admin_ui`) |
| `§l§i§s§t§r` | lista com ícone | `list_form.json` (`list_ui`) |
| `§m§o§d§a§l§r` | modal com preview do player | `modal_form.json` (`modal_ui`) |
| `§m§e§m§b§e§r` | tela de membros | `member_form.json` (`member_ui`) |
| `§c§o§s§m§e§t§i§c§r` | 3 slots fixos | `cosmetic_ui.json` (`cosmetic_ui`) |
| `§c§u§s§t§o§m` | loja categoria+itens | `shop_form_new.json` (`split_form`) |
| `§c§a§t§e§g§o§r§y` | (nível item, não título) | `shop_form_new.json` |

---

### R4 — O ramo de fallback é a conjunção de TODAS as negações
**Confidence: confirmado.** Esta é a regra que preserva a lista vanilla.

```json
{
  "default_ui@common_dialogs.main_panel_no_buttons": {
    "$title_panel": "common_dialogs.standard_title_label",
    "$title_size": [ "100% - 15px", 10 ],
    "$title_max_size": [ "100% - 15px", 10 ],
    "size": [ 225, 200 ],
    "$text_name": "#title_text",
    "$title_text_binding_type": "none",
    "$child_control": "server_form.long_form_panel",
    "layer": 2,
    "bindings": [
      {
        "binding_type": "view",
        "source_property_name": "((#title_text - '§l§i§s§t§r' = #title_text) and (#title_text - '§g§r§i§d§r' = #title_text) and (#title_text - '§c§o§s§m§e§t§i§c§r' = #title_text) and (#title_text - '§m§e§m§b§e§r' = #title_text) and (#title_text - '§c§u§s§t§o§m' = #title_text))",
        "target_property_name": "#visible"
      }
    ]
  }
}
```

São exatamente 5 termos para os 5 hooks irmãos. **Esquecer de adicionar um termo ao AND ao criar um hook novo faz as duas telas aparecerem sobrepostas** — não é falha silenciosa, é falha visível e feia. O oposto (termo a mais, hook a menos) mata o fallback e a lista vanilla some.

O equivalente do `custom_form` tem um único termo, porque só há um hook:

```json
"bindings": [
  {
    "binding_type": "view",
    "source_property_name": "(#title_text - '§m§o§d§a§l§r' = #title_text)",
    "target_property_name": "#visible"
  }
]
```

Repare que aqui não há `not`: a condição do fallback já é a forma "não contém".

---

### R5 — Marcadores no script carregam um `§r` a mais que o JSON não testa
**Confidence: confirmado (grep no BP), com uma nuance.**

O JS obfuscado do BP contém as constantes:

```
'§g§r§i§d§r'            (scripts/.core.js, scripts/modules/admin/access.js, …)
'§g§r§i§d§r§d§i§m§r'    (scripts/modules/admin/spy.js)
'§c§u§s§t§o§m§r'        (scripts/modules/shop/customForm.js)
'§c§a§t§e§g§o§r§y§r'    (scripts/modules/shop/customForm.js)
'§m§o§d§a§l§r'          (vários)
'§m§e§m§b§e§r'          (vários)
```

O JSON testa `'§c§u§s§t§o§m'` (sem `§r` final) e `'§c§a§t§e§g§o§r§y'` (sem `§r` final), mas o script escreve `'§c§u§s§t§o§m§r'` e `'§c§a§t§e§g§o§r§y§r'`. **Como o teste é "contém substring", o `§r` de reset no fim funciona como terminador cosmético e não quebra o match.** O `§r` restaura a cor padrão para o texto real que vem depois do marcador.

Nuance importante — `'§g§r§i§d§r§d§i§m§r'` **contém** `'§g§r§i§d§r'` como prefixo. Isso quer dizer que uma tela com o marcador estendido também dispara o hook do grid. Ou é intencional (variante de grid), ou é um caso onde ordem/especificidade importa. **Confidence: suspeita** quanto à intenção; **confirmado** quanto ao fato de a substring bater.

**Lição para o SonheMenu:** marcadores nunca podem ser prefixo um do outro, a não ser deliberadamente. Se algum dia existirem `§d§r§e§a§m§r` e `§d§r§e§a§m§r§2`, o segundo dispara os dois hooks.

---

### R6 — Coleção: `#form_button_contents` para stack/factory, `#form_button_length` para grid
**Confidence: confirmado.** São **dois bindings de nome diferente** e não são intercambiáveis nos exemplos lidos.

**Forma stack + factory** (`list_form.json`, `member_form.json`, `shop_form_new.json`, e o próprio `server_form.long_form_dynamic_buttons_panel`):

```json
"button_list_content": {
  "type": "stack_panel",
  "orientation": "vertical",
  "size": [ "100%", "100%c" ],
  "factory": {
    "name": "buttons",
    "control_ids": {
      "button": "@list_ui.button_style"
    }
  },
  "collection_name": "form_buttons",
  "bindings": [
    {
      "binding_name": "#form_button_contents",
      "binding_name_override": "#collection_length"
    }
  ]
}
```

**Forma grid** (`admin_form.json`):

```json
"button_list_content": {
  "type": "grid",
  "grid_dimensions": [ 3, 3 ],
  "size": [ "100%", "100%c" ],
  "grid_rescaling_type": "horizontal",
  "grid_item_template": "admin_ui.button_style",
  "grid_fill_direction": "horizontal",
  "factory": {
    "name": "buttons",
    "control_name": "admin_ui.button_style"
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

Observações de peso:

1. O grid do Admin Suite declara **`grid_dimensions` E `factory` E `grid_item_template` E `#maximum_grid_items` ao mesmo tempo**. Com `grid_rescaling_type: "horizontal"`, `grid_dimensions [3,3]` age como semente/limite de colunas e `#maximum_grid_items` define quantos itens realmente instanciar. Isso **contradiz diretamente** a nota `//3` do nosso `sonhe_grid.json`, que proíbe `grid_dimensions` junto de `#maximum_grid_items`. **Confidence: confirmado** que o Admin Suite faz isso; **suspeita** de que a nossa proibição venha de outra causa que foi mal atribuída.
2. Na forma grid o factory usa `"control_name"` (singular, um template só). Na forma stack usa `"control_ids"` (mapa por tipo de item: `button`, `label`, `header`, `divider`). **A chave é diferente e não é opcional.**
3. `#form_button_contents` e `#form_button_length` são bindings distintos do engine. Nosso `sonhe_grid.json` anota que "a pesquisa NÃO confirmou que `#form_button_contents` alimenta `#maximum_grid_items`" — correto, **não alimenta; quem alimenta é `#form_button_length`**. Esta é a peça que faltava.

---

### R7 — Grid com contagem calculada por expressão
**Confidence: confirmado.** `shop_form_new.json`, `split_form.item_scrolling_content`:

```json
{
  "items": {
    "type": "grid",
    "size": [ "100%", "100%c" ],
    "grid_dimensions": [ 3, 0 ],
    "grid_item_template": "split_form.item_button_wrapper",
    "grid_fill_direction": "horizontal",
    "grid_rescaling_type": "horizontal",
    "factory": {
      "name": "buttons",
      "control_name": "split_form.item_button_wrapper"
    },
    "collection_name": "form_buttons",
    "bindings": [
      { "binding_name": "#form_text" },
      {
        "binding_type": "view",
        "source_property_name": "(1 * ('%.10s' * #form_text - ']'))",
        "target_property_name": "#category_count"
      },
      { "binding_name": "#form_button_length" },
      {
        "binding_type": "view",
        "source_property_name": "(#form_button_length - #category_count)",
        "target_property_name": "#maximum_grid_items"
      }
    ]
  }
}
```

Cinco coisas confirmadas aqui de uma vez:

- **`grid_dimensions: [3, 0]`** — 3 colunas, linhas ilimitadas. O `0` no eixo Y é válido e significa "cresce conforme os itens".
- **Ordem de bindings importa.** `{ "binding_name": "#form_text" }` aparece **antes** da `view` que consome `#form_text`; `{ "binding_name": "#form_button_length" }` aparece **antes** da `view` que o consome. Um binding `view` só enxerga o que já foi resolvido acima dele no mesmo array. Inverter a ordem = expressão avalia sobre valor vazio, silenciosamente.
- **Formatação printf na aritmética:** `'%.10s' * #form_text` produz os 10 primeiros caracteres de `#form_text`. O operador `*` com uma string de formato à esquerda é `sprintf`.
- **`1 * string` converte para número.**
- **Uma view binding pode escrever num nome arbitrário (`#category_count`) e outra view binding pode lê-lo em seguida.** É a única forma de "variável temporária" em runtime.

O label do corpo usa a operação inversa para esconder o prefixo do jogador:

```json
{
  "label": {
    "type": "label",
    "text": "#final_body_text",
    "size": [ "100% - 10px", "default" ],
    "bindings": [
      { "binding_name": "#form_text" },
      {
        "binding_type": "view",
        "source_property_name": "(('§f' + #form_text - ('%.12s' * ('§f' + #form_text))) - ']')",
        "target_property_name": "#final_body_text"
      }
    ]
  }
}
```

Lendo a aritmética: `'§f' + #form_text` tem 2 caracteres a mais; `%.12s` disso equivale a `%.10s` do original; subtrair o prefixo de si mesmo deixa o resto; `- ']'` remove o fechamento. **Inferência: o corpo do form começa com 10 caracteres numéricos seguidos de `]` — algo como `0000000003]Texto real…`.** Confidence: **provável** (a aritmética só fecha com essa forma; o JS obfuscado não permitiu confirmar diretamente).

Mesmo truque, mais simples, para o título:

```json
{
  "title@split_form.label_custom": {
    "text": "#final_title_text",
    "bindings": [
      { "binding_name": "#title_text" },
      {
        "binding_type": "view",
        "source_property_name": "(#title_text - '§c§u§s§t§o§m')",
        "target_property_name": "#final_title_text"
      }
    ]
  }
}
```

**O marcador é removido do texto antes de exibir.** Vale copiar: mesmo sendo invisível, remover evita que o `§r` final zere formatação que o autor queria manter.

---

### R8 — Ícone de botão: `image` sem `texture`, três bindings, um estado `'loading'`
**Confidence: confirmado.** Padrão idêntico em `server_form.json`, `list_form.json`, `admin_form.json`, `member_form.json`, `shop_form_new.json`.

```json
{
  "icon": {
    "type": "image",
    "layer": 30,
    "size": [ 20, 20 ],
    "anchor_from": "center",
    "anchor_to": "center",
    "offset": [ 0, -5 ],
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
```

- **`#form_button_texture_file_system` não é opcional.** Sem ele, texturas vindas de URL/pacote remoto não resolvem e o ícone fica em branco — sem erro.
- **`'loading'` é um valor real que `#texture` assume.** Tratá-lo como textura válida produz um quadrado quebrado.
- O `image` **não declara `"texture"` estático**. Declarar um valor estático e depois sobrescrever por binding é tolerado, mas os cinco arquivos do Admin Suite não fazem isso em nenhum ícone de botão.

Em `server_form.dynamic_button` (o único lugar) o estado `'loading'` ganha uma barra de progresso:

```json
{
  "progress@progress.progress_loading_bars": {
    "size": [ 30, 4 ],
    "offset": [ -2, 16 ],
    "bindings": [
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
```

---

### R9 — Dois labels irmãos alternados por `resolve_sibling_scope` no ícone
**Confidence: confirmado.** Substitui um "layout condicional" que o JSON UI não tem.

```json
{
  "text_with_icon": {
    "type": "label",
    "text": "#form_button_text",
    "layer": 32,
    "anchor_from": "center", "anchor_to": "center",
    "text_alignment": "center",
    "offset": [ 0, 10 ],
    "color": [ 1, 1, 1 ],
    "bindings": [
      {
        "binding_name": "#form_button_text",
        "binding_type": "collection",
        "binding_collection_name": "form_buttons"
      },
      {
        "binding_type": "view",
        "source_control_name": "icon",
        "resolve_sibling_scope": true,
        "source_property_name": "#visible",
        "target_property_name": "#visible"
      }
    ]
  }
},
{
  "text_only": {
    "type": "label",
    "text": "#form_button_text",
    "layer": 32,
    "anchor_from": "center", "anchor_to": "center",
    "text_alignment": "center",
    "color": [ 1, 1, 1 ],
    "bindings": [
      {
        "binding_name": "#form_button_text",
        "binding_type": "collection",
        "binding_collection_name": "form_buttons"
      },
      {
        "binding_type": "view",
        "source_control_name": "icon",
        "resolve_sibling_scope": true,
        "source_property_name": "(not #visible)",
        "target_property_name": "#visible"
      }
    ]
  }
}
```

Regras embutidas:

- **`source_control_name` é o nome do irmão *sem* namespace e sem `@base`.** Aqui é `"icon"`, e o irmão realmente se chama `icon` no mesmo `panel_name`.
- **`resolve_sibling_scope: true` é obrigatório** para sair do próprio escopo. Sem ele o binding lê o `#visible` do próprio label — auto-referência que resolve para algo indefinido, sem erro.
- Ambos precisam **repetir** o binding de dado `#form_button_text` na coleção. Cada folha carrega o próprio contexto de coleção; o binding do pai não desce.

Em `list_form.json` a mesma dupla existe com posicionamentos diferentes (`offset [30,0]` com ícone à esquerda × centralizado sem ícone).

---

### R10 — O botão clicável é uma camada separada por cima do visual
**Confidence: confirmado.** Nenhuma tela custom desenha texto dentro do botão vanilla.

```json
{
  "form_button@common_buttons.light_text_button": {
    "size": [ "100%", "100%" ],
    "anchor_from": "top_left",
    "anchor_to": "top_left",
    "$pressed_button_name": "button.form_button_click",
    "$button_text": "",
    "bindings": [
      {
        "binding_type": "collection_details",
        "binding_collection_name": "form_buttons"
      }
    ]
  }
}
```

- **`$button_text: ""`** — o botão não desenha texto; quem desenha é o `panel_name` irmão, abaixo dele na ordem de `controls`.
- **`$pressed_button_name: "button.form_button_click"`** é o nome fixo que o engine converte no callback do `ActionFormData`. Errar esse nome = clique não faz nada, sem erro.
- **`collection_details` mora no botão clicável, não no painel visual.** É ele que informa ao engine *qual índice* foi clicado. Colocar no lugar errado → todo clique reporta índice 0 ou nenhum, silenciosamente.
- A aparência vem de `$default_button_texture` / `$hover_button_texture` / `$pressed_button_texture`, **declaradas no painel pai** e herdadas por escopo de variável:

```json
"button_style": {
  "type": "panel",
  "size": [ "25%", "60%x" ],
  "$default_button_texture": "textures/ui/btn",
  "$hover_button_texture": "textures/ui/btnpress",
  "$pressed_button_texture": "textures/ui/btnpress",
  …
}
```

Repare em `"size": [ "25%", "60%x" ]` — largura 25% do grid, altura 60% *da própria largura* (`x` = referência ao eixo X do próprio controle). Item de grid **percentual** funciona; o que não pode é o pai não ter tamanho (R2).

---

### R11 — Guarda contra string vazia em teste de marcador (`'_' +`)
**Confidence: confirmado.** É o detalhe mais sutil do pack inteiro.

```json
"button_style": {
  "type": "panel",
  "size": [ "25%", "60%x" ],
  "bindings": [
    {
      "binding_name": "#form_button_text",
      "binding_type": "collection",
      "binding_collection_name": "form_buttons"
    },
    {
      "binding_type": "view",
      "source_property_name": "((('_' + #form_button_text) - '§m§e§m§b§e§r' = ('_' + #form_button_text)) and (not (#form_button_text = '')))",
      "target_property_name": "#visible"
    }
  ]
}
```

E o par complementar em `right_button_style`:

```json
{
  "binding_type": "view",
  "source_property_name": "(not (('_' + #form_button_text) - '§m§e§m§b§e§r' = ('_' + #form_button_text)))",
  "target_property_name": "#visible"
}
```

Por que o `'_'`: com `#form_button_text` vazio, `'' - 'qualquer'` = `''`, e `'' = ''` é **verdadeiro** — o teste "não contém o marcador" retorna verdadeiro para célula vazia, e o slot vazio se desenha. Prefixar `'_'` garante que a string nunca seja vazia. O `and (not (#form_button_text = ''))` é o **segundo** cinto de segurança, que oculta explicitamente a célula vazia.

**Isto é exatamente o problema de "slots vazios" que o SonheMenu já enfrentou** (ver commit `feat(SonheMenu_RP): tema dark sem asset custom + slots vazios ocultos`). A nossa solução atual usa só `(not (#form_button_text = ''))`; o Admin Suite usa os dois.

---

### R12 — Botão de fechar próprio exige remapeamento de input
**Confidence: confirmado.** Repetido literalmente em 5 arquivos.

```json
{
  "close_button_style@common_buttons.light_text_button": {
    "size": [ "100% - 2px", "100% - 2px" ],
    "anchor_from": "center",
    "anchor_to": "center",
    "$button_text": "",
    "$default_button_texture": "textures/ui/close",
    "$hover_button_texture": "textures/ui/closepress",
    "$pressed_button_texture": "textures/ui/closepress",
    "$pressed_button_name": "button.menu_exit",
    "button_mappings": [
      {
        "from_button_id": "button.menu_select",
        "to_button_id": "button.menu_exit",
        "mapping_type": "pressed"
      },
      {
        "from_button_id": "button.menu_ok",
        "to_button_id": "button.menu_exit",
        "mapping_type": "focused"
      }
    ]
  }
}
```

Sem os `button_mappings`, o botão funciona no mouse/toque mas **não** no controle. E o `third_party_server_screen` continua com o mapeamento global do vanilla, preservado sem alteração:

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
}
```

**Este bloco é byte-a-byte igual ao vanilla.** É a única parte de `server_form.json` que o autor não tocou — sinal de que mexer aqui é arriscado.

---

### R13 — Slot fixo por índice: `collection_name` no pai, `collection_index` no filho
**Confidence: confirmado.** Alternativa a factory quando o número de itens é conhecido e o layout é irregular.

`cosmetic_ui.json`:

```json
"bottom": {
  "type": "stack_panel",
  "orientation": "horizontal",
  "size": [ "100%", "fill" ],
  "collection_name": "form_buttons",
  "controls": [
    {
      "left_column": {
        "type": "panel",
        "size": [ "50%", "100%" ],
        "collection_index": 0,
        "controls": [ { "btn_0@cosmetic_ui.custom_button_impl1": { … } } ]
      }
    },
    {
      "right_column": {
        "type": "stack_panel",
        "orientation": "vertical",
        "size": [ "50%", "100%" ],
        "collection_name": "form_buttons",
        "controls": [
          {
            "top_slot": {
              "type": "panel", "size": [ "100%", "50%" ],
              "collection_index": 1,
              "controls": [ { "btn_1@cosmetic_ui.custom_button_impl2": { … } } ]
            }
          },
          {
            "bottom_slot": {
              "type": "panel", "size": [ "100%", "50%" ],
              "collection_index": 2,
              "controls": [ { "btn_2@cosmetic_ui.custom_button_impl3": { … } } ]
            }
          }
        ]
      }
    }
  ]
}
```

Detalhe crítico: **`collection_name` é redeclarado no `right_column`**, mesmo o pai já tendo. O contexto de coleção **não atravessa** níveis de container de forma confiável; o autor reafirma. Mesmo padrão no `customForm/inventory_screen.json`, que usa `collection_name: "container_items"` no pai e `collection_index: 27..35` nos filhos da hotbar.

---

### R14 — Modal e formulário custom: as `$vars` vêm de `settings_common`, não são inventadas
**Confidence: confirmado.** Tanto `server_form.json` quanto `modal_form.json` reaproveitam a fábrica vanilla de controles de opções, item por item:

```json
"generated_contents": {
  "type": "stack_panel",
  "size": [ "100%", "100%c" ],
  "orientation": "vertical",
  "anchor_from": "top_left",
  "anchor_to": "top_left",
  "factory": {
    "name": "buttons",
    "control_ids": {
      "label": "@modal_ui.custom_label",
      "toggle": "@modal_ui.custom_toggle",
      "slider": "@modal_ui.custom_slider",
      "step_slider": "@modal_ui.custom_step_slider",
      "dropdown": "@modal_ui.custom_dropdown",
      "input": "@modal_ui.custom_input",
      "header": "@modal_ui.custom_header",
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
}
```

- A coleção do modal é **`custom_form`**, e o tamanho vem de **`#custom_form_length`** — nomes totalmente diferentes dos do long_form.
- As 8 chaves de `control_ids` (`label`, `toggle`, `slider`, `step_slider`, `dropdown`, `input`, `header`, `divider`) são **fixas do engine**. Faltar uma faz aquele tipo de campo não renderizar — sem erro.
- O `divider` aponta direto para o vanilla `@settings_common.option_group_section_divider`, sem cópia.

Ancestrais vanilla confirmados como existentes no corpus 1.26 (`resource_packs/vanilla/ui/`):

| Referência usada | Onde está no vanilla |
|---|---|
| `common.base_screen` | `ui_common.json` |
| `common.scrolling_panel` | `ui_common.json` |
| `common.text_edit_box` | `ui_common.json` |
| `common_dialogs.main_panel_no_buttons` | `ui_template_dialogs.json` |
| `common_dialogs.standard_title_label` | `ui_template_dialogs.json` |
| `common_buttons.light_text_button` | `ui_template_buttons.json` |
| `progress.progress_loading_bars` | `feed_common.json` (e outros) |
| `settings_common.*` (todos) | `settings_sections/settings_common.json` |

**Regra:** herdar de um nome vanilla que não existe na versão-alvo **não gera log**; o controle simplesmente não é construído. É uma das principais causas de "sumiu sem erro" em upgrade de versão do jogo.

O `custom_input` do `modal_form.json` é o exemplo de como trocar só o visual sem reescrever a mecânica:

```json
"custom_text_bg": {
  "type": "image",
  "texture": "textures/ui/input",
  "size": [ "100% + 10px", "100% - 2px" ]
},
…
"text_edit@common.text_edit_box": {
  "size": [ "100% - 10px", "100%" ],
  "max_length": 1080,
  "$text_edit_box_placeholder_content_binding_name": "#custom_placeholder_text",
  "$text_edit_box_placeholder_content_binding_type": "collection",
  "$text_edit_box_grid_collection_name": "custom_form",
  "$text_edit_box_content_binding_type": "collection",
  "$text_edit_box_content_binding_name": "#custom_input_text",
  "$option_binding_name": "#custom_input_text",
  "$text_box_enabled_binding_name": "#custom_input_enabled",
  "$text_box_name": "custom_input",
  "$text_background_default": "modal_ui.custom_text_bg",
  "$text_background_hover": "modal_ui.custom_text_bg_hover",
  "$text_background_locked": "modal_ui.custom_text_bg_locked"
}
```

`$text_background_default` / `_hover` / `_locked` recebem **nomes de controle** (`modal_ui.custom_text_bg`), não caminhos de textura.

---

### R15 — Preview de player 3D dentro do modal
**Confidence: confirmado.** Vale registrar porque é o único `type: "custom"` do pack.

```json
"player_preview": {
  "type": "custom",
  "renderer": "live_player_renderer",
  "property_bag": { "#look_at_cursor": true },
  "animation_reset_name": "screen_animation_reset",
  "anims": [
    "@common.screen_exit_size_animation_push",
    "@common.screen_exit_size_animation_pop",
    "@common.screen_entrance_size_animation_push",
    "@common.screen_entrance_size_animation_pop"
  ],
  "size": [ "100%", "100%" ],
  "anchor_from": "center",
  "anchor_to": "center",
  "layer": 10
}
```

Usado dentro de um container com `"clips_children": true`, senão o modelo vaza para fora do painel:

```json
"clipping_container": {
  "type": "panel",
  "size": [ "100% - 4px", "100% - 4px" ],
  "layer": 2,
  "clips_children": true,
  "controls": [ { "player_model@modal_ui.player_preview": { "layer": 1 } } ]
}
```

---

### R16 — `100%y` / `100%x` para forçar quadrado
**Confidence: confirmado.** Usado para o botão de fechar e para itens de lista lateral.

```json
"cls": {
  "type": "panel",
  "size": [ "100%y", "100%" ],
  …
}
```

```json
"new_button_style": {
  "type": "panel",
  "size": [ "100%y", "100%" ],
  …
}
```

```json
"right_button_style": {
  "type": "panel",
  "size": [ "100%", "100%x" ],
  …
}
```

`"100%y"` = "minha largura é 100% da minha própria altura". Só funciona se o **outro** eixo tiver tamanho resolvível. Dois eixos cruzados (`["100%y","100%x"]`) é referência circular — resultado indefinido, sem erro.

---

## 5. Causas prováveis de falha silenciosa (síntese)

Cada item abaixo é uma condição em que o cliente **não emite `[UI][error]`** e a tela custom simplesmente não aparece. Ordenado pela força da evidência.

| # | Causa | Evidência | Confidence |
|---|---|---|---|
| F1 | Arquivo novo ausente de `_ui_defs.json` → namespace inexistente → `@ns.controle` vira referência morta | §2.1: os 7 arquivos novos estão listados, os 5 de caminho vanilla não precisam | confirmado |
| F2 | Ancestral em cadeia `%` com tamanho zero (`[0,0]`, `100%c` sem filhos) | R2, diff `main_screen_content` vanilla `[0,0]` × Admin Suite `["100%","100%"]` | confirmado |
| F3 | Herdar de nome vanilla inexistente na versão-alvo | R14, tabela de ancestrais | provável |
| F4 | `binding_type: "view"` colocado **antes** do `binding_name` que ele consome | R7, ordem literal em `split_form` items grid | confirmado |
| F5 | Falta de `resolve_sibling_scope: true` num binding com `source_control_name` | R9 | confirmado |
| F6 | `source_control_name` apontando para um irmão que não existe com aquele nome exato | R9 | provável |
| F7 | `collection_details` fora do controle clicável → clique sem índice | R10 | provável |
| F8 | Falta de `#form_button_texture_file_system` → ícone remoto nunca resolve | R8 | provável |
| F9 | Marcador vazio / `#form_button_text = ''` fazendo teste "não contém" retornar verdadeiro | R11, guarda `'_' +` explícita | confirmado |
| F10 | Contexto de coleção não redeclarado num container aninhado | R13, `collection_name` repetido em `right_column` | provável |
| F11 | Chave errada no factory (`control_name` × `control_ids`) | R6 | confirmado |
| F12 | Binding de contagem errado no grid (`#form_button_contents` em vez de `#form_button_length`) | R6 | confirmado |
| F13 | Marcador que é prefixo de outro marcador disparando dois hooks | R5, `§g§r§i§d§r§d§i§m§r` contém `§g§r§i§d§r` | suspeita |
| F14 | Termo faltando no AND do fallback → sobreposição, ou termo sobrando → fallback morto | R4 | confirmado |
| F15 | `"100%y"` e `"100%x"` cruzados no mesmo controle | R16 (inferência sobre o uso observado) | suspeita |

---

## 6. Aplicação no SonheMenu

Estado atual lido (somente leitura, nada editado):

- `ADDONS/SonheMenu_RP/ui/_ui_defs.json` → `["ui/sonhe_forms.json", "ui/sonhe_grid.json"]`
- `ui/sonhe_forms.json` → namespace `server_form`, sobrescreve **só** `long_form`
- `ui/sonhe_grid.json` → namespace `sonhe_forms`, tela de grid
- Marcador: `§d§r§e§a§m§r`

### 6.1 O que já está certo (converge com o Admin Suite)

| Nosso padrão | Equivalente no Admin Suite |
|---|---|
| Namespace próprio (`sonhe_forms`) para a tela, `server_form` só como roteador | idêntico (`admin_ui`, `list_ui`, …) |
| `long_form` reescrito como `type: panel` com filhos condicionais | idêntico |
| Marcador `§d§r§e§a§m§r` no título, testado por subtração de string | idêntico |
| Ramo vanilla preservado com `@common_dialogs.main_panel_no_buttons` e as mesmas `$vars` | idêntico |
| `{ "binding_name": "#title_text" }` declarado antes da `view` que o consome | idêntico (R7 / F4) |
| Ícone como `image` sem `texture`, via `binding_name_override` | idêntico (R8) |
| `collection_details` no próprio botão | idêntico (R10) |
| `(not (#form_button_text = ''))` para ocultar slot vazio | metade do padrão (falta o `'_' +`) |

### 6.2 Divergências a investigar, por prioridade

**A1 — Não sobrescrevemos `main_screen_content`. (risco alto)**
`sonhe_forms.json` só redefine `long_form`. Logo `main_screen_content` continua o vanilla, com `"size": [0, 0]`. Nosso `sonhe_forms.grid_screen` usa `"size": [ 320, 452 ]` — **pixel absoluto**, então hoje sobrevive. Mas **qualquer mudança para `%` em `grid_screen`, `grid_stack` ou `tiles_grid` colapsa a tela para 0px, sem erro.** Isso explica a classe inteira de "mudança mínima fez a UI sumir". A correção defensiva é copiar o `main_screen_content` do Admin Suite (R2) — passa a ser sobrescrita de um controle a mais, mas remove a armadilha permanentemente.

**A2 — `grid_dimensions` + `#maximum_grid_items` não é proibido. (risco médio, ganho alto)**
A nota `//3` do `sonhe_grid.json` lista como PROIBIDO "`grid_dimensions` junto de `#maximum_grid_items`", e a nota `//5` diz que P3/P4 (altura adaptativa) foram deixados de lado porque "a pesquisa NÃO confirmou que `#form_button_contents` alimenta `#maximum_grid_items`". **Ambas as premissas estão respondidas:** o binding correto é **`#form_button_length`**, não `#form_button_contents` (R6/F12), e o Admin Suite usa `grid_dimensions [3,3]` + `grid_rescaling_type: "horizontal"` + `#maximum_grid_items` simultaneamente, em produção. Para altura adaptativa nossa configuração de referência seria:

```json
"tiles_grid": {
  "type": "grid",
  "size": [ "100%", "100%c" ],
  "grid_dimensions": [ 3, 0 ],
  "grid_fill_direction": "horizontal",
  "grid_rescaling_type": "horizontal",
  "grid_item_template": "sonhe_forms.tile",
  "factory": {
    "name": "buttons",
    "control_name": "sonhe_forms.tile"
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

`grid_dimensions [3, 0]` vem literalmente do `split_form.items` (R7). **Não aplicar sem teste em jogo** — o histórico do repo (`fix: reverte topologia de altura adaptativa que quebrou em jogo`) mostra que já quebrou uma vez, e o `100%c` no eixo Y do grid depende do A1 estar resolvido.

**A3 — Falta a guarda `'_' +` no teste de slot vazio. (risco baixo, custo zero)**
Hoje usamos só `(not (#form_button_text = ''))`. O Admin Suite usa as duas metades juntas (R11). Se algum dia um tile precisar testar marcador no texto do botão, a versão sem `'_'` dá falso-positivo em célula vazia.

**A4 — Não removemos o marcador antes de exibir o título. (cosmético)**
`sonhe_grid.json` faz `"text": "#title_text"` direto. O `split_form` remove o marcador antes (R7). Como `§d§r§e§a§m§r` termina em `§r`, ele **reseta a formatação** do que vier depois — se algum dia o título usar cor, ela morre no ponto do marcador. Padrão a copiar:

```json
"bindings": [
  { "binding_name": "#title_text" },
  {
    "binding_type": "view",
    "source_property_name": "(#title_text - '§d§r§e§a§m§r')",
    "target_property_name": "#final_title_text"
  }
]
```
com `"text": "#final_title_text"`.

**A5 — Marcador único, sem irmãos, e sem AND no fallback. (ok hoje, dívida amanhã)**
Nosso fallback testa um único termo, o que é correto para um hook só (idêntico ao `custom_form` do Admin Suite). **No momento em que existir uma segunda tela**, o fallback vira o AND de todas as negações (R4) e o novo marcador não pode ser prefixo de `§d§r§e§a§m§r` nem tê-lo como prefixo (F13).

**A6 — Roteamento por item ainda não explorado. (oportunidade)**
Filtrar itens da mesma `form_buttons` por marcador no texto do botão (R3 nível 2 / R11) permitiria, num único `ActionFormData`, ter grid principal + linha de ações fixas (voltar/fechar/paginação) sem gambiarra no script.

**A7 — Não temos `button_mappings` no nosso fechamento. (acessibilidade)**
Se/quando o SonheMenu ganhar botão de fechar próprio, copiar o bloco de R12 inteiro, incluindo os dois mapeamentos — senão o menu não fecha no controle.

### 6.3 Ordem de teste sugerida

1. A1 isolado (copiar `main_screen_content` com `["100%","100%"]`), sem mais nada. Confirmar que a tela em pixel fixo continua idêntica.
2. A4 e A3 juntos — mudanças cosméticas e de guarda, risco quase nulo.
3. A2 sozinho, só depois de 1 e 2 estarem estáveis em jogo, e com `grid_dimensions [3, 0]` + `#form_button_length`.
4. A6/A5/A7 só quando houver uma segunda tela.

---

## 7. Apêndice — `server_form.json` do Admin Suite, blocos de roteamento na íntegra

```json
{
	"namespace": "server_form",
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
		"size": [ "100%", "100%" ],
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
	"long_form": {
		"type": "panel",
		"size": [ "100%", "100%" ],
		"controls": [
			{
				"hook_cosmetic_ui@cosmetic_ui.main_panel": {
					"layer": 10,
					"bindings": [
						{
							"binding_type": "view",
							"source_property_name": "(not (#title_text - '§c§o§s§m§e§t§i§c§r' = #title_text))",
							"target_property_name": "#visible"
						}
					]
				}
			},
			{
				"hook_shop_ui@split_form.split_long_form": {
					"layer": 10,
					"bindings": [
						{
							"binding_type": "view",
							"source_property_name": "(not (#title_text - '§c§u§s§t§o§m' = #title_text))",
							"target_property_name": "#visible"
						}
					]
				}
			},
			{
				"hook_member_ui@member_ui.main_screen": {
					"layer": 10,
					"bindings": [
						{
							"binding_type": "view",
							"source_property_name": "(not (#title_text - '§m§e§m§b§e§r' = #title_text))",
							"target_property_name": "#visible"
						}
					]
				}
			},
			{
				"hook_admin_ui@admin_ui.main_screen": {
					"layer": 10,
					"bindings": [
						{
							"binding_type": "view",
							"source_property_name": "(not (#title_text - '§g§r§i§d§r' = #title_text))",
							"target_property_name": "#visible"
						}
					]
				}
			},
			{
				"hook_list_ui@list_ui.main_screen": {
					"layer": 10,
					"bindings": [
						{
							"binding_type": "view",
							"source_property_name": "(not (#title_text - '§l§i§s§t§r' = #title_text))",
							"target_property_name": "#visible"
						}
					]
				}
			},
			{
				"default_ui@common_dialogs.main_panel_no_buttons": {
					"$title_panel": "common_dialogs.standard_title_label",
					"$title_size": [ "100% - 15px", 10 ],
					"$title_max_size": [ "100% - 15px", 10 ],
					"size": [ 225, 200 ],
					"$text_name": "#title_text",
					"$title_text_binding_type": "none",
					"$child_control": "server_form.long_form_panel",
					"layer": 2,
					"bindings": [
						{
							"binding_type": "view",
							"source_property_name": "((#title_text - '§l§i§s§t§r' = #title_text) and (#title_text - '§g§r§i§d§r' = #title_text) and (#title_text - '§c§o§s§m§e§t§i§c§r' = #title_text) and (#title_text - '§m§e§m§b§e§r' = #title_text) and (#title_text - '§c§u§s§t§o§m' = #title_text))",
							"target_property_name": "#visible"
						}
					]
				}
			}
		]
	},
	"custom_form": {
		"type": "panel",
		"size": [ "100%", "100%" ],
		"controls": [
			{
				"hook_modal_ui@modal_ui.main_screen": {
					"layer": 10,
					"bindings": [
						{
							"binding_type": "view",
							"source_property_name": "(not (#title_text - '§m§o§d§a§l§r' = #title_text))",
							"target_property_name": "#visible"
						}
					]
				}
			},
			{
				"default_custom_form@common_dialogs.main_panel_no_buttons": {
					"$title_panel": "common_dialogs.standard_title_label",
					"$title_size": [ "100% - 15px", 10 ],
					"$title_max_size": [ "100% - 15px", 10 ],
					"size": [ 225, 200 ],
					"$text_name": "#title_text",
					"$title_text_binding_type": "none",
					"$child_control": "server_form.custom_form_panel",
					"layer": 2,
					"bindings": [
						{
							"binding_type": "view",
							"source_property_name": "(#title_text - '§m§o§d§a§l§r' = #title_text)",
							"target_property_name": "#visible"
						}
					]
				}
			}
		]
	}
}
```

> Nota: o restante de `server_form.json` (`long_form_panel`, `long_form_scrolling_content`, `long_form_dynamic_buttons_panel`, `dynamic_button`, `dynamic_label`, `dynamic_header`, `custom_form_panel`, `custom_form_scrolling_content`, `generated_contents`, `custom_label`, `custom_header`, `custom_toggle`, `custom_slider`, `custom_step_slider`, `custom_dropdown`, `custom_dropdown_content`, `custom_dropdown_radio`, `custom_input`) é **cópia integral do vanilla**, mantida no arquivo porque sobrescrever um `.json` de caminho vanilla **substitui o arquivo inteiro**, não faz merge. Omitir um desses nomes quebraria o ramo de fallback — mais uma falha silenciosa.
>
> Nosso `sonhe_forms.json` **não** copia esses controles e mesmo assim funciona, porque ele é um arquivo de nome novo (`ui/sonhe_forms.json`) registrado no `_ui_defs.json`, e nesse caso o namespace `server_form` é **estendido/mesclado**, não substituído. Essa é a diferença estrutural mais importante entre as duas abordagens: **Admin Suite substitui `ui/server_form.json`; SonheMenu injeta num arquivo separado.** As duas funcionam; a nossa é menos frágil a mudanças de versão do jogo, e é por isso que preservamos `common_dialogs.main_panel_no_buttons` referenciando `server_form.long_form_panel` do vanilla sem redefini-lo.
