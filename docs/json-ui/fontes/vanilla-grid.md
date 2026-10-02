# Grids e listas dinâmicas em JSON UI — corpus vanilla 1.26.44

Corpus: `c:/Users/Desktop/Documents/Nova pasta/assets/assets/resource_packs/vanilla/ui/` (188 arquivos .json).
Metodologia: grep literal + parser de blocos por contagem de chaves (script Python ad-hoc) sobre TODAS as ocorrências de `"type": "grid"`. Toda contagem abaixo é reprodutível pelos comandos citados.

---

## 0. Arquivos pedidos — o que existe de fato

| Arquivo pedido | Existe? | Observação |
|---|---|---|
| `chest_screen.json` | Sim | namespace `chest`. Grids fixos em px (`small_chest_grid` 9x3, `large_chest_grid` 9x6). |
| `inventory_screen.json` | Sim | namespace real é **`crafting`** (não "inventory"). Contém armor/offhand/crafting grids fixos + `scroll_grid` (recipe book, dinâmico). |
| `container_screen.json` | **Não existe** | confirmado por `ls` no corpus — não há arquivo com esse nome. |
| `hotbar_*.json` | **Não existe nenhum arquivo com esse padrão** | o hotbar vanilla vive em `ui_common.json` (`common.hotbar_grid_template`, grid 9x1 fixo) e é referenciado por `@common.hotbar_grid_template` em `chest_screen.json`, `redstone_screen.json`, `inventory_screen.json` etc. Também há `#hotbar_grid_dimensions` (binding dinâmico) em `hud_screen.json` para o HUD. |

confidence: confirmado (checado com `ls` direto no diretório, 188 arquivos, nomes exatos listados).

---

## 1. Tabela completa — TODOS os grids do vanilla (134 ocorrências de `"type": "grid"`)

Contagem de `grep -c '"type":\s*"grid"'` recursivo no corpus: **134 ocorrências em 65 arquivos**.
(Um levantamento anterior citou "144 grids" — não bate com este corpus/versão. O número correto e verificado aqui é **134**.)

| Arquivo | Controle | grid_dimensions | grid_dimension_binding | collection_name | grid_item_template | grid_rescaling_type | size | factory | #maximum_grid_items (literal) | #maximum_grid_items (fonte do binding) |
|---|---|---|---|---|---|---|---|---|---|---|
| anvil_screen.json | recipe_grid | [ 5, 1 ] | - | - | - | - | [ "83%", "40%" ] | nao | - | - |
| anvil_screen_pocket.json | inventory_grid | - | - | combined_hotbar_and_inventory_items | common.pocket_ui_container_item | horizontal | [ "100%", "default" ] | nao | 36 | - |
| beacon_screen_pocket.json | inventory_grid | - | - | combined_hotbar_and_inventory_items | common.pocket_ui_container_item | horizontal | [ "100%", "default" ] | nao | 36 | - |
| book_screen.json | book_grid | [ 2, 1 ] | - | book_pages | - | - | - | nao | - | - |
| brewing_stand_screen.json | brewing_output_slots | [ 3, 1 ] | - | brewing_result_items | - | - | [ 54, 18 ] | nao | - | - |
| brewing_stand_screen_pocket.json | brewing_out_slots | [ 3, 1 ] | - | brewing_result_items | - | - | [ 130, 42 ] | nao | - | - |
| brewing_stand_screen_pocket.json | inventory_grid | - | - | combined_hotbar_and_inventory_items | common.pocket_ui_container_item | horizontal | [ "100%", "default" ] | nao | 36 | - |
| bundle_purchase_warning_screen.json | bundle_grid | - | $bundle_grid_dimension | $bundle_collection_name | bundle_purchase_warning.bundle_grid_item | - | [ "100%", "default" ] | nao | - | - |
| chat_screen.json | auto_complete_grid | - | - | auto_complete | chat.auto_complete_panel_contents_with_item | - | [ "100%", "100%" ] | nao | - | - |
| chest_screen.json | small_chest_grid | [ 9, 3 ] | - | container_items | chest.chest_grid_item | - | [ 162, 54 ] | nao | - | - |
| chest_screen.json | large_chest_grid | [ 9, 6 ] | - | container_items | chest.chest_grid_item | - | [ 162, 108 ] | nao | - | - |
| choose_realm_screen.json | realms_world_item_grid | - | #realms_grid_dimension | realms_collection | choose_realm.realms_world_item | - | [ "100%", "default" ] | nao | - | - |
| coin_purchase_screen.json | coin_purchase_grid | - | #coin_offer_size | coin_purchase_grid | coin_purchase.offer_grid_item | - | [ "100%", "fill" ] | nao | - | - |
| crafter_screen_pocket.json | crafter_input_grid | [ 3, 3 ] | - | container_items | crafter_pocket.crafter_enabled_slot_template | - | - | nao | - | - |
| create_world_upsell_screen.json | realm_grid | - | #realm_grid_dimension | realm_list | create_world_upsell.create_world_upsell_grid_item | - | [ "100%", "default" ] | nao | - | - |
| create_world_upsell_screen.json | world_grid | - | #world_grid_dimension | world_list | create_world_upsell.create_world_upsell_grid_item | - | [ "100%", "default" ] | nao | - | - |
| custom_templates_screen.json | templates_item_grid | - | #templates_grid_dimension | templates_collection | custom_templates.templates_item | - | [ "100%", "default" ] | nao | - | - |
| enchanting_screen.json | dust_panel | [ 1, 3 ] | - | #enchant_buttons | - | - | - | nao | - | - |
| enchanting_screen.json | item_grid | [ 1, 1 ] | - | enchanting_input_items | - | - | [ 18, 18 ] | nao | - | - |
| enchanting_screen.json | lapis_grid | [ 1, 1 ] | - | enchanting_lapis_items | - | - | [ 18, 18 ] | nao | - | - |
| enchanting_screen.json | enchantments_grid | [ 1, 3 ] | - | #enchant_buttons | enchanting.enchant_button_panel | - | [ "100%", "100%" ] | nao | - | - |
| enchanting_screen_pocket.json | inventory_grid | - | - | combined_hotbar_and_inventory_items | common.pocket_ui_container_item | horizontal | [ "100%", "default" ] | nao | 36 | - |
| enchanting_screen_pocket.json | grid | [ 1, 3 ] | - | #enchant_buttons | - | - | [ "100%", "100%" ] | nao | - | - |
| expanded_skin_pack_screen.json | skins_grid | - | - | skin_pack_collection | expanded_skin_pack.skins_grid_item | horizontal | [ "100% - 8px", "default" ] | nao | - | #skins_grid_dimensions |
| furnace_screen.json | scroll_grid | - | - | $collection_name | $grid_item_template | horizontal | [ "100%", "default" ] | nao | - | #recipe_book_total_items |
| gamepad_layout_screen.json | gamepad_action_grid | - | #gamepad_action_item_grid_dimension | gamepad_action_items | gamepad_action_items | - | [ "100%", "default" ] | nao | - | - |
| gameplay_common.json | item_grid | - | #bundle_tooltip_grid_dimensions | bundle_items | $bundle_tooltip_slot_type | - | - | nao | - | - |
| grindstone_screen_pocket.json | inventory_grid | - | - | combined_hotbar_and_inventory_items | common.pocket_ui_container_item | horizontal | [ "100%", "default" ] | nao | 36 | - |
| horse_screen.json | equip_grid | - | #equip_grid_dimensions | horse_equip_items | @common.container_item | - | - | nao | - | - |
| horse_screen.json | inv_grid | - | #inv_grid_dimensions | container_items | @common.container_item | - | - | nao | - | - |
| horse_screen_pocket.json | base_grid | - | - | $pane_collection | common.pocket_ui_container_item | horizontal | [ "100% - 4px", "default" ] | nao | "$container_size" | - |
| horse_screen_pocket.json | equip_grid | - | #equip_grid_dimensions | horse_equip_items | horse_pocket.equip_item_panel | - | - | nao | - | - |
| host_options_screen.json | host_grid | - | $grid_dimension_binding | $grid_collection_name | $grid_item_template | - | [ "100%", "default" ] | nao | - | - |
| hud_screen.json | hotbar_grid | - | #hotbar_grid_dimensions | $hotbar_collection_name | hud.gui_hotbar_grid_item | - | - | nao | - | - |
| hud_screen.json | edu_hotbar_grid | - | #hotbar_grid_dimensions | $hotbar_collection_name | hud.gui_hotbar_grid_item | - | - | nao | - | - |
| hud_screen.json | boss_health_grid | - | #boss_grid_dimension | boss_bars | hud.boss_health_panel | - | [ 182, "30%" ] | nao | - | - |
| hud_screen.json | sub_panel_content | - | #layout_customization_dimension | $customization_option_collection_name | hud.layout_customization_option | - | [ "100%", "100%" ] | nao | - | - |
| inventory_screen.json | armor_grid | [ 1, 4 ] | - | $item_collection_name | - | - | [ 18, 72 ] | nao | - | - |
| inventory_screen.json | offhand_grid | [ 1, 1 ] | - | $item_collection_name | - | - | [ 18, 18 ] | nao | - | - |
| inventory_screen.json | crafting_grid_3x3 | [ 3, 3 ] | - | crafting_input_items | - | - | [ 54, 54 ] | nao | - | - |
| inventory_screen.json | crafting_grid_2x2 | [ 2, 2 ] | - | crafting_input_items | - | - | [ 36, 36 ] | nao | - | - |
| inventory_screen.json | output_grid_3x3 | [ 1, 1 ] | - | crafting_output_items | - | - | [ 26, 26 ] | nao | - | - |
| inventory_screen.json | output_grid_2x2 | [ 1, 1 ] | - | crafting_output_items | - | - | [ 18, 18 ] | nao | - | - |
| inventory_screen.json | scroll_grid | - | - | $collection_name | $grid_item_template | horizontal | [ "100%", "default" ] | nao | - | #recipe_book_total_items |
| inventory_screen_pocket.json | crafting_grid_3x3 | [ 3, 3 ] | - | crafting_input_items | crafting_pocket.crafting_input_grid_item | - | [ 84, 84 ] | nao | - | - |
| inventory_screen_pocket.json | crafting_grid_2x2 | [ 2, 2 ] | - | crafting_input_items | crafting_pocket.crafting_input_grid_item | - | [ 56, 56 ] | nao | - | - |
| inventory_screen_pocket.json | output_grid | [ 1, 1 ] | - | crafting_output_items | - | - | [ 28, 28 ] | nao | - | - |
| inventory_screen_pocket.json | armor_grid | [ 1, 4 ] | - | $item_collection_name | - | - | [ 28, 112 ] | nao | - | - |
| inventory_screen_pocket.json | offhand_grid | [ 1, 1 ] | - | $item_collection_name | - | - | [ 28, 28 ] | nao | - | - |
| inventory_screen_pocket.json | hotbar_grid | [ 9, 1 ] | - | hotbar_items | crafting_pocket.hotbar_grid_item | - | [ 252, 28 ] | nao | - | - |
| invite_screen.json | online_xbox_live_friend_list_grid | - | #online_xbox_live_friend_grid_dimension | $collection_name | online_xbox_live_friend_grid_item | - | [ "100%", "default" ] | nao | - | - |
| invite_screen.json | offline_xbox_live_friend_list_grid | - | #offline_xbox_live_friend_grid_dimension | $collection_name | offline_xbox_live_friend_grid_item | - | [ "100%", "default" ] | nao | - | - |
| invite_screen.json | online_platform_friend_list_grid | - | #online_platform_friend_grid_dimension | $collection_name | online_platform_friend_grid_item | - | [ "100%", "default" ] | nao | - | - |
| invite_screen.json | offline_platform_friend_list_grid | - | #offline_platform_friend_grid_dimension | $collection_name | offline_platform_friend_grid_item | - | [ "100%", "default" ] | nao | - | - |
| invite_screen.json | online_linked_account_friend_list_grid | - | #online_linked_account_friend_grid_dimension | $collection_name | online_linked_account_friend_grid_item | - | [ "100%", "default" ] | nao | - | - |
| invite_screen.json | offline_linked_account_friend_list_grid | - | #offline_linked_account_friend_grid_dimension | $collection_name | offline_linked_account_friend_grid_item | - | [ "100%", "default" ] | nao | - | - |
| loom_screen.json | scroll_grid | - | - | $collection_name | $grid_item_template | horizontal | [ "100%", "default" ] | nao | - | #pattern_selector_total_items |
| mob_effect_screen.json | mob_effect_grid | - | #mob_effect_grid_size | mob_effects_collection | mob_effect.mob_effect_grid_item | - | [ 150, "default" ] | nao | - | - |
| npc_interact_screen.json | skins_grid | - | #skins_grid_dimensions | skins_collection | npc_interact.skins_grid_item | - | [ 160, 65 ] | nao | - | - |
| npc_interact_screen.json | actions | - | #student_button_grid_dimensions | student_buttons_collection | npc_interact.student_button | - | [ "fill", "default" ] | nao | - | - |
| pause_screen.json | players_grid | - | #players_grid_dimension | players_collection | pause.player_grid_item | - | [ "100%", "default" ] | nao | - | - |
| pdp_screen.json | user_rating_star_list_grid | - | #ratings_star_dimensions | ratings_star_collection | pdp.user_rating_star_button | - | [ "100%", "default" ] | nao | - | - |
| pdp_screen.json | bundle_thumbnail_grid | - | $bundle_thumbnail_grid_dimension_binding | $mashup_collection_name | pdp.bundle_thumbnail | - | [ "100%", "100%c" ] | nao | - | - |
| pdp_screen.json | bundle_grid | - | $bundle_offer_grid_dimension_binding | $mashup_collection_name | pdp.bundle_offer_summary_grid_item | - | [ "100%", "default" ] | nao | - | - |
| permissions_screen.json | players_grid | - | #players_grid_dimension | players_collection | permissions.player_grid_item | - | [ "100%", "default" ] | nao | - | - |
| permissions_screen.json | permissions_options_grid | - | #permissions_grid_dimension | permissions_collection | permissions.permissions_options_grid_item | - | [ "100%", "default" ] | nao | - | - |
| persona_cast_character_screen.json | cast_grid | - | #cast_character_options_dimensions | cast_character_options | persona_cast_character_screen.cast_single_character_button_panel | - | [ "100%", "100%c" ] | nao | - | - |
| persona_sdl.json | color_grid | - | #color_single_page_size | color_collection | persona_sdl.color_grid_item | horizontal | [ "100% - 2px", "100%c + 2px" ] | nao | - | #color_single_page_size |
| persona_sdl.json | skins_grid | - | $skin_dimension_binding | $skin_collection_name | persona_sdl.persona_skin_button_for_pack_view | - | [ "80%", "30%x" ] | nao | - | - |
| persona_sdl.json | skin_pack_grid | - | $skin_pack_dimension_binding | $skin_pack_collection_name | persona_sdl.persona_skin_pack_panel | - | [ "100% - 4px", "100%c" ] | nao | - | - |
| persona_sdl.json | expanded_skin_grid | - | $skin_dimension_binding | $skin_collection_name | persona_sdl.persona_skin_picker_skin_button | - | [ "100% - 4px", "100%c + 2px" ] | nao | - | - |
| play_screen.json | world_item_grid_base | - | - | - | - | - | [ "100%", "default" ] | nao | - | - |
| play_screen.json | more_servers_grid | - | #servers_network_world_item_grid_dimension | servers_network_worlds | more_servers_world_item | - | [ "100%", "default" ] | nao | - | - |
| play_screen.json | third_party_featured_server_grid | - | #third_party_featured_item_grid_dimension | third_party_server_network_worlds | featured_server_world_item | - | [ "100%", "default" ] | nao | - | - |
| play_screen.json | placeholder_loading_personal_realms | - | #loading_personal_realms_grid_dimension | loading_personal_realms | play.empty_grid | - | [ "100%", "default" ] | nao | - | - |
| play_screen.json | placeholder_loading_friends_realms | - | #loading_friends_realms_grid_dimension | loading_friends_realms | play.empty_grid | - | [ "100%", "default" ] | nao | - | - |
| pocket_containers.json | inventory_grid | - | - | $pane_collection | common.pocket_ui_container_item | horizontal | [ "100%", "default" ] | nao | "$container_size" | - |
| portfolio_screen.json | photo_list_grid | [ 2, 1 ] | - | photos | photo_grid_item | - | - | nao | - | - |
| progress_screen.json | required_resource_pack_list_grid | - | #required_resource_pack_grid_dimension | required_resourcepacks | progress.resource_pack_grid_item | - | [ "100%", "100%c" ] | nao | - | - |
| progress_screen.json | optional_resource_pack_list_grid | - | #optional_resource_pack_grid_dimension | optional_resourcepacks | progress.resource_pack_grid_item | - | [ "100%", "100%c" ] | nao | - | - |
| realms_pending_invitations.json | gamertag_item_grid | - | #gamertag_item_grid_dimension | pending_invites_collection | realms_pending_invitations.gamertag_item | - | [ "100%", "default" ] | nao | - | - |
| realms_settings_screen.json | branches_grid | - | #realms_branch_grid_dimension | realms_branch_collection | realms_settings.branch_item_template | - | [ "100%", "default" ] | nao | - | - |
| redstone_screen.json | redstone_input_grid | $grid_dimensions (var) | - | container_items | common.container_item | - | - | nao | - | - |
| redstone_screen.json | crafter_input_grid | $grid_dimensions (var) | - | container_items | redstone.crafter_enabled_slot_template | - | - | nao | - | - |
| skin_pack_purchase_screen.json | skins_grid | - | #skins_grid_dimensions | skins_collection | skin_pack_purchase.skins_grid_item | - | - | nao | - | - |
| skin_picker_screen.json | skins_grid | - | #premium_skins_grid_dimensions | premium_skins_collection | skin_picker.skins_grid_item | - | - | nao | - | - |
| skin_picker_screen.json | premium_packs_grid | - | #premium_packs_grid_dimensions | premium_packs_collection | skin_picker.pack_grid_item | - | - | nao | - | - |
| skin_picker_screen.json | default_skins_grid | - | #default_skins_grid_dimensions | default_skins_collection | skin_picker.default_skins_grid_item | - | [ "100%", "100%" ] | nao | - | - |
| skin_picker_screen.json | recent_skins_grid | - | #recent_skins_grid_dimensions | recent_skins_collection | skin_picker.recent_skins_grid_item | - | [ "100%", "100%" ] | nao | - | - |
| smithing_table_2_screen.json | recipe_grid | [ 9, 1 ] | - | - | - | - | [ "100%", "90%" ] | nao | - | - |
| smithing_table_2_screen_pocket.json | smithing_table_contents_panel | [ 5, 5 ] | - | - | - | - | [ "100%-40px", "100%-40px" ] | nao | - | - |
| smithing_table_screen.json | recipe_grid | [ 5, 1 ] | - | - | - | - | [ "83.5%", "90%" ] | nao | - | - |
| smithing_table_screen_pocket.json | inventory_grid | - | - | combined_hotbar_and_inventory_items | common.pocket_ui_container_item | horizontal | [ "100%", "default" ] | nao | 36 | - |
| stonecutter_screen.json | scroll_grid | - | - | $collection_name | $grid_item_template | horizontal | [ "100%", "default" ] | nao | - | #stone_selector_total_items |
| store_common.json | suggested_content_offers_grid | - | - | $offer_collection_name | common_store.suggested_content_offers_grid_item | - | [ "100% - 24px", "100%" ] | nao | - | - |
| store_item_list_screen.json | store_offer_grid | - | - | $store_offer_grid_collection_name | $grid_item_template | horizontal | [ "100% + 2px", "100%c + 4px" ] | nao | - | #max_grid_offers |
| store_item_list_screen.json | persona_offer_grid | - | - | $persona_piece_collection_name | persona_sdl.persona_piece_offer | horizontal | [ "100%", "100%c" ] | nao | - | #max_grid_offers |
| store_item_list_screen.json | vertical_store_offer_grid | - | - | $store_offer_grid_collection_name | $grid_item_template | vertical | [ "100% + 2px", "100%c + 4px" ] | nao | - | #max_grid_offers |
| store_promo_timeline_screen.json | promo_multi_item_grid | - | - | $tooltip_button_collection_name | promo_timeline.promo_grid_item | horizontal | [ "100%", "100%c" ] | nao | - | #promo_grid_offers |
| store_promo_timeline_screen.json | promo_skin_pack_grid | - | #skin_pack_dimensions | skin_pack_collection | promo_timeline.promo_skin_panel | - | [ "100%", "100%c" ] | nao | - | - |
| store_promo_timeline_screen.json | persona_skin_pack_category_grid | - | $skin_dimension_binding | $skin_collection_name | persona_sdl.persona_skin_picker_skin_button | - | [ "100%", "100%c" ] | nao | - | - |
| store_search_screen.json | trending_offers_grid | - | #trending_offers_dimensions | $offer_collection_name | store_search.store_offer_grid_item | - | [ "100%", "14.0625%x + 33px" ] | nao | - | - |
| store_search_screen.json | trending_rows_grid | - | #trending_rows_dimensions | $store_row_collection_name | store_search.trending_row_content | - | [ "100%", "default" ] | nao | - | - |
| structure_editor_screen.json | axis_grid | [ 1, 3 ] | - | $grid_axis_collection_name | - | - | [ "100%", "100%c" ] | nao | - | - |
| trade_2_screen.json | single_item_grid | [ 1, 1 ] | - | - | - | - | [ "100%c", "100%c" ] | nao | - | - |
| trade_screen.json | purchase_grid | [ 4, 1 ] | - | - | - | - | [ "84%", "90%" ] | nao | - | - |
| trade_screen_pocket.json | purchase_grid | [ 4, 1 ] | - | - | - | - | [ 120, 60 ] | nao | - | - |
| trade_screen_pocket.json | inventory_grid | - | - | combined_hotbar_and_inventory_items | common.pocket_ui_container_item | horizontal | [ "100%", "default" ] | nao | 36 | - |
| ugc_viewer_screen.json | grid_content | - | - | ugc_items | ugc_viewer.grid_item | horizontal | [ "100%", "default" ] | nao | - | #ugc_max_grid_items |
| ui_common.json | container_grid | - | - | $item_collection_name | $grid_item_template | horizontal | [ "100%", "default" ] | nao | - | #collection_total_items |
| ui_common.json | hotbar_grid_template | [ 9, 1 ] | - | hotbar_items | common.grid_item_for_hotbar | - | [ 162, 18 ] | nao | - | - |
| ui_common.json | inventory_grid | [ 9, 3 ] | - | inventory_items | common.grid_item_for_inventory | - | [ 162, 54 ] | nao | - | - |
| ui_purchase_common.json | screenshots_grid | - | #screenshots_grid_dimensions | category_collection | purchase_common.screenshots_grid_item | - | [ "100%c", "100% - 4px" ] | nao | - | - |
| ui_purchase_common.json | offer_grid | - | #offer_grid_dimensions | offer_collection | store.offer_grid_item | - | [ "100%c", "100%" ] | nao | - | - |
| win10_trial_conversion_screen.json | pack_list_grid | - | $grid_dimension | $collection_name | win10_trial_conversion.grid_item_vertical | - | [ "100%", "100%c" ] | nao | - | - |
| world_templates_screen.json | world_template_item_grid | - | #world_template_item_grid_dimension | world_templates | world_templates.world_template_item | - | [ "100%", "default" ] | nao | - | - |
| world_templates_screen.json | custom_world_template_item_grid | - | #custom_world_template_item_grid_dimension | custom_world_templates | world_templates.world_template_item | - | [ "100%", "default" ] | nao | - | - |
| settings_sections/controls_section.json | keymapping_grid | - | $keymapping_grid_dimension | $keymapping_collection | controls_section.keymapping_item_parent | - | [ "100%", "default" ] | nao | - | - |
| settings_sections/controls_section.json | gamepad_mapping_grid | - | $keymapping_grid_dimension | $keymapping_collection | controls_section.gamepad_mapping_item | - | [ "100%", "default" ] | nao | - | - |
| settings_sections/general_section.json | language_list_grid | - | #language_grid_dimension | languages | general_section.language_grid_item | - | [ "100%", "100%c" ] | nao | - | - |
| settings_sections/general_section.json | treatment_grid | - | #treatments_grid_dimension | treatment_collection | general_section.treatment_grid_item | - | [ "100%", "100%c" ] | nao | - | - |
| settings_sections/general_section.json | unused_treatment_grid | - | #unused_treatments_grid_dimension | unused_treatment_collection | general_section.unused_treatment_grid_item | - | [ "100%", "100%c" ] | nao | - | - |
| settings_sections/general_section.json | configuration_grid | - | #configurations_grid_dimension | configuration_collection | general_section.configuration_grid_item | - | [ "100%", "100%c" ] | nao | - | - |
| settings_sections/general_section.json | realms_features_grid | - | #realms_features_grid_dimension | realms_features_collection | general_section.realms_feature_grid_item | - | [ "100%", "100%c" ] | nao | - | - |
| settings_sections/general_section.json | unused_realms_features_grid | - | #unused_realms_features_grid_dimension | unused_realms_features_collection | general_section.unused_realms_feature_grid_item | - | [ "100%", "100%c" ] | nao | - | - |
| settings_sections/general_section.json | available_gatherings_grid | - | #gatherings_grid_dimension | gatherings_collection | general_section.gathering_item_template | - | [ "100%", "default" ] | nao | - | - |
| settings_sections/general_section.json | new_edu_create_world_screen_radio_button | - | #dev_new_edu_create_world_screen_radio_dimension | dev_new_edu_create_world_screen_radio | general_section.new_edu_create_world_screen_grid_item | - | ["100%", "100%c"] | nao | - | - |
| settings_sections/general_section.json | new_play_screen_radio_button | - | #dev_new_play_screen_radio_dimension | dev_new_play_screen_radio | general_section.new_play_screen_grid_item | - | ["100%", "100%c"] | nao | - | - |
| settings_sections/general_section.json | new_edit_world_screen_radio_button | - | #dev_new_edit_world_screen_radio_dimension | dev_new_edit_world_screen_radio | general_section.new_edit_world_screen_grid_item | - | ["100%", "100%c"] | nao | - | - |
| settings_sections/general_section.json | new_send_invites_screen_radio_button | - | #dev_new_send_invites_screen_radio_dimension | dev_new_send_invites_screen_radio | general_section.new_send_invites_screen_grid_item | - | ["100%", "100%c"] | nao | - | - |
| settings_sections/general_section.json | new_death_screen_radio_button | - | #dev_new_death_screen_radio_dimension | dev_new_death_screen_radio | general_section.new_death_grid_item | - | ["100%", "100%c"] | nao | - | - |
| settings_sections/general_section.json | new_bed_screen_radio_button | - | #dev_new_bed_screen_radio_dimension | dev_new_bed_screen_radio | general_section.new_bed_grid_item | - | ["100%", "100%c"] | nao | - | - |
| settings_sections/general_section.json | ore_ui_gameplay_ui_radio_button | - | #dev_ore_ui_gameplay_ui_radio_dimension | dev_ore_ui_gameplay_ui_radio | general_section.ore_ui_gameplay_ui_grid_item | - | ["100%", "100%c"] | nao | - | - |
| settings_sections/general_section.json | new_settings_screen_radio_button | - | #dev_new_settings_screen_radio_dimension | dev_new_settings_screen_radio | general_section.new_settings_screen_grid_item | - | ["100%", "100%c"] | nao | - | - |

**Padrão claro nas 134 linhas**: cada grid usa **ou** `grid_dimensions` literal `[N,M]` (crafting 3x3/2x2, armadura 1x4, chest 9x3/9x6, hotbar 9x1 — sempre com `size` em px) **ou** `grid_dimension_binding`/binding para `#maximum_grid_items` (listas de tamanho variável — realms, skins, players, recipe book — quase sempre com `size` em `%`/`default`/`100%c`). As duas únicas exceções literais são `redstone_screen.json` (`"grid_dimensions": "$grid_dimensions"` — variável repassada pelo pai, resolvida em tempo de instância para um array fixo) e `host_options_screen.json` (`"grid_dimension_binding": "$grid_dimension_binding"` — indireção de variável). Nenhuma das 134 mistura os dois mecanismos no mesmo controle.

confidence: confirmado.

---

## 2. Disputa #3 — `#form_button_contents` vs `#form_button_length`

Grep no corpus inteiro:

```
grep -rn "form_button_contents" vanilla/ui/   → 1 ocorrência, em server_form.json:140
grep -rn "form_button_length"   vanilla/ui/   → 0 ocorrências
```

Trecho literal, `server_form.json` linhas 119-144 (`server_form.long_form_dynamic_buttons_panel`):

```json
"long_form_dynamic_buttons_panel": {
  "type": "stack_panel",
  "size": ["100% - 4px", "100%c"],
  "offset": [2,0],
  "orientation": "vertical",
  "anchor_from": "top_middle",
  "anchor_to": "top_middle",

  "factory":{
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
    {
      "binding_name": "#form_button_contents",
      "binding_name_override": "#collection_length"
    }
  ]
}
```

**Veredicto**: o nome real é **`#form_button_contents`**. `#form_button_length` não existe em lugar nenhum do corpus vanilla — é fabricação/confusão de um dos estudos anteriores (provavelmente por analogia com `#custom_form_length`, que é um nome real usado em outro form, o `custom_form`, linha 301 do mesmo arquivo, para o mesmo padrão).

**Mas atenção ao detalhe que os dois estudos anteriores erraram por igual**: `#form_button_contents` **não alimenta um `grid`**. O controle `long_form_dynamic_buttons_panel` é um **`stack_panel` com `factory`**, não `"type": "grid"`. O binding aponta para `binding_name_override: "#collection_length"` (a propriedade de contagem de um `factory`/`stack_panel`), **não** para `"#maximum_grid_items"` (a propriedade de contagem de um `grid`). O ActionFormData vanilla nativo (`long_form`) é sempre renderizado como lista vertical via factory — nunca como grid. Portanto:
- Usar `#form_button_contents` para dizer "quantos botões o `ActionFormData` mandou" → confirmado, é esse o nome.
- Usar `#form_button_contents` diretamente como fonte de `#maximum_grid_items` em um `grid` → **sem precedente vanilla direto** (o vanilla nunca faz essa combinação porque nunca usa grid pra isso). É uma extrapolação por analogia com o padrão geral do item 4 abaixo (qualquer binding pode ter `binding_name_override` trocado para `#maximum_grid_items`), plausível mas não comprovada em produção pela Mojang.

confidence: confirmado (nome do binding e onde aparece) / provável (que o mesmo binding funcionaria redirecionado para `#maximum_grid_items` em um grid customizado).

---

## 3. Item #4 — `grid_dimensions` e `#maximum_grid_items` são mutuamente exclusivos?

Script de verificação: para cada um dos 134 controles `"type": "grid"`, extraído o bloco completo por contagem de chaves e checado se `grid_dimensions` (literal) e `maximum_grid_items` (literal ou como alvo de `binding_name_override`) aparecem **no mesmo controle**.

```
CO-OCORRÊNCIA grid_dimensions + maximum_grid_items (mesmo controle): 0 de 134
```

Nenhum dos 134 grids vanilla combina os dois. Cada grid escolhe um mecanismo de contagem: ou fixo (`grid_dimensions: [N,M]`) ou dinâmico (`grid_dimension_binding` **ou** `bindings` com `binding_name_override: "#maximum_grid_items"`). Isso é coerente com a documentação de engine: `grid_dimensions` define linhas×colunas fixas; `maximum_grid_items`/`grid_dimension_binding` fazem a engine calcular a grade a partir de uma contagem, junto com `grid_rescaling_type` (100 % dos casos com `maximum_grid_items` no corpus também têm `grid_rescaling_type: "horizontal"` ou `"vertical"` — são a mesma família de padrão "grid elástico").

**Veredicto sobre a disputa**: o estudo que disse "0 co-ocorrências, mutuamente exclusivos" está certo em espírito e na contagem-tipo (aqui deu 0/134, não 0/144 — corpus com número de grids ligeiramente diferente, mas a conclusão é idêntica). Não há nenhum caso, nem em addon nenhum deste corpus (que é 100% vanilla, sem addons de terceiros), onde os dois convivam no mesmo controle. O outro estudo, que alega conviverem "em addon de produção com grid_rescaling_type", está falando de um addon de terceiros fora deste corpus — **não é evidência vanilla** e não pode ser verificada aqui; mecanicamente também não faz sentido: se `grid_dimensions` fixa linhas×colunas, um binding pra `#maximum_grid_items` (que serve pra a engine *calcular* dimensões a partir da contagem) fica redundante/conflitante com a fonte de verdade.

confidence: confirmado (para o corpus vanilla, contagem exata 0/134) / a alegação do "addon de produção" não foi e não pode ser verificada aqui — fora de escopo do corpus autoritativo.

---

## 4. Item #5 — `grid_dimensions` aceita 0 numa dimensão (ex. `[3,0]`)?

```
grep -n '"grid_dimensions":\s*\[' vanilla/ui/**/*.json   → 33 ocorrências literais
grep desses 33 por \b0\b dentro do array                  → 0 ocorrências
```

Todos os 33 `grid_dimensions` literais do corpus (tabela abaixo, também presente na seção 1):

`[5,1]`, `[2,1]`, `[3,1]` (x2), `[9,3]`, `[9,6]`, `[3,3]` (x3), `[1,3]` (x4), `[1,1]` (x7), `[1,4]` (x2), `[2,2]` (x2), `[9,1]` (x2), `[5,5]`, `[4,1]` (x2).

Nenhum contém `0` em qualquer posição. **Não há precedente vanilla** para `grid_dimensions: [N,0]` como "linhas ilimitadas". O mecanismo vanilla pra tamanho dinâmico é outro completamente distinto (item 3): trocar `grid_dimensions` inteiro por `grid_dimension_binding`/`maximum_grid_items` + `grid_rescaling_type`, nunca colocar `0` num eixo de `grid_dimensions`.

confidence: confirmado (ausência de precedente, contagem exata sobre as 33 ocorrências literais do corpus).

---

## 5. Item #6 — por que o item template do grid precisa ser fixo em px?

Evidência: o template canônico usado por praticamente todo grid vanilla de inventário (`common.container_item`, `ui_common.json`):

```json
"container_item": {
  "type": "input_panel",
  "size": [ 18, 18 ],
  "layer": 1,
  "$cell_image_size|default": [ 18, 18 ],
  "$cell_overlay_ref|default": "common.cell_overlay",
  "$button_ref|default": "common.container_slot_button_prototype",
  "$stack_count_required|default": true,
  "$durability_bar_required|default": true,
  "$storage_bar_required|default": true,
  "$item_renderer|default": "common.item_renderer",
  "$item_renderer_panel_size|default": [ 18, 18 ],
  "$item_renderer_size|default": [ 16, 16 ],
  "$item_renderer_offset|default": [ 0, 0 ],
  "$background_images|default": "common.cell_image_panel",
  ...
}
```

E os wrappers de hotbar/inventário que o reaproveitam, também em `ui_common.json`:

```json
"grid_item_for_inventory@common.container_item": { "$item_collection_name": "inventory_items" },
"grid_item_for_hotbar@common.container_item":    { "$item_collection_name": "hotbar_items" },

"hotbar_grid_template": {
  "type": "grid",
  "size": [ 162, 18 ],
  "grid_dimensions": [ 9, 1 ],
  "grid_item_template": "common.grid_item_for_hotbar",
  "collection_name": "hotbar_items"
}
```

`162 / 9 = 18px` por célula — bate exatamente com o `size: [18,18]` do template. Todos os templates de item de grid do corpus (`chest.chest_grid_item`, `crafting_pocket.crafting_input_grid_item`, `common.pocket_ui_container_item`, etc.) têm `size` em px inteiro, nunca em `%`.

**Confirmação do "porquê"**: o `type: "grid"` do JSON UI calcula o tamanho de cada célula dividindo o `size` total do grid pelas dimensões (`grid_dimensions` ou o resultado de `maximum_grid_items`/`grid_rescaling_type`) — é aritmética simples de pixel, não um layout de porcentagem recursivo como `stack_panel`. Um item template em `%` dentro de um grid teria a % resolvida contra o tamanho *já calculado* da célula (que por sua vez depende do total do grid em px ou de `default`/`fill`), criando um ciclo de dependência circular em muitos casos (`size: "100%"` de um filho cuja célula pai também depende do filho para se calcular quando o grid usa `"default"`/`"100%c"`). Por isso todo template vanilla usa px fixo: evita essa ambiguidade e garante `N colunas × largura fixa = size total` de forma determinística. O outro lado (grids com `size: ["100%", "default"]`, contagem dinâmica) só funciona porque o item template dentro deles **também** é px fixo — é o `grid_rescaling_type` que decide quantas colunas cabem dividindo a largura disponível pela largura fixa do item, não o contrário.

confidence: confirmado (todos os templates encontrados são px) / provável (a explicação mecânica do "por quê", que é inferência de engenharia reversa sobre o comportamento observado, não documentação oficial da Mojang).

---

## 6. Item #7 — alternativa `stack_panel` + `factory`: quando é melhor que grid

O vanilla usa esse padrão amplamente — 95 ocorrências da chave `"factory": {`, em 37 arquivos, incluindo `server_form.json`, `settings_sections/*.json`, `store_item_list_screen.json`, `store_promo_timeline_screen.json`, `trade_2_screen.json`. Exemplo canônico (o mesmo já citado na seção 2), `server_form.custom_form`:

```json
"generated_contents": {
  "type": "stack_panel",
  "size": ["100%", "100%c"],
  "orientation": "vertical",
  "factory": {
    "name": "buttons",
    "control_ids": {
      "label": "@server_form.custom_label",
      "toggle": "@server_form.custom_toggle",
      "slider": "@server_form.custom_slider",
      "step_slider": "@server_form.custom_step_slider",
      "dropdown": "@server_form.custom_dropdown",
      "input": "@server_form.custom_input",
      "header": "@server_form.custom_header",
      "divider": "@settings_common.option_group_section_divider"
    }
  },
  "collection_name": "custom_form",
  "bindings": [
    { "binding_name": "#custom_form_length", "binding_name_override": "#collection_length" }
  ]
}
```

**Quando o vanilla escolhe factory em vez de grid:**
1. **Itens de tipo/formato heterogêneo por linha da coleção.** `ModalFormData` mistura toggle, slider, dropdown, texto e header na mesma lista — cada elemento da coleção tem um `control_ids` diferente selecionado por `#type` do item. Um `grid` só instancia um único `grid_item_template`, sempre o mesmo layout — não serve pra heterogeneidade.
2. **Layout de lista vertical de altura variável por item** (ex.: um header mais alto, um divisor fino, um slider mais alto que um label). `stack_panel` empilha cada item com sua própria altura (`"100%c"` no eixo); um `grid` força todas as células ao mesmo tamanho fixo.
3. **Contagem 100% dinâmica sem necessidade de organização em colunas.** É exatamente o caso do `ActionFormData`/`ModalFormData`: lista de 1 coluna, altura total soma das alturas dos itens (`#collection_length` conta o "length"/tamanho da coleção pro stack_panel saber quantas vezes rodar a factory).

**Quando o vanilla prefere grid**: item sempre do mesmo tipo/tamanho e quando se quer organização em N colunas fixas (crafting 3x3, chest 9x3, hotbar 9x1) ou N colunas elásticas recalculadas pela largura disponível (`grid_rescaling_type` + `maximum_grid_items` — telas de skins, realms, recipe book, mods de loja).

**No caso concreto de renderizar os botões de um `ActionFormData` (é o que o SonheMenu faz)**: o próprio vanilla, em `server_form.long_form` (o form nativo de `ActionFormData`), usa `stack_panel` + `factory`, **nunca grid**. Isso é evidência forte de que o "shape literal" mais fiel ao comportamento nativo é a lista vertical via factory — que é exatamente o fallback `list_screen`/`buttons_factory` que já existe em `sonhe_grid.json`. O layout em grade de tiles (3 colunas) é uma escolha de UX própria do addon, sem equivalente 1:1 no vanilla.

confidence: confirmado.

---

## 7. Item #8 — envolver grid/lista em `common.scrolling_panel`

Exemplo vanilla completo de "grid dentro de scroll", `ui_common.json`:

```json
"container_grid": {
  "type": "grid",
  "grid_rescaling_type": "horizontal",
  "size": [ "100%", "default" ],
  "anchor_to": "top_left",
  "anchor_from": "top_left",
  "$item_collection_name|default": "inventory_items",
  "$grid_item_template|default": "common.container_item",
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
},

"container_scroll_panel@common.scrolling_panel_with_offset": {
  "$scrolling_content|default": "common.container_grid",
  "$scrolling_pane_offset": [ 0, 0 ],
  "$scrolling_pane_size": [ "100%", "100%" ],
  "$scrolling_pane_size_touch": [ "100% + 10px", "100%" ],
  ...
}
```

Ou seja: o grid dinâmico (`grid_rescaling_type` + `#maximum_grid_items`) vira o `$scrolling_content` de um `common.scrolling_panel_with_offset` (que herda de `common.scrolling_panel`). É o padrão "grid elástico dentro de scroll" usado pra listas de inventário genéricas que podem crescer além da tela.

**$vars obrigatórias de `common.scrolling_panel` (sem `|default`)**: dentro da definição de `scrolling_panel` em `ui_common.json` (linhas ~4627-4720), **toda** variável tem `|default` (`$scrolling_pane_size`, `$scroll_view_port_size`, `$scroll_size`, `$show_background`, etc. — mais de 20 vars, todas com fallback), **exceto uma**: `$scrolling_content`. O próprio comentário do arquivo vanilla confirma:

```
// The content you want inside the scrolling viewport must be specified
// by defining $scrolling_content.
```

E o uso interno, dentro do `controls` de `scrolling_panel`:

```json
"scrolling_content@$scrolling_content": {
  "$scrolling_content_anchor_from|default": "top_left",
  "$scrolling_content_anchor_to|default": "top_left",
  "anchor_from": "$scrolling_content_anchor_from",
  "anchor_to": "$scrolling_content_anchor_to"
}
```

**O que acontece se faltar `$scrolling_content`**: a sintaxe `nome@$scrolling_content` faz o parser resolver o nome do controle-pai a partir do valor da variável `$scrolling_content`. Se a variável não estiver definida (nenhum valor, nem via `|default` nem passada na instância), a referência `@$scrolling_content` não resolve pra nenhum namespace/controle válido — o resultado observável é a área de scroll ficar **vazia** (sem conteúdo, sem erro visível em tela; o log de conteúdo do jogo tende a acusar herança/referência inválida). É por isso que toda instância concreta de `scrolling_panel` no corpus (server_form, tab_content do crafting, container_scroll_panel) sempre define `$scrolling_content` explicitamente — nunca deixam pra depender de default, porque **não existe** default na base.

Outras vars que também costumam precisar de ajuste manual (mas têm default, então "faltar" só produz visual levemente errado, não vazio): `$scroll_size` (largura da trilha, default `[4,"100%"]`), `$scrolling_pane_size` (default `["100%","100%"]` — raramente serve puro, quase todo uso customiza pra abrir espaço pra trilha do scroll).

confidence: confirmado ($scrolling_content é a única var sem `|default` na definição de `scrolling_panel`, comentário do próprio arquivo vanilla confirma a obrigatoriedade) / provável (o efeito exato de "vazio sem erro" é inferência sobre o comportamento de resolução de `@$variavel`, não testado em jogo neste levantamento).

---

## 8. Aplicação no SonheMenu

Lido `ADDONS/SonheMenu_RP/ui/sonhe_grid.json` (namespace `sonhe_forms`) só para diagnóstico — **nada foi editado**, conforme pedido.

O arquivo já contém duas implementações, e ambas **já seguem exatamente os padrões vanilla confirmados acima**:

1. **`grid_screen` / `tiles_grid`**: `grid_dimensions: [3,4]` literal + `collection_name` + **sem** binding de contagem + `grid_item_template` fixo em `96px`. Isso bate 100% com o padrão observado nos 134 grids vanilla de dimensão fixa (chest 9x3/9x6, crafting 3x3/2x2, hotbar 9x1): `grid_dimensions` literal nunca convive com `#maximum_grid_items`/`grid_dimension_binding`, e o item template é sempre px. **Nada a corrigir aqui.**

2. **`list_screen` / `buttons_factory`**: `stack_panel` + `factory` + `collection_name: "form_buttons"` + binding `"#form_button_contents" → "#collection_length"`. Isso é **cópia literal e correta** do padrão de `server_form.long_form_dynamic_buttons_panel` (seção 2 acima) — inclusive o nome do binding, `#form_button_contents`, está certo. A pesquisa anterior do time (comentário `//5` no arquivo) estava certa em ficar em dúvida: **não existe confirmação vanilla de que `#form_button_contents` alimente `#maximum_grid_items`**, porque o vanilla nunca usa esse binding num grid — só no `stack_panel`/factory, mirando `#collection_length`. Isso é exatamente o que a investigação atual confirma (item 2/seção 2).

**Sobre os comentários `//3`/`//5` do arquivo (P3/P4 "não resolvidos de propósito")**:
- A dúvida registrada era se dava pra trocar `tiles_grid` de `grid_dimensions` fixo para `grid_rescaling_type` + `#maximum_grid_items` alimentado por `#form_button_contents`, pra ter altura adaptativa à quantidade real de botões do form.
- Evidência desta investigação: tecnicamente isso seguiria o padrão geral do vanilla (qualquer binding pode ter seu `binding_name_override` redirecionado pra `#maximum_grid_items` — visto em `#skins_grid_dimensions`, `#recipe_book_total_items`, `#max_grid_offers`, etc., seção 1). Não há nada de especial em `#form_button_contents` que o impeça de ser redirecionado da mesma forma:
  ```json
  "bindings": [
    { "binding_name": "#form_button_contents", "binding_name_override": "#maximum_grid_items" }
  ]
  ```
  adicionado ao `tiles_grid` (removendo `grid_dimensions` — mutuamente exclusivos, seção 3) e adicionando `"grid_rescaling_type": "horizontal"`. Isso é **provável que funcione**, mas continua **sem precedente vanilla literal** (o vanilla nunca faz essa combinação exata pra ActionFormData) — é extrapolação por analogia, não cópia comprovada. Testar em jogo antes de assumir que resolve P3/P4.
- Se testar e funcionar, `grid_rescaling_type: "horizontal"` recalcula quantas colunas cabem por linha dividindo a largura do grid pela largura fixa do `tile` (96px) — o que muda o número de colunas por tela, não só a altura. Se o objetivo era **só** altura adaptativa mantendo 3 colunas fixas, `grid_rescaling_type` sozinho não trava colunas em 3; seria necessário `size` do grid travado em `288px` de largura (`96*3`) pra forçar sempre 3 por linha mesmo com contagem dinâmica — o que já é o caso hoje (`grid_stack` tem `size: [288, "100%c"]`), então na prática desse layout específico provavelmente manteria 3 colunas. Ainda assim, validar em jogo antes de trocar a "mecânica preservada" documentada no `//2`.
- Item template continua obrigatoriamente px (`96x96`) em qualquer um dos dois caminhos — isso não muda, é confirmado pela seção 5.

Nenhuma mudança foi aplicada em `ADDONS/SonheMenu_RP` ou `ADDONS/SonheMenu_BP` — só leitura para este diagnóstico, conforme instruído.
