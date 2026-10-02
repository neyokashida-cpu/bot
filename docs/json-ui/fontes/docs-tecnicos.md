# JSON UI — Extração de Docs Técnicos (Tarefa B)

Complementa `docs-wiki.md` (Tarefa A). Foco: **modificar `server_form`** e **geração dinâmica de conteúdo**, mais buttons/toggles, preserve-title-texts, type-conversion, e o bloco de operadores do intro.md que a Tarefa A deixou pendente para cá.

Fontes lidas (conteúdo idêntico por byte-a-byte, confirmado via `diff`):
- **modifying-server-forms.md** = msf.md = server_forms.md
- **dynamic-content-generation.md** = dcg.md
- **buttons-and-toggles.md** = bt.md
- **preserve-title-texts.md** = ptt.md
- **type-conversion.md** = tc.md
- **best-practices.md** = bp.md = wikibp.md = jsonui_best.md (já coberto em docs-wiki.md, não repetido aqui)
- **intro.md** = json-ui-intro.md = jsonui_intro.md (só a seção "Using Operators" foi extraída aqui; o resto é conteúdo introdutório básico já coberto conceitualmente em docs-wiki.md)
- **doc.md** / json-ui-documentation.md / wiki_doc.md / wikidoc.md / juidoc.md — já cobertos integralmente em docs-wiki.md, não relidos.

**string-to-number.md e s2n.md: arquivo com conteúdo `404: Not Found` — não é documentação real, é uma página que não existe/não foi coletada corretamente.** Nenhuma afirmação extraída dele. O conteúdo equivalente ("String to Number") existe de fato dentro de **type-conversion.md**, coberto na seção 5 abaixo.

Todas as citações usam o nome canônico do arquivo lido.

---

## 1. Modificando Server Forms — confirmado (modifying-server-forms.md)

Tutorial trabalha em cima de `ui/server_form.json`. Pré-requisito assumido pela doc: conhecimento básico de JSON-UI.

### 1.1 Action Form (long_form)

Passo 1 — inserir um novo elemento em `main_screen_content` via `modifications`/`insert_back` no array `controls`, contendo um `panel` com `factory`:

```json
{
  "main_screen_content": {
    "modifications": [
      {
        "array_name": "controls",
        "operation": "insert_back",
        "value": [
          {
            "wiki_server_form_factory": {
              "type": "panel",
              "factory": {
                "name": "server_form_factory",
                "control_ids": {
                  "long_form": "@server_form.our_long_form_panel"
                }
              }
            }
          }
        ]
      }
    ]
  }
}
```

Pontos confirmados pela doc:
- O nome do painel injetado (`wiki_server_form_factory`) **pode ser qualquer coisa, mas não pode ser igual a `"server_form_factory"`** (nome reservado do factory nativo) nem igual ao nome de um elemento-irmão.
- `factory.name` **deve ser exatamente `"server_form_factory"`** — é esse nome que amarra os dados enviados pelo jogo (via `ActionFormData`/`ModalFormData`) ao `long_form`/`custom_form`.
- É possível repetir esse bloco várias vezes (`wiki_server_form_factory_2`, etc.), mas a doc recomenda **fazer isso uma única vez** e usar um painel único (`our_long_form_panel`) que referencia internamente todos os formulários customizados — reduz repetição.
- `"long_form": "@server_form.our_long_form_panel"` é a referência (namespace `server_form`) ao painel-container que você define.

Passo 2 — definir `our_long_form_panel`, que recebe o binding de `#title_text` uma única vez no pai (para não repetir em cada filho), e dentro dele os elementos customizados condicionam sua visibilidade a um teste de substring no título:

```json
{
  "our_long_form_panel": {
    "type": "panel",
    "bindings": [
      { "binding_name": "#title_text" }
    ],
    "controls": [
      {
        "our_custom_made_long_form": {
          "type": "image",
          "texture": "textures/items/apple",
          "size": [32, 32],
          "$title_needs_to_contain": "wiki_form:",
          "bindings": [
            {
              "binding_type": "view",
              "source_control_name": "our_long_form_panel",
              "source_property_name": "(not ((#title_text - $title_needs_to_contain) = #title_text))",
              "target_property_name": "#visible"
            }
          ]
        }
      }
    ]
  }
}
```

**Mecanismo do marcador de título (relevante ao nosso truque de detectar custom vs vanilla):** `(#title_text - $title_needs_to_contain) = #title_text` é `true` quando a substring **não** existe no título (subtração de string que não está presente não muda a string); `not(...)` inverte para `true` quando a substring **existe**. Confirmado, modifying-server-forms.md.

### 1.2 Problema do overlap e a correção (crítico)

A doc afirma explicitamente: **"you might notice it overlaps with the normal action form"** — ou seja, **por padrão, ao injetar seu painel customizado, ele fica sobreposto ao `long_form` vanilla, ambos visíveis ao mesmo tempo.** Confirmado, modifying-server-forms.md.

**Correção obrigatória**: adicionar bindings ao elemento `long_form` (o vanilla) via `modifications`/`insert_back` no array `bindings`, para que ele **se esconda** quando o marcador estiver presente no título:

```json
{
  "long_form": {
    "modifications": [
      {
        "array_name": "bindings",
        "operation": "insert_back",
        "value": [
          { "binding_name": "#title_text" },
          {
            "binding_type": "view",
            "source_property_name": "((#title_text - 'wiki_form:') = #title_text)",
            "target_property_name": "#visible"
          }
        ]
      }
    ]
  }
}
```

Aqui a lógica é invertida em relação ao painel customizado: `(#title_text - 'wiki_form:') = #title_text` é `true` (form vanilla visível) **quando o marcador NÃO está presente**; quando o marcador está presente, essa expressão vira `false` e o `long_form` vanilla se esconde, deixando só o customizado visível.

**Múltiplos marcadores**: a doc mostra que dá para encadear vários testes de substring com `-`: `(#title_text - 'form_1' - 'form_2' - 'form_3')` — cada `-` remove aquela substring específica se presente; a comparação final `= #title_text` só é `true` se **nenhuma** delas foi removida (ou seja, nenhuma estava presente). Confirmado, modifying-server-forms.md.

**Implicação para "UI some silenciosamente"**: se o binding que esconde o `long_form` vanilla (`target_property_name: "#visible"`) estiver com a lógica invertida, ou se o marcador usado no factory customizado não bater exatamente (case-sensitive, string diferente por typo) com o marcador testado no `long_form` vanilla, o resultado não é um crash nem um erro — é **os dois formulários ficarem `#visible=false` ao mesmo tempo** (nenhum aparece) OU **ambos `#visible=true`** (sobrepostos, parecendo bugado). A doc não usa a palavra "falha silenciosa", mas descreve exatamente esse mecanismo de visibilidade condicional por substring como a única coisa que decide se o form aparece — não há fallback nem erro reportado nesse fluxo. Confiança: **provável** (é inferência direta da mecânica descrita, não uma frase literal da doc sobre "falha silenciosa").

### 1.3 Modal Forms (custom_form)

**Confirmado, modifying-server-forms.md**: "Editing the modal forms is the same as editing long form but we need to modify multiple things. **Modal Forms are called Custom Forms inside `server_form.json`**."

Diferenças em relação ao Action Form:
- O `factory.control_ids` do painel injetado precisa ter **duas chaves**, não uma: `"long_form"` e `"custom_form"`, ambas apontando para os respectivos paineis customizados:

```json
"factory": {
  "name": "server_form_factory",
  "control_ids": {
    "long_form": "@server_form.our_long_form_panel",
    "custom_form": "@server_form.our_custom_form_panel"
  }
}
```

- O elemento vanilla a receber o binding de ocultação (equivalente ao `long_form` da seção 1.2) é `custom_form`, não `long_form`.
- Fora essas trocas de nome, a estrutura de `our_custom_form_panel` e o mecanismo de marcador de título (`$title_needs_to_contain`, `source_property_name` com subtração de string) são **idênticos** ao caso do Action Form.
- O bloco final de `main_screen_content` (`modifications`/`insert_back`) precisa referenciar **ambos** `long_form` e `custom_form` no mesmo `control_ids` — não são dois blocos separados de `main_screen_content`, é um único painel-factory servindo os dois tipos de form.

**Nota**: a doc não cobre `MessageFormData` (form de mensagem/confirmação) neste tutorial — só Action Form (`long_form`) e Modal Form (`custom_form`). Ausência confirmada por leitura completa do arquivo; confiança da ausência: **suspeita** (não é garantido que a Mojang não trate `MessageFormData` como um terceiro `control_ids`, só que este tutorial específico não menciona).

---

## 2. Geração Dinâmica de Conteúdo — confirmado (dynamic-content-generation.md)

Pré-requisitos assumidos pela doc: bindings, collections, e saber adicionar elementos a um entry point de tela.

Aviso da doc: ao longo do tutorial, **"control"** e **"element"** são usados como sinônimos.

### 2.1 Factories

Uma factory gera elementos especificados em `control_name` ou `control_ids`.

- **Invocação**: muitas factories vanilla são invocadas nativamente pelo engine. Alternativamente, podem ser invocadas manualmente sobrescrevendo `#collection_length`.
- **Data Binding**: para usar `#collection_length`, a factory precisa estar dentro de um container que suporte collection (ex.: `collection_panel`, `stack_panel`). O valor pode ser `int` ou `string[]`, dependendo da implementação da factory.

**Propriedades-chave (tabela da doc):**

| Propriedade | Tipo | Descrição |
|---|---|---|
| `name` | string | Identificador único da factory. Crítico para factories nativas; para factories custom pode ser qualquer string arbitrária. |
| `control_name` | string | Referência ao controle a ser gerado pela factory. |
| `control_ids` | Object | Mapeia chaves string arbitrárias para referências de controles a gerar. Usado ao gerar múltiplos controles distintos. **Deve permanecer inalterado para factories invocadas nativamente pelo engine.** |
| `factory_variables` | string[] | Lista de variáveis a passar para os controles gerados pela factory. |
| `max_children_size` | int | Número máximo de controles a gerar. |

#### Usando `control_name`

`#collection_length` deve ser sobrescrito com um valor `int` — é o número de elementos gerados. Exemplo da doc: título `Count:3` é lido via bindings (`#hud_title_text_string` → `#count`), depois `(#count - 'Count:' + 0)` extrai o valor inteiro (o `+ 0` garante default `0` se a string vier vazia), e o resultado sobrescreve `#collection_length`.

#### Usando `control_ids`

`#collection_length` deve ser sobrescrito com um **array de strings** (as chaves definidas em `control_ids`). A doc afirma: **"There's not much freedom with this approach as there is no way to manipulate arrays in JSON UI."** — a solução é pré-definir arrays possíveis dentro de `property_bag` (ex.: `#list1`, `#list2`) e escolher entre eles via binding que constrói o nome da chave dinamicamente: `('#list' + #choice)`. Os elementos são gerados **na ordem especificada no array escolhido**.

#### Factory via `"type": "factory"` (relevante ao server_form)

A doc mostra exatamente o trecho vanilla de `server_form.json`:

```json
{
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
  }
}
```

Confirmado: **"Name of control here acts as the factory name and thus should remain unchanged"** — ou seja, o nome do controle `server_form_factory` em si (não só a propriedade `factory.name`) é o identificador usado pelo engine; renomeá-lo quebra a invocação nativa. A doc afirma que estas factories com `"type": "factory"` são **"always invoked natively by the engine"**, mas que é possível "modificar as referências de controle para gerar elementos customizados em vez disso" — o que é exatamente a técnica usada em modifying-server-forms.md (seção 1) para trocar `long_form`/`custom_form` pelos painéis próprios.

### 2.2 Grids

Grids geram e organizam elementos em layout de grade. Elementos são gerados a partir de um template especificado em `grid_item_template`. É possível gerar um número fixo via `grid_dimensions` ou variável sobrescrevendo `#maximum_grid_items` (binding) ou `maximum_grid_items` (propriedade).

**Propriedades-chave (tabela da doc):**

| Propriedade | Tipo | Descrição |
|---|---|---|
| `grid_dimensions` | Vector [columns, rows] | Número de colunas e linhas. Gera no máximo `columns × rows` elementos. |
| `grid_dimension_binding` | string | Nome de binding que fornece as dimensões do grid. **Só aceita bindings hardcoded.** |
| `grid_item_template` | string | Referência ao controle a ser gerado pelo grid. |
| `grid_rescaling_type` | enum | `none`, `horizontal`, `vertical`. |
| `maximum_grid_items` | int | Máximo de controles a gerar. Binding correspondente: `#maximum_grid_items`. |
| `grid_position` | Vector [row, column] | Posição de um controle dentro do grid. |

**:::danger confirmado:** "Try not to use `vertical` as the value of `grid_rescaling_type`. It may crash your game." — é um aviso de **crash documentado** (não falha silenciosa) para `grid_rescaling_type: "vertical"`.

**Tamanho default do grid**: `["100%c", "100%c"]`. A doc recomenda manter a altura dinâmica (`100%c`): **"If a fixed height is applied, generated elements may overlap if the height is too small, or have unintended gaps if the height is too large."** — overlap/gaps por altura fixa mal dimensionada, não um erro reportado.

#### Usando `grid_dimensions`

Recomendação da doc: **não sobrescrever `size`** neste caso, pois "some elements can go outside the grid bounds and mess up the layout" — elementos podem sair dos limites do grid e bagunçar o layout, silenciosamente (sem erro, só visual quebrado).

#### Sobrescrevendo `#maximum_grid_items`

Para funcionar corretamente:
1. É preciso modificar a **largura** do grid — o número de colunas neste modo é `floor(largura_do_grid / largura_do_template)`.
2. É preciso setar `grid_rescaling_type: "horizontal"`.
3. Sobrescrever `#maximum_grid_items` via binding (ou definir a propriedade `maximum_grid_items` diretamente).

Exemplo da doc: grid com `size: [160, "100%c"]` e template de 32px de largura → `floor(160/32) = 5` colunas. Binding extrai `Count:{valor}` do título da mesma forma que em factories (`#count - 'Count:' + 0`) e sobrescreve `#maximum_grid_items`.

#### Grid Position

Permite posicionar manualmente controles no grid em vez de gerá-los via template, usando `grid_position: [row, column]` em cada filho declarado explicitamente em `controls`, referenciando o template via herança (`apple_1@hud.hud_apple`). A doc recomenda **definir `size` explicitamente** neste caso ("to avoid layout issues").

### 2.3 "Useful Information" — informações soltas relevantes ao nosso problema (confirmado, dynamic-content-generation.md)

- "When used with a collection, Factories and Grids automatically index generated elements."
- "Generated elements can access outside bindings via `source_control_name`, **but outside elements cannot access bindings from generated elements**." — limitação de escopo unidirecional: um elemento gerado dentro do grid/factory pode ler bindings de fora via `source_control_name`, mas o inverso não funciona.
- **"Invisible elements inside a Grid still occupy physical space, which can leave unintentional gaps in your UI."** — relevante ao sintoma "UI some silenciosamente": um tile do grid que ficou `#visible=false` por lógica de binding não desaparece do layout, ele deixa um buraco vazio no lugar — pode ser confundido com "sumiço" quando na verdade é só um elemento invisível ocupando espaço.
- "In Grids, animations linked with the `next` property can appear bugged. After the first animation, the duration divides among the grid elements, causing subsequent animations to speed up. (`flip_book` animations are the only exception)." — bug de timing de animação encadeada dentro de grids, não um sumiço de UI, mas pode gerar comportamento visual inesperado (animação acelerando) que parece "quebrado" sem erro no log.

---

## 3. Buttons and Toggles — confirmado (buttons-and-toggles.md)

### 3.1 Toggles

Exemplo usa herança do template vanilla `ui/ui_template_toggles.json` (`common_toggles.light_text_toggle`):

```json
"our_toggle@common_toggles.light_text_toggle": {
  "size": [64, 32],
  "$button_text": "Click me!",
  "$toggle_name": "wiki_toggle",
  "$toggle_view_binding_name": "wiki_toggle_state"
}
```

- `$toggle_name`: **"Required, but it has no effect unless a hardcoded toggle name is used."**
- `$toggle_view_binding_name`: "The toggle name that allows us to retrieve data" — é o nome usado por outros elementos para ler o estado do toggle via `source_control_name`.

Para controlar visibilidade de outro elemento a partir do estado do toggle, usa-se binding `view` com `source_control_name` apontando para o `$toggle_view_binding_name`, `source_property_name: "#toggle_state"` (retorna boolean), `target_property_name: "#visible"`.

### 3.2 Buttons

**Confirmado**: "Generally, buttons have limited functionality, as they are primarily used in hardcoded instances, such as navigating to a screen or opening a dialog."

Exemplo usa `ui/ui_template_buttons.json` (`common_buttons.light_text_button`):

```json
"our_button@common_buttons.light_text_button": {
  "size": [64, 32],
  "$button_text": "Click me!",
  "$pressed_button_name": "button.menu_exit"
}
```

`$pressed_button_name` — **obrigatório**; aceita nomes de botão globais ou hardcoded. No exemplo, `button.menu_exit` fecha a tela atual ao clicar.

### 3.3 Hover Text (Content Buttons)

Para botões que mostram texto ao passar o mouse, é necessário usar **Content Buttons** (`common_buttons.light_content_button`), referenciando `ui/ui_template_buttons.json` e `ui/ui_common.json`:

```json
"our_button@common_buttons.light_content_button": {
  "size": [18, 18],
  "$button_content": "namespace.our_button_content_panel",
  "$pressed_button_name": "button.menu_exit"
}
```

Dentro do painel de conteúdo, o elemento de hover usa herança de `common.hover_text`:

```json
"our_hover_text@common.hover_text": {
  "ignored": "$default_state",
  "property_bag": { "#hover_text": "" }
}
```

- `"ignored": "$default_state"` — **obrigatório**: torna o elemento não-visível quando o botão está em estado default (não hovered).
- **Nota da doc**: o hover text via `#hover_text` em `property_bag` **"doesn't support localizing so if that's what you are looking to do, create a custom hover text."**

### 3.4 Play Animation ao clicar

Para tocar uma animação ao clicar num botão, usa-se o mesmo valor de `$pressed_button_name` como `play_event` da animação:

```json
"example_animation": {
  "anim_type": "offset",
  "easing": "linear",
  "duration": 2,
  "from": [0, 0],
  "to": [-50, 0],
  "play_event": "button.example_button_id"
}
```

O botão usa `"$pressed_button_name": "button.example_button_id"`, e o elemento a ser animado referencia a animação via `"anims": ["@namespace.example_animation"]`.

---

## 4. Preserve Title Texts — confirmado (preserve-title-texts.md)

**Relevância direta ao nosso marcador de título invisível**: este tutorial ensina a técnica canônica de "escutar" um título/subtítulo/scoreboard só quando ele contém uma palavra-chave específica, e então **guardar** esse valor localmente — é a mesma família de técnica usada no marcador de `#title_text` do server_form (seção 1), mas resolvendo um problema adicional: **persistência do valor** entre atualizações de título que não contêm a palavra-chave.

### 4.1 Problema descrito pela doc

"Passing data to the UI via titles, subtitles, or scoreboards is a very common technique. However, you often need a UI element to only react to specific information, not every single title command that is run." **Métodos antigos "often had bugs or used `global` variables, which is not ideal for reusable components."** A solução usa `property_bag` para dar a cada instância do componente sua própria "memória local", tornando-o **verdadeiramente modular** (sem colisão entre múltiplas instâncias na mesma tela).

### 4.2 Código (label + painel-filho invisível como "cérebro")

```json
"preserved_title_display": {
    "$update_string": "update",
    "type": "label",
    "text": "#text",
    "controls": [
        {
            "data_control": {
                "type": "panel",
                "size": [0, 0],
                "property_bag": { "#preserved_text": "" },
                "bindings": [
                    { "binding_name": "#hud_title_text_string" },
                    {
                        "binding_name": "#hud_title_text_string",
                        "binding_name_override": "#preserved_text",
                        "binding_condition": "visibility_changed"
                    },
                    {
                        "binding_type": "view",
                        "source_property_name": "(not (#hud_title_text_string = #preserved_text) and not ((#hud_title_text_string - $update_string) = #hud_title_text_string))",
                        "target_property_name": "#visible"
                    }
                ]
            }
        }
    ],
    "bindings": [
        {
            "binding_type": "view",
            "source_control_name": "data_control",
            "source_property_name": "(#preserved_text - $update_string)",
            "target_property_name": "#text"
        }
    ]
}
```

### 4.3 Mecanismo, passo a passo (confirmado pela doc)

1. **`property_bag: {"#preserved_text": ""}`**: cria uma variável local. Como não é `global`, **cada instância** de `preserved_title_display` tem seu próprio `#preserved_text` privado — "so they don't interfere with each other. This fixes the major flaw in older methods."
2. **Binding com `binding_condition: "visibility_changed"`**: é o gatilho de gravação. Quando a visibilidade do `data_control` muda, ele copia instantaneamente o título atual (`#hud_title_text_string`) para `#preserved_text`.
3. **Condição de visibilidade** (o `data_control` "pisca" visível por um único frame só quando ambas são verdadeiras):
   - `not (#hud_title_text_string = #preserved_text)` — o título recebido é **diferente** do já salvo (evita re-disparar no mesmo título repetido).
   - `not ((#hud_title_text_string - $update_string) = #hud_title_text_string)` — o título **contém** a palavra-chave (`$update_string`).
4. Sequência: título novo com keyword chega → painel fica visível → `visibility_changed` dispara e salva o texto → a condição de visibilidade imediatamente volta a `false` → painel esconde de novo.
5. O `label` pai só lê o dado do filho: `source_control_name: "data_control"`, `source_property_name: "(#preserved_text - $update_string)"` (remove a keyword antes de exibir).

**Aplicação ao nosso caso**: este é o padrão de referência da wiki para "detectar substring em `#title_text`/`#hud_title_text_string` e reagir só quando presente, sem interferir entre instâncias" — a mesma primitiva de subtração de string (`(#texto - $substring) = #texto` → `true` se ausente) usada em modifying-server-forms.md para alternar custom/vanilla. Confiança: **confirmado** que é a mesma primitiva de linguagem (subtração de string), **provável** que seja aplicável 1:1 ao caso de servidor form sem adaptação (a doc não menciona `server_form.json` neste arquivo).

---

## 5. String ↔ Number / Type Conversion — confirmado (type-conversion.md)

Arquivo real equivalente a "string-to-number": **type-conversion.md** (o arquivo nomeado `string-to-number.md`/`s2n.md` está quebrado — conteúdo `404: Not Found`, sem informação extraível).

### 5.1 String → Number

```json
"label": {
    "type": "label",
    "text": "#text",
    "property_bag": { "#str": "10", "#float": 1.0 },
    "bindings": [
        { "binding_type": "view", "source_property_name": "(#str * 1)", "target_property_name": "#integer" },
        { "binding_type": "view", "source_property_name": "(#str * #float)", "target_property_name": "#float" },
        { "binding_type": "view", "source_property_name": "('Result: ' + #integer)", "target_property_name": "#text" }
    ]
}
```

**Processo confirmado**: "By doing arithmetic operation on strings (except addition), you convert a string into a number." — ou seja, `*`, `/`, `-` numa string a convertem para número; `+` não (vira concatenação).

**Notas da doc:**
- Strings alfanuméricas (ex.: `a123`) **não** retornam `123` (a conversão falha silenciosamente para valores não puramente numéricos — a doc não descreve o que acontece, só que "will not return 123").
- Somar string e float (`'abc' + 1.2`) **"will not produce anything"**.
- Não é possível exibir floats diretamente — requer a técnica da seção "Float to String".

### 5.2 Number → String

Concatenar com `+` uma string e um número sempre resulta string: `('Result: ' + #num)`. **Nota**: não é possível combinar string e **float** dessa forma — "it will produce nothing" (mesma limitação citada acima).

### 5.3 Float → String

**Não existe "float to number"** porque, segundo a doc, "floats are a sub-child of numbers, so floats are already numbers by itself."

Técnica: já que não dá para somar string+float diretamente, o valor inteiro do float é reconstruído somando comparações booleanas (`(0 + (#float > 0) + (#float > 1) + ... + (#float > 9))`), cada uma virando `1` ou `0` (ver seção 5.4), então concatenado como string.

**Limitações confirmadas pela doc**:
- Essa técnica só suporta floats **entre 1 e 10**.
- O resultado **não inclui a parte decimal** — para `6.7` o output é `6`, não `6.7`.
- "There is a way to include the decimal but, it requires a more complex expression" (não detalhado neste arquivo).
- "This is great if you know the range of your number reference, otherwise, you will need to guess."

### 5.4 Boolean → Number

```json
"source_property_name": "(#bool + #hahasixseven)"
```

**Confirmado**: "Any arithmetic operations done between booleans and numbers will always result a number. Internally, `true` is recognized as 1, and `false` is 0." O "boolean" usado na operação pode ser uma expressão, desde que resulte em booleano.

---

## 6. Operadores (intro.md) — a tabela completa (referenciada por docs-wiki.md, extraída aqui)

Confirmado, intro.md (seção "Using Operators"): operadores usáveis em `$variables` e `#bindings`, dentro de propriedades comuns como `size` e `offset`.

| Nome | Operador | Exemplos |
|---|---|---|
| Addition | `+` | `"100% + 420px"`, `($text + ' my')`, `($index + 2)`, `('#' + $bdg_nm + '_name')` |
| Subtraction | `-` | `"100% - 69px"`, `($text - ' my')`, `($index - 13)` |
| Multiplication | `*` | `($var * 9)`, `(#value * 5)` |
| Division | `/` | `($var / 12)`, `(#value / 2)` |
| Equal to | `=` | `($var = 12)`, `($var = 'this_text')`, `(#name = 'Wither')` |
| Greater than | `>` | `(#value > 13)` |
| Less than | `<` | `($var < 4)` |
| Greater or equal than | `>` ou `=` combinados | `(#value > 2 or #value = 2)` |
| Less or equal than | `<` ou `=` combinados | `(#value < 2 or #value = 2)` |
| Logical AND | `and` | `($is_school and $is_open)` |
| Logical OR | `or` | `($is_cool or $is_awesome)` |
| Logical NOT | `not` | `(not #name)`, `(not (#name = 'text'))`, `(not $name)` |

Nota: **não existem operadores nativos de `>=`/`<=`** — a doc mostra que "maior ou igual"/"menor ou igual" são compostos via `or` entre `>`/`<` e `=` (não é um único token).

Subtração de string (`-`) é a base de toda a técnica de detecção de marcador de título usada em modifying-server-forms.md (seção 1.1) e preserve-title-texts.md (seção 4): remove a substring do lado direito se presente na string do lado esquerdo; se a substring não existir, a string permanece inalterada — por isso `(#texto - 'marcador') = #texto` é o teste padrão de "marcador ausente".

---

## 7. Síntese — "falha silenciosa" nos dois documentos centrais

Nem **modifying-server-forms.md** nem **dynamic-content-generation.md** usam a expressão "falha silenciosa" ou equivalente direto. Nenhum dos dois documenta um caso de "a UI desaparece sem nenhum log". O que os dois documentam, e que é relevante ao sintoma relatado:

1. **modifying-server-forms.md**: o mecanismo inteiro de mostrar/esconder custom vs. vanilla depende de **dois bindings de visibilidade espelhados e opostos** (um no painel customizado testando presença do marcador, outro no `long_form`/`custom_form` vanilla testando ausência do marcador). Não há nenhum mecanismo de fallback nem validação cruzada entre os dois — se um dos dois bindings estiver com o marcador errado (typo, string diferente, esquecido), o resultado é **silencioso**: ou os dois ficam invisíveis (menu "some") ou os dois ficam visíveis (sobreposição). A doc só descreve o "acontece overlap" (ambos visíveis) como sintoma a corrigir — não descreve o caso inverso (ambos invisíveis), mas a mecânica de binding é simétrica o bastante para produzi-lo caso a string do marcador não bata exatamente dos dois lados. Confiança: **provável** para o cenário "ambos invisíveis", já que é inferido da mecânica e não afirmado literalmente pela doc.
2. **dynamic-content-generation.md**: documenta dois casos de "sumiço não é sumiço real" — (a) elemento invisível dentro de um Grid continua ocupando espaço físico (pode parecer um item "faltando" no meio do grid, mas é só um espaço vazio), e (b) elementos que saem dos limites do grid quando `size` é sobrescrito com `grid_dimensions` — "pode bagunçar o layout" sem gerar erro. Também documenta um crash real e citado (`grid_rescaling_type: "vertical"`), que não é falha silenciosa — é crash.

**Conclusão de confiança**: a wiki não afirma diretamente "server_form falha silenciosamente sem log". O que ela documenta é que o mecanismo de visibilidade condicional do server_form (marcador de título) **não tem nenhuma rede de segurança** — qualquer descasamento entre o binding de show e o de hide produz um resultado visual errado sem nenhum erro reportado no ContentLog. Isso é consistente com — mas não prova causalmente — o sintoma relatado pelo usuário. Confiança: **suspeita** quanto à causa exata do bug relatado; **confirmado** quanto ao mecanismo de binding em si.

---

## 8. Referência cruzada de arquivos usados nesta tarefa (para auditoria)

| Nome canônico | Duplicatas confirmadas (diff byte-a-byte) |
|---|---|
| modifying-server-forms.md | msf.md, server_forms.md |
| dynamic-content-generation.md | dcg.md |
| buttons-and-toggles.md | bt.md |
| preserve-title-texts.md | ptt.md |
| type-conversion.md | tc.md |
| best-practices.md (não relido, ver docs-wiki.md) | bp.md, wikibp.md, jsonui_best.md |
| intro.md (só seção Operators extraída aqui) | json-ui-intro.md, jsonui_intro.md |
| doc.md (não relido, ver docs-wiki.md) | json-ui-documentation.md, wiki_doc.md, wikidoc.md, juidoc.md |
| string-to-number.md — **arquivo vazio/quebrado (`404: Not Found`)** | s2n.md (mesmo conteúdo quebrado) |
