# Layout adaptativo e dependência circular de tamanho — Corpus vanilla 1.26.44

Corpus: `c:/Users/Desktop/Documents/Nova pasta/assets/assets/resource_packs/vanilla/ui/`

Arquivos lidos por completo:
- `npc_interact_screen.json` (namespace `npc_interact`)
- `popup_dialog.json` (namespace `popup_dialog`)
- `ui_template_dialogs.json` (namespace `common_dialogs` — confirmado: não existe `common_dialogs.json`)
- `edu_discovery_dialog.json` (namespace `discovery_dialog`, único `dialog_*.json` de fato, além do que já citado)
- `csb_sections/csb_upsell_dialog.json` (namespace `csb_upsell`, é o outro arquivo que casa com `*dialog*.json`)
- `ui_edu_common.json` (namespace `edu_common`, consultado como apoio porque `npc_interact` e `discovery_dialog` dependem dele para fechar as cadeias de `%c`)
- `ui_common.json` (namespace `common`, consultado para `tts_label_focus_wrapper`)

Não existe nenhum arquivo `dialog_*.json` além de `edu_discovery_dialog.json`; `storage_management_popup.json` e `persona_popups.json` são `*popup*`, não `*dialog*`, e não foram abertos.

---

## 1. Quando o vanilla usa `%c` vs `%cm`

Regra observada, consistente em todo o corpus lido:

- **`%c` ("soma dos filhos")**: usado no **eixo de orientação** de um `stack_panel` (largura num `horizontal`, altura num `vertical`), onde o tamanho final é a soma sequencial do tamanho de cada filho. Também usado em `panel`/`image` simples quando há efetivamente um único filho "de conteúdo" que se quer abraçar exatamente.
- **`%cm` ("maior filho")**: usado no **eixo transversal** de um `stack_panel` (altura num `horizontal`, largura num `vertical`), para que o painel fique do tamanho do maior filho naquele eixo. Também usado em `panel`/`image` quando os filhos são **sobrepostos** (mesma posição, camadas via `layer`) em vez de empilhados — somar seria errado, então usa-se o máximo.

Evidência literal (`npc_interact_screen.json:765-812`, dentro de `add_help_section`):

```json
"text_url": {
  "type": "panel",
  "size": [ "100%cm", "100%cm" ],
  "controls": [
    { "tts_border@common.non_interact_focus_border_button": { ... } },
    {
      "wrapper_panel_url": {
        "type": "stack_panel",
        "orientation": "vertical",
        "size": [ "100%cm", "100%c" ],
        "controls": [
          { "text_url_a@npc_interact.help_label": { "text": "$text_url_a" } },
          { "padding@common.empty_panel": { "size": [ "100%sm", 12 ] } },
          { "text_url_b@npc_interact.help_label": { "text": "$text_url_b" } }
        ]
      }
    }
  ]
}
```

`text_url` é um `panel` comum com dois filhos **sobrepostos** (borda de foco + wrapper de texto) → usa `%cm/%cm` (máximo dos dois). `wrapper_panel_url` é `stack_panel vertical` → eixo de orientação (Y) usa `%c` (soma dos 3 filhos empilhados), eixo transversal (X) usa `%cm` (largura = a do label mais largo). Mesmo padrão espelhado em `wrapper_panel_command` (linhas 838-861) e em `add_buttons`/`add_help_section` (Y=`%cm`, cross-axis de stack horizontal, linhas 768 e 884).

Confidence: **confirmado**.

---

## 2/3. Profundidade de aninhamento de `%c`/`%cm` — CRÍTICO

Resposta direta: o vanilla aninha **`%c`/`%cm` em pelo menos 5 e até 6 níveis reais**, no mesmo eixo, em telas hoje em uso (inclusive na própria `npc_interact_screen.json`). Não é um padrão raro nem acidental — é a forma canônica de montar diálogo com altura variável. Achamos 3 cadeias independentes:

### Cadeia A — 5 níveis (eixo Y), dentro de `npc_interact_screen.json` + `ui_edu_common.json`

Caminho da árvore (aba "Advanced" do NPC, aviso de URL inválida):

1. `npc_interact.action` — `npc_interact_screen.json:689-695` — `image`, `size: ["100%","100%c"]`
2. → filho `command@npc_interact.action_command`, que resolve para `npc_interact.action_template` — `npc_interact_screen.json:621-623` — `stack_panel`, `size: ["100% - 12px","100%c"]`
3. → filho `url_warning@npc_interact.url_notifications` — `npc_interact_screen.json:585-590` — `stack_panel`, `size: ["100%","100%c"]`
4. → filho `empty_uri_warning@edu_common.inline_notification` — `ui_edu_common.json:1457-1460` — `image`, `size: ["100%","100%cm"]`
5. → filho `stack` — `ui_edu_common.json:1489-1494` — `stack_panel`, `size: ["100% - 6px","100%cm + 11px"]`
6. → filhos `icon`/`spacer`/`warning_text` (linhas 1497-1519): tamanhos fixos ou `"default"` — a cadeia **termina** aqui (nenhum usa `%c`/`%cm`/`%`/`fill` em Y).

```json
// npc_interact_screen.json:689-695
"action": {
  "type": "image",
  "texture": "textures/ui/dialog_background_opaque",
  "size": [ "100%", "100%c" ],
  "controls": [
    { "trash@edu_common.photo_trash_button": { } },
    { "command@npc_interact.action_command": {} },
    { "url@npc_interact.action_url": {} }
  ]
}
```

```json
// npc_interact_screen.json:621-623 (action_template, base de action_command/action_url)
"action_template@npc_interact.main_stack_panel": {
  "size": [ "100% - 12px", "100%c" ],
  "controls": [ ..., { "url_warning@npc_interact.url_notifications": {} }, ... ]
}
```

```json
// npc_interact_screen.json:585-590
"url_notifications": {
  "type": "stack_panel",
  "orientation": "vertical",
  "size": ["100%", "100%c"],
  "controls": [
    { "empty_uri_warning@edu_common.inline_notification": { ... } },
    { "invalid_uri_warning@edu_common.inline_notification": { ... } }
  ]
}
```

```json
// ui_edu_common.json:1457-1494
"inline_notification": {
  "type": "image",
  "texture": "textures/ui/background_indent_no_top",
  "size": [ "100%", "100%cm" ],
  "controls": [
    {
      "stack": {
        "type": "stack_panel",
        "orientation": "horizontal",
        "size": [ "100% - 6px", "100%cm + 11px" ],
        "controls": [
          { "icon": { "type": "image", "texture": "$icon", "size": "$icon_size" } },
          { "spacer": { "type": "panel", "size": [ 4, "100%sm" ] } },
          { "warning_text": { "type": "label", "size": [ "fill", "default" ], "text": "$warning_text" } }
        ]
      }
    }
  ]
}
```

### Cadeia B — 6 níveis (eixo Y), moldura de diálogo + view do "student" em `npc_interact_screen.json`

1. `common_dialogs.dialog_background_opaque_with_child` (usado como `$custom_background` do painel `student`) — `ui_template_dialogs.json:448-454` — `image`, `size: ["100%","100%c + 31px"]`
2. → filho `control` (dentro de `dialog_background_hollow_common`) — `ui_template_dialogs.json:377-384` — `image`, `size: $common_background_size` = `["100% - 16px","100%c - 27px"]`
3. → filho `inside_header_panel@$child_control` = `npc_interact.student_view_content` — `npc_interact_screen.json:1278-1281` — `panel`, `size: ["100%","100%cm"]`
4. → filho `student@npc_interact.student_stack_panel` — `npc_interact_screen.json:1268-1269` — `stack_panel`, `size: ["100%","100%c"]`
5. → filho `buttons@npc_interact.student_buttons` — `npc_interact_screen.json:1238-1239` — `panel`, `size: ["100%","100%c"]`
6. → filho `buttons` (stack interno) — `npc_interact_screen.json:1242-1246` — `stack_panel`, `size: ["100% + 2px","100%cm"]`
7. → filho `actions` (grid) — `npc_interact_screen.json:1249-1252` — `size: ["fill","default"]` — cadeia **termina** (grid se automedidas pelo próprio algoritmo de grid, não por `%c`).

```json
// ui_template_dialogs.json:371-416 (mecanismo genérico usado por toda a família dialog_background_hollow_*)
"dialog_background_hollow_common@common_dialogs.dialog_background_common": {
  "layer": 2,
  "controls": [
    {
      "control": {
        "type": "image",
        "$common_background_size|default": [ "100% - 16px", "100%c - 27px" ],
        "size": "$common_background_size",
        "controls": [
          { "inside_header_panel@$child_control": {} },
          { "close_button_holder@common_dialogs.common_close_button_holder": {} },
          { "title_label@common_dialogs.title_label": { } }
        ]
      }
    }
  ]
}
```

### Cadeia C — 5 níveis (eixos X e Y), `popup_dialog.json` + `edu_discovery_dialog.json`

1. `popup_dialog.form_fit_screen_with_title_and_close` — `popup_dialog.json:615-622` — `panel`, `size: ["100%cm","100%cm"]`
2. → filho `panel_content` — `popup_dialog.json:639-641` — `panel`, `size: $panel_size` = `["100%cm + 16px","100%c + 31px"]`
3. → filho `contents` — `popup_dialog.json:694-696` — `panel`, `size: ["100%c","100%c"]`
4. → filho `contents@$modal_contents` = `discovery_dialog.content` — `edu_discovery_dialog.json:54-56` — `stack_panel`, `size: [218, "100%c"]`
5. → filho `body_text@common.tts_label_focus_wrapper` — `edu_discovery_dialog.json:59-62` / `ui_common.json:1304-1312` — `panel`, `size: ["100%","100%cm"]`
6. → filho `label@$tts_label_panel` = `discovery_dialog.service_body_label` — `edu_discovery_dialog.json:4-6` — `size: ["100%","default"]` — cadeia **termina**.

```json
// popup_dialog.json:615-622
"form_fit_screen_with_title_and_close": {
  "type": "panel",
  "size": [ "100%cm", "100%cm" ],
  ...
}
// popup_dialog.json:639-696 (panel_content -> contents, resumido)
"panel_content": { "type": "panel", "size": "$panel_size", "controls": [
  { "header": { "size": [ "100%c + 15px", 0 ] } },
  { "close_button_panel": { "size": [ "100%c", 0 ] } },
  { "contents": { "type": "panel", "size": [ "100%c", "100%c" ], "controls": [
    { "contents@$modal_contents": {} }
  ] } }
]}
```

```json
// edu_discovery_dialog.json:54-73
"content": {
  "type": "stack_panel",
  "size": [ 218, "100%c" ],
  "controls": [
    { "body_text@common.tts_label_focus_wrapper": { "size": [ "100%", "100%cm" ], "$tts_label_panel": "discovery_dialog.service_body_label" } },
    { "text_to_button_padding@common.empty_panel": { "size": [ "100%", 9 ] } },
    { "buttons@discovery_dialog.service_buttons": {} }
  ]
}
```

### Conclusão da pergunta crítica

Aninhar `%c`/`%cm` **2, 3, 4, 5 e até 6 níveis** no mesmo eixo é um padrão vanilla normal e amplamente usado — inclusive dentro do próprio `npc_interact_screen.json`, o arquivo mais próximo do caso de uso do addon. Um "quebrou com 2 níveis" **não pode ser atribuído à profundidade do aninhamento em si**. Nas três cadeias acima, todo nível que quebra a corrente o faz por um motivo específico, nunca por causa da contagem de níveis:
- termina em tamanho fixo (px),
- termina em `"default"` (automedição por conteúdo/texto),
- termina em `grid` (`"default"`, algoritmo próprio de grid).

Suspeitas mais prováveis para a quebra real do addon (não confirmadas neste corpus, é diagnóstico, não evidência vanilla): (a) algum filho no meio da cadeia usando `%`/`fill` no mesmo eixo do pai `%c` (ver seção 3 — violação da regra de circularidade), (b) tipo de controle que não participa do cálculo de `%c` da forma esperada (ex.: `grid`, `custom`, `scrolling_panel`), (c) binding de visibilidade dinâmica que não força reflow do `%c` do ancestral quando muda em runtime.

Confidence: **confirmado** (as 3 cadeias são citações literais e íntegras do corpus).

---

## 3. Regra de dependência circular

Regra: um controle com `size` `%c`/`%cm` em um eixo não deve ter, no mesmo eixo, filho direto com `%` simples (percentual do pai) ou `fill` — porque ambos exigem que o tamanho do pai já esteja resolvido, e o `%c`/`%cm` do pai exige que o filho já esteja resolvido primeiro. Isso cria uma dependência circular sem solução determinística.

Verificação: percorri **todos os pais `%c`/`%cm` das 3 cadeias acima** (mais de 15 nós) e listei o tipo de tamanho de **cada filho direto no mesmo eixo**. Resultado: **nenhuma ocorrência** de filho `%`/`fill` no mesmo eixo de um pai `%c`/`%cm`. Os filhos são sempre um de:
- valor fixo em px (`0`, `10`, `20`...),
- expressão aritmética sobre `%c`/`%cm` (`"100%c + 15px"`, `"100%cm - 27px"` etc. — mesma família, permitido, porque ainda depende só dos netos),
- `%sm` (tamanho igual ao maior irmão — resolvido *depois* dos irmãos normais, não do pai, então não fecha o ciclo),
- `"default"` (automedição por conteúdo).

Um caso que **parece** contrariar a regra mas não contraria (`csb_upsell_dialog.json:555-570`):

```json
"csb_price": {
  "type": "panel",
  "size": [ "100%", "fill" ],
  "controls": [
    { "price_details@csb_price_details": { ... } }
  ]
},
"csb_price_details": {
  "type": "stack_panel",
  "size": [ "100%", "100%c" ],
  ...
}
```

Aqui o **pai** (`csb_price`) usa `fill` em Y, e o **filho** (`csb_price_details`) usa `%c` em Y — é a direção oposta da regra (pai não é `%c`, então não há ciclo: o pai é resolvido de fora para dentro por quem o contém, independente do filho). Não é uma violação, é só a combinação inversa e permitida.

Confidence: **confirmado** dentro do corpus examinado (nenhuma amostra em contrário encontrada); generalizar para *todo* o resource pack vanilla sem grep exaustivo em todos os ~200 arquivos de `ui/` seria **provável**, não confirmado.

---

## 4. Padrão canônico: imagem de fundo como PAI do conteúdo

Confirma-se o padrão: para altura variável, o vanilla usa uma `image` de fundo com `size: ["100%","100%c"]` (ou `%cm`) contendo o conteúdo real como **filho direto** (não irmão em camada). Dois exemplos literais completos:

### Exemplo 1 — `npc_interact_screen.json:689-723` (o mais direto, sem indireção de template)

```json
"action": {
  "type": "image",
  "texture": "textures/ui/dialog_background_opaque",
  "size": [ "100%", "100%c" ],
  "controls": [
    {
      "trash@edu_common.photo_trash_button": {
        "anchor_from": "top_right",
        "anchor_to": "top_right",
        "offset": [ -4, 4 ],
        "button_mappings": [
          { "from_button_id": "button.menu_select", "to_button_id": "button.delete_action", "mapping_type": "pressed" },
          { "from_button_id": "button.menu_ok", "to_button_id": "button.delete_action", "mapping_type": "pressed" }
        ],
        "bindings": [
          { "binding_type": "collection_details", "binding_collection_name": "actions_collection", "binding_collection_prefix": "actions" }
        ]
      }
    },
    { "command@npc_interact.action_command": {} },
    { "url@npc_interact.action_url": {} }
  ]
}
```

A textura `dialog_background_opaque` é o **pai**; `command`/`url` (conteúdo real, tamanho variável) são filhos diretos. A altura da imagem (`%c`) acompanha o conteúdo automaticamente.

### Exemplo 2 — `ui_template_dialogs.json:443-454` + `371-416` (mecanismo genérico reaproveitado por praticamente todo diálogo form-fitting do jogo)

```json
"dialog_background_opaque_with_child@common_dialogs.dialog_background_hollow_common": {
  "size": [ "100%", "100%c + 31px" ],
  "texture": "textures/ui/dialog_background_opaque",
  "$fill_alpha": 0.0
},
"dialog_background_hollow_common@common_dialogs.dialog_background_common": {
  "layer": 2,
  "controls": [
    {
      "control": {
        "type": "image",
        "$dialog_background_texture|default": "textures/ui/control",
        "texture": "$dialog_background_texture",
        "$common_background_size|default": [ "100% - 16px", "100%c - 27px" ],
        "size": "$common_background_size",
        "controls": [
          { "inside_header_panel@$child_control": {} },
          { "close_button_holder@common_dialogs.common_close_button_holder": {} },
          { "title_label@common_dialogs.title_label": { "anchor_from": "top_middle", "anchor_to": "top_middle", "offset": [ 0, -15 ] } }
        ]
      }
    }
  ]
}
```

`inside_header_panel@$child_control` (o conteúdo real de cada tela que usa esse template) é filho direto da imagem `control`, que por sua vez é filho da imagem externa `dialog_background_opaque_with_child`. É esse mecanismo que a própria `npc_interact_screen.json:1497-1514` usa para o painel "student":

```json
"student@common_dialogs.form_fitting_main_panel_no_buttons": {
  "$panel_size": [ 320, "100%cm" ],
  "size": "$panel_size",
  "$child_control": "npc_interact.student_view_content",
  "$custom_background": "common_dialogs.dialog_background_opaque_with_child",
  ...
}
```

Confidence: **confirmado**.

---

## 5. anchor/offset + `%c` para centralizar

Regra observada: para um controle de tamanho `%c`/`%cm` ficar centralizado sem "puxar" para um lado conforme o conteúdo muda, `anchor_from` e `anchor_to` devem ser o **mesmo ponto simétrico** (`center`/`center`, ou `top_middle`/`top_middle` para centralizar só no eixo X, `left_middle`/`left_middle` só no eixo Y etc.). Isso ancora o *centro* da caixa `%c`, então crescer/encolher expande para os dois lados igualmente. `offset` continua funcionando normalmente por cima disso, como ajuste fino a partir desse ponto central — não interfere na centralização.

Exemplos literais:

```json
// ui_template_dialogs.json:36-47 — título sempre centralizado no eixo X, largura variável
"title_label": {
  "type": "panel",
  "anchor_from": "top_middle",
  "anchor_to": "top_middle",
  "$title_size|default": [ "100%c", 10 ],
  "size": "$title_size",
  "$title_offset|default": [ 0, 9 ],
  "offset": "$title_offset",
  ...
}
```

```json
// ui_template_dialogs.json:324-337 + npc_interact_screen.json:1497-1514
// anchor center/center herdado, size mistura fixo (X) e %cm (Y) — cresce/encolhe centrado nos dois eixos
"form_fitting_main_panel_no_buttons": {
  "type": "panel",
  "size": [ "100%", "100%c" ],
  "anchor_from": "center",
  "anchor_to": "center",
  ...
}
// instanciado como:
"student@common_dialogs.form_fitting_main_panel_no_buttons": {
  "$panel_size": [ 320, "100%cm" ],
  "size": "$panel_size"
  // anchor_from/anchor_to "center" herdados do template — não sobrescritos
}
```

```json
// popup_dialog.json:643-650 — header com largura %c, ancorado top_middle/top_middle (mesmo truque)
"header": {
  "type": "panel",
  "size": [ "100%c + 15px", 0 ],
  "anchor_from": "top_middle",
  "anchor_to": "top_middle",
  "offset": "$title_offset"
}
```

Contraexemplo didático (uso de `%c` **sem** intenção de centralizar, para mostrar que `anchor` e `size:%c` são ortogonais — aqui o anchor é escolhido para posicionar *fora* do canto, não para centralizar):

```json
// npc_interact_screen.json:1394-1400
"close_button_holder": {
  "type": "panel",
  "size": [ "100%c", "100%c" ],
  "anchor_from": "top_right",
  "anchor_to": "bottom_right",
  "offset": [ 8, -3 ]
}
```

Confidence: **confirmado**.
