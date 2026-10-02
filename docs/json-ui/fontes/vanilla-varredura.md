# Varredura de propriedades — Corpus vanilla JSON UI (cliente 1.26.44)

Fonte: `c:/Users/Desktop/Documents/Nova pasta/assets/assets/resource_packs/vanilla/ui/`
Método: `grep -r` literal sobre todo o corpus (arquivos `.json`, incluindo subpastas `csb_sections/`, `marketplace_sdl/`, `realmsPlus_sections/`, `settings_sections/`).

Nota sobre contagem de arquivos: o diretório raiz tem 188 entradas (184 arquivos `.json` de nível raiz + 4 subpastas). Somando os `.json` dentro das 4 subpastas, o corpus real tem **207 arquivos `.json`**. A lista completa está na seção final.

## Tabela de propriedades

| Propriedade | Existe? | Ocorrências (exatas) | Arquivos com match | Tipo de controle observado | Exemplo literal |
|---|---|---|---|---|---|
| `keep_ratio` | Sim | 41 | 19 | `image` (dentro de `panel`) | `csb_sections/csb_banner.json:152` → `"keep_ratio": true,` |
| `clips_children` | Sim | 26 | 15 | `panel` | `mob_effect_screen.json:151` → `"clips_children": true,` |
| `allow_clipping` | Sim | 6 | 4 | `panel` | `pause_screen.json:1290` → `"allow_clipping": false,` |
| `propagate_alpha` | Sim | 15 | 9 | `panel` raiz de tela / `stack_panel` | `game_tip_screen.json:175` → `"propagate_alpha": true,` |
| `enabled` | Sim | 52 (chave `"enabled"`) | 18 | qualquer controle (via `$enabled` ou binding) | `progress_screen.json:141` → `"enabled": "$enabled"` |
| `ignored` | Sim | 941 | 85 | qualquer controle (condição de visibilidade) | `anvil_screen.json:162` → `"ignored": "(not $is_ps4)"` |
| `use_anchored_offset` | Sim | 12 | 3 | `panel`, `stack_panel` | `hud_screen.json:324` → `"use_anchored_offset": true,` |
| `tiled` | Sim | 43 (chave `"tiled"`) | 22 | `image` | `coin_purchase_screen.json:1020` → `"tiled": "x",` |
| `"fill"` (valor de size) | Sim | 667 | 118 | qualquer controle, dentro de `size: [...]` | `authentication_screen.json:261` → `"size": [ "fill", "100%" ],` |
| `%cm` | Sim | 422 | 72 | usado em strings de `size`/`offset` (unidade "content max") | `authentication_modals.json:76` → `"size": [ "100%cm + 8px + 8px", "100%cm + 22px + 8px" ],` |
| `modifications` | **Não** | 0 | 0 | — | (nenhuma ocorrência, nem case-insensitive) |
| `collection_index` | Sim | 55 | 10 | instância de controle referenciado em `controls` (ex.: `radio_item_with_label_and_content`) | `chat_settings_menu_screen.json:151` → `"collection_index": 0,` |
| `variables` | Sim | 277 | 81 | nível raiz de definição de controle (array de laço de variáveis) | `anvil_screen.json:409` → `"variables": [` |
| `binding_condition` | Sim | 502 | 74 | dentro de blocos `bindings` | `authentication_modals.json:13` → `"binding_condition": "once"` |
| `grid_rescaling_type` | Sim | 21 | 19 | `grid` | `anvil_screen_pocket.json:210` → `"grid_rescaling_type": "horizontal",` |
| `grid_fill_direction` | Sim | 2 | 2 | `grid` | `hud_screen.json:3112` → `"grid_fill_direction": "vertical",` |
| `nineslice_size` | **Não** (como chave de propriedade) | 0 | 0 | — | Só aparece como nome de *binding* customizado, não como propriedade de controle: `start_screen.json:1465-1466` → `"binding_name": "#banner_nineslice_size", "binding_name_override": "#nineslice_size",` |

### Observações
- `modifications` e `nine_slice_size` (com underscore) têm 0 ocorrências em qualquer grafia/case.
- `nineslice_size` (sem underscore) não existe como **chave de propriedade** de controle neste corpus; as únicas 2 ocorrências são nomes de binding (`#nineslice_size`, `#banner_nineslice_size`) definidos manualmente em `start_screen.json`, ou seja, não confirma a existência da propriedade nativa com esse nome.
- `enabled` como propriedade direta (`"enabled": false`) é raro — `realms_allowlist.json:273` traz comentário explícito: `// a hack: you cannot set "enabled":false directly on a ui control`, indicando que o padrão real é controlar via binding/`ignored`.

## Índice completo do corpus (`ui/**/*.json`, 207 arquivos)

Gerado por `find . -name "*.json" | sed 's|^\./||' | sort` executado na raiz do corpus vanilla.

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
