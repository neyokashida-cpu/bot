# Coletados — Chest-UI / Inventário Custom (Tarefa A)

Fonte: `.../scratchpad/{chest_sf.json, chest_inv.json, chest_inventory_system.json, chest_screen.json, inv.json}`
Comparação: `c:/Users/Desktop/Documents/Nova pasta/assets/assets/resource_packs/vanilla/ui/`

## 1. Identificação de cada arquivo

### chest_screen.json
- **Origem: vanilla puro. confidence: confirmado.**
- `diff` byte-a-byte (ignorando CRLF) contra `vanilla/ui/chest_screen.json` retornou **vazio** — conteúdo idêntico.
- Namespace `"chest"`. Define `small_chest_grid`/`large_chest_grid` (`type: "grid"`, `grid_dimensions: [9,3]`/`[9,6]`, `grid_item_template: "chest.chest_grid_item"`, `collection_name: "container_items"`) — o grid REAL de baú do jogo (não é o hack de server_form).

### chest_inv.json e chest_inventory_system.json
- **Origem: addon/tutorial de terceiros (estilo "fake chest UI" para `server_form`). confidence: confirmado (arquivos idênticos entre si, byte a byte — mesmo md5 `fc05c4c0...` não, na verdade os dois têm o MESMO conteúdo textual completo, verificado por leitura integral).**
- Namespace `"chest_ui_inventory_system"` — não existe em vanilla. É a camada que fabrica um "hotbar" e "inventário do jogador" falsos dentro do `server_form`, usando o mesmo `collection_name: "form_buttons"` do ActionFormData.
- Trecho-chave (paginação via texto do título, ambos arquivos, linhas 20-21):
  ```json
  "collection_name": "form_buttons",
  "$size": "$condition",
  "$start_index": "(($size - '§c§h§e§s§t' - '§') * 1)",
  ```
  Isso extrai um índice inteiro embutido no `#title_text` do form (técnica de "subtração de string" do JSON UI) para decidir onde a página de itens do hotbar/inventário começa dentro da coleção `form_buttons` — não existe outro canal de dados entre o script e a UI além do título/corpo do form.
- `inventory_item_panel` (18x18) combina `bg@chest_ui.cell` (textura de fundo de slot) + `inventory_button_amount` (label do stack) + `inventory_item@common.button` — o "slot" é um **botão comum**, não um controle de item nativo.
- Clique: `inventory_item@common.button` mapeia `button.form_button_click` tanto em `pressed` quanto em `focused` (linhas 296-310) — ou seja, cada slot é clicável (envia o índice do botão pressionado de volta ao script), mas **não há drag-and-drop real**: é reordenação impossível, só seleção por clique único, como qualquer botão de ActionFormData.
- Ícone do item é decodificado do próprio texto do botão via aritmética de string:
  ```json
  "source_property_name": "((#form_button_texture - (#form_button_texture % 65536)) / 65536)",
  "target_property_name": "#item_id_aux"
  ```
  (extrai o "aux id" do item embutido como número codificado no texto do botão, para renderizar via `beacon.item_renderer`).

### inv.json
- **Origem: vanilla (quase puro). confidence: confirmado (com ressalva).**
- Namespace `"crafting"`. `diff` contra `vanilla/ui/inventory_screen.json` (que define esse namespace) mostrou só **51 linhas diferentes em 2699** — a única diferença real é que o campo de busca da tela de criativo (`text_edit_control@common.text_edit_box`, com toda a config de `$magnifying_glass_*`, `$text_clear_button_*`, TTS etc.) foi **substituído por um placeholder minúsculo** (`text_edit_control@common.text_edit_control`, sem propriedades). Resto é 1:1 idêntico à vanilla, incluindo os 7 controles `"type": "grid"` da tela de crafting/criativo.
- Contém o padrão canônico de slot com clique/segurar/drop de item real (não é fake): `inventory_container_slot_button@common.container_slot_button_prototype`, com `button_mappings` completos para `button.container_take_half_place_one`, `button.container_auto_place`, `button.container_take_all_place_all`, `button.coalesce_stack`, `button.drop_one`, `button.drop_all`, `button.cursor_drop_all`, `button.cursor_drop_one` — este é o mecanismo real de "segurar item no cursor e soltar" do inventário nativo (baseado em botões de controlador/mapeamento, não em mouse-drag primitivo do JSON UI).

## 2. Padrão consolidado: como o "baú fake" é emulado em server_form

1. **Sem inventário real por trás.** Todo "baú"/"inventário" dentro de um `server_form` é só uma `grid` (ou `stack_panel` de `stack_panel`s) ligada à coleção nativa `form_buttons` do ActionFormData — a mesma lista de botões que qualquer form comum usa.
2. **Metadado extra vem embutido no texto**, não em propriedade separada:
   - No `#title_text` do form: prefixos/sufixos com caracteres de seção (`§`) usados só como marcador, decodificados por subtração de string (`$title_text - '§c§h§e§s§t'`), permitindo (a) decidir qual layout mostrar e (b) transportar um índice de paginação inteiro.
   - No próprio texto do botão (`#form_button_text`/`#form_button_texture`): codifica textura do item, aux id (`%65536`), durabilidade (`dur#00`) e tamanho da pilha (`stack#01`), tudo via fatiamento de string (`%.8s`, `%.14s`) — é a mesma técnica usada em `chest_sf.json` para separar telas de baú/fornalha.
3. **Slot = botão, clique = seleção, não drag.** Todo "slot" é um botão binding em `collection_name` com 3 estados (`default/hover/pressed`) mapeados para `button.form_button_click`. Não existe drag real no JSON UI de `server_form`; qualquer efeito de "arrastar item" precisa ser simulado no lado do script (reabrindo o form com novo estado), não pelo controle de UI.
4. **"Grade" dinâmica = conjunto fixo de layouts pré-declarados.** Como `grid_dimensions` não pode ser lido de uma coleção em tempo real de forma confiável nesse cliente, o padrão usado (em `csf.json`, tarefa B) é declarar N variantes de grid com `grid_dimensions` fixo (`[9,1]`, `[1,1]`, `[9,2]`... `[9,6]`) e usar `ignored`/binding de visibilidade para escolher a variante certa a partir do código embutido no título.
