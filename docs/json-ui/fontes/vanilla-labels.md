# JSON UI vanilla — texto, truncamento e labels multi-linha (cliente 1.26.44)

Corpus: `c:/Users/Desktop/Documents/Nova pasta/assets/assets/resource_packs/vanilla/ui/`
Regra seguida: toda afirmação tem caminho + trecho literal. Sem trecho = marcado como "suspeita".

---

## 1) Catálogo de uso (grep)

| Propriedade | Arquivos com ocorrência | Observação |
|---|---|---|
| `max_size` | 82 arquivos | uso mais comum: tooltips, labels de nome/skin, scroll viewports |
| `font_type` | 79 arquivos | valores encontrados: `"smooth"`, `"default"`, `"rune"`, `"MinecraftTen"` |
| `font_scale_factor` | 52 arquivos | varia de 0.5 a 1.5 (ver seção 5) |
| `text_alignment` | 72 arquivos | valores encontrados: `"left"`, `"center"`, `"right"` (nenhum outro valor existe no corpus) |

Exemplos de arquivo por propriedade: `ui_common.json`, `settings_sections/general_section.json`, `skin_picker_screen.json`, `expanded_skin_pack_screen.json`, `csb_sections/csb_subscription_panel.json`, `store_data_driven_screen.json`.

confidence: **confirmado** (contagem de grep direta no corpus).

---

## 2) max_size — truncamento Y com "..." e quebra X com hífen

Evidência literal, comentário do próprio Mojang no código-fonte:

```
c:\Users\Desktop\Documents\Nova pasta\assets\assets\resource_packs\vanilla\ui\ui_common.json:7202
// $tool_tip_text_max_size defines how text wraps (x wraps with a '-' and y will cut off with '...')
```

Isso confirma exatamente:
- **Eixo X** do `max_size` (largura): quando uma palavra não cabe, o motor quebra a palavra com um **hífen `-`** e continua na linha seguinte.
- **Eixo Y** do `max_size` (altura): quando o texto excede a altura disponível, o motor **corta (trunca) com reticências `...`**.

Propriedade complementar confirmada: `hide_hyphen`. Ela existe justamente porque o hífen de quebra de palavra (eixo X) é o comportamento *padrão* e precisa ser desligado explicitamente:

```
c:\...\vanilla\ui\settings_sections\general_section.json:2824
"hide_hyphen": true,
```

Segunda evidência (truncamento por limite rígido de pixels, mesmo texto/comentário duplicado em dois arquivos):

```
c:\...\vanilla\ui\skin_picker_screen.json:1306-1323
c:\...\vanilla\ui\expanded_skin_pack_screen.json:675-692
// In the edge case where the skin name is too long to fit, ... then the
// skin name should truncate. Since the label's parent control has a width
// of "100%c", this truncation must be due to a hard pixel limit for the
// label width.
...
"size": [ "default", 10 ],
"max_size": [ 181, 10 ],
```

confidence: **confirmado**.

---

## 3) Label multi-linha de altura variável (sem truncar, sem ciclo)

Padrão confirmado: **label sem `max_size`**, com `size` usando `"default"` (ou omitindo o eixo) para a altura, dentro de um `stack_panel` cujo próprio `size` usa `"100%c"` na altura (sizes-to-children). Como o pai cresce a partir do filho e o filho não tem um `max_size` que o prenda, não há dependência circular — o filho define sua altura pelo texto, o pai absorve essa altura.

Exemplo vanilla literal (label dentro de stack_panel, cresce com o texto, sem max_size):

```
c:\...\vanilla\ui\settings_sections\general_section.json:21-23  (o stack_panel ancestral)
"general_tab_section": {
  "type": "stack_panel",
  "size": [ "100%", "100%c" ],
  ...

c:\...\vanilla\ui\settings_sections\general_section.json:2819-2836  (o label filho)
"content_log_location_label": {
  "type": "label",
  "text": "#text",
  "size": [ "100%", "default" ],
  "color": "$body_text_color",
  "hide_hyphen": true,
  "bindings": [ ... ]
}
```

Segundo exemplo (mesmo padrão, `size: ["90%", "default"]`, zero `max_size`):

```
c:\...\vanilla\ui\csb_sections\csb_subscription_panel.json:218-229
"panel_details_ln1": {
  "type": "label",
  "text": "$benefit",
  "font_type": "smooth",
  "text_alignment": "left",
  "size": [ "90%", "default" ]
}
```

confidence: **confirmado**.

---

## 4) size vs max_size vs min_size — tabela

| Propriedade | Eixo X (largura) | Eixo Y (altura) |
|---|---|---|
| `size` | Tamanho-base/preferido. `"default"` = ajusta à largura do texto/conteúdo. `"100%"`, valores fixos ou `"100%c"` (child-sizing) também valem. | Idem: `"default"` faz a altura do label seguir o texto já quebrado (após aplicar wrap). |
| `min_size` | Piso: o controle nunca fica mais estreito que isto, mesmo que `size` calculado seja menor. | Piso de altura — útil para não colapsar quando o texto está vazio/curto. |
| `max_size` | Teto de largura. Ao ser atingido, o texto quebra linha; se uma palavra sozinha não couber, ela é hifenizada (`-`), salvo `hide_hyphen: true`. | Teto de altura. Ao ser atingido, o texto restante é **cortado com "..."** (evidência seção 2). |

Efeitos combinados observados no corpus:
- `size: ["default","default"]` + sem `max_size`/`min_size` → label cresce livremente nos dois eixos (ex.: `tooltip_text` em `ui_common.json:7098-7102` quando `$tool_tip_text_max_size` não é sobrescrito).
- `size` com largura fixa + `max_size` com altura fixa pequena → truncamento garantido com "..." (é exatamente o bug do `screen_body`, seção 7).
- `min_size` sem `max_size` → controle pode crescer sem limite, só não encolhe abaixo do piso (`ui_common.json:7163`: `"min_size": [25, "default"]`).

confidence: **confirmado** para os padrões com trecho citado; **provável** para a generalização da coluna "efeito" (mecânica padrão do motor JSON UI, documentada de forma indireta pelos comentários do próprio Mojang, não por um único trecho exaustivo).

---

## 5) Fontes disponíveis

Declaradas em `font/font_metadata.json` e usadas via `font_type`/`backup_font_type` em `ui/*.json`:

| font_type | Onde aparece | Nota |
|---|---|---|
| `"smooth"` | majoritário (texto de corpo em quase toda UI) | fonte SDF (`font/smooth/*.fontdata`), suave em qualquer escala |
| `"default"` | bitmap 8px (`font/default8.png`, `glyph_XX.png`) | fonte pixelada legada |
| `"rune"` | `enchanting_screen.json:129` | glifos da mesa de encantamento |
| `"MinecraftTen"` | `ui_common.json:3145-3157` (`minecraftTenLabel`), `sonhe_forms.json:screen_title` (uso do addon) | fonte de título (TrueType, `font/minecraft-ten.ttf`); **sempre** combinada com `"backup_font_type": "UIFont"` e comentário explícito: `// We don't load MinecraftTen in these cases so we need to revert to Mojangles.` (dispositivos low-memory) |
| `"UIFont"` | só aparece como **`backup_font_type`**, nunca como `font_type` primário | fallback de segurança para MinecraftTen |

`SmoochSans`: **não encontrado** em nenhum arquivo do corpus (`ui/`, `font/font_metadata.json`). confidence: **suspeita** de que não exista como `font_type` selecionável em JSON UI nesta versão — pode ser confusão com a tipografia de marca usada fora do JSON UI (launcher/loja), não confirmável aqui.

### font_scale_factor — limite prático
Valores observados no corpus vão de **0.5** (`csb_subscription_panel.json:211`, bullet decorativo) a **1.5** (`persona_common.json:493`) e **1.39** especificamente para `MinecraftTen` (`ui_common.json:3154`, com offset `[0,-2]` compensando o baseline da fonte).
- Não há nenhum comentário vanilla definindo um "limite técnico" numérico — o motor não trava o valor.
- Na prática, os únicos valores > 1.3 usados sempre vêm acompanhados de ajuste de `offset` e de `size`/`max_size` dedicados (ex. `MinecraftTen`), evidência de que escalas grandes exigem realocar espaço manualmente, senão cortam texto ou colidem com vizinhos.
- confidence: **provável** para "0.7–1.2 é a faixa segura sem ajuste extra" (é o que domina o corpus); **confirmado** que valores fora disso (0.5, 1.33, 1.39, 1.5) só aparecem com offset/size compensados manualmente.

---

## 6) text_alignment

Valores confirmados no corpus (nenhum outro existe):

| Valor | Efeito |
|---|---|
| `"left"` | Alinha o texto à esquerda da caixa do label (padrão do motor quando omitido). |
| `"center"` | Centraliza cada linha horizontalmente dentro da largura do label. |
| `"right"` | Alinha à direita. |

confidence: **confirmado** (grep exaustivo, só esses 3 valores aparecem em 72 arquivos).

---

## 7) Problema concreto — `screen_body` truncando com "..."

Arquivo do addon (lido, **não editado**, conforme instrução):
`C:/Users/Desktop/Desktop/Projetos/bot/ADDONS/SonheMenu_RP/ui/sonhe_grid.json:88-106`

```json
"screen_body": {
  "type": "label",
  "text": "#form_text",
  "size": [ "100% - 8px", "default" ],
  "max_size": [ "100% - 8px", 30 ],
  "text_alignment": "left",
  "font_type": "smooth",
  "font_size": "normal",
  "line_padding": 1,
  "color": [ 0.72, 0.72, 0.78 ],
  "shadow": false,
  "hide_hyphen": true,
  "localize": false,
  "layer": 3,
  "bindings": [ { "binding_name": "#form_text" } ]
}
```

Diagnóstico: `max_size` trava a altura em **30px** (≈3 linhas de fonte `smooth`). Pela evidência da seção 2 (`ui_common.json:7202`), ultrapassar essa altura força o motor a **cortar o texto com "..."** — é exatamente o sintoma relatado.

O controle é usado dentro de `grid_stack` e `list_stack` (`sonhe_grid.json:41-56` e `379-395`), que **já são** `stack_panel` com `"size": [288, "100%c"]` — ou seja, a altura do pai **já** se ajusta ao conteúdo. Isso é o mesmo formato do exemplo vanilla confirmado na seção 3 (`general_tab_section` + `content_log_location_label`).

### Correção proposta (baseada só nos padrões confirmados acima)

Remover o teto de altura do `max_size`, deixando apenas o teto de largura (que é o eixo que você quer mesmo limitar, para a quebra de linha automática continuar funcionando):

```json
"screen_body": {
  "type": "label",
  "text": "#form_text",
  "size": [ "100% - 8px", "default" ],
  "max_size": [ "100% - 8px" ],
  "text_alignment": "left",
  "font_type": "smooth",
  "font_size": "normal",
  "line_padding": 1,
  "color": [ 0.72, 0.72, 0.78 ],
  "shadow": false,
  "hide_hyphen": true,
  "localize": false,
  "layer": 3,
  "bindings": [ { "binding_name": "#form_text" } ]
}
```

Por que isso é seguro e segue o padrão vanilla:
- `size: ["100% - 8px", "default"]` já é o que faz a quebra automática de linha (largura fixa + altura `"default"`) — igual ao padrão `panel_details_ln1` (seção 3), que usa `["90%", "default"]` sem `max_size` nenhum.
- Ao tirar o segundo elemento do `max_size`, você mantém o teto de largura (evita que o label espalhe para os lados) mas remove o teto de altura que causava o corte com "...".
- Não há dependência circular porque `grid_stack`/`list_stack` já usam `"100%c"` na altura — exatamente o mesmo esqueleto do `general_tab_section` vanilla que hospeda um label de altura variável.
- `hide_hyphen: true` pode continuar como está (decisão de estilo, não é a causa do bug).

Se quiser manter *algum* teto de segurança (para nunca deixar um texto absurdamente longo estourar a tela), use um valor bem alto em vez de remover — o próprio vanilla faz isso em tooltips: `"max_size": [ 15, 200 ]` (`ui_common.json:7244`, com o comentário `// 200 was used in thoughts that whatever text was used would not need more than 200px`). Ou seja, troque `30` por algo como `200` em vez de remover o segundo valor, se preferir manter um limite defensivo.

confidence: **confirmado** para o diagnóstico (mecanismo de truncamento) e para o padrão de correção (label sem teto de altura dentro de stack_panel `100%c`); **provável** para a recomendação específica do valor `200` como teto defensivo (é um número específico de outro contexto, não uma regra universal).
