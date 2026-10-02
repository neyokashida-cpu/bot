# Pesquisa web (GitHub): addons que sobrescrevem server_form + issues de fallback silencioso

Data da pesquisa: 2026-08-31
Objetivo: achar implementações públicas no GitHub que sobrescrevem `server_form.json`
(ActionFormData/ModalFormData) via resource pack com JSON UI custom, extrair a técnica de
"esconder vanilla / mostrar custom", dependências de manifest RP↔BP, e procurar
issues/discussions sobre fallback silencioso pro form vanilla. Buscas feitas via WebSearch
(`site:github.com` + variações) e leitura via WebFetch (github.com e raw.githubusercontent.com).

Nenhum arquivo em `ADDONS/SonheMenu_RP` ou `ADDONS/SonheMenu_BP` foi tocado nesta tarefa.

---

## 1. Documentação oficial da técnica — Bedrock Wiki (Bedrock-OSS/bedrock-wiki)

Repo: https://github.com/Bedrock-OSS/bedrock-wiki (branch `wiki`)

### 1.1 Técnica central de override
Fonte: https://raw.githubusercontent.com/Bedrock-OSS/bedrock-wiki/wiki/docs/json-ui/modifying-server-forms.md
(espelha https://wiki.bedrock.dev/json-ui/modifying-server-forms)

- **Técnica confirmada**: usar `modifications` em `RP/ui/server_form.json` pra inserir
  painéis custom dentro de `server_form_factory` (que referencia `control_ids` `long_form` e
  `custom_form`), e controlar visibilidade com **binding no texto do título** (`#title_text`)
  comparado a um marcador string, ex. prefixo `"wiki_form:"`.
- Padrão de binding pra **esconder o vanilla quando o marcador está presente**:
  ```
  "source_property_name": "((#title_text - 'wiki_form:') = #title_text)"
  ```
  (se a subtração da string marcadora não muda `#title_text`, o marcador NÃO está presente →
  form vanilla fica visível; caso contrário, esconde.)
- Painel custom usa a lógica inversa (`not (...)`) pra só aparecer quando o marcador bate.
- **Não documenta nenhum bug conhecido de fallback silencioso** nem dependências de manifest
  RP↔BP — o tutorial assume que o comportamento é determinístico desde que os bindings estejam
  certos.
- confidence: confirmado (conteúdo lido diretamente do raw.githubusercontent.com).

### 1.2 Boas práticas / por que um binding pode falhar sem erro
Fonte: https://raw.githubusercontent.com/Bedrock-OSS/bedrock-wiki/wiki/docs/json-ui/best-practices.md

- Recomenda **um único ponto de entrada** de merge por tela vanilla ("Multiple entry points
  increase failure risk if Mojang renames targeted elements") — relevante pro nosso caso: se o
  addon tiver mais de um ponto de `modifications` mexendo em `server_form`, um deles pode
  silenciosamente parar de casar com a árvore vanilla (ex. após update do jogo) sem lançar erro,
  e o resultado visual é exatamente "cai pro form vanilla".
- Recomenda usar `ignored: true` em vez de `visible: false` pra controles não usados (implica
  que controles "escondidos" via `visible` continuam ativos/computando bindings).
- confidence: confirmado.

### 1.3 Binding scope/tipos — por que uma falha de binding não gera log
Fonte: https://raw.githubusercontent.com/Bedrock-OSS/bedrock-wiki/wiki/docs/json-ui/json-ui-documentation.md

- Confirma 3 escopos de binding (`global`, `view`, `collection`) e junta pistas de que erros de
  binding **não lançam erro nem log**: `binding_name_override` ausente faz o binding "executar
  mas nunca atualizar nenhuma propriedade"; `source_control_name` incorreto (control não existe)
  "silently fails, leaving dependent elements unsynced"; mismatch de `binding_type` "produces no
  error but leaves controls invisible".
- **Isso é a explicação técnica mais direta pro nosso sintoma** ("cai silenciosamente pro form
  vanilla, sem log de erro") — é uma característica geral do sistema de binding do JSON UI, não
  um bug específico de algum addon: binding errado = elemento não aparece, sem erro em lugar
  nenhum (nem ContentLog).
- confidence: confirmado (é o texto/paráfrase direta da doc), mas é inferência nossa que isso
  *explica* o sintoma do projeto — a doc não fala de `server_form` fallback especificamente
  nesse arquivo.

### 1.4 `preserve-title-texts.md` (padrão `property_bag`)
Fonte: https://raw.githubusercontent.com/Bedrock-OSS/bedrock-wiki/wiki/docs/json-ui/preserve-title-texts.md

- Documenta um problema **adjacente** à técnica de marcador-no-título: como a mesma tela pode
  ter vários componentes reagindo ao `#title_text` global, sem isolamento (`property_bag`) cada
  atualização de título faz *todos* os componentes reavaliarem a condição, criando risco de
  conflito entre instâncias/componentes que dependem do mesmo campo de texto pra decidir estado.
  Não é sobre truncamento/corrupção de texto, é sobre **múltiplos consumidores do mesmo sinal de
  título colidindo** — relevante se o addon usa `#title_text` tanto pro marcador
  custom-vs-vanilla quanto pra outro propósito (ex. paginação) no mesmo form.
- confidence: confirmado (conteúdo lido), mas é sobre um problema de arquitetura relacionado,
  não uma citação direta do bug "fallback silencioso".

---

## 2. Implementação pública real — Chest-UI (Herobrine643928/LeGend077)

Repo: https://github.com/Herobrine643928/Chest-UI (166 estrelas, mantido por Herobrine64 e
LeGend077) — reskina ActionFormData pra parecer um baú/fornalha estilo Java, via Script API +
JSON UI, sem entidades.

### 2.1 Técnica de override
Fonte: https://raw.githubusercontent.com/Herobrine643928/Chest-UI/main/RP/ui/chest_server_form.json

- Mesmo padrão da doc oficial: binding de visibilidade baseado em subtração de string sobre
  `#title_text`:
  ```json
  {
    "binding_type": "view",
    "source_property_name": "(not ((#title_text - $condition) = #title_text))",
    "target_property_name": "#visible"
  }
  ```
- Usa `collection_name: form_buttons` pra popular os "slots" do baú (grid), decodificando
  textura/durabilidade/tamanho de pilha embutidos no texto do botão — mesmo padrão achado nos
  arquivos locais do projeto (`docs/json-ui/fontes/coletados-chest.md` já documenta isso a
  partir de arquivos coletados localmente, não do GitHub; aqui é a mesma técnica confirmada na
  fonte pública original).
- confidence: confirmado (JSON lido do raw.githubusercontent.com).

### 2.2 Dependency entre RP e BP no manifest
Fontes:
- https://raw.githubusercontent.com/Herobrine643928/Chest-UI/main/RP/manifest.json
- https://raw.githubusercontent.com/Herobrine643928/Chest-UI/main/BP/manifest.json

- **RP declara dependency explícita pro UUID do módulo `data` do BP**: RP `dependencies` →
  `{"uuid": "792bede7-337e-41e9-09c3-dd20395d1263", "version": [1,5,0]}` = mesmo UUID do pack BP.
  BP por sua vez depende de `@minecraft/server` (1.18.0) e `@minecraft/server-ui` (1.3.0).
- Confirma que a prática pública padrão é RP→BP dependency por UUID (não é só BP→RP), garantindo
  que o RP só seja considerado "completo" com o BP correspondente presente — se um dos dois pack
  estiver desatualizado/ausente/com UUID divergente, o comportamento esperado (não documentado
  explicitamente como erro visível) é o form abrir sem a skin custom.
- confidence: confirmado (manifests lidos diretamente).

### 2.3 Issues relacionadas a "UI não aparece"
Fonte: https://github.com/Herobrine643928/Chest-UI/issues/51 ("UI Not showing", fechada)

- Relato: `ChestFormData` não mostra nada (remove HUD/sidebar mas não renderiza UI); só a
  variante "large" funcionava, outras variantes de tamanho de grid não apareciam; usuário na
  versão 26.31 do Chest-UI.
- **Não consegui extrair via WebFetch os comentários/causa raiz/fix** (a página só devolveu
  título+corpo da issue, sem thread). Não dá pra confirmar se a causa foi binding de
  visibilidade quebrado, incompatibilidade de versão do Minecraft, ou outra coisa.
- confidence: confirmado que a issue existe e o sintoma é "grid não aparece" (não
  necessariamente = cair pro vanilla, já que Chest-UI não tem "vanilla list" por trás — o
  ActionFormData original já é substituído); **provável, não confirmado**, que seja parecido com
  o bug do nosso projeto — recomendo abrir a issue diretamente no navegador se quiser os
  comentários completos, já que o WebFetch não trouxe a thread.

### 2.4 Risco de plataforma documentado em fonte adjacente
Fonte: https://raw.githubusercontent.com/boredape874/mcbejsonuimasterAI/main/docs/47-custom-auxid-and-form-progress.md
(repo: https://github.com/boredape874/mcbejsonuimasterAI — não é addon, é doc/notas técnicas
sobre engenharia reversa de JSON UI de server forms)

- Documenta uma técnica adjacente (progress bar embutida via prefixo numérico no corpo do form,
  extraído via binding aritmético `(#form_text * 1)`), e explicitamente avisa: **"PC works as
  documented. However, Android may diverge in some cases, and iOS may break this approach
  completely. Console behavior is unconfirmed."**
- **Achado relevante pro projeto**: é uma fonte (não oficial, doc de terceiro) alegando que
  técnicas de binding baseadas em manipulação de string/número no título/corpo do form têm
  **comportamento divergente por plataforma**, podendo "quebrar completamente" em iOS. Isso é
  compatível com um cenário de fallback intermitente/silencioso que aparece só em alguns
  dispositivos.
- confidence: suspeita (é uma nota de um repo de terceiro não-oficial, sem link pra bug tracker
  da Mojang ou reprodução documentada — trate como hipótese a testar, não como fato
  estabelecido).

---

## 3. Outros repositórios relevantes verificados

| Repo | O que é | Relevância pro tema |
|---|---|---|
| [LeGend077/json-ui-examples](https://github.com/LeGend077/json-ui-examples) | Coleção de exemplos de JSON UI | Confirma namespace `server_form` com `long_form`/`custom_form` pra propriedades tipo `$show_close_button: false`; tem exemplo de "Java-like Chest UI in Server Forms" e "Custom NPC Screen with Server Form Layout". confidence: confirmado (README lido). |
| [Mojang/bedrock-samples](https://github.com/Mojang/bedrock-samples/blob/main/resource_pack/ui/server_form.json) | Fonte oficial vanilla do `server_form.json` | Baseline pra qualquer override — confirma estrutura `server_form_factory` → `long_form`/`custom_form`, painéis scrolláveis, `form_buttons` como collection. confidence: confirmado. |
| [Majorum-eu/TabulaUI-API](https://github.com/Majorum-eu/TabulaUI-API) | API de menus de terceiro (não é override JSON UI de resource pack) | **Não relevante** — não sobrescreve `server_form.json`, é builder pattern de plugin server-side (parece Java/BDS plugin API). Sem menção a fallback. |
| [GoldRush-developpement/EasyUIBuilder](https://github.com/GoldRush-developpement/EasyUIBuilder) | Ferramenta que gera `_ui_defs.json`/`server_form.json` automaticamente | README não documenta a técnica de binding nem bugs de fallback — é só descrito como "auto-generation". Não deu pra extrair código-fonte real via WebFetch. confidence: suspeita/inconclusivo. |
| kejonaMC/CrossplatForms, kejonaMC/BedrockFormShop, Yahir-AR/FormAPI-PMMP, NoteLand/WDForms, w1zardz/formapi-craft | Bibliotecas/plugins server-side (Java, PocketMine-MP, Geyser) | **Não relevantes** — geram forms nativos via protocolo, não usam JSON UI de resource pack, não têm o padrão "esconder vanilla/mostrar custom". |

---

## 4. Busca por issues/discussions com termos específicos

Buscas feitas: `"server_form" bedrock "falls back" OR "fallback"`, `"json ui" bedrock
server_form silently fails OR "not showing"`, `"ActionFormData" "custom ui" "not working" OR
"silently" bedrock github issue`, `site:github.com bedrock-wiki json-ui issues discussions
server_form bug`.

- **Nenhuma issue/discussion no GitHub foi encontrada usando literalmente os termos "server_form
  not showing", "ActionFormData custom ui not working" ou "json ui silently fails"** aplicados
  ao ecossistema Bedrock/JSON UI — os resultados que bateram nesses termos eram de projetos sem
  relação (ex. um issue de RPC framework genérico `gsd-build/gsd-2#447` sobre
  `ctx.ui.custom()`, não é Minecraft).
- A única issue diretamente no tema (grid/form não aparecendo num addon que reskina
  `server_form`) foi a #51 do Chest-UI, coberta na seção 2.3.
- Não encontrei nenhuma issue aberta no próprio `Bedrock-OSS/bedrock-wiki` sobre bug de
  `server_form` (a busca só retornou os arquivos de doc, não issues).
- confidence: busca não encontrou nada além do já citado — não invento resultado onde não achei.

---

## 5. Síntese pro projeto

1. A técnica pública padrão (doc oficial + Chest-UI real) é **idêntica** à esperada: modificar
   `server_form_factory`/`long_form`/`custom_form` via `modifications`, e usar um **binding de
   subtração de string sobre `#title_text`** como flag custom-vs-vanilla. Não existe uma segunda
   técnica alternativa documentada publicamente (ex. nenhuma fonte usa side-channel via item/NBT
   em vez do título).
2. **Não existe bug documentado, oficial ou comunitário, chamado/catalogado como "fallback
   silencioso pro form vanilla"** no ecossistema JSON UI. O que existe é a característica geral
   do binding system do JSON UI (seção 1.3): binding mal configurado = controle não aparece,
   **sem log, sem erro, em lugar nenhum** — isso por si só já explica por que o sintoma do
   projeto não gera nada no ContentLog. Não é um "bug" no sentido de defeito reportável, é o
   comportamento normal (e mal documentado) do binding system.
3. Fonte de terceiro não-oficial (mcbejsonuimasterAI, seção 2.4) levanta hipótese de
   **divergência de plataforma** (PC ok / Android diverge / iOS pode quebrar) pra técnicas de
   binding aritmético sobre texto do form — vale testar em dispositivos diferentes se o fallback
   do projeto for intermitente por device.
4. Confirmado nos manifests reais do Chest-UI que a prática pública é **RP depender do BP por
   UUID** (não o inverso) — vale conferir se `ADDONS/SonheMenu_RP/manifest.json` tem
   `dependencies` apontando pro UUID do `SonheMenu_BP` (fora do escopo desta tarefa editar, só
   comparar).
5. A issue #51 do Chest-UI ("UI Not showing") é o achado mais próximo de um relato real de
   "grid custom não aparece", mas o WebFetch não conseguiu extrair a thread de comentários —
   recomenda-se abrir manualmente para ver causa raiz/fix se for perseguir essa pista.

---

## Fontes citadas (URLs exatas)

- https://raw.githubusercontent.com/Bedrock-OSS/bedrock-wiki/wiki/docs/json-ui/modifying-server-forms.md
- https://raw.githubusercontent.com/Bedrock-OSS/bedrock-wiki/wiki/docs/json-ui/best-practices.md
- https://raw.githubusercontent.com/Bedrock-OSS/bedrock-wiki/wiki/docs/json-ui/json-ui-documentation.md
- https://raw.githubusercontent.com/Bedrock-OSS/bedrock-wiki/wiki/docs/json-ui/preserve-title-texts.md
- https://github.com/Herobrine643928/Chest-UI
- https://raw.githubusercontent.com/Herobrine643928/Chest-UI/main/RP/ui/chest_server_form.json
- https://raw.githubusercontent.com/Herobrine643928/Chest-UI/main/RP/manifest.json
- https://raw.githubusercontent.com/Herobrine643928/Chest-UI/main/BP/manifest.json
- https://github.com/Herobrine643928/Chest-UI/issues/51
- https://raw.githubusercontent.com/boredape874/mcbejsonuimasterAI/main/docs/47-custom-auxid-and-form-progress.md
- https://github.com/LeGend077/json-ui-examples
- https://raw.githubusercontent.com/LeGend077/json-ui-examples/main/README.md
- https://github.com/Mojang/bedrock-samples/blob/main/resource_pack/ui/server_form.json
- https://github.com/Majorum-eu/TabulaUI-API
- https://github.com/GoldRush-developpement/EasyUIBuilder
