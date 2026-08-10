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
from persona import SYSTEM_PROMPT

MAX_HISTORICO = 12  # quantidade de mensagens (usuário+bot) guardadas por conversa


class Chat(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.client = AsyncAnthropic(api_key=config.ANTHROPIC_API_KEY)
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

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if not self._deve_responder(message):
            return

        texto_limpo = re.sub(rf"<@!?{self.bot.user.id}>", "", message.content).strip()
        if not texto_limpo:
            texto_limpo = "(a pessoa só te mencionou/mandou mensagem sem texto, tipo só um oi)"

        chave = (message.channel.id, message.author.id)
        self.historico[chave].append({"role": "user", "content": texto_limpo})

        async with message.channel.typing():
            resposta = await self._gerar_resposta(chave, message.author.display_name)

        if resposta is None:
            return

        self.historico[chave].append({"role": "assistant", "content": resposta})

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

    async def _gerar_resposta(self, chave, nome_usuario: str) -> str | None:
        mensagens = list(self.historico[chave])
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
