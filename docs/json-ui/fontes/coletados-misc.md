# Coletados — arquivos diversos (Tarefa A)

Fonte: `.../scratchpad/{csf.json, vsf.json, sf.json, sop.json, g1.json, gv.json, cb.json, ct.json}`
Comparação: `c:/Users/Desktop/Documents/Nova pasta/assets/assets/resource_packs/vanilla/ui/`
Convenção: **confirmado** (evidência estática direta) / **provável** / **suspeita**.

---

## 1. Identificação por arquivo

### vsf.json
- **Origem: vanilla puro. confidence: confirmado.**
- `diff --strip-trailing-cr` contra `vanilla/ui/server_form.json` → **vazio** (531/531 linhas idênticas, só CRLF difere). Cabeçalho `(c) Mojang. All rights reserved` presente.
- Nenhum padrão novo — é o mesmo `server_form.json` vanilla já usado como baseline em `coletados-serverform.md`.

### gv.json
- **Origem: vanilla puro. confidence: confirmado.**
- `diff --strip-trailing-cr` contra `vanilla/ui/_global_variables.json` → **vazio** (459/459 linhas idênticas). É o arquivo de cores/tema (`$light_button_default_text_color`, `$dark_toggle_checked_hover_text_color` etc.), já teria sido a base de qualquer estudo de tema anterior — nenhum padrão novo.

### ct.json
- **Origem: vanilla puro. confidence: confirmado.**
- `diff --strip-trailing-cr` contra `vanilla/ui/chest_screen.json` → **vazio** (277/277 linhas idênticas). Já coberto em detalhe em `coletados-chest.md` (namespace `chest`, `small_chest_grid`/`large_chest_grid`, `grid_dimensions: [9,3]`/`[9,6]`). Sem padrão novo — por regra da tarefa, não aprofundado de novo aqui.

### cb.json
- **Origem: download falho. confidence: confirmado.**
- Conteúdo integral do arquivo (14 bytes): `404: Not Found`. Não é JSON UI, não há nada a extrair.

### sf.json
- **Origem: download falho — mesma página que já apareceu em outro estudo. confidence: confirmado.**
- `md5sum` idêntico a `skyls.json` e `skyls_sf.json` (`b8e69651f883d48f0897b83e3d24d050`). Conteúdo é a página HTML renderizada de **"Skyls - Code Snippets With Videos"** (`<title>Skyls - Code Snippets With Videos</title>`), não JSON puro.
- Já analisado em profundidade em `coletados-serverform.md` (seção sobre `skyls_sf.json`/`skyls_clean.json`). Nenhum conteúdo novo a extrair de `sf.json` em si — é literalmente a mesma fonte, já limpa e citada naquele relatório via `skyls_clean.json`.

### g1.json
- **Origem: download falho, fonte diferente das outras. confidence: confirmado.**
- Conteúdo é HTML de um interstitial **"Vercel Security Checkpoint"** (`<title>Vercel Security Checkpoint</title>`, CSS de spinner de verificação anti-bot). O `grep` por `grid_dimensions`/`collection_name`/`namespace` não encontrou nenhuma ocorrência — confirma que não há JSON UI nenhum embutido no arquivo, ao contrário do que aconteceu com `sf.json`/`skyls.json` (onde a página tinha o código incorporado). Não há como recuperar o conteúdo pretendido a partir deste arquivo.

### sop.json
- **Origem: tutorial/ferramenta de depuração de layout, não vanilla. confidence: confirmado (é um snippet de teste — texto literal `"Test 1"`..`"Test 5"`, comentários explicativos em inglês, não existe em `vanilla/ui/`).**
- Padrão **novo**, não visto em nenhum estudo anterior deste projeto: um painel de depuração visual para calibrar `use_anchored_offset` usando `"modifications"` (`operation: "insert_back"`) sobre `start_screen_content`. Ele injeta 4 sliders (`common.slider`) cujo `#slider_value` é lido via `binding_type: "view"` + `source_control_name` de cada slider, escrito num `property_bag` do painel alvo, e usado para pilotar size/offset em tempo real:
  ```json
  "bindings": [
    {
      "binding_type": "view",
      "source_control_name": "size_x",
      "source_property_name": "( (#slider_value + 1) / 10 )",
      "target_property_name": "#size_binding_x"
    },
    {
      "binding_type": "view",
      "source_control_name": "offset_x",
      "source_property_name": "( ( #slider_value ) / 10 )",
      "target_property_name": "#anchored_offset_value_x"
    }
  ]
  ```
  com o painel alvo declarando `"property_bag": { "#size_binding_x": 0.0, ..., "#anchored_offset_value_x": 0.0 }` e `"use_anchored_offset": true`. É a única fonte do corpus que demonstra, de forma isolada e comentada, como um `property_bag` local pode ser pilotado por bindings `view` cruzados entre controles irmãos (`source_control_name`) para simular um inspector de layout ao vivo — útil como referência de debug, não como padrão de produção (usa `common_buttons.light_text_button` com texto/placeholders de teste, e mexe em `start_screen`, não em `server_form`).

### csf.json
- **Origem: addon/tutorial de terceiros ("chest fake UI" para `server_form`), não vanilla. confidence: confirmado — comentário de autor humano na linha 49 (`// this line took a decade to figure out`) e namespace `chest_ui` inexistente no corpus vanilla.**
- Estruturalmente é uma variante do mesmo "baú falso dentro do server_form" já documentado em `coletados-chest.md` a partir de `chest_inv.json`/`chest_inventory_system.json`/`chest_sf.json` — os truques de decodificação de string em `#form_button_text`/`#form_button_texture` (`dur#00`, `stack#01`, `#item_id_aux` via `% 65536`) **já estão registrados naquele relatório** e não são repetidos aqui. Dois padrões, porém, são novos e não apareceram em nenhum estudo anterior:

  **(a) Seletor de tamanho de grade por múltiplos painéis simultâneos + toggle de build separado do toggle de binding.** `chest_panel` empilha 8 instâncias de `chest_ui_template` (uma para cada tamanho de baú: 1, 5, 9, 18, 27, 36, 45, 54 slots), cada uma com seu próprio marcador de seção no título **e** uma flag de variável independente para desativá-la na build:
  ```json
  "09@chest_ui.chest_ui_template": {
      "$grid_size": [ 9, 1 ],
      "$condition": "§c§h§e§s§t§0§9",
      "ignored": "$disable_9_slots_layout"
  },
  ```
  O `binding_type: "view"` dentro de `chest_ui_template` decide a visibilidade em runtime (`(not ((#title_text - $condition) = #title_text))`); o `"ignored": "$disable_9_slots_layout"` é um mecanismo **separado**, resolvido em tempo de parse/build via `$variável`, para remover uma variante inteira do layout sem tocar no binding. É a combinação dos dois mecanismos (runtime binding de visibilidade + variável de "ignored" para poda de build) que não tinha aparecido antes.

  **(b) Array de bindings reaproveitado via variável.** `inventory_item@common.button` define `"$aux_id"` como um array de 4 objetos de binding (decodifica textura/aux id do item) e depois o reusa literalmente em três sub-painéis diferentes (`default_control`, `hover_control`, `pressed_control`) apenas escrevendo `"bindings": "$aux_id"`:
  ```json
  "item@beacon.item_renderer": {
      "size": [16, 16],
      "layer": 4,
      "bindings": "$aux_id"
  }
  ```
  Isso evita repetir os 4 objetos de binding em cada um dos 3 estados do botão — técnica de DRY via `$variável` armazenando um array inteiro de `bindings` (não só um valor escalar), reaproveitável em qualquer controle-filho. Não visto em nenhum outro arquivo do corpus estudado até agora.

---

## 2. Resumo de proveniência

| Arquivo | Origem | Confidence |
|---|---|---|
| vsf.json | vanilla puro (`server_form.json`, idêntico) | confirmado |
| gv.json | vanilla puro (`_global_variables.json`, idêntico) | confirmado |
| ct.json | vanilla puro (`chest_screen.json`, idêntico) | confirmado |
| cb.json | download falho (`404: Not Found`) | confirmado |
| sf.json | download falho (mesma página HTML de `skyls.json`) | confirmado |
| g1.json | download falho (interstitial "Vercel Security Checkpoint") | confirmado |
| sop.json | snippet de debug de layout (não vanilla, não `server_form`) | confirmado |
| csf.json | addon/tutorial de terceiros ("chest fake UI") | confirmado |

Nenhuma afirmação acima foi inventada: toda comparação usou `diff`/`md5sum` sobre os arquivos citados, ou leitura integral (`Read`) do conteúdo mostrado nos trechos.
