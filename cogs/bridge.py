"""
SONHE — Ponte de chat Discord <-> Minecraft
Não expõe slash commands: sobe um servidor HTTP (aiohttp) dentro do próprio
processo do bot, na porta que o Railway definir em $PORT.

Sentido Minecraft -> Discord:
  O addon SonheBridge_BP faz POST /minecraft-chat a cada mensagem de chat, e
  POST /minecraft-morte quando um jogador morre. As mensagens de chat são
  enviadas via WEBHOOK (nome + avatar do jogador), pra parecer que é a
  pessoa mesma falando no canal — não o bot. Mensagens de morte/status vão
  como mensagem normal do bot, por serem mais "narração" que "fala".

  Avatar: se o jogador tiver vínculo CONFIRMADO (/admin link), usa a foto de
  perfil do Discord dele. Senão, tenta renderizar a skin Bedrock de verdade
  via mc-heads.net (que consulta a GeyserMC pra contas Bedrock/Xbox); se
  isso falhar por qualquer motivo, o pior caso é só um avatar quebrado no
  Discord — não afeta o envio da mensagem.

Sentido Discord -> Minecraft:
  Mensagens mandadas em 💬・chat-mine entram numa fila em memória. O addon
  faz GET /discord-queue a cada poucos segundos (polling — o Bedrock
  Dedicated Server não aceita conexão de entrada, só consegue puxar). Cada
  GET esvazia a fila. Mensagens vindas do PRÓPRIO webhook são ignoradas
  (senão a mensagem do jogador voltaria pro jogo como se fosse do Discord —
  ver _eco_do_webhook).

IMPORTANTE — tudo isso depende de @minecraft/server-net, que em ago/2026
ainda é pré-lançamento (ver auditoria do projeto). Enquanto isso não
estiver confirmado do lado do jogo, esse servidor HTTP sobe normalmente mas
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
import database

log = logging.getLogger("sonhe")

TAMANHO_MAX_FILA = 100  # evita crescer sem limite se o Minecraft ficar offline
NOME_WEBHOOK = "SONHE — Minecraft"


def _avatar_skin_bedrock(nome_jogador: str) -> str:
    """Tenta renderizar a skin real (via GeyserMC); mc-heads.net cai pro Steve padrão sozinho se não achar."""
    return f"https://mc-heads.net/avatar/.{nome_jogador}/100"


class Bridge(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.fila_para_minecraft: deque[dict] = deque(maxlen=TAMANHO_MAX_FILA)
        self._runner: web.AppRunner | None = None
        self._webhooks_cache: dict[int, discord.Webhook] = {}

    # ── ciclo de vida do cog ────────────────────────────────
    async def cog_load(self):
        app = web.Application(middlewares=[self._middleware_auth])
        app.router.add_post("/minecraft-chat", self._handler_minecraft_chat)
        app.router.add_post("/minecraft-morte", self._handler_minecraft_morte)
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

    # ── avatar + webhook ─────────────────────────────────────
    async def _resolver_avatar(self, nome_jogador: str) -> str:
        vinculo = await database.obter_vinculo_confirmado_por_nome(nome_jogador)
        if vinculo:
            try:
                usuario = self.bot.get_user(vinculo["user_id"]) or await self.bot.fetch_user(vinculo["user_id"])
                if usuario:
                    return str(usuario.display_avatar.url)
            except discord.NotFound:
                pass
        return _avatar_skin_bedrock(nome_jogador)

    async def _obter_webhook(self, canal: discord.TextChannel) -> discord.Webhook | None:
        if canal.id in self._webhooks_cache:
            return self._webhooks_cache[canal.id]
        try:
            for wh in await canal.webhooks():
                if wh.name == NOME_WEBHOOK:
                    self._webhooks_cache[canal.id] = wh
                    return wh
            wh = await canal.create_webhook(name=NOME_WEBHOOK, reason="Ponte de chat SONHE <-> Minecraft")
            self._webhooks_cache[canal.id] = wh
            return wh
        except discord.Forbidden:
            log.warning("Bridge: sem permissão 'Gerenciar Webhooks' no canal chat-mine.")
            return None

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

        tag = str(dados.get("tag", ""))[:32]

        canal = self.bot.get_channel(config.CHANNEL_CHAT_MINE_ID)
        if canal is None:
            log.warning("Bridge: CHANNEL_CHAT_MINE_ID não resolveu — ID errado ou bot ainda não conectou?")
            return web.json_response({"erro": "canal do Discord indisponível"}, status=503)

        webhook = await self._obter_webhook(canal)
        nome_exibido = f"{tag} {jogador}".strip() if tag else jogador
        texto = discord.utils.escape_markdown(mensagem)[:2000]

        try:
            if webhook:
                await webhook.send(
                    content=texto,
                    username=nome_exibido[:80],
                    avatar_url=await self._resolver_avatar(jogador),
                )
            else:
                # Sem permissão de webhook: cai pro envio normal do bot, sem spoofing.
                await canal.send(f"**{nome_exibido}**\n{texto}")
        except discord.HTTPException:
            log.exception("Bridge: falha ao enviar mensagem do Minecraft pro Discord.")
            return web.json_response({"erro": "falha ao enviar"}, status=502)

        return web.json_response({"ok": True})

    async def _handler_minecraft_morte(self, request: web.Request):
        try:
            dados = await request.json()
            mensagem = str(dados["mensagem"])[:200]
        except (ValueError, KeyError, TypeError):
            return web.json_response({"erro": "corpo inválido — esperado {jogador, mensagem}"}, status=400)

        canal = self.bot.get_channel(config.CHANNEL_CHAT_MINE_ID)
        if canal is None:
            return web.json_response({"erro": "canal do Discord indisponível"}, status=503)

        try:
            await canal.send(f"💀 {mensagem}")
        except discord.HTTPException:
            log.exception("Bridge: falha ao enviar mensagem de morte pro Discord.")
            return web.json_response({"erro": "falha ao enviar"}, status=502)

        return web.json_response({"ok": True})

    async def _handler_discord_queue(self, request: web.Request):
        mensagens = list(self.fila_para_minecraft)
        self.fila_para_minecraft.clear()
        return web.json_response({"mensagens": mensagens})

    # ── Discord -> fila (consumida pelo addon via polling) ───
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.channel.id != config.CHANNEL_CHAT_MINE_ID:
            return
        if message.author.bot:
            return
        if message.webhook_id is not None:
            # Eco do próprio webhook (Minecraft -> Discord) — se não filtrar
            # isso, a mensagem do jogador voltaria pro jogo como se fosse
            # alguém no Discord respondendo a si mesmo.
            return
        if not message.content:
            return
        self.fila_para_minecraft.append(
            {"autor": message.author.display_name[:32], "mensagem": message.content[:400]}
        )


async def setup(bot: commands.Bot):
    await bot.add_cog(Bridge(bot))
