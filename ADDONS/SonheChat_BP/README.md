# SonheChat

Boas-vindas com contagem de jogadores + chat com Rank/Tag. Sem vinculação com o Discord ainda — Rank e Tag são atribuídos manualmente por um operador dentro do próprio mundo.

## Instalar (Aternos)

1. Compacte `SonheChat_BP/` e `SonheChat_RP/` cada uma como `.zip` e renomeie pra `.mcpack` (ou combine as duas num `.mcaddon`).
2. Em Aternos: aba do mundo → Addons → upload dos dois `.mcpack`.
3. **Importante:** o toggle "Beta APIs"/Experimental Gameplay só liga na criação do mundo. Se o mundo do SONHE já existe, é preciso recriar (ou testar antes num mundo à parte).

## Comandos do operador (precisa de cheats/OP)

Rank (`0`=Membro, `1`=Staff, `2`=Admin, `3`=Dono):
```
/scoreboard players set <jogador> sonhe_rank 2
```

Tag (`0`=sem tag, `1`=Recém-chegado, `2`=Explorador, `3`=Investigador, `4`=Guardião, `5`=Veterano, `6`=Lenda):
```
/scoreboard players set <jogador> sonhe_tag 6
```

Jogador sem rank/tag definido cai no padrão: rank Membro, sem tag.
