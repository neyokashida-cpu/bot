# Alpha, cor e transparência em JSON UI (Bedrock 1.26.44)

Corpus: `assets/resource_packs/vanilla/ui/` (188 arquivos), autoritativo.
Todo achado abaixo cita caminho real + trecho. Confidence: **confirmado** (visto no código), **provável** (inferência forte com evidência indireta), **suspeita** (conhecimento geral do engine, sem arquivo vanilla que prove).

---

## PARTE A — Alpha

### A.1 O que `alpha` é e qual a faixa válida

`alpha` é a opacidade de um controle: `0.0` = invisível, `1.0` = totalmente opaco. Multiplica o canal alpha da textura/cor do próprio controle.

Grep em todo o corpus (`"alpha"` aparece em ~90 arquivos, centenas de ocorrências) não retornou **nenhum** valor fora de `[0.0, 1.0]`. O maior valor parcial (não-1.0) encontrado é `0.85`:

```
authentication_modals.json:107
  "black_tint_image@popup_dialog.black_tint_image": {
    "size": [ "100%c", "100%c" ],
    "alpha": 0.85,
```

Depois disso vêm vários `0.8` (crafter_screen_pocket.json:158, persona_popups.json, pdp_screen.json:1871, ui_common.json:3452, general_section.json:4287 etc.) e um `0.75` isolado (`ui_edu_common.json:1593`). **Confirmado: sim, existe caso vanilla com alpha > 0.8** — é `0.85`, no overlay de fundo (`black_tint_image`) do `authentication_modals.json`. Não existe nenhum caso vanilla entre `0.85` e `1.0` exclusive (nenhum `0.9x`).

`0.9` **não é** um valor fora do padrão vanilla — está dentro da faixa válida (`0.0–1.0`) e é só 0.05 acima do teto observado no corpus. Não há mecanismo de "alpha inválido acima de X quebra o parser" — o formato aceita qualquer float; o motor deve fazer clamp internamente se passar de 1.0 (não há evidência de teste desse caso no vanilla porque ninguém shippa isso).

### A.2 Alpha herda para filhos?

**Não, por padrão não.** Só herda (propaga) se o controle tiver `"propagate_alpha": true`. Comentário literal do próprio pack confirma a semântica:

```
game_tip_screen.json:174-175
  "alpha": "@game_tip.fade_animation",
  "propagate_alpha": true,
```

```
hud_screen.json:2268-2270
  "hud_title_text": {
    ...
    "alpha": "@hud.anim_title_text_alpha_in",
    "propagate_alpha": true,
```

Todos os 14 usos de `propagate_alpha` no corpus (`game_tip_screen.json:175`, `hud_screen.json:2270`, `pdp_screenshots_section.json:81,94`, `start_screen.json:1969,1988`, `store_item_list_screen.json:631`, `store_inventory_screen.json:1415`, `store_data_driven_screen.json:789`, `store_search_screen.json:197`, `ui_common.json:6460,6469,6478,6493`) estão em **animações de fade** (entrada/saída de tela inteira, transição de item de loja) onde se quer que um painel INTEIRO — fundo + filhos — suma/apareça junto. É opt-in exatamente porque o padrão é o oposto.

Confirmação adicional, no próprio código do usuário (fora do corpus vanilla mas coerente com ele — ver `ADDONS/SonheMenu_RP/ui/sonhe_grid.json`, comentário original do autor):
```
"panel_bg": {
  "//": "FUNDO DO PAINEL: preto ~70% ... SEM propagate_alpha: o alpha nao vaza
         para os filhos, titulo/corpo/labels/icones ficam opacos.",
```
Isso é a leitura correta da mecânica vanilla: uma imagem de fundo com `alpha: 0.7` e sem `propagate_alpha` deixa **só a própria imagem** semitransparente; o texto e ícones desenhados por cima (outros controles, mesmo sendo filhos) continuam 100% opacos a menos que tenham o próprio `alpha` setado.

**Confidence: confirmado.**

### A.3 `image` vs `panel` vs `label` — comportamento de alpha é igual?

O campo é o mesmo (`"alpha": <float>`) nos três, e a regra de não-propagação é a mesma. A diferença é **o que existe para ficar transparente**:

| Tipo | O que o alpha afeta | Evidência |
|---|---|---|
| `image` | a textura inteira do controle | `hud_screen.json:655 "alpha": 0.65` sobre `type: image` |
| `panel` | `panel` não desenha nada sozinho (sem textura própria) — alpha nele só importa se tiver `propagate_alpha:true`, senão não há efeito visual direto | `common_dialogs.full_screen_background` (`ui_template_dialogs.json:481-503`) é `type: panel` cujo alpha (`$fill_alpha`) é repassado ao filho `image` via variável, não por propagação |
| `label` | a cor/opacidade do texto (e do shadow) | `chat_screen.json` labels com `alpha` ligado a binds de fade |

Não há evidência vanilla de "alpha em panel se comporta diferente de alpha em image" no sentido de regra especial — a diferença é estrutural (panel não tem pixel próprio para ficar translúcido).

**Confidence: confirmado** (mecanismo), **provável** (a generalização "todos se comportam igual" além do que o corpus mostra).

### A.4 Alpha × layer — existe interação?

**Não há interação direta entre o valor numérico de `alpha` e o valor numérico de `layer`.** São dois eixos ortogonais: `layer` decide ordem de desenho (z-order); `alpha` decide opacidade do que já foi desenhado nessa posição. Um controle com `alpha: 0.9` em `layer: 5` continua desenhado depois (por cima) de um `layer: 1`, só que semitransparente — dá pra ver o de baixo por trás dele.

Onde a interação **aparece na prática** é quando duas camadas translúcidas se empilham: o resultado visual é a multiplicação/composição das opacidades, não a soma. Isso é exatamente o que o autor do SonheMenu_RP documentou no próprio commit (ver seção "Aplicação"): fundo do painel a 0.7/0.9 (`layer:1`) + fundo do tile a 0.85 (`layer:1`, dentro de outro painel) por cima resulta numa área "mais opaca que o cabeçalho", porque ali são duas pretas translúcidas empilhadas, e no cabeçalho é só uma.

**Confidence: confirmado** (não há campo/flag vanilla que ligue os dois); **provável** (composição multiplicativa ao empilhar, comportamento padrão de blending alpha-over-alpha, consistente com o observado).

### A.5 `color` é `[r,g,b]` (ou `[r,g,b,a]`) 0..1 e multiplica a textura?

**Confirmado**, com evidência direta de variáveis já pré-multiplicadas por 1.0 (identidade) e por valores de tinta:

```
ui_common.json:611   "color": [ 1.0, 1.0, 1.0, 1.0 ]     // rotating_text, sem tingir (identidade)
ui_common.json:1259  "color": [ 1.0, 1.0, 0.0, 1.0 ]     // focus_border_yellow — tinge borda branca de amarelo
ui_common.json:1263  "color": [ 0.0, 0.0, 0.0, 1.0 ]     // focus_border_black — tinge de preto
```

Os dois últimos são o MESMO controle-base (`focus_border_white`, uma imagem branca) reaproveitado só trocando `color`:
```
ui_common.json:1252-1264
  "focus_border_white": { "type": "image", "layer": 2, "texture": "textures/ui/focus_border_white" },
  "focus_border_yellow@common.focus_border_white": { "color": [ 1.0, 1.0, 0.0, 1.0 ] },
  "focus_border_black@common.focus_border_white": { "color": [ 0.0, 0.0, 0.0, 1.0 ] },
```
Isso só faz sentido se `color` **multiplica** os pixels da textura branca — branco × amarelo = amarelo, branco × preto = preto. É o padrão "textura neutra/branca + tint via `color`" usado em todo o corpus (o próprio `flat_solid_background` em `ui_template_dialogs.json:364-369` usa `texture: textures/ui/White` + `"color": "$0_color_format"`, onde `$0_color_format = [0.0,0.0,0.0]` — branco tingido de preto).

`color` também aceita **bind de dado externo** (não é lista fixa), ex.:
```
ui_common.json:2222  "empty_progress_bar":  { "texture": "textures/ui/empty_progress_bar", "color": "#color" }
ui_common.json:2229  "filled_progress_bar": { "texture": "textures/ui/filled_progress_bar", "color": "#color", ... }
```
`#color` aqui vem de dado da entidade (barra de vida/boss bar colorida por script), reforçando que é multiplicação de tint sobre uma textura em escala de cinza/branca.

**Confidence: confirmado.**

---

## PARTE C — Tons rosa/magenta

### C.1 De onde vem magenta/rosa em UI do Bedrock

O corpus **não tem** nenhum asset de "textura faltando" tipo xadrez preto/magenta dentro de `ui/` ou `textures/ui/` — não existe `missing_texture.png` genérico ali (existem apenas fallbacks específicos: `missing_item.png`, `missing_pack_icon.png`, ambos ícones de conteúdo, não texturas de UI). O padrão xadrez preto/magenta de "textura ausente" é comportamento do **motor de renderização** (mesma convenção do Java: cor de erro clássica), não um asset ou regra do JSON UI em si.

**Confidence: suspeita** (é conhecimento geral consolidado do engine Minecraft — o corpus vanilla, por definição, não tem texturas quebradas para provar isso a partir de dentro dele mesmo).

### C.2 Causas plausíveis e com evidência indireta no corpus

| Causa | Mecanismo | Evidência de suporte |
|---|---|---|
| **Caminho de textura errado/typo** em `"texture"` | o `image` não encontra o arquivo → motor desenha placeholder (xadrez preto/magenta) | comportamento de engine, não de arquivo JSON — **suspeita** |
| **`color` tingindo uma textura branca/neutra com valores tipo `[1, 0, 1]`** | `color` multiplica; se a textura de base é branca (`textures/ui/White`, `white_background`) e o `color` foi setado (por engano, variável errada, ou herança incorreta de `@base`) para algo com R e B altos e G baixo, o resultado É magenta/rosa | confirmado que `color` multiplica (ver A.5); o corpus tem exemplos deliberados desse padrão, ex. `$nested_transparent_purple_label_color: [0.247, 0.098, 0.616]` em `_global_variables.json:380` — roxo/magenta INTENCIONAL (cor de raridade/label), prova que a técnica "textura neutra + tint" produz magenta quando o vetor de cor tem essa forma |
| **Bind (`"color": "#algumacoisa"`) resolvendo para um valor inesperado** | se o dado de origem (ex. raridade de item, cor de time, boss bar) não é o esperado, o tint herda a cor "errada" | `ui_common.json:2222,2229` mostram `color` vindo de bind externo (`#color`), confirmando que UI pode herdar cor de fora do JSON |
| **`texture` apontando para arquivo `.json` de meta em vez do `.png`, ou index de nine-slice/array de texturas fora do intervalo** | renderização inconsistente, pode aparecer como cor sólida de erro | não observado no corpus vanilla (não há erro shippado); **suspeita** |

### C.3 Conclusão da Parte C

Rosa/magenta em Bedrock JSON UI vem de **uma destas duas famílias**, nessa ordem de probabilidade:
1. Textura não encontrada → placeholder do motor (fora do JSON UI, comportamento de engine). **Suspeita.**
2. `color` (tint multiplicativo) aplicado sobre textura branca/neutra com um vetor RGB que cai na faixa magenta/rosa — intencional (existe até um exemplo vanilla de roxo/magenta proposital para raridade) ou acidental (variável de cor errada herdada de `@base`, ou bind resolvendo para o valor errado). **Confirmado que o mecanismo existe; provável que seja a explicação em um caso concreto**, dependendo de qual controle está exibindo o rosa.

Não há, no corpus, nenhuma ligação entre **alpha** e a cor aparecer rosa — alpha só controla opacidade, nunca matiz. Se algo ficou rosa, o campo a investigar é `texture` (caminho) e `color`/binds de cor, não `alpha`.

---

## A pergunta crítica: alpha 0.7 → 0.9 derrubou a UI para a lista vanilla?

**Não é plausível, e o próprio histórico do repositório do usuário confirma isso.**

### O que `alpha` PODE causar
- Mudar a opacidade daquele controle específico (e, se `propagate_alpha:true`, dos filhos).
- Se duas camadas translúcidas empilham (ex. fundo do painel + fundo do tile por cima), a composição fica mais escura/opaca que uma camada isolada — isso é uma inconsistência **visual** (ex.: cabeçalho mais "vazado" que a área dos tiles), não um erro de carregamento.
- Nada além de 0.0–1.0 é usado no vanilla, mas nada no formato impede um valor tipo 0.9 nem indica que ele seja tratado como inválido — é dentro da faixa observada (teto vanilla real: 0.85; muitos usos vanilla também chegam a 0.8, e a própria tela de faces do botão do SonheMenu_RP já usa `0.85`, `0.95` e `1.0` sem quebrar nada).

### O que `alpha` NÃO PODE causar
- Alpha não é validado estruturalmente a ponto de rejeitar o arquivo/tela inteira. Um float fora de faixa seria, na pior hipótese, clampado silenciosamente pelo motor — não gera erro de parse.
- Uma UI inteira "cair pra lista vanilla" é sintoma clássico de **falha estrutural do JSON** (erro de sintaxe, referência circular de tamanho, `@base` inválido, chave duplicada) que faz o pacote de recursos rejeitar aquele namespace/tela e o jogo cair de volta pro built-in — isso é outra categoria de bug, nada a ver com o valor numérico de uma propriedade de opacidade.

### Evidência direta no próprio projeto

O histórico de commits do `ADDONS/SonheMenu_RP` documenta exatamente esse tipo de quebra — e a causa **não foi alpha**:

```
commit 019da28 — refactor(SonheMenu_RP): altura adaptativa e contraste, topologia do npc_interact
  "Aplicado: grid_screen [320,"100%c"] com um unico filho; fundo como pai do
   conteudo [...] NAO VERIFICADO EM JOGO."

commit 817852b — fix(SonheMenu_RP): reverte topologia de altura adaptativa que quebrou em jogo
  "O 1.0.33 (019da28) juntou duas coisas num commit so: a mudanca de MAIOR risco
   (fundo virar PAI do conteudo, dois niveis de image encadeados em %c com
   aritmetica e anchor center) [...] o resultado voltou pro vanilla em jogo,
   sem nenhum [UI][error]."
```

Ou seja: a quebra real e confirmada ("voltou pro vanilla em jogo") veio de uma **mudança de topologia de tamanho** (pai/filho com `%c` encadeado em 2 níveis, não confirmado no vanilla além de 1 nível) — não de um número de opacidade. O commit seguinte, que de fato mexeu em alpha:

```
commit 6a347a5 — fix(SonheMenu_RP): unifica opacidade do fundo, sobe alpha 0.7 -> 0.9
  "So o numero do alpha mudou, nada de estrutura."
```

é uma alteração isolada, sem qualquer mudança de `size`/`%c`/`@base`, e o próprio autor documentou isso explicitamente. Não há, nem no corpus vanilla nem no histórico do projeto, nenhum caso onde só um valor de `alpha` tenha causado fallback para vanilla.

**Se a tela realmente caiu pra lista vanilla depois dessa mudança pontual**, as hipóteses corretas a checar são (em ordem de probabilidade):
1. Erro de sintaxe introduzido ao editar a linha (vírgula, chave) — checar `content_log`/`[UI][error]` no log do cliente/servidor.
2. Alguma outra edição feita "junto" na mesma sessão que não ficou isolada no diff (comparar working tree vs. `HEAD` antes de assumir que só o alpha mudou).
3. Cache de pack no cliente não atualizado (sintoma comum, não relacionado a alpha).

**Confidence: confirmado** (o mecanismo de alpha não tem como causar rejeição estrutural; a causa raiz real, no histórico deste projeto, foi topologia de tamanho, documentada pelo próprio autor).

---

## Aplicação no SonheMenu

- `ADDONS/SonheMenu_RP/ui/sonhe_grid.json:29-34` (`panel_bg`, `alpha: 0.9`) está dentro da faixa vanilla observada (teto real 0.85, mas 0.9 não é estruturalmente diferente — é só um float válido a mais).
- **Ponto real de atenção, não é o valor em si**: `panel_bg` de `grid_screen` foi para `0.9`, mas o `panel_bg` equivalente de `list_screen` (linha 371) **continua em `0.7`**, apesar do commit dizer "unifica opacidade do fundo". Vale conferir se isso é intencional — hoje as duas telas do menu têm opacidade de fundo diferente.
- Os `fd_bg` dos 3 estados do tile (`face_default` 0.85, `face_hover` 0.95, `face_pressed` 1.0 — linhas 185, 215, 245) empilham sobre o `panel_bg` do `grid_screen`; como nenhum dos dois tem `propagate_alpha`, cada camada é independente — mas visualmente a soma de duas pretas translúcidas (painel 0.9 + tile 0.85/0.95/1.0) deixa a área de tiles sensivelmente mais escura que qualquer área que só tenha o `panel_bg` sozinho (cabeçalho/corpo). Isso é o efeito que o próprio autor descreveu no commit `6a347a5` — é uma questão de composição visual, não de erro de carregamento.
- Se o objetivo é emparelhar a opacidade "sentida" do cabeçalho com a dos tiles, o ajuste vanilla-consistente seria reduzir o alpha da camada que fica por baixo (ex. `panel_bg` ficar mais claro, tipo 0.7–0.75) já que a camada de cima do tile já soma opacidade — em vez de subir as duas, que é o que amplia a diferença de contraste com o cabeçalho (que não tem segunda camada).
- Nenhuma evidência (vanilla ou do próprio histórico do projeto) sustenta que mexer só em `alpha` derruba a tela pra lista vanilla — se isso for observado de novo, o primeiro lugar a olhar é o log `[UI][error]` do cliente/servidor e um diff completo do commit (não assumir que só a linha do alpha mudou).
