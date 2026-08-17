"""
SONHE — Ponte de chat Discord <-> Minecraft
Não expõe slash commands de chat: sobe um servidor HTTP (aiohttp) dentro do
próprio processo do bot, na porta que o Railway definir em $PORT. Só expõe
/inventario como slash command (ver seção "Inventário" abaixo).

Sentido Minecraft -> Discord:
  O addon SonheBridge_BP faz POST pro bot em cada evento:
    /minecraft-chat                  — mensagem de chat (webhook, nome+avatar do jogador)
    /minecraft-morte                 — morte de jogador (embed)
    /minecraft-entrou / -saiu        — entrada/saída no mundo (embed, mensagem sorteada)
    /minecraft-vincular-solicitar    — pedido de código pro /vincular (ver vinculacao.py)
    /minecraft-inventario-resposta   — resposta a um pedido de /inventario

  Avatar do webhook: se o jogador tiver vínculo CONFIRMADO, usa a foto de
  perfil do Discord dele. Senão, tenta renderizar a skin Bedrock de verdade
  via mc-heads.net; se falhar, o pior caso é só um avatar quebrado — não
  afeta o envio da mensagem.

Sentido Discord -> Minecraft:
  Mensagens mandadas em 💬・chat-mine E pedidos de /inventario entram numa
  fila em memória (fila_para_minecraft). O addon faz GET /discord-queue a
  cada poucos segundos (polling — o Bedrock Dedicated Server não aceita
  conexão de entrada, só consegue puxar). Cada item tem um campo "tipo" pra
  o addon saber o que fazer: "mensagem" (mostra no chat) ou
  "inventario_request" (lê o inventário do jogador citado e responde em
  /minecraft-inventario-resposta). Mensagens vindas do PRÓPRIO webhook são
  ignoradas (ver _eco_do_webhook em on_message).

Inventário (/inventario):
  Como o servidor não aceita conexão de entrada, o bot não "pergunta" na
  hora — ele bota o pedido na fila e ESPERA (com timeout) a resposta chegar
  pelo próximo ciclo de polling do addon. Por isso pode levar alguns
  segundos, e só funciona com o jogador online no mundo (leitura ao vivo do
  inventário — sem acesso a arquivo, não dá pra ler o inventário de quem tá
  offline). É somente leitura: não existe nenhum endpoint pra alterar item.

IMPORTANTE — tudo isso depende de @minecraft/server-net, que em ago/2026
ainda é pré-lançamento (ver auditoria do projeto). Enquanto isso não
estiver confirmado do lado do jogo, esse servidor HTTP sobe normalmente mas
simplesmente não recebe nenhum POST — não quebra nada.
"""

import asyncio
import logging
import os
import random
import uuid
from collections import deque

import discord
from aiohttp import web
from discord import app_commands
from discord.ext import commands

import config
import database

log = logging.getLogger("sonhe")

TAMANHO_MAX_FILA = 100  # evita crescer sem limite se o Minecraft ficar offline
NOME_WEBHOOK = "SONHE — Minecraft"
TIMEOUT_INVENTARIO_SEGUNDOS = 10.0

MENSAGENS_ENTROU = [
    "{jogador} atravessou a passagem e chegou ao SONHE.",
    "{jogador} acordou dentro do sonho.",
    "{jogador} entrou — mais um sonhador no mundo.",
    "{jogador} cruzou a porta. Bem-vindo(a) de volta.",
    "{jogador} apareceu entre a névoa.",
    "{jogador} chegou. O mundo fica um pouco mais cheio.",
    "{jogador} pisou no SONHE novamente.",
    "{jogador} entrou no mundo — que sonho vai viver hoje?",
    "{jogador} surgiu do outro lado da passagem.",
    "{jogador} está de volta ao SONHE.",
]

MENSAGENS_SAIU = [
    "{jogador} atravessou a passagem de volta.",
    "{jogador} saiu do sonho, por enquanto.",
    "{jogador} desapareceu na névoa.",
    "{jogador} deixou o SONHE.",
    "{jogador} fechou os olhos e foi embora.",
    "{jogador} saiu — até a próxima passagem.",
    "{jogador} voltou pro mundo real.",
    "{jogador} desconectou do sonho.",
    "{jogador} se foi, o SONHE continua sonhando.",
    "{jogador} saiu do mundo.",
]


def _avatar_skin_bedrock(nome_jogador: str) -> str:
    """Tenta renderizar a skin real (via GeyserMC); mc-heads.net cai pro Steve padrão sozinho se não achar."""
    return f"https://mc-heads.net/avatar/.{nome_jogador}/100"


class Bridge(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.fila_para_minecraft: deque[dict] = deque(maxlen=TAMANHO_MAX_FILA)
        self._pedidos_inventario: dict[str, asyncio.Future] = {}
        self._runner: web.AppRunner | None = None
        self._webhooks_cache: dict[int, discord.Webhook] = {}

    # ── ciclo de vida do cog ────────────────────────────────
    async def cog_load(self):
        app = web.Application(middlewares=[self._middleware_auth])
        app.router.add_post("/minecraft-chat", self._handler_minecraft_chat)
        app.router.add_post("/minecraft-morte", self._handler_minecraft_morte)
        app.router.add_post("/minecraft-entrou", self._handler_minecraft_entrou)
        app.router.add_post("/minecraft-saiu", self._handler_minecraft_saiu)
        app.router.add_post("/minecraft-vincular-solicitar", self._handler_vincular_solicitar)
        app.router.add_post("/minecraft-inventario-resposta", self._handler_inventario_resposta)
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
        for futuro in self._pedidos_inventario.values():
            if not futuro.done():
                futuro.cancel()

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

    def _canal_chat_mine(self) -> discord.TextChannel | None:
        canal = self.bot.get_channel(config.CHANNEL_CHAT_MINE_ID)
        if canal is None:
            log.warning("Bridge: CHANNEL_CHAT_MINE_ID não resolveu — ID errado ou bot ainda não conectou?")
        return canal

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

        canal = self._canal_chat_mine()
        if canal is None:
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
            return web.json_response({"erro": "corpo inválido — esperado {mensagem}"}, status=400)

        canal = self._canal_chat_mine()
        if canal is None:
            return web.json_response({"erro": "canal do Discord indisponível"}, status=503)

        embed = discord.Embed(description=f"💀 {mensagem}", color=0x2B2D31)
        try:
            await canal.send(embed=embed)
        except discord.HTTPException:
            log.exception("Bridge: falha ao enviar mensagem de morte pro Discord.")
            return web.json_response({"erro": "falha ao enviar"}, status=502)

        return web.json_response({"ok": True})

    async def _handler_minecraft_entrou(self, request: web.Request):
        return await self._handler_transicao_jogador(request, MENSAGENS_ENTROU, cor=0x57A64A)

    async def _handler_minecraft_saiu(self, request: web.Request):
        return await self._handler_transicao_jogador(request, MENSAGENS_SAIU, cor=0x8A8A8A)

    async def _handler_transicao_jogador(self, request: web.Request, modelos: list[str], cor: int):
        try:
            dados = await request.json()
            jogador = str(dados["jogador"])[:32]
        except (ValueError, KeyError, TypeError):
            return web.json_response({"erro": "corpo inválido — esperado {jogador}"}, status=400)

        canal = self._canal_chat_mine()
        if canal is None:
            return web.json_response({"erro": "canal do Discord indisponível"}, status=503)

        texto = random.choice(modelos).format(jogador=f"**{jogador}**")
        embed = discord.Embed(description=texto, color=cor)
        embed.set_thumbnail(url=await self._resolver_avatar(jogador))
        embed.set_footer(text="Projeto Sonhe • Created by Team ANÚBIS.")
        try:
            await canal.send(embed=embed)
        except discord.HTTPException:
            log.exception("Bridge: falha ao enviar aviso de entrada/saída no chat-mine.")
            return web.json_response({"erro": "falha ao enviar"}, status=502)

        return web.json_response({"ok": True})

    async def _handler_vincular_solicitar(self, request: web.Request):
        try:
            dados = await request.json()
            jogador = str(dados["jogador"])[:32]
            moedas = int(dados.get("moedas", 0))
        except (ValueError, KeyError, TypeError):
            return web.json_response({"erro": "corpo inválido — esperado {jogador}"}, status=400)

        codigo = await database.criar_codigo_vinculo(jogador, max(moedas, 0))
        return web.json_response({"codigo": codigo})

    async def _handler_inventario_resposta(self, request: web.Request):
        try:
            dados = await request.json()
            pedido_id = str(dados["id"])
        except (ValueError, KeyError, TypeError):
            return web.json_response({"erro": "corpo inválido — esperado {id}"}, status=400)

        futuro = self._pedidos_inventario.get(pedido_id)
        if futuro is None or futuro.done():
            # Resposta atrasada (ninguém mais espera, o /inventario já deu timeout) — ignora.
            return web.json_response({"ok": True})

        if "erro" in dados:
            futuro.set_result({"erro": str(dados["erro"])[:200]})
        else:
            futuro.set_result({"itens": dados.get("itens", [])})
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
            {"tipo": "mensagem", "autor": message.author.display_name[:32], "mensagem": message.content[:400]}
        )

    # ── /inventario ──────────────────────────────────────────
    @app_commands.command(
        name="inventario", description="Vê o inventário do Minecraft de alguém vinculado (somente leitura)."
    )
    @app_commands.describe(membro="Ver o inventário de outra pessoa (opcional)")
    async def inventario(self, interaction: discord.Interaction, membro: discord.Member | None = None):
        alvo = membro or interaction.user
        perfil = await database.obter_perfil(alvo.id)
        if perfil["minecraft_status"] != "confirmado":
            await interaction.response.send_message(
                "Essa conta não tem um Minecraft vinculado (`/vincular`).", ephemeral=True
            )
            return

        await interaction.response.defer()

        pedido_id = uuid.uuid4().hex
        futuro = asyncio.get_running_loop().create_future()
        self._pedidos_inventario[pedido_id] = futuro
        self.fila_para_minecraft.append(
            {"tipo": "inventario_request", "id": pedido_id, "jogador": perfil["minecraft_nome"]}
        )

        try:
            resultado = await asyncio.wait_for(futuro, timeout=TIMEOUT_INVENTARIO_SEGUNDOS)
        except asyncio.TimeoutError:
            await interaction.followup.send(
                "Não consegui puxar o inventário a tempo — o jogador precisa estar online no "
                "servidor Minecraft agora. Tenta de novo em alguns segundos."
            )
            return
        finally:
            self._pedidos_inventario.pop(pedido_id, None)

        if resultado.get("erro"):
            await interaction.followup.send(f"Não deu: {resultado['erro']}")
            return

        embed = self._montar_embed_inventario(alvo, perfil["minecraft_nome"], resultado.get("itens", []))
        await interaction.followup.send(embed=embed)

    def _montar_embed_inventario(self, alvo: discord.abc.User, nome_minecraft: str, itens: list[dict]) -> discord.Embed:
        embed = discord.Embed(
            title=f"🎒 Inventário de {nome_minecraft}",
            color=config.COR_DREAMCORE,
            description="Somente leitura — direto do jogo agora.",
        )
        embed.set_thumbnail(url=alvo.display_avatar.url)

        secoes: dict[str, list[str]] = {}
        for item in itens:
            secao = str(item.get("secao", "Inventário"))
            nome = str(item.get("nome", "?"))
            qtd = item.get("quantidade", 1)
            secoes.setdefault(secao, []).append(f"{nome} ×{qtd}" if qtd and qtd > 1 else nome)

        if not secoes:
            embed.add_field(name="Inventário", value="Vazio.", inline=False)
        else:
            for secao, linhas in secoes.items():
                embed.add_field(name=secao, value="\n".join(linhas)[:1024], inline=False)

        embed.set_footer(text="Projeto Sonhe • Created by Team ANÚBIS.")
        return embed


async def setup(bot: commands.Bot):
    await bot.add_cog(Bridge(bot))
