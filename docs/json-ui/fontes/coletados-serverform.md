# Fonte: comparação lado a lado de 6 `server_form` custom coletados

> **Cliente alvo:** 1.26.44.
> **Fontes estudadas (6):** `easyui_server_form.json`, `yasser_server_form.json`, `skyls_sf.json` (= `skyls.json`, bytes idênticos, `md5 b8e69651f883d48f0897b83e3d24d050`), `tile_server_form.json`, `chest_server_form.json` — todos em
> `C:/Users/Desktop/AppData/Local/Temp/claude/c--Users-Desktop-Desktop-Projetos-bot/af2a5c2c-b27f-4843-989f-56bffbe0db88/scratchpad/`.
> **Corpus vanilla de referência:** `c:/Users/Desktop/Documents/Nova pasta/assets/assets/resource_packs/vanilla/ui/` — usei `server_form.json` e `ui_template_dialogs.json` (namespace `common_dialogs`; **não existe `common_dialogs.json`**, confirmado por `grep -n "\"namespace\"" ui_template_dialogs.json` → linha 7 `"namespace": "common_dialogs"`).
> **Pack próprio consultado só para a seção 7 (leitura, sem edição):** `c:/Users/Desktop/Desktop/Projetos/bot/ADDONS/SonheMenu_RP/ui/{_ui_defs,sonhe_forms,sonhe_grid}.json`.
> **Nota de proveniência:** `skyls_sf.json`/`skyls.json` não são JSON puro — são o HTML de uma página (skyls.dev) com o `server_form.json` embutido em `<pre><code class="language-json">` com syntax-highlight escapado. Extraí o bloco de código (`extract_skyls2.py`, no mesmo scratchpad) removendo tags e decodificando entidades HTML; o resultado limpo está em `skyls_clean.json` no mesmo diretório e é o que foi lido/citado abaixo. `easyui_server_form.json` é JSON puro mas estruturalmente inválido (seção 3.1).
> Convenção de confiança: **confirmado** (lido byte-a-byte no arquivo, comportamento documentado em spec/wiki oficial ou verificável estaticamente) / **provável** (padrão conhecido da comunidade, consistente entre várias fontes, mas não vi o motor rodando) / **suspeita** (hipótese plausível, não teria como confirmar sem abrir o jogo).

---

## 1. Resumo executivo

Nenhuma das 6 fontes usa a técnica que a própria wiki oficial (`modifying-server-forms.md`, presente no scratchpad) recomenda — `"modifications"` com `"operation": "insert_back"` para **adicionar** um factory novo em `main_screen_content` e só then esconder o `long_form` vanilla original com um binding extra. As 6 fazem algo mais arriscado e mais comum na prática: **redefinem o control `long_form` inteiro, pelo mesmo nome**, confiando que a ordem de carregamento dos arquivos do RP faça a definição delas vencer a da vanilla dentro do namespace `server_form`. Isso funciona, mas tem duas implicações que explicam sumiço silencioso sem `[UI][error]`:

1. **Nenhuma delas mantém uma cópia funcional do `long_form` vanilla como rede de segurança.** Se a condição de visibilidade de todo o ramo custom falhar (marcador errado, expressão sem parênteses fechando, variável `$` não definida), o resultado não é "cai pra lista vanilla" — é **tela em branco**, porque o `long_form` vanilla original não existe mais nesse arquivo depois do override. A exceção parcial é o padrão de "ramo `default_long_form`" usado por `skyls`/`tile_server_form` (ver §3.3–3.4): eles **recriam manualmente** um clone do `long_form` vanilla dentro do próprio arquivo como um dos ramos, condicionado a "nenhum marcador bateu". Esse clone É o mecanismo de fallback pra lista vanilla — e é também o ponto exato onde uma string de marcador mal escrita (typo, código de cor `§` a mais/a menos, título com espaço extra) faz o menu **cair silenciosamente na lista vanilla**, exatamente o sintoma relatado.
2. **Risco sistêmico, comum às 6 e independente do JSON:** se o RP customizado carregar com prioridade **abaixo** da vanilla na pilha de `resource_packs` do mundo/servidor, a definição de `long_form` da vanilla vence por último e a tela custom nunca aparece — sem erro nenhum, porque do ponto de vista do parser nada está errado. Isso não aparece em nenhum dos 6 arquivos (é config de mundo, não de UI), mas é a explicação mais barata a descartar antes de caçar bug em JSON.

Achados de maior impacto, por fonte, com trecho e localização exatos nas seções 3–6.

---

## 2. Baseline vanilla (necessário para julgar os outros 6)

`server_form.json` (vanilla), namespace `server_form`:

```json
"main_screen_content": {
  "type": "panel",
  "size": [0, 0],
  "controls": [
    { "server_form_factory": {
        "type": "factory",
        "control_ids": {
          "long_form": "@server_form.long_form",
          "custom_form": "@server_form.custom_form"
        }
    } }
  ]
},

"long_form@common_dialogs.main_panel_no_buttons": {
  "$title_panel": "common_dialogs.standard_title_label",
  "$title_size": [ "100% - 15px", 10 ],
  "size": [225, 200],
  "$text_name": "#title_text",
  "$title_text_binding_type": "none",
  "$child_control": "server_form.long_form_panel",
  "layer": 2
},
```

Dois fatos-âncora, confirmados:

- **`main_screen_content` é `[0, 0]`.** O `factory` escolhe qual control vira o filho direto desse painel zero. Vanilla nunca deixa esse filho direto em `%` — `long_form` recebe `"size": [225, 200]` **absoluto em pixel**, na própria linha da invocação do template, não dentro dele.
- Conferido em `ui_template_dialogs.json` linha 205–232, `common_dialogs.main_panel_no_buttons` **não define `size` no template** — quem chama é quem tem que dar um tamanho real, senão herda o que vier (ou nada). É por isso que toda variante séria dá `size` explícito no ponto de invocação, nunca dentro do template base.

---

## 3. Ficha por fonte

### 3.1 `easyui_server_form.json` — estruturalmente inválido

- **Override:** redefine `"long_form@long_form"` (auto-herda do próprio nome — estranho, mas sintaticamente aceito como shorthand `@`).
- **Discriminação:** dezenas de ramos (`LABEL_TEST`, `PANEL_EXAMPLE`, `GRID_EXAMPLE`, ... até `MODIFICATION_EXAMPLE`) cada um visível por `(#title_text = 'ALGO_EXAMPLE')`, claramente copiados do **addon de exemplos "ui_test"** da documentação, não de um menu real.
- **Achado crítico (confirmado por schema):** o valor de `"controls"` **não é um array**, é um objeto direto com as chaves dos controles:
  ```json
  "long_form@long_form": {
      "controls": {
          "long_form@common_dialogs.main_panel_no_buttons": { ... },
          "LABEL_TEST@ui_test.ui_test": { ... },
          ...
      },
      "bindings": { "1": { "source_property_name": "..." } },
      "con": { "1": { "source_property_name": "..." } }
  }
  ```
  Isso viola a definição `nm:controls` do schema JSON UI comunitário (`ui.schema.json`, verificado via script de extração: `"nm:controls"` só aceita `{"type":"array","items":{...patternProperties...}}` ou uma `$variavel` — nunca um objeto de chaves nomeadas). Além disso `"bindings"` (que deveria ser array) e o campo inexistente `"con"` também são objetos com chave string `"1"`. **Confiança: confirmado** que a estrutura viola o schema; **provável** (não testável sem abrir o jogo) que isso derrube o parse do control inteiro e jogue 100% de volta pra lista vanilla, sem log de erro — motores tolerantes a JSON costumam ignorar silenciosamente o nó malformado em vez de abortar o pack inteiro.
- **Botões:** não dá pra avaliar com confiança — a estrutura de controles não segue o formato que o motor espera.
- **Size no long_form:** não declarado no nó externo.
- **Tema:** usa `common_dialogs.main_panel_no_buttons` no primeiro ramo (herdaria nine-slice vanilla, se o arquivo carregasse).
- **Veredito:** não é um exemplo de técnica, é um copy-paste quebrado do addon de exemplos oficial. Fica na tabela como "pior caso" de referência.

### 3.2 `yasser_server_form.json`

- **Override:** redefine `"long_form"` puro (sem `@template`), tipo `panel`, sem `size`, com dois filhos: `menu@server_form.menu` (lista vanilla-like) e `test@server_form.test` (grid custom).
- **Discriminação:** binding `global` captura `#title_text` em `#text`; `menu` visível se `(not (#text = 'test'))`, `test` visível se `((#text = 'test'))` — mutuamente exclusivos e complementares (par binário fechado, sem lacuna).
  ```json
  "menu@common_dialogs.main_panel_no_buttons": {
    "...": "...",
    "bindings": [
      { "binding_type": "global", "binding_name": "#title_text", "binding_name_override": "#text" },
      { "binding_type": "view", "source_property_name": "(not (#text = 'test'))", "target_property_name": "#visible" }
    ]
  },
  "test": {
    "type": "panel", "size": ["100%","100%"],
    "bindings": [
      { "binding_type": "global", "binding_name": "#title_text", "binding_name_override": "#text" },
      { "binding_type": "view", "source_property_name": "((#text = 'test'))", "target_property_name": "#visible" }
    ]
  }
  ```
  **Suspeita alta:** o marcador é a palavra literal `'test'`. Qualquer diálogo legítimo do servidor (ou de outro addon) cujo título seja exatamente "test" ativa o ramo grid por engano — colisão de nome real, não hipotética.
- **Botões:** três `stack_panel` (`buttons`, `buttons1`, `buttons2`) com **`collection_index` literal de 0 a 6**, cada botão com `$default_button_texture`/`$hover_button_texture`/etc. **hardcoded** (ex.: `"textures/ui/icon_steve"`), sem nenhum binding a `#form_button_texture`. Ou seja: o ícone nunca reflete o que o servidor mandou — está fixo por posição. Se o form tiver menos de 7 botões ou mudar de ordem, ícone e texto (que aí sim vem de `#form_button_text` via `collection`) ficam dessincronizados.
- **Size no long_form:** não declarado (nem no `long_form` externo nem no `test`, que usa `["100%","100%"]`) — mesmo padrão de risco de colapso sob pai `[0,0]` que a vanilla evita com pixel absoluto (ver §6, P2).
- **Tema:** `menu` herda nine-slice vanilla via `common_dialogs.main_panel_no_buttons`. `test` é um `panel` cru — **sem `common.common_panel`, sem moldura, sem fundo** — os botões flutuam direto sobre o mundo.
- **Bindings de texto/ícone:** texto via `common_buttons.light_text_button` + `collection`/`collection_details` (padrão vanilla, ok); ícone **não é bindado** (ver acima).

### 3.3 `skyls_sf.json` / `skyls.json` (limpo em `skyls_clean.json`)

- **Override:** redefine `"long_form"` como `panel` com `"size": ["100%", "100%"]` e dois filhos via `common_dialogs.main_panel_no_buttons`.
- **Discriminação — o padrão "ramo default explícito":**
  ```json
  "default_long_form@common_dialogs.main_panel_no_buttons": {
    "size": [225, 200], "$child_control": "server_form.long_form_panel",
    "bindings": [
      { "binding_name": "#title_text" },
      { "binding_type": "view",
        "source_property_name": "((#title_text - 'Custom Form') = #title_text)",
        "target_property_name": "#visible" }
    ]
  },
  "cutsom_long_form@common_dialogs.main_panel_no_buttons": {
    "size": [322.5, 185], "$child_control": "server_form.my_super_custom_panel_main",
    "bindings": [
      { "binding_name": "#title_text" },
      { "binding_type": "view",
        "source_property_name": "(#title_text = 'Custom Form')",
        "target_property_name": "#visible" }
    ]
  }
  ```
  `default_long_form` **recria a lista vanilla de verdade** (`$child_control: server_form.long_form_panel`, que continua existindo porque este arquivo nunca sobrescreveu esse nome) e fica visível sempre que o título **não contiver** a substring `'Custom Form'`. Isso é ao mesmo tempo a discriminação e o mecanismo exato de "cai pra lista vanilla, sem erro": qualquer diálogo cujo título não seja **exatamente** `'Custom Form'` mostra a lista padrão. Complementar por construção (subtração de string), sem lacuna — mas frágil a maiúsculas/espaços porque a comparação é sensível a isso.
- **Botões:** `my_super_custom_panel_main` é `stack_panel` horizontal com `collection_name: "form_buttons"`; dentro, **`collection_index` literal** (0–3) espalhado por `stack_panel`s aninhados (um grande + coluna direita com 1 + linha inferior com 2) — layout artesanal de 4 posições fixas, não um grid genérico.
- **Size no long_form:** o wrapper externo `"long_form"` usa `"100%","100%"` — sob um pai `[0,0]` isso é risco de colapso (§6, P2) **se** o motor recortar (clip) filhos ao tamanho do pai; como os dois ramos internos (`default_long_form`/`cutsom_long_form`) têm `size` absoluto próprio (`[225,200]` / `[322.5,185]`), na prática eles não dependem do tamanho do wrapper — **suspeita moderada**, não confirmada.
- **Tema:** ambos os ramos passam por `common_dialogs.main_panel_no_buttons`, então herdam moldura/nine-slice vanilla (`common.common_panel`) automaticamente — o grid custom não é "pelado" como o do yasser.
- **Bindings de texto/ícone (o mais correto dos 6 nesse ponto):**
  ```json
  "image": { "type": "image", "size": "$icon_size", "bindings": [
    { "binding_name": "#form_button_texture", "binding_name_override": "#texture", "binding_type": "collection", "binding_collection_name": "form_buttons" },
    { "binding_name": "#form_button_texture_file_system", "binding_name_override": "#texture_file_system", "binding_type": "collection", "binding_collection_name": "form_buttons" },
    { "binding_type": "view", "source_property_name": "(not ((#texture = '') or (#texture = 'loading')))", "target_property_name": "#visible" }
  ]},
  "form_button@common_buttons.light_text_button": { "$button_text": "#null", ... }
  ```
  Ícone vem de fato do servidor (igual ao `dynamic_button` vanilla). O botão clicável real usa `$button_text: "#null"` — texto vazio de propósito — porque o rótulo visível é um `label` **separado**, bindado direto a `#form_button_text`. Separação limpa entre hitbox/click e visual.

### 3.4 `tile_server_form.json`

- **Override:** redefine `"long_form"` como `panel` (`"size":["100%","100%"]`) com **5 ramos** via `common_dialogs.main_panel_no_buttons`: `default_long_form` (fallback), `bi_main_form`, `bi_settings_form`, `bi_islands_form`, `bi_auction_form` — claramente o addon "BedrockIslands".
- **Discriminação — encadeamento de subtrações no fallback:**
  ```json
  "default_long_form@common_dialogs.main_panel_no_buttons": {
    "size": [225, 200], "$child_control": "server_form.long_form_panel",
    "bindings": [
      { "binding_name": "#title_text" },
      { "binding_type": "view",
        "source_property_name": "((((((#title_text - 'BedrockIslands') - 'Island Settings') - 'Islands§r') - 'Auction House') = #title_text))",
        "target_property_name": "#visible" }
    ]
  },
  "bi_islands_form@common_dialogs.main_panel_no_buttons": {
    "size": [310, 188], "$child_control": "server_form.bi_islands_panel",
    "bindings": [
      { "binding_name": "#title_text" },
      { "binding_type": "view", "source_property_name": "(#title_text = 'Islands§r')", "target_property_name": "#visible" }
    ]
  }
  ```
  **Achado de maior valor pra este chamado:** o marcador `'Islands§r'` embute literalmente o código de formatação `§r` (reset) **dentro** da string comparada. Isso é exatamente o tipo de string frágil que explica sumiço sem log: se o servidor mandar o título sem esse `§r` final (locale diferente, versão do script que mudou, ou o cliente normalizando/removendo códigos de formatação em algum ponto do pipeline antes do JSON UI enxergar `#title_text`), nenhum dos 4 testes do `default_long_form` bate a substring, a subtração encadeada não muda nada, `(inalterado = original)` fica **verdadeiro**, e **a lista vanilla aparece silenciosamente** — sem `[UI][error]`, porque do ponto de vista do JSON UI está tudo funcionando como programado. **Confiança: confirmado** que essa é a lógica escrita; **provável** que seja a causa mais realista de "sumiço silencioso" citada no problema, porque depende de um detalhe de string (`§r` sobrando ou faltando) fácil de quebrar numa atualização do script do servidor sem tocar em UI nenhuma.
- **Botões:** zero `grid`/`factory` genérico. Cada tela (`bi_main_panel`, `bi_settings_panel`, `bi_islands_panel`, `bi_auction_panel`) é um `stack_panel` artesanal com **`collection_index` literal** por posição (0 a 6 dependendo da tela), usando o template `bi_pic_button` (`$bg` = textura de arte **fixa e hardcoded** por índice, ex. `"textures/ui/menu/islands"`). O texto do botão (`#form_button_text`) só é lido para **decidir entre dois ícones alternativos** (ex. `bi_settings_tile` mostra `set_donate` se o texto for exatamente `'Donate'`, senão `set_pic`) — o texto em si nunca é desenhado como rótulo visível. É a implementação menos "genérica" das 6: um dashboard artesanal para um conjunto fixo e conhecido de botões de um addon específico, não um framework de grid reaproveitável.
- **Size no long_form:** mesmo padrão do skyls (`"100%","100%"` no wrapper, absoluto nos ramos internos) — mesma suspeita moderada de §3.3.
- **Tema:** todos os 5 ramos passam por `common_dialogs.main_panel_no_buttons` → herdam moldura nine-slice vanilla; os botões usam arte PNG própria por índice (`textures/ui/menu/*`), sem nine-slice — cada textura é esticada para o `$slot` exato que foi desenhada, então não há distorção visível **desde que ninguém mude os tamanhos**.
- **Bindings de texto/ícone:** ícone nunca vem de `#form_button_texture` (sempre arte fixa por posição); texto só usado para lógica condicional de ícone, nunca exibido.

### 3.5 `chest_server_form.json` — namespace **diferente**, `chest_ui`

- **Atenção estrutural:** este arquivo declara `"namespace": "chest_ui"`, **não** `"server_form"`. Ele não é, sozinho, um override de `server_form.json` — é uma biblioteca de telas que precisa ser **referenciada a partir de** um `server_form.json` externo (não incluído entre os 6 arquivos fornecidos) via algo como `"...@chest_ui.chest_panel"` dentro de um ramo de `long_form`, no mesmo padrão de `$child_control` visto em §3.3/§3.4. Não dá pra confirmar a "técnica de override" nem a "discriminação por título" deste arquivo isoladamente — só o que ele expõe internamente. **Confiança: confirmado** (é o que o `grep` do namespace mostra); o resto desta ficha descreve só o conteúdo interno.
- **Discriminação interna (dentro de `chest_ui`, entre os 8 tamanhos de baú):**
  ```json
  "chest_ui_template": {
    "type": "panel", "size": ["100%c","100%c"],
    "bindings": [
      { "binding_name": "#title_text", "binding_type": "global" },
      { "binding_type": "view",
        "source_property_name": "(not ((#title_text - $condition) = #title_text))",
        "target_property_name": "#visible" }
    ]
  },
  "chest_panel": { "type": "panel", "size": ["100%","100%"], "controls": [
    { "09@chest_ui.chest_ui_template": { "$grid_size": [9,1], "$condition": "§c§h§e§s§t§0§9", "ignored": "$disable_9_slots_layout" } },
    { "01@chest_ui.chest_ui_template": { "$grid_size": [1,1], "$condition": "§c§h§e§s§t§0§1", "ignored": "$disable_1_slots_layout" } },
    ...
  ]}
  ```
  Marcador **invisível**: cada `$condition` é a palavra (`chest09`, `chest01`, ...) soletrada com um código `§` na frente de **cada caractere** (`§c§h§e§s§t§0§9`). Como códigos de formatação válidos não aparecem como texto no título renderizado, o marcador fica escondido do jogador mas continua presente na string crua `#title_text` que o JSON UI compara. É a mesma técnica usada pelo SonheMenu (§7) — mas aqui **sem ramo de fallback**: se o título não contiver nenhuma das 8 sequências exatas, `chest_panel` inteiro fica em branco (nenhum dos 8 ramos liga), não "cai pra lista vanilla" — cai pra **nada visível**, o que só não é totalmente silencioso porque quem quer que monte o `server_form.json` externo decida o que fica por trás.
  Risco adicional: cada ramo também tem `"ignored": "$disable_N_slots_layout"` — uma variável extra que, se ficar indefinida ou for propagada errada no escopo (`$` variables em JSON UI seguem regra de escopo por herança de template, não são globais), pode desligar um tamanho de baú inteiro mesmo com o marcador de título correto. **Suspeita.**
- **Botões — único dos 6 a usar o control `grid` nativo de verdade:**
  ```json
  "grid_items": {
    "type": "grid", "size": ["100%","default"],
    "grid_dimensions": "$grid_size",
    "grid_item_template": "chest_ui.inventory_item_panel",
    "collection_name": "form_buttons", "layer": 1
  }
  ```
  Isso é genuinamente data-driven (a quantidade de células vem do `$grid_size` por tamanho de baú, não de `collection_index` manual).
- **Bindings de texto/ícone — o esquema mais elaborado e mais frágil dos 6:** o ícone não usa só `#form_button_texture` como caminho de textura; ele também aceita um **inteiro empacotado** decodificado via aritmética:
  ```json
  "$aux_id": [
    { "binding_name": "#form_button_texture", "binding_type": "collection", "binding_collection_name": "form_buttons" },
    { "binding_type": "view", "source_property_name": "(not (('%.8s' * #form_button_texture) = 'textures'))", "target_property_name": "#visible" },
    { "binding_type": "view", "source_property_name": "((#form_button_texture - (#form_button_texture % 65536)) / 65536)", "target_property_name": "#item_id_aux" }
  ]
  ```
  E a quantidade/durabilidade do item são **strings com protocolo próprio** que o UI recorta com operadores printf-like (`'%.14s' * #form_button_text`, `'%.8s'`, `'%.6s'`) procurando sufixos combinados como `'stack#01'` ou `'dur#00'`:
  ```json
  { "source_property_name": "((#form_button_text - 'stack#01') = #form_button_text)", "target_property_name": "#visible" },
  { "source_property_name": "(('§z') + (('%.8s' * #form_button_text) - ('%.6s' * #form_button_text)))", "target_property_name": "#stack_size" }
  ```
  Isso é poderoso (emula um baú de verdade, com `beacon.item_renderer` pra ícone 3D, barra de durabilidade, tooltip) mas depende de um **contrato de string não documentado** entre o script do servidor e este JSON: se o texto do botão não vier exatamente no formato esperado (`...stack#NN`, `...dur#NN`, ID numérico empacotado do jeito certo), a aritmética de string não trava nem loga nada — só produz um número/rótulo errado silenciosamente. É o exemplo mais claro, das 6 fontes, de "falha silenciosa por contrato de dado implícito" em vez de falha de UI propriamente dita.
- **Size:** `chest_panel` = `["100%","100%"]`; como não temos o pai real (arquivo externo não fornecido), não dá pra avaliar o risco de colapso — fica em aberto.
- **Tema:** fundo próprio via `"$border_and_background_texture"` com matemática de nine-slice manual (`"100%c + 14px"`/`"100%c + 11px"`, comentário do próprio autor: `// this line took a decade to figure out`) — não usa `common_dialogs`, estilo visual de contêiner (like `chest_screen.json` vanilla), não de diálogo.

---

## 4. Tabela comparativa

| Critério | easyui | yasser | skyls | tile (BedrockIslands) | chest (`chest_ui`) |
|---|---|---|---|---|---|
| Técnica de override | redefine `long_form@long_form` (estrutura inválida) | redefine `long_form` puro | redefine `long_form` | redefine `long_form` | **não é override de `server_form`** — namespace `chest_ui` à parte, referenciado de fora |
| Discriminação | `#title_text = 'X_EXAMPLE'` (dezenas de ramos, exemplo copiado) | `#text = 'test'` (marcador = palavra comum) | `title - 'Custom Form' = title` (subtração de string) | `title` com 4 substrings encadeadas, uma contendo `§r` embutido | `title - $condition = title`, `$condition` = palavra soletrada com `§` por letra (marcador invisível) |
| Ramos complementares? | indeterminável (estrutura quebrada) | sim (par binário fechado) | sim (subtração cobre "tudo que não é X") | sim, **mas** frágil ao `§r` literal | sim entre os 8 tamanhos; **sem fallback nenhum** se não bater |
| Fallback pra lista vanilla existe? | não | não (substitui `long_form` inteiro) | **sim** — `default_long_form` clona `$child_control: server_form.long_form_panel` | **sim** — mesmo padrão | não (fica em branco, não em lista) |
| Montagem dos botões | indeterminável | 3× `stack_panel` + `collection_index` literal (0–6) | `stack_panel` aninhado + `collection_index` literal (0–3) | `stack_panel` artesanal por tela + `collection_index` literal (0–6) | **`type: grid` real** + `grid_dimensions` + `collection_name` |
| `size` no `long_form` | não declarado | não declarado | `["100%","100%"]` no wrapper, absoluto nos ramos | `["100%","100%"]` no wrapper, absoluto nos ramos | N/A (não é o `long_form`) |
| Tema | herdaria nine-slice vanilla (se carregasse) | ramo lista: nine-slice vanilla · ramo grid: **sem moldura nenhuma** | nine-slice vanilla em ambos ramos (via `common_dialogs`) | nine-slice vanilla em todos ramos + arte PNG fixa por botão | fundo próprio com nine-slice manual, estilo baú |
| Ícone vem do servidor? | indeterminável | **não** (hardcoded por índice) | sim (`#form_button_texture` → `#texture`, padrão vanilla) | **não** (arte fixa por índice; texto só escolhe entre 2 ícones) | sim, incluindo protocolo próprio de ID numérico empacotado |
| Texto do botão exibido? | indeterminável | sim (`collection` → `light_text_button`) | sim (label separado, botão real com `$button_text:"#null"`) | **não** (texto só usado para lógica condicional) | sim, com parsing de sufixos (`stack#NN`, `dur#NN`) |

---

## 5. Ranking de robustez

**Mais robusta: `skyls` (skyls_clean.json).** É a única, das 4 fontes que de fato sobrescrevem `server_form.long_form` sozinhas, que junta tudo que reduz risco de falha silenciosa ao mesmo tempo: (a) tem um ramo `default_long_form` que **realmente recria** a lista vanilla como fallback, então uma falha de marcador degrada pra algo visível e funcional em vez de tela em branco; (b) o binding de ícone (`#form_button_texture`/`#texture_file_system`/estado `loading`) é bit-a-bit igual ao `dynamic_button` vanilla, então reflete o que o servidor realmente manda; (c) separa o botão clicável (`$button_text:"#null"`) do rótulo visível, evitando texto duplicado; (d) ambos os ramos passam por `common_dialogs.main_panel_no_buttons`, herdando moldura nine-slice sem reinventar nada. Ponto fraco real: o marcador `'Custom Form'` é sensível a maiúscula/espaço, e o wrapper externo usa `%` — mas como os ramos internos têm `size` absoluto, isso é só suspeita, não falha confirmada.

**Mais frágil: `chest_server_form.json` (`chest_ui`).** Não por incompetência técnica — é a implementação tecnicamente mais sofisticada das 6 (único `grid` nativo, emula baú de verdade com `item_renderer`) — mas porque empilha três fontes de falha silenciosa ao mesmo tempo: (1) depende de um arquivo externo não fornecido para sequer entrar em cena, então a "discriminação" real está fora do que foi auditado; (2) não tem ramo de fallback — título sem marcador = tela em branco, sem sinal nenhum de qual dos 8 layouts deveria ter aparecido; (3) o binding de ícone/quantidade/durabilidade depende de um contrato de string não documentado (`stack#NN`, `dur#NN`, inteiro empacotado por 65536) entre o script do servidor e este JSON — qualquer divergência de formato produz número ou ícone errado sem erro algum, porque aritmética de string do JSON UI nunca lança exceção, só devolve valor incorreto. `easyui_server_form.json` seria "mais frágil" ainda em sentido absoluto (estrutura de `controls` inválida por schema), mas não conta como implementação de técnica — é lixo de exemplo copiado, não uma escolha de design pra comparar.

---

## 6. Catálogo de causas de falha silenciosa (achados transversais)

| # | Achado | Onde se vê | Confiança |
|---|---|---|---|
| P1 | `main_screen_content` vanilla é `[0,0]`; todo filho direto do `factory` precisa de `size` absoluto (não `%`) na própria invocação, senão colapsa | `server_form.json` vanilla (`long_form@...`: `"size":[225,200]`) | confirmado |
| P2 | `skyls` e `tile_server_form` dão `["100%","100%"]` ao wrapper `long_form` — sob um pai `[0,0]`, isso é risco de colapso *se* o motor recortar (clip) filhos ao tamanho do pai; como os ramos internos têm `size` absoluto, o dano real é incerto | `skyls_clean.json` linha 5-8; `tile_server_form.json` linha 3-8 | suspeita |
| P3 | Marcador de título com código de formatação `§` embutido literal (`'Islands§r'`) quebra silenciosamente se o servidor mandar o título sem esse código | `tile_server_form.json` linha 112 | confirmado (é o que está escrito); provável que seja causa real de sumiço |
| P4 | Marcador invisível "soletrado" com `§` por letra (`§c§h§e§s§t§0§9`) — técnica válida, mas cada `§X` precisa ser um código reconhecido pelo cliente para não aparecer como texto; não testado no jogo | `chest_server_form.json` linha 146 | provável |
| P5 | Ícone de botão hardcoded por `collection_index` em vez de bindado a `#form_button_texture` — funciona só enquanto o servidor mandar os botões sempre na mesma ordem e quantidade | `yasser_server_form.json` linhas 116-148; `tile_server_form.json` (`$bg` fixo em todo `bi_pic_button`) | confirmado |
| P6 | Ramo custom sem `common.common_panel`/nine-slice — sem erro, mas sem moldura nenhuma (visualmente "quebrado" mesmo funcionando) | `yasser_server_form.json`, control `test`, linhas 69-99 (sem `@common_dialogs...`) | confirmado |
| P7 | `"controls"` como objeto em vez de array viola o schema comunitário (`nm:controls` só aceita array ou `$variavel`) | `easyui_server_form.json` linhas 2-31; `ui.schema.json` def `nm:controls` | confirmado (schema) / provável (consequência em jogo) |
| P8 | Ausência de ramo de fallback: se nenhum marcador bater, a tela fica em branco, não vira lista vanilla | `chest_server_form.json` (`chest_panel`, 8 ramos, nenhum "else") | confirmado |
| P9 | Contrato de string implícito entre script e UI (`stack#NN`, `dur#NN`, inteiro empacotado ÷65536) sem validação — divergência de formato = dado errado sem log | `chest_server_form.json` linhas 284-296, 509-521, 564-572 | confirmado (é o que está escrito) |
| P10 | Risco sistêmico fora do JSON: prioridade do RP customizado abaixo da vanilla na pilha de `resource_packs` do mundo faz a definição vanilla de `long_form` vencer por último — sumiço 100% silencioso, nenhuma das 6 fontes previne isso | (não é um arquivo específico — é configuração de mundo) | provável |

---

## 7. Aplicação no SonheMenu

Lido (sem editar) `ADDONS/SonheMenu_RP/ui/_ui_defs.json`, `ui/sonhe_forms.json`, `ui/sonhe_grid.json`.

**Onde o SonheMenu já está alinhado com o padrão mais robusto da amostra (skyls, §3.3/§5):**

- Marcador **invisível** por letra, mesma família da técnica do `chest_server_form` (§3.5, P4): `'§d§r§e§a§m§r'` (soletra "dreamr"), em vez de palavra comum como o `yasser` (P5 evitado).
- Ramos **complementares por construção**, usando a mesma subtração de string que `skyls`/`tile` usam para o fallback:
  ```json
  { "binding_type": "view", "source_property_name": "((#title_text - '§d§r§e§a§m§r') = #title_text)", "target_property_name": "#visible" }
  ```
  para o ramo vanilla, e a negação exata (`not (...)`) para o ramo custom — sem lacuna nem sobreposição, ao contrário do `'test'` do yasser.
- O ramo vanilla (`sonhe_vanilla_form@common_dialogs.main_panel_no_buttons`) **clona de verdade** `$child_control: server_form.long_form_panel` com `size: [225,200]` absoluto — é o mesmo "ramo default explícito" que faltou no `chest_server_form` (P8) e que dá ao SonheMenu uma rede de segurança real: se o marcador falhar por qualquer razão, cai na lista vanilla funcional, não em branco.
- Binding de ícone **idêntico** ao `dynamic_button` vanilla e ao `custom_button` do `skyls` (`#form_button_texture`→`#texture`, guarda de vazio/`'loading'`), documentado no próprio arquivo como "MECANICA PRESERVADA (não mexer)" — é o padrão que se mostrou mais correto na comparação (§3.3, §4).
- Usa `type: grid` nativo (mesma família do `chest_server_form`, §3.5) em vez de `collection_index` manual — mais escalável que `yasser`/`tile`.

**Onde a análise desta comparação levanta suspeita específica para o SonheMenu (nenhuma delas é edição sugerida, só o que a auditoria expõe):**

- `long_form` em `sonhe_forms.json` não declara `size` no wrapper externo (`"long_form": {"type":"panel","controls":[...]}`), igual ao `yasser` (§3.2). Isso só não é risco porque, igual ao `skyls`, os dois ramos internos (`sonhe_vanilla_form` com `[225,200]`, `sonhe_custom_form@sonhe_forms.grid_screen` cujo `grid_screen` declara `[320,452]`) têm tamanho absoluto próprio — mesma suspeita moderada de P2, não confirmada.
- `tiles_grid` usa `grid_dimensions: [3,4]` **fixo, sem binding de contagem** (o próprio arquivo documenta isso de propósito: `"SEM binding de contagem"`). Isso significa que um form do servidor com mais de 12 botões perde os excedentes silenciosamente — sem erro, só sem os itens 13+. Não é o mesmo tipo de bug dos P1-P9 (não é falha de exibição, é limite de capacidade conhecido e documentado pelos próprios comentários do arquivo), mas é o tipo de coisa que, combinada com um form do servidor que cresce com o tempo, pode um dia parecer "sumiço silencioso" pra quem não sabe do limite de 12.
- O risco sistêmico P10 (prioridade do RP na pilha do mundo) se aplica ao SonheMenu como a qualquer um dos 6 — vale conferir a ordem em `world_resource_packs.json` antes de investigar JSON UI, caso o sintoma relatado ("some silenciosamente, cai na lista vanilla") apareça de forma consistente e não pontual.

Nenhum arquivo em `ADDONS/SonheMenu_RP` ou `ADDONS/SonheMenu_BP` foi alterado nesta tarefa.
