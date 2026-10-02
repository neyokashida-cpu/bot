# Diagnóstico Final — Bug do menu SONHE caindo pra lista vanilla

> Síntese de 31 relatórios de pesquisa (`docs/json-ui/fontes/*.md`) + auditoria direta do addon real
> (`ADDONS/SonheMenu_RP`, `ADDONS/SonheMenu_BP`). Documento só de diagnóstico — **nenhum arquivo do
> addon foi editado**. A correção real vem depois, com aprovação do usuário.
>
> Cliente alvo: Bedrock 1.26.44. Data da síntese: 2026-08-31.
> Convenção de confiança usada nas fontes e preservada aqui: **confirmado** (evidência direta de
> código/documentação oficial) / **provável** (inferência forte, consistente entre fontes) /
> **suspeita** (hipótese plausível, não testada em jogo).

---

## 1. Resumo executivo

O sintoma relatado — "o menu às vezes cai pro form vanilla em lista, sem log, de forma
intermitente" — **não tem uma única causa comprovada em jogo**, mas tem uma explicação estrutural
muito mais forte que qualquer bug de sintaxe no JSON: **a própria Microsoft afirma, em documentação
oficial, que overrides de JSON UI não são "cooperativos"** — quando mais de um pack (ou mais de uma
cópia/versão do mesmo pack) toca o mesmo arquivo/namespace, só um vence, decidido pela **ordem da
pilha de packs**, que "para a maioria dos jogadores não é definida de forma intencional", e essa
disputa **nunca gera entrada no Content Log** porque, do ponto de vista do motor, nada de errado
aconteceu (`web-docs.md` §6-7). Isso é o fio condutor deste documento.

Causas ranqueadas por confiança, da mais forte pra mais fraca:

1. **[ALTO]** Ausência de `dependencies` ligando `SonheMenu_BP` → `SonheMenu_RP` no manifest, combinada
   com o modelo "quem ganha não erra" da Microsoft. Se o RP não estiver presente/ativo no mundo
   naquele momento, o BP monta o `ActionFormData` normalmente, o marcador `§d§r§e§a§m§r` vira
   formatação inerte sem ninguém pra interceptar, e o resultado é **exatamente** a lista vanilla,
   com log limpo (`sonhe-bp.md` §4, `sonhe-atual.md` §5).
2. **[ALTO, confirmado empiricamente pelo próprio projeto]** Cache/versão de pack dessincronizada
   entre mundos e entre cliente↔servidor: a auditoria encontrou um mundo local (`Server`) e o
   `packcache` do cliente correspondente **travados 26 versões atrás do HEAD**, rodando uma build
   com bugs já corrigidos (`sonhe-atual.md` §0). Isso é reforçado por um bug real e catalogado pela
   própria Mojang (`MCPE-153925`) descrevendo uma race condition de cache de pack explicitamente
   classificada como "unpredictable" (`web-cache.md` §4).
3. **[MÉDIO]** Falha silenciosa de binding dentro do próprio `sonhe_forms.json` (marcador não
   complementar, ordem de bindings trocada, `§` corrompido por encoding) — mecanismo genérico muito
   bem documentado (`addon-ui1.md`–`addon-ui5.md`, `adminsuite-forms.md`, `docs-tecnicos.md`), mas a
   auditoria da lógica **atual** do pack não encontrou nenhuma dessas falhas — a lógica de marcador
   está correta e é, inclusive, mais robusta que a maioria dos addons de terceiros estudados.
4. **[BAIXO, mas real e já confirmado no código do BP]** O grid fixo de 12 slots (`grid_dimensions
   [3,4]`, sem contagem dinâmica) faz com que dois menus reais da Auction House percam botões
   silenciosamente — um sintoma relacionado, mas distinto (itens somem *dentro* da tela custom, a
   tela custom não desaparece inteira).

Nenhuma fonte (nem o corpus vanilla, nem os 5 addons de terceiros, nem a pesquisa web) encontrou um
mecanismo pelo qual **só** um valor de `alpha` (como o `0.7 → 0.9` do último commit) derrube a tela
inteira pro vanilla — isso está descartado com alta confiança (`vanilla-alpha.md`).

---

## 2. Como o mecanismo de override funciona — a técnica do marcador de título, do zero

### 2.1 O ponto de entrada vanilla

Todo `ActionFormData`/`ModalFormData` do Minecraft Bedrock é desenhado por um único arquivo do
resource pack vanilla, `ui/server_form.json`, namespace `server_form`. A cadeia é
(`vanilla-serverform.md` §1-2, `docs-tecnicos.md` §2.1):

```
third_party_server_screen  (screen raiz, @common.base_screen)
  └─ main_screen_content    (panel, size [0,0]  ← IMPORTANTE: tamanho zero)
       └─ server_form_factory   (type: factory)
            ├─ control_ids.long_form   = "@server_form.long_form"    (ActionFormData/MessageFormData)
            └─ control_ids.custom_form = "@server_form.custom_form"  (ModalFormData)
```

`main_screen_content` é **`[0,0]`** de propósito — cada filho recebe tamanho absoluto em pixel na
própria invocação (`long_form@common_dialogs.main_panel_no_buttons` vanilla é `size: [225,200]`).
Isso importa porque **qualquer filho que use `%` diretamente sob essa raiz colapsa para 0px, sem
nenhum erro** — é o primeiro mecanismo de "sumiço silencioso" que aparece em praticamente todas as
fontes (`vanilla-serverform.md` §2.1, `adminsuite-forms.md` R2, `addon-ui1.md` R4).

### 2.2 A única forma de "conversar" entre o script (BP) e a tela (RP)

O `ActionFormData`/`ModalFormData` do `@minecraft/server-ui` não tem nenhum campo dedicado para
"isto é uma tela custom". O único canal de dados é o **texto** que o script já manda de qualquer
forma: `.title()`, `.body()` e os textos/ícones de `.button()` (`addon-ui1.md` R10,
`vanilla-serverform.md` §8.3). Toda técnica de override de `server_form` estudada — a documentação
oficial da Bedrock Wiki (`docs-tecnicos.md` §1.1), os 5 addons de exemplo (`addon-ui1.md`-`addon-ui5.md`),
o Admin Suite (`adminsuite-forms.md`), o Chest-UI real publicado no GitHub (`web-github.md` §2) e o
próprio SonheMenu — usa a mesma ideia: **embutir um marcador de texto no título** e testar sua
presença via JSON UI.

### 2.3 O teste de presença: subtração de string

O JSON UI tem um operador `-` sobre strings: `A - 'sub'` remove a primeira ocorrência de `'sub'` de
`A`. Se o resultado for **igual** a `A`, a substring não estava presente. Daí o teste-padrão:

```json
{ "binding_type": "view",
  "source_property_name": "((#title_text - 'MARCADOR') = #title_text)",
  "target_property_name": "#visible" }
```

`true` = "o título **não** contém o marcador" → mostra o ramo vanilla.
A negação (`not (...)`) do mesmo predicado → mostra o ramo custom.

Isso é documentado literalmente pela Bedrock Wiki como a técnica oficial de comunidade
(`docs-tecnicos.md` §1.1-1.2, `web-github.md` §1.1) e usado por **todas** as fontes de terceiros
lidas: `ui1`-`ui5` (`'Custom Form'` visível), Admin Suite (`§g§r§i§d§r`, `§m§e§m§b§e§r` etc.),
Chest-UI real no GitHub (`(not ((#title_text - $condition) = #title_text))`), skyls, tile_server_form
(BedrockIslands). **Importante:** o operador `-` sobre string **tem 0 ocorrências em todo o corpus
vanilla oficial** (208 arquivos, `vanilla-serverform.md` §5.7, `vanilla-grid.md` §2). Ele funciona,
é a técnica canônica de comunidade e está na própria Bedrock Wiki — mas nunca foi usado pela Mojang,
o que o torna, em teoria, a peça de sintaxe menos testada por eles em qualquer atualização do
engine.

### 2.4 A topologia usada pelo SonheMenu (e por praticamente todos os addons estudados)

O `long_form` vanilla (`long_form@common_dialogs.main_panel_no_buttons`) é redefinido, no arquivo do
pack, como um `panel` puro com dois filhos irmãos, cada um herdando de
`common_dialogs.main_panel_no_buttons` (ou de um controle próprio) e testando o marcador:

```
long_form (panel, sem herança)
├─ ramo A: @common_dialogs.main_panel_no_buttons, size [225,200], $child_control=server_form.long_form_panel
│    visível quando  NÃO contém o marcador   → é a lista/modal vanilla original
└─ ramo B: @<tela custom>, size próprio
     visível quando  CONTÉM o marcador       → é a tela do addon
```

`sonhe_forms.json:8-44` implementa exatamente isso. É a mesma topologia de `ui1`-`ui5`, do Admin
Suite e do Chest-UI real — **confirmada como o padrão de facto de toda a comunidade**, não uma
invenção do projeto.

### 2.5 As duas rotas de registro do override — e por que isso importa

Há duas formas válidas de fazer o arquivo custom "vencer" o vanilla dentro do namespace
`server_form`:

| Rota | Quem faz | Como funciona | Dependências extras |
|---|---|---|---|
| **(A) Mesmo caminho** | `ui1`-`ui5`, Admin Suite, Chest-UI | grava em `RP/ui/server_form.json` (o mesmo caminho do vanilla); **não precisa** de `_ui_defs.json` porque o vanilla já registra esse caminho | nenhuma |
| **(B) Arquivo novo + registro** | **SonheMenu** | grava em `RP/ui/sonhe_forms.json`, namespace `server_form`, e lista o arquivo em `_ui_defs.json` | o `_ui_defs.json` precisa ser lido com sucesso; e o merge do namespace `server_form` entre dois arquivos diferentes precisa resolver `long_form` pra versão do pack |

O merge, nas duas rotas, acontece **por chave de topo dentro do namespace, não por arquivo inteiro**
— isso é confirmado de forma independente em `addon-ui1.md` R2, `addon-ui2.md` R2, `addon-ui4.md` R2
e `adminsuite-forms.md` R1: um arquivo pode redefinir só `long_form` e continuar referenciando
`server_form.long_form_panel`, que só existe no vanilla, e funciona. A rota B do SonheMenu é
**válida e usada em produção** (é a mesma do Admin Suite), mas introduz uma dependência extra que a
rota A não tem: **a doc oficial da Microsoft não documenta a regra de merge entre pacotes que
declaram o mesmo namespace** (`web-docs.md` §4) — o comportamento é conhecido pela comunidade, mas
não é um contrato garantido por escrito pela Mojang.

---

## 3. Por que falha silenciosamente — teoria unificada

### 3.1 A tese central: JSON UI não é "cooperativo" por design (achado mais forte)

Fonte primária: `web-docs.md` §6, citando literalmente
[*Guidelines for Building Cooperative Add-Ons*](https://learn.microsoft.com/en-us/minecraft/creator/documents/practices/guidelinesforbuildingcooperativeaddons):

> "Because JSON UI (...) and fonts (...) are **not overridable in a cooperative manner** - such
> that multiple Add-Ons can customize the same asset - cooperative Add-Ons **should not override
> any JSON UI** or font glyph files."
>
> "Do not override UI files (resource packs/ui)"
>
> "...based on **per-world pack stack order, one of them will 'win' and the other won't be
> available**... For most players, pack stack order is **not set in any particular intentful
> order**."

E o mecanismo de "Pack Stacking" em si (`web-docs.md` §5, citando a doc oficial *Create Custom Grass
Blocks*):

> "**Pack Stacking** is how content is loaded on top of Vanilla content, causing each object that
> has the same name in both packs to be overwritten by the *latest* applied pack."

E por que isso nunca gera log (`web-docs.md` §7, citando *Content Error Log*):

> "**Errors and warnings** ... occur when problematic or concerning content is processed."

Perder uma disputa de pilha de packs **não é conteúdo problemático** do ponto de vista do motor — é
o comportamento esperado do Pack Stacking. Logo, **não há razão, pela lógica documentada, para o
engine logar isso como erro**. Essa é a explicação estrutural que melhor bate com "some sem log,
intermitente, sem mudar nada no JSON": não é o JSON que está errado, é a disputa de qual definição
de `server_form.long_form` está ativa **naquele momento, naquele mundo, naquele cliente**.

### 3.2 Os mecanismos concretos que fazem o SonheMenu "perder" essa disputa

A tese acima é abstrata até ser amarrada a evidência concreta do projeto. Há três mecanismos reais,
cada um encontrado de forma independente:

**(a) RP ausente/inativo sem que ninguém seja avisado — `sonhe-bp.md` §4, `sonhe-atual.md` §5**

`ADDONS/SonheMenu_RP/manifest.json` (arquivo inteiro, 19 linhas) **não tem** bloco `dependencies`.
`ADDONS/SonheMenu_BP/manifest.json:20-33` só declara dependências de módulo de script
(`@minecraft/server`, `@minecraft/server-ui`, `@minecraft/server-net`), nenhuma delas aponta pro
UUID do RP (`b71a84eb-d21e-4460-bb7c-eb9758d1ede4`). `sonhe-bp.md` conclui, com evidência de código
(todos os 9 pontos de construção de `ActionFormData` sempre incluem o marcador — `sonhe-bp.md` §3):
se o RP estiver ausente/desativado num mundo específico, **o BP roda normalmente**, o marcador
`§d§r§e§a§m§r` é só formatação de cor sem efeito nenhum (nada intercepta), e o resultado é a lista
vanilla **com log limpo**, porque do ponto de vista do BP `form.show()` resolveu normalmente.
`sonhe-bp.md` chama isso textualmente de "o caminho que melhor bate com 'às vezes cai na lista
vanilla, sem erro'".

**(b) Cache/versão de pack dessincronizada — confirmado empiricamente — `sonhe-atual.md` §0**

A auditoria direta do disco deste computador encontrou **dois mundos locais** com o pack instalado:

| Mundo | `version` do RP instalado | Última cópia |
|---|---|---|
| `ClaudeAurudoLegal` | `[1,0,36]` — em dia com o HEAD | 27/ago |
| `Server` (`RCWd1qdM+y4=`) | `[1,0,10]` — **26 versões atrás** | 24/ago |

O `packcache` do cliente que se conecta no mundo `Server` também está travado em `[1,0,10]`, no
mesmo intervalo de minutos da cópia parada no mundo. O `sonhe_forms.json` **dessa cópia antiga**
tem bugs já corrigidos no repo (grafia errada de `nine_slice_size`, referência direta a
`textures/ui/sonhe/panel_frame` que estica mal, `main_screen_content` redeclarado com
`size:["100%","100%"]` que não existe mais no HEAD). Ou seja: **se o teste que motivou o relato do
bug foi feito nesse mundo/cliente, o sintoma "caiu pro vanilla" não é sobre o JSON atual — é uma
build de dias atrás, com problemas já resolvidos, que nunca foi reinstalada.** É a manifestação mais
direta e concreta da tese da seção 3.1: uma versão "vence" sobre a outra sem nenhum aviso.

Reforço externo: `web-cache.md` §4 encontrou um bug real catalogado pela própria Mojang,
**MCPE-153925** ("Client can overwrite/corrupt resource packs when caching from host"), descrevendo
uma race condition de nomeação de pasta de cache quando dois packs terminam o download quase ao
mesmo tempo — citação literal do próprio relator: **"the bug is timing related and thus
unpredictable"**, e o workaround documentado é simplesmente "entrar de novo, provavelmente vai
funcionar". Esse ticket é sobre packs baixados de servidor, não sobre pastas de desenvolvimento
locais — mas prova que o subsistema de cache de resource pack do Bedrock **tem histórico real e
reconhecido** de bugs de timing/race condition, o que sustenta a hipótese de cache como causa raiz
recorrente, mesmo fora do caso específico já confirmado no item anterior.

**(c) Falha de binding dentro do próprio JSON (mecanismo genérico, mas hoje não confirmado ativo)**

Além da disputa de pacote, existe uma segunda classe de "silêncio" — **inerente ao modelo de
binding do JSON UI**, independente de qualquer disputa de pack. A Bedrock Wiki confirma
explicitamente (`web-github.md` §1.3, parafraseando `json-ui-documentation.md`):
`binding_name_override` ausente "executa mas nunca atualiza nenhuma propriedade";
`source_control_name` incorreto "silently fails, leaving dependent elements unsynced"; mismatch de
`binding_type` "produces no error but leaves controls invisible". `web-falhas.md` #10 e
`docs-wiki.md` §5 confirmam o mesmo pelo lado da doc oficial e da wiki. Os addons de terceiros
estudados mostram essa classe de bug em produção real: `addon-ui2.md` R3 encontra um par de
bindings **não complementar** em `ui2` (título como `"Custom Form Extra"` deixa os dois ramos
invisíveis ao mesmo tempo); `coletados-serverform.md` §3.4 mostra o `tile_server_form`
(BedrockIslands) com um marcador que embute literalmente `'Islands§r'` — se o `§r` final não vier
exatamente daquele jeito no título recebido, **os quatro testes falham e a lista vanilla aparece
silenciosamente**.

A auditoria do `sonhe_forms.json` atual (`sonhe-atual.md` §1.1, confirmado por leitura direta nesta
síntese) **não encontrou nenhuma dessas falhas hoje**: o par de bindings é complementar por
construção (`A` vs `not(A)`, não duas comparações independentes — ver §4 abaixo), a ordem de âncora
antes do view-binding está correta em todos os controles, e o marcador é idêntico nos dois lados
(RP e BP). Essa classe de causa continua sendo o item de maior probabilidade **se algum dia o JSON
for editado sem seguir o checklist da seção 6**, mas não é a explicação mais provável do estado
atual.

### 3.3 Síntese das três camadas

| Camada | Mecanismo | Gera log? | Evidência de que já aconteceu neste projeto |
|---|---|---|---|
| 1. Pack Stacking (Microsoft) | ordem de pilha decide quem vence; nunca é "erro" | Não, por definição (`web-docs.md` §6-7) | é a explicação genérica que enquadra as camadas 2 |
| 2a. Dependency RP↔BP ausente | RP pode estar ausente/inativo sem aviso | Não (`sonhe-bp.md` §4) | gap confirmado nos dois manifests |
| 2b. Cache/versão de pack | cliente/mundo usa cópia antiga | Não | **confirmado empiricamente** — mundo `Server` 26 versões atrás (`sonhe-atual.md` §0) + bug real MCPE-153925 |
| 3. Binding mal formado dentro do JSON | marcador não bate, ordem errada, encoding | Não (`docs-wiki.md`, `web-github.md` §1.3) | mecanismo genérico bem documentado; **não confirmado ativo** no `sonhe_forms.json`/`sonhe_grid.json` atuais |

---

## 4. Catálogo de riscos estruturais encontrados no addon atual

Cada item tem evidência (arquivo:linha), nível de confiança e uma correção concreta. Os diffs abaixo
são **propostas**, não foram aplicadas.

### R1 — [ALTO] [confirmado o gap / provável a causa] Sem `dependencies` ligando BP → RP

**Evidência:** `ADDONS/SonheMenu_RP/manifest.json` (arquivo inteiro, sem bloco `dependencies`);
`ADDONS/SonheMenu_BP/manifest.json:20-33` (só módulos de script). UUID do RP:
`b71a84eb-d21e-4460-bb7c-eb9758d1ede4`, versão atual `[1, 0, 36]`.

**Fontes que sustentam:** `sonhe-atual.md` §5, `sonhe-bp.md` §4, `addon-ui5.md` R10/D3 (ui5 faz
dependência mútua por UUID entre RP e BP), `web-github.md` §2.2 (Chest-UI real no GitHub declara
`RP → BP` por UUID em produção).

**Correção proposta:**

```diff
--- a/ADDONS/SonheMenu_BP/manifest.json
+++ b/ADDONS/SonheMenu_BP/manifest.json
@@
     "dependencies": [
         {
             "module_name": "@minecraft/server",
             "version": "2.10.0-beta"
         },
         {
             "module_name": "@minecraft/server-ui",
             "version": "2.2.0-beta"
         },
         {
             "module_name": "@minecraft/server-net",
             "version": "1.0.0-beta"
+        },
+        {
+            "uuid": "b71a84eb-d21e-4460-bb7c-eb9758d1ede4",
+            "version": [1, 0, 36]
         }
     ]
```

**Ressalva importante (confirmada por `sonhe-bp.md` §4):** `dependencies` no manifest de um BP
**não bloqueia** a ativação do BP se o RP não estiver presente — no Bedrock isso normalmente só gera
um aviso/erro de "dependência ausente" no Content Log, sem travar o BP. Ou seja: o ganho real dessa
mudança é **diagnóstico** (passa a aparecer *algo* no log quando o RP falta), não uma trava dura.
Continua sendo a correção de maior valor porque hoje **não existe nem esse diagnóstico**.
**Custo de manutenção:** toda vez que a `version` do RP subir, essa entrada precisa ser atualizada
junto, senão o BP passa a acusar dependência desatualizada.

---

### R2 — [ALTO] [confirmado] Grid fixo de 12 slots estoura em 2 menus reais da Auction House

**Evidência:** `ADDONS/SonheMenu_RP/ui/sonhe_grid.json:108-117` (`tiles_grid`, `grid_dimensions:
[3,4]` = 12 células, sem binding de contagem, comentário próprio do arquivo em `sonhe_grid.json:109`
confirma que é proposital). Do lado do script: `abrirVerAnuncios` monta até 13 botões numa página do
meio cheia (10 itens + "Página anterior" + "Próxima página" + "Voltar"); `abrirMinhasVendas` **não
tem paginação nenhuma** — qualquer vendedor com ≥12 anúncios ativos estoura.

**Fontes que sustentam:** `sonhe-atual.md` risco #1, `sonhe-bp.md` §1-2 (tabela completa dos 14
forms do addon com contagem de botões por tela).

**Correção proposta (lado do script, não toca em JSON UI):**

```diff
--- a/ADDONS/SonheMenu_BP/scripts/auction.js
+++ b/ADDONS/SonheMenu_BP/scripts/auction.js
@@
-const ITENS_POR_PAGINA = 10;
+const ITENS_POR_PAGINA = 9;
```

(reduz de 10 para 9 itens por página, deixando espaço garantido para os 3 botões de navegação —
9 + 3 = 12, exatamente o teto do grid. Localizar a constante e o loop de `abrirVerAnuncios`,
`auction.js:390-404`.) Em `abrirMinhasVendas` (`auction.js:788-794`), aplicar o mesmo padrão de
paginação já usado em `abrirVerAnuncios`, com o mesmo teto de 9 itens + navegação.

**Alternativa mais arriscada (não recomendada agora):** trocar `grid_dimensions` fixo por
`grid_rescaling_type: "horizontal"` + binding `#form_button_contents → #maximum_grid_items` — ver
item [ARRISCADO] #9 na seção 6.

---

### R3 — [ALTO, confirmado empiricamente, sem ação de código] Mundo de teste desatualizado

**Evidência:** `sonhe-atual.md` §0 — mundo `Server` (`minecraftWorlds/RCWd1qdM+y4=`) e o `packcache`
do cliente correspondente travados em `version [1,0,10]`, 26 versões atrás do HEAD (`[1,0,36]`).

**Ação (operacional, não é diff de código):** copiar `ADDONS/SonheMenu_RP` atual por cima de
`minecraftWorlds/RCWd1qdM+y4=/resource_packs/SonheMenu_RP/`, e limpar o `packcache` do cliente que
conecta nesse mundo, **antes de qualquer novo teste em jogo** (ver skill `mcpe-pack-deploy` do
próprio projeto). Sem isso, qualquer teste feito nesse mundo específico está testando uma build de
3+ dias atrás, com bugs já corrigidos.

---

### R4 — [MÉDIO] [confirmado a divergência / suspeita o efeito] `long_form` sem `size`

**Evidência:** `ADDONS/SonheMenu_RP/ui/sonhe_forms.json:8-9`:

```json
"long_form": {
    "type": "panel",
    "controls": [ ... ]
```

Não há `size` neste nó. `ui4` e `ui5` (dois addons de terceiros independentes) declaram
`"size": ["100%", "100%"]` nesse mesmo ponto. O Admin Suite também sobrescreve o pai
(`main_screen_content`) com tamanho real, pelo mesmo motivo.

**Fontes:** `addon-ui4.md` R3/D1, `addon-ui5.md` R1/D1, `sonhe-atual.md` §2.

**Efeito atual (confirmado por análise da árvore):** inofensivo hoje — os dois ramos filhos
(`sonhe_vanilla_form`, `size [225,200]`; `sonhe_custom_form@grid_screen`, `size [320,452]`) têm
tamanho próprio em pixel, então não dependem do tamanho do pai `long_form`. É uma fragilidade
**latente**: se um dia um terceiro filho for pendurado direto em `long_form` usando `%`, ele
colapsa pra 0px sem erro (regra confirmada em `vanilla-serverform.md` §2.1 e §6.3).

**Correção proposta:**

```diff
--- a/ADDONS/SonheMenu_RP/ui/sonhe_forms.json
+++ b/ADDONS/SonheMenu_RP/ui/sonhe_forms.json
@@
   "long_form": {
     "type": "panel",
+    "size": [ "100%", "100%" ],
     "controls": [
```

---

### R5 — [MÉDIO] [confirmado] Validador de dev desatualizado no repo aplica regra já revogada

**Evidência:** `sonhe-atual.md` risco #4 — `ADDONS/tools/audit_ui.py` (arquivo não rastreado pelo
git) acusa `type:grid + collection_name` como proibido (na verdade é o padrão que funciona,
confirmado por `vanilla-grid.md` §3: 0 de 134 grids vanilla combinam `grid_dimensions` com
`#maximum_grid_items` — a proibição real é essa combinação, não `grid` + `collection_name`) e
acusa `binding_name` `#null` como desconhecido (é o idioma de âncora do próprio pack, documentado em
`sonhe_grid.json:5` como mecânica preservada).

**Correção proposta:** apagar `ADDONS/tools/audit_ui.py`, ou (se ele tiver valor de CI) atualizar as
tabelas `PROP_PROIBIDA`/`NS_VANILLA` internas pra refletir a regra correta documentada em
`JSON_UI_NOTAS.md`. *Nota: este relatório não leu o conteúdo completo de `audit_ui.py`, então o diff
exato depende de abrir o arquivo — a recomendação aqui é de escopo (o quê corrigir), não de linha
exata.*

**Risco se não corrigido:** alguém pode "consertar" o `tiles_grid` de volta pro padrão
`stack_panel + #maximum_grid_items` seguindo o alerta do script, e esse padrão **já foi testado e
comprovadamente não populou** (`sonhe-atual.md`, `JSON_UI_NOTAS.md`).

---

### R6 — [BAIXO] [confirmado a ausência no vanilla, provável a fragilidade] Operador `-` de string sem precedente vanilla

**Evidência:** `sonhe_forms.json:24,37` usa `((#title_text - '§d§r§e§a§m§r') = #title_text)` e sua
negação. Grep exaustivo em 207-208 arquivos do corpus vanilla oficial: **0 ocorrências** do operador
`-` sobre string em `source_property_name` (`vanilla-serverform.md` §5.7, `vanilla-grid.md` §2,
`addon-ui1.md` R6).

**Contraponto:** É a técnica **oficialmente documentada pela Bedrock Wiki**
(`docs-tecnicos.md` §1.1-1.2, citação literal do tutorial `modifying-server-forms.md`) e usada por
**todos** os addons de terceiros e pelo Chest-UI real publicado no GitHub. Não é uma invenção de
risco do projeto — é o padrão de facto da comunidade inteira.

**Ação recomendada:** nenhuma agora. Registrar como o ponto de maior fragilidade de sintaxe caso uma
atualização futura do engine mude o parser de expressões — não há como mitigar isso sem abandonar a
técnica de marcador por completo (o que nenhuma fonte estudada faz).

---

### R7 — [BAIXO] [confirmado] Bug de truncamento de label — `screen_body` corta com "..."

**Evidência:** `ADDONS/SonheMenu_RP/ui/sonhe_grid.json:88-106`:

```json
"screen_body": {
  "type": "label",
  "text": "#form_text",
  "size": [ "100% - 8px", "default" ],
  "max_size": [ "100% - 8px", 30 ],
  ...
```

`max_size` trava a altura em 30px (~3 linhas). O comentário do próprio arquivo vanilla confirma o
mecanismo: `"$tool_tip_text_max_size defines how text wraps (x wraps with a '-' and y will cut off
with '...')"` (`ui_common.json:7202`, citado em `vanilla-labels.md` §2). Texto de corpo mais longo
que 3 linhas é cortado com reticências, silenciosamente.

**Fonte:** `vanilla-labels.md` §7 (diagnóstico e correção detalhados).

**Correção proposta:**

```diff
--- a/ADDONS/SonheMenu_RP/ui/sonhe_grid.json
+++ b/ADDONS/SonheMenu_RP/ui/sonhe_grid.json
@@ "screen_body"
     "size": [ "100% - 8px", "default" ],
-    "max_size": [ "100% - 8px", 30 ],
+    "max_size": [ "100% - 8px" ],
```

Por que é seguro (`vanilla-labels.md` §7): `grid_stack`/`list_stack` já são `stack_panel` com altura
`"100%c"` (cresce com o conteúdo) — exatamente o mesmo esqueleto que o vanilla usa para labels
multi-linha sem `max_size` em Y (`ui_common.json`, `general_tab_section` +
`content_log_location_label`, citados em `vanilla-labels.md` §3). Não há dependência circular.

---

### R8 — [BAIXO, cosmético] Alpha inconsistente entre `grid_screen` (0.9) e `list_screen` (0.7)

**Evidência:** `sonhe_grid.json:33` (`panel_bg`, `alpha: 0.9`) vs. `sonhe_grid.json:371` (`list_bg`,
`alpha: 0.7`) — apesar do commit `6a347a5` dizer "unifica opacidade do fundo".

**Fonte:** `vanilla-alpha.md`, seção "Aplicação no SonheMenu".

**Correção proposta (qualquer uma das duas, à escolha):**

```diff
--- a/ADDONS/SonheMenu_RP/ui/sonhe_grid.json
+++ b/ADDONS/SonheMenu_RP/ui/sonhe_grid.json
@@ "list_bg"
-          "alpha": 0.7,
+          "alpha": 0.9,
```

ou, seguindo a recomendação de `vanilla-alpha.md` (reduzir a camada de baixo já que os tiles somam
outra camada por cima):

```diff
--- a/ADDONS/SonheMenu_RP/ui/sonhe_grid.json
+++ b/ADDONS/SonheMenu_RP/ui/sonhe_grid.json
@@ "panel_bg"
-          "alpha": 0.9,
+          "alpha": 0.72,
```

Sem risco de regressão estrutural — `list_screen` é hoje um fallback **não ativo** (não referenciado
por `sonhe_forms.json`), então o impacto imediato é zero; a mudança só importa se/quando o fallback
for ativado.

---

### R9 — [BAIXO, oportunidade] Marcador não é removido do título antes de exibir

**Evidência:** `sonhe_grid.json:59-76` (`screen_title`), `"text": "#title_text"` direto, sem
remover `§d§r§e§a§m§r` antes de mostrar.

**Fonte:** `adminsuite-forms.md` R7 (o Admin Suite remove o marcador do texto antes de exibir,
porque o marcador termina em `§r`, que reseta formatação de cor de qualquer texto que viesse depois
dele no mesmo título).

**Risco atual:** nenhum — o `screen_title` usa `color` forçada na mão (`sonhe_grid.json:69`), então
o `§r` do marcador não tem nada pra "resetar". Vira relevante só se um dia o título usar cor
embutida no próprio texto.

---

### R10 — [informativo, não é bug] Padrão `#null` do pack não tem precedente vanilla

**Evidência:** `tile_button`, `tile_icon` e `tile_label` em `sonhe_grid.json` repetem um par de
âncoras `{"binding_name":"#null", binding_type: collection}` + `{"binding_name":"#null",
binding_type: collection_details}` em cada folha.

**Fonte:** `vanilla-colecoes.md` §0 e §6 — confirma que esse literal `#null` **não existe em nenhum
arquivo do corpus vanilla** (0 ocorrências). É convenção própria do pack. O vanilla resolve o mesmo
problema com `binding_collection_name` explícito por binding, sem essa âncora repetida.

**Ação:** nenhuma — inofensivo, documentado como "mecânica preservada" no próprio arquivo
(`sonhe_grid.json:5`). Registrado aqui só para completude do catálogo.

---

## 5. Lições do corpus vanilla e addons de terceiros (compacto)

Cada linha aponta pro relatório-fonte para detalhe. Convenção: ✅ o que fazer / ❌ o que não fazer.

| Fonte | Lição principal |
|---|---|
| `addon-ui1.md` | ✅ merge por controle de topo dentro do namespace, não por arquivo. ❌ ramos não-complementares no marcador de título (buraco onde os dois somem). |
| `addon-ui2.md` | ❌ `#form_button_length` não existe no vanilla (é `#form_button_contents`). ❌ par de bindings de marcador com buraco lógico. ✅ `resolve_sibling_scope` pra esconder moldura vazia. |
| `addon-ui3.md` | Contra-exemplo didático: acumula `grid_dimensions` + `#maximum_grid_items` + `factory` no mesmo grid — mistura de famílias que o corpus vanilla nunca faz (0/134). ✅ topologia de scroll (grid dentro de `common.scrolling_panel`) é a certa a copiar. |
| `addon-ui4.md` | ✅ `long_form` deve declarar `size` explícito no wrapper de override. ✅ layout "burro" (stack_panel + `collection_index` literal) é um fallback válido se o `grid` falhar. |
| `addon-ui5.md` | ✅ tema via `$default_button_texture` sem `\|default` sobrescreve o template do botão de forma limpa. ✅ dependência mútua RP↔BP por UUID no manifest. |
| `adminsuite-forms.md` | ✅ arquitetura multi-tela escalável: hooks por marcador + fallback = AND de todas as negações. ✅ `main_screen_content` redeclarado com tamanho real evita o colapso de `%`. ❌ nosso teste de "célula vazia" falta a guarda `'_' + texto` contra falso-positivo de string vazia. |
| `coletados-chest.md` | Todo "inventário" dentro de `server_form` é fake — é `form_buttons` normal com metadado codificado no texto do botão. Não existe drag-and-drop real nessa camada. |
| `coletados-exemplos.md` | Catálogo de referência rápida: os 4 `binding_type`, os modos de `image` (nine-slice/tile/UV/grayscale/fill), `binding_condition: "once"`. |
| `coletados-misc.md` | Confirma (via `diff` byte-a-byte) que vários arquivos coletados são vanilla puro sem alteração — baseline de comparação. |
| `coletados-serverform.md` | Comparação de 6 `server_form` reais de terceiros: nenhum usa a técnica `modifications` recomendada pela wiki oficial; todos redefinem `long_form` inteiro. `skyls` é o mais robusto (tem fallback real); `chest_ui` é o mais frágil (sem fallback nenhum). |
| `docs-tecnicos.md` | Fonte da técnica oficial de override (`modifying-server-forms.md`) e do mecanismo de grid dinâmico (`dynamic-content-generation.md`). Confirma: nem essa doc nem a de dynamic content usam a expressão "falha silenciosa" — é dedução, não afirmação literal da Mojang. |
| `docs-wiki.md` | Referência completa de propriedades/tipos de controle. `visible:false` continua sendo avaliado; `ignored:true` é o único que remove de fato da árvore (ganho de performance real). |
| `sonhe-atual.md` | Auditoria própria — achado do mundo/cache desatualizado (R3) e catálogo de riscos (base das seções 4 deste documento). |
| `sonhe-bp.md` | Auditoria própria do BP — tabela dos 14 forms, 2 telas que estouram 12 botões, gap de `dependencies`. |
| `vanilla-adaptativo.md` | Aninhar `%c`/`%cm` 5-6 níveis é padrão vanilla normal — não é a profundidade que quebra, é filho `%`/`fill` no mesmo eixo de um pai `%c` (dependência circular). |
| `vanilla-alpha.md` | Alpha nunca derruba estrutura — no máximo é clampado. Descarta a hipótese "só o alpha 0.7→0.9 quebrou a tela". |
| `vanilla-colecoes.md` | Não existe "herança de binding" no vanilla — cada controle declara `binding_collection_name` próprio. `collection_details` não é "gate", é binding independente. |
| `vanilla-common.md` | `common.panel` não existe (é confusão com `common.common_panel` ou `common.empty_panel`). `common.button` não tem textura própria — quem herda fornece os 4 estados. |
| `vanilla-grid.md` | Catálogo de 134 grids reais: `grid_dimensions` e `#maximum_grid_items` são **mutuamente exclusivos em 100% dos casos vanilla** (0/134). `#form_button_contents` é o nome real; nunca é usado com `grid`, só com `stack_panel+factory`. |
| `vanilla-labels.md` | `max_size` em Y trunca com "..."; label sem `max_size` dentro de `stack_panel 100%c` cresce livre. Base da correção do R7. |
| `vanilla-layer.md` | `layer` é relativo ao pai/escopo de irmãos, nunca global. `server_form` não tem véu preto de tela cheia por padrão. |
| `vanilla-scroll.md` | `scroll_view` só é instanciado indiretamente via `@common.scrolling_panel`; `$scrolling_content` é a única variável sem `\|default` — omiti-la deixa a área de scroll vazia sem erro. |
| `vanilla-serverform.md` | Referência autoritativa completa da árvore `server_form`/`common_dialogs`: tabela de `$vars`, ordem de bindings, nomes literais que não podem ser renomeados. Base de quase todo o catálogo da seção 4. |
| `vanilla-telas-modernas.md` | 5 telas vanilla reais com grade de tiles: padrão dominante é texto **dentro** do tile, ancorado embaixo; duas técnicas de hover (overlay branco / troca de textura). |
| `vanilla-tema.md` | `textures/ui/White` tem borda preta 2px (armadilha); `Gray.png`/`Grey.png` são **pretos puros** apesar do nome. Sintaxe de nineslice é sempre `nineslice_size` (sem underscore), sempre em `.json` sidecar. |
| `vanilla-varredura.md` | `modifications` e `nineslice_size` como propriedade inline: **0 ocorrências** em qualquer grafia no corpus vanilla — reforça que sidecar é a única forma real usada. |
| `web-cache.md` | Bug real da Mojang (MCPE-153925) sobre race condition de cache de pack — pilar de evidência da causa #2 (seção 3.2b). |
| `web-docs.md` | **Achado central deste documento** — doc oficial da Microsoft confirma que JSON UI não é cooperativo e que a disputa de pack stack nunca gera log. |
| `web-falhas.md` | Catálogo de 10 causas documentadas de "UI some sem erro" — de migração pra Ore UI a bug de configurações de pack corrigido na 1.26.20. |
| `web-github.md` | Chest-UI real no GitHub confirma a técnica de marcador em produção e o padrão de dependência RP→BP por UUID. |
| `web-mcpedl.md` | Busca negativa: nenhum relato público confirmado do sintoma exato em MCPEDL/Reddit — não é um "bug conhecido da comunidade" citável, é diagnóstico original deste projeto. |

---

## 6. Plano de correção recomendado (ordem de prioridade)

Cada item marcado quanto à chance de regressão, já que a prioridade é não quebrar o addon.

1. **[SEGURO]** Redeploy do pack no mundo/cliente `Server` (R3) — ação puramente operacional, zero
   risco de código. Fazer **antes** de qualquer outro teste, para não confundir bug de cache com bug
   de JSON.
2. **[SEGURO]** Adicionar `dependencies` no `SonheMenu_BP/manifest.json` apontando pro UUID do RP
   (R1) — mudança aditiva de 4 linhas, não altera nenhum comportamento de renderização existente,
   só passa a gerar diagnóstico quando o RP faltar.
3. **[SEGURO]** Adicionar `"size": ["100%", "100%"]` ao nó `long_form` (R4) — uma linha, alinhamento
   defensivo confirmado inofensivo pela própria análise da árvore atual (ambos os ramos já têm
   tamanho absoluto próprio).
4. **[SEGURO]** Corrigir/depreciar `ADDONS/tools/audit_ui.py` (R5) — é ferramenta de dev, não é
   carregada pelo jogo; o risco está em **não** corrigi-la (pode induzir uma "correção" futura que
   quebre o grid de verdade).
5. **[SEGURO]** Remover o teto de altura do `max_size` em `screen_body` (R7) — mudança testada
   contra o mesmo padrão vanilla confirmado (label em `stack_panel 100%c`), sem dependência
   circular.
6. **[SEGURO]** Reduzir `ITENS_POR_PAGINA` em `auction.js` e/ou paginar `abrirMinhasVendas` (R2) —
   fica inteiramente do lado do script, não toca em nenhum arquivo `.json` de UI.
7. **[SEGURO, opcional]** Unificar o `alpha` entre `grid_screen` e `list_screen` (R8) — cosmético,
   `list_screen` hoje não está em uso ativo.
8. **[SEGURO, opcional]** Remover marcador do título antes de exibir (R9) — só relevante se o título
   algum dia usar formatação de cor própria.
9. **[ARRISCADO — não fazer sem teste isolado]** Trocar `grid_dimensions [3,4]` fixo por
   `grid_rescaling_type: "horizontal"` + binding `#form_button_contents → #maximum_grid_items` para
   ganhar altura adaptativa. Motivo do alerta: o próprio histórico do repositório já reverteu uma
   tentativa de topologia de altura adaptativa que quebrou em jogo (`commit 817852b`), e nenhuma
   fonte vanilla confirma essa combinação específica funcionando com `ActionFormData` (é
   extrapolação por analogia, não cópia comprovada — `vanilla-grid.md` §8). Se for tentado, isolar
   num commit próprio, testável e revertível em 2 linhas.
10. **[ARRISCADO — não recomendado agora]** Migrar a rota de registro de `_ui_defs.json` +
    arquivo novo para o caminho vanilla direto (`ui/server_form.json`, sem `_ui_defs.json`), como
    fazem `ui1`-`ui5` e o Chest-UI real. Teoricamente reduz a superfície de "arquivo não registrado"
    (elimina a dependência do item 2b da seção 3.1/3.2), mas exigiria reescrever/copiar todo o
    conteúdo hoje herdado implicitamente do vanilla por merge de namespace — alto risco de esquecer
    algum controle e quebrar o ramo de fallback inteiro.

---

## 7. Índice remissivo — os 31 arquivos-fonte

| # | Arquivo | O que cobre |
|---|---|---|
| 1 | `addon-ui1.md` | Addon de terceiro #1 — override mínimo de `server_form` pelo caminho vanilla, sem `_ui_defs.json`; prova de merge por controle de topo. |
| 2 | `addon-ui2.md` | Addon de terceiro #2 — `stack_panel` horizontal; expõe buraco de binding não-complementar e nome errado `#form_button_length`. |
| 3 | `addon-ui3.md` | Addon de terceiro #3 — grid + scroll, mesma base do ui2; contra-exemplo de mistura `grid_dimensions`+`#maximum_grid_items`+`factory`. |
| 4 | `addon-ui4.md` | Addon de terceiro #4 — versão esquelética, mosaico manual de `stack_panel` com `collection_index`, sem `grid`. |
| 5 | `addon-ui5.md` | Addon de terceiro #5 — mesmo esqueleto do ui4 com tema completo (nine-slice, `$default_button_texture`, dependência RP↔BP por UUID). |
| 6 | `adminsuite-forms.md` | Admin Suite 1.50 — arquitetura multi-tela via hooks de marcador + fallback AND; grid dinâmico real; guarda contra string vazia. |
| 7 | `coletados-chest.md` | "Baú fake" dentro de `server_form` — técnicas de codificação de textura/durabilidade/pilha no texto do botão. |
| 8 | `coletados-exemplos.md` | Exemplos didáticos gerados por schema/ferramenta (grid, image, binding) + rascunho próprio `ex_scroll.json`. |
| 9 | `coletados-misc.md` | Arquivos diversos coletados — confirmação de vanilla puro por `diff`, downloads falhos, snippet de debug de layout. |
| 10 | `coletados-serverform.md` | Comparação lado a lado de 6 `server_form` de terceiros (easyui, yasser, skyls, tile/BedrockIslands, chest_ui) — ranking de robustez. |
| 11 | `docs-tecnicos.md` | Extração de docs técnicos da Bedrock Wiki — `modifying-server-forms`, `dynamic-content-generation`, buttons/toggles, `preserve-title-texts`, type-conversion, tabela de operadores. |
| 12 | `docs-wiki.md` | Extração da doc geral da Bedrock Wiki — tipos de controle, todas as categorias de propriedade, `alpha`/`layer`/`visible`/`ignored`, boas práticas. |
| 13 | `sonhe-atual.md` | Auditoria do próprio `SonheMenu_RP` (HEAD) — achado do mundo/cache desatualizado + catálogo de riscos estruturais. |
| 14 | `sonhe-bp.md` | Auditoria do `SonheMenu_BP` — tabela de todos os 14 forms do addon, telas que estouram 12 botões, ausência de `dependencies` pro RP. |
| 15 | `vanilla-adaptativo.md` | Layout adaptativo e dependência circular de `%c`/`%cm` no corpus vanilla — profundidade de aninhamento, padrão "fundo como pai do conteúdo". |
| 16 | `vanilla-alpha.md` | Alpha/cor/transparência no vanilla — faixa de valores, não-propagação, prova de que alpha sozinho não derruba a UI. |
| 17 | `vanilla-colecoes.md` | Bindings de coleção no vanilla — regra real de `collection`/`collection_details`, ausência do padrão `#null` do addon. |
| 18 | `vanilla-common.md` | Controles-base do namespace `common` (`common.button`, `common.common_panel`, etc.) — o que existe de fato vs. nomes presumidos. |
| 19 | `vanilla-grid.md` | Catálogo completo dos 134 grids vanilla; `#form_button_contents` vs. `#form_button_length`; `grid_dimensions` × `#maximum_grid_items` mutuamente exclusivos. |
| 20 | `vanilla-labels.md` | Truncamento de texto (`max_size` em Y = "..."), padrão de label multi-linha sem `max_size`; base do diagnóstico/correção do `screen_body`. |
| 21 | `vanilla-layer.md` | Z-order/`layer` no vanilla — relativo ao pai, nunca global; cadeia de fundos escuros de `server_form`. |
| 22 | `vanilla-scroll.md` | `scrolling_panel`/`scroll_view` no vanilla — receita de lista/grid rolável, armadilhas de tamanho, variável obrigatória `$scrolling_content`. |
| 23 | `vanilla-serverform.md` | Referência autoritativa completa de `server_form` + `common_dialogs` — árvore de controles, `$vars`, ordem de bindings, pontos de override seguros. |
| 24 | `vanilla-telas-modernas.md` | 5 telas vanilla com grade de tiles ícone+título — padrões de proporção, espaçamento, hover, posição do texto. |
| 25 | `vanilla-tema.md` | Texturas de tema (`Black`, `White`, armadilha `Gray`/`Grey`) e sintaxe real de `nineslice_size` (sempre sidecar `.json`). |
| 26 | `vanilla-varredura.md` | Varredura de propriedades diversas no corpus vanilla — confirma ausência de `modifications` e `nineslice_size` inline. |
| 27 | `web-cache.md` | Pesquisa web — cache de pack no cliente, bug real e catalogado da Mojang (MCPE-153925, race condition "unpredictable"). |
| 28 | `web-docs.md` | Documentação oficial Microsoft Learn — Pack Stacking, **Guidelines for Building Cooperative Add-Ons (achado central deste diagnóstico)**, Content Error Log. |
| 29 | `web-falhas.md` | 10 causas documentadas de JSON UI custom sumir sem erro — migração pra Ore UI, mudança de escala 1.26.0, título, merge, `_ui_defs`, cache, prioridade de packs, dependency, bug 1.26.20, binding silencioso. |
| 30 | `web-github.md` | Addons públicos reais no GitHub (Chest-UI) que sobrescrevem `server_form` — técnica confirmada em produção, dependência RP→BP por UUID. |
| 31 | `web-mcpedl.md` | Pesquisa em MCPEDL/Reddit — nenhum relato público confirmado do sintoma exato "cai pra vanilla intermitente". |

---

*Fim do diagnóstico. Nenhum arquivo em `ADDONS/SonheMenu_RP` ou `ADDONS/SonheMenu_BP` foi alterado
na produção deste documento.*
