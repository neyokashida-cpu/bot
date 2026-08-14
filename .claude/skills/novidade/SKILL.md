---
name: novidade
description: Publica um embed de atualização em #novidades quando uma mecânica ou funcionalidade nova do SONHE for definida/implementada na conversa. Invocado com /novidade.
---

# /novidade — Update do SONHE

Quando o usuário disparar `/novidade`, poste um embed de atualização no canal
`#novidades` (`config.CHANNEL_NOVIDADES_ID`, atualmente `1534524896191844392`)
usando a ferramenta MCP `mcp__sonhe-discord__send_embed`.

## Passos

1. Leia o contador em `.claude/skills/novidade/counter.txt` (um número inteiro puro,
   ex: `3`). Se o arquivo não existir ou estiver vazio, comece do `0`.
2. Incremente +1 e formate com 3 dígitos (`001`, `012`, `123`...).
3. Grave o novo valor de volta no arquivo (sobrescreva com o número puro, sem `#`
   e sem zero-padding — ex: grave `4`, não `#004`).
4. Componha o embed com base no que foi **realmente** definido/construído na
   conversa até aqui. Nunca invente funcionalidade que não foi implementada.

## Formato do embed

- `channel_id`: `1534524896191844392`
- `author_name`: `🐺 Team ANÚBIS`
- `title`: `📼 Atualização #{numero-com-3-digitos}`
- `description`: tom humano, caloroso, com postura — como uma equipe real
  contando o que fez, não um changelog técnico seco. Estrutura sugerida:
  - abertura curta e pessoal
  - o que foi definido/construído (bullets ou parágrafos curtos)
  - por que isso importa pro projeto (conecta com a identidade do SONHE
    quando fizer sentido, sem forçar lore)
  - fechamento com reconhecimento/compromisso — mostra que a equipe se
    importa, sem soar corporativo
- `footer`: `Projeto Sonhe • Created by Team ANÚBIS.`
- `thumbnail_url`: mesma capa institucional usada nos outros embeds
  (`ANUBIS_LOGO_URL` em `config.py`) — manter consistência visual.
- `color`: `1774139` (mesma paleta institucional dos outros embeds do
  projeto — não inventar cor nova sem pedir).

## Regras

- Nunca pule número nem reaproveite um número já usado.
- Nunca marque como "novidade" algo que ainda não foi implementado de
  verdade na conversa/código.
- Tom acolhedor mas sóbrio — nada de emoji em excesso, nada de linguagem
  de marketing.
- Se o canal não for encontrado ou o envio falhar, avise o usuário — não
  finja que funcionou.
