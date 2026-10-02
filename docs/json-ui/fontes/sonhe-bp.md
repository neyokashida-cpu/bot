# Auditoria SonheMenu_BP — origem do fallback pra lista vanilla

Escopo: `ADDONS/SonheMenu_BP/manifest.json` + todos os arquivos em `scripts/`
(main.js, menu.js, auction.js, casa.js, configuracoes.js, conquistas.js,
dados_jogador.js, diario.js, estatisticas.js, inventario_resumo.js).
Somente leitura — nenhum arquivo foi alterado.

Cliente alvo: 1.26.44. Marcador esperado no título: `§d§r§e§a§m§r`
(constante `MARCADOR_GRADE`, `menu.js:26`). Grid do RP: `grid_dimensions
[3,4]` = 12 slots.

---

## 1) Tabela de todos os ActionFormData/forms do addon

| # | Menu/tela | Função — arquivo:linha | Marcador? | Título literal (concatenado) | Nº de botões |
|---|---|---|---|---|---|
| 1 | **Ver anúncios** (página cheia, com paginação nos dois sentidos) | `abrirVerAnuncios` — `auction.js:390-404` | Sim | `§d§r§e§a§m§r§dVer anúncios (N/M)§r` | **até 13** (10 itens + "Página anterior" + "Próxima página" + "Voltar") |
| 2 | **Minhas vendas** (com anúncios do vendedor) | `abrirMinhasVendas` — `auction.js:788-794` | Sim | `§d§r§e§a§m§r§dMinhas vendas§r` | **N + 1, sem teto** (1 botão por anúncio ativo do vendedor + "Voltar" — **não há paginação aqui**) |
| 3 | Menu principal | `abrirMenuPrincipal` — `menu.js:269-277` | Sim | `§d§r§e§a§m§r§dSONHE§r` | 9 (8 páginas de `PAGINAS` + "Fechar") |
| 4 | Auction House (submenu) | `abrirAuctionHouse` — `auction.js:326-333` | Sim | `§d§r§e§a§m§r§dAuction House§r` | 4 |
| 5 | Minha Casa (casa já definida) | `abrirCasa` — `menu.js:160-171` | Sim | `§d§r§e§a§m§r§dMinha Casa§r` | 4 |
| 6 | Minha Casa (sem casa definida) | `abrirCasa` — `menu.js:160-171` | Sim | idem | 3 |
| 7 | Configurações | `abrirConfiguracoes` — `menu.js:200-213` | Sim | `§d§r§e§a§m§r§dConfigurações§r` | 3 |
| 8 | Páginas secundárias (Perfil / Status / Diário / Inventário) | `abrirPaginaSecundaria` — `menu.js:254-259` | Sim | `§d§r§e§a§m§r§d{titulo}§r` | 2 |
| 9 | Conquistas | `abrirConquistas` — `conquistas.js:143-147` | Sim | `§d§r§e§a§m§r§dConquistas§r` | 2 |
| 10 | Ver anúncios (lista vazia) | `abrirVerAnuncios` — `auction.js:372-375` | Sim | `§d§r§e§a§m§r§dVer anúncios§r` | 1 |
| 11 | Minhas vendas (vazio) | `abrirMinhasVendas` — `auction.js:775-778` | Sim | `§d§r§e§a§m§r§dMinhas vendas§r` | 1 |
| 12 | Detalhe do anúncio | `abrirDetalheAnuncio` — `auction.js:464` | **Não** (é `MessageFormData`, não `ActionFormData`) | `"Detalhe do anúncio"` | 2 (`button1`/`button2`, não é grid) |
| 13 | Cancelar anúncio | `confirmarCancelamento` — `auction.js:813-817` | **Não** (`MessageFormData`) | `"Cancelar anúncio"` | 2 (`button1`/`button2`) |
| 14 | Anunciar item | `abrirAnunciarItem` — `auction.js:611-615` | **Não** (`ModalFormData`) | `"Anunciar item"` | N/A — campos de texto/dropdown, sem `.button()` |

Confidence: **confirmado** (leitura direta do código, contagem manual de cada `.button()`/loop).

---

## 2) CRÍTICO — algum menu passa de 12 botões?

**Sim, dois.** Ordenados do maior pro menor nº de botões:

1. **`abrirMinhasVendas` (`auction.js:788-810`) — sem teto, o pior caso.**
   Diferente de `abrirVerAnuncios`, esta função **não fatia a lista** com
   `ITENS_POR_PAGINA` — itera `meus` (todos os anúncios ativos daquele
   vendedor) inteiro num único `for`:
   ```js
   const form = new ActionFormData().title(`${MARCADOR_GRADE}§dMinhas vendas§r`).body("Escolha um anúncio pra cancelar.");
   for (const dados of meus) {
       const nome = nomeDeExibicao(dados);
       const status = dados.expiraEm < agora ? "expirado" : "ativo";
       form.button(`${nome}\n${dados.preco} moedas (${status})`, iconePorCategoria(dados.item.typeId));
   }
   form.button("Voltar", ICONE_PLACEHOLDER);
   ```
   (`auction.js:788-794`). Qualquer vendedor com **12 ou mais** anúncios
   próprios ativos gera 13+ botões. `AUCTION_HOUSE.md` fala em teto de
   ~200 anúncios **no total do servidor**, não por vendedor — nada no
   código impede um único jogador de acumular mais de 11 anúncios. Confidence: **confirmado**.

2. **`abrirVerAnuncios` — página cheia com paginação nos dois sentidos**
   (`auction.js:390-404`):
   ```js
   for (const dados of itensPagina) { // até ITENS_POR_PAGINA = 10
       ...
       form.button(`${nome}\n${dados.preco} moedas - ${dados.vendedorNomeMinecraft} (${restante})`, iconePorCategoria(dados.item.typeId));
   }
   const temAnterior = paginaAtual > 0;
   const temProxima = paginaAtual < totalPaginas - 1;
   if (temAnterior) form.button("Página anterior", ICONE_PLACEHOLDER);
   if (temProxima) form.button("Próxima página", ICONE_PLACEHOLDER);
   form.button("Voltar", ICONE_PLACEHOLDER);
   ```
   Numa página do meio (não a primeira nem a última, exige `totalPaginas
   >= 3` e a página cheia com 10 anúncios ativos), o total é
   `10 + 1 (anterior) + 1 (próxima) + 1 (Voltar) = 13` botões. Na primeira
   ou última página o total fica em 12 (no limite, não estoura). Confidence: **confirmado**.

Todos os outros forms do addon ficam em **9 botões ou menos** (menu
principal = 9; ver tabela acima). Confidence: **confirmado**.

---

## 3) Existe caminho que monta o form SEM o marcador?

**Para `ActionFormData`: não.** Os 9 pontos de construção de
`ActionFormData` do addon (`menu.js:166`, `menu.js:208-209`,
`menu.js:255-256`, `menu.js:269`, `conquistas.js:143-144`,
`auction.js:327-328`, `auction.js:372-373`, `auction.js:390-391`,
`auction.js:775-776`, `auction.js:788`) **todos** interpolam
`MARCADOR_GRADE` no `.title()` — confirmado por grep de
`new ActionFormData` + `.title(` no diretório inteiro (nenhuma ocorrência
sem o marcador). Confidence: **confirmado**.

**Só existem 3 pontos sem marcador, e nenhum é `ActionFormData`:**
- `abrirDetalheAnuncio` (`auction.js:464`) — `MessageFormData`, título
  literal `"Detalhe do anúncio"`.
- `confirmarCancelamento` (`auction.js:813-817`) — `MessageFormData`,
  título literal `"Cancelar anúncio"`.
- `abrirAnunciarItem` (`auction.js:611-615`) — `ModalFormData`, título
  literal `"Anunciar item"`.

Esses três são tipos de form diferentes (confirmação sim/não de 2 botões
fixos, ou campos de formulário) — não usam `.button()` em grade e
presumivelmente nunca deveriam disparar a tela custom de qualquer forma.
**Não explicam** o sintoma relatado ("às vezes abre como lista vanilla
comum") porque o sintoma descrito é sobre telas que deveriam ser grade e
não são — essas três nunca foram grade. Confidence: **confirmado** (quanto
à ausência do marcador) / **suspeita** (quanto a não serem a causa do
sintoma relatado, já que não foi inspecionado o lado RP pra confirmar que
ele de fato ignora esses dois tipos de form).

---

## 4) `manifest.json` declara dependency pro RP?

**Não.** `ADDONS/SonheMenu_BP/manifest.json:20-33`:
```json
"dependencies": [
    { "module_name": "@minecraft/server", "version": "2.10.0-beta" },
    { "module_name": "@minecraft/server-ui", "version": "2.2.0-beta" },
    { "module_name": "@minecraft/server-net", "version": "1.0.0-beta" }
]
```
Só módulos de API. **Nenhuma entrada com `"uuid"` apontando pro RP**
(`SonheMenu_RP`, uuid `b71a84eb-d21e-4460-bb7c-eb9758d1ede4`, lido de
`ADDONS/SonheMenu_RP/manifest.json`).

Isso **é o padrão inconsistente dentro do próprio repositório**: o
`SonheChat_BP` (pack irmão) declara corretamente uma dependency por UUID
pro seu companion data pack —
```json
{ "uuid": "1afb8ca5-5349-41cb-8ed6-335f21be1d9f", "version": [1, 0, 0] }
```
(`ADDONS/SonheChat_BP/manifest.json`) — ou seja, o time já usa esse
mecanismo em outro pack, só não foi replicado aqui.

**Risco avaliado:** `dependencies` no manifest de um BP **não bloqueia a
ativação do BP** se o pack referenciado (RP) não estiver no mundo — no
Bedrock isso normalmente só gera um aviso/erro de "dependência ausente" no
content log, sem impedir o BP de rodar sozinho. Ou seja, mesmo que o
dependency fosse adicionado, ele funcionaria como *diagnóstico* (aparece
no log), não como trava. Hoje, **sem o dependency, não existe nem esse
diagnóstico**: se o RP estiver desativado no mundo, o BP monta o
`ActionFormData` normalmente, `§d§r§e§a§m§r` é só formatação invisível sem
efeito nenhum sem o `view` binding do RP pra interceptá-la, e o resultado
é **exatamente** a lista vanilla — com **log limpo**, porque do ponto de
vista do BP nada deu errado (`form.show()` resolveu normalmente). Esse é o
caminho que melhor bate com "às vezes cai na lista vanilla, sem erro".
Confidence: **provável** (o mecanismo de dependency-sem-bloqueio é
conhecimento de plataforma, não foi testado neste addon especificamente;
o resto — ausência do campo e o comportamento do marcador sem RP — é
**confirmado** por código).

---

## 5) Algum script falha ao carregar?

**Achado relevante: `auction.js:3` faz import estático, sem guarda, de
`@minecraft/server-net`:**
```js
import { http, HttpRequestMethod, HttpHeader, HttpRequest } from "@minecraft/server-net";
```
Import ES module estático não pode ser envolvido em `try/catch` (diferente
do truque usado em `main.js:48-73`, que importa `@minecraft/server` inteiro
via `import * as mcserver` justamente pra não quebrar o carregamento se um
símbolo faltar). Se `@minecraft/server-net` não resolver — módulo
beta/pré-lançamento, só existe com o toggle experimental correspondente
ativo no mundo — o import falha na avaliação do módulo, e a falha se
propaga pela cadeia de imports:
`auction.js` (falha) ← `menu.js:9` (`import { abrirAuctionHouse } from
"./auction.js"`) ← `main.js:3` (`import { abrirMenuPrincipal } from
"./menu.js"`).

Isso derrubaria o `main.js` inteiro — inclusive o `world.beforeEvents.chatSend.subscribe`
do `!menu` (`main.js:34`) — não apenas a Auction House. **Isso explicaria
"menu não abre nunca" mais do que "às vezes abre como lista vanilla"**,
então é um risco correlato, não a causa direta confirmada do sintoma
relatado.

**Contradição de documentação encontrada:** o `README.md` deste mesmo pack
afirma o oposto do que o código faz:
> "Pack **local**, sem `@minecraft/server-net` — funciona mesmo se o
> `SonheBridge_BP` não estiver instalado ou o módulo de rede não estiver
> liberado no host."

Mas `manifest.json:29-32` **declara** a dependency de
`@minecraft/server-net`, e `auction.js` **usa** `http`/`HttpRequest` de
fato (função `chamarBridge`, `auction.js:33-43`) pra chamadas de
compra/venda/cancelamento/expiração da Auction House. O README está
desatualizado/errado — o pack **não** é mais "só local" como descrito.
Confidence: **confirmado** (a contradição em si, comparando README linha
14-16 com manifest.json linhas 29-32 e auction.js linha 3).

Demais imports do addon (`casa.js`, `configuracoes.js`, `conquistas.js`,
`dados_jogador.js`, `diario.js`, `estatisticas.js`,
`inventario_resumo.js`) usam só símbolos estáveis de `@minecraft/server`
(`world`, `system`, `Player`, `MolangVariableMap`, `ItemStack`) — nenhum
outro import de módulo beta sem guarda foi encontrado. Confidence:
**confirmado**.

---

## 6) Versões de módulo declaradas x compatibilidade com 1.26.44

De `manifest.json:20-33`:

| Módulo | Versão declarada | Observação |
|---|---|---|
| `@minecraft/server` | `2.10.0-beta` | sufixo `-beta` — exige o toggle experimental de Beta APIs ativo no mundo/servidor. |
| `@minecraft/server-ui` | `2.2.0-beta` | idem — `ActionFormData`/`ModalFormData`/`MessageFormData` vêm desse módulo. |
| `@minecraft/server-net` | `1.0.0-beta` | idem; o próprio comentário do pack irmão `SonheBridge_BP` (`scripts/main.js:5-6`) documenta: *"`@minecraft/server-net` ainda é pré-lançamento (ago/2026) e só funciona se estiver liberado no host"*. |

Todas as três dependências são versões `-beta`, ou seja, **o addon inteiro
depende do toggle experimental de Beta APIs estar ligado no mundo**. Não
foi encontrado no repositório nenhum arquivo com tabela oficial de
compatibilidade de versão de módulo x build de cliente 1.26.44 pra
confirmar numericamente se `2.10.0-beta`/`2.2.0-beta`/`1.0.0-beta` são
exatamente as builds certas pra essa build de cliente — isso exigiria
checar a documentação oficial de módulos do Bedrock (fora do repo)
correspondente à data de build do cliente. Confidence: **suspeita** quanto
à compatibilidade numérica exata; **confirmado** quanto ao fato de que as
três dependências são beta e portanto condicionadas ao experimental
toggle.

---

## Lista de riscos (prioridade)

1. **`abrirMinhasVendas` sem paginação** (`auction.js:788-794`) — estoura
   os 12 slots do grid sempre que um vendedor tiver ≥12 anúncios ativos;
   sem teto nenhum no código. **Confirmado.**
2. **BP sem dependency declarada pro RP** (`manifest.json`) — se o RP
   estiver ausente/desativado, o BP roda sozinho, produz lista vanilla com
   log limpo, e não há nem um aviso de dependência ausente pra apontar a
   causa. **Provável** como explicação do sintoma relatado.
3. **`abrirVerAnuncios` pode chegar a 13 botões** numa página do meio
   cheia (`auction.js:390-404`). **Confirmado.**
4. **Import estático sem guarda de `@minecraft/server-net`**
   (`auction.js:3`) — módulo beta; se indisponível, derruba `auction.js` →
   `menu.js` → `main.js` inteiro (não abre nem a lista vanilla, não abre
   nada). Sintoma diferente do relatado, mas mesmo módulo de risco.
   **Confirmado o mecanismo; suspeita quanto a já ter acontecido em
   produção.**
5. **README.md desatualizado** — afirma que o pack não usa
   `@minecraft/server-net`, quando o manifest e `auction.js` mostram que
   usa. Risco de decisão errada por quem lê só o README antes de instalar.
   **Confirmado.**
6. **Três dependências de módulo em `-beta`** — todo o addon (inclusive o
   `ActionFormData` que carrega o marcador) só existe se o toggle
   experimental estiver ligado no mundo/servidor de destino.
   **Confirmado o gate; não verificado neste repo se o mundo de produção
   tem o toggle ligado.**

---

## Conclusão sobre o lado BP

Todo `ActionFormData` do addon carrega o marcador `§d§r§e§a§m§r` sem
exceção — o BP **não tem** nenhum caminho de `ActionFormData` que "esquece"
o marcador. A causa mais provável do sintoma ("às vezes abre como lista
vanilla, sem erro") do lado BP não é ausência de marcador, e sim (a) o RP
não estar de fato aplicado/ativo naquele momento — sem dependency
declarada, isso não deixa rastro nenhum no log — e/ou (b) alguns menus da
Auction House ultrapassarem os 12 slots do grid (13 em `abrirVerAnuncios`,
ilimitado em `abrirMinhasVendas`), o que pode levar o RP a não conseguir
desenhar a grade e cair de volta pro form padrão — mas isso já é hipótese
sobre o comportamento do RP, fora do escopo desta auditoria (BP-only).
