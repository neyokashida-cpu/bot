# Scroll (`scrolling_panel` / `scroll_view`) — corpus vanilla 1.26.44 (Tarefa A)

Corpus: `c:/Users/Desktop/Documents/Nova pasta/assets/assets/resource_packs/vanilla/ui/`.
Metodologia: grep literal por `scrolling_panel` e `scroll_view` em todo `ui/**/*.json`, leitura direta dos
3+ arquivos mais completos. Todo trecho citado é copiado literalmente do corpus (caminho + linha).

Contagem bruta: `scrolling_panel|scroll_view` → **358 ocorrências em 91 arquivos** (grep recursivo,
case-insensitive). confidence: confirmado.

---

## 1. Onde vive o mecanismo — a fábrica em `ui_common.json` (namespace `common`)

Achado central: **`"type": "scroll_view"` literal só aparece em 2 arquivos do corpus inteiro**:
`ui_common.json` (onde o tipo é definido) e um único override em `persona_popups.json`. confidence: confirmado
(grep exaustivo de `"type": "scroll_view"`, 0 outras ocorrências em 91 arquivos que citam scroll).

Ou seja: **nenhuma tela vanilla declara `"type": "scroll_view"` diretamente**. Toda tela compõe scroll
herdando de `@common.scrolling_panel` (ou de um wrapper de namespace local construído em cima dele, ex.
`world_templates.common_scrolling_panel`). Essa é a regra prática nº 1.

Cadeia de herança completa, todas em `ui_common.json`:

```
scroll_view_control (type: scroll_view)          — ui_common.json:4391
  └─ usado por: scrolling_panel_base (type: input_panel)   — ui_common.json:4607
       └─ usado por: scrolling_panel (type: panel)         — ui_common.json:4627
            └─ scrolling_panel_with_offset@common.scrolling_panel   — ui_common.json:4722
            └─ container_scroll_panel@common.scrolling_panel_with_offset — ui_common.json:5336
                 └─ mapped_scroll_panel@common.container_scroll_panel    — ui_common.json:4729
```

`scrolling_panel_base` (`ui_common.json:4607-4625`) é o nó que de fato instancia o `scroll_view`:

```json
"scrolling_panel_base": {
  "type": "input_panel",
  "$scroll_view_name|default": "scroll_view",
  "controls": [
    { "$scroll_view_name@common.scroll_view_control": {
        "allow_scroll_even_when_content_fits": "$allow_scroll_even_when_content_fits" } }
  ]
}
```

`scrolling_panel` (`ui_common.json:4627-4720`) não cria um `scroll_view` sozinho — ele instancia **dois**
`scrolling_panel_base` filhos, um para mouse e um para touch, e liga um ou outro via `ignored`:

```json
"controls": [
  { "scroll_touch@common.scrolling_panel_base": { "ignored": "(not $touch)", ... "$use_touch_mode": true, ... } },
  { "scroll_mouse@common.scrolling_panel_base": { "ignored": "$touch", "size": "$scrolling_pane_size", "offset": "$scrolling_pane_offset" } }
]
```
(`ui_common.json:4680-4718`)

Isso significa: **toda variável de tamanho/offset do scroll existe em par** — a versão normal e a versão
`_touch` (`$scroll_view_port_size` vs `$scroll_view_port_size_touch`, etc.). Se você só ajusta a variável
normal e esquece a `_touch`, o modo touch usa o **default de fábrica** (`[ "100%", "100%" ]`), não o seu valor
— ver §4.

---

## 2. Os 3 exemplos mais completos lidos

### 2.1 `select_world_screen.json` — lista dinâmica dentro de scroll (linhas 259-329)

```json
"select_world_panel@common.scrolling_panel": {
  "size": [ "100%", "100%" ],
  "$scroll_view_port_size|default": [ "100% - 2px", "100% -2px" ],
  "$scroll_view_port_offset|default": [ 2, 2 ],
  "$scroll_view_port_size_touch|default": [ "100% - 2px", "100% - 2px" ],
  "$scroll_view_port_offset_touch|default": [ 2, 2 ],
  "$scrolling_content": "select_world.select_world_list",
  "$show_background": false
},

"select_world_list@common.vertical_stack_panel": {
  "size": [ "100%", "100%c" ],
  ...
  "controls": [
    { "realms_world_label@common_dialogs.standard_title_label": {...} },
    { "realms_world_list@play.realms_world_item_grid": { "$grid_name": "#realms_world_item_grid_dimension", ... } },
    { "padding_middle@common.empty_panel": { "size": [ "100%", "2px" ] } },
    { "local_world_label@common_dialogs.standard_title_label": {...} },
    { "local_world_list@play.local_world_item_grid": {...} },
    { "padding_end@common.empty_panel": { "size": [ "100%", "2px" ] } }
  ]
}
```

O conteúdo rolável (`$scrolling_content`) é um `vertical_stack_panel` de tamanho `[ "100%", "100%c" ]`
contendo **dois grids dinâmicos empilhados** (mundos de Realms + mundos locais), cada um vindo de
`play_screen.json`. A base comum dos dois grids (`play_screen.json:115-121`):

```json
"world_item_grid_base": {
  "type": "grid",
  "size": [ "100%", "default" ],
  "layer": 1,
  "anchor_to": "top_left",
  "anchor_from": "top_left"
}
```

e a especialização com coleção dinâmica (`play_screen.json:4357-4367`):

```json
"local_world_item_grid@play.world_item_grid_base": {
  "$world_item_grid_template|default": "play.local_world_item",
  "grid_item_template": "$world_item_grid_template",
  "grid_dimension_binding": "#local_world_item_grid_dimension",
  "collection_name": "local_worlds",
  "bindings": [ { "binding_name": "#local_world_item_grid_dimension" } ]
}
```

### 2.2 `world_templates_screen.json` — grid dinâmico dentro de scroll (linhas 638-660, 858-912)

```json
"world_template_item_grid": {
  "type": "grid",
  "size": [ "100%", "default" ],
  "layer": 1,
  "anchor_to": "top_left",
  "anchor_from": "top_left",
  "grid_item_template": "world_templates.world_template_item",
  "grid_dimension_binding": "#world_template_item_grid_dimension",
  "collection_name": "world_templates",
  ...
}
```

Esse grid é envolvido por um wrapper de scroll local ao namespace, construído em cima de
`common.scrolling_panel` (linhas 858-891):

```json
"common_scrolling_panel@common.scrolling_panel": {
  "layer": 1,
  "$scrolling_pane_size": [ "100% - 1px", "100%" ],
  "$scrolling_content": "$scrolling_content",
  "$scroll_size": [ 5, "100% - 4px" ],
  "$show_background": false,
  "anchor_from": "top_right",
  "anchor_to": "top_right"
},

"scrolling_offsets@world_templates.common_scrolling_panel": {
  "size": [ "100% - 4px", "100%" ],
  "max_size": [ 280, "100%" ],
  "offset": [ 2, 0 ],
  "anchor_from": "top_middle",
  "anchor_to": "top_middle"
},

"common_scroll_pane": {
  "type": "panel",
  "anchor_from": "top_left",
  "anchor_to": "top_left",
  "size": [ "100% - 4px", "100%c" ],
  "offset": [ 2, 0 ]
},

"template_scroll_panel@world_templates.common_scroll_pane": {
  "controls": [ { "world_template_screen_content_stack_panel@world_templates.world_template_screen_content_stack_panel": {} } ]
}
```

Padrão repetido: o **conteúdo** que fica dentro do scroll usa `size: [ "100% - Npx", "100%c" ]` — largura
fixa/percentual, altura **sempre `100%c`** (content-driven). Já o **grid** dinâmico lá dentro usa
`size: [ "100%", "default" ]` — largura 100%, altura `default` (auto pelo próprio grid).

### 2.3 `store_data_driven_screen.json` (namespace `store_layout`) — scroll com override de touch/PS4 (linhas 8-140)

```json
"sdl_scrolling_content_panel": {
  "type": "panel",
  "$sdl_scrolling_content_panel_size|default": [ "100%", "100%c" ],
  "size": "$sdl_scrolling_content_panel_size",
  "controls": [ { "sdl_scrolling_content_stack@store_layout.sdl_scrolling_content_stack": {} } ]
},

"sdl_scrolling_section@common.scrolling_panel": {
  "anchor_from": "top_left",
  "anchor_to": "top_left",
  "size": [ "100%", "100%" ],
  "$scrolling_content": "store_layout.sdl_scrolling_content_panel",
  "$scroll_size": [ 4, "100% - 8px" ],
  "$scroll_bar_left_padding_size": [ 0, 0 ],
  "$scroll_bar_right_padding_size": [ 3, "100%" ],
  "$show_background": false
},

"character_creator_sdl_scroll_section@store_layout.sdl_scrolling_section_panel": {
  "variables": [
    { "requires": "$is_ps4",
      "$scroll_view_control_anchor": "top_left",
      "$scroll_view_control_size": [ "100%", "100% - 25px" ],
      "$scroll_view_port_panel_size": [ "100%", "100% + 25px" ],
      "$scroll_view_port_size": [ "100%", "100% - 25px" ],
      "$scroll_view_port_clips_children": false }
  ]
}
```

Esse exemplo mostra o caso "plataforma especial": no PS4, o viewport é encurtado em 25px e
`clips_children` é desligado explicitamente — evidência de que `clips_children: true` é o padrão em todo o
resto do corpus (é o `|default: true` em `ui_common.json:4301`) e só é desligado quando a intenção é
deixar conteúdo vazar de propósito (barra de navegação sobreposta).

---

## 3. Receita — lista/grid rolável com coleção dinâmica

Baseado nos 3 exemplos acima, o padrão vanilla para "lista/grid rolável com dados dinâmicos" é sempre:

1. Defina o **conteúdo** (o que rola) como um controle próprio — `stack_panel` (lista) ou `grid` (grade) —
   com `collection_name` (ou `$collection_name`) e, se for grid, `grid_item_template` +
   `grid_dimension_binding`. Ex.: `world_template_item_grid` (`world_templates_screen.json:638-660`).
2. Dê a esse controle `size: [ "100%", "100%c" ]` se for `stack_panel`, ou `size: [ "100%", "default" ]`
   se for `type: "grid"` — nunca uma altura fixa em px nem `"100%"` da tela.
3. Envolva esse controle com `@common.scrolling_panel` (direto, ou via um wrapper de namespace como
   `world_templates.common_scrolling_panel`), passando-o como `$scrolling_content`.
4. Ajuste `$scroll_view_port_size` / `$scroll_view_port_offset` (e os pares `_touch`) para abrir um
   respiro em px para a barra de rolagem — todos os exemplos subtraem de 2px a 18px do lado da barra
   (`"100% - 2px"`, `"100% - 4px"`, `"100% - 8px"`, `"100% - 18px"` no touch de `container_scroll_panel`).
5. Se precisar de várias seções dentro do mesmo scroll (ex. "Mundos do Realms" + "Mundos locais" em
   `select_world_screen.json`), empilhe vários grids/labels dentro do mesmo `vertical_stack_panel` de
   `100%c` — não crie um `scrolling_panel` por seção.

---

## 4. Armadilhas de tamanho dentro do scroll

| elemento | regra observada | pode ser % | quebra se... | evidência |
|---|---|---|---|---|
| Controle passado em `$scrolling_content` (o conteúdo que rola) | altura **sempre `100%c`** no eixo de rolagem; largura `%`/px fixo | largura sim, altura não (deve ser `%c`) | usar `100%` fixo na altura em vez de `100%c` congela o conteúdo do tamanho do viewport e nada aparece rolável | `select_world_screen.json:270` (`[100%,100%c]`); `store_data_driven_screen.json:11` (`[100%,100%c]`); `world_templates_screen.json:897` (`["100% - 4px","100%c"]`) |
| `grid` dinâmico dentro do scroll | altura sempre `"default"` (auto) | largura `100%` | dar altura fixa/`%` a um `type:"grid"` corta itens que excedem essa altura, já que o grid não expande o pai | `play_screen.json:117` (`["100%","default"]`); `world_templates_screen.json:640` (`["100%","default"]`) |
| `$scroll_view_port_size` / `offset` | inset em **px literal subtraído do %** (`"100% - Npx"`, N de 2 a 18) + offset em px puro (`[1,1]`, `[2,2]`) | a base é `%`, mas sempre com desconto px | usar `100%` puro sem desconto faz o conteúdo/scrollbar desenhar por cima da borda/moldura do painel | `select_world_screen.json:261-264`; `ui_common.json:4723-4726` (`scrolling_panel_with_offset`, `"100% - 8px"`/`offset [1,1]`); `ui_common.json:5343-5346` (`container_scroll_panel`, `"100% - 2px"`/`"100% - 18px"` no touch) |
| `$scroll_size` (largura da trilha/barra) | **sempre px literal** em ambos os defaults (`[4,"100%"]` em `ui_common.json:4649`) e em todo override visto | só o comprimento (2º valor) é `%`; a espessura é sempre px fixo (2 a 5px) | dar `%` à espessura da barra faz ela esticar/afinar junto com a tela — nenhum caso no corpus faz isso | `ui_common.json:4649` (default `[4,"100%"]`); `world_templates_screen.json:862` (`[5,"100% - 4px"]`); `store_data_driven_screen.json:97` (`[4,"100% - 8px"]`) |
| Variáveis `_touch` (`$scroll_view_port_size_touch`, `$scroll_bar_contained_touch`, etc.) | **sempre espelhadas manualmente** ao lado da variável normal | — | esquecer o par `_touch` faz o modo toque cair no default de fábrica (`["100%","100%"]`, offset `[0,0]`), ignorando silenciosamente o layout pensado para mouse | `scrolling_panel` inteiro em `ui_common.json:4627-4720` sempre declara os dois; `select_world_screen.json:261-264` declara os 4 (normal + touch) |
| `clips_children` do viewport (`$scroll_view_port_clips_children`) | default `true` (`ui_common.json:4301`) | é booleano, não %, mas citado aqui por ser a única exceção documentada | só é desligado (`false`) para casos de plataforma especiais, com comentário/contexto explícito (PS4) — desligar sem motivo deixa o conteúdo vazar por cima de outros controles | `store_data_driven_screen.json:111` (`$scroll_view_port_clips_children: false`, dentro de `variables: [{ "requires": "$is_ps4" }]`) |
| Raiz do `scrolling_panel` (`$scrolling_pane_size`) | `100%`/`100% - 1px` do pai, nunca px fixo | sim | dar tamanho fixo à raiz impede o scroll de se adaptar a telas menores (o próprio design é 100% responsivo) | `ui_common.json:4631-4632` (default `["100%","100%"]`); `world_templates_screen.json:860` (`["100% - 1px","100%"]`) |

confidence de toda a tabela: **confirmado** para as linhas com citação de múltiplos arquivos concordando
(conteúdo `100%c`, grid `default`, `$scroll_size` sempre px); **provável** para a leitura de "por que quebra"
(inferida da consistência do padrão, não de um comentário vanilla explícito) — exceto a linha de
`clips_children`, que é **confirmado** porque o próprio arquivo isola o caso com `variables/requires`.

---

## 5. Achado extra (suspeita, não confirmado em jogo)

`persona_popups.json:99-107` faz algo que não aparece em mais nenhum lugar do corpus: sobrescreve
`"type": "scroll_view"` diretamente por cima de `@common.scrolling_panel` (que por padrão é `type: "panel"`):

```json
"popup_content@common.scrolling_panel": {
  "type": "scroll_view",
  "size": [ "100% - 16px", "100% - 64px" ],
  "offset": [ 0, 23 ],
  "$scrolling_pane_offset": [ 0, 0 ],
  "anchor_from": "top_middle",
  "anchor_to": "top_middle",
  "$show_background": false
}
```

Isso troca o tipo da raiz para `scroll_view` enquanto ainda herda os `controls` de `scrolling_panel`
(que internamente criam outro `scroll_view` filho via `scroll_touch`/`scroll_mouse`). Não foi possível
confirmar em jogo se isso é redundante-mas-inofensivo ou gera comportamento duplicado de scroll.
confidence: **suspeita** — não replicar esse padrão sem testar; use `@common.scrolling_panel` sem
sobrescrever `type`, como fazem os outros 89 arquivos.
