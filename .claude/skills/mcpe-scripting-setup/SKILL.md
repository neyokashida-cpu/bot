---
name: mcpe-scripting-setup
description: Configura a Scripting API (@minecraft/server) num behavior pack de Minecraft Bedrock (MCPE) — módulo de script no manifest, pasta scripts/, e um main.js inicial funcional. Use quando o pedido for "adicionar scripting", "usar a API do minecraft/server", "criar lógica em JS/TS pro addon" ou similar.
---

# Scripting API (@minecraft/server)

Baseado em Microsoft Learn (Script API Reference) e Bedrock Wiki (Intro to Scripting), atualizado em 2026.

## 1. Adicione o módulo de script + dependência no manifest.json do BP

```json
{
    "format_version": 2,
    "header": {
        "name": "Nome do Addon",
        "description": "...",
        "uuid": "BP_HEADER_UUID",
        "version": [1, 0, 0],
        "min_engine_version": [1, 21, 50]
    },
    "modules": [
        { "type": "data", "uuid": "BP_MODULE_UUID", "version": [1, 0, 0] },
        {
            "type": "script",
            "language": "javascript",
            "uuid": "BP_SCRIPT_MODULE_UUID",
            "entry": "scripts/main.js",
            "version": [1, 0, 0]
        }
    ],
    "dependencies": [
        { "uuid": "RP_HEADER_UUID", "version": [1, 0, 0] },
        { "module_name": "@minecraft/server", "version": "2.7.0" }
    ]
}
```

Gere um UUID novo pro módulo de script (não reaproveite o do módulo `data`). Confira em [Microsoft Learn — Script API Reference](https://learn.microsoft.com/en-us/minecraft/creator/scriptapi/) qual é a versão estável mais recente de `@minecraft/server` no momento — a API muda com frequência entre versões do jogo.

## 2. Estrutura

```
BP/
└── scripts/
    └── main.js
```

Se for usar TypeScript, escreva em `scripts_src/` (ou similar) e configure um bundler (esbuild/webpack/tsc) que gere o `.js` final em `scripts/main.js` — o jogo só executa JavaScript puro, nunca `.ts` diretamente.

## 3. main.js inicial

**Use sempre import nomeado** (`import { world, system } from "@minecraft/server"`) — nunca `import * as mc`, que não é o padrão recomendado pela documentação atual e dificulta tree-shaking/leitura.

```javascript
import { world, system } from "@minecraft/server";

world.afterEvents.worldLoad?.subscribe(() => {
    world.sendMessage("§7[Addon] Mundo carregado, scripts ativos.");
});

// Exemplo: reagir a um jogador entrando no mundo
world.afterEvents.playerSpawn.subscribe((evento) => {
    if (!evento.initialSpawn) return;
    evento.player.sendMessage(`Bem-vindo(a), ${evento.player.name}!`);
});

// Exemplo: rodar algo a cada N ticks (1 segundo = 20 ticks)
system.runInterval(() => {
    // lógica periódica aqui
}, 20);
```

## 4. Eventos comuns

| Evento | Quando dispara |
|---|---|
| `world.afterEvents.playerSpawn` | Jogador entra/reaparece no mundo (`initialSpawn` diferencia primeira entrada de respawn) |
| `world.afterEvents.entitySpawn` | Qualquer entidade (incluindo mobs customizados) é criada |
| `world.beforeEvents.chatSend` | Antes de uma mensagem de chat ser enviada — permite cancelar (`evento.cancel = true`) |
| `world.afterEvents.entityHurt` | Uma entidade sofre dano |
| `world.afterEvents.blockPlace` / `blockBreak` | Bloco colocado/quebrado por jogador |
| `system.run(fn)` | Roda `fn` uma vez, no próximo tick |
| `system.runInterval(fn, ticks)` | Roda `fn` repetidamente a cada N ticks |
| `system.runTimeout(fn, ticks)` | Roda `fn` uma vez, após N ticks |

## 5. Testar

Ative **Content Log** em Configurações > Criador antes de testar — erros de script (exceptions, sintaxe) aparecem lá, não travam o jogo silenciosamente. Edite `main.js`, salve, e recarregue o mundo (sair e entrar de novo já é suficiente com development packs).

## 6. Ir além

Combine com `mcpe-custom-item` (componente `minecraft:on_use` disparando um evento customizado) ou `mcpe-custom-entity` (`component_groups`/`events` reagindo a chamadas da Scripting API) pra lógica customizada de verdade — pura JSON não cobre tudo, é aí que o script entra.
