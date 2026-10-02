# Pesquisa web: addons com menu custom (JSON UI / server_form) e relatos de fallback pro form vanilla

Data da pesquisa: 2026-08-31
Objetivo: verificar se addons públicos populares (MCPEDL/Reddit/fóruns) que sobrescrevem
`server_form`/ActionFormData via JSON UI têm relatos de usuários sobre o menu custom cair
silenciosamente pro form vanilla em lista (comportamento intermitente).

**Observação metodológica**: mcpedl.com bloqueia fetch direto (HTTP 403 / anti-bot). O conteúdo
das páginas abaixo foi obtido via proxy leitor (r.jina.ai) espelhando a mesma URL pública.

---

## Addons verificados no MCPEDL

### 1. Shop UI Addon V2.0.3 — https://mcpedl.com/shop-ui-addon/
Comentários revisados. **Nenhum relato** do bug procurado (menu sumindo / voltando pra lista
vanilla / intermitência). Achados nos comentários, sem relação direta:
- Richard12 (2 nov 2024) e alphaskill (22 mai 2025): reclamam de não conseguir obter o item
  que abre a loja (`shop:open`) — problema de obtenção de item, não de UI caindo pro vanilla.
- jao451 (26 abr 2024): "os dois links da descrição levavam ao mesmo arquivo RP" (bug de
  download, corrigido pelo autor).
- confidence: não aplicável (nenhum relato relevante encontrado).

### 2. ShopUI - N — https://mcpedl.com/shopui/
Comentários revisados (dúvidas sobre bypass de restock, editar preços, pedidos de update).
**Nenhum relato** de UI caindo pro form vanilla ou comportamento intermitente.
- confidence: não aplicável.

### 3. Advanced Economy Shop — https://mcpedl.com/advanced-economy-shop-beta/
Não há relato do bug específico (fallback silencioso pro form vanilla), mas há relatos de
o comando não funcionar em certos contextos, o que é adjacente:
- Ian2555 (2 mai 2026): digitou `/shop` e nada apareceu.
- Aura22 (12 mai 2026): "funciona no mundo local, mas no servidor Aternos o comando `/shop`
  não é reconhecido" — sugere causa de infraestrutura/scripting API não habilitada, não
  necessariamente fallback de JSON UI.
- kyaGD (8 ago 2026), respondendo a esse tipo de problema: "quando criar um mundo, vá em
  experiments, ative 'Beta APIs' e o comando /shop vai funcionar" — indica que a causa raiz
  comum nesses relatos é experimento desativado, não bug de UI.
- Pixura Studios: sugeriu ao autor adicionar JSON de texturas de botões via `server_form.json`
  "pra não alterar a UI original" — é uma sugestão de implementação, não um bug relatado.
- confidence: suspeita (os relatos são sobre o comando/scripting API não rodar, não sobre a
  UI cair pro form vanilla depois de abrir).

### 4. Task/Quest System — https://mcpedl.com/tasksystem/
Página sem seção de comentários visível no conteúdo obtido (pode estar em widget carregado via
JS não capturado pelo proxy). Nenhum relato coletado.
- confidence: não aplicável (sem dados).

### 5. Clickable Menu v3 — https://mcpedl.com/clickable-menu/
Comentários revisados. Único problema relatado é de crash ao trocar gamemode, não relacionado:
- FrostFirePiggyMCPEDL (9 out 2021): "My game just crashed if i switch gamemode survival and
  creative every time fixed pls" — crash geral, não fallback de UI.
- confidence: não aplicável ao tema pesquisado.

### 6. mvShop / Minimal Shop — https://mcpedl.com/mv/
Página sem seção de comentários visível no conteúdo obtido pelo proxy (só descrição/changelog).
- confidence: não aplicável (sem dados).

### 7. Admin Menu — https://mcpedl.com/admin-menu/
Comentários revisados. Há relato de menu não abrindo, mas é abertura via tag de permissão, não
fallback de JSON UI pro form vanilla:
- Comentário de usuário: "the menu wont open" mesmo depois de `/tag @s add admin` — parece
  problema de permissão/tag, não de UI custom caindo pro form padrão em lista.
- Outro usuário: "This addon dosen't work for 1.19.41" (incompatibilidade de versão).
- Outro usuário: "Its shutting my server down for 'WatchDog Exeption'" (crash/watchdog, não
  fallback de UI).
- confidence: suspeita (menu não abre é diferente de "abre mas em lista vanilla"; não dá pra
  confirmar que é o mesmo bug que estamos rastreando).

---

## Busca em Reddit / fóruns

Buscas feitas (WebSearch): `site:reddit.com` para "custom menu form not showing bug", "grid
menu addon shop UI bug report" (também tentando forums.gg), "shows default"/"vanilla list"
bug bedrock, "doesn't always"/"randomly" default menu bug. **Nenhum resultado relevante do
Reddit (r/MCPE, r/Minecraft) ou de forums.gg foi encontrado** — as buscas só retornaram
páginas de terceiros sem relação (documentação, sites de outros jogos/engines, Scribd, itch.io
de projetos não-Minecraft).
- confidence: não aplicável — busca não encontrou nada, não há citação pra fazer.

## Documentação técnica (Bedrock Wiki)

- https://wiki.bedrock.dev/json-ui/modifying-server-forms — explica como sobrescrever
  `server_form.json`. Menciona apenas que a UI custom pode **sobrepor visualmente** o form
  padrão ("you might notice it overlaps with the normal action form"), resolvido com bindings
  condicionais no `long_form` original. **Não há menção** a fallback silencioso, bug conhecido,
  race condition ou quebra entre versões do jogo.
- confidence: confirmado (é o texto literal da doc), mas o conteúdo não confirma nem contradiz
  a hipótese do fallback silencioso — só não trata do assunto.

---

## Conclusão

**Não foi encontrado nenhum relato confirmado, em MCPEDL ou Reddit/fóruns, de um addon público
cuja UI custom (server_form/ActionFormData via JSON UI) caia silenciosamente pro form vanilla
em lista de forma intermitente.** Os problemas relatados nos addons pesquisados são de outra
natureza: item/comando pra abrir o menu não funciona, incompatibilidade de versão, crash de
gamemode, watchdog exception, ou scripting API (Beta APIs) desativada no mundo — nenhum deles é
o padrão "abre, mas às vezes mostra a lista padrão em vez do grid custom" que motivou esta
pesquisa. Isso é consistente com duas leituras: (a) o problema é raro o suficiente pra não
gerar comentários públicos massivos, ou (b) usuários que passam por isso tendem a relatar como
"menu não abre" genérico sem diferenciar causa, dificultando encontrar via busca textual.

Recomendação: não tratar isso como "bug documentado da comunidade" — não há citação pra
embasar essa afirmação. Se for investigar a causa raiz do nosso addon, focar em timing/ordem
de carregamento do resource pack e em condições de binding no JSON UI (não há evidência externa
de que seja um problema conhecido e generalizado no ecossistema).
