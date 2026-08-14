---
name: mcpe-custom-block
description: Cria um bloco customizado de Minecraft Bedrock (MCPE) — JSON do bloco, textura, geometria e entrada de idioma. Use quando o pedido for "criar um bloco novo", "criar um bloco customizado" ou similar.
---

# Bloco customizado (Bedrock Add-On)

Baseado em bedrock.dev (Blocks Intro / Block Components) e Microsoft Learn (Advanced Custom Blocks), atualizado em 2026. **A partir da versão 1.21.80**, se usar `minecraft:geometry` ou `minecraft:material_instances`, os dois componentes são obrigatórios juntos (não dá mais pra ter só um).

## 1. BP — `blocks/custom_block.json`

```json
{
    "format_version": "1.21.50",
    "minecraft:block": {
        "description": {
            "identifier": "sonhe:custom_block",
            "menu_category": {
                "category": "construction",
                "group": "itemGroup.name.stone"
            }
        },
        "components": {
            "minecraft:geometry": "minecraft:geometry.full_block",
            "minecraft:material_instances": {
                "*": {
                    "texture": "sonhe:custom_block",
                    "render_method": "opaque"
                }
            },
            "minecraft:collision_box": { "origin": [-8, 0, -8], "size": [16, 16, 16] },
            "minecraft:selection_box": { "origin": [-8, 0, -8], "size": [16, 16, 16] },
            "minecraft:destructible_by_mining": { "seconds_to_destroy": 3 },
            "minecraft:destructible_by_explosion": { "explosion_resistance": 6 },
            "minecraft:friction": 0.6,
            "minecraft:map_color": "#8a8a8a",
            "minecraft:loot": "loot_tables/blocks/custom_block.json"
        }
    }
}
```

### Componentes mais usados (referência rápida)

| Componente | Função |
|---|---|
| `minecraft:geometry` | Modelo/forma do bloco (`minecraft:geometry.full_block` pro cubo padrão, ou uma geometria customizada feita no Blockbench) |
| `minecraft:material_instances` | Textura por face (`"*"` = todas as faces; ou `"up"`, `"north"`, etc. pra faces diferentes) |
| `minecraft:collision_box` / `minecraft:selection_box` | Hitbox física e hitbox de seleção do mouse — em unidades de 1/16 de bloco |
| `minecraft:destructible_by_mining` | Tempo (segundos) pra quebrar |
| `minecraft:destructible_by_explosion` | Resistência a explosão |
| `minecraft:friction` | Escorregamento (0 = gelo, 0.6 = padrão) |
| `minecraft:map_color` | Cor no mapa |
| `minecraft:loot` | Caminho pra loot table de drop |

Use **`"states"`** + **`"permutations"`** dentro de `minecraft:block` pra criar variações (ex: um bloco que muda de textura por direção, ou um bloco de múltiplos estágios de crescimento).

## 2. RP — registrar a textura

`resource_pack/textures/terrain_texture.json`:
```json
{
    "resource_pack_name": "vanilla",
    "texture_name": "atlas.terrain",
    "texture_data": {
        "sonhe:custom_block": {
            "textures": "textures/blocks/custom_block"
        }
    }
}
```

E a imagem em `resource_pack/textures/blocks/custom_block.png` (16x16, PNG).

Pra aparecer no inventário/mão com o item do bloco, adicione também em `resource_pack/blocks.json`:
```json
{
    "format_version": [1, 1, 0],
    "sonhe:custom_block": {
        "textures": "sonhe:custom_block"
    }
}
```

## 3. Idioma — `texts/en_US.lang`

```
tile.sonhe:custom_block.name=Custom Block
```

## 4. Loot table (drop ao quebrar)

`loot_tables/blocks/custom_block.json`:
```json
{
    "pools": [
        {
            "rolls": 1,
            "entries": [
                { "type": "item", "name": "sonhe:custom_block", "weight": 1 }
            ]
        }
    ]
}
```

## 5. Testar

`/give @s sonhe:custom_block` no jogo, ou procure pelo nome no inventário criativo (categoria definida em `menu_category`).
