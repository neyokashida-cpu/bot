"""
SONHE — Chat humano (Madotsuki)
Responde quando: mencionam o bot, respondem a uma mensagem dele, ou mandam DM.

Usa a API da Anthropic direto (biblioteca `anthropic`), sem framework de agente —
é só uma chamada simples com histórico curto por canal/usuário, guardado em memória
(reseta se o bot reiniciar; não precisa de banco de dados pra isso).
"""

import asyncio
import random
import re
from collections import defaultdict, deque

import discord
from discord.ext import commands
from anthropic import AsyncAnthropic

import config
import database
from persona import SYSTEM_PROMPT

MAX_HISTORICO = 12  # quantidade de mensagens (usuário+bot) guardadas por conversa

# Gatilho de diagnóstico: só dispara com essa frase exata (nada mais, nada menos)
# e só pra Direção/ANÚBIS — evita que qualquer membro puxe a config interna do bot pelo chat.
FRASE_STATUS = "Mostre quem você é."

# Quando a API falha (ex: 529 Overloaded), manda uma dessas em vez de ficar
# digitando e não responder nada.
FALLBACKS_ERRO = [
    "ihh trava bugou aqui, manda de novo?",
    "eita, deu ruim aqui do meu lado. tenta outra vez",
    "travei no meio, manda de novo pra mim",
]


class Chat(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.client = AsyncAnthropic(api_key=config.ANTHROPIC_API_KEY, max_retries=4)
        self._iniciado_em = discord.utils.utcnow()
        # histórico por (canal_id, autor_id) — DM e canal de servidor tratados igual
        self.historico: dict[tuple[int, int], deque] = defaultdict(
            lambda: deque(maxlen=MAX_HISTORICO)
        )

    def _deve_responder(self, message: discord.Message) -> bool:
        if message.author.bot:
            return False
        if isinstance(message.channel, discord.DMChannel):
            return True
        if self.bot.user in message.mentions:
            return True
        if message.reference and message.reference.resolved:
            autor_da_msg_respondida = getattr(message.reference.resolved, "author", None)
            if autor_da_msg_respondida and autor_da_msg_respondida.id == self.bot.user.id:
                return True
        return False

    def _tem_algum_cargo(self, autor: discord.abc.User, cargos_ids: set[int]) -> bool:
        guild = self.bot.get_guild(config.GUILD_ID)
        if guild is None:
            return False
        membro = guild.get_member(autor.id)
        if membro is None:
            return False
        return any(cargo.id in cargos_ids for cargo in membro.roles)

    def _autorizado(self, autor: discord.abc.User) -> bool:
        return self._tem_algum_cargo(autor, {config.ROLE_ANUBIS_DONO_ID, config.ROLE_DIRECAO_ID})

    def _eh_administracao(self, autor: discord.abc.User) -> bool:
        return self._tem_algum_cargo(
            autor,
            {
                config.ROLE_ANUBIS_DONO_ID,
                config.ROLE_DIRECAO_ID,
                config.ROLE_GUARDA_ID,
                config.ROLE_RECEPCAO_ID,
            },
        )

    def _embed_status(self) -> discord.Embed:
        guild = self.bot.get_guild(config.GUILD_ID)
        uptime = discord.utils.utcnow() - self._iniciado_em
        horas, resto = divmod(int(uptime.total_seconds()), 3600)
        minutos = resto // 60

        embed = discord.Embed(
            title="Status atual — Sistema de Registro",
            color=config.COR_BOAS_VINDAS_1,
        )
        embed.add_field(
            name="🤖 Bot",
            value=(
                f"{self.bot.user} (ID `{self.bot.user.id}`)\n"
                f"Latência: {round(self.bot.latency * 1000)}ms\n"
                f"Online há: {horas}h{minutos:02d}\n"
                f"Cogs carregados: {', '.join(self.bot.cogs)}"
            ),
            inline=False,
        )

        if guild is not None:
            embed.add_field(
                name="🖥️ Servidor",
                value=f"{guild.name} (ID `{guild.id}`)\nMembros: {guild.member_count}",
                inline=False,
            )
            for titulo, prefixo in (("📺 Canais", "CHANNEL_"), ("🎭 Cargos", "ROLE_")):
                for i, bloco in enumerate(self._resolver(guild, prefixo)):
                    nome_campo = titulo if i == 0 else f"{titulo} (cont.)"
                    embed.add_field(name=nome_campo, value=bloco, inline=False)
        else:
            embed.add_field(name="🖥️ Servidor", value="⚠️ GUILD_ID não resolvido.", inline=False)

        embed.add_field(
            name="💬 Chat",
            value=f"Modelo: `{config.CLAUDE_MODEL}`\nConversas em memória: {len(self.historico)}",
            inline=False,
        )
        embed.set_footer(text="SONHE • Diagnóstico interno — visível só pra Direção/ANÚBIS")
        return embed

    @staticmethod
    def _resolver(guild: discord.Guild, prefixo: str) -> list[str]:
        linhas = []
        for nome, valor in vars(config).items():
            if not nome.startswith(prefixo) or not nome.endswith("_ID"):
                continue
            if not isinstance(valor, int) or valor == 0:
                linhas.append(f"⚠️ `{nome}` — não configurado")
                continue
            obj = guild.get_channel(valor) if prefixo == "CHANNEL_" else guild.get_role(valor)
            if obj is None:
                linhas.append(f"❌ `{nome}` (`{valor}`) — não encontrado")
            else:
                rotulo = f"#{obj.name}" if prefixo == "CHANNEL_" else obj.name
                linhas.append(f"✅ `{nome}` → {rotulo}")

        blocos, atual = [], ""
        for linha in linhas:
            candidata = f"{atual}\n{linha}" if atual else linha
            if len(candidata) > 1000:
                blocos.append(atual)
                atual = linha
            else:
                atual = candidata
        if atual:
            blocos.append(atual)
        return blocos

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if not self._deve_responder(message):
            return

        texto_limpo = re.sub(rf"<@!?{self.bot.user.id}>", "", message.content).strip()

        if texto_limpo == FRASE_STATUS and self._autorizado(message.author):
            await message.channel.send(embed=self._embed_status())
            return

        if not texto_limpo:
            texto_limpo = "(a pessoa só te mencionou/mandou mensagem sem texto, tipo só um oi)"

        cargo = "ADMIN" if self._eh_administracao(message.author) else "MEMBRO"
        texto_com_cargo = f"[CARGO:{cargo}] {texto_limpo}"

        chave = (message.channel.id, message.author.id)

        async with message.channel.typing():
            resposta = await self._gerar_resposta(chave, texto_com_cargo)

        if not resposta:
            await message.channel.send(random.choice(FALLBACKS_ERRO))
            return

        # Só grava os dois turnos no histórico depois de confirmar sucesso —
        # se a API falhar antes, não sobra um "user" sem par que quebraria a
        # alternância exigida pela Messages API na próxima chamada.
        self.historico[chave].append({"role": "user", "content": texto_com_cargo})
        self.historico[chave].append({"role": "assistant", "content": resposta})
        await database.ajustar_amizade(message.author.id, config.AMIZADE_POR_CONVERSA)

        # Quebra em mensagens curtas — gente real não manda um textão só.
        partes = self._quebrar_em_mensagens(resposta)
        for i, parte in enumerate(partes):
            if not parte:
                continue
            # delay curto entre mensagens seguidas, pra não parecer metralhadora
            if i > 0:
                await asyncio.sleep(random.uniform(0.8, 2.0))
                async with message.channel.typing():
                    await asyncio.sleep(min(len(parte) * 0.02, 1.5))
            await message.channel.send(parte)

    async def _gerar_resposta(self, chave, texto_novo: str) -> str | None:
        mensagens = [*self.historico[chave], {"role": "user", "content": texto_novo}]
        try:
            resposta = await self.client.messages.create(
                model=config.CLAUDE_MODEL,
                max_tokens=400,
                system=SYSTEM_PROMPT,
                messages=mensagens,
            )
        except Exception as e:
            print(f"[chat] erro na API da Anthropic: {e}")
            return None

        texto = "".join(
            bloco.text for bloco in resposta.content if getattr(bloco, "type", None) == "text"
        )
        return texto.strip()

    @staticmethod
    def _quebrar_em_mensagens(texto: str, limite: int = 300) -> list[str]:
        """Quebra por linha em branco/quebra natural; junta linhas curtas até o limite."""
        linhas = [l.strip() for l in texto.split("\n") if l.strip()]
        if not linhas:
            return [texto[:limite]]

        partes = []
        atual = ""
        for linha in linhas:
            candidata = f"{atual} {linha}".strip() if atual else linha
            if len(candidata) > limite:
                if atual:
                    partes.append(atual)
                atual = linha
            else:
                atual = candidata
        if atual:
            partes.append(atual)
        return partes


async def setup(bot: commands.Bot):
    await bot.add_cog(Chat(bot))
