# Fonte: addon "ui5" — JSON UI #5 (Custom Textures)

**Caminho analisado:** `c:/Users/Desktop/Downloads/ADDONS EXEMPLOS/ui5/`
**Arquivos lidos (todos):**

| Arquivo | Bytes | Papel |
|---|---|---|
| `ui5/RP/ui/server_form.json` | 15319 | **único** arquivo de UI do pack |
| `ui5/RP/textures/custom_ui/custom_bg.png` + `custom_bg.json` | — | fundo nine-slice do painel/tile |
| `ui5/RP/textures/custom_ui/custom_bg_hover.png` + `custom_bg_hover.json` | — | fundo nine-slice de hover/pressed |
| `ui5/RP/textures/custom_ui/close_button.png` / `close_button_hover.png` | — | ícone do X (sem `.json`, logo **sem** nine-slice) |
| `ui5/RP/manifest.json` | — | RP, `min_engine_version [1,19,60]`, **depende do BP** |
| `ui5/BP/manifest.json` | — | BP, deps `@minecraft/server 1.16.0` + `@minecraft/server-ui 1.3.0`, **depende do RP** |
| `ui5/BP/scripts/main.js` | — | idêntico ao de ui4 exceto `.body("Select Something Here")` |

**NÃO existe** `ui5/RP/ui/_ui_defs.json`.
Referência de vídeo: `"metadata": { "url": "https://youtu.be/E21eNDjtAow" }`.

---

## Resumo

ui5 é o **mesmo esqueleto de ui4 com tema completo por cima**. O `long_form`, o discriminador por título, o `my_super_custom_panel_main` (mosaico de `stack_panel` com `collection_index` 0-3) e o `custom_button` são **byte-a-byte iguais aos de ui4** em quase tudo. Comparei os dois arquivos: as diferenças são exatamente cinco, e todas são de **aparência**, não de mecânica.

O que ui5 acrescenta:

1. **O ramo custom deixa de herdar `common_dialogs.main_panel_no_buttons`.** Vira um `panel` cru onde o autor desenha tudo: fundo, título, corpo, botão de fechar. Isso significa **abandonar a moldura vanilla inteiramente**.
2. **Um botão de fechar próprio**, com `button_mappings` explícito mapeando para `button.menu_exit`.
3. **Um sistema de tema por `$variável` que atravessa a herança** — `$default_button_texture` / `$hover_button_texture` / `$pressed_button_texture` declarados no `custom_button` e consumidos lá embaixo pelo `common_buttons.light_text_button`.
4. **Nine-slice de verdade**, via `.json` ao lado do `.png`.
5. **`#form_text` renderizado** (ui4 ignora).

É a fonte mais próxima do que o SonheMenu quer ser. E é a fonte que mostra o **caminho alternativo** ao que o SonheMenu escolheu: ui5 troca a moldura vanilla por assets custom; o SonheMenu troca a moldura vanilla por retângulos `type: "image"` apontando para texturas vanilla (`textures/ui/Black`, `textures/ui/white_background`) tingidos por `color`. Duas soluções para o mesmo problema.

---

## Tabela de padrões

| # | Padrão | Como ui5 faz | Igual a ui4? | Confidence |
|---|---|---|---|---|
| P1 | Ativar override | `RP/ui/server_form.json`, mesmo caminho do vanilla, sem `_ui_defs.json` | **sim** | confirmado |
| P2 | Escopo | redefine só `long_form`; `long_form_panel` etc. continuam do vanilla | **sim** | confirmado |
| P3 | Discriminador | dois irmãos com `view` em `#visible` sobre `#title_text` | **sim, expressões idênticas** | confirmado |
| P4 | Âncora do binding | `{ "binding_name": "#title_text" }` primeiro | **sim** | confirmado |
| P5 | Ramo vanilla | `@common_dialogs.main_panel_no_buttons` + `$child_control: server_form.long_form_panel` | **sim, literal** | confirmado |
| P6 | Ramo custom | `panel` cru `[322.5, 190]` com 4 filhos desenhados à mão | **NÃO** (ui4 herda o template) | confirmado |
| P7 | Indentação interna | `indent_panel` de `["100% - 16px", "100%"]` envolvendo tudo | **NÃO** (ui4 delega ao template) | confirmado |
| P8 | Fundo | `type: "image"` + `texture: "textures/custom_ui/custom_bg"` + `size: ["100% + 5px", "100% + 5px"]` + `alpha: 0.9` | **NÃO** | confirmado |
| P9 | Nine-slice | `.json` irmão do `.png` com `base_size` + `nineslice_size` | **NÃO** | confirmado |
| P10 | Título | `label` com `font_type: "MinecraftTen"` + `font_size: "large"` | **NÃO** | confirmado |
| P11 | Corpo | `label` lendo `#form_text` | **NÃO** (ui4 ignora `#form_text`) | confirmado |
| P12 | Fechar | `type: "button"` próprio com `button_mappings` → `button.menu_exit` | **NÃO** | confirmado |
| P13 | Tema dos tiles | `$default_button_texture` / `$hover_...` / `$pressed_...` **sem `|default`** no `custom_button` | **NÃO** | confirmado |
| P14 | Cor do label do tile | `[1, 1, 1]` (branco) | **NÃO** (ui4 usa `[0,0,0]`) | confirmado |
| P15 | Layout dos botões | mosaico de `stack_panel` + `collection_index` 0-3 | **sim, literal** | confirmado |
| P16 | Ícone / clique / `collection_details` | trio de bindings + `light_text_button` + `$button_text: "#null"` | **sim, literal** | confirmado |
| P17 | Dependência entre packs | RP e BP se declaram mutuamente por UUID | **NÃO** (ui4 não declara) | confirmado |

---

## Diff exato ui4 → ui5

Estas são **todas** as diferenças entre os dois `server_form.json`:

1. `cutsom_long_form` deixa de ser `@common_dialogs.main_panel_no_buttons` e vira `panel` cru com `size: [322.5, 190]` (ui4: `[322.5, 185]`) e 4 subcontroles novos.
2. Seis controles novos: `my_close_button`, `my_form_body`, `my_form_label`, `my_form_background` (e os aninhados `indent_panel`, `content_stack`).
3. `custom_button` ganha três linhas de tema no topo (`$default_button_texture`, `$hover_button_texture`, `$pressed_button_texture`).
4. O label do tile muda de `"color": [0, 0, 0]` para `"color": [1, 1, 1]`.
5. Indentação de tab (ui4) para 4 espaços (ui5). Cosmético.

**Tudo o mais é idêntico.** Isso é um dado forte: significa que a mecânica de `server_form` (R1–R5, R7, R9–R11 do `addon-ui4.md`) é **estável entre as duas versões de engine** (`1.20.0` em ui4, `1.19.60` em ui5) e não é sensível ao tema.

---

## Regras extraídas

### R1 — Confirmação independente de todas as regras de ui4. `[confirmado]`

`long_form` de ui5, literal:

```json
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
        ...
```

Idêntico a ui4 caractere por caractere (fora indentação). **Duas fontes independentes convergindo na mesma forma = regra dura, não coincidência.**

Em particular: `"size": ["100%", "100%"]` no `long_form` está presente nas duas. O SonheMenu **omite**. `[suspeita]` mantida e reforçada.

### R2 — O ramo custom pode ser um `panel` cru sem nenhuma herança vanilla. `[confirmado]`

```json
{
    "cutsom_long_form": {
        "type": "panel",
        "size": [322.5, 190],
        "layer": 2,
        "controls": [
            {
                "indent_panel": {
                    "type": "panel",
                    "size": ["100% - 16px", "100%"],
                    "controls": [
                        { "my_form_label@server_form.my_form_label": {} },
                        {
                            "my_close_button@server_form.my_close_button": {
                                "offset": [8, -8],
                                "layer": 64
                            }
                        },
                        { "my_form_background@server_form.my_form_background": {} },
                        {
                            "content_stack": {
                                "type": "stack_panel",
                                "size": ["100%", "100%"],
                                "orientation": "vertical",
                                "controls": [
                                    { "padding": { "type": "panel", "size": ["100%", 8] } },
                                    { "my_form_body@server_form.my_form_body": {} },
                                    { "button_panel@server_form.my_super_custom_panel_main": {} }
                                ]
                            }
                        }
                    ]
                }
            }
        ],
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
```

Cinco observações que viram regra:

1. **Sem `anchor_from`/`anchor_to`.** O painel não declara ancoragem. O default centraliza (o pai `long_form` é `["100%","100%"]`). ui4 também não ancora o ramo custom porque o template já fazia.
2. **A ordem dos `controls` NÃO é a ordem de desenho** — `my_form_background` vem em terceiro, depois do label e do botão de fechar, mas ainda fica atrás porque não declara `layer` (default `0`) enquanto o label declara `"layer": 8` e o close `"layer": 64`. **`layer` manda, ordem no array não.** `[confirmado]`
3. **`indent_panel` de `["100% - 16px", "100%"]`** replica manualmente o que `main_panel_no_buttons` fazia via `$panel_indent_size|default: [ "100% - 16px", "100% - 31px" ]` (`.../vanilla/ui/ui_template_dialogs.json`). Quem abandona o template tem de refazer a margem à mão.
4. **`content_stack` começa com um `padding` de `["100%", 8]`.** Espaçador é um `panel` vazio. Não existe `margin`.
5. **Os `bindings` do discriminador ficam no `panel` cru**, exatamente na mesma posição estrutural que ocupavam no controle derivado de ui4. A posição do binding é o que importa, não o tipo do controle.

### R3 — Fundo com `size: ["100% + 5px", "100% + 5px"]` — sangra para fora do pai de propósito. `[confirmado]`

```json
"my_form_background": {
    "type": "image",
    "size": ["100% + 5px", "100% + 5px"],
    "texture": "textures/custom_ui/custom_bg",
    "alpha": 0.9
},
```

O fundo é **maior** que o container. `+5px` compensa a indentação de 16px do `indent_panel` mais a borda do nine-slice, e garante que não sobre fresta.

`alpha: 0.9` — translúcido, não opaco. O mundo aparece por trás.

**Este mesmo controle é reusado em três lugares diferentes com sizes diferentes:**

```json
{ "bg@server_form.my_form_background": { "alpha": 1 } }
```
(dentro do `my_close_button` — sobrescreve o alpha para opaco)

```json
{ "my_form_background@server_form.my_form_background": { "size": ["100% - 22px", "100%"] } }
```
(dentro do `my_form_body` — sobrescreve o size)

→ **Regra:** um controle de tema pequeno e reusável, cujas propriedades são sobrescritas na instanciação, é mais barato que várias definições. `[confirmado]`

### R4 — Nine-slice: `.json` irmão do `.png`, com `base_size` **escalar**. `[confirmado]`

`ui5/RP/textures/custom_ui/custom_bg.json`:

```json
{
    "base_size": 8,
    "nineslice_size": 3
}
```

`ui5/RP/textures/custom_ui/custom_bg_hover.json`: idêntico.

Três fatos:

1. A chave é `nineslice_size`, **uma palavra só**, sem underscore no meio. (O comentário `//3` do `sonhe_grid.json` já lista "a grafia errada de nineslice_size (com underscore no meio)" como proibida — **ui5 confirma a grafia certa**.)
2. `base_size` aqui é um **escalar** (`8`), não um array `[8, 8]`. Textura quadrada. `[confirmado]` que o escalar é aceito; `[suspeita]` que o array também seja, para texturas não-quadradas.
3. `close_button.png` e `close_button_hover.png` **não têm `.json`**. Nine-slice é opt-in: sem o `.json`, a imagem estica uniformemente. Ícones não devem ter `.json`; molduras devem.

O `.png` é referenciado **sem extensão** no JSON UI: `"texture": "textures/custom_ui/custom_bg"`.

### R5 — Tema dos tiles: `$variável` **sem `|default`** para forçar override através da cadeia de herança. `[confirmado — este é o achado mais importante de ui5]`

```json
"custom_button": {
    "$padding|default": [80, 80],
    "$button_size|default": [64, 64],
    "$icon_size|default": [32, 32],

    "$default_button_texture": "textures/custom_ui/custom_bg",
    "$hover_button_texture": "textures/custom_ui/custom_bg_hover",
    "$pressed_button_texture": "textures/custom_ui/custom_bg_hover",

    "type": "panel",
    "size": "$padding",
    ...
```

Note a assimetria deliberada: os três primeiros têm `|default`, os três de textura **não**.

Por quê: o template vanilla `light_button_assets` (`.../vanilla/ui/ui_template_buttons.json`, linha 39) declara:

```json
"light_button_assets@common.button": {
    "$default_button_texture|default": "textures/ui/button_borderless_light",
    "$default_content_alpha|default": 1,
    "$hover_content_alpha|default": 1,
    "$hover_button_texture|default": "textures/ui/button_borderless_lighthover",
    "$pressed_button_texture|default": "textures/ui/button_borderless_lightpressed",
    "$locked_button_texture|default": "textures/ui/disabledButtonNoBorder",
    ...
```

E `light_text_button@light_button_assets` (linha 319) as consome:

```json
{
    "default@$button_state_panel": {
        "$new_ui_button_texture": "$default_button_texture",
        ...
    }
},
{
    "hover@$button_state_panel": {
        "$new_ui_button_texture": "$hover_button_texture",
        ...
    }
},
{
    "pressed@$button_state_panel": {
        "$new_ui_button_texture": "$pressed_button_texture",
        ...
    }
},
```

**Mecanismo:** `$var|default: X` significa "se `$var` já tem valor no escopo, mantenha; senão use X". `custom_button` é o **pai** do `form_button@common_buttons.light_text_button`, então define `$default_button_texture` **sem** `|default` = valor duro. Quando `light_button_assets` roda seu `|default`, a variável já existe → o default é descartado → o botão vanilla desenha a textura do addon.

**Consequências práticas, todas confirmadas por este código:**

- Variáveis `$` **descem** do pai para os filhos através da árvore de `controls` E através da cadeia de herança `@`. Um pai pode retematizar um template vanilla que ele nem instancia diretamente.
- Escrever `"$default_button_texture|default": "..."` no seu controle **não** sobrescreveria nada se o valor já existir acima; escrever sem `|default` sobrescreve. A barra vertical não é decoração.
- `$pressed_button_texture` reusa `custom_bg_hover` — não é preciso ter três texturas.

**Este é o mecanismo de tema mais limpo do corpus e o SonheMenu não usa.**

### R6 — Botão de fechar próprio: `type: "button"` + `default_control`/`hover_control` + `button_mappings` para `button.menu_exit`. `[confirmado]`

```json
"my_close_button": {
    "type": "button",
    "default_control": "default",
    "hover_control": "hover",
    "$default_texture|default": "textures/custom_ui/close_button",
    "$hover_texture|default": "textures/custom_ui/close_button_hover",
    "$alpha|default": 1,
    "$size|default": [16, 16],
    "anchor_from": "top_right",
    "anchor_to": "top_right",
    "size": [14, 14],
    "sound_name": "random.click",
    "controls": [
        {
            "bg@server_form.my_form_background": {
                "alpha": 1
            }
        },
        {
            "default": {
                "type": "image",
                "size": "$size",
                "texture": "$default_texture",
                "alpha": "$alpha"
            }
        },
        {
            "hover": {
                "type": "image",
                "size": "$size",
                "texture": "$hover_texture",
                "alpha": "$alpha"
            }
        }
    ],
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
},
```

Regras dentro deste bloco:

1. **`type: "button"` puro, sem herdar `common.button`.** Escrevendo `button_mappings` à mão você não precisa do template. O `common.button` vanilla faz exatamente isso com `$pressed_button_name` (`.../vanilla/ui/ui_common.json`, linha 44):
```json
"button_mappings": [
  {
    "from_button_id": "button.menu_select",
    "to_button_id": "$pressed_button_name",
    "mapping_type": "pressed"
  },
  {
    "from_button_id": "button.menu_ok",
    "to_button_id": "$pressed_button_name",
    "mapping_type": "focused"
  }
],
```
ui5 só substituiu `$pressed_button_name` por `button.menu_exit` literal.
2. **O par `menu_select`/`pressed` + `menu_ok`/`focused` é obrigatório** para funcionar em toque e em controle/teclado. Um sozinho quebra em uma das plataformas. `[provável]` — o padrão aparece nas duas fontes (`common.button` vanilla e `my_close_button`).
3. **`default_control` e `hover_control` apontam para nomes de filhos.** Sem `pressed_control` aqui — o botão só tem dois estados. Se você declarar `pressed_control: "pressed"` e não existir filho `pressed`, `[suspeita]` o estado simplesmente não desenha (falha silenciosa).
4. **`size: [14, 14]` no botão mas `$size: [16, 16]` nas imagens** — as imagens sangram 1px para cada lado, mesma técnica do `+5px` do fundo.
5. **`sound_name: "random.click"`** — som declarado explicitamente porque não herdou `common.button`.
6. **`"layer": 64` passado na instanciação**, não na definição:
```json
"my_close_button@server_form.my_close_button": {
    "offset": [8, -8],
    "layer": 64
}
```
`offset: [8, -8]` com `anchor_to: "top_right"` empurra o X para fora da borda direita.

### R7 — Título com fonte display: `MinecraftTen` + `font_size: "large"`. `[confirmado]`

```json
"my_form_label": {
    "type": "label",
    "font_type": "MinecraftTen",
    "font_size": "large",
    "anchor_from": "top_left",
    "anchor_to": "top_left",
    "text": "#title_text",
    "layer": 8,
    "offset": [9, -16],
    "bindings": [
        {
            "binding_name": "#title_text"
        }
    ]
},
```

- `font_type: "MinecraftTen"` + `font_size: "large"`. **ui5 NÃO usa `font_scale_factor` nem `backup_font_type`.**
- Contraste com o SonheMenu (`sonhe_grid.json`, `screen_title`), que usa `font_scale_factor: 1.39` + `backup_font_type: "UIFont"` + `offset: [0, -2]` e documenta isso como cópia de `common.minecraftTenLabel`. **Duas rotas válidas.** A de ui5 é mais curta; a do SonheMenu é mais fiel ao vanilla.
- `offset: [9, -16]` com `anchor_to: "top_left"` — Y negativo sobe o título para fora do container, sobre a borda superior.
- Nenhuma `color` declarada → herda `$title_text_color` do tema. **Risco:** em fundo escuro isso pode sumir. O SonheMenu já registrou esse aprendizado no comentário de `screen_title`: *"Branco puro na mao: NAO herdar $title_text_color, que e cinza escuro [0.3,0.3,0.3] e desaparece no preto."* ui5 escapa porque o `custom_bg` dele é claro. **Não copiar `my_form_label` sem forçar `color`.**
- A âncora `{ "binding_name": "#title_text" }` sozinha (sem `view`) — quando o objetivo é só renderizar, um binding puro basta.

### R8 — `#form_text` (o `.body()` do script) renderizado explicitamente. `[confirmado]`

```json
"my_form_body": {
    "type": "panel",
    "anchor_from": "top_middle",
    "size": ["100%", 28],
    "layer": 8,
    "controls": [
        {
            "form_body_text": {
                "type": "label",
                "text": "#form_text",
                "layer": 8,
                "bindings": [
                    {
                        "binding_name": "#form_text"
                    }
                ]
            }
        },
        {
            "my_form_background@server_form.my_form_background": {
                "size": ["100% - 22px", "100%"]
            }
        }
    ]
},
```

- Mesmo padrão do label: `"text": "#form_text"` **e** binding homônimo. Os dois.
- Altura **fixa** `28`, não `"default"`. Sem quebra de linha automática; texto longo é cortado.
- O SonheMenu faz melhor aqui (`screen_body` usa `size: ["100% - 8px", "default"]` + `max_size` = quebra automática). **Manter o do SonheMenu.**
- No `main.js` de ui5: `.body("Select Something Here")` — ui4 tinha `.body("")`. É a razão de existir este controle.

### R9 — Label do tile em branco. `[confirmado]`

```json
{
    "text": {
        "type": "label",
        "text": "#form_button_text",
        "layer": 32,
        "color": [1, 1, 1],
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
```

ui4 tinha `[0, 0, 0]`. Única linha do `custom_button` que mudou além das três texturas. **Trocar o tema do fundo obriga a trocar a cor do texto — não há herança de contraste.**

### R10 — RP e BP declaram dependência mútua por UUID. `[confirmado]`

`ui5/RP/manifest.json`:
```json
"header": { ..., "uuid": "1d36b39b-806c-46ba-bd6c-f04acd33dd51", "version": [0, 0, 1] },
"dependencies": [
    {
        "uuid": "440ac16a-a636-41da-89a4-64edbb06f4f1",
        "version": [0, 0, 1]
    }
]
```

`ui5/BP/manifest.json`:
```json
"header": { ..., "uuid": "440ac16a-a636-41da-89a4-64edbb06f4f1", "version": [0, 0, 1] },
"dependencies": [
    {
        "uuid": "1d36b39b-806c-46ba-bd6c-f04acd33dd51",
        "version": [0, 0, 1]
    },
    { "module_name": "@minecraft/server", "version": "1.16.0" },
    { "module_name": "@minecraft/server-ui", "version": "1.3.0" }
]
```

Referência cruzada exata dos UUIDs de `header`. **ui4 não faz isso** — os manifests de ui4 não têm dependência entre RP e BP.

Efeito: com a dependência, ativar o BP força o RP a estar ativo. Sem ela, o jogador pode ativar só o BP → **o form aparece como lista vanilla, sem nenhum erro**. Este é um vetor de falha silenciosa que vive **fora** do JSON UI. `[confirmado como mecanismo; provável como causa de "sumiu do nada"]`

### R11 — `min_engine_version` baixo não impede o override. `[confirmado]`

ui5 declara `[1, 19, 60]`; ui4 declara `[1, 20, 0]`. Ambos rodam. `min_engine_version` é piso, não trava. Não é fonte de falha silenciosa de UI.

### R12 — `version` do pack é o que fura o cache do cliente. `[provável]`

Os dois packs estão em `[0, 0, 1]`. O SonheMenu está em `[1, 0, 36]` — 36 bumps. Isso indica que o projeto já usa bump de versão como ferramenta de invalidação de cache.
`[suspeita]` relevante para o problema central: se o cliente segurar o RP antigo em cache, você vê a **lista vanilla** com o JSON novo no disco e **zero erro**. Sintoma indistinguível de bug de JSON. Antes de caçar bug de JSON, confirmar que o `version` subiu e que o cliente recarregou.

---

## O que ui5 ensina sobre a **falha silenciosa**

Novos vetores que ui4 não revelava:

| # | Vetor | Mecanismo | Confidence |
|---|---|---|---|
| V1 | BP ativo sem RP ativo | sem `dependencies` cruzada, o RP pode ficar de fora → lista vanilla, log limpo | confirmado (ui5 se protege; ui4 não) |
| V2 | `$variável` sobrescrita com `\|default` por engano | `\|default` não vence um valor já existente → sua textura é ignorada e a vanilla desenha | confirmado (R5) |
| V3 | `default_control`/`hover_control`/`pressed_control` apontando para filho inexistente | o estado não desenha; o botão continua clicável e invisível | suspeita |
| V4 | Ordem no array de `controls` confundida com ordem de desenho | `layer` manda; um fundo sem `layer` cobre o conteúdo | confirmado (R2.2) |
| V5 | Label sem `color` explícita em fundo escuro | `$title_text_color` vanilla é escuro → texto invisível, não ausente | confirmado (documentado no próprio SonheMenu) |
| V6 | `nineslice_size` grafado errado no `.json` da textura | a textura vira stretch simples ou não carrega; nada no log de UI | provável |
| V7 | Cache do cliente com RP antigo | JSON novo no disco, UI velha na tela | provável |

---

## Aplicação no SonheMenu

### O que ui5 valida no que o SonheMenu já faz

- **Grafia `nineslice_size`** (uma palavra). O `sonhe_grid.json` proíbe explicitamente a grafia com underscore no meio; ui5 confirma qual é a certa. Os `.json` do SonheMenu em `textures/ui/sonhe/` (`panel_frame.json`, `tile_frame.json`) devem seguir o mesmo formato de `custom_bg.json`.
- **Ramo custom como `panel` cru** (`grid_screen` é `type: "panel"` com fundo próprio). ui5 faz exatamente isso. Rota validada.
- **Fundo com sangria** — SonheMenu usa `"size": ["100% + 2px", "100% + 2px"]` no `panel_edge`; ui5 usa `+5px`. Mesma técnica.
- **`layer` explícito em cada camada** (`panel_edge: 0`, `panel_bg: 1`, `grid_content: 2`, labels `3`). ui5 faz `0/8/64`. Ambos corretos; o do SonheMenu é mais legível.
- **Faces de botão como filhos nomeados** (`default`/`hover`/`pressed` em `tile_button`). ui5 faz `default`/`hover` em `my_close_button`. Mesma mecânica.
- **`text` + binding homônimo** nos labels. Idêntico.

### Divergências e oportunidades — ranqueadas

**D1 — `long_form` sem `size`.** `[suspeita, custo zero]`
Reforçada por ui5: **as duas fontes** declaram `"size": ["100%", "100%"]`. O SonheMenu omite. Primeira coisa a testar.

**D2 — SonheMenu não usa o mecanismo de `$default_button_texture`.** `[oportunidade confirmada]`
O SonheMenu monta hover/pressed com três `panel` de faces (`face_default`, `face_hover`, `face_pressed`), cada um com dois `image` de `textures/ui/Black` / `textures/ui/white_background` tingidos. São ~60 linhas de JSON para o que ui5 resolve em três:

```json
"$default_button_texture": "textures/ui/sonhe/tile_frame",
"$hover_button_texture": "textures/ui/sonhe/tile_frame_hover",
"$pressed_button_texture": "textures/ui/sonhe/tile_frame_hover",
```

**Mas** o SonheMenu escolheu deliberadamente "tema dark sem asset custom" (comentário `//` de `sonhe_grid.json`), e `tile_button@common.button` não passa por `light_button_assets` — herda `common.button` direto, que **não** define `$default_button_texture`. Então a rota de ui5 só se aplica se trocar a base para `@common_buttons.light_text_button` (como o `row_button` do fallback já faz).
**Recomendação:** não trocar agora. Registrar como caminho de simplificação futura, para quando os assets `tile_frame.png` forem adotados de fato.

**D3 — Nenhuma dependência cruzada entre `SonheMenu_RP` e `SonheMenu_BP`.** `[confirmado como lacuna]`
`ADDONS/SonheMenu_RP/manifest.json` tem `header.uuid = b71a84eb-d21e-4460-bb7c-eb9758d1ede4` e **nenhum bloco `dependencies`**. ui5 declara dependência mútua por UUID; ui4 não declara e é o exemplo mais frágil.
Se o BP puder rodar sem o RP no servidor, o `/menu` vira lista vanilla sem nenhum erro. **Isto encaixa exatamente na descrição do problema central ("cai na lista vanilla, SEM nenhum [UI][error]").**
Ação sugerida (fora do escopo de edição deste trabalho — só registro): adicionar em `SonheMenu_BP/manifest.json`
```json
"dependencies": [
    { "uuid": "b71a84eb-d21e-4460-bb7c-eb9758d1ede4", "version": [1, 0, 36] }
]
```
Atenção: com `version` exata, **todo bump do RP obriga bump correspondente aqui**, senão o pack não resolve. É uma troca: mais segurança, mais manutenção.

**D4 — Rota de instalação: `_ui_defs.json` vs. mesmo caminho.** `[confirmado como diferença]`
**Nem ui4 nem ui5 têm `_ui_defs.json`.** Os dois colocam o arquivo em `RP/ui/server_form.json`. O SonheMenu usa `_ui_defs.json` + dois arquivos com nomes próprios.
A rota do SonheMenu é legítima e tem vantagem real (separar `long_form` do layout em dois arquivos), mas adiciona um ponto de falha silenciosa exclusivo: **se o `_ui_defs.json` não for lido, os dois arquivos não existem para o engine e não há JSON inválido para logar.**
Mitigação de menor custo, mantendo a separação em dois arquivos: renomear `ui/sonhe_forms.json` → `ui/server_form.json` (path do vanilla, dispensa `_ui_defs.json` para ele) e deixar no `_ui_defs.json` apenas `ui/sonhe_grid.json`. Assim o override do `long_form` — a peça crítica — passa a não depender do `_ui_defs.json`.

**D5 — Discriminador com `§` vs. ASCII.** `[suspeita]`
ui4 e ui5 usam `'Custom Form'` — ASCII puro, com espaço, sem código de formatação. SonheMenu usa `'§d§r§e§a§m§r'` — seis códigos `§` encadeados.
Além disso os dois exemplos usam **igualdade exata** no ramo custom (`(#title_text = 'Custom Form')`), enquanto o SonheMenu usa `(not ((#title_text - '...') = #title_text))`.
Duas variáveis independentes num mesmo lugar crítico. Bisseção sugerida: primeiro trocar só o marcador por ASCII mantendo a expressão; depois trocar só a expressão mantendo o marcador.

**D6 — Espaçamento por `panel` vazio.** `[confirmado; SonheMenu já faz]`
ui5: `{ "padding": { "type": "panel", "size": ["100%", 8] } }`
SonheMenu: `{ "gap_a": { "type": "panel", "size": [ "100%", 4 ] } }`
Mesma técnica. Nada a mudar.

**D7 — Botão de fechar.** `[oportunidade]`
O SonheMenu **não tem** botão de fechar no `grid_screen`. Como o ramo custom abandona `main_panel_no_buttons`, também abandonou o X do vanilla. ui5 mostra o padrão pronto e portável — R6 acima. Copiar `my_close_button` trocando as texturas por um `image` de `textures/ui/white_background` tingido (para manter "sem asset custom") e mantendo os dois `button_mappings` para `button.menu_exit`.

### Ordem de ataque recomendada ao problema central

1. **Confirmar que o RP chegou ao cliente** (D3 + V7): bump de `version`, checar o ContentLog, confirmar RP ativo no mundo. Isso elimina os vetores que não são JSON.
2. **Adicionar `"size": ["100%", "100%"]` ao `long_form`** (D1). Uma linha.
3. **Forçar os dois ramos**: trocar as expressões por `(1 = 0)` / `(1 = 1)` para provar se o problema é discriminador ou layout.
4. **Se for discriminador**: bisseção D5 (marcador ASCII, depois igualdade exata no lugar de `not`+subtração).
5. **Se for layout**: `grid` → `list_screen` (fallback já documentado) → topologia estilo-ui4 com `collection_index` literal em `stack_panel` aninhados (ver `addon-ui4.md`, seção D3).
6. Só depois: consolidar rota de instalação (D4) e botão de fechar (D7).

---

## Apêndice A — controles de tema de ui5 na íntegra

```json
"my_close_button": {
    "type": "button",
    "default_control": "default",
    "hover_control": "hover",
    "$default_texture|default": "textures/custom_ui/close_button",
    "$hover_texture|default": "textures/custom_ui/close_button_hover",
    "$alpha|default": 1,
    "$size|default": [16, 16],
    "anchor_from": "top_right",
    "anchor_to": "top_right",
    "size": [14, 14],
    "sound_name": "random.click",
    "controls": [
        { "bg@server_form.my_form_background": { "alpha": 1 } },
        { "default": { "type": "image", "size": "$size", "texture": "$default_texture", "alpha": "$alpha" } },
        { "hover":   { "type": "image", "size": "$size", "texture": "$hover_texture",   "alpha": "$alpha" } }
    ],
    "button_mappings": [
        { "from_button_id": "button.menu_select", "to_button_id": "button.menu_exit", "mapping_type": "pressed" },
        { "from_button_id": "button.menu_ok",     "to_button_id": "button.menu_exit", "mapping_type": "focused" }
    ]
},

"my_form_body": {
    "type": "panel",
    "anchor_from": "top_middle",
    "size": ["100%", 28],
    "layer": 8,
    "controls": [
        { "form_body_text": { "type": "label", "text": "#form_text", "layer": 8,
            "bindings": [ { "binding_name": "#form_text" } ] } },
        { "my_form_background@server_form.my_form_background": { "size": ["100% - 22px", "100%"] } }
    ]
},

"my_form_label": {
    "type": "label",
    "font_type": "MinecraftTen",
    "font_size": "large",
    "anchor_from": "top_left",
    "anchor_to": "top_left",
    "text": "#title_text",
    "layer": 8,
    "offset": [9, -16],
    "bindings": [ { "binding_name": "#title_text" } ]
},

"my_form_background": {
    "type": "image",
    "size": ["100% + 5px", "100% + 5px"],
    "texture": "textures/custom_ui/custom_bg",
    "alpha": 0.9
},
```

## Apêndice B — `custom_button` de ui5 (só o topo difere de ui4)

```json
"custom_button": {
    "$padding|default": [80, 80],
    "$button_size|default": [64, 64],
    "$icon_size|default": [32, 32],

    "$default_button_texture": "textures/custom_ui/custom_bg",
    "$hover_button_texture": "textures/custom_ui/custom_bg_hover",
    "$pressed_button_texture": "textures/custom_ui/custom_bg_hover",

    "type": "panel",
    "size": "$padding",
    "controls": [
        {
            "main_ui": {
                "type": "panel",
                "size": "$button_size",
                "controls": [
                    {
                        "panel_name": {
                            "type": "panel",
                            "size": "$button_size",
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
                                        "size": "$icon_size",
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
                                        "color": [1, 1, 1],
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
                            "size": "$button_size",
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
```

`my_super_custom_panel_main` de ui5 é **idêntico** ao de ui4 (transcrito na íntegra em `addon-ui4.md`, regra R7).
