# Investigação JSON UI Vanilla — Cliente 1.26.44

Corpus autoritativo: `c:/Users/Desktop/Documents/Nova pasta/assets/assets/resource_packs/vanilla/ui/`
Texturas: `c:/Users/Desktop/Documents/Nova pasta/assets/assets/resource_packs/vanilla/textures/ui/`

Dimensões de PNG lidas byte a byte do chunk IHDR (script Python local) e cruzadas com um segundo
decoder independente (`System.Drawing.Bitmap` via PowerShell) para os casos citados como
"confirmado". Cores de pixel também lidas pelos dois decoders quando relevante.

---

## TAREFA A — Texturas de tema (fundo de painel sem asset custom)

| Textura | Dimensão real | Cor sólida (pixel central) | Borda? | Sidecar `.json`? | Usada em (exemplo real) | confidence |
|---|---|---|---|---|---|---|
| `textures/ui/Black` | 2×2 | preto (0,0,0,255) | Não | `Black.json`: `nineslice_size:1, base_size:[2,2]` | `coin_purchase_screen.json` (`"texture": "textures/ui/Black"`), `authentication_screen.json`, `content_log.json` | confirmado |
| `textures/ui/white_background` | 2×2 | branco (255,255,255,255) | Não | sem sidecar | usada como fundo simples | confirmado |
| `textures/ui/dark_bg` | 3×3 | cinza-escuro neutro (22,22,22,255) | Não | `dark_bg.json`: `nineslice_size:1, base_size:[3,3]` | `crafter_screen_pocket.json`, `pocket_containers.json`, `win10_trial_conversion_screen.json` | confirmado |
| `textures/ui/control_gray` | 2×2 | cinza médio (49,49,49,255) | Não | sem sidecar | `chat_settings_menu_screen.json` | confirmado |
| `textures/ui/dialog_background_opaque` | 16×16 | gradiente branco→cinza(198)→cinza(85), moldura preta 1px | **Sim** — borda preta ~1px + banda cinza interna decorativa (não é cor sólida uniforme) | `dialog_background_opaque.json`: `nineslice_size:4, base_size:[16,16]` | `horse_screen_pocket.json` (`"$dialog_background": "dialog_background_opaque"`), `chalkboard_screen.json` | confirmado |
| `textures/ui/screen_background` | 1×1 | preto (0,0,0,255) | Não (1px, sem espaço p/ borda) | `screen_background.json`: `nineslice_size:0, base_size:[1,1]` | `play_screen.json`, `store_common.json`, `ui_common.json` | confirmado |
| `textures/ui/hud_tip_text_background` | 6×6 | preto opaco no miolo, **cantos totalmente transparentes** (alpha 0) | Sim, mas é borda arredondada transparente nos 4 cantos, não linha de cor | `hud_tip_text_background.json`: `nineslice_size:[2,2,2,2], base_size:[6,6]` | `hud_screen.json`, `ui_common.json` | confirmado |
| `textures/ui/dialog_background_hollow_1..8` | variável (18×101 até 42×42, ver Tarefa B) | painel "furado" (moldura com buraco no meio p/ conteúdo vazar) | Sim, moldura decorativa completa, não cor sólida | sidecar próprio para cada número (`nineslice_size` array) | `ui_template_dialogs.json` (`"$dialog_background": "dialog_background_hollow_6"` etc.) | confirmado |
| `textures/ui/White` | **15×15** | branco (255,255,255) só no miolo 11×11 | **SIM — armadilha confirmada**: borda preta opaca de exatamente 2px em todos os lados | sem sidecar (nenhum `White.json` no pack) | usado tintado via `color` em `ui_template_buttons.json` (`nested_label_content_background_assets`, cor multiplicada por cima do preto+branco) | confirmado |
| `textures/ui/dark` | 15×15 | **marrom/laranja escuro (127,51,0,255)**, não cinza | Sim — mesma moldura preta 2px do White | sem sidecar | não referenciado como `"textures/ui/dark"` puro nos screens varridos (uso indireto via variável) | provável |
| `textures/ui/Gray` e `textures/ui/Grey` | 2×2 | **ARMADILHA: pixel real é preto puro (0,0,0,255), apesar do nome "Gray/Grey"** | Não | `Gray.json` / `Grey.json`: `nineslice_size:1, base_size:[2,2]` (idêntico ao Black.json) | `choose_realm_screen.json`, `resource_packs_screen.json`, `tabbed_upsell_screen.json`, `storage_management.json` | confirmado (verificado com 2 decoders PNG independentes) |
| `textures/ui/background_panel` | 16×16 | gradiente branco→cinza→cinza-escuro, moldura preta | Sim, decorativo (não sólido) | `background_panel.json`: `nineslice_size:4, base_size:[16,16]` | referenciado por telas com painel "elevado" | confirmado |
| `textures/ui/greyBorder` | 16×16 | cinza (85/33), moldura preta com cantos suavizados (alpha parcial) | Sim | `greyBorder.json`: `nineslice_size:4, base_size:[16,16]` | usado como moldura decorativa, não fundo sólido | confirmado |
| `textures/ui/panel_outline` | 4×4 | vazado no centro (alpha 0), borda preta 1px + faixa 30,30,30 | Sim (é literalmente um contorno) | `panel_outline.json`: `nineslice_size:1, base_size:[4,4]` | usado como outline sobreposto, não como fundo | confirmado |

### Achados-chave (Tarefa A)

1. **Confirma a armadilha do enunciado**: `textures/ui/White` é 15×15, com um miolo branco de 11×11 cercado por **2px de preto opaco em todos os lados**. Se usado sem nineslice adequado (ou esticado sem cuidado), a borda preta aparece ampliada/distorcida.
2. **Armadilha nova, não estava no enunciado**: `Gray.png` e `Grey.png` — apesar do nome — decodificam para **preto puro (0,0,0)**, byte a byte idêntico a `Black.png`. Confirmado com dois decodificadores PNG independentes (parser manual + `System.Drawing.Bitmap`). Não usar essas texturas esperando um cinza.
3. **`dark.png` não é cinza-escuro**: é um marrom/laranja escuro (127,51,0) com a mesma moldura preta de 2px do White. Quem quiser um "cinza escuro" neutro deve usar `dark_bg.png` (22,22,22, 3×3, sem borda) ou `control_gray.png` (49,49,49, 2×2, sem borda) — ambas confirmadas sólidas e sem moldura.
4. Texturas verdadeiramente sólidas e **sem borda**, seguras para fundo de painel via nineslice/stretch simples: `Black` (0,0,0), `white_background` (255,255,255), `dark_bg` (22,22,22), `control_gray` (49,49,49), `screen_background` (0,0,0, 1×1).
5. As famílias `dialog_background_opaque*`, `dialog_background_hollow_*`, `background_panel`, `greyBorder`, `panel_outline` **não são cor sólida** — são texturas decorativas com gradiente e/ou moldura, pensadas para nineslice (ver Tarefa B), não para tingimento de cor uniforme.

---

## TAREFA B — Nineslice

### Grep bruto

- `grep -rn "nineslice_size" ui/` → **2 ocorrências**, ambas em `ui/start_screen.json`, e nenhuma é uma atribuição direta de valor: é um `binding_name`/`binding_name_override` (`"#banner_nineslice_size"` → `"#nineslice_size"`), ou seja, um valor dinâmico vindo de binding, não um literal `"nineslice_size": N` dentro de um controle `image`.
- `grep -rn "base_size" ui/` → **0 ocorrências** de `base_size` como propriedade dentro de qualquer arquivo de tela (`ui/*.json`). A propriedade só existe nos sidecars de textura.
- `grep -rln "nineslice_size" textures/ui/*.json` → **334 arquivos** sidecar usam a propriedade.
- Confirmado em todo o corpus (`grep -rniE "nine_slice|nineSlice"`): **não existe nenhuma variação de grafia** — é sempre `nineslice_size`, uma palavra "nineslice" + `_size`, sem underscore entre "nine" e "slice". `base_size` segue o mesmo padrão sempre.

### Conclusão sobre sintaxe

O corpus vanilla **não demonstra a forma "inline dentro do controle image"** (`{"type":"image","texture":"...","nineslice_size": 4}`) como um literal presente em nenhuma das ~350 telas varridas. A convenção 100% observada no vanilla é:

**Arquivo sidecar** — um `.json` com o **mesmo nome** do `.png`, na mesma pasta (`textures/ui/<nome>.json` ao lado de `textures/ui/<nome>.png`). O controle `image` apenas referencia a textura pelo caminho; o motor lê o sidecar automaticamente.

Exemplo literal 1 — forma escalar (borda uniforme em todos os lados), arquivo `textures/ui/Black.json`:
```json
{
  "nineslice_size": 1,
  "base_size": [
    2,
    2
  ]
}
```

Exemplo literal 2 — forma array `[esquerda, topo, direita, baixo]` (bordas assimétricas), arquivo `textures/ui/dialog_background_hollow_1.json`:
```json
{
  "nineslice_size": [
    8,
    23,
    8,
    76
  ],
  "base_size": [
    18,
    101
  ]
}
```

Exemplo literal 3 — `hud_tip_text_background.json` (borda simétrica pequena, array explícito em vez de escalar):
```json
{
  "nineslice_size": [
    2,
    2,
    2,
    2
  ],
  "base_size": [
    6,
    6
  ]
}
```

Uso do controle correspondente (não repete nineslice_size, só referencia a textura), `ui/coin_purchase_screen.json`:
```json
"black_image": {
  "type": "image",
  "texture": "textures/ui/Black"
}
```

Único uso "inline" real encontrado (via `bindings`, não atribuição direta), `ui/start_screen.json` linha ~1465:
```json
"bindings": [
  {
    "binding_name": "#banner_nineslice_size",
    "binding_name_override": "#nineslice_size",
    "binding_condition": "once"
  }
]
```

Comentário do próprio vanilla confirmando que devs vanilla raciocinam sobre o nineslice ao dimensionar filhos, `ui/local_world_picker_screen.json` linha 53:
```
// background_hollow_3 has a (6, 21, 6, 6) nineslice offset, so we need to modify the size and offsets
```

confidence: **confirmado** (grafia da propriedade e as duas sintaxes, escalar e array) / **provável** (que a sintaxe inline dentro do bloco `image` como literal simples funcione no engine — é documentada pela comunidade/Microsoft Docs, mas o corpus vanilla 1.26.44 não contém nenhum exemplo literal disso, só via sidecar ou binding).

---

## TAREFA C — Botões

Correção de premissa: **não existe `common_buttons.json` nem `common.json`** como nomes de arquivo no pack. Os arquivos reais são:
- `ui/ui_template_buttons.json` → `"namespace": "common_buttons"`
- `ui/ui_common.json` → `"namespace": "common"` (é aqui que vive o controle-base `"button"`, referenciado como `common.button` em todo o resto do pack)

### Controle-base `common.button` — `ui/ui_common.json` linhas 44-101

```json
"button": {
  "type": "button",
  ...
  "layer": 1,
  "sound_name": "random.click",
  "sound_volume": 1.0,
  "sound_pitch": 1.0,
  "locked_control": "",
  "default_control": "default",
  "hover_control": "hover",
  "pressed_control": "pressed",
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
  "$button_bindings|default": [],
  "bindings": "$button_bindings"
}
```
confidence: **confirmado**

- `default_control`/`hover_control`/`pressed_control` apontam para os **nomes dos filhos** dentro de `"controls"` do botão concreto (não são caminhos, são nomes de controle-filho tipo `"default"`, `"hover"`, `"pressed"`). O engine troca automaticamente qual filho fica visível conforme o estado do mouse/foco/toque.
- **Som de clique**: `"sound_name": "random.click"` é o padrão herdado por **todo** botão que estende `common.button` (inclusive `common_buttons.light_text_button`, `dark_text_button`, etc., que não sobrescrevem `sound_name`). Confirmado por grep: `sound_name` só aparece sobrescrito em 2 lugares fora de botões genéricos (`item.book.page_turn` no livro, `ui.loom.select_pattern` no tear) — ou seja, é exceção pontual, não padrão de botão.

### Estados default/hover/pressed em `common_buttons` — `ui/ui_template_buttons.json` linhas 350-404 (`light_text_button`)

```json
"controls": [
  { "default@$button_state_panel": { "$new_ui_button_texture": "$default_button_texture", ... "layer": 1 } },
  { "hover@$button_state_panel":   { "$new_ui_button_texture": "$hover_button_texture", ...   "layer": 4 } },
  { "pressed@$button_state_panel": { "$new_ui_button_texture": "$pressed_button_texture",
      "$button_offset|default": "$button_pressed_offset", ... "layer": 5 } },
  { "locked@$button_state_panel":  { "$new_ui_button_texture": "$locked_button_texture", ... "layer": 1 } }
]
```
Cada estado troca a textura de fundo (`$new_ui_button_texture`) e a cor do texto; o estado `pressed` é o único que também aplica `$button_offset: $button_pressed_offset`.

### `$button_pressed_offset` — o vanilla NÃO usa `[0,0]` por padrão

Grep em `ui_template_buttons.json` (16 ocorrências de `button_pressed_offset`): o **padrão vanilla mais comum é `[0, 1]`**, ex. linha 321 (`light_text_button`), 409 (`dark_text_button`), 702 (`light_content_button`), 886 (`dark_content_button`), 1150 (`light_glyph_button`):
```json
"$button_pressed_offset|default": [ 0, 1 ],
```
Ou seja, o vanilla desloca o **conteúdo** (texto/label) 1px para baixo ao pressionar, como feedback tátil intencional — isso é aplicado só ao *texto/label do botão* via `$button_offset`, não ao painel/imagem de fundo inteiro do botão (que não se move).

Onde o vanilla força **`[0, 0]`** explicitamente (para NÃO deslocar nada ao clicar), linha 693 (`single_image_with_border_button`):
```json
"single_image_with_border_button@common_buttons.light_content_button": {
  "$button_offset": [ 0, 0 ],
  ...
}
```
E linha 684 (`transparent_content_button`):
```json
"$button_offset": [ 0, 0 ],
```
Ambos são variantes de botão só-imagem (ícone/imagem única, sem texto), onde qualquer deslocamento do conteúdo no clique causaria "pulo" visível do ícone dentro do quadro — por isso zeram o offset. Já nos botões com texto, o vanilla aceita o deslocamento de 1px como affordance de "apertado".

confidence: **confirmado** (valores e trechos citados) — a *razão de projeto* (evitar "pulo" do ícone) é inferência lógica sobre por que essas duas variantes zeram o offset, marcada como **provável**.

### Padrão "tile quadrado com ícone + texto abaixo"

Não foi encontrado no corpus varrido (`ui_iconbutton.json`, `pause_screen.json`, `sidebar_navigation.json`, `store_common.json`, `how_to_play_common.json`, `ui_template_tabs.json`) um template reutilizável de **ícone acima + texto abaixo** dentro de um botão quadrado único. O que existe, confirmado:

- `ui/ui_iconbutton.json` (`iconbutton.iconbutton_button_content`, linhas 20-82): ícone e texto lado a lado (stack horizontal), não ícone-em-cima:
```json
"iconbutton_button_content": {
  "type": "stack_panel",
  "size": [ "100%", 16 ],
  "orientation": "horizontal",
  "controls": [
    { "icon_wrapper": { ... "icon_with_border": { "size": [18,18], ... } } },
    { "padding_middle@common.empty_panel": { "size": [2, "100%"] } },
    { "vertically_centered_text": { ... "profile_button_label@common_buttons.new_ui_binding_button_label": {...} } }
  ]
}
```
- `ui/store_common.json` (`store_offer_grid_item`, linha 8762+) é o mais próximo de "tile quadrado com imagem + texto abaixo" (thumbnail de oferta da loja + descrição/preço abaixo), mas é uma peça de conteúdo de marketplace, não um botão de navegação genérico reaproveitável.

confidence: **suspeita** — não invento um template vanilla de "ícone-em-cima + label-embaixo" que não localizei; se esse padrão existir em algum addon custom (ex. SonheMenu), ele não vem diretamente de um template vanilla equivalente encontrado nesta varredura.

### Estrutura macro do botão (`new_ui_button_panel`, `ui/ui_template_buttons.json` linhas 73-130)

```json
"new_ui_button_panel": {
  "type": "panel",
  ...
  "controls": [
    { "$button_image@$button_image": { "size": "$button_image_size", ... "layer": 1 } },
    { "button_content": { "type": "panel", "size": "$button_content_size",
        "controls": [ { "$button_type_panel@$button_type_panel": { "layer": 3 } } ] } },
    { "border@common_buttons.focus_border": { ... } }
  ]
}
```
Três camadas por estado: imagem de fundo (layer 1) → conteúdo (texto/ícone, layer 3) → borda de foco (`focus_border`, textura `textures/ui/focus_border_white`).

---

## Resumo de arquivos-fonte citados

- `ui/ui_common.json` (namespace `common`) — controle-base `button`
- `ui/ui_template_buttons.json` (namespace `common_buttons`) — variantes de botão, offsets, sons herdados
- `ui/ui_template_dialogs.json` (namespace `common_dialogs`) — confirma que **não existe `common_dialogs.json`** como arquivo; o namespace vive aqui
- `ui/ui_iconbutton.json` (namespace `iconbutton`) — ícone+label horizontal
- `ui/start_screen.json` — único uso de `nineslice_size` como binding dinâmico
- `ui/local_world_picker_screen.json` — comentário vanilla sobre nineslice de `dialog_background_hollow_3`
- `textures/ui/*.json` (334 arquivos) — sidecars de nineslice
