# JSON UI — Extração da Documentação da Wiki (Tarefa A)

Fontes lidas (conteúdo idêntico por hash MD5 — arquivos duplicados):
- **json-ui-documentation.md** = wiki_doc.md = wikidoc.md = juidoc.md = doc.md (hash `c2638252...`)
- **best-practices.md** = bp.md = wikibp.md (hash `400b2baf...`)

Todas as citações abaixo usam o nome canônico `json-ui-documentation.md` ou `best-practices.md`; os arquivos-espelho carregam o texto idêntico.

---

## 1. Tipos de controle (`type`) — confirmado (json-ui-documentation.md)

| type | Descrição | Categorias de propriedades que aceita |
|---|---|---|
| `panel` | Container genérico (como `<div>`) | Control, Layout, Data Binding |
| `stack_panel` | Como `panel`, mas empilha filhos conforme `orientation` | Stack Panel, Collection, Control, Layout, Data Binding |
| `collection_panel` | Como `stack_panel`, sem `orientation` | Collection, Control, Layout, Data Binding |
| `grid` | Grade de elementos | Grid, Collection, Control, Layout, Data Binding |
| `label` | Texto | Text, Control, Layout, Data Binding |
| `image` | Sprite/textura | Sprite, Control, Layout, Data Binding |
| `input_panel` | Panel que aceita input | Input, Focus, Sound, Control, Layout, Data Binding |
| `button` | Botão com 4 estados (default, hover, pressed, locked) | Button, Input, Focus, Sound, Control, Layout, Data Binding |
| `toggle` | 2 estados (checked/unchecked), cada um com hover e locked | Toggle, Input, Focus, Sound, Control, Layout, Data Binding |
| `dropdown` | Toggle para dropdown | Dropdown, Toggle, Input, Focus, Sound, Control, Layout, Data Binding |
| `slider` | Input de intervalo | Slider, Input, Focus, Sound, Control, Layout, Data Binding |
| `slider_box` | "Thumb" do slider | Slider Box, Input, Control, Layout, Data Binding |
| `edit_box` | Campo de texto (single-line por padrão) | Text Edit, Button, Input, Focus, Control, Layout, Data Binding |
| `scroll_view` | Panel com scroll | Scroll View, Input, Control, Layout, Data Binding |
| `scrollbar_track` | Trilho da scrollbar | Input, Control, Layout |
| `scrollbar_box` | "Thumb" da scrollbar (vertical por padrão) | Input, Control, Layout |
| `factory` | Gerador de elementos | Control, Layout |
| `screen` | Elemento raiz de tela | Screen, Control, Layout, Data Binding |
| `custom` | Renderer especial criado em código nativo (`renderer`) | Custom Render, Control, Layout, Data Binding |
| `selection_wheel` | Roda de seleção | Selection Wheel, Input, Focus, Sound, Control, Layout, Data Binding |

**Legado (não funciona mais)** — confirmado: `tab`, `carousel_label`, `grid_item`, `scrollbar`.

---

## 2. Propriedades por categoria — confirmado (json-ui-documentation.md)

### 2.1 Control (aplicável a quase todo elemento)

| Propriedade | Tipo | Default | Descrição |
|---|---|---|---|
| `visible` | boolean | `true` | Se o elemento deve ser visível |
| `enabled` | boolean | `true` | Se `false` (ou herdado como locked), elemento/filhos ficam em estado locked |
| `layer` | int | `0` | Z-index relativo ao **elemento pai**. Maior = renderiza acima; negativo = abaixo do pai |
| `alpha` | float | `1.0` | Transparência do elemento. **Só afeta o próprio elemento, não os filhos**, a menos que `propagate_alpha` |
| `propagate_alpha` | boolean | `false` | Faz `alpha` também se aplicar a todos os filhos |
| `clips_children` | boolean | `false` | Corta visual e interativamente tudo além dos limites do elemento |
| `allow_clipping` | boolean | `true` | Se `clips_children` tem efeito. Caso `false`, `clips_children` não faz nada |
| `clip_offset` | Vector [x,y] | `[0,0]` | Offset do início do clipping |
| `clip_state_change_event` | string | — | (sem descrição na doc) |
| `enable_scissor_test` | boolean | — | Ver Scissor Test do OpenGL |
| `property_bag` | object | — | Variáveis/propriedades de dados (ver seção 6) |
| `selected` | boolean | — | Se a caixa de texto é selecionada por padrão |
| `use_child_anchors` | boolean | `false` | Usa `anchor_from`/`anchor_to` do filho |
| `controls` | array | — | Filhos do elemento |
| `anims` | string[] | — | Nomes das animações |
| `disable_anim_fast_forward` | boolean | — | — |
| `animation_reset_name` | string | — | — |
| `ignored` | boolean | `false` | Se o elemento deve ser ignorado (**ver seção 5 — diferença crítica de `visible`**) |
| `variables` | array/object | — | Condições que alteram valores de `$variáveis` |
| `modifications` | array | — | Modifica arquivos de UI de resource packs abaixo (vanilla é o mais "de baixo") |
| `grid_position` | Vector [row,col] | — | Posição do controle dentro de um grid |
| `collection_index` | int | — | Índice do controle na coleção |

**Legado:** `z_order` (int, versão antiga de `layer`), `scroll_report` (string[]), `alignment` (enum: top_left/top_middle/top_right/left_middle/center/right_middle/bottom_left/bottom_middle/bottom_right).

### 2.2 Layout

| Propriedade | Tipo | Default | Descrição |
|---|---|---|---|
| `size` | Vector [w,h] | `["default","default"]` | Ver **seção 3 — unidades de tamanho** |
| `max_size` / `min_size` | Vector [w,h] | `["default","default"]` | Limites de tamanho |
| `offset` | Vector [x,y] | `[0,0]` | Posição relativa ao pai, baseada em top-left `[0,0]`. Aceita `10`, `"10px"`, `"50%"`, `"50%x"`, `"50%y"` |
| `anchor_from` | enum | `center` | Ponto de ancoragem no elemento pai |
| `anchor_to` | enum | `center` | Ponto de ancoragem no próprio elemento |
| `inherit_max_sibling_width` / `_height` | boolean | `false` | Usa a largura/altura máxima do elemento irmão |
| `use_anchored_offset` | boolean | — | — |
| `contained` | boolean | — | — |
| `draggable` | enum (`vertical`/`horizontal`/`both`) | — | Torna o elemento arrastável (precisa aceitar input) |
| `follows_cursor` | boolean | `false` | Segue o cursor |

Valores de `anchor_from`/`anchor_to`: `top_left`, `top_middle`, `top_right`, `left_middle`, `center`, `right_middle`, `bottom_left`, `bottom_middle`, `bottom_right`.

### 2.3 Data Binding

| Propriedade | Tipo | Descrição |
|---|---|---|
| `bindings` | array de "binding object" | Vincula valores/variáveis hardcoded a uma propriedade do elemento |

**Binding object** (dentro de `bindings`):

| Propriedade | Tipo | Descrição |
|---|---|---|
| `ignored` | boolean (default `false`) | Se o binding deve ser ignorado |
| `binding_type` | enum | `global`, `view`, `collection`, `collection_details`, `none` |
| `binding_name` | string | Nome do valor/condição da binding |
| `binding_name_override` | string | Propriedade de destino que recebe o valor de `binding_name` |
| `binding_collection_name` | string | Nome da coleção de itens a usar |
| `binding_collection_prefix` | string | — |
| `binding_condition` | enum | `always`, `always_when_visible`, `visible`, `once`, `none`, `visibility_changed` |
| `source_control_name` | string | Elemento observado |
| `source_property_name` | string | Propriedade lida do `source_control_name` |
| `target_property_name` | string | Propriedade de destino que recebe o valor de `source_property_name` |
| `resolve_sibling_scope` | boolean | Se `true`, só permite selecionar irmão no mesmo control e bloqueia nomes fora do escopo de irmãos, para `source_control_name`. **Se irmão e pai tiverem o mesmo nome, o pai tem prioridade mesmo com `true`** |

### 2.4 Stack Panel
`orientation` (enum, default `vertical`): `vertical` ou `horizontal`.

### 2.5 Grid

| Propriedade | Tipo | Descrição |
|---|---|---|
| `grid_dimensions` | Vector [columns, rows] | Número de colunas/linhas |
| `maximum_grid_items` | int | Máximo de itens gerados |
| `grid_dimension_binding` | string | Binding para as dimensões |
| `grid_rescaling_type` | enum | `vertical`, `horizontal`, `none` |
| `grid_fill_direction` | enum | `vertical`, `horizontal`, `none` |
| `grid_item_template` | string | Elemento capaz de lidar com coleções (ex.: `common.container_item`) |
| `precached_grid_item_count` | int | — |

### 2.6 Text

`text`, `color` (Vector [r,g,b], default `[1,1,1]`), `locked_color`, `shadow` (bool, default `false`), `hide_hyphen`, `notify_on_ellipses` (string[]), `enable_profanity_filter`, `locked_alpha` (float), `font_size` (enum: `small`/`normal`/`large`/`extra_large`, default `normal`), `font_scale_factor` (float, default `1.0`), `localize` (bool, default `false`), `line_padding`, `font_type` (enum: `default`/`rune`/`unicode`/`smooth`/`MinecraftTen`/custom), `backup_font_type`, `text_alignment`.
Legado: `wrap`, `clip` — não funcionam mais.

### 2.7 Sprite (`image`)

`texture` (string, caminho a partir da raiz do pack), `allow_debug_missing_texture` (bool, default `true` — exibe textura "missing" se não achar), `uv`, `uv_size`, `texture_file_system` (enum: `InUserPackage`, `InAppPackage`, `RawPath`, `RawPersistent`, `InSettingsDir`, `InExternalDir`, `InServerPackage`, `InDataDir`, `InUserDir`, `InWorldDir`, `StoreCache`), `nineslice_size`, `tiled` (bool/enum `x`/`y`), `tiled_scale`, `clip_direction` (enum: `left`/`right`/`up`/`down`/`center`), `clip_ratio` (float 0–1), `clip_pixelperfect`, `keep_ratio` (default `true`), `bilinear` (default `false`), `fill` (default `false`), `$fit_to_width`, `zip_folder`, `grayscale`, `force_texture_reload`, `base_size`.

### 2.8 Input / Button Mapping

Input: `button_mappings`, `modal`, `inline_modal`, `always_listen_to_input`, `always_handle_pointer`, `always_handle_controller_direction`, `hover_enabled`, `prevent_touch_input`, `consume_event`, `consume_hover_events` (quando `false`, impede que o elemento seja "hovered"), `gesture_tracking_button`.

Button Mapping object: `ignored`, `from_button_id`, `to_button_id`, `mapping_type` (enum: `global`/`pressed`/`double_pressed`/`focused`), `scope` (enum: `view`/`controller`), `input_mode_condition`, `ignore_input_scope`, `consume_event`, `handle_select`, `handle_deselect`, `button_up_right_of_first_refusal`.

### 2.9 Focus

`default_focus_precedence`, `focus_enabled`, `focus_wrap_enabled`, `focus_magnet_enabled`, `focus_identifier`, `focus_change_down/up/left/right` (aceita `FOCUS_OVERRIDE_STOP` para travar a navegação numa borda), `focus_mapping`, `focus_container`, `use_last_focus`, `focus_navigation_mode_left/right/down/up` (enum: `none`/`stop`/`custom`/`contained`), `focus_container_custom_left/right/down/up` (array de `{other_focus_container_name, focus_id_inside}`).

### 2.10 Button
`default_control`, `hover_control`, `pressed_control`, `locked_control` — nome do filho exibido em cada estado.

### 2.11 Toggle
`radio_toggle_group`, `toggle_name`, `toggle_default_state`, `toggle_group_forced_index`, `toggle_group_default_selected`, `reset_on_focus_lost`, `toggle_on_hover`, `toggle_on_button`, `toggle_off_button`, `enable_directional_toggling`, `toggle_grid_collection_name`, `checked_control`, `unchecked_control`, `checked_hover_control`, `unchecked_hover_control`, `checked_locked_control`, `unchecked_locked_control`, `checked_locked_hover_control`, `unchecked_locked_hover_control`.

Nota (confiança: **provável**, doc marca com ressalva "acho que esses valores estão certos"): existem índices hardcoded de toggle default em telas como settings/inventory (`$search_index - $construction_index`, etc.) e alguns toggles são "obrigatórios" (ex.: abas construction/equipment/items/nature no inventário) controlados por uma função interna do engine — modificar essas telas por completo pode disparar uma assertion.

### 2.12 Dropdown
`dropdown_name`, `dropdown_content_control`, `dropdown_area`.

### 2.13 Sound
`sound_name`, `sound_volume`, `sound_pitch`, `sounds` (array de objetos `{sound_name, sound_volume, sound_pitch, min_seconds_between_plays}`).

### 2.14 Collection
`collection_name` (string) — nome da coleção usada.

### 2.15 Text Edit
`text_box_name`, `text_edit_box_grid_collection_name`, `constrain_to_rect`, `enabled_newline`, `text_type` (enum: `ExtendedASCII`/`IdentifierChars`/`NumberChars`), `max_length`, `text_control`, `place_holder_control`, `can_be_deselected`, `always_listening`, `virtual_keyboard_buffer_control`.

### 2.16 Slider / Slider Box
Slider: `slider_track_button`, `slider_small_decrease_button`, `slider_small_increase_button`, `slider_steps`, `slider_direction` (enum `vertical`/`horizontal`), `slider_timeout`, `slider_collection_name`, `slider_name`, `slider_select_on_hover`, `slider_selected_button`, `slider_deselected_button`, `slider_box_control`, `background_control`, `background_hover_control`, `progress_control`, `progress_hover_control`.
Slider Box: `default_control`, `hover_control`, `locked_control`.

### 2.17 Scroll View
`scrollbar_track_button`, `scrollbar_touch_button`, `scroll_speed`, `gesture_control_enabled`, `always_handle_scrolling`, `touch_mode`, `scrollbar_box`, `scrollbar_track`, `scroll_view_port`, `scroll_content`, `scroll_box_and_track_panel`, `jump_to_bottom_on_update` (pula para o fim ao atualizar/adicionar filhos).

### 2.18 Custom Render
`renderer` (enum extenso: `hover_text_renderer`, `3d_structure_renderer`, `splash_text_renderer`, `ui_holo_cursor`, `trial_time_renderer`, `panorama_renderer`, `actor_portrait_renderer`, `banner_pattern_renderer`, `live_player_renderer`, `web_view_renderer`, `hunger_renderer`, `bubbles_renderer`, `mob_effects_renderer`, `cursor_renderer`, `progress_indicator_renderer`, `camera_renderer`, `horse_jump_renderer`, `armor_renderer`, `horse_heart_renderer`, `heart_renderer`, `hotbar_cooldown_renderer`, `hotbar_renderer`, `hud_player_renderer`, `live_horse_renderer`, `holographic_postrenderer`, `enchanting_book_renderer`, `debug_screen_renderer`, `gradient_renderer`, `paper_doll_renderer`, `name_tag_renderer`, `flying_item_renderer`, `inventory_item_renderer`, `credits_renderer`, `vignette_renderer`, `progress_bar_renderer`, `debug_overlay_renderer`, `background_renderer`, `bohr_model_renderer`, `equipment_preview_renderer`; legado: `experience_renderer`, `menu_background_renderer`).
Propriedades específicas por renderer: `gradient_direction`, `color1`/`color2`, `text_color`/`background_color` (name_tag), `primary_color`/`secondary_color` (progress_bar), `camera_tilt_degrees`, `starting_rotation`, `use_selected_skin`, `use_uuid`, `use_skin_gui_scale`, `use_player_paperdoll`, `rotation` (paper_doll/panorama), `end_event` (credits), `item_id_aux`/`item_custom_color`/`armor_trim_material`/`armor_trim_pattern` (equipment_preview).
Relevante para addons: `inventory_item_renderer` "só funciona em telas quando in-game".

### 2.19 Screen
`render_only_when_topmost`, `screen_not_flushable`, `always_accepts_input`, `render_game_behind` (não impede a tela de baixo de receber input), `absorbs_input`, `is_showing_menu`, `is_modal`, `should_steal_mouse`, `low_frequency_rendering`, `screen_draws_last`, `vr_mode`, `force_render_below`, `send_telemetry`, `close_on_player_hurt`, `cache_screen`, `load_screen_immediately`, `gamepad_cursor`, `gamepad_cursor_deflection_mode`, `should_be_skipped_during_automation`.

### 2.20 Selection Wheel / TTS / Legado (Tab, Carousel Text)
Selection Wheel: `inner_radius`, `outer_radius`, `state_controls`, `slice_count`, `button_name`, `iterate_left_button_name`, `iterate_right_button_name`, `initial_button_slice`.
TTS: `tts_name`, `tts_control_header`, `tts_section_header`, `tts_control_type_order_priority`, `tts_index_priority`, `tts_toggle_on/off`, `tts_override_control_value`, `tts_inherit_siblings`, `tts_value_changed`, `ttsSectionContainer`, `tts_ignore_count`, `tts_skip_message`, `tts_value_order_priority`, `tts_play_on_unchanged_focus_control`, `tts_ignore_subsections`, `text_tts`, `use_priority`, `priority`.
Tab (legado): `tab_index`, `tab_group`, `tab_control`. Carousel Text (legado): `always_rotate`, `rotate_speed`, `hover_color`, `hover_alpha`, `pressed_color`, `pressed_alpha`.

---

## 3. Unidades de tamanho (`size`, `max_size`, `min_size`) — confirmado (json-ui-documentation.md)

| Valor | Significado |
|---|---|
| `"default"` | = `"100%"` |
| `0` | Pixels (número puro) |
| `"0px"` | Pixels como string — usado para somar/subtrair de um valor percentual (ex.: `"75% + 12px"`) |
| `"0%"` | Percentual relativo ao **elemento pai** |
| `"0%c"` | Percentual da largura/altura total dos **filhos** do elemento |
| `"0%cm"` | Percentual da largura/altura do **maior filho visível** |
| `"0%sm"` | Percentual da largura/altura de um **elemento irmão** |
| `"0%y"` | Percentual da própria altura do elemento |
| `"0%x"` | Percentual da própria largura do elemento |
| `"fill"` | Expande até o espaço restante do pai |

`offset` aceita: `10` / `"10px"` (pixels), `"50%"` (do pai), `"50%x"` / `"50%y"` (da própria largura/altura).

Operadores de string/número utilizáveis em `$variáveis` e `#bindings` dentro de `size`/`offset` etc. (json-ui-documentation.md via **intro.md**, ver docs-tecnicos.md): `+`, `-`, `*`, `/`, `=`, `>`, `<`, `and`, `or`, `not`.

---

## 4. Anchors — confirmado (json-ui-documentation.md)
`anchor_from` = ponto no elemento **pai**; `anchor_to` = ponto no **próprio elemento** que se conecta ao ponto de `anchor_from`. Se ambos forem iguais, o elemento fica centrado nesse ponto comum. Se diferentes (ex.: `anchor_from: center`, `anchor_to: top_left`), o ponto `top_left` do elemento é posicionado no ponto `center` do pai.

---

## 5. Alpha, layer, propagate_alpha, visible, ordem de renderização e falha silenciosa (foco pedido)

- **`layer`** (int, default `0`) — z-index **relativo ao pai**; valores maiores renderizam por cima, negativos por baixo do pai. Confirmado, json-ui-documentation.md.
- **`alpha`** (float, default `1.0`) — afeta **somente o próprio elemento**; filhos não são afetados a menos que `propagate_alpha: true` seja setado no pai. Confirmado, json-ui-documentation.md.
- **`propagate_alpha`** (boolean, default `false`) — propaga o alpha do pai para os filhos. Confirmado, json-ui-documentation.md.
- **`visible`** (boolean, default `true`) — controla visibilidade, mas **não remove o controle da avaliação/computação da UI**. Confirmado (best-practices.md): "Using `visible: false` does not have the same effect [de `ignored: true`] and the controls will still be evaluated."
- **`ignored`** (boolean, default `false`) — equivalente a **deletar** o controle: ele e todos os filhos deixam de ser avaliados, com o mesmo ganho de performance de não existir. Confirmado, best-practices.md.
- **Ordem de renderização**: não há uma declaração isolada de "ordem" fora de `layer`; a doc trata `layer` como o único mecanismo declarado de ordenação (substituto do antigo `z_order`). Confirmado, json-ui-documentation.md.
- **`clips_children`/`allow_clipping`**: cortam filhos fora dos limites do elemento (visual e interativamente); `allow_clipping: false` anula esse corte. Confirmado, json-ui-documentation.md.

### Indícios de "falha silenciosa" nos documentos da wiki
1. **Modificação de árvore aninhada com nome de controle-alvo inexistente**: "if the specified target child control name does not exist, it will cause a **resource pack error**. Your UI will function as normal without issue" — ou seja, **há um erro registrado**, mas o jogo continua rodando normalmente (não é 100% silencioso — fica só fora da vista do jogador, no log de erro do resource pack). Confirmado, best-practices.md. **Relevante para o problema do usuário**: se o menu custom depende de `namespace/algum_controle_filho` que não existe (por typo ou por mudança vanilla), isso não trava o jogo nem aparece in-game — só no ContentLog/resource-pack error, o que bate com "some sem log visível ao usuário".
2. **Elementos invisíveis dentro de um Grid ainda ocupam espaço físico**, podendo deixar "gaps" não intencionais — não é um sumiço completo da UI, mas pode ser confundido com um item de grid "desaparecendo". Confirmado, dynamic-content-generation.md (ver docs-tecnicos.md).
3. **`grid_rescaling_type: "vertical"` "pode travar o jogo"** — é um crash documentado, não uma falha silenciosa. Confirmado (aviso `:::danger`), dynamic-content-generation.md.
4. Não foi encontrada, em nenhum dos 5 arquivos-fonte desta tarefa, uma declaração genérica de que "a JSON UI falha silenciosamente sem nenhum log em qualquer circunstância". A doc só documenta o caso (1) acima como gerando log de erro. Confiança da ausência: **suspeita** (não é possível provar uma negativa varrendo só 2 documentos, mas nenhuma menção direta foi localizada).

---

## 6. Property Bag — confirmado (json-ui-documentation.md)
`property_bag` guarda variáveis "locais" ao controle (ex.: `#preserved_text`, `#hover_text`). A doc lista dezenas de chaves conhecidas amarradas a renderers específicos (ex.: `#item_id_aux`, `#banner_patterns` para `inventory_item_renderer`; `#toggle_state` para `type: toggle`; `#slider_value`/`#slider_steps` para `type: slider`). Destaques genéricos, sem amarração a um renderer: `#visible`, `#text`, `#index`, `#collection_name`, `#collection_prefix`, `force_update`, `reset_group` (enum: `video`/`audio`/`accessibility`).

Bindings genéricas cujo valor "depende da tela em que estão" (inclui `server_form.json`): **`#title_text`**, `#body_text`, `#hover_text`, `#cross_out_icon`. Confirmado, json-ui-documentation.md. Isso é a base técnica usada por `modifying-server-forms.md` (ver docs-tecnicos.md) para detectar, via string matching em `#title_text`, se o form atual é o custom ou o vanilla.

No arquivo `server_form.json` a doc lista como coleções conhecidas: `custom_form`, `form_buttons`, `custom_dropdown`. Confirmado, json-ui-documentation.md.

---

## 7. Animações — confirmado (json-ui-documentation.md)
Tipos (`anim_type`): `alpha`, `clip`, `color`, `flip_book`, `offset`, `size`, `uv`, `wait`, `aseprite_flip_book`.
Propriedades: `duration`, `next` (nome da próxima animação ao terminar), `destroy_at_end`, `play_event`, `end_event`, `start_event`, `reset_event`, `easing` (grande lista de curvas: linear, spring, in/out/in_out para quad/cubic/quart/quint/sine/expo/circ/bounce/back/elastic), `from`, `to`, `initial_uv`, `fps`, `frame_count`, `frame_step`, `reversible`, `resettable`, `scale_from_starting_alpha`, `activated`.

---

## 8. Boas práticas (best-practices.md) — confirmado

### 8.1 Compatibilidade
- JSON-UI é **não versionada**; qualquer alteração pode quebrar quando a Mojang atualiza a UI vanilla.
- **Modifique só o necessário**: incluir bindings/anchors/offsets redundantes ao lado da propriedade que você realmente quer mudar aumenta o risco de quebra quando a Mojang mudar nomes de binding/anchors. Se você está reproduzindo o conteúdo inteiro de um arquivo vanilla no seu pack "você está fazendo JSON-UI errado".
- **Use `modifications`** (insert_front/insert_back/etc., ver seção 9) em vez de mesclar direto no `root_panel` — reduz a chance de quebra quando a Mojang mudar nomes de controle irmãos.
- **Evite modificar árvores aninhadas**; prefira mudar a definição do elemento em vez do elemento dentro da árvore. Quando inevitável, use a sintaxe `"pai/filho": {...}` (e `"pai/filho/neto"` para vários níveis) para atingir controles aninhados — mas nome de controle-alvo inexistente gera erro de resource pack (ver seção 5, item 1).
- **Use um único ponto de entrada** (entry point) por tela para mesclar sua UI customizada com a vanilla — reduz pontos de falha e facilita debug.
- **Evite trabalhar em namespaces vanilla**: para adições grandes, crie um namespace próprio no `_ui_defs.json` e referencie via `elemento@namespace.elemento`. Um prefixo tipo `wiki:namespace` também ajuda a evitar colisão.

### 8.2 Performance
- JSON-UI é o **segundo subsistema mais custoso de FPS** (atrás só de entidades); é "incrivelmente desotimizado".
- **Minimize operadores** (`+`, `-`, `*`, `/`, comparação lógica) — cada um adiciona overhead de avaliação; simplifique expressões (ex.: `(2 * (-1 * $x))` → `(-2 * $x)`).
- **Minimize bindings** — cada binding adicional soma overhead (é citado como razão de a tela de settings demorar pra abrir).
- **Evite controles desnecessários** — um `panel` vazio sem função deve ser deletado ou marcado `"ignored": true` (equivalente a deletar); `"visible": false"` **não** dá esse ganho de performance porque o controle continua sendo avaliado.
- Prefira consolidar múltiplos controles quase-idênticos (ex.: 5 imagens condicionais por binding_text) em um único controle parametrizado por binding, reduzindo controles/bindings/operadores totais.
