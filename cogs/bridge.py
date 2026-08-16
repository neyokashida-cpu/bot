"""
SONHE — Ponte de chat Discord <-> Minecraft
Não expõe slash commands: sobe um servidor HTTP (aiohttp) dentro do próprio
processo do bot, na porta que o Railway definir em $PORT.

Sentido Minecraft -> Discord:
  O addon SonheBridge_BP faz POST /minecraft-chat a cada mensagem de chat.
  Esse handler repassa pro canal 💬・sala-de-estar.

Sentido Discord -> Minecraft:
  Mensagens mandadas em 💬・sala-de-estar entram numa fila em memória.
  O addon faz GET /discord-queue a cada poucos segundos (polling — o
  Bedrock Dedicated Server não aceita conexão de entrada, só consegue puxar).
  Cada GET esvazia a fila (fire-and-forget: só existe um Minecraft
  consumindo, então não precisa de confirmação separada).

IMPORTANTE — isso depende de @minecraft/server-net, que em ago/2026 ainda é
pré-lançamento e só funciona se o permissions.json do servidor Bedrock
liberar o módulo (ver auditoria do projeto). Enquanto isso não estiver
confirmado do lado do jogo, esse servidor HTTP sobe normalmente mas
simplesmente não recebe nenhum POST — não quebra nada.
"""

import asyncio
import logging
import os
from collections import deque

import discord
from aiohttp import web
from discord.ext import commands

import config

log = logging.getLogger("sonhe")

TAMANHO_MAX_FILA = 100  # evita crescer sem limite se o Minecraft ficar offline


class Bridge(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.fila_para_minecraft: deque[dict] = deque(maxlen=TAMANHO_MAX_FILA)
        self._runner: web.AppRunner | None = None

    # ── ciclo de vida do cog ────────────────────────────────
    async def cog_load(self):
        app = web.Application(middlewares=[self._middleware_auth])
        app.router.add_post("/minecraft-chat", self._handler_minecraft_chat)
        app.router.add_get("/discord-queue", self._handler_discord_queue)
        app.router.add_get("/health", self._handler_health)

        self._runner = web.AppRunner(app)
        await self._runner.setup()
        porta = int(os.getenv("PORT", "8080"))
        site = web.TCPSite(self._runner, "0.0.0.0", porta)
        await site.start()
        log.info(f"Bridge HTTP escutando na porta {porta}")

    async def cog_unload(self):
        if self._runner:
            await self._runner.cleanup()

    # ── autenticação ─────────────────────────────────────────
    @web.middleware
    async def _middleware_auth(self, request: web.Request, handler):
        if request.path == "/health":
            return await handler(request)
        if not config.BRIDGE_SECRET:
            return web.json_response({"erro": "BRIDGE_SECRET não configurado no bot"}, status=503)
        if request.headers.get("Authorization") != f"Bearer {config.BRIDGE_SECRET}":
            return web.json_response({"erro": "não autorizado"}, status=401)
        return await handler(request)

    # ── handlers ─────────────────────────────────────────────
    async def _handler_health(self, request: web.Request):
        return web.json_response({"status": "ok"})

    async def _handler_minecraft_chat(self, request: web.Request):
        try:
            dados = await request.json()
            jogador = str(dados["jogador"])[:32]
            mensagem = str(dados["mensagem"])[:400]
        except (ValueError, KeyError, TypeError):
            return web.json_response({"erro": "corpo inválido — esperado {jogador, mensagem}"}, status=400)

        rank = str(dados.get("rank", ""))[:32]
        tag = str(dados.get("tag", ""))[:32]
        prefixo = f"**[{tag}]** " if tag else ""

        canal = self.bot.get_channel(config.CHANNEL_SALA_DE_ESTAR_ID)
        if canal is None:
            log.warning("Bridge: CHANNEL_SALA_DE_ESTAR_ID não resolveu — bot ainda não conectou?")
            return web.json_response({"erro": "canal do Discord indisponível"}, status=503)

        texto = f"🌙 {prefixo}**{jogador}**\n{discord.utils.escape_markdown(mensagem)}"
        await canal.send(texto[:2000])
        return web.json_response({"ok": True})

    async def _handler_discord_queue(self, request: web.Request):
        mensagens = list(self.fila_para_minecraft)
        self.fila_para_minecraft.clear()
        return web.json_response({"mensagens": mensagens})

    # ── Discord -> fila (consumida pelo addon via polling) ───
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.channel.id != config.CHANNEL_SALA_DE_ESTAR_ID:
            return
        if message.author.bot:
            return
        if not message.content:
            return
        self.fila_para_minecraft.append(
            {"autor": message.author.display_name[:32], "mensagem": message.content[:400]}
        )


async def setup(bot: commands.Bot):
    await bot.add_cog(Bridge(bot))
