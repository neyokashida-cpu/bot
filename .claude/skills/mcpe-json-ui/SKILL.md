---
name: mcpe-json-ui
description: Fundamentos de JSON UI do Minecraft Bedrock (MCPE) — _ui_defs.json, namespaces e override do vanilla, tipos de controle, herança com @, $variáveis, size/anchor/offset, nine-slice e bindings (data/view/collection) com a regra de escopo e ordem. Use quando o pedido for "mexer na UI do jogo", "customizar tela/form/HUD", "criar UI custom com JSON UI", "sobrescrever server_form", "meu binding não funciona" ou "meu controle não aparece".
---

# JSON UI (Bedrock) — fundamentos

Baseado em `Mojang/bedrock-samples` (resource_pack/ui, branch main) e na Bedrock Wiki. JSON UI **não é data-driven documentada oficialmente** como blocos/itens: quase toda regra vem de leitura do vanilla. Quando esta skill diz "confirmar em jogo", significa que não existe fonte oficial — teste antes de afirmar.

Fontes principais:
- https://github.com/Mojang/bedrock-samples/tree/main/resource_pack/ui (vanilla literal)
- https://wiki.bedrock.dev/json-ui/json-ui-intro
- https://wiki.bedrock.dev/json-ui/json-ui-documentation
- https://wiki.bedrock.dev/json-ui/dynamic-content-generation
- https://wiki.bedrock.dev/json-ui/modifying-server-forms

## 1. Registro de arquivos: `ui/_ui_defs.json`

Todo arquivo de UI do seu RP precisa estar listado aqui, senão é simplesmente ignorado:

```json
{
    "ui_defs": [
        "ui/meu_forms.json",
        "ui/meu_grid.json"
    ]
}
```

O `_ui_defs.json` de packs diferentes é **mesclado**, não substituído (verificado na prática: um pack que registra só o próprio arquivo não apaga o registro dos outros). Existe também `_global_variables.json` (variáveis `$` globais, também mesclado).

Não é necessário copiar `ui/server_form.json` do vanilla pra sobrescrever coisas dele — basta um arquivo próprio declarando o **mesmo namespace**.

## 2. Namespace e override do vanilla

```json
{
    "namespace": "server_form",

    "long_form_panel": {
        "type": "panel",
        "controls": [ /* ... */ ]
    }
}
```

Regras:
- `namespace` é o primeiro par do arquivo. Referências entre arquivos usam `namespace.controle`.
- Declarar um controle com o mesmo `namespace` + mesmo nome do vanilla **substitui** o controle vanilla inteiro (não faz merge de propriedades). Se você quer só acrescentar, use `modifications` (seção 8).
- O override é por controle. Sobrescrever `long_form_panel` não sobrescreve `long_form`; sobrescrever nenhum dos dois é possível "pela metade" — controles top-level do mesmo arquivo/namespace entram juntos.
- Redefinir um controle que o vanilla declara com `@` (ex.: vanilla tem `"long_form@common_dialogs.main_panel_no_buttons"`) como um `"long_form"` de `"type": "panel"` **funciona** — existe pack publicado fazendo exatamente isso.
- **Ordem dos resource packs importa**: com dois packs declarando o mesmo namespace/controle, quem está **no topo da lista** do mundo ganha. Se seu override "não pega", verifique se outro pack (mobília, HUD, texture pack de UI) também mexe no mesmo namespace antes de suspeitar do seu JSON.

Nomes de arquivo não têm relação com namespace. Evite `meu_forms.json` declarando `server_form` e `meu_grid.json` declarando `meu_forms` — isso já causou confusão real em debug.

## 3. Tipos de controle

| type | Uso |
|---|---|
| `panel` | container simples, sem visual próprio |
| `image` | desenha uma textura (`texture`, `nineslice_size`, `uv`, `uv_size`) |
| `label` | texto (`text`, `color`, `font_size`, `font_type`) |
| `button` | botão com `default_control`/`hover_control`/`pressed_control` + `button_mappings` |
| `stack_panel` | empilha filhos (`orientation`: `vertical`/`horizontal`); suporta `factory` |
| `grid` | malha de itens gerados por `grid_item_template` + `collection_name` |
| `input_panel` | painel que captura input/foco |
| `scroll_view` | área rolável (na prática use `common.scrolling_panel`) |
| `screen` | tela raiz (`@common.base_screen` + `$screen_content`) |
| `factory` | instancia um controle escolhido por id em runtime (`control_ids`) |
| `custom` | renderer nativo (`renderer`: `progress_bar_renderer`, `gradient_renderer`, `hover_text_renderer`, ...) |
| `collection_panel` | container que suporta `factory` sobre uma collection |

## 4. Herança com `@`

```json
{
    "namespace": "meu_ui",

    "botao_base@common_buttons.light_text_button": {
        "size": [ "100%", 30 ],
        "$pressed_button_name": "button.form_button_click"
    },

    "botao_verde@meu_ui.botao_base": {
        "$default_button_texture": "textures/ui/meu/tile_verde"
    }
}
```

- `nome@namespace.controle` = copia tudo do pai e aplica o que você escreveu por cima.
- Dentro de `controls`, o nome do filho também pode herdar: `{ "linha@meu_ui.botao_base": {} }`.
- `@` sem namespace (`"filho@botao_base"`) resolve no namespace do arquivo atual.
- Referência com `@` na frente do valor (`"long_form": "@server_form.long_form"` em `control_ids`) significa "instancie esse controle".

## 5. `$variáveis`

```json
{
    "meu_botao@common_buttons.light_text_button": {
        "$default_button_texture": "textures/ui/meu/tile",
        "$hover_button_texture": "textures/ui/meu/tile",
        "$pressed_button_texture": "textures/ui/meu/tile",
        "$locked_button_texture": "textures/ui/meu/tile",
        "$border_visible": false,
        "$default_state_border_visible": false,
        "$hover_state_border_visible": false,
        "$pressed_state_border_visible": false,
        "$locked_state_border_visible": false
    }
}
```

Escopo real:
- `$var` definida num controle **propaga para todos os descendentes**. Comprovado no vanilla: `light_button_assets` define `$default_button_texture|default`, um filho lê e repassa como `$new_ui_button_texture`, e o neto `button_image` usa em `"texture": "$new_ui_button_texture"`.
- `"$var|default": valor` = usa esse valor **só se ninguém acima já definiu**. Logo, valor herdado do pai vence o `|default` do vanilla.
- `$var` **não** atravessa para outro controle por referência de nome: ela flui pela árvore de instanciação, não pelo arquivo.
- Variáveis **não** são bindings. `$titulo` é resolvido na montagem da UI; `#titulo` é dado do jogo em runtime. Não misture.

Reskin de botão: o padrão canônico da Mojang (`transparent_content_button` em `ui_template_buttons.json`) passa as **quatro** texturas de estado **no próprio nó `@`** que estende `light_text_button`/`light_content_button`, junto com os flags de borda. Definir no pai funciona por propagação, mas esquecer `$locked_button_texture` ou os `*_border_visible` deixa a moldura de foco vanilla aparecendo.

## 6. `size`, `anchor`, `offset`

```json
{
    "exemplo": {
        "type": "panel",
        "size": [ "100% - 4px", "100%c" ],
        "anchor_from": "top_left",
        "anchor_to": "top_left",
        "offset": [ 2, 0 ],
        "layer": 2
    }
}
```

Unidades de `size`:

| Valor | Significado |
|---|---|
| `40` | 40 pixels de UI |
| `"100%"` | 100% do **pai** naquele eixo |
| `"100% - 4px"` | percentual do pai menos pixels (aritmética permitida) |
| `"100%c"` | relativo aos **filhos** (children) — cresce com o conteúdo |
| `"60%x"` | percentual do **próprio outro eixo** (x aqui) |
| `"default"` | tamanho natural do controle (texto, textura) |
| `"fill"` | ocupa o espaço sobrando no `stack_panel` |

Regras que quebram layout na prática:
- Filho com `%` dentro de pai de tamanho `0` = tamanho `0`. O `main_screen_content` vanilla é `"size": [0, 0]` — se você ancora uma tela custom `70%x75%` dentro dele, ela mede zero. Sobrescreva com `["100%", "100%"]` ou dê tamanho absoluto ao filho.
- `"100%c"` num container cujos filhos ainda não existem (grid com 0 itens) resolve para `0` — nada é desenhado.
- Combinar pai `100%c` (depende dos filhos) com filho `%` (depende do pai) é dependência circular: resultado tipicamente `0`.
- `anchor_from` é o ponto do **pai**, `anchor_to` é o ponto do **filho**. Valores: `top_left`, `top_middle`, `top_right`, `left_middle`, `center`, `right_middle`, `bottom_left`, `bottom_middle`, `bottom_right`.
- `offset` é aplicado depois da âncora, em pixels.
- `layer` decide quem desenha na frente (maior = na frente), dentro do mesmo pai.
- `visible: false` ainda ocupa espaço em `stack_panel`/`grid`. Pra remover do layout use `ignored: true` (ou `"ignored": "(not $flag)"`).

## 7. Texturas e nine-slice

Duas formas, e a do vanilla é a segunda:

```json
{
    "moldura": {
        "type": "image",
        "texture": "textures/ui/meu/panel_frame",
        "nineslice_size": [ 8, 8, 8, 8 ],
        "size": [ "100%", "100%" ]
    }
}
```

```json
// textures/ui/meu/panel_frame.json — metadado, fica ao lado do PNG
{
    "nineslice_size": 8,
    "base_size": [ 32, 32 ]
}
```

- A chave correta no controle `image` é **`nineslice_size`** (sem underscore entre "nine" e "slice"). `nine_slice_size` **não existe** e é silenciosamente ignorada — erro comum e difícil de ver, porque a textura continua desenhando, só esticada.
- `nineslice_size` aceita int (borda igual nos 4 lados) ou `[left, top, right, bottom]`.
- `base_size` deve ser o tamanho real em pixels do PNG. `nineslice_size` está na **mesma unidade** (pixels da textura original).
- O vanilla **nunca** declara nine-slice no UI JSON: usa só o `.json` irmão do PNG (`button_borderless_light.json` = `{"nineslice_size": 1, "base_size": [4,4]}`; `dialog_background_opaque.json` = `{"nineslice_size": 4, "base_size": [16,16]}`). Prefira esse caminho: é metadado da textura, vale em todo lugar que ela for usada.
- **Precedência** entre o `.json` irmão e a chave no controle `image`: não há documentação. Se você precisa dos dois, confirme em jogo.
- Bordas maiores que o destino distorcem: `nineslice_size: 100` numa textura de 1254px desenhada num tile de ~48px de tela pede 200px de borda em 48px de espaço. Texturas de UI vanilla são de 4 a 16px.
- PNG sem canal alpha (colortype 2, RGB) **carrega e desenha**, mas fica 100% opaco — cantos arredondados e transparência são impossíveis. Todo o vanilla de UI é RGBA (colortype 6). Exporte PNG-32.

## 8. `modifications` (patch em vez de substituir)

Quando você quer só acrescentar a um controle vanilla:

```json
{
    "namespace": "server_form",

    "long_form": {
        "modifications": [
            {
                "array_name": "bindings",
                "operation": "insert_back",
                "value": [
                    { "binding_name": "#title_text" },
                    {
                        "binding_type": "view",
                        "source_property_name": "((#title_text - 'meu_form:') = #title_text)",
                        "target_property_name": "#visible"
                    }
                ]
            }
        ]
    }
}
```

Operações: `insert_front`, `insert_back`, `insert_before`/`insert_after` (com `control_name`), `replace`, `remove`. `array_name` costuma ser `bindings`, `controls` ou `button_mappings`.

## 9. Bindings

Três coisas diferentes chamadas "binding":

**Data binding** — traz um dado do jogo para o property bag do controle:

```json
{
    "bindings": [
        {
            "binding_name": "#form_button_texture",
            "binding_name_override": "#texture",
            "binding_type": "collection",
            "binding_collection_name": "form_buttons"
        }
    ]
}
```

**View binding** — calcula uma propriedade a partir do que **já está** no property bag:

```json
{
    "bindings": [
        {
            "binding_type": "view",
            "source_property_name": "(not ((#texture = '') or (#texture = 'loading')))",
            "target_property_name": "#visible"
        }
    ]
}
```

**Collection details** — injeta o contexto do item atual da collection (é isso que faz o clique saber em qual índice clicou):

```json
{
    "bindings": [
        { "binding_type": "collection_details", "binding_collection_name": "form_buttons" }
    ]
}
```

### Campos

| Campo | O que faz |
|---|---|
| `binding_name` | nome do dado de origem (`#algo`) fornecido pelo engine |
| `binding_name_override` | com que nome esse dado entra no property bag deste controle |
| `binding_type` | `global`, `view`, `collection`, `collection_details`, `none` |
| `binding_collection_name` | nome da collection (obrigatório em `collection`/`collection_details`) |
| `binding_condition` | `always`, `always_when_visible`, `visible`, `once`, `none`, `visibility_changed` |
| `source_control_name` | lê o property bag de **outro** controle (por nome) |
| `resolve_sibling_scope` | permite que `source_control_name` resolva um irmão, não só ancestral |
| `source_property_name` | expressão a avaliar (view binding) |
| `target_property_name` | propriedade a escrever (`#visible`, `#text`, `#texture`, ...) |

`binding_condition` **não tem default documentado**. `always_when_visible`/`visible` só atualizam enquanto o controle está visível — o que cria deadlock num controle que começa invisível e depende do próprio binding para aparecer. Nesse caso use `"binding_condition": "always"` no **data** binding. Isso é comportamento observado, não documentado: confirme em jogo.

### Linguagem de expressão

| Operador | Exemplo |
|---|---|
| `+` | `('Total: ' + #valor)`, `(#a + 1)` |
| `-` | `"100% - 69px"`, `(#index - 13)`, `(#texto - ' meu')` |
| `*`, `/` | `(#str * 1)` (truque de string→número) |
| `=`, `<>` | `(#texture = '')` |
| `<`, `>`, `<=`, `>=` | `(#count > 0)` |
| `not` | `(not (#texture = ''))` |
| `and`, `or` | `(not ((#texture = '') or (#texture = 'loading')))` |
| `?:` | `((#count > 0) ? 'sim' : 'nao')` |

**Subtração de string** remove a primeira ocorrência da substring. Os idiomas canônicos:

```
"contém":     (not ((#title_text - 'marcador') = #title_text))
"não contém": ((#title_text - 'marcador') = #title_text)
"vários":     (not ((#title_text - 'form_1' - 'form_2') = #title_text))
```

Parentize **cada operação binária**. Não há documentação de precedência no parser; 100% dos exemplos oficiais escrevem `((X - 'sub') = X)` com o par interno. Escrever `(X - 'sub' = X)` é risco de agrupamento errado — nunca vi fonte confirmando ou negando o comportamento, então trate parênteses explícitos como obrigatórios.

Caracteres não-ASCII, incluindo `§` (U+00A7, bytes `C2 A7` em UTF-8), funcionam dentro de `source_property_name` — a Wiki usa `'§z'` de propósito como marcador invisível. O que **não** está documentado é se `#title_text` chega ao binding com os códigos `§` preservados ou normalizados; se um marcador feito de `§` não funcionar, teste primeiro com um marcador ASCII (`'meu_form:'`) para isolar.

### REGRA DE ESCOPO (a que mais quebra UI)

**Um `binding_type: "view"` não lê propriedades globais da tela. Ele lê apenas o property bag do próprio controle** (ou do controle apontado por `source_control_name`).

Então para usar `#title_text` (que é global) numa condição, o **mesmo controle** precisa importar o dado antes:

```json
{
    "meu_ramo@common_dialogs.main_panel_no_buttons": {
        "bindings": [
            { "binding_name": "#title_text" },
            {
                "binding_type": "view",
                "source_property_name": "(not ((#title_text - 'meu_form:') = #title_text))",
                "target_property_name": "#visible"
            }
        ]
    }
}
```

**A ordem dentro do array importa.** Os bindings são processados na ordem declarada e cada view binding é avaliado contra o estado atual do property bag — inclusive valores escritos por bindings anteriores do mesmo array. Prova no vanilla (`dynamic_button > image`): primeiro o `collection` binding escreve `#texture` via `binding_name_override`, e só depois o view binding lê `#texture` (o nome sobrescrito, não `#form_button_texture`). Inverter a ordem mantém o bug.

Alternativa: declarar `{ "binding_name": "#title_text" }` num ancestral e nos filhos usar `"source_control_name": "nome_do_ancestral"`.

Sintoma clássico da omissão: a expressão avalia com string vazia, `('' - 'marcador') = ''` é **true**, e o ramo que devia esconder fica visível enquanto o outro fica invisível — os dois travados no estado errado ao mesmo tempo.

## 10. Conteúdo dinâmico: factory vs grid

São mecanismos **mutuamente exclusivos**. Varredura dos 208 arquivos de `resource_pack/ui` do vanilla: 73 controles `"type": "grid"`, **zero** com a chave `factory`.

**Factory** vive em `stack_panel`/`collection_panel`, usa `control_ids` e conta itens por `#collection_length`:

```json
{
    "long_form_dynamic_buttons_panel": {
        "type": "stack_panel",
        "size": [ "100% - 4px", "100%c" ],
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

**Grid** usa `grid_item_template` + `collection_name`, e conta itens por `#maximum_grid_items`:

```json
{
    "container_grid": {
        "type": "grid",
        "grid_rescaling_type": "horizontal",
        "size": [ "100%", "default" ],
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

Regras de grid tiradas do vanilla:
- **`grid_dimensions` e `grid_rescaling_type` nunca coexistem** (0 casos em 73 grids). `grid_dimensions: [cols, rows]` = malha estática. `grid_rescaling_type: "horizontal"` = número de colunas **derivado** de (largura do grid / largura do item), linhas crescem; nesse modo não se declara `grid_dimensions`. Um terceiro caminho é `grid_dimension_binding`.
- **Item de grid tem tamanho absoluto em pixels.** `chest.chest_grid_item` é 18x18, `grid_item_for_recipe_book` é `[18,18]`, containers usam 32x32. Item com largura em `%` do grid, junto de `grid_rescaling_type: "horizontal"`, é dependência circular — o grid precisa da largura do item pra calcular colunas e o item precisa do grid.
- **Grid dentro de scrolling panel vai embrulhado.** O vanilla passa um panel intermediário `["100%", "100%c"]` como `$scrolling_content` e deixa o grid em `["100%", "default"]`:

```json
{
    "scroll_grid_panel@common.crafting_root_input_panel": {
        "type": "input_panel",
        "size": [ "100%", "100%c" ],
        "controls": [ { "grid@crafting.scroll_grid": {} } ]
    },
    "recipe_book_scroll_panel@crafting.scroll_panel": {
        "$scrolling_content": "crafting.scroll_grid_panel",
        "$collection_name": "recipe_book"
    }
}
```

- Cada filho gerado **não herda bindings de collection de graça**: quem lê valor da collection declara `"binding_type": "collection"` + `"binding_collection_name"` explicitamente. O índice para o clique vem do `collection_details` no controle do botão (o mesmo que tem `$pressed_button_name`).
- `#collection_index` existe e é o índice do controle na collection.

## 11. Caso concreto: `server_form` (ActionFormData / ModalFormData)

Árvore vanilla (`resource_pack/ui/server_form.json`):

```
third_party_server_screen@common.base_screen
  $screen_content = server_form.main_screen_content
    main_screen_content            panel, size [0,0]
      server_form_factory          type factory
        long_form  -> @server_form.long_form     (ActionFormData)
        custom_form -> @server_form.custom_form  (ModalFormData)

long_form@common_dialogs.main_panel_no_buttons   size [225,200], $child_control = long_form_panel
  long_form_panel                  stack_panel vertical
    scrolling_panel@common.scrolling_panel
      $scrolling_content = long_form_scrolling_content
        main_label                 label, text "#form_text"
        long_form_dynamic_buttons_panel   stack_panel + factory "buttons"
          dynamic_button           stack_panel horizontal 100%x32
            panel_name > image     32x32, ícone
            form_button@common_buttons.light_text_button   size ["fill", 32]
```

Bindings/collections que **realmente existem** nessa tela:

| Nome | Tipo |
|---|---|
| `#title_text` | global |
| `#form_text` | global |
| `#submit_text` | global |
| `#submit_button_visible` | global |
| `#form_button_contents` | contagem da collection `form_buttons` |
| `#form_button_text` | collection `form_buttons` |
| `#form_button_texture` | collection `form_buttons` |
| `#form_button_texture_file_system` | collection `form_buttons` |
| `#custom_form_length` | contagem da collection `custom_form` |
| `#custom_dropdown_length` | contagem da collection `custom_dropdown` |

Grep de `#form_[a-z_]*` em todos os 208 arquivos de UI vanilla retorna **só** os cinco `#form_*` acima. **`#form_button_length` não existe.** `#maximum_grid_items` é propriedade genérica de `type: "grid"`, nunca fornecida pelo `server_form`. Um `binding_name` inexistente é **no-op silencioso**: o `binding_name_override` nunca é preenchido e a contagem fica 0.

Padrão de tela custom por marcador no título (o BP prefixa algo no `.title()`, o RP escolhe o ramo):

```json
{
    "namespace": "server_form",

    "long_form": {
        "type": "panel",
        "size": [ "100%", "100%" ],
        "controls": [
            {
                "ramo_custom@meu_ui.tela_custom": {
                    "layer": 10,
                    "bindings": [
                        { "binding_name": "#title_text" },
                        {
                            "binding_type": "view",
                            "source_property_name": "(not ((#title_text - 'meu_form:') = #title_text))",
                            "target_property_name": "#visible"
                        }
                    ]
                }
            },
            {
                "ramo_default@common_dialogs.main_panel_no_buttons": {
                    "$title_panel": "common_dialogs.standard_title_label",
                    "$title_size": [ "100% - 15px", 10 ],
                    "$title_max_size": [ "100% - 15px", 10 ],
                    "size": [ 225, 200 ],
                    "$text_name": "#title_text",
                    "$title_text_binding_type": "none",
                    "$child_control": "server_form.long_form_panel",
                    "layer": 2,
                    "bindings": [
                        { "binding_name": "#title_text" },
                        {
                            "binding_type": "view",
                            "source_property_name": "((#title_text - 'meu_form:') = #title_text)",
                            "target_property_name": "#visible"
                        }
                    ]
                }
            }
        ]
    }
}
```

Notas desse padrão:
- Os dois ramos precisam do data binding `#title_text` **antes** do view binding, cada um no próprio array (seção 9).
- Reproduzir o ramo default fielmente ao vanilla (`$title_panel`, `$title_size`, `$text_name`, `$title_text_binding_type: "none"`, `$child_control`) é o que faz o form normal continuar funcionando.
- `main_screen_content` vanilla é `size [0,0]`. Se a tela custom usa `%`, sobrescreva `main_screen_content` com `["100%","100%"]` **ou** dê tamanho absoluto à tela custom.
- O marcador precisa ser **idêntico** no BP e no RP. Renomear marcador exige reimplantar os dois lados juntos: BP roda no servidor, RP no cliente, e eles se desatualizam de forma independente. Para migração, aceite os dois: `(not ((#title_text - 'novo:' - 'antigo:') = #title_text))`.
- `ModalFormData` cai em `custom_form`, árvore separada. Sobrescrever `long_form` não afeta ele.

## 12. Erros comuns (sintoma → causa)

**Controle não aparece de jeito nenhum (nem o fundo)**
- View binding lendo dado global sem o data binding correspondente antes no mesmo array → expressão avalia com valor vazio e `#visible` vira false. Causa nº 1 de UI invisível.
- Pai com `size [0,0]` (ou `100%c` sem filhos) e filho em `%` → tamanho zero.
- Referência `@namespace.controle` que não resolve → controle descartado. Confira o namespace certo (não o nome do arquivo).
- Arquivo não listado em `ui/_ui_defs.json`.

**Controle aparece, mas sempre visível / sempre invisível independente da condição**
- Falta de parênteses internos na subtração de string: use `((X - 'sub') = X)`, não `(X - 'sub' = X)`.
- `binding_condition` `visible`/`always_when_visible` num controle que começa invisível → deadlock. Teste `always`.
- Comparação de string com valor que na verdade não chega igual (códigos `§`, espaços). Teste com marcador ASCII.

**Binding nunca dispara / valor sempre vazio**
- `binding_name` que não existe no engine → no-op silencioso, sem erro. Confirme o nome grepando o vanilla, não invente.
- Falta `binding_type: "collection"` + `binding_collection_name` ao ler valor de collection.
- View binding lendo o nome original em vez do `binding_name_override` (ex.: leia `#texture`, não `#form_button_texture`, depois do override).
- Ordem invertida: view binding declarado antes do data binding que ele consome.

**Grid vazio**
- Contagem não preenchida: `#maximum_grid_items` sem binding válido, ou usando `#collection_length` (que é de factory, não de grid).
- `factory` declarada dentro de `type: "grid"` → não existe; grid usa `grid_item_template`. Chave dentro de `factory` é `control_ids`, nunca `control_name`.
- `grid_dimensions` + `grid_rescaling_type` juntos → estratégias de layout contraditórias.
- Item de grid com tamanho em `%` sob `grid_rescaling_type` → 0 colunas.
- Grid direto como `$scrolling_content` sem o panel `100%c` intermediário → altura 0.

**Textura esticada / sem cantos**
- Chave `nine_slice_size` (inválida) em vez de `nineslice_size`; ou falta o `.json` irmão do PNG.
- `nineslice_size` maior que o destino em pixels.
- PNG sem canal alpha → retângulo opaco, sem transparência.

**Override do vanilla não pega**
- Outro resource pack declara o mesmo namespace e está acima na ordem do mundo.
- Você sobrescreveu um controle-filho mas o pai que o instancia é outro (ex.: mudar `long_form_panel` sem mudar `long_form`).
- Duas versões do mesmo pack no cache do cliente (pack entregue por download de servidor): o cliente monta a árvore da versão que o servidor declarar. Limpe o `packcache` e reentre.
- Substituição não é merge: se você redeclarou o controle, propriedades que você não escreveu **desapareceram**. Use `modifications` se a intenção era acrescentar.

**Botão fica com aparência vanilla**
- Texturas de estado passadas só parcialmente (falta `$locked_button_texture`).
- Moldura de foco (`border@common_buttons.focus_border`, `textures/ui/focus_border_white`) não é afetada por `$*_button_texture` — desligue com `$border_visible: false` e os quatro `$*_state_border_visible: false`.
- O botão que você vê não é o seu: se a tela custom não está sendo instanciada, você está olhando o `dynamic_button` vanilla.

## 13. Debug em jogo

JSON UI não dá erro visível por padrão. Ative **Content Log** + **Content Log GUI** em Configurações > Criador: controles rejeitados no parse e `@extend` que não resolveu aparecem lá.

Testes que isolam causa (aplique um por vez):

1. **A árvore é instanciada?** Ponha um `label` com `text` literal (sem binding) como primeiro filho do controle sob suspeita. Se não aparecer, o problema é override/referência, não binding.
2. **O binding é a causa?** Troque o view binding por `"source_property_name": "(1 = 1)"` ou ponha `"visible": true` fixo. Se aparecer, a causa é a expressão/escopo.
3. **O dado chega?** `label` com `bindings: [{ "binding_name": "#title_text" }]` e `"text": "#title_text"`. Compare com um segundo label **sem** o data binding — se o primeiro mostra e o segundo não, escopo confirmado.
4. **É encoding?** Troque o marcador por ASCII puro nos dois lados.
5. **É layout?** Dê tamanho absoluto em pixels e `layer` alto ao controle. Se aparecer, era dimensional.
6. **É o pack certo?** Limpe o cache de packs do cliente e confirme a versão do manifest que foi baixada.
