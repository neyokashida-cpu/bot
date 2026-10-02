# Documentação oficial (Microsoft Learn) — JSON UI, bindings, resource pack priority

Pesquisa feita em 2026-08-31, via WebSearch/WebFetch, restrita a `learn.microsoft.com/minecraft` (site oficial
da Microsoft/Mojang para creators; não existe "criador.mojang.com" ativo — o domínio oficial atual é
`learn.microsoft.com/en-us/minecraft/creator`). Nenhum arquivo de `ADDONS/SonheMenu_RP` ou `ADDONS/SonheMenu_BP`
foi tocado.

---

## 1. Bindings — sintaxe oficial atual

Fonte: [JSON UI Documentation - minecraft:ui_element](https://learn.microsoft.com/en-us/minecraft/creator/reference/content/jsonuireference/examples/jsonuicomponents/ui_element?view=minecraft-bedrock-stable)

**confidence: confirmado** (tabela de propriedades da doc oficial, atualizada em 2026-03-05)

`bindings` é um array dentro de `minecraft:ui_element`. Cada item aceita:

| Propriedade | Tipo | Descrição (oficial) |
|---|---|---|
| `binding_name` | String | "The name of the data source to bind to (e.g., '#player_name')." |
| `binding_name_override` | String | "The property on the UI element to bind the value to." |
| `binding_type` | enum | "The type of binding." |
| `binding_condition` | enum | "When the binding should be evaluated." |
| `binding_collection_name` | String | "The name of the collection when using collection bindings." |
| `source_control_name` | String | "The name of the source control for view bindings." |
| `source_property_name` | String | "The property name on the source control." |
| `target_property_name` | String | "The property name on the target element." |

**Gap identificado na doc oficial (confirmado):** a página lista os enums `binding_type`, `binding_condition`,
`anchor_from`, `anchor_to`, `type`, `grid_rescaling_type` etc., mas em **todos** eles a coluna "Value/Title/
Description" retorna literalmente `undefined` para cada linha — ou seja, a doc oficial hoje **não enumera os
valores possíveis** (ex.: não diz explicitamente que `binding_type` aceita `view`/`collection`, nem que
`binding_condition` aceita `visible`/`visible_bind` etc.). O rodapé da página marca `ai-usage: ai-assisted`,
sugerindo geração semi-automática incompleta. Isso é uma lacuna real da doc oficial, não uma opinião nossa.

**Não encontrado na doc oficial:** `resolve_sibling_scope` (usado amplamente em exemplos de UI custom para
resolver bindings em controles-irmão) **não aparece** na tabela de propriedades de `bindings` desta página.
Se o addon depende dele, está usando um comportamento que a página de referência atual da Microsoft não
documenta — comportamento pode ser real (compilado no engine) mas não está coberto pela doc.

## 2. `visible`, `layer`, `alpha` — propriedades oficiais de `minecraft:ui_element`

Mesma fonte acima. **confidence: confirmado**

| Propriedade | Tipo | Descrição literal |
|---|---|---|
| `visible` | Boolean | "Whether this element is visible by default." |
| `layer` | Integer | "The rendering layer for this element. Higher values render on top of lower values." |
| `alpha` | Decimal (0.0–1.0) | "The opacity of the element, from 0.0 (transparent) to 1.0 (opaque)." |
| `propagate_alpha` | Boolean | "Whether alpha transparency is propagated to child elements." |

Não há, nesta página, nenhuma nota sobre `visible` versus binding de `#visible`/`visible_bind` além do que já
está na tabela — a doc oficial trata isso como propriedade estática; o binding dinâmico de visibilidade é
inferido pelo uso de `binding_name` + `binding_condition`, mas de novo sem exemplos de valores concretos (ver
gap acima).

## 3. `grid` — não existe página de referência dedicada

**confidence: confirmado (busca negativa)**

A lista oficial completa de páginas em "JSON UI Documentation"
([jsonuilist](https://learn.microsoft.com/en-us/minecraft/creator/reference/content/jsonuireference/examples/jsonuilist?view=minecraft-bedrock-stable))
contém **apenas 4 páginas**:

- [ui_defs](https://learn.microsoft.com/en-us/minecraft/creator/reference/content/jsonuireference/examples/jsonuicomponents/ui_defs?view=minecraft-bedrock-stable)
- [ui_element](https://learn.microsoft.com/en-us/minecraft/creator/reference/content/jsonuireference/examples/jsonuicomponents/ui_element?view=minecraft-bedrock-stable)
- [ui_global_variables](https://learn.microsoft.com/en-us/minecraft/creator/reference/content/jsonuireference/examples/jsonuicomponents/ui_global_variables?view=minecraft-bedrock-stable)
- [ui_screen](https://learn.microsoft.com/en-us/minecraft/creator/reference/content/jsonuireference/examples/jsonuicomponents/ui_screen?view=minecraft-bedrock-stable)

Não há páginas oficiais separadas para `grid`, `collection`, `panel`, `image`, `button`, `label`, `stack_panel`
etc. `grid` é só um dos valores possíveis do campo `type` dentro de `ui_element` — mas, como notado acima, essa
enumeração de `type` aparece com valores `undefined` na tabela, então a Microsoft não documenta oficialmente,
em texto, o que `grid` faz, nem `grid_dimension_binding`, `grid_item_template`, `grid_rescaling_type` além dos
nomes e tipos genéricos ("The template element to use for grid items.", etc. — sem exemplos).

## 4. `ui_defs.json` e `ui_screen.json` — estrutura oficial, sem regra de merge documentada

Fontes: [ui_defs](https://learn.microsoft.com/en-us/minecraft/creator/reference/content/jsonuireference/examples/jsonuicomponents/ui_defs?view=minecraft-bedrock-stable),
[ui_screen](https://learn.microsoft.com/en-us/minecraft/creator/reference/content/jsonuireference/examples/jsonuicomponents/ui_screen?view=minecraft-bedrock-stable)

**confidence: confirmado** (estrutura) / **suspeita** (comportamento de merge entre packs, não documentado)

- `_ui_defs.json`: "The \_ui_defs.json file that lists all UI screen files that should be loaded by Minecraft.
  This file is required for custom UI screens to be recognized." — só um array `ui_defs: [string]` de paths.
- `ui_screen`: "UI screen files use a namespace-based structure where each JSON key (except 'namespace') defines
  a UI element. Elements can inherit from other elements using the '@' syntax (e.g.,
  'my_button@common.button'). Variables are defined with '\$' prefix and can be overridden."

**Nenhuma das duas páginas explica** o que acontece quando dois resource packs (ex.: o pack vanilla interno +
o `SonheMenu_RP`) declaram o **mesmo namespace** (`server_form`) ou o mesmo nome de controle dentro dele — se é
substituição total do namespace, merge campo-a-campo, ou "último a carregar vence" controle por controle. Essa
regra de merge não está documentada nestas páginas oficiais.

## 5. Prioridade/ordem de resource packs — "Pack Stacking" (mecanismo confirmado)

Fonte: [Create Custom Grass Blocks: An Introduction to Resource Packs](https://learn.microsoft.com/en-us/minecraft/creator/documents/resourcepack?view=minecraft-bedrock-stable)

**confidence: confirmado**

> "**Pack Stacking** is how content is loaded on top of Vanilla content, causing each object that has the same
> name in both packs to be overwritten by the *latest* applied pack."

> "If another pack that uses the dirt.png file is loaded **after** My_RESOURCE_Pack, then Minecraft will use
> that file instead."

> "Move your pack above others to ensure your **dirt.png** texture is loaded before other resource packs."

Ou seja: quando dois packs mexem no **mesmo arquivo/registro**, o que vence é o **carregado por último** na
ordem de pilha (o pack mais "acima"/"abaixo" na lista "Selected" do jogo, que o jogador reordena manualmente
por drag-and-drop). Essa doc fala de texturas como exemplo, mas o mecanismo de Pack Stacking é genérico ("each
object that has the same name") e é o mesmo mecanismo citado na doc de Cooperative Add-Ons abaixo, aplicado lá
explicitamente a entidades e (por extensão declarada) a UI.

## 6. Achado mais relevante: Microsoft desaconselha oficialmente overrides de JSON UI em cenários multi-pack

Fonte: [Guidelines for Building Cooperative Add-Ons](https://learn.microsoft.com/en-us/minecraft/creator/documents/practices/guidelinesforbuildingcooperativeaddons?view=minecraft-bedrock-stable)

**confidence: confirmado — é a nota oficial mais direta encontrada sobre o comportamento relatado**

Trecho literal, seção "Namespacing and Identifiers" → "JSON UI and Custom Fonts overrides are disalllowed"
(sic, erro de digitação no original da Microsoft):

> "Because JSON UI (i.e., files in `<resource pack name>/ui`) and fonts (i.e., files in `<resource pack
> name>/font`) are **not overridable in a cooperative manner** - such that multiple Add-Ons can customize the
> same asset - cooperative Add-Ons **should not override any JSON UI or font glyph files**."

E na seção "Types of Customizations to Avoid":

> "Do not override UI files (resource packs/ui)"

E no início do documento, explicando o mecanismo geral de conflito (aplica-se also a UI por extensão do mesmo
princípio):

> "if two Add-Ons ship an entity called `"common:boss"`, then based on **per-world pack stack order, one of
> them will 'win' and the other won't be available**... For most players, pack stack order is **not set in any
> particular intentful order**."

> "one will 'win' (based on pack stack order, **which for most players is not set in any particular intentful
> order**)... We do not want to rely on players configuring their pack stack order precisely in order to have
> great experiences."

**Leitura direta para o caso do addon:** a própria Microsoft afirma que JSON UI **não é seguro para coexistir
com outros packs** que toquem o mesmo arquivo/namespace — só um pack "ganha", decidido pela ordem de pilha por
mundo, ordem essa que o jogador tipicamente não define de propósito. Isso é compatível com o sintoma relatado
("às vezes cai pro form vanilla sem log") **se** houver qualquer outro pack (inclusive uma cópia antiga do
próprio `SonheMenu_RP` em cache, um dev pack duplicado, ou outro add-on instalado) competindo pelo mesmo
namespace `server_form` — o pack que perder a disputa de stack order simplesmente não aplica o override, sem
isso ser tratado como "erro" pelo engine.

## 7. Fallback silencioso / ausência de log — não há confirmação oficial explícita

Fontes: [Content Error Log](https://learn.microsoft.com/en-us/minecraft/creator/documents/contenterrorlog?view=minecraft-bedrock-stable),
[Troubleshooting and Fixing Add-On Bugs](https://learn.microsoft.com/en-us/minecraft/creator/documents/troubleshootingaddons?view=minecraft-bedrock-stable)

**confidence: suspeita** (inferência combinando duas fontes; nenhuma das duas fala do caso específico
"server_form cai pro vanilla sem log")

O Content Error Log documenta duas categorias:

> "**Errors and warnings** - Show up in both the GUI dialog, content log history screen, and the content log
> file - Occur when problematic or concerning content is processed"

> "**Info and verbose** - Only show up in the log file - Occur to show a record of steps taken during the
> course processing content"

Isso confirma que o log **só dispara para problemas que o engine reconhece como problema** (JSON malformado,
tipo errado, referência de textura ausente etc.) — "**Errors and warnings ... occur when problematic or
concerning content is processed**". Um pack que simplesmente **perde a disputa de pack-stack order** (seção 6)
não é "conteúdo problemático" do ponto de vista do engine — é um comportamento esperado do Pack Stacking — logo
**não há motivo, pela lógica documentada, para o engine logar isso como erro**. Isso é dedução nossa a partir
das duas páginas, não uma frase literal da Microsoft dizendo "o fallback de server_form é silencioso".

O guia "Troubleshooting and Fixing Add-On Bugs" (atualizado em 2025-12-23, o mais recente dos dois) cobre
JSON/sintaxe, entities, blocks, items, scripts, recipes, loot tables e performance — **não menciona JSON UI,
`server_form` nem forms customizados em nenhum lugar**. Busca negativa confirmada: a Microsoft não tem uma
seção de troubleshooting dedicada a esse cenário.

## 8. A própria técnica de override de `server_form` não é documentada oficialmente

**confidence: suspeita (busca negativa relevante)**

Buscas por `site:learn.microsoft.com "server_form"`, `"modify server form"` e `"custom forms actionformdata"`
não retornaram nenhuma página oficial que documente o namespace `server_form` como mecanismo suportado de
reskin de `ActionFormData`/`ModalFormData` via JSON UI. As únicas páginas oficiais sobre esses forms são a
referência da Script API (`ActionFormData`, `ModalFormData`, `MessageFormData`, `CustomForm`) — nenhuma delas
menciona um caminho de override via resource pack. A técnica usada pelo addon (override do namespace interno
`server_form`) parece ser conhecimento de comunidade (ex.: Bedrock Wiki — **não oficial**, não citado como
fonte aqui por instrução do pedido), não um contrato documentado/garantido pela Microsoft. Combinado com o
achado da seção 6 (Microsoft desaconselha overrides de UI justamente por não serem "cooperativos"/estáveis),
isso é consistente com instabilidade sem aviso entre packs, entre mundos, ou potencialmente entre versões do
jogo.

## 9. Mudanças recentes que podem afetar `server_form` (release notes oficiais)

Fonte: [1.26.30 Update Notes](https://learn.microsoft.com/en-us/minecraft/creator/documents/update1.26.30?view=minecraft-bedrock-stable)

**confidence: confirmado** (mudanças reais) / **provável** (relevância direta para o bug relatado)

- `@minecraft/server-ui` v2.1.0 lançado nesta versão: `MessageBox`, `CustomForm` e o framework **DDUI**
  (Data-Driven UI) saíram de beta para estável — é o substituto oficial "moderno" para
  `ActionFormData`/`ModalFormData`/`MessageFormData`, com bindings reativos via `Observable*` em vez de JSON UI.
  Ver [Introduction to DataDriven UI (DDUI)](https://learn.microsoft.com/en-us/minecraft/creator/documents/scripting/intro-to-ddui?view=minecraft-bedrock-stable).
  Isso não quebra `server_form` diretamente, mas sinaliza que a Microsoft está movendo o caminho "oficial" de
  customização de forms para longe do override via JSON UI.
- "Fixed the on-screen keyboard not dismissing after submitting text in JSON UI text fields on iOS and
  Android." — fix pontual em JSON UI, não relacionado a fallback.
- "Fixed a bug where resource packs with subpacks would not correctly save to new worlds when they were added
  automatically by activating a corresponding behavior pack." — bug de subpacks não sendo persistidos
  corretamente ao ativar via behavior pack; se `SonheMenu_RP` usa subpacks ou é ativado automaticamente pelo
  `SonheMenu_BP`, isso é uma pista adicional a checar (mas o fix já foi aplicado nesta versão).
- Nenhuma menção a `server_form`, `ui_defs`, namespace override ou prioridade de pack neste changelog.

Não achei nada relevante em buscas por breaking changes de JSON UI em 1.26.0/1.26.10/1.26.20/1.26.40 além do
que já está listado aqui — não abri as 4 páginas individualmente por não terem aparecido menções a UI custom
nos resumos de busca; se necessário, dá para aprofundar depois.

---

## Buscas que não retornaram nada relevante (negativas, declaradas)

- `site:learn.microsoft.com "server_form" json ui` — nenhuma página oficial documentando o namespace.
- `"introduction to json ui" OR "getting started" json ui tutorial` (site:learn.microsoft.com) — não existe um
  tutorial de introdução ao JSON UI na doc oficial atual, só a referência técnica das 4 páginas da seção 3.
- Troubleshooting oficial (seção 7) não menciona JSON UI/forms em nenhum ponto.

## Lista de fontes citadas

- https://learn.microsoft.com/en-us/minecraft/creator/reference/content/jsonuireference/examples/jsonuicomponents/ui_element?view=minecraft-bedrock-stable
- https://learn.microsoft.com/en-us/minecraft/creator/reference/content/jsonuireference/examples/jsonuicomponents/ui_defs?view=minecraft-bedrock-stable
- https://learn.microsoft.com/en-us/minecraft/creator/reference/content/jsonuireference/examples/jsonuicomponents/ui_screen?view=minecraft-bedrock-stable
- https://learn.microsoft.com/en-us/minecraft/creator/reference/content/jsonuireference/examples/jsonuilist?view=minecraft-bedrock-stable
- https://learn.microsoft.com/en-us/minecraft/creator/documents/resourcepack?view=minecraft-bedrock-stable
- https://learn.microsoft.com/en-us/minecraft/creator/documents/practices/guidelinesforbuildingcooperativeaddons?view=minecraft-bedrock-stable
- https://learn.microsoft.com/en-us/minecraft/creator/documents/contenterrorlog?view=minecraft-bedrock-stable
- https://learn.microsoft.com/en-us/minecraft/creator/documents/troubleshootingaddons?view=minecraft-bedrock-stable
- https://learn.microsoft.com/en-us/minecraft/creator/documents/scripting/intro-to-ddui?view=minecraft-bedrock-stable
- https://learn.microsoft.com/en-us/minecraft/creator/documents/update1.26.30?view=minecraft-bedrock-stable
