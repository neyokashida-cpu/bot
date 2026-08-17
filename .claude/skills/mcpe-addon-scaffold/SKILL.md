---
name: mcpe-addon-scaffold
description: Cria a estrutura inicial de um Add-On de Minecraft Bedrock (MCPE) do zero — par behavior pack + resource pack, manifest.json corretos com UUIDs combinando, pastas padrão e onde instalar pra testar. Use quando o pedido for "criar um addon novo", "começar um addon do zero" ou similar.
---

# Scaffold de Add-On Bedrock

Baseado na documentação oficial (Microsoft Learn — Add-Ons Reference: manifest.json) e no Bedrock Wiki (Project Setup), atualizado em 2026.

## 1. Gere 4 UUIDs únicos antes de tudo

Nunca reutilize UUIDs de outro addon/tutorial — eles servem pra identificar o pack de forma única no jogo. Gere com:

```bash
python -c "import uuid; [print(uuid.uuid4()) for _ in range(4)]"
```

Você vai precisar de: `BP_HEADER_UUID`, `BP_MODULE_UUID`, `RP_HEADER_UUID`, `RP_MODULE_UUID`.

## 2. Estrutura de pastas

```
meu_addon_BP/
├── manifest.json
├── pack_icon.png          # 256x256, opcional mas recomendado
├── texts/
│   ├── en_US.lang
│   └── languages.json
├── entities/
├── items/
├── blocks/
├── loot_tables/
├── recipes/
├── spawn_rules/
└── scripts/                # só se for usar a Scripting API — ver skill mcpe-scripting-setup

meu_addon_RP/
├── manifest.json
├── pack_icon.png
├── texts/
│   ├── en_US.lang
│   └── languages.json
├── entity/
├── items/
├── blocks/
├── textures/
│   ├── blocks/
│   ├── items/
│   └── entity/
├── models/
├── animations/
├── animation_controllers/
├── render_controllers/
└── sounds/
```

## 3. manifest.json do Behavior Pack

`format_version` 2 é a base estável e amplamente compatível (v3 ainda está em preview e exige `<metadata>/<author>`, então evite por enquanto). Use a versão numérica `[major, minor, revision]` pro `version`/`min_engine_version` — é o formato mais compatível.

```json
{
    "format_version": 2,
    "header": {
        "name": "Nome do Addon",
        "description": "Descrição curta (1-2 linhas, aparece no jogo).",
        "uuid": "BP_HEADER_UUID",
        "version": [1, 0, 0],
        "min_engine_version": [1, 21, 50]
    },
    "modules": [
        {
            "type": "data",
            "uuid": "BP_MODULE_UUID",
            "version": [1, 0, 0]
        }
    ],
    "dependencies": [
        {
            "uuid": "RP_HEADER_UUID",
            "version": [1, 0, 0]
        }
    ]
}
```

## 4. manifest.json do Resource Pack

```json
{
    "format_version": 2,
    "header": {
        "name": "Nome do Addon",
        "description": "Descrição curta (1-2 linhas, aparece no jogo).",
        "uuid": "RP_HEADER_UUID",
        "version": [1, 0, 0],
        "min_engine_version": [1, 21, 50]
    },
    "modules": [
        {
            "type": "resources",
            "uuid": "RP_MODULE_UUID",
            "version": [1, 0, 0]
        }
    ]
}
```

Note a dependência: o **BP depende do RP** (aponta pro `RP_HEADER_UUID`), não o contrário — é a convenção padrão dos packs vanilla.

## 5. texts/languages.json e en_US.lang

`languages.json`:
```json
["en_US"]
```

`en_US.lang` (vazio serve de início, cada skill de conteúdo — entidade/item/bloco — adiciona linhas aqui):
```
pack.name=Nome do Addon
pack.description=Descrição curta.
```

## 6. Onde instalar pra testar (Windows)

Copie (ou crie link simbólico) as duas pastas pra:
```
%LOCALAPPDATA%\Packages\Microsoft.MinecraftUWP_8wekyb3d8bbwe\LocalState\games\com.mojang\development_behavior_packs\
%LOCALAPPDATA%\Packages\Microsoft.MinecraftUWP_8wekyb3d8bbwe\LocalState\games\com.mojang\development_resource_packs\
```
(Em instalações via Xbox/Preview o caminho pode variar; a pasta `com.mojang` também aparece em `...\Users\Shared\games\com.mojang` em algumas versões.) Usar `development_*_packs` evita precisar reimportar `.mcpack`/`.mcaddon` a cada mudança — o jogo recarrega ao reabrir o mundo.

Ative **Content Log** em Configurações > Criador, pra ver erros de parsing de JSON direto no jogo.

## 7. Próximos passos

Depois do scaffold, use as outras skills MCPE pra popular o addon:
- `mcpe-custom-entity` — criar um mob customizado
- `mcpe-custom-item` — criar um item customizado
- `mcpe-custom-block` — criar um bloco customizado
- `mcpe-scripting-setup` — adicionar a Scripting API (`@minecraft/server`)

Recipes, loot tables e spawn rules seguem o mesmo padrão (JSON com `format_version` + `minecraft:recipe_shaped`/`minecraft:loot_table`/`minecraft:spawn_rules`) — não têm skill dedicada ainda; siga a doc oficial (Microsoft Learn) ou peça pra criar na hora.
