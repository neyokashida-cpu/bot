---
name: mcpe-custom-item
description: Cria um item customizado de Minecraft Bedrock (MCPE) no formato moderno data-driven (format_version 1.20+) — JSON do item, textura, ícone e entrada de idioma. Use quando o pedido for "criar um item novo", "criar uma arma/ferramenta/comida customizada" ou similar.
---

# Item customizado (Bedrock Add-On)

Baseado em bedrock.dev (Item Components / Item Format History) e Microsoft Learn (How to Add Custom Items), atualizado em 2026. Este é o formato **data-driven** moderno (pós-1.16.100) — evite o formato antigo baseado em `"minecraft:icon": {"texture": "..."}` isolado sem `description`/`components`, que está obsoleto.

## 1. BP — `items/custom_item.json`

```json
{
    "format_version": "1.21.30",
    "minecraft:item": {
        "description": {
            "identifier": "sonhe:custom_item",
            "menu_category": {
                "category": "items",
                "group": "itemGroup.name.misc"
            }
        },
        "components": {
            "minecraft:icon": "sonhe:custom_item",
            "minecraft:display_name": { "value": "item.sonhe:custom_item" },
            "minecraft:max_stack_size": 64,
            "minecraft:hand_equipped": false
        }
    }
}
```

### Componentes mais usados (referência rápida)

| Componente | Função | Exemplo |
|---|---|---|
| `minecraft:icon` | Textura do item na UI (referencia a chave em `item_texture.json` do RP) | `"sonhe:custom_item"` |
| `minecraft:display_name` | Chave de tradução do nome | `{"value": "item.sonhe:custom_item"}` |
| `minecraft:max_stack_size` | Tamanho máximo da pilha (1-64) | `64` |
| `minecraft:food` | Torna o item comestível | `{"nutrition": 3, "saturation_modifier": 0.6, "can_always_eat": false}` |
| `minecraft:durability` | Durabilidade (ferramentas/armas) | `{"max_durability": 250}` |
| `minecraft:hand_equipped` | Renderiza como ferramenta segurada na mão (3ª pessoa) | `true` |
| `minecraft:wearable` | Equipável como armadura | `{"slot": "slot.armor.head"}` |
| `minecraft:cooldown` | Delay de uso (tipo poção/elytra) | `{"category": "sonhe:habilidade", "duration": 1.5}` |
| `minecraft:use_animation` | Animação ao usar | `"eat"`, `"drink"`, `"bow"`, `"block"` |
| `minecraft:use_modifiers` | Tempo de uso (item carregável) | `{"use_duration": 1.0, "movement_modifier": 0.35}` |
| `minecraft:damage` | Dano de ataque corpo a corpo | `4` |
| `minecraft:enchantable` | Permite encantar | `{"slot": "sword", "value": 14}` |
| `minecraft:on_use` | Dispara evento customizado ao usar (combine com Scripting API) | `{"event": "sonhe:usou_item"}` |

Para arma/ferramenta: combine `minecraft:hand_equipped: true` + `minecraft:durability` + `minecraft:damage` + `minecraft:enchantable`.
Para comida: combine `minecraft:food` + `minecraft:use_animation: "eat"` + `minecraft:use_modifiers`.

## 2. RP — registrar a textura

`resource_pack/textures/item_texture.json`:
```json
{
    "resource_pack_name": "vanilla",
    "texture_name": "atlas.items",
    "texture_data": {
        "sonhe:custom_item": {
            "textures": "textures/items/custom_item"
        }
    }
}
```

E a imagem em `resource_pack/textures/items/custom_item.png` (16x16 ou 32x32, PNG com transparência).

## 3. Idioma — `texts/en_US.lang`

```
item.sonhe:custom_item.name=Custom Item
```

## 4. Receita (opcional)

Se o item deve ser craftável, crie `recipes/custom_item.json`:
```json
{
    "format_version": "1.21.50",
    "minecraft:recipe_shaped": {
        "description": { "identifier": "sonhe:custom_item" },
        "tags": ["crafting_table"],
        "pattern": ["AAA", "ABA", "AAA"],
        "key": {
            "A": { "item": "minecraft:iron_ingot" },
            "B": { "item": "minecraft:diamond" }
        },
        "result": { "item": "sonhe:custom_item" }
    }
}
```

## 5. Testar

`/give @s sonhe:custom_item` no jogo, ou procure pelo nome no inventário criativo (categoria definida em `menu_category`).
