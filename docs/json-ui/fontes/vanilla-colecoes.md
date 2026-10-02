# Bindings de coleção — corpus vanilla 1.26.44 (Tarefa B)

Corpus: `c:/Users/Desktop/Documents/Nova pasta/assets/assets/resource_packs/vanilla/ui/`
(207 arquivos `.json`). Todo caminho abaixo é relativo a essa raiz.

## 0. Aviso importante sobre o padrão `#null` do addon

O enunciado da tarefa descreve o par-âncora `{"binding_name":"#null","binding_type":"collection",...}` +
`{"binding_name":"#null","binding_type":"collection_details",...}`. **Esse literal `#null` não existe em
nenhum arquivo do corpus vanilla** — confirmado por grep exaustivo (`grep -rn "#null" ui/` → 0 ocorrências).
confidence: **confirmado**.

`#null` é um idioma do próprio pack `ADDONS/SonheMenu_RP` (usado em `ui/sonhe_grid.json` e documentado em
`docs/json-ui/fontes/addon-ui1.md:906/925`, `sonhe-atual.md:112-141`, `vanilla-serverform.md:1403`). O doc
`vanilla-serverform.md:1403` já registrou isso: *"O par de âncoras `#null` extra (collection + collection_details)
é adição do pack, sem precedente vanilla — o `dynamic_button` põe `collection_details` só no botão, não em
cada folha."* Esta tarefa confirma essa conclusão de forma independente, com a evidência bruta abaixo, e
descreve a regra real observada no vanilla (que é sobre `binding_collection_name` explícito, não sobre um
binding-name mudo `#null`).

## 1. Contagens brutas (grep em `ui/`, recursivo, 207 arquivos)

| termo buscado | ocorrências (linhas) | arquivos distintos |
|---|---|---|
| `collection_name` (substring bruta, inclui `binding_collection_name`) | 3211 | 117 |
| — dos quais, chave direta `"collection_name":` (propriedade de controle) | 235 | — |
| — dos quais, `"binding_collection_name":` (dentro de `bindings[]`) | 2238 | — |
| `collection_details` (substring bruta) | 1194 | — |
| — dos quais, `"binding_type": "collection_details"` literal | 301 | — |
| — dos quais, `"binding_type": "$xxx_collection_details"` (via variável) | 695 | — |
| — chave direta `"collection_details":` como propriedade de controle (fora de `binding_type`) | **0** | — |
| `binding_name_override` | 2965 | — |
| `collection_index` | 68 | — |

Arquivos com mais `collection_name`: `store_common.json` (585), `pdp_screen.json` (261), `persona_sdl.json` (228),
`resource_packs_screen.json` (184), `store_promo_timeline_screen.json` (170). Arquivos com mais
`binding_name_override`: `store_common.json` (234), `settings_sections/general_section.json` (176),
`play_screen.json` (176). confidence: **confirmado** (contagens de grep literal).

Achado relevante: `"collection_details"` **nunca** aparece como propriedade direta de um controle no vanilla
(sempre é valor de `binding_type`, literal ou via `$variável`). `"collection_name"` **pode** ser propriedade
direta de controle (235 casos) — é isso que marca um controle como raiz de coleção (ver §4).

## 2. `binding_type: "collection"` — regra real de `binding_collection_name`

Varredura de todas as 803 ocorrências de `"binding_type": "collection"` em `ui/**/*.json`, olhando uma janela
de ±6 linhas ao redor de cada uma: **100% delas (803/803) têm `"binding_collection_name"` explícito dentro do
mesmo objeto de binding.** Não existe, no corpus vanilla, nenhum binding `collection` que dependa de herança
implícita do nome da coleção a partir de um ancestral. confidence: **confirmado** (varredura programática,
sem exceções).

Ou seja: para LER um campo do item de uma coleção (`binding_name` → `binding_name_override`), o binding
sempre carrega seu próprio `binding_collection_name` — seja um literal (`"container_items"`) seja uma
`$variável` herdada normalmente do controle-pai (herança padrão de `$variável` do JSON UI, não é mecanismo
especial de coleção). Isso vale tanto para irmãos quanto para descendentes.

Exemplo (`ui_common.json:5256-5263`, `item_lock_cell_image`, controle-folha simples, sem `collection_details`
nenhum na árvore):
```json
"item_lock_cell_image": {
  "type": "image",
  "texture": "textures/ui/cell_image_lock",
  "bindings": [
    {
      "binding_name": "#item_lock",
      "binding_name_override": "#visible",
      "binding_type": "collection",
      "binding_collection_name": "$item_collection_name"
    }
  ]
}
```
Este controle é um **irmão direto** de outros que carregam `collection_details` dentro de `common.container_item`
(ver §3) e funciona sozinho, sem repetir nenhuma âncora — porque `binding_collection_name` já resolve tudo que
esse binding precisa.

## 3. `binding_type: "collection_details"` — para que serve, e quando É repetido entre irmãos

`collection_details` (sozinho, sem `binding_name`/`binding_name_override`) não lê um campo — ele **ancora o
controle como unidade endereçável dentro da coleção** (índice próprio, seleção, foco). Ele aparece tipicamente
UMA VEZ por controle "unidade" (um botão, um `custom` item-renderer), não em cada binding de exibição.

### 3.1 Caso REAL de repetição entre irmãos (não-descendentes)

Em `common.container_item` (`ui_common.json:5079-5196`), a lista `"controls"` tem estes filhos diretos, todos
irmãos entre si:
- `item_cell` → (descendo) `item` → `$item_renderer@$item_renderer` (default = `common.item_renderer`)
- `item_selected_image@common.slot_selected`
- `item_button_ref@$button_ref` (default = `common.container_slot_button_prototype`)
- `item_lock_cell_image@common.item_lock_cell_image`
- `container_item_lock_overlay@common.container_item_lock_overlay`

`item_renderer` (`ui_common.json:3876-3891`, dentro do ramo `item_cell`) declara sua própria âncora:
```json
"item_renderer": {
  "type": "custom",
  "renderer": "inventory_item_renderer",
  "bindings": [
    { "binding_type": "collection_details", "binding_collection_name": "$item_collection_name" },
    { "binding_name": "#item_renderer_data", "binding_type": "collection",
      "binding_collection_name": "$item_collection_name", "binding_condition": "$item_renderer_binding_condition" }
    // ...mais bindings "collection"
  ]
}
```
`container_slot_button_prototype` (`ui_common.json:4778-4847`, usado no ramo **irmão** `item_button_ref`)
declara a **mesma âncora de novo**, independentemente:
```json
"container_slot_button_prototype": {
  "type": "button",
  "bindings": [
    { "binding_type": "collection_details", "binding_collection_name": "$item_collection_name",
      "binding_condition": "once" },
    { "binding_type": "$focus_id_binding_type", "binding_name": "#focus_identifier",
      "binding_name_override": "#focus_identifier", "binding_collection_name": "$item_collection_name",
      "binding_condition": "once" }
    // ...mais 4 bindings de foco, todos com binding_collection_name repetido
  ]
}
```
`item_renderer` e `container_slot_button_prototype` são dois ramos **irmãos** (ambos filhos de
`container_item`, em sub-ramos diferentes — `item_cell > item > $item_renderer` vs `item_button_ref`). Nenhum
herda a âncora do outro: **cada um declara `collection_details` por conta própria**, apontando para o mesmo
`$item_collection_name`. confidence: **confirmado** (JSON literal, dois arquivos-fonte no mesmo control,
mesma linha-base `ui_common.json`).

### 3.2 Caso REAL de NÃO-repetição (irmão simples que só lê dado, sem precisar da âncora)

Ainda dentro de `container_item`, `item_lock_cell_image` (§2 acima) e os dois filhos de
`container_item_lock_overlay` (`ui_common.json:5223-5251`, `container_item_lock_yellow`/`container_item_lock_red`)
são irmãos de `item_renderer` e de `container_slot_button_prototype`, mas **nenhum dos três declara
`collection_details`** — só usam `binding_type: "collection"` com `binding_collection_name` explícito, porque
tudo que precisam é ler um campo (`#item_lock`, `#item_lock_in_inventory`, `#item_lock_in_slot`) e aplicar em
`#visible`. Não precisam de identidade de índice/seleção, só do valor.

### 3.3 Caso REAL de descendente que NÃO repete a âncora (porque nem precisa dela)

`server_form.json:146-230`, control `dynamic_button` (usado por `long_form_dynamic_buttons_panel`, que tem
`collection_name: "form_buttons"` — a raiz de coleção). `dynamic_button` tem dois filhos diretos, irmãos entre si:

- `panel_name` → `image` (ícone): bindings `"binding_type": "collection"` com `binding_collection_name: "form_buttons"`
  explícito, **sem `collection_details` em nenhum ponto dessa sub-árvore**.
- `form_button@common_buttons.light_text_button`: bindings = **só uma entrada**:
  ```json
  "bindings": [
    { "binding_type": "collection_details", "binding_collection_name": "form_buttons" }
  ]
  ```
  O texto do botão não vem desse binding — vem de `$button_text_binding_type: "collection"` +
  `$button_text_grid_collection_name: "form_buttons"`, repassados como `$variável` para dentro do template
  `light_text_button`.

Dentro de `light_text_button` (`ui_template_buttons.json:319-523`), o descendente final que de fato lê o texto
é `new_ui_binding_button_label` (`ui_template_buttons.json:482-523`), vários níveis abaixo de `form_button`
(via `$button_state_panel` → `button_content` → `$button_type_panel`):
```json
"new_ui_binding_button_label": {
  "type": "label",
  "text": "$button_text",
  "$button_text_collection_details|default": "none",
  "bindings": [
    { "binding_type": "$button_text_collection_details",
      "binding_collection_name": "$button_text_grid_collection_name",
      "binding_collection_prefix": "$button_text_collection_prefix" },
    { "binding_type": "$button_text_binding_type", "binding_condition": "$button_binding_condition",
      "binding_collection_name": "$button_text_grid_collection_name",
      "binding_name": "$button_text", "binding_name_override": "$button_text" }
  ]
}
```
Como `dynamic_button` **não** passa `$button_text_collection_details`, o default `"none"` prevalece: o
primeiro binding fica desativado (`binding_type: "none"`) — este descendente **não repete** a âncora
`collection_details` do seu ancestral `form_button`. Ele só precisa do segundo binding (`collection`), que
já carrega seu próprio `binding_collection_name` (herdado por `$variável`, não por herança de binding).
confidence: **confirmado**.

### 3.4 Regra exata consolidada

Não existe, no vanilla, um mecanismo de "herança de binding entre controles" — nem descendente nem irmão
herdam bindings uns dos outros. O que parece herança é **herança de `$variável`** (mecanismo padrão do JSON
UI: filho herda o valor resolvido de uma `$variável` do pai/ancestral em `controls[]`, sujeito a override —
ver skill `mcpe-json-ui`). Com isso:

- **`binding_type: "collection"` (ler um campo)** — nunca depende de `collection_details` estar presente em
  nenhum lugar da árvore. Basta que o próprio binding tenha `binding_collection_name` (literal ou `$variável`
  herdada normalmente). É por isso que controles-irmãos simples (§3.2, §2) nunca precisam repetir nada além
  do próprio binding com seu `binding_collection_name`.
- **`binding_type: "collection_details"` (ancorar a UNIDADE endereçável — índice, foco, seleção)** — é
  colocado **uma vez por controle que atua como unidade independente da coleção** (um `button`, um `custom`
  item-renderer). Quando duas dessas unidades vivem em ramos **irmãos** dentro do mesmo controle-coleção
  (ex.: `item_renderer` e `container_slot_button_prototype`, ambos sob `container_item`), **cada uma declara
  sua própria `collection_details`** — não há propagação lateral entre irmãos, confirmado em §3.1.
- Um controle **descendente de outro que já tem `binding_type: "collection"` ou `collection_details`** não
  herda esses bindings automaticamente só por estar abaixo na árvore — ele só "parece" não precisar repetir
  quando (a) não precisa da semântica de `collection_details` (só quer ler um valor, caso §3.3) ou (b) o
  ancestral repassa o nome da coleção via `$variável` normal, e o próprio descendente declara seu binding
  `collection`/`collection_details` referenciando essa `$variável` herdada (o que technically ainda é "declarar
  de novo", só que sem precisar saber o literal da coleção).
- Resumindo para o caso do addon: o padrão `{"binding_name":"#null", binding_type: collection}` +
  `{"binding_name":"#null", binding_type: collection_details}` repetido em cada folha **não tem
  correspondência vanilla** como âncora-tolerante-a-ruído; o vanilla resolve o mesmo problema (múltiplas
  sub-partes visuais lendo da mesma coleção) com `binding_collection_name` explícito em cada binding de
  leitura, e `collection_details` reservado só para o(s) controle(s) que precisam de identidade de índice
  própria (tipicamente botões/renderers). confidence: **provável** (é a leitura mais direta da evidência,
  mas não há como testar em runtime a partir do JSON estático).

## 4. `collection_name` como propriedade direta de controle (raiz de coleção)

235 controles no corpus declaram `"collection_name": "<literal ou $variável>"` diretamente (não dentro de
`bindings[]`). Isso marca o controle como raiz de uma coleção, usado por dois mecanismos distintos observados:

**(a) Expansão automática por template** — tipos `grid` (com `grid_item_template`) e `collection_panel` (com
bloco `"factory": {...}`) usam `collection_name` para saber de qual fonte de dados gerar N cópias do template.
Exemplo (`chest_screen.json:30-38`):
```json
"small_chest_grid": {
  "type": "grid",
  "grid_dimensions": [ 9, 3 ],
  "grid_item_template": "chest.chest_grid_item",
  "collection_name": "container_items"
}
```

**(b) Filhos nomeados manualmente + `collection_index` fixo** — ver §5. Exemplo
(`store_common.json:5430-5479`, `screenshots_grid`): `"collection_name": "$offer_collection_name"` no pai,
e cada um dos 4 filhos nomeados (`screenshot_1`..`screenshot_4`) leva `"collection_index": 0..3` fixo.

Para controles do tipo `collection_panel` com bloco `"factory"` (ex.: `icon_overlay_position_factory`,
`store_common.json:749-790`), os filhos gerados pela factory **não** herdam `$variável` automaticamente
como filhos normais herdariam — precisam de `"factory_variables": [...]` explícito listando cada `$variável`
que deve ser repassada (`store_common.json:766-775`, `847-859`). Isso é o caso mais próximo, no vanilla, de
"preciso repetir explicitamente porque a árvore normal de herança não se aplica" — mas é herança de
`$variável` através de fronteira de factory, não de binding entre irmãos comuns. confidence: **confirmado**
(estrutura `factory_variables` está no JSON, o comportamento de não-herança automática por trás dela é
conhecimento de engine — **suspeita** quanto ao "porquê", **confirmado** quanto ao "o quê").

## 5. `collection_index` — dois contextos distintos, catalogados

68 ocorrências totais. Dois usos **completamente diferentes** do mesmo nome de chave:

### 5.1 Propriedade de controle, override de índice fixo (55 ocorrências, sem `#`)

Usado em filhos **nomeados manualmente** (não gerados por template/factory) de um controle-pai com
`collection_name`, para dizer "eu sou o item de índice N dessa coleção" — desativando a expansão automática
por item e fixando este controle-folha (e sua sub-árvore) num slot específico.

Exemplo (`store_common.json:5442-5477`, dentro de `screenshots_grid`, pai com `collection_name:
"$offer_collection_name"`):
```json
{ "screenshot_1@common_store.one_key_art_screenshot_panel": { "collection_index": 0 } },
{ "screenshot_2@common_store.one_key_art_screenshot_panel": { "collection_index": 1 } },
{ "screenshot_3@common_store.one_key_art_screenshot_panel": { "collection_index": 2 } },
{ "screenshot_4@common_store.one_key_art_screenshot_panel": { "collection_index": 3 } }
```
Outro exemplo, `chat_settings_menu_screen.json:150-211` (7 filhos manuais de `chat_color_dropdown_content`,
que tem `"collection_name": "font_colors"` em `chat_settings_menu_screen.json:142`), cada um com
`"collection_index": 0` a `6`. Mesmo padrão em `persona_popups.json:583` (`collection_index: 0`) e `:653`
(`collection_index: 1`), filhos nomeados de `create_persona_choice_stack` (`collection_name:
"persona_type_toggles_collection"`, linha 569).

Arquivos com esse uso: `chat_settings_menu_screen.json` (7), `choose_realm_screen.json` (3),
`csb_sections/content_section.json` (4), `pdp_screenshots_section.json` (3), `persona_popups.json` (2),
`persona_sdl.json` (6), `realms_slots_screen.json` (3), `store_common.json` (9), `store_filter_menu_screen.json`
(6), `store_promo_timeline_screen.json` (7). confidence: **confirmado**.

Regra: só faz sentido em filho de um controle com `collection_name` próprio (literal ou `$variável`) — não
funciona sem esse contexto de coleção ancestral. Os bindings de leitura da sub-árvore (`binding_type:
"collection"`) continuam precisando do seu próprio `binding_collection_name` normalmente (§2); o que
`collection_index` muda é qual índice da coleção esses bindings resolvem, no lugar do índice automático
que um item gerado por template/factory teria.

### 5.2 Chave dentro de `"property_bag"` de controle `type: "custom"` (13 ocorrências, com `#`)

Contexto totalmente diferente: controles `"type": "custom"` (renderer C++ nativo, ex.:
`"renderer": "inventory_item_renderer"`) recebem um bloco `"property_bag"` com chaves prefixadas `#`, lidas
pelo renderer nativo — não é binding JSON UI. Exemplo (`cartography_screen_pocket.json:19-28`):
```json
"chest_item_renderer": {
  "type": "custom",
  "renderer": "inventory_item_renderer",
  "size": [ 16, 16 ],
  "property_bag": {
    "#item_id_aux": 3538944,
    "#collection_name": "inventory_tab",
    "#collection_index": 0
  }
}
```
Arquivos: `cartography_screen_pocket.json` (2), `furnace_screen_pocket.json` (2), `inventory_screen_pocket.json`
(1), `loom_screen_pocket.json` (3), `smithing_table_2_screen_pocket.json` (2), `stonecutter_screen_pocket.json`
(2), `trade_2_screen_pocket.json` (1). Todos em telas "_pocket" (UI de bolso legada, 9-slot). confidence:
**confirmado** que a sintaxe existe; **suspeita** quanto ao comportamento exato do renderer nativo (fora do
JSON, não auditável por este método).

## 6. Resumo executivo da regra pedida

1. Não existe "herança de binding" no vanilla — cada controle declara os bindings que precisa, sempre com
   `binding_collection_name` próprio quando é `binding_type: "collection"`.
2. `collection_details` não é uma âncora "gate" que outros bindings dependem para funcionar — é ela própria
   um binding independente, usado quando o controle precisa ser uma unidade endereçável (índice/foco/seleção)
   da coleção. Controles-irmãos que só exibem um valor **não precisam dela** (§2, §3.2). Controles-irmãos que
   **também** são unidades endereçáveis (outro botão, outro custom-renderer) **repetem-na cada um por si**
   (§3.1) — não há propagação lateral nem vertical automática desse binding específico.
3. O padrão `#null` + par-âncora repetido do addon é uma convenção própria do pack, sem precedente vanilla
   direto — o vanilla resolve o problema equivalente com `binding_collection_name` explícito por binding.
