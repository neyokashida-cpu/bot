---
name: mcpe-custom-entity
description: Cria um mob/entidade customizada de Minecraft Bedrock (MCPE) — JSON de comportamento (behavior pack), JSON de cliente (resource pack), spawn egg e entrada de idioma. Use quando o pedido for "criar um mob novo", "criar uma entidade customizada" ou similar.
---

# Entidade customizada (Bedrock Add-On)

Baseado em Microsoft Learn (Entity Behavior Introduction) e bedrock.dev (Entities), atualizado em 2026.

Toda entidade precisa de **dois arquivos**: um no behavior pack (regras/IA/stats) e um no resource pack (aparência/animação). O `identifier` (`namespace:nome`) tem que ser **idêntico** nos dois.

## 1. Escolha um namespace

Use um prefixo curto e único do seu addon (ex: `sonhe:` em vez de `minecraft:`), pra nunca colidir com IDs vanilla ou de outros addons.

## 2. BP — `entities/custom_mob.json`

```json
{
    "format_version": "1.21.50",
    "minecraft:entity": {
        "description": {
            "identifier": "sonhe:custom_mob",
            "is_spawnable": true,
            "is_summonable": true,
            "is_experimental": false
        },
        "component_groups": {
            "sonhe:agressivo": {
                "minecraft:behavior.melee_attack": {
                    "priority": 2,
                    "speed_multiplier": 1.2,
                    "track_target": true
                },
                "minecraft:attack": { "damage": 3 }
            }
        },
        "components": {
            "minecraft:type_family": {
                "family": ["custom_mob", "mob"]
            },
            "minecraft:health": { "value": 20, "max": 20 },
            "minecraft:collision_box": { "width": 0.6, "height": 1.8 },
            "minecraft:physics": {},
            "minecraft:movement": { "value": 0.25 },
            "minecraft:movement.basic": {},
            "minecraft:navigation.walk": {
                "can_path_over_water": true,
                "avoid_water": true
            },
            "minecraft:behavior.random_stroll": {
                "priority": 6,
                "speed_multiplier": 1.0
            },
            "minecraft:behavior.look_at_player": {
                "priority": 7,
                "look_distance": 8.0
            }
        },
        "events": {
            "sonhe:tornar_agressivo": {
                "add": { "component_groups": ["sonhe:agressivo"] }
            }
        }
    }
}
```

### Componentes mais usados (referência rápida)

| Componente | Função |
|---|---|
| `minecraft:health` | Vida máxima/atual |
| `minecraft:movement` | Velocidade base de movimento |
| `minecraft:physics` | Ativa gravidade e colisão |
| `minecraft:collision_box` | Tamanho da hitbox |
| `minecraft:type_family` | Categoriza a entidade (afeta o que a ataca/ignora) |
| `minecraft:navigation.walk` | Pathfinding terrestre |
| `minecraft:behavior.random_stroll` | Anda à toa quando ocioso |
| `minecraft:behavior.melee_attack` | Ataque corpo a corpo em alvo |
| `minecraft:attack` | Dano do ataque corpo a corpo |
| `minecraft:behavior.look_at_player` | Olha pro jogador próximo |

`component_groups` + `events` servem pra mudar o comportamento em runtime (ex: um mob pacífico que fica agressivo quando atacado — dispare o evento via `minecraft:behavior.hurt_by_target` ou pela Scripting API).

## 3. RP — `entity/custom_mob.json`

```json
{
    "format_version": "1.10.0",
    "minecraft:client_entity": {
        "description": {
            "identifier": "sonhe:custom_mob",
            "min_engine_version": "1.8.0",
            "materials": { "default": "entity_alphatest" },
            "textures": { "default": "textures/entity/custom_mob" },
            "geometry": { "default": "geometry.custom_mob" },
            "animations": {
                "walk": "animation.custom_mob.walk",
                "look_at_target": "animation.common.look_at_target"
            },
            "scripts": {
                "animate": ["walk", "look_at_target"]
            },
            "render_controllers": ["controller.render.custom_mob"],
            "spawn_egg": {
                "base_color": "#8B4513",
                "overlay_color": "#2E2E2E"
            }
        }
    }
}
```

Isso referencia três arquivos que você ainda precisa criar no RP (fora do escopo desta skill, mas obrigatórios pro mob aparecer):
- `models/entity/custom_mob.geo.json` (geometria — normalmente feita no Blockbench)
- `textures/entity/custom_mob.png`
- `animations/custom_mob.animation.json` + `render_controllers/custom_mob.render_controller.json` (pode reusar `controller.render.default` se o modelo for simples)

## 4. Idioma — adicione em `texts/en_US.lang` (nos dois packs, ou só no RP se preferir)

```
entity.sonhe:custom_mob.name=Custom Mob
item.spawn_egg.entity.sonhe:custom_mob.name=Custom Mob Spawn Egg
```

## 5. Testar

`/summon sonhe:custom_mob` no jogo (com Cheats ativado no mundo), ou dê o spawn egg pelo inventário criativo.

## 6. Loot table (opcional, se o mob deve dropar item ao morrer)

`loot_tables/entities/custom_mob.json`:
```json
{
    "pools": [
        {
            "rolls": 1,
            "entries": [
                { "type": "item", "name": "minecraft:feather", "weight": 1 }
            ]
        }
    ]
}
```
E referencie em `minecraft:loot` dentro do `components` do BP: `"minecraft:loot": { "table": "loot_tables/entities/custom_mob.json" }`.
