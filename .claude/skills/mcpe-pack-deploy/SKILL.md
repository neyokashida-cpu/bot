---
name: mcpe-pack-deploy
description: Instala e VALIDA add-ons de Minecraft Bedrock (MCPE) num mundo ou servidor dedicado copiando pastas na mão (sem symlink) — onde o pack vive, world_behavior_packs.json / world_resource_packs.json, ordem de prioridade, bump de version pra furar cache e leitura do ContentLog. Use quando o pedido for "meu pack não aparece no mundo", "instalar o addon no servidor", "a UI/textura não mudou depois de editar", "conferir se o resource pack chegou no cliente" ou "ler o ContentLog do servidor".
---

# Deploy e validação de packs (servidor dedicado / mundo)

Escopo: **entrega**. Se o pack está instalado e ativo mas o comportamento em si está errado, o problema é de conteúdo — veja `mcpe-json-ui`, `mcpe-custom-server-form` ou `mcpe-scripting-setup`.

Referência real usada nos exemplos abaixo: servidor dedicado em `/c/Users/Desktop/Downloads/Eita`, mundo `worlds/Bedrock level`.

## 1. Onde os packs podem viver

No servidor dedicado (BDS) existem três pares de diretórios, e eles não são equivalentes:

```
<server>/
├── behavior_packs/            # pool global (aqui só vem vanilla/chemistry/editor da Mojang)
├── resource_packs/            # pool global
├── development_behavior_packs/    # pool global, recarrega sem reiniciar o servidor
├── development_resource_packs/    # idem
└── worlds/
    └── Bedrock level/
        ├── behavior_packs/    # cópia POR MUNDO — é aqui que addon de terceiro costuma ficar
        ├── resource_packs/
        ├── world_behavior_packs.json   # a lista de ATIVOS
        └── world_resource_packs.json   # a lista de ATIVOS
```

Regras que valem sempre:

- Copiar a pasta do pack **não ativa nada**. Ativação é a entrada no `world_*_packs.json`. Um pack presente em `worlds/<mundo>/behavior_packs/` e ausente do JSON simplesmente não existe pro jogo.
- O inverso também vale: uma entrada no JSON cujo `pack_id` não corresponde a nenhuma pasta encontrada é **ignorada em silêncio**, sem erro fatal. No servidor `Eita`, `world_behavior_packs.json` lista `9c49a642-c83e-477b-825a-bd27e3249ac6` v2.0.5 e `world_resource_packs.json` lista `c62bb4f5-...` v2.0.5 e `c5f99db1-...` v0.1.5 — nenhum dos três tem pasta correspondente, e o mundo carrega normalmente. É por isso que "eu coloquei no json" não é prova de nada.
- `development_*_packs` é o único lugar que recarrega conteúdo (JSON de item/bloco/UI, scripts) sem reiniciar. Bom pra iteração, ruim pra produção. Fonte: [Bedrock Wiki — Troubleshooting / dev packs](https://wiki.bedrock.dev/guide/troubleshooting).
- Não use symlink/junction pra ligar o repo ao servidor: o BDS enumera diretórios de verdade e, em Windows, junction + cópia por FTP/painel de host é a origem mais comum de "instalei mas não aparece". Copie os arquivos.

## 2. world_behavior_packs.json e world_resource_packs.json

Formato real, extraído de `worlds/Bedrock level/world_resource_packs.json` do servidor `Eita`:

```json
[
  { "pack_id": "1afb8ca5-5349-41cb-8ed6-335f21be1d9f", "version": [1, 0, 0] },
  { "pack_id": "6bf93476-10f3-4223-ae7c-ee68b42181c2", "version": [1, 0, 2] },
  { "pack_id": "d2a1b92d-5f8b-4c1d-9d6b-c74b2d8e4b71", "version": [1, 0, 0] }
]
```

Três regras duras:

1. **`pack_id` é o UUID do `header`**, nunca o de um `modules[]`. No `SonheChat_RP` o header é `1afb8ca5-5349-41cb-8ed6-335f21be1d9f` e o module é `da4a1698-...`; só o primeiro entra aqui. Colocar UUID de módulo = pack ignorado sem mensagem.
2. **`version` tem que casar com `header.version` do manifest**, campo por campo. `ModernFurnitureWE_RP` tem `header.version [1,0,2]` e a entrada diz `[1,0,2]`. Se você subir o manifest pra `[1,0,3]` e esquecer o JSON, a entrada aponta pra uma versão que não existe mais e o pack cai fora.
3. **A ordem do array define prioridade de override.** Em resource packs, quem está por cima ganha o arquivo em conflito — é isso que decide qual pack manda no `ui/`, nas texturas e no `_ui_defs.json` quando dois packs mexem na mesma coisa. Isso é crítico pra UI: dois packs sobrescrevendo o namespace `server_form` e só um vale.

Sobre qual extremidade do array tem prioridade: no cliente, o topo da lista de packs na tela do mundo é o que vence, e o JSON é lido na mesma ordem da lista. **Confirme em jogo antes de reordenar por fé**: coloque o seu pack numa ponta, teste, e se não mudar coloque na outra. É teste de 30 segundos e evita meia hora de teoria.

Recomendação prática: mantenha um único pack seu mexendo em `ui/` por servidor. Prioridade entre resource packs é a categoria de bug mais chata de diagnosticar porque não gera log.

## 3. Dependência BP -> RP no manifest

Se o behavior pack precisa do resource pack (ícones, UI, texturas dos itens), declare no `manifest.json` do BP:

```json
{
    "header": {
        "uuid": "BP_HEADER_UUID",
        "version": [1, 0, 3],
        "min_engine_version": [1, 21, 50]
    },
    "modules": [
        { "type": "data", "uuid": "BP_MODULE_UUID", "version": [1, 0, 3] },
        {
            "type": "script",
            "language": "javascript",
            "uuid": "BP_SCRIPT_UUID",
            "entry": "scripts/main.js",
            "version": [1, 0, 3]
        }
    ],
    "dependencies": [
        { "uuid": "RP_HEADER_UUID", "version": [1, 0, 3] },
        { "module_name": "@minecraft/server", "version": "2.10.0-beta" },
        { "module_name": "@minecraft/server-ui", "version": "2.2.0-beta" }
    ]
}
```

Exemplo real do servidor: `SonheChat_BP` declara `{"uuid": "1afb8ca5-5349-41cb-8ed6-335f21be1d9f", "version": [1,0,0]}`, que é exatamente o header do `SonheChat_RP`. Se a `version` da dependência não casar com o `header.version` do RP instalado, o BP não carrega e o mundo pode se recusar a abrir — esse caso **sim** aparece no log.

Cuidado: dependência de RP não substitui a entrada no `world_resource_packs.json`. Ela só amarra as versões.

## 4. Version do manifest e cache

O cliente guarda os packs baixados do servidor num cache indexado por **UUID + version** (no Windows, algo como `%LOCALAPPDATA%\Temp\Minecraft Bedrock\minecraftpe\packcache\resource\<hash>/`). Consequência direta:

- Editar arquivos dentro do pack **sem mexer na `version`** faz o cliente reaproveitar a cópia antiga. Você edita `ui/sonhe_forms.json`, entra no servidor e vê o JSON de ontem.
- Toda vez que você reimplanta um RP num servidor que serve pack pra cliente: suba `header.version` (e a `version` correspondente no `world_resource_packs.json`, e a `dependencies` do BP se houver).
- É comum sobrar **mais de uma versão do mesmo pack no cache do cliente** — dois diretórios, mesmo `header.uuid`, versions diferentes. Se o servidor ainda anuncia a version antiga, é a antiga que monta a árvore de UI, com o conteúdo antigo dentro. Sintoma clássico: BP novo + RP velho no cliente, e qualquer combinação BP/RP acoplada (marcador de título, nome de textura, id de item) quebra.
- Reset limpo pro teste: sair do servidor, apagar o diretório `packcache` inteiro, reentrar, e confirmar que só um diretório do seu pack foi recriado, com a version que você espera.

## 5. Conferir que o RP realmente chegou no cliente

O BP roda no servidor; o RP roda no cliente. São dois deploys independentes, e o log do servidor não prova nada sobre o cliente.

- `server.properties`: `texturepack-required=false` (valor real no `Eita`) significa que o jogador pode **recusar** os recursos e entrar mesmo assim — nesse caso ele joga sem seu RP e você vê o comportamento vanilla enquanto o servidor jura que está tudo certo. Ponha `texturepack-required=true` durante o diagnóstico.
- Cliente: nas configurações do servidor/mundo, a opção de aceitar recursos precisa estar ligada, e no primeiro join tem que aparecer a barra de download do pack. Se não apareceu barra, nada chegou.
- Prova visual barata e definitiva: coloque no RP uma mudança impossível de confundir (uma cor de fundo berrante num painel, um label fixo com texto literal). Se ela aparece, o RP está carregado e com prioridade; se não aparece, pare de depurar bindings e vá depurar entrega.
- Existe também o conceito de "resource packs required" no nível do mundo (a flag que o servidor manda ao cliente). **Não confirmei o nome exato do campo nesta versão do BDS**; trate `texturepack-required` no `server.properties` como a chave a mexer e valide em jogo.

## 6. ContentLog: a fonte de verdade

Habilite no `server.properties` (valores reais do `Eita`):

```properties
content-log-file-enabled=true
content-log-console-output-enabled=true
content-log-level=verbose
```

Isso gera `ContentLog<data>_<n>.txt` na raiz do servidor (um por boot) e replica no `Dedicated_Server.txt`. Cada linha tem o formato `HH:MM:SS[Categoria][nível]-mensagem`.

Linhas reais, e o que cada prefixo te diz:

```
13:11:38[Scripting][verbose]-Plugin Discovered [SONHE Chat & Boas-vindas] PackId [bc2d468e-f1b6-40d0-a95e-516d176d5059_1.0.0] ModuleId [b02cafb3-...]
13:11:38[Scripting][verbose]-Plugin [Modern Furniture WE 13.7 BP] - promoted [@minecraft/server] from [2.1.0] to [2.9.0] requested by [...]
13:11:41[Recipes][error]-recipes/bladrillos_gris_blanco_escalera.json | f:bladrillos... | The Item: ... is missing or invalid, can't make the recipe
13:11:41[Item][warning]-worlds/Bedrock level/behavior_packs/ModernFurnitureWE_BP/item_catalog/crafting_item_catalog.json | The item f:barandilla1 was created with the category set to 'items', and is now being set to 'construction'
```

- `[Scripting][verbose] Plugin Discovered` é **o teste de instalação do BP**. Se o nome do seu pack não aparece nessa lista no boot, o BP não foi carregado: ou a pasta está no lugar errado, ou o `pack_id`/`version` no `world_behavior_packs.json` não casa, ou não há entrada nenhuma. Nenhum outro sintoma é necessário.
- `[Scripting][verbose] promoted [@minecraft/server] from X to Y` mostra a resolução de versão de módulo entre packs. Útil quando dois BPs pedem versões diferentes da API: o maior ganha e o pack que pedia a menor pode quebrar em runtime.
- `[Recipes][error]` / `[Item][warning]` sempre citam **o caminho do arquivo culpado**, inclusive de qual pack ele veio. Use isso pra saber se o erro é seu ou de um pack de terceiro antes de sair mexendo.
- Erros de script (exception em runtime) saem em `[Scripting][error]` com stack — é o único jeito de ver que o `main.js` morreu no import.

O que o ContentLog **não** te dá: nada sobre JSON UI. O parse de `ui/*.json` acontece no cliente. Pra ver controle rejeitado, `@extend` que não resolve ou textura faltando, você precisa do log do **cliente** (ativar `Content Log` e `Content Log GUI` nas opções de criador do jogo). Procurar erro de UI no log do servidor é tempo perdido.

## 7. Ordem de behavior packs e `chatSend`

Ordem em behavior packs não é só override de arquivo: com scripts, ela decide **quem roda primeiro** e portanto quem cancela o evento antes do outro ver.

```javascript
world.beforeEvents.chatSend.subscribe((ev) => {
    if (!ev.message.startsWith("!")) return;
    ev.cancel = true; // ninguém depois de mim processa esta mensagem
});
```

Se dois BPs assinam `beforeEvents.chatSend` e o primeiro faz `ev.cancel = true` de forma ampla (por exemplo, um pack de chat customizado que cancela tudo pra reformatar), o segundo pack pode nunca ver a mensagem — seus comandos de chat "param de funcionar" sem nenhum erro em lugar nenhum. No `Eita` isso é risco concreto: `SonheChat_BP` e `SonheBridge_BP` estão ativos juntos e ambos mexem em chat.

Diagnóstico: `world.sendMessage` no início de cada handler e ver qual imprime. Correção: reordenar as entradas de `world_behavior_packs.json`, ou tornar o cancelamento condicional em vez de global. **A relação exata entre posição no array e ordem de execução de handler não está documentada pela Mojang** — confirme empiricamente antes de afirmar qual ponta roda primeiro.

## 8. Checklist: "meu pack não aparece" / "minha UI não mudou"

Rode na ordem. Cada passo elimina uma camada; não pule pra debugar conteúdo antes do passo 6.

1. A pasta do pack existe em `worlds/<mundo>/behavior_packs/<Pack>/` (ou `resource_packs/`) e tem `manifest.json` legível na raiz da pasta — não dentro de uma subpasta extra criada pelo unzip.
2. `header.uuid` do manifest está no `world_*_packs.json` correspondente, e `version` do JSON == `header.version` do manifest, campo por campo.
3. `JSON.parse` passa nos dois `world_*_packs.json` (vírgula sobrando derruba a lista inteira, não só uma entrada).
4. Boot do servidor: `[Scripting][verbose] Plugin Discovered [<seu pack>]` aparece no ContentLog novo. Se não, volte ao 2.
5. Não há erro `[Recipes][error]` / `[Item][error]` / `[Scripting][error]` citando arquivo do seu pack.
6. RP: `header.version` foi incrementada nesta rodada de deploy? Se não, o cliente pode estar servindo cache. Suba a version e limpe o `packcache`.
7. Cliente aceitou os recursos (barra de download apareceu) e `texturepack-required=true` durante o teste.
8. Mudança berrante de prova (cor/label fixo) aparece em jogo. Só a partir daqui o problema é de conteúdo.
9. Nenhum outro pack ativo mexe nos mesmos arquivos. Confirme com `grep -rl "<namespace ou arquivo>" worlds/<mundo>/resource_packs/*/ui/` antes de acusar prioridade.
10. Se BP e RP compartilham um contrato (nome de textura, id de item, marcador de título), os dois foram reimplantados **na mesma rodada**. Deploy pela metade é a causa mais comum de bug "impossível".

Exemplo real de aplicação: no servidor `Eita`, `grep` por `b71a84eb` e `1a5f3c14` (header UUIDs do SonheMenu RP e BP) nos dois `world_*_packs.json` retorna **zero** ocorrências, e `worlds/Bedrock level/resource_packs/` só tem `SonheChat_RP`. Ou seja, o SonheMenu não está instalado nesse servidor — qualquer teste do menu feito ali estava exercitando outro deploy (outro servidor, ou cache do cliente), não esse. Esse é o passo 1 do checklist pegando o bug antes de qualquer análise de JSON.

## 9. Erros comuns

| Sintoma | Causa |
|---|---|
| Pack copiado, nada acontece, nenhum log | Falta a entrada no `world_*_packs.json` — copiar pasta não ativa |
| `pack_id` está no JSON e o pack é ignorado sem erro | UUID de `modules[]` em vez do `header`, ou `version` divergindo do manifest |
| Tudo parou de carregar de uma vez | `world_*_packs.json` inválido (vírgula/colchete) — a lista toda é descartada |
| Editei JSON/UI e o jogo mostra a versão antiga | `header.version` não subiu; cliente serve o pack do `packcache` |
| BP novo funciona, RP parece velho | Deploy pela metade, ou duas versions do mesmo RP no cache do cliente e o servidor anuncia a antiga |
| RP nunca chega no cliente | `texturepack-required=false` + jogador recusou recursos |
| Textura/UI custom sumiu depois de instalar outro addon | Prioridade de override: outro RP acima do seu na ordem do array |
| Comando de chat do meu pack não responde e não há erro | Outro BP cancelou `beforeEvents.chatSend` antes — ordem dos behavior packs |
| `[Recipes][error]` citando pack que não é meu | Erro de pack de terceiro; ignore, não é regressão sua |
| Erro de UI não aparece em log nenhum | Parse de JSON UI é no cliente; ative o Content Log do cliente, não do servidor |
| Mundo não abre depois de adicionar BP | `dependencies` do BP aponta pra RP com version que não existe instalada |
| Funciona em `development_*_packs` e quebra em produção | Dev pack recarrega e tolera iteração; o pool do mundo exige version/UUID coerentes e reinício |

## Fontes

- [Microsoft Learn — Bedrock Dedicated Server](https://learn.microsoft.com/en-us/minecraft/creator/documents/bedrockdedicatedserver) (layout de diretórios, `server.properties`)
- [Microsoft Learn — Addons / manifest e dependências](https://learn.microsoft.com/en-us/minecraft/creator/documents/behaviorpack)
- [Bedrock Wiki — Troubleshooting](https://wiki.bedrock.dev/guide/troubleshooting) (Content Log, dev packs)
- [Microsoft Learn — Script API Reference](https://learn.microsoft.com/en-us/minecraft/creator/scriptapi/) (`beforeEvents.chatSend`, versões de módulo)
- Servidor real inspecionado: `/c/Users/Desktop/Downloads/Eita` — `server.properties`, `worlds/Bedrock level/world_behavior_packs.json`, `worlds/Bedrock level/world_resource_packs.json`, `ContentLog2026-08-17_13-11-38_1.txt`, `Dedicated_Server.txt`
