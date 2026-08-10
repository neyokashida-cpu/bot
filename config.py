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
CLAUDE_MODEL = "claude-sonnet-5"

# ── Servidor ───────────────────────────────────────────
GUILD_ID = 1533795652600070174  # ID do servidor Discord do SONHE

# ── Canais · Despertar ─────────────────────────────────
CHANNEL_DESPERTAR_ID = 1533798154036580453        # 👋・despertar
CHANNEL_LEIA_ANTES_ID = 1534524827451527399       # 📖・leia-antes
CHANNEL_O_QUE_E_ISSO_ID = 1534525087254839356     # 📚・o-que-é-isso (fórum)
CHANNEL_NOVIDADES_ID = 1534524896191844392        # 📼・novidades
CHANNEL_PASSAGEM_ID = 1534524941968343150         # 🚪・passagem
CHANNEL_FACA_PARTE_ID = 1534524996507144252       # 🤝・faça-parte
CHANNEL_ADEUS_ID = 1534529010275582133            # 👋・adeus

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
CHANNEL_RECURSOS_ID = 1536365057800405052         # ⚖・recursos

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

# ── Cargos · Outros ─────────────────────────────────────
ROLE_PATRONO_ID = 1534589625681711296             # 💠 Patrono
ROLE_COLABORADOR_ID = 1534589644174266692         # 🎖️ Colaborador
ROLE_SILENCIADO_ID = 1534589657273077800          # 🔇 Silenciado
ROLE_AVISO_REGISTROS_ID = 1536365918916186242     # 📼 Aviso: Registros
ROLE_AVISO_PASSAGENS_ID = 1536365978365988894     # 🚪 Aviso: Passagens

# ── Tickets ──────────────────────────────────────────────
# Categoria onde os canais de ticket são criados. 0 = cria na raiz do servidor.
CATEGORY_TICKETS_ID = 0

# ── Imagens (10.1) ──────────────────────────────────────
# Panorâmica da rua do Subúrbio ao fim de tarde.
PANORAMA_SUBURBIO_URL = "https://SEU-LINK-AQUI/panoramica.png"

# ── Cores dos embeds (nunca alterar — 10.1 / 10.2) ─────
COR_BOAS_VINDAS_1 = 0x1B1F3B
COR_BOAS_VINDAS_2 = 0x0B0C10

# ── Mascote / narradora do sistema ─────────────────────
# Nome exibido como autor dos embeds institucionais.
NOME_SISTEMA = "🌙 Sistema de Registro"
NOME_REGISTRO_AUTOMATICO = "📁 Registro Automático"
