# SonheChat

Boas-vindas com contagem de jogadores + chat com Rank/Tag. Rank e Tag são
atribuídos manualmente por um operador dentro do próprio mundo (via
`/scoreboard`). A vinculação com o Discord (`!vincular` no jogo, `/vincular`
no Discord) é feita pelo pack `SonheBridge_BP`, não por este pack.

## Instalar (Aternos)

1. Compacte `SonheChat_BP/` e `SonheChat_RP/` cada uma como `.zip` e renomeie pra `.mcpack` (ou combine as duas num `.mcaddon`).
2. Em Aternos: aba do mundo → Addons → upload dos dois `.mcpack`.
3. **Importante:** o toggle "Beta APIs"/Experimental Gameplay só liga na criação do mundo. Se o mundo do SONHE já existe, é preciso recriar (ou testar antes num mundo à parte).

## Comandos do operador (precisa de cheats/OP)

Rank (`0`=Visitante, `1`=Membro, `2`=Staff, `3`=Admin, `4`=Dono):
```
/scoreboard players set <jogador> sonhe_rank 2
```

Tag (`0`=sem tag, `1`=Recém-chegado, `2`=Explorador, `3`=Investigador, `4`=Guardião, `5`=Veterano, `6`=Lenda):
```
/scoreboard players set <jogador> sonhe_tag 6
```

Jogador sem rank/tag definido cai no padrão: rank Visitante, sem tag.

Com `SonheBridge_BP` instalado, rank e tag passam a ser setados
automaticamente pelo Discord no `/vincular` e a cada level up — os comandos
acima continuam funcionando pra ajuste manual quando necessário.
