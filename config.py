"""
SONHE — Configuração do Bot (ANÚBIS)
Preencha tudo abaixo com os IDs reais do seu Discord.
Como pegar um ID: Configurações do Discord > Avançado > Modo Desenvolvedor (ativar),
depois clique com botão direito no canal/cargo > "Copiar ID".
"""

import os
from dotenv import load_dotenv

load_dotenv()

# ── Token ──────────────────────────────────────────────
BOT_TOKEN = os.getenv("BOT_TOKEN")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
BRIDGE_SECRET = os.getenv("BRIDGE_SECRET")  # autentica as chamadas addon -> bridge HTTP
CLAUDE_MODEL = "claude-sonnet-5"

# ── Servidor ───────────────────────────────────────────
GUILD_ID = 1533795652600070174  # ID do servidor Discord do SONHE

# ── Servidor Minecraft (Bedrock, Aternos) ──────────────
# Preencher com o endereço/porta reais quando disponíveis (cogs/status.py).
# A porta do Aternos free pode mudar a cada reinício do servidor — conferir
# no painel do Aternos sempre que o servidor for reiniciado do zero.
MINECRAFT_SERVER_ADDRESS = "plus-09.bedhosting.com.br"
MINECRAFT_SERVER_PORT = 20110

# ── Canais · Despertar ─────────────────────────────────
CHANNEL_DESPERTAR_ID = 1533798154036580453        # 👋・despertar
CHANNEL_LEIA_ANTES_ID = 1534524827451527399       # 📖・leia-antes
CHANNEL_O_QUE_E_ISSO_ID = 1534525087254839356     # 📚・o-que-é-isso (fórum)
CHANNEL_NOVIDADES_ID = 1534524896191844392        # 📼・novidades
CHANNEL_PASSAGEM_ID = 1534524941968343150         # 🚪・passagem
CHANNEL_CHAT_MINE_ID = 1538219830040076308                           # TODO: cole aqui o ID real do canal chat-mine
CHANNEL_FACA_PARTE_ID = 1534524996507144252       # 🤝・faça-parte
CHANNEL_ADEUS_ID = 1534529010275582133            # 👋・adeus
CHANNEL_COMANDOS_ID = 1537496944010854521         # 👾・comandos

# ── Canais · Primeira Passagem ─────────────────────────
CHANNEL_SALA_DE_ESTAR_ID = 1536364174211424256    # 💬・sala-de-estar
CHANNEL_ESTATICA_ID = 1536364238958760028         # 📺・estática
CHANNEL_GALERIA_ID = 1536364269912727594          # 🖼️・galeria
CHANNEL_REGISTROS_AUTOMATICOS_ID = 1536364297624494170  # 🎲・registros-automáticos

# ── Canais · Expedição ─────────────────────────────────
CHANNEL_RELATORIOS_DE_CAMPO_ID = 1536364536129396747    # 🗺️・relatórios-de-campo (fórum)
CHANNEL_COORDENADAS_ID = 1536364561899327568      # 🧭・coordenadas
CHANNEL_CONFLITOS_ID = 1536364586544930846        # ⚔・conflitos
CHANNEL_TROCAS_ID = 1536364616282677298           # 🛒・trocas

# ── Canais · Arquivos ───────────────────────────────────
CHANNEL_ABRIR_REGISTRO_ID = 1536364975961018428   # 🎫・abrir-registro
CHANNEL_SUGESTOES_ID = 1536365009792274542        # 📮・sugestões
CHANNEL_OCORRENCIAS_ID = 1536365032428806175      # 🐞・ocorrências

# ── Canais de voz · Silêncio ────────────────────────────
CHANNEL_VOZ_SALA_DE_ESTAR_ID = 1536365242701844491      # 🔊 Sala de Estar
CHANNEL_VOZ_EXPEDICAO_01_ID = 1536365288424218825       # 🔊 Expedição 01
CHANNEL_VOZ_SALA_RESERVADA_ID = 1536365321672466505     # 🔊 Sala Reservada
CHANNEL_VOZ_AFK_ID = 1536365354299822204                # 🔇 Silêncio (AFK)

# ── Canais · ANÚBIS (privada) ──────────────────────────
CHANNEL_QUADRO_GERAL_ID = 1536365632403017792     # 📌・quadro-geral
CHANNEL_MODERACAO_ID = 1536365658919669781        # 🔨・moderação
CHANNEL_LOGS_ID = 1536365691224195113             # 📊・logs
CHANNEL_TESTES_ID = 1536365717442531339           # 🧪・testes
CHANNEL_ARQUIVO_MORTO_ID = 1536365743619178508    # 🗂・arquivo-morto
CHANNEL_VOZ_REUNIAO_ID = 1536365768541732864      # 🔊 Reunião

# ── Cargos · Bots ───────────────────────────────────────
ROLE_MADOTSUKI_ID = 1536345387827339348           # Madotsuki (bot próprio)
ROLE_LORITTA_ID = 1533799254760489084             # Loritta
ROLE_SISTEMAS_ID = 1534589285054025758            # Sistemas

# ── Cargos · ANÚBIS (staff) ─────────────────────────────
ROLE_ANUBIS_DONO_ID = 1534589369711726794         # 👑 ANÚBIS
ROLE_DIRECAO_ID = 1534589402917900318             # 🛡️ Direção
ROLE_GUARDA_ID = 1534589426737479901              # ⚙️ Guarda
ROLE_RECEPCAO_ID = 1534589442994733067            # 🤝 Recepção

# ── Cargos · Expedição (progressão por XP) ─────────────
ROLE_RECEM_CHEGADO_ID = 1534589591342813386       # 👋 Recém-chegado (0)
ROLE_EXPLORADOR_ID = 1534589548363907373          # 🧭 Explorador (5)
ROLE_INVESTIGADOR_ID = 1534589533943890062        # 🔍 Investigador (15)
ROLE_GUARDIAO_DE_PASSAGENS_ID = 1534589518668107816     # 🗝️ Guardião de Passagens (30)
ROLE_VETERANO_ID = 1534589502578888804            # 🌙 Veterano da Expedição (50)
ROLE_LENDA_DO_SONHE_ID = 1534589483356524717      # ⭐ Lenda do Sonhe (75)

# ── Progressão por XP — nível mínimo → cargo ───────────
# Usado pelo /perfil e pelo ganho de XP por mensagem (cogs/economia.py).
NIVEIS_XP = (
    (0, ROLE_RECEM_CHEGADO_ID, "👋 Recém-chegado"),
    (5, ROLE_EXPLORADOR_ID, "🧭 Explorador"),
    (15, ROLE_INVESTIGADOR_ID, "🔍 Investigador"),
    (30, ROLE_GUARDIAO_DE_PASSAGENS_ID, "🗝️ Guardião de Passagens"),
    (50, ROLE_VETERANO_ID, "🌙 Veterano da Expedição"),
    (75, ROLE_LENDA_DO_SONHE_ID, "⭐ Lenda do Sonhe"),
)

# ── Economia (Statz) ────────────────────────────────────
NOME_MOEDA = "Statz"
EMOJI_MOEDA = "⭐"

XP_POR_MENSAGEM = 1
STATZ_POR_MENSAGEM = (1, 5)          # min, max — sorteado a cada mensagem válida
COOLDOWN_MENSAGEM_ECONOMIA = 60      # segundos entre ganhos por mensagem

DAILY_STATZ = (50, 150)              # min, max — sorteado a cada /daily

CUSTO_CASAMENTO = 10_000             # cada lado paga esse valor (pedir e aceitar)

# ── Amizade (nível de interação com a Madotsuki) ────────
AMIZADE_POR_CONVERSA = 2             # ganho por troca de mensagem no chat (cogs/chat.py)
NIVEIS_AMIZADE = (
    (0, "🌫️ Desconhecidos"),
    (10, "🌙 Conhecidos"),
    (50, "✨ Amigos"),
    (150, "💛 Amigos de verdade"),
    (400, "🌌 Melhores amigos"),
)

# ── Mines ────────────────────────────────────────────────
MINES_TAMANHO_TABULEIRO = 16          # 4x4
MINES_PADRAO_QTD_MINAS = 3
MINES_MIN_MINAS = 1
MINES_MAX_MINAS = 10
MINES_HOUSE_EDGE = 0.03               # 3% de margem da casa nos multiplicadores

# ── Cargos · Outros ─────────────────────────────────────
ROLE_PATRONO_ID = 1534589625681711296             # 💠 Patrono
ROLE_COLABORADOR_ID = 1534589644174266692         # 🎖️ Colaborador
ROLE_SILENCIADO_ID = 1534589657273077800          # 🔇 Silenciado
ROLE_AVISO_REGISTROS_ID = 1536365918916186242     # 📼 Aviso: Registros
ROLE_AVISO_PASSAGENS_ID = 1536365978365988894     # 🚪 Aviso: Passagens

# ── Cargos · Separadores de perfil ──────────────────────
# Cargos sem permissão, só pra organizar a lista de cargos visualmente.
# Todo membro (novo ou já existente) deve ter os três.
ROLE_DIVISOR_ANUBIS_ID = 1534589310454595744      # ── ANÚBIS ──
ROLE_DIVISOR_EXPEDICAO_ID = 1534589463806607500   # ── Expedição (progressão) ──
ROLE_DIVISOR_OUTROS_ID = 1534589608187138128      # ── Outros ──
CARGOS_SEPARADORES = (ROLE_DIVISOR_ANUBIS_ID, ROLE_DIVISOR_EXPEDICAO_ID, ROLE_DIVISOR_OUTROS_ID)

# ── Tickets ──────────────────────────────────────────────
# Categoria onde os canais de ticket são criados. 0 = cria na raiz do servidor.
CATEGORY_TICKETS_ID = 0

# ── Imagens (10.1) ──────────────────────────────────────
# Logo do estúdio ANÚBIS (rodapé dos embeds institucionais).
ANUBIS_LOGO_URL = (
    "https://cdn.discordapp.com/attachments/1533795653812093020/1536400314570113064/"
    "images.png?ex=6a7b43cb&is=6a79f24b&hm=f64e44011a91d9138c6cf377f701d0b359a16fc7210c16fb67d1661aeb52a1ef&"
)

# Panorâmica da rua do Subúrbio ao fim de tarde. Vazio = embed sem imagem (não quebra o send).
PANORAMA_SUBURBIO_URL = (
    "https://cdn.discordapp.com/attachments/1533795653812093020/1536402628051869857/"
    "images_4.jfif?ex=6a7b45f3&is=6a79f473&"
    "hm=ee6ece24f90a31d3b0096118b1afda1177f703750d47de87a2f41193381b772c"
)

# Boneco de erro 404 (embed de saída — 👋・adeus).
IMAGEM_ERRO_404_URL = (
    "https://cdn.discordapp.com/attachments/1533795653812093020/1534527848683929600/"
    "images-removebg-preview.png?ex=6a7effed&is=6a7dae6d&"
    "hm=a71561b42b231f46982cd93008316378dd4602afbd0a63238f1ffba32f7daa82"
)

# ── Cores dos embeds (nunca alterar — 10.1 / 10.2) ─────
COR_BOAS_VINDAS_1 = 0x1B1F3B
COR_BOAS_VINDAS_2 = 0x0B0C10
COR_ADEUS = 0x0B0C10

# Lavanda enevoada — usada nos sistemas novos (perfil, economia, mines).
# Separada das cores institucionais acima (essas nunca mudam, ver spec 10.1/10.2).
COR_DREAMCORE = 0xB9A7D9

# ── Mascote / narradora do sistema ─────────────────────
# Nome exibido como autor dos embeds institucionais.
NOME_SISTEMA = "🌙 Sistema de Registro"
NOME_REGISTRO_AUTOMATICO = "📁 Registro Automático"
