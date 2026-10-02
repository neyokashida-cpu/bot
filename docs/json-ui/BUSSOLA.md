# Bússola — docs/json-ui/

Índice de navegação. Objetivo: nunca refazer uma busca/leitura que já existe aqui.
Antes de investigar qualquer coisa sobre JSON UI do SonheMenu, siga esta ordem:

1. Leia **`DIAGNOSTICO_FINAL.md`** (raiz de `docs/json-ui/`) — é a síntese. Causa mais provável do bug,
   riscos catalogados com evidência, correções propostas. Cobre 90% do que se precisa saber.
2. Se precisar de mais profundidade num ponto específico, use a tabela abaixo pra ir direto no arquivo
   de `fontes/` que já cobre o assunto — não regrepe o corpus vanilla nem rebusque a web do zero.
3. Só pesquise algo novo se o assunto genuinamente não aparecer em nenhuma linha abaixo.

Pastas `veredictos/`, `capitulos/`, `diagnosticos/` estão **vazias** — plano original de 4 fases foi
substituído por agentes diretos; verificação adversarial virou parte do prompt de cada fonte, e a síntese
final é só o `DIAGNOSTICO_FINAL.md`. Pode ignorar essas 3 pastas.

## Documento raiz

| Arquivo | Conteúdo |
|---|---|
| `DIAGNOSTICO_FINAL.md` | Síntese de tudo. Causa raiz ranqueada, catálogo de riscos com correção proposta, plano priorizado [SEGURO]/[ARRISCADO]. |

## fontes/ — nosso addon (leitura, sem edição)

| Arquivo | Conteúdo |
|---|---|
| `sonhe-atual.md` | Auditoria do SonheMenu_RP atual: `sonhe_forms.json`, `sonhe_grid.json`, `_ui_defs.json`, manifest, `audit_ui.py`. |
| `sonhe-bp.md` | Auditoria do SonheMenu_BP: todos os scripts, marcador de título `§d§r§e§a§m§r`, pontos de overflow de grid (`abrirVerAnuncios`, `abrirMinhasVendas`). |

## fontes/ — corpus vanilla oficial (1.26.44, 207 arquivos)

| Arquivo | Conteúdo |
|---|---|
| `vanilla-serverform.md` | Onde cada namespace mora de fato (`server_form`, `common_dialogs` = `ui_template_dialogs.json`). Referência-mãe. |
| `vanilla-common.md` | Namespace `common` (`ui_common.json`): `common_panel`, `common.button`, scrolling_panel, container, todas as $variáveis/defaults. |
| `vanilla-grid.md` | Todo uso real de `"type": "grid"` no corpus: binding de contagem (`#form_button_contents`), `grid_dimensions` x `#maximum_grid_items` (mutuamente exclusivos). |
| `vanilla-colecoes.md` | Bindings de coleção (`collection_name`, `collection_details`, `collection_index`), regra de repetir binding-âncora em controles irmãos. |
| `vanilla-scroll.md` | `scrolling_panel`/`scroll_view`: regras de tamanho (px fixo vs %), armadilhas dentro de scroll. |
| `vanilla-telas-modernas.md` | 5 telas reais de grade de tiles (loja, world templates, skins, persona) — proporção, espaçamento, hover. |
| `vanilla-adaptativo.md` | Aninhamento `%c`/`%cm` — confirmado seguro até 5-6 níveis (derruba a hipótese de que 2 níveis quebrou a build). |
| `vanilla-alpha.md` | Alpha é opacidade pura, teto ~0.85, sem propagação pra filho sem `propagate_alpha` explícito. Descarta alpha como causa do bug. |
| `vanilla-layer.md` | `layer` é sempre relativo a irmãos, nunca global. |
| `vanilla-labels.md` | Truncamento de texto (hífen no X, "..." no Y). Fix proposto pro `screen_body` do nosso grid. |
| `vanilla-tema.md` | Texturas sólidas, grafia `nineslice_size`+`base_size`, defaults de botão. |
| `vanilla-varredura.md` | Tabela de existência/contagem de ~17 propriedades (`keep_ratio`, `propagate_alpha`, `modifications` etc.) + lista dos 207 arquivos do corpus. |

## fontes/ — addons de terceiros e coletados

| Arquivo | Conteúdo |
|---|---|
| `addon-ui1.md` | Override mínimo de `server_form`, 5 arquivos. |
| `addon-ui2.md` | JSON UI custom com `stack_panel` horizontal. |
| `addon-ui3.md` | Mesma base do ui2 + `type: grid` + `scrolling_panel` (delta documentado). |
| `addon-ui4.md` | `server_form.json` único arquivo, botões customizados. |
| `addon-ui5.md` | `server_form.json` único arquivo, texturas customizadas. |
| `adminsuite-forms.md` | Admin Suite 1.50 — arquitetura completa (`list_form`, `modal_form`, `admin_form`, `shop_form_new`). |
| `coletados-serverform.md` | Comparação lado a lado de 6 `server_form` custom coletados na web. |
| `coletados-chest.md` | Chest-UI / inventário fake via JSON UI (grid multi-coluna, slots). |
| `coletados-misc.md` | Arquivos diversos coletados — origem identificada, padrões novos extraídos. |
| `coletados-exemplos.md` | Exemplos didáticos de grid/imagem/binding/scroll (gerados de `ui.schema.json`). |

## fontes/ — documentação técnica (Bedrock Wiki)

| Arquivo | Conteúdo |
|---|---|
| `docs-wiki.md` | `json-ui-documentation.md` + `best-practices.md` — sintaxe geral, binding, unidades. |
| `docs-tecnicos.md` | **`modifying-server-forms.md`** (a doc da técnica de marcador — confirma overlap sem correção) + `dynamic-content-generation.md` + buttons/toggles + preserve-title-texts + type-conversion. |

## fontes/ — pesquisa web

| Arquivo | Conteúdo |
|---|---|
| `web-docs.md` | **Achado-chave**: doc oficial Microsoft diz JSON UI overrides não são cooperativos, vencedor = ordem de pilha de packs "não intencional pra maioria dos jogadores", perder não gera log. |
| `web-falhas.md` | Causas documentadas de UI custom sumir sem erro. |
| `web-cache.md` | Cache de cliente Bedrock + bug real Mojang MCPE-153925 (race condition "unpredictable"). |
| `web-github.md` | Implementações públicas no GitHub (Chest-UI: RP depende do BP por UUID — nós fazemos o oposto/nada). |
| `web-mcpedl.md` | Comentários de usuários em addons públicos — nenhum relato do bug exato encontrado (busca negativa registrada). |

## Perguntas comuns → onde ir direto

- "Por que a UI custom às vezes some sem log?" → `DIAGNOSTICO_FINAL.md` seção 3, evidência raiz em `web-docs.md`.
- "Como funciona o marcador de título?" → `DIAGNOSTICO_FINAL.md` seção 2, doc técnico em `docs-tecnicos.md`.
- "Isso é bug de cache/mundo desatualizado?" → `web-cache.md` (MCPE-153925) + `DIAGNOSTICO_FINAL.md` seção 4 (mundo `RCWd1qdM+y4=` travado em `1.0.10`).
- "Grid pode estourar 12 slots?" → `sonhe-bp.md` (evidência) + `vanilla-grid.md` (o que o vanilla faz em vez disso).
- "Uma propriedade X existe no jogo?" → `vanilla-varredura.md` primeiro; se não estiver lá, `vanilla-common.md`/`vanilla-grid.md`/`vanilla-colecoes.md` por assunto.
- "Como um addon de terceiro faz Y?" → tabela "addons de terceiros" acima, escolha pelo padrão (grid simples, scroll, botão custom, textura).
