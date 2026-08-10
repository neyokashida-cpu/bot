# SONHE — Bot (Greet + Verificação)

Primeira parte do bot próprio: recebe quem chega e libera acesso depois da leitura das diretrizes.

## O que já faz
- **Greet automático** (`cogs/greet.py`): quando alguém entra, ganha o cargo `👋 Recém-chegado` e recebe os 2 embeds oficiais em `👋・despertar` (specs 10.1 e 10.2 do manual).
- **Botão de aceite** (`cogs/verification.py`): botão "Registrar leitura" em `📖・leia-antes` que troca `👋 Recém-chegado` por `🧭 Explorador`, com resposta privada (efêmera).

## Setup

1. Crie o bot em https://discord.com/developers/applications
   - Ative os **Privileged Gateway Intents** → `SERVER MEMBERS INTENT` (obrigatório pro greet funcionar).
   - Copie o Token.
2. Instale as dependências:
   ```
   pip install -r requirements.txt
   ```
3. Copie `.env.example` para `.env` e cole o token:
   ```
   cp .env.example .env
   ```
4. Ative o **Modo Desenvolvedor** no Discord (Configurações > Avançado) e preencha todos os IDs em `config.py`:
   - `GUILD_ID`
   - IDs dos canais (`despertar`, `leia-antes`, `o-que-é-isso`, `novidades`, `passagem`, `faça-parte`)
   - IDs dos cargos (`Recém-chegado`, `Explorador`)
   - `PANORAMA_SUBURBIO_URL` — link direto de uma imagem (ex: hospedada no Imgur ou GitHub)
5. Convide o bot pro servidor com permissão de **Gerenciar Cargos** e **Enviar Mensagens**.
   - Importante: o cargo do bot precisa estar **acima** de `👋 Recém-chegado` e `🧭 Explorador` na lista de cargos, senão ele não consegue atribuir/remover.
6. Rode:
   ```
   python main.py
   ```

## Como enviar o botão de aceite

O botão não aparece sozinho — ele precisa ser postado uma vez, manualmente, depois dos 3 embeds de diretrizes (10.3, 10.4, 10.5) já estarem em `📖・leia-antes`.

Como administrador, digite no próprio canal `📖・leia-antes`:
```
!enviar_aceite
```
O bot apaga o comando e posta o botão no lugar. Depois disso, ele fica ativo pra sempre (view persistente — sobrevive a restart do bot).

## Teste antes de abrir ao público
1. Entre com uma conta secundária → confirme que os 2 embeds aparecem em `👋・despertar` e que o cargo `Recém-chegado` foi atribuído.
2. Clique em "Registrar leitura" → confirme a resposta efêmera e a troca de cargo.
3. Clique de novo → confirme que ele avisa "leitura já registrada" e não duplica nada.

## Próximos módulos (na ordem que você escolher)
- Sistema de tickets (`🎫・abrir-registro`)
- Sistema de nível/XP
- Vínculo de conta Minecraft ↔ Discord

Cada um vira um novo cog em `cogs/`, sem tocar no que já existe.
