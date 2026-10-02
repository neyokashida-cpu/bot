# Coletados — exemplos didáticos (Tarefa B)

Fonte: `.../scratchpad/{full_menu_example.json, grid_example.json, image_example.json, binding_example.json, ex_scroll.json, tree.json}`
Comparação: `c:/Users/Desktop/Documents/Nova pasta/assets/assets/resource_packs/vanilla/ui/` + relatórios anteriores em `docs/json-ui/fontes/`.
Convenção: **confirmado** / **provável** / **suspeita**.

---

## 1. Identificação por arquivo

### grid_example.json, image_example.json, binding_example.json
- **Origem: gerado por ferramenta baseada no schema `ui.schema.json` (presente no mesmo scratchpad), não é tutorial escrito à mão nem tela vanilla real. confidence: provável.**
- Evidência: os três arquivos dumpam **todas** as propriedades de `panel`/`image` com seus valores default, na mesma ordem exata em que aparecem em `ui.schema.json` (`visible`, `enabled`, `layer`, `alpha`, `propagate_alpha`, `clips_children`, `allow_clipping`, `clip_offset`, `clip_state_change_event`, `enable_scissor_test`, `property_bag`, `selected`, `use_child_anchors`, `anims`, `disable_anim_fast_forward`, `animation_reset_name`, `variables`...) — padrão típico de geração automática a partir de um schema (o mesmo schema referenciado como `$schema` em `skyls_clean.json`: `https://kalmemarq.github.io/Bugrock-JSON-UI-Schemas/ui.schema.json`), não de um humano escrevendo um exemplo mínimo.

- **grid_example.json** — padrão canônico de `grid`, com a superfície completa de propriedades (não vista tão explícita em outro lugar do corpus):
  ```json
  "inventory_grid": {
      "type": "grid",
      "grid_dimensions": [3, 3],
      "maximum_grid_items": 9,
      "grid_dimension_binding": "",
      "grid_rescaling_type": "horizontal",
      "grid_fill_direction": "horizontal",
      "grid_item_template": "common.inventory_slot",
      "precached_grid_item_count": 0,
      "size": [180, 180]
  }
  ```
  e uma segunda grade em lista vertical (`grid_dimensions: [1,5]`, `grid_rescaling_type: "none"`, `grid_fill_direction: "vertical"`) sem `grid_item_template` (campo vazio — mostra que o template é opcional na definição isolada). Novo aqui: ver os 8 campos de grid lado a lado com seus defaults explícitos (`grid_dimension_binding: ""`, `precached_grid_item_count: 0`) não aparece em nenhum grid real vanilla estudado até agora (lá os campos não usados simplesmente são omitidos).

- **image_example.json** — 5 variantes de `image` cobrindo os modos que não tinham exemplo isolado nos relatórios anteriores: nine-slice (`nineslice_size: 4`), tile (`tiled: true, tiled_scale: [2,2]`), recorte por UV (`uv: [16,16], uv_size: [16,16]`), escala de cinza (`grayscale: true, bilinear: true`) e preenchimento total (`fill: true, keep_ratio: false, layer: -1`). Trecho do modo `fill`:
  ```json
  "fill_image": {
      "type": "image",
      "texture": "textures/ui/panorama_overlay",
      "fill": true,
      "keep_ratio": false,
      "size": ["100%", "100%"],
      "layer": -1
  }
  ```

- **binding_example.json** — o mais rico dos três: cobre os 4 `binding_type` (`global`, `collection`, `collection_details`, `view`), `binding_condition: "once"` (bind executado uma única vez, não a cada tick) e um binding `view` **entre controles irmãos** via `source_control_name`:
  ```json
  { "binding_type": "global", "binding_name": "#online_player_count", "binding_condition": "once" },
  {
    "binding_type": "view",
    "source_control_name": "player_name_label",
    "source_property_name": "#localplayername",
    "target_property_name": "#text"
  }
  ```
  Esse segundo trecho é o padrão canônico de "ler uma propriedade computada de outro controle nomeado no mesmo escopo" — mais explícito do que qualquer ocorrência vista em `vsf.json`/`csf.json`, que só encadeiam bindings dentro do próprio controle.

### full_menu_example.json
- **Origem: gerado por uma ferramenta terceira chamada "EasyUIBuilder" (v2.0), não vanilla, não tutorial oficial. confidence: confirmado — o próprio arquivo se autoidentifica.**
  ```json
  "footer_text": {
      "type": "label",
      "text": "Made with EasyUIBuilder v2.0",
      ...
  }
  ```
- Padrão novo: geração de N botões a partir do tamanho de uma coleção via `factory` (não `grid`), com **filtro por texto** para simular "várias telas com o mesmo `form_buttons`":
  ```json
  "template_button_easy_ui_builder_stack_panel": {
      "type": "stack_panel",
      "factory": { "name": "buttons", "control_name": ".template_button_easy_ui_builder" },
      "collection_name": "form_buttons",
      "bindings": [
          { "binding_name": "#form_button_length", "binding_name_override": "#collection_length" }
      ]
  }
  ```
  e cada botão-filho só fica visível se o próprio texto do botão bater com uma string fixa:
  ```json
  "$condition": "(#form_button_text = 'Play')",
  ...
  "bindings": [
      { "binding_type": "view", "source_property_name": "$condition", "target_property_name": "#visible" }
  ]
  ```
  Isso é diferente do padrão de índice/tamanho embutido no título (`csf.json`, `coletados-chest.md`): aqui a seleção é por **igualdade exata de texto do botão**, não por substring do título do form. Nota: `#form_button_length` **não existe no corpus vanilla** (`vanilla-grid.md` já confirmou isso — o nome real é `#form_button_contents`); este arquivo repete o mesmo erro/fabricação já sinalizado naquele relatório, o que reforça que `full_menu_example.json` é conteúdo de terceiros não verificado, não vanilla.

### ex_scroll.json
- **Origem: rascunho próprio do projeto (namespace `sonhe_forms`), não é exemplo de terceiros apesar do nome do arquivo. confidence: confirmado — `"namespace": "sonhe_forms"` e nomes de controle (`grid_screen`, `resizeable_scrolling_panel`, `tiles_grid`) batem com a linha de desenvolvimento do próprio `SonheMenu_RP`, não com nenhuma fonte externa do corpus.**
- O binding central do arquivo,
  ```json
  "bindings": [
      { "binding_name": "#form_button_contents", "binding_name_override": "#maximum_grid_items" }
  ]
  ```
  **já foi extensivamente investigado e resolvido em `vanilla-grid.md`** (seção "Disputa #3"): `#form_button_contents` é o nome real confirmado no vanilla, mas o vanilla nunca o usa para alimentar `#maximum_grid_items` de um `grid` (só `#collection_length` de `stack_panel`/`factory`) — redirecionar para `#maximum_grid_items` é extrapolação plausível, não comprovada em produção pela Mojang. Não repito a análise aqui.
- Único elemento não coberto antes: o wrapper `resizeable_scrolling_panel@common.scrolling_panel` com todos os tamanhos internos em combinações de `"100%cm"`/`"100%c"` (`$scrolling_pane_size`, `$scroll_view_control_size`, `$scroll_view_stack_panel_size`, `$scroll_view_port_panel_size`, `$view_port_size`) e `$scroll_bar_contained: true` — mostra o conjunto completo de 8 variáveis de dimensionamento que `common.scrolling_panel` espera para se comportar como "altura automática, mas com teto (`$scroll_view_port_max_size`) antes de rolar":
  ```json
  "$scroll_view_port_max_size": ["100%", 208],
  "$scroll_bar_contained": true,
  "$scroll_bar_left_padding_size": [0, 0]
  ```
  Isso já aparece espalhado em `addon-ui1.md`/`vanilla-adaptativo.md`, mas não como uma lista fechada das 8 variáveis relevantes lado a lado — valor de referência rápida, não descoberta nova de mecanismo.

### tree.json
- **Origem: não é JSON UI — é a resposta bruta da GitHub Trees API para o repositório `Mojang/bedrock-samples`. confidence: confirmado.**
  ```json
  {
    "sha": "736072450c26a7c67f07b1661f29d9a5ebaa14b1",
    "url": "https://api.github.com/repos/Mojang/bedrock-samples/git/trees/...",
    "tree": [ { "path": ".github", "mode": "040000", "type": "tree", "sha": "...", "url": "..." }, ... ]
  }
  ```
  Contém apenas metadados de listagem de arquivos (path/sha/size/url) do repositório, provavelmente usado para descobrir quais arquivos baixar (correlaciona com a pasta `bedrock-samples-main/` já presente no mesmo scratchpad). Nenhum controle, grid, binding ou tema — nada a extrair como padrão de JSON UI.

---

## 2. Resumo de proveniência

| Arquivo | Origem | Confidence |
|---|---|---|
| grid_example.json | gerado a partir de `ui.schema.json` | provável |
| image_example.json | gerado a partir de `ui.schema.json` | provável |
| binding_example.json | gerado a partir de `ui.schema.json` | provável |
| full_menu_example.json | ferramenta de terceiros "EasyUIBuilder v2.0" | confirmado |
| ex_scroll.json | rascunho próprio (`sonhe_forms`), não didático de terceiros | confirmado |
| tree.json | metadado da GitHub Trees API, não é JSON UI | confirmado |

Padrões canônicos novos extraídos: grid com todos os campos explícitos (grid_example), os 5 modos de `image` lado a lado incluindo `fill`/`grayscale`/UV-crop (image_example), binding `view` entre controles irmãos via `source_control_name` + `binding_condition: "once"` (binding_example), e seleção de botão por igualdade exata de `#form_button_text` via factory+collection_length (full_menu_example). `ex_scroll.json` e `tree.json` não trouxeram mecanismo genuinamente novo além do já registrado em `vanilla-grid.md`/`vanilla-adaptativo.md`.
