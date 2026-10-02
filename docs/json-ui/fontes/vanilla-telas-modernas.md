# Telas modernas com grade de tiles (ícone + título) — corpus vanilla 1.26.44 (Tarefa B)

Corpus: `c:/Users/Desktop/Documents/Nova pasta/assets/assets/resource_packs/vanilla/ui/`.
Metodologia: `find`/`ls` recursivo para listar `ui/` inteiro, grep por `"type": "grid"` +
`grid_item_template` para achar telas candidatas, leitura direta das mais promissoras.

## 0. Listagem completa de `ui/` (207 arquivos, confirmado via `find`)

```
_global_variables.json
_ui_defs.json
achievement_screen.json
add_external_server_screen.json
adhoc_inprogess_screen.json
adhoc_screen.json
anvil_screen.json
anvil_screen_pocket.json
authentication_modals.json
authentication_screen.json
auto_save_info_screen.json
beacon_screen.json
beacon_screen_pocket.json
blast_furnace_screen.json
book_screen.json
brewing_stand_screen.json
brewing_stand_screen_pocket.json
bundle_purchase_warning_screen.json
cartography_screen.json
cartography_screen_pocket.json
chalkboard_screen.json
chat_screen.json
chat_settings_menu_screen.json
chest_screen.json
choose_realm_screen.json
coin_purchase_screen.json
command_block_screen.json
confirm_delete_account_screen.json
content_log.json
content_log_history_screen.json
crafter_screen_pocket.json
create_world_upsell_screen.json
credits_screen.json
csb_purchase_error_screen.json
csb_screen.json
csb_sections/content_section.json
csb_sections/csb_banner.json
csb_sections/csb_buy_now_screen.json
csb_sections/csb_common.json
csb_sections/csb_purchase_amazondevicewarning_screen.json
csb_sections/csb_purchase_warning_screen.json
csb_sections/csb_subscription_panel.json
csb_sections/csb_upsell_dialog.json
csb_sections/csb_welcome_screen.json
csb_sections/faq_section.json
csb_sections/landing_section.json
custom_templates_screen.json
day_one_experience_intro_screen.json
day_one_experience_screen.json
death_screen.json
debug_screen.json
dev_console_screen.json
disconnect_screen.json
display_logged_error_screen.json
edu_discovery_dialog.json
edu_featured.json
edu_pause_screen_pause_button.json
emote_wheel_screen.json
enchanting_screen.json
enchanting_screen_pocket.json
encyclopedia_screen.json
expanded_skin_pack_screen.json
feed_common.json
file_upload_screen.json
furnace_screen.json
furnace_screen_pocket.json
game_tip_screen.json
gamepad_disconnected.json
gamepad_layout_screen.json
gameplay_common.json
gamma_calibration_screen.json
gathering_info_screen.json
global_pause_screen.json
grindstone_screen.json
grindstone_screen_pocket.json
horse_screen.json
horse_screen_pocket.json
host_options_screen.json
how_to_play_common.json
how_to_play_screen.json
hud_crosshair_overlay.json
hud_screen.json
immersive_reader.json
in_bed_screen.json
inventory_screen.json
inventory_screen_pocket.json
invite_screen.json
jigsaw_editor_screen.json
late_join_pregame_screen.json
library_modal_screen.json
local_world_picker_screen.json
loom_screen.json
loom_screen_pocket.json
manifest_validation_screen.json
marketplace_sdl/sdl_content_navigation.json
marketplace_sdl/sdl_dropdowns.json
marketplace_sdl/sdl_image_row.json
marketplace_sdl/sdl_label.json
marketplace_sdl/sdl_text_row.json
mob_effect_screen.json
non_xbl_user_management_screen.json
npc_interact_screen.json
online_safety_screen.json
pack_settings_screen.json
panorama_screen.json
patch_notes_screen.json
pause_screen.json
pdp_screen.json
pdp_screenshots_section.json
perf_turtle.json
permissions_screen.json
persona_cast_character_screen.json
persona_common.json
persona_popups.json
persona_sdl.json
play_screen.json
pocket_containers.json
popup_dialog.json
portfolio_screen.json
progress_screen.json
rating_prompt.json
realmsPlus_sections/realmsPlus_purchase_warning_screen.json
realms_allowlist.json
realms_common.json
realms_create.json
realms_invite_link_settings_screen.json
realms_pending_invitations.json
realms_plus_ended_screen.json
realms_settings_screen.json
realms_slots_screen.json
realms_stories_transition_screen.json
redstone_screen.json
resource_packs_screen.json
safe_zone_screen.json
scoreboards.json
screenshot_screen.json
select_world_screen.json
server_form.json
settings_screen.json
settings_sections/controls_section.json
settings_sections/general_section.json
settings_sections/realms_world_section.json
settings_sections/settings_common.json
settings_sections/social_section.json
settings_sections/world_section.json
sidebar_navigation.json
sign_screen.json
simple_inprogress_screen.json
skin_pack_purchase_screen.json
skin_picker_screen.json
smithing_table_2_screen.json
smithing_table_2_screen_pocket.json
smithing_table_screen.json
smithing_table_screen_pocket.json
smoker_screen.json
start_screen.json
stonecutter_screen.json
stonecutter_screen_pocket.json
storage_management.json
storage_management_popup.json
storage_migration_common.json
storage_migration_generic_screen.json
store_common.json
store_data_driven_screen.json
store_filter_menu_screen.json
store_inventory_screen.json
store_item_list_screen.json
store_progress_screen.json
store_promo_timeline_screen.json
store_sales_item_list_screen.json
store_search_screen.json
store_sort_menu_screen.json
structure_editor_screen.json
submit_feedback_screen.json
tabbed_upsell_screen.json
test_anims_screen.json
thanks_for_testing_screen.json
third_party_store_screen.json
toast_screen.json
token_faq_screen.json
trade_2_screen.json
trade_2_screen_pocket.json
trade_screen.json
trade_screen_pocket.json
trial_upsell_screen.json
ugc_viewer_screen.json
ui_art_assets_common.json
ui_common.json
ui_common_classic.json
ui_edu_common.json
ui_friendsbutton.json
ui_iconbutton.json
ui_purchase_common.json
ui_template_buttons.json
ui_template_dialogs.json
ui_template_tabs.json
ui_template_toggles.json
update_dimensions.json
update_version.json
win10_trial_conversion_screen.json
world_conversion_complete_screen.json
world_recovery_screen.json
world_templates_screen.json
xbl_console_qr_signin.json
xbl_console_signin.json
xbl_console_signin_succeeded.json
xbl_immediate_signin.json
```
confidence: confirmado (`find … -name "*.json" | wc -l` → 207).

**Achado negativo relevante**: `achievement_screen.json` (candidato citado na tarefa) **não contém
`"type": "grid"` nem `grid_item_template`** — só tem ícones de barra de progresso
(`empty_progress_bar_icon`, `full_progress_bar_icon_base`, linhas 16-22). A grade de conquistas em si não
está neste corpus (deve ser resolvida em outro sistema/arquivo não presente). confidence: confirmado.
`resource_packs_screen.json` também foi descartado: usa lista vertical de linhas com ícone 32px + nome
(`icon_image`), não `type: "grid"` — layout de lista, não de tile-grid.

---

## 1. As 5 telas escolhidas (mais parecidas com "grade de tiles ícone + título")

| Tela | Namespace | Tile | Padrão |
|---|---|---|---|
| `store_common.json` | `common_store` | `suggested_content_offers_grid_item` | card de oferta "hero" 3x1/4x1, capa 16:9 + título abaixo |
| `store_item_list_screen.json` | `store_item_list` | `store_offer_grid_item_OLD` | card de loja completo, 25% de largura, capa + banner de desconto + título sobreposto ao rodapé da capa |
| `world_templates_screen.json` | `world_templates` | `world_template_item` | linha-tile horizontal (screenshot à esquerda + texto à direita), textura de borda troca por estado |
| `skin_picker_screen.json` | `skin_picker` | `skins_grid_item` | tile quadrado só-ícone (preview 3D), sem título, cadeado sobreposto |
| `persona_cast_character_screen.json` | `persona_cast_character_screen` | `cast_single_character_button_panel` | tile quadrado auto-proporcional (`"100%x"`), borda de estado nomeada (`default`/`hover`/`pressed`) |

---

## 2. `store_common.json` — `suggested_content_offers_grid_item` (linhas 10060-10101, 10304-10385)

```json
"suggested_content_offers_grid_item": {
  "type": "panel",
  "$suggested_offers_grid_item_size|default": [ "33.33333%", "100%" ],
  "size": "$suggested_offers_grid_item_size",
  "controls": [
    { "frame@common_store.banner_fill": {
        // overdraw our width by 1 pixel, to work around a layout/rendering rounding error
        "size": [ "100% + 1px", "100%" ],
        "controls": [
          { "key_art@common_store.store_offer_key_art": {
              "size": [ "100% - 2px", "56.25%x" ],
              "offset": [ 0, 1 ], "anchor_from": "top_middle", "anchor_to": "top_middle",
              "controls": [ { "key_art_frame@common.square_image_border_white": { "size": ["100% + 2px","100% + 2px"] } } ]
          } },
          { "title_label_panel": {
              "type": "stack_panel",
              "size": [ "100% - 6px", 20 ], "offset": [ 3, -2 ],
              "anchor_from": "bottom_left", "anchor_to": "bottom_left",
              "controls": [ { "title": { "type": "label", "text": "#title_label", ... } },
                             { "offer_type": { "type": "label", "text": "#offer_type_label", ... } } ]
          } },
          { "offer_button@common.button": { "layer": 4, "default_control": "", ... } }
        ]
    } }
  ]
},

"suggested_content_offers_grid": {
  "type": "grid",
  "size": [ "100% - 24px", "100%" ],
  "grid_item_template": "common_store.suggested_content_offers_grid_item",
  "collection_name": "$offer_collection_name",
  "$suggested_offers_grid_dimensions|default": [ 3, 1 ],
  "grid_dimensions": "$suggested_offers_grid_dimensions"
}
```

- **Proporção do tile**: `33.33333%` de largura (grade 3x1) ou `25%` (`suggested_content_offers_panel_4x1`,
  linha 10378, grade 4x1) × `100%` da altura do painel de cards.
- **Capa/ícone**: `56.25%x` de altura — ou seja, altura = 56,25% da **própria largura do tile**, o que
  força proporção 16:9 (`100/56.25 = 1.7778`) independente do tamanho final na tela.
- **Espaçamento entre tiles**: não há gutter explícito — o `frame` de cada item **overdesenha 1px de
  largura** (`"100% + 1px"`, comentário literal no arquivo: *"work around a layout/rendering rounding
  error that can result in an extra 1 pixel space showing up between items"*), e a capa interna recua
  `"100% - 2px"` — o espaço visual entre cards vem desse recuo de 1-2px dentro de cada slot, não de um
  parâmetro de "gap" do grid.
- **Borda/moldura**: `key_art_frame@common.square_image_border_white` (`ui_common.json:1246-1250`,
  textura `textures/ui/square_image_border_white`), desenhada por cima da capa (`layer: 2`).
- **Hover**: `offer_button@common.button` desenhado por cima de tudo (`layer: 4`) só para capturar
  clique/foco — **não há troca visual de textura no hover neste tile específico** (a variante com
  hover/pressed visível é a de `store_item_list_screen.json`, ver §3).
- **Texto**: **abaixo da capa, dentro do mesmo tile** — `title_label_panel` é um `stack_panel` ancorado
  `bottom_left`, com `title` + `offer_type` empilhados, ocupando a faixa inferior do tile (20px), não
  sobre a imagem.

confidence: confirmado (trecho copiado literalmente, com comentário original do arquivo preservado).

---

## 3. `store_item_list_screen.json` — `store_offer_grid_item_OLD` (linhas 217-260, 261-338, 500-543)

```json
"store_offer_grid_item": {                              // wrapper ativo (linha 217)
  "type": "panel",
  "$store_offer_grid_item_size|default": [ "25%", "100%c+2px" ],
  "size": "$store_offer_grid_item_size",
  "controls": [ { "item@common_store.content_card_offer_item_standard": {
      "size": [ "100%-2px", "56.25%x + 34px" ], ... } } ]
},

"store_offer_grid_item_OLD": {                           // variante completa presente no corpus (linha 243)
  "type": "panel",
  "$store_offer_grid_item_size|default": [ "25%", "56.25%x + 36px" ],
  "controls": [
    { "frame@common_store.store_description_background": {
        "size": [ "100% - 2px", "100% - 2px" ],
        "controls": [
          { "key_art@store_item_list.store_offer_key_art": { "size": ["100% - 2px","56.25%x"], ... } },
          { "title_label_panel": {
              "type": "panel", "size": [ "100% - 6px", 20 ], "offset": [ 3, -14 ],
              "anchor_from": "bottom_left", "anchor_to": "bottom_left", ... } },
          // "This is the border hover/press states and click region, since the controls are complex
          //  it is better to draw a simple white border around the content rather than create 3 sets
          //  of each control when only the border changes"
          { "offer_button@common.button": { "layer": 4, "default_control": "", ... } }
        ]
    } }
  ]
}
```

- **Proporção**: `25%` de largura (grade 4 colunas) × `56.25%x + 36px` de altura — capa 16:9 baseada na
  própria largura **mais** uma faixa fixa de 36px reservada ao texto/preço abaixo.
- **A variante ativa por padrão** (`store_offer_grid_item`, escolhida quando `$content_cards_enabled` é
  falso) referencia `common_store.content_card_offer_item_standard` — **esse controle não está definido em
  nenhum arquivo do corpus fornecido** (não existe `common_store.json`; `store_common.json` usa o
  namespace `common_store` mas não define esse símbolo). confidence: confirmado que a referência é órfã
  neste corpus — a versão realmente inspecionável e completa é a `_OLD`.
- **Borda/moldura**: `common_store.store_description_background` (frame geral do card) +
  `key_art_frame@common.square_image_border_white` ao redor da capa.
- **Hover/pressed**: comentário literal do próprio arquivo (acima) explica a técnica vanilla — em vez de
  redesenhar o card inteiro 3 vezes (default/hover/pressed), desenha-se **uma borda branca simples por
  cima** (`offer_button@common.button`, com filhos nomeados `hover@common.square_image_border_white` /
  `pressed@common.square_image_border_white`, linhas 10234-10281 do `store_common.json` para o equivalente
  em grid de categoria). O botão some as bordas com estado nomeado — é o mecanismo padrão de botão do
  JSON UI (filhos chamados `default`/`hover`/`pressed`/`locked` trocam de visibilidade sozinhos conforme o
  estado do botão pai).
- **Texto**: `title_label_panel` ancorado `bottom_left`, `offset: [3, -14]` — o valor **negativo em Y**
  faz o painel de texto **subir por cima da parte inferior da capa** (sobreposição parcial imagem+texto),
  diferente do tile de `store_common.json` (que fica abaixo, sem sobrepor).

confidence: confirmado para a estrutura e o comentário; **suspeita** quanto a `content_card_offer_item_standard`
ser de fato usado em telas 1.26.44 reais, já que a definição não existe neste corpus.

---

## 4. `world_templates_screen.json` — `world_template_item` (linhas 573-660)

```json
"world_template_content_panel": {
  "type": "stack_panel",
  "orientation": "horizontal",
  "size": [ "100%", "100%" ],
  "variables": [
    { "requires": "$default_state", "$border_texture": "textures/ui/default_indent" },
    { "requires": "$hover_state",   "$border_texture": "textures/ui/world_screenshot_focus_border" },
    { "requires": "$pressed_state", "$border_texture": "textures/ui/world_screenshot_focus_border" },
    { "requires": "$locked_state",  "$border_texture": "textures/ui/default_indent" }
  ],
  "controls": [
    { "world_template_screenshot@world_templates.world_template_screenshot": {} },
    { "world_template_text_panel@world_templates.world_template_text_panel": { "size": [ "fill", "100%" ] } },
    { "lock_panel": { "size": [ "100%c + 4px", "100%" ], "controls": [ { "lock_icon@world_templates.lock_icon": {} } ] } }
  ]
},

"world_template_item": {
  "type": "stack_panel",
  "size": [ "100%", 30 ],
  "orientation": "horizontal",
  "controls": [ { "world_template_item_button@world_templates.world_template_item_button": { "size": ["fill","100% + 1px"] } } ]
}
```

- **Proporção**: este NÃO é um tile quadrado — é uma **linha horizontal fixa de 30px de altura**, largura
  `100%` do grid (`world_template_item_grid`, `size: ["100%","default"]`, linha 638-646). É o padrão
  "lista com miniatura", não "grade de ícones".
- **Borda/moldura**: em vez de overlay separado (como nos dois exemplos acima), aqui a **textura de fundo
  muda de arquivo conforme o estado** (`$border_texture` trocado por `variables/requires`:
  `textures/ui/default_indent` no estado normal/bloqueado, `textures/ui/world_screenshot_focus_border` no
  hover/pressed) — uma segunda técnica de hover vanilla, alternativa à de overlay branco.
- **Hover**: troca de textura de borda (acima), não overlay.
- **Cadeado**: `lock_panel` com `lock_icon`, sobreposto do lado direito, visível via binding
  `#lock_visible` (linha 560-567) — usado para itens bloqueados/premium.
- **Texto**: dentro de `world_template_text_panel` (linhas 375-456) — nome no topo, descrição/versão
  embaixo, ao lado da screenshot (não sobre ela) — texto sempre fora da imagem, à direita.

confidence: confirmado.

---

## 5. `skin_picker_screen.json` — `skins_grid_item` (linhas 699-739)

```json
"skins_grid_item": {
  "type": "panel",
  "anchor_from": "bottom_left", "anchor_to": "bottom_left",
  "size": [ "default", "100%" ],
  "controls": [
    { "clip": { "size": [ "100%", "100% - 2px" ], "offset": [ 0, 2 ], "clips_children": true,
                "controls": [ { "model@skin_model": {} } ] } },
    { "lock@skin_lock": {} },
    { "button@skin_picker.premium_skin_button": {} }
  ]
}
```

- **Proporção**: `size: [ "default", "100%" ]` — a largura é decidida pelo **grid** (não pelo item), a
  altura ocupa 100% da linha do grid. Sem título.
- **Conteúdo**: em vez de imagem estática, o tile hospeda um controle `type: "custom"` (`skin_model`,
  `renderer: "paper_doll_renderer"`) — **preview 3D do skin girando**, não um ícone 2D.
- **Borda/moldura**: nenhuma moldura decorativa própria — só o `clip` que corta o modelo 3D no retângulo
  do tile.
- **Cadeado**: `skin_lock` (`textures/ui/lock`, 8x8px), ancorado `bottom_middle`, visível via
  `#skin_lock_visible` — mesma técnica de overlay do `world_templates`.
- **Hover**: o botão de fato (`skin_picker.skin_button`, base em `ui_common`-style `type: "button"`) fica
  como camada separada por cima; a tela usa `button_mappings` para eventos de hover (`button.premium_skin_hovered`)
  em vez de troca visual local — o feedback visual de hover aqui é delegado a outro consumidor (provável
  painel de detalhe fora do tile), não uma borda no próprio tile.
- **Texto**: **nenhum título dentro do tile** — só ícone/preview + cadeado. É o contraponto ao padrão
  "ícone + título": mostra que nem todo tile vanilla tem texto embutido.

confidence: confirmado.

---

## 6. `persona_cast_character_screen.json` — `cast_single_character_button_panel` (linhas 262-365)

```json
"cast_single_character_button_panel": {
  "type": "panel",
  "size": [ "33%", "100%x" ],
  "controls": [
    { "cast_character_button@common.button": {
        "max_size": [ "100%-2px", "100%-2px" ],
        "anchor_from": "center", "anchor_to": "center",
        "controls": [
          { "background_image": { "type": "image", "size": ["100%","100%"], "texture": "textures/ui/White", "color": "black", "alpha": 0.8 } },
          { "selected@persona_common.selected_border": { "$enable_border": false, "bindings": [...] } },
          { "default@common.empty_panel": {} },
          { "hover@persona_common.focus_border": {} },
          { "pressed@persona_common.focus_border": {} },
          { "button_outline": { "size": ["100%-2px","100%-2px"], "texture": "textures/ui/White",
              "controls": [ { "cast_character_content@persona_cast_character_screen.cast_character_button_content_panel": {} } ] } }
        ]
    } }
  ]
}
```

- **Proporção**: `size: [ "33%", "100%x" ]` — largura `33%` do grid (3 colunas), altura `"100%x"` =
  **100% da própria largura do tile** → **tile perfeitamente quadrado**, autoproporcional independente da
  tela. É o único dos 5 exemplos com essa técnica de "quadrado via `%x`".
- **Borda/moldura**: `background_image` cinza translúcido (`color: black`, `alpha: 0.8`) como base, mais
  `button_outline` (retângulo branco `-2px`) como moldura de conteúdo.
- **Hover**: técnica de **estado nomeado** explícita e didática — filhos literalmente chamados
  `default@common.empty_panel`, `hover@persona_common.focus_border`,
  `pressed@persona_common.focus_border` dentro do botão — o motor do JSON UI troca a visibilidade sozinho
  conforme o estado (`default_control` implícito por convenção de nome). `focus_border`
  (`persona_common.json:65-70`) é uma imagem cuja textura padrão é `textures/ui/focus_border_selected`.
  Há ainda um estado `selected` (`persona_common.selected_border`, textura
  `textures/ui/focus_border_white`) controlado por **binding de coleção**, não por estado de botão —
  usado para marcar "personagem atualmente em uso".
- **Texto**: **não há título de texto no tile** — o conteúdo é o próprio personagem renderizado
  (`cast_character_button_content_panel` → `in_use_grid_item`, uma imagem 20x20 de ícone de status). Assim
  como o `skin_picker`, este é um tile "só visual", sem label.

confidence: confirmado.

---

## 7. Síntese comparativa

| Tela | Proporção do tile | Espaçamento | Borda/moldura | Hover | Texto |
|---|---|---|---|---|---|
| `store_common` (`suggested_content_offers_grid_item`) | `33.33%`/`25%` largura × `100%` altura; capa `56.25%x` (16:9) | overdraw de 1px no frame + recuo de 1-2px na capa (sem gutter de grid) | `square_image_border_white` ao redor da capa | botão clicável sem troca visual própria neste tile | abaixo da capa, dentro do tile (stack_panel `bottom_left`) |
| `store_item_list` (`store_offer_grid_item_OLD`) | `25%` largura × `56.25%x + 36px` altura | recuo `100% - 2px` no frame | `store_description_background` + `square_image_border_white` | overlay de borda branca nomeada (`hover`/`pressed`) por cima do card | sobreposto ao rodapé da capa (`offset` Y negativo) |
| `world_templates` (`world_template_item`) | linha `100%` × `30px` fixo (não é grade quadrada) | nenhum (stack_panel simples) | textura de fundo troca por estado (`default_indent` → `world_screenshot_focus_border`) | **troca de textura de fundo**, não overlay | ao lado da miniatura, nunca sobre ela |
| `skin_picker` (`skins_grid_item`) | largura `default` (definida pelo grid) × `100%` altura | nenhum explícito | nenhuma (só `clips_children`) | delegado a outro painel via `button_mappings` | **sem texto** — só ícone/preview 3D |
| `persona_cast_character_screen` (`cast_single_character_button_panel`) | `33%` × `100%x` (**quadrado perfeito via `%x`**) | `max_size` `-2px` cria a margem entre tiles | `background_image` translúcido + `button_outline` branco | estado nomeado `default`/`hover`/`pressed` (convenção de botão) + `selected` via binding de coleção | **sem texto** — conteúdo é o próprio ícone/avatar |

**Padrão dominante para "texto"**: quando existe título, ele fica **dentro do próprio tile**, ancorado
`bottom_left`/`bottom_middle` — nunca abaixo do tile como elemento irmão externo, e às vezes sobrepondo a
borda inferior da imagem (offset Y negativo). Tiles "só-ícone" (personagem, skin) simplesmente não têm
título — o nome/descrição fica em um painel de detalhe fora da grade.

**Padrão dominante para "hover"**: duas técnicas convivem no vanilla — (1) overlay de borda branca com
filhos nomeados `default`/`hover`/`pressed` por cima do conteúdo (`store_item_list`, `persona_cast_character_screen`,
técnica documentada com comentário explícito no próprio arquivo), e (2) troca da textura de fundo/moldura
via `variables`/`requires` conforme `$hover_state`/`$pressed_state` (`world_templates`). Ambas evitam
duplicar todo o conteúdo do card 3 vezes.

confidence geral da síntese: **provável** (agregação de 5 exemplos confirmados individualmente; não é
prova de que 100% das telas do jogo seguem só esses 2 padrões de hover, apenas os únicos observados nas
telas lidas).
