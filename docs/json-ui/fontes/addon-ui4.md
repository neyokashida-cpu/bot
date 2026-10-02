# Fonte: addon "ui4" — JSON UI #4 (Custom Buttons)

**Caminho analisado:** `c:/Users/Desktop/Downloads/ADDONS EXEMPLOS/ui4/`
**Arquivos lidos (todos):**

| Arquivo | Bytes | Papel |
|---|---|---|
| `ui4/RP/ui/server_form.json` | 5808 | **único** arquivo de UI do pack |
| `ui4/RP/manifest.json` | — | RP, `min_engine_version [1,20,0]`, módulo `resources` |
| `ui4/BP/manifest.json` | — | BP com módulo `script`, deps `@minecraft/server 1.6.0` + `@minecraft/server-ui 1.1.0` |
| `ui4/BP/scripts/main.js` | — | dois `ActionFormData`, um com título `"Custom Form"` |
| `ui4/RP/pack_icon.png`, `ui4/BP/pack_icon.png` | — | irrelevantes |

**NÃO existe** `ui4/RP/ui/_ui_defs.json`. **NÃO existe** `ui4/RP/textures/`. Zero assets custom.
Referência de vídeo declarada no manifesto do BP: `"metadata": { "url": "https://www.youtube.com/watch?v=Hrpp2Ihg8lU" }`.

---

## Resumo

ui4 é a versão **mínima e "esquelética"** do override de `server_form`: um arquivo só, 5.8 KB, que redefine **exatamente um** controle top-level — `long_form` — e adiciona dois controles auxiliares (`my_super_custom_panel_main` e `custom_button`). Tudo o mais (moldura de diálogo, título, `long_form_panel`, `custom_form`, o `factory` de `main_screen_content`) continua vindo do vanilla.

A técnica central é o **discriminador por título**: o script manda `title("Custom Form")`, e o JSON tem dois ramos irmãos dentro de `long_form`, cada um com um `view` binding em `#visible` que testa o `#title_text`. O ramo que não casa fica invisível — não é removido, é apenas invisível. Isso já explica a classe inteira de "falha silenciosa": **quando a expressão do discriminador não bate, os DOIS ramos podem ficar invisíveis e a tela some sem erro nenhum no log.**

O layout dos botões **não é um grid nem um factory**. É um mosaico de `stack_panel` aninhados onde cada botão é instanciado à mão com um `collection_index` literal (0, 1, 2, 3). Quatro botões fixos, hard-coded, mesmo o script mandando nove. O `main.js` documenta isso no comentário:

```js
res.selection //This Is Number Will Be Derived From The "collection_index" property of a button in JSON UI
```

O tema é **zero**: nenhuma textura própria, nenhuma cor de fundo, nenhuma borda. A moldura é a caixa de diálogo vanilla (`common_dialogs.main_panel_no_buttons`). A única concessão estética é `"color": [0, 0, 0]` no label do botão.

---

## Tabela de padrões

| # | Padrão | Como ui4 faz | Confidence |
|---|---|---|---|
| P1 | Ativar o override | arquivo em `RP/ui/server_form.json`, mesmo caminho do vanilla, `"namespace": "server_form"`, **sem** `_ui_defs.json` | confirmado |
| P2 | Escopo do override | redefine só `long_form`; `long_form_panel`, `custom_form`, `main_screen_content` continuam do vanilla | confirmado |
| P3 | Discriminador | dois filhos irmãos de `long_form` com `view` binding em `#visible` testando `#title_text` | confirmado |
| P4 | Âncora do binding | `{ "binding_name": "#title_text" }` **puro, primeiro**, antes do `view` binding | confirmado |
| P5 | Ramo vanilla | `@common_dialogs.main_panel_no_buttons` com `$child_control: "server_form.long_form_panel"` (cópia literal do vanilla + bindings) | confirmado |
| P6 | Ramo custom | também `@common_dialogs.main_panel_no_buttons`, só troca `$child_control` e `size` | confirmado |
| P7 | Botões de coleção | `collection_index` literal em cada botão + `collection_name: "form_buttons"` repetido em **cada** `stack_panel` da cadeia | confirmado |
| P8 | Contagem da coleção | **nenhum** binding `#form_button_contents` → `#collection_length` | confirmado |
| P9 | Ícone | `type: "image"` **sem** propriedade `texture`, alimentado por `binding_name_override` | confirmado |
| P10 | Clique | `@common_buttons.light_text_button` com `$pressed_button_name: "button.form_button_click"` e `$button_text: "#null"` | confirmado |
| P11 | Wrapper de visibilidade do ícone | `panel_name` com `view` binding + `source_control_name: "image"` + `resolve_sibling_scope: true` | confirmado |
| P12 | `collection_details` | binding no botão clicável, **não** no painel-pai | confirmado |
| P13 | Tema | nenhum. Sem textura, sem `$default_button_texture` | confirmado |
| P14 | Schema | `"$schema": "https://kalmemarq.github.io/Bugrock-JSON-UI-Schemas/ui.schema.json"` (ignorado pelo jogo, ajuda o editor) | confirmado |

---

## Regras extraídas

### R1 — Sobrescrever `server_form` **não** exige `_ui_defs.json`. `[confirmado]`

O pack inteiro é:

```
ui4/RP/manifest.json
ui4/RP/pack_icon.png
ui4/RP/ui/server_form.json
```

Não há `_ui_defs.json` em lugar nenhum. Basta o arquivo estar no **mesmo caminho** do vanilla (`ui/server_form.json`) com o **mesmo namespace**.

**Corolário (importante para o SonheMenu):** existem duas rotas válidas — (a) mesmo caminho, sem `_ui_defs.json`, como ui4/ui5; (b) caminho novo + `_ui_defs.json` declarando o arquivo, como o SonheMenu faz hoje. As duas funcionam, mas a rota (a) tem menos peças que podem quebrar em silêncio.

### R2 — O override é **por chave top-level**, não por arquivo inteiro. `[confirmado]`

Prova direta: ui4 referencia um controle que **nunca define**.

```json
"$child_control": "server_form.long_form_panel",
```

`server_form.long_form_panel` só existe no vanilla (`.../vanilla/ui/server_form.json`, chave `"long_form_panel"`). O addon funciona → as chaves não redefinidas do vanilla continuam resolvíveis. O engine faz merge por nome de controle dentro do namespace, com o pack de prioridade maior vencendo chave a chave.

**Consequência para falha silenciosa:** se você renomear uma chave que o vanilla referencia (ex.: apagar `long_form` do seu arquivo e chamá-lo de `long_form_custom`), o `factory` de `main_screen_content` continua pedindo `"@server_form.long_form"` e vai receber a versão vanilla. Você vê a lista vanilla, sem nenhum erro. **Falha silenciosa clássica.**

Evidência do factory vanilla (`.../vanilla/ui/server_form.json`):

```json
"main_screen_content": {
  "type": "panel",
  "size": [0, 0],
  "controls": [
      {
        "server_form_factory": {
            "type": "factory",
            "control_ids": {
            "long_form": "@server_form.long_form",
            "custom_form": "@server_form.custom_form"
        }
      }
    }
  ]
},
```

### R3 — `long_form` deixa de ser controle derivado e vira `panel` puro com `size` explícito. `[confirmado]`

Vanilla:

```json
"long_form@common_dialogs.main_panel_no_buttons": { ... "size": [225, 200], ... }
```

ui4:

```json
"long_form": {
	"type": "panel",
	"size": ["100%", "100%"],
	"controls": [ ... dois ramos ... ]
},
```

Note que o `size` é **declarado explicitamente**. Não confiar no default.

**Diferença observada no SonheMenu:** `ADDONS/SonheMenu_RP/ui/sonhe_forms.json` declara

```json
"long_form": {
    "type": "panel",
    "controls": [ ... ]
}
```

**sem `size`**. As duas fontes de terceiros (ui4 e ui5) declaram `"size": ["100%", "100%"]`. `[suspeita]` — a omissão do `size` é uma diferença real entre o SonheMenu e as duas fontes que funcionam; não vi o engine falhar por isso, mas é a variável de menor custo para eliminar.

### R4 — O discriminador precisa de uma âncora `binding_name` **antes** do `view` binding. `[confirmado]`

Os dois ramos têm, na mesma ordem:

```json
"bindings": [
	{
		"binding_name": "#title_text"
	},
	{
		"binding_type": "view",
		"source_property_name": "((#title_text - 'Custom Form') = #title_text)",
		"target_property_name": "#visible"
	}
]
```

O primeiro binding (sem `binding_type`, sem `target_property_name`) existe **só** para trazer `#title_text` para o escopo do controle. O segundo lê essa propriedade já resolvida. Sem a âncora, `#title_text` no `view` seria vazio, a expressão daria `('' - 'Custom Form') = ''` → `true` → o ramo vanilla apareceria sempre e o custom nunca. **Falha silenciosa, sem log.**

Esse é o padrão idêntico nos três packs (ui4, ui5, SonheMenu) → é uma regra dura.

### R5 — A expressão do discriminador usa subtração de string, e a **negação lógica é feita invertendo o teste, não com `not`**. `[confirmado no código / provável na semântica]`

Ramo vanilla (aparece quando o título **não** contém o marcador):

```json
"source_property_name": "((#title_text - 'Custom Form') = #title_text)",
```

Ramo custom (aparece quando o título **é** o marcador):

```json
"source_property_name": "(#title_text = 'Custom Form')",
```

Leitura: `A - B` remove de `A` a primeira ocorrência da substring `B`. Se o resultado é igual a `A`, então `B` não estava em `A`.

`[confirmado]` que o par é exatamente esse no arquivo.
`[provável]` a semântica de `-` como remoção de substring: **não encontrei nenhum uso de `-` sobre strings em todo o corpus vanilla de 188 arquivos** (`grep -rn "source_property_name" | grep -- " - '"` → 0 resultados). O que o vanilla tem é o operador `+` de concatenação:

```json
"source_property_name": "('textures/ui/game_tip_animations/' + #animation_name)",
```
(`.../vanilla/ui/game_tip_screen.json`)

Ou seja: `-` sobre string é feature real usada por terceiros, mas **fora do repertório da Mojang**. Isso é relevante — é território menos testado.

**Assimetria a notar:** ui4 usa `=` **exato** no ramo custom (`#title_text = 'Custom Form'`), não subtração. Isso significa que o título tem de ser *exatamente* `"Custom Form"`. O SonheMenu usa o par simétrico com subtração dos dois lados:

```json
"source_property_name": "(not ((#title_text - '§d§r§e§a§m§r') = #title_text))",
```

O par do SonheMenu é mais robusto (aceita marcador embutido em qualquer posição) mas depende de **duas** features menos comuns: `-` sobre string **e** `not` aplicado ao resultado. `[suspeita]` — se houver um ponto de fragilidade no discriminador do SonheMenu, é a combinação `not (... = ...)` com subtração dentro; ui4/ui5 nunca escrevem `not` no ramo custom.

### R6 — O ramo custom pode continuar herdando a moldura vanilla. `[confirmado]`

ui4 **não** desenha nada próprio. O ramo custom é o mesmo template da caixa de diálogo:

```json
{
	"cutsom_long_form@common_dialogs.main_panel_no_buttons": {
		"$title_panel": "common_dialogs.standard_title_label",
		"$title_size": ["100% - 14px", 10],
		"size": [322.5, 185],
		"$text_name": "#title_text",
		"$title_text_binding_type": "none",
		"$child_control": "server_form.my_super_custom_panel_main",
		"layer": 2,
		"bindings": [ ... ]
	}
}
```

(o typo `cutsom_` é literal no arquivo — nome de controle é livre, não valida contra nada)

Só quatro coisas mudam em relação ao ramo default: o nome, o `size` (`[322.5, 185]` — note o **float**, aceito), o `$child_control`, e a direção do teste de `#visible`.

**`$title_size` divergente do vanilla:** ui4 usa `["100% - 14px", 10]`; o vanilla usa `["100% - 15px", 10]` e ainda passa `$title_max_size`. ui4 **omite `$title_max_size`**. O default sobrevive porque `common_dialogs.standard_title_label` declara:

```json
"$title_max_size|default": [ "default", 10 ],
"max_size": "$title_max_size",
```
(`.../vanilla/ui/ui_template_dialogs.json`)

→ **Regra geral:** `$var|default` no template significa que omitir a variável no consumidor é seguro. Omitir uma variável **sem** `|default` no template é o que estoura. `[confirmado]`

### R7 — Layout de mosaico: `stack_panel` aninhados + `collection_index` literal. `[confirmado]`

Não há `grid`, não há `factory`. A estrutura inteira:

```json
"my_super_custom_panel_main": {
	"type": "stack_panel",
	"size": ["100%", "100%"],
	"orientation": "horizontal",
	"anchor_from": "center",
	"anchor_to": "center",
	"collection_name": "form_buttons",

	"controls": [
		{
			"offset_button@server_form.custom_button": {
				"$icon_size": [69, 69],
				"$button_size": [133, 133],
				"$padding": [153, 153],
				"collection_index": 0
			}
		},
		{
			"right_side_stack": {
				"type": "stack_panel",
				"size": ["100%", "100%"],
				"orientation": "vertical",
				"anchor_from": "center",
				"anchor_to": "center",
				"collection_name": "form_buttons",
				"controls": [
					{
						"offset_button@server_form.custom_button": {
							"$button_size": [138, 55],
							"$padding": [148, 76.5],
							"collection_index": 1
						}
					},
					{
						"bottom_right_stack": {
							"type": "stack_panel",
							"size": ["100%", "100%"],
							"orientation": "horizontal",
							"anchor_from": "center",
							"anchor_to": "center",
							"collection_name": "form_buttons",
							"controls": [
								{
									"offset_button@server_form.custom_button": {
										"$button_size": [64, 64],
										"$padding": [74, 69],
										"collection_index": 2
									}
								},
								{
									"offset_button@server_form.custom_button": {
										"$button_size": [64, 64],
										"$padding": [74, 69],
										"collection_index": 3
									}
								}
							]
						}
					}
				]
			}
		}
	]
},
```

Três fatos duros aqui:

1. **`collection_name: "form_buttons"` é repetido em CADA nível de `stack_panel`** — no pai, no `right_side_stack` e no `bottom_right_stack`. Não é herdado automaticamente pelo aninhamento. `[confirmado — repetição literal em 3 níveis]`
2. **Dois filhos irmãos com o MESMO nome** (`offset_button` aparece 2x dentro de `bottom_right_stack`) e isso **não** quebra. `[confirmado]`
3. **Não existe binding de `#collection_length`.** Como os índices são literais, o engine não precisa saber o tamanho da coleção. `[confirmado]` — o vanilla, em contraste, precisa:
```json
"collection_name": "form_buttons",
"bindings": [
  {
    "binding_name": "#form_button_contents",
    "binding_name_override": "#collection_length"
  }
]
```
→ **`collection_index` fixo e `#collection_length` são alternativas, não complementos.**

### R8 — Espaçamento é feito por um painel-invólucro maior que o botão (`$padding`), não por margem. `[confirmado]`

```json
"custom_button": {
	"$padding|default": [80, 80],
	"$button_size|default": [64, 64],
	"$icon_size|default": [32, 32],
	"type": "panel",
	"size": "$padding",
	"controls": [
		{
			"main_ui": {
				"type": "panel",
				"size": "$button_size",
				...
```

`$padding` é o slot ocupado no `stack_panel`; `$button_size` é o botão desenhado dentro. A diferença é o respiro. Ex.: botão `[64,64]` dentro de slot `[74,69]`.

Os três `$var|default` no topo do controle garantem que instanciar `@server_form.custom_button` sem passar nada ainda renderiza. **Boa prática defensiva.**

### R9 — Ícone: `image` **sem** `texture`, alimentado por `binding_name_override`. `[confirmado]`

```json
{
	"image": {
		"type": "image",
		"layer": 200,
		"size": "$icon_size",
		"offset": [0, -5],
		"bindings": [
			{
				"binding_name": "#form_button_texture",
				"binding_name_override": "#texture",
				"binding_type": "collection",
				"binding_collection_name": "form_buttons"
			},
			{
				"binding_name": "#form_button_texture_file_system",
				"binding_name_override": "#texture_file_system",
				"binding_type": "collection",
				"binding_collection_name": "form_buttons"
			},
			{
				"binding_type": "view",
				"source_property_name": "(not ((#texture = '') or (#texture = 'loading')))",
				"target_property_name": "#visible"
			}
		]
	}
}
```

Cinco detalhes que são regra:

- Nenhuma propriedade `"texture"` no controle. Se você colocar `"texture": "..."`, o binding compete com o literal.
- `#form_button_texture_file_system` **sempre** acompanha `#form_button_texture`. Sem ele, ícones que vêm de resource pack vs. de arquivo não resolvem.
- O `view` de `#visible` vem **por último**, depois dos bindings que produzem `#texture`. Ordem importa: view bindings leem o estado já montado.
- `layer: 200` — muito alto, para o ícone ficar acima das faces do botão vanilla.
- O teste inclui `'loading'`: enquanto a textura carrega, `#texture` vale literalmente a string `loading`.

**Isto é cópia literal do vanilla** (`dynamic_button` em `.../vanilla/ui/server_form.json`), inclusive a expressão. Quando você copia esse trio de bindings você está em terreno testado pela Mojang.

### R10 — Wrapper de visibilidade cross-control via `resolve_sibling_scope`. `[confirmado]`

```json
"panel_name": {
	"type": "panel",
	"size": "$button_size",
	"bindings": [
		{
			"binding_type": "view",
			"source_control_name": "image",
			"resolve_sibling_scope": true,
			"source_property_name": "(not (#texture = ''))",
			"target_property_name": "#visible"
		}
	],
	"controls": [ { "image": {...} }, { "text": {...} } ]
}
```

O painel lê `#texture` **de dentro do filho chamado `image`**. `source_control_name` + `resolve_sibling_scope: true` é o mecanismo. Também cópia literal do vanilla (`dynamic_button.panel_name`).

**Armadilha:** `source_control_name: "image"` casa pelo **nome do controle**. Se você renomear o filho `image` para outra coisa e esquecer de atualizar aqui, o binding não resolve → o painel some inteiro (ícone + label) → **falha silenciosa**. `[provável]`

### R11 — O clique é delegado ao `light_text_button` vanilla, com o texto neutralizado por `#null`. `[confirmado]`

```json
{
	"form_button@common_buttons.light_text_button": {
		"$pressed_button_name": "button.form_button_click",
		"anchor_from": "top_left",
		"anchor_to": "top_left",
		"size": "$button_size",
		"$button_text": "#null",
		"$button_text_binding_type": "collection",
		"$button_text_grid_collection_name": "form_buttons",
		"$button_text_max_size": ["100%", 20],
		"bindings": [
			{
				"binding_type": "collection_details",
				"binding_collection_name": "form_buttons"
			}
		]
	}
}
```

- `$button_text: "#null"` → o botão continua sendo botão, mas não desenha texto. O texto real é o label irmão `text` no `panel_name`. **Este é o truque para ter ícone-em-cima-de-texto em vez do texto do vanilla.**
- `"binding_type": "collection_details"` no **próprio botão** é o que faz `res.selection` no script devolver o índice certo. Sem ele o clique não sabe qual item da coleção foi acionado.
- `$pressed_button_name: "button.form_button_click"` é o ID que o `server-ui` escuta. **Literal obrigatório**, não inventável.

### R12 — Label do botão é um `label` irmão, não o texto do botão. `[confirmado]`

```json
{
	"text": {
		"type": "label",
		"text": "#form_button_text",
		"layer": 32,
		"color": [0, 0, 0],
		"offset": [0, -8],
		"anchor_from": "bottom_middle",
		"bindings": [
			{
				"binding_name": "#form_button_text",
				"binding_type": "collection",
				"binding_collection_name": "form_buttons"
			}
		]
	}
}
```

Note: `"text": "#form_button_text"` **e** o binding com o mesmo nome. Os dois juntos. A propriedade `text` declara qual token renderizar; o binding traz o valor daquele índice da coleção.

`color: [0, 0, 0]` — preto. ui4 assume fundo claro (moldura vanilla). Em fundo escuro isso some.

### R13 — Camadas (`layer`) usadas em degraus largos. `[confirmado]`

| Controle | layer |
|---|---|
| ramo `long_form` (ambos) | `2` |
| `image` (ícone) | `200` |
| `text` (label) | `32` |
| `form_button` | herdado do template |

Nada de `layer: 1, 2, 3`. Degraus grandes para não colidir com as camadas internas de `light_text_button` (que usa `1/4/5` para default/hover/pressed — ver `.../vanilla/ui/ui_template_buttons.json`).

### R14 — O `$schema` é decorativo. `[confirmado]`

```json
"$schema": "https://kalmemarq.github.io/Bugrock-JSON-UI-Schemas/ui.schema.json",
```

Presente em ui4 **e** ui5, lado a lado com `"namespace"`. O jogo ignora a chave; serve para autocomplete no VS Code. Não é fonte de erro nem de proteção.

### R15 — O lado do script é trivial e o marcador é o título inteiro. `[confirmado]`

`ui4/BP/scripts/main.js`:

```js
const customUi = new ActionFormData()
    .title("Custom Form")
    .body("")
    .button("Rewards", "textures/ui/promo_holiday_gift_small")
    .button("Shop", "textures/ui/icon_deals")
    .button("Ban Tool", "textures/ui/hammer_l")
    .button("Skins", "textures/ui/icon_hangar")
    // ... mais 5 iguais, 9 no total
```

Nove botões no script, **quatro** slots no JSON. Os cinco restantes simplesmente não são desenhados — **sem erro, sem aviso**. É a demonstração mais limpa da falha silenciosa: a UI custom não some, mas dados somem.

E `.body("")` — string vazia. ui4 nunca renderiza `#form_text`; o ramo custom não tem nenhum controle lendo `#form_text`.

---

## O que ui4 ensina sobre a **falha silenciosa** (o problema central do SonheMenu)

Ordenado por probabilidade de ser a causa, com base no que este pack faz e no que o SonheMenu faz diferente:

| Hipótese | Mecanismo | Confidence |
|---|---|---|
| H1 | O discriminador de `#visible` avaliou falso nos dois ramos → nada desenha. O jogo não loga expressão que resolve para vazio. | confirmado (mecanismo); provável (é a causa no SonheMenu) |
| H2 | A âncora `{ "binding_name": "#title_text" }` foi removida/reordenada → `#title_text` vazio no `view` → ramo custom nunca visível, ramo vanilla sempre visível = **exatamente "caiu na lista vanilla"** | confirmado (mecanismo) |
| H3 | Chave top-level renomeada: o factory vanilla continua resolvendo `@server_form.long_form` para a versão vanilla | confirmado |
| H4 | `$variável` sem `|default` no template consumido e não passada pelo consumidor | confirmado (o mecanismo `|default` existe; ver R6) |
| H5 | `source_control_name` apontando para um nome de filho que não existe mais | provável |
| H6 | `size` omitido no `long_form` (SonheMenu omite; ui4 e ui5 declaram `["100%","100%"]`) | suspeita |

**Regra operacional derivada:** quando a UI "some e cai no vanilla", o ramo vanilla está **visível**. Isso significa que o teste do ramo vanilla deu `true`. Nos dois ramos o teste é sobre `#title_text`. Logo o suspeito nº 1 é sempre `#title_text` chegar vazio ou diferente do esperado — **não** o layout, **não** o grid.

---

## Aplicação no SonheMenu

### O que o SonheMenu já faz igual a ui4 (não mexer)

- Redefine **só** `long_form` como `panel` com dois ramos irmãos. `ADDONS/SonheMenu_RP/ui/sonhe_forms.json`:
```json
"long_form": {
    "type": "panel",
    "controls": [
      { "sonhe_vanilla_form@common_dialogs.main_panel_no_buttons": { ... } },
      { "sonhe_custom_form@sonhe_forms.grid_screen": { ... } }
    ]
}
```
- Âncora `{ "binding_name": "#title_text" }` antes do `view` binding, nos dois ramos. **Idêntico a ui4.** Correto.
- Ramo vanilla é a cópia literal do vanilla com `$child_control: "server_form.long_form_panel"`. **Idêntico a ui4.** Correto.
- Trio de bindings do ícone (`#form_button_texture` + `#form_button_texture_file_system` + `view` de `#visible` com teste de `'loading'`) em `sonhe_forms.tile_icon`. **Idêntico a ui4/vanilla.** Correto.
- `$pressed_button_name: "button.form_button_click"`. Correto.
- Ausência de binding `#collection_length` no grid (`tiles_grid` usa `grid_dimensions` fixo). Consistente com R7 — índice determinado estaticamente dispensa contagem.

### Divergências reais entre SonheMenu e ui4 — ranqueadas

**D1 — `long_form` sem `size`.** `[suspeita, custo zero de corrigir]`
ui4: `"size": ["100%", "100%"]`. ui5: idem. SonheMenu: ausente.
Teste: adicionar `"size": [ "100%", "100%" ]` em `long_form` de `sonhe_forms.json`. Uma linha, reversível.

**D2 — Forma do discriminador custom.** `[suspeita]`
ui4/ui5 ramo custom: `"(#title_text = 'Custom Form')"` — igualdade simples, sem `not`, sem `-`.
SonheMenu ramo custom: `"(not ((#title_text - '§d§r§e§a§m§r') = #title_text))"` — `not` + subtração.
O SonheMenu depende de **duas** features fora do repertório vanilla. Se o marcador puder ir no título inteiro (ex.: `title("§d§r§e§a§m§r" + nome)` continua embutido, mas se o marcador fosse o título todo), a forma de ui4 seria mais segura.
Além disso: o marcador `§d§r§e§a§m§r` é uma sequência de **códigos de cor**. `[suspeita]` — códigos `§` podem ser consumidos/normalizados pelo pipeline de texto antes de chegar em `#title_text`; ui4/ui5 usam texto ASCII puro (`Custom Form`). Vale um teste A/B com marcador ASCII.

**D3 — `collection_index` vs. `grid_dimensions`.** `[confirmado como diferença; não como defeito]`
ui4 instancia N botões à mão com `collection_index` literal e **não** usa `grid`. SonheMenu usa `type: "grid"` + `grid_dimensions: [3, 4]` + `grid_item_template`.
As duas rotas são válidas. A de ui4 é mais burra e mais previsível: **se o grid do SonheMenu voltar a falhar em popular, a rota ui4 (12 instâncias explícitas de `tile` com `collection_index` 0..11 dentro de `stack_panel` aninhados) é um fallback que dispensa `grid` inteiramente.** É um terceiro caminho além do `list_screen` que o `sonhe_grid.json` já documenta como fallback.
Cuidado: nessa rota é obrigatório repetir `"collection_name": "form_buttons"` em **cada** `stack_panel` da cadeia (R7.1).

**D4 — `collection_details` no botão.** `[confirmado, e o SonheMenu já está certo]`
ui4 põe `collection_details` no `form_button`. SonheMenu põe em `tile_button` (o botão) — mesma posição. Correto. O comentário `//2` do `sonhe_grid.json` já registra isso como "mecânica preservada".

**D5 — Rota de instalação.** `[confirmado como diferença]`
ui4 não tem `_ui_defs.json`; o arquivo está em `ui/server_form.json`.
SonheMenu tem `_ui_defs.json` apontando para `ui/sonhe_forms.json` + `ui/sonhe_grid.json`.
A rota do SonheMenu adiciona uma dependência: se `_ui_defs.json` não for lido (typo no caminho, arquivo fora da lista, cache do cliente), **os dois arquivos simplesmente não existem para o engine** e a tela é a vanilla — **sem nenhum `[UI][error]`, porque não há JSON inválido, só JSON não carregado.** Este é um vetor de falha silenciosa que ui4 **não tem**.
Mitigação barata: renomear `sonhe_forms.json` → `server_form.json` (mesmo caminho do vanilla) e manter só `sonhe_grid.json` no `_ui_defs.json`. Reduz a superfície pela metade.

### Checklist de bisseção quando a UI sumir (derivado de ui4)

1. O ramo vanilla está aparecendo? Se sim → o teste de `#title_text` do ramo vanilla deu `true` → o problema é o **discriminador**, não o layout.
2. Trocar temporariamente o `view` binding do ramo custom por `"source_property_name": "(1 = 1)"` e o do vanilla por `"(1 = 0)"`. Se a tela custom aparece → é 100% discriminador. Se não aparece → é layout/binding interno.
3. Trocar o marcador `§d§r§e§a§m§r` por ASCII (`SONHE`) nos dois lados (script + JSON) e repetir.
4. Trocar a expressão custom pela forma de ui4: `"(#title_text = 'SONHE')"`, com o script mandando `title("SONHE")` exato.
5. Só depois disso investigar `grid`, `tile`, ícones.

### Snippet pronto: fallback estilo-ui4 (sem `grid`) para o SonheMenu

Se o `grid` voltar a falhar, esta topologia dispensa `grid_dimensions`, `grid_item_template` e qualquer binding de contagem. Cada tile é explícito.

```json
"tiles_manual": {
  "type": "stack_panel",
  "orientation": "vertical",
  "size": [ 288, "100%c" ],
  "collection_name": "form_buttons",
  "controls": [
    { "row0@sonhe_forms.tiles_row": { "$i0": 0, "$i1": 1, "$i2": 2 } },
    { "row1@sonhe_forms.tiles_row": { "$i0": 3, "$i1": 4, "$i2": 5 } },
    { "row2@sonhe_forms.tiles_row": { "$i0": 6, "$i1": 7, "$i2": 8 } },
    { "row3@sonhe_forms.tiles_row": { "$i0": 9, "$i1": 10, "$i2": 11 } }
  ]
},

"tiles_row": {
  "type": "stack_panel",
  "orientation": "horizontal",
  "size": [ "100%", 96 ],
  "collection_name": "form_buttons",
  "controls": [
    { "c0@sonhe_forms.tile": { "collection_index": "$i0" } },
    { "c1@sonhe_forms.tile": { "collection_index": "$i1" } },
    { "c2@sonhe_forms.tile": { "collection_index": "$i2" } }
  ]
}
```

Ressalvas antes de usar:
- `"collection_name": "form_buttons"` **precisa** estar em `tiles_manual` e em `tiles_row` (R7.1 — ui4 repete em 3 níveis).
- `[suspeita]` `collection_index` recebendo `"$i0"` (variável) em vez de literal não é atestado por ui4/ui5 — eles sempre escrevem o número cru (`0`, `1`, `2`, `3`). Se der problema, expandir as 12 instâncias à mão com números literais.
- O comentário `//3` de `sonhe_grid.json` lista `collection_index` como PROIBIDO nesta build. **Essa proibição vale para a topologia de `grid`** (onde o item já é indexado pelo grid). Fora do `grid`, dentro de `stack_panel`, é exatamente o que ui4 e ui5 fazem e funciona.

---

## Apêndice: `server_form.json` de ui4 na íntegra

```json
{
	"namespace": "server_form",
	"$schema": "https://kalmemarq.github.io/Bugrock-JSON-UI-Schemas/ui.schema.json",

	"long_form": {
		"type": "panel",
		"size": ["100%", "100%"],
		"controls": [
			{
				"default_long_form@common_dialogs.main_panel_no_buttons": {
					"$title_panel": "common_dialogs.standard_title_label",
					"$title_size": ["100% - 14px", 10],
					"size": [225, 200],
					"$text_name": "#title_text",
					"$title_text_binding_type": "none",
					"$child_control": "server_form.long_form_panel",
					"layer": 2,
					"bindings": [
						{
							"binding_name": "#title_text"
						},
						{
							"binding_type": "view",
							"source_property_name": "((#title_text - 'Custom Form') = #title_text)",
							"target_property_name": "#visible"
						}
					]
				}
			},
			{
				"cutsom_long_form@common_dialogs.main_panel_no_buttons": {
					"$title_panel": "common_dialogs.standard_title_label",
					"$title_size": ["100% - 14px", 10],
					"size": [322.5, 185],
					"$text_name": "#title_text",
					"$title_text_binding_type": "none",
					"$child_control": "server_form.my_super_custom_panel_main",
					"layer": 2,
					"bindings": [
						{
							"binding_name": "#title_text"
						},
						{
							"binding_type": "view",
							"source_property_name": "(#title_text = 'Custom Form')",
							"target_property_name": "#visible"
						}
					]
				}
			}
		]
	},

	"my_super_custom_panel_main": { /* ver R7 acima — íntegra */ },

	"custom_button": { /* ver R8/R9/R10/R11/R12 acima — íntegra */ }
}
```

(os dois blocos elididos estão transcritos literalmente nas regras R7 a R12; nada foi omitido do arquivo — ele tem exatamente 3 chaves além de `namespace` e `$schema`)
