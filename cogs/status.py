"""
SONHE — Status do servidor Minecraft (Bedrock, Aternos)
Ping externo via mcstatus (protocolo RakNet/Unconnected Ping-Pong) — roda
inteiramente do lado do bot Discord, sem depender de nada dentro do jogo
(sem @minecraft/server-net, sem RCON, sem acesso a arquivo do Aternos).

Mantém o embed fixo de #passagem (config.CHANNEL_PASSAGEM_ID) atualizado,
reaproveitando exatamente o mesmo formato/identidade visual já publicado
ali (autor "🌙 Sistema de Acesso", separadores ━━━, blocos de texto
Endereço/Porta/Status) — só o conteúdo muda entre online/offline.
"""

import logging

import discord
from discord import app_commands
from discord.ext import commands, tasks
from mcstatus import BedrockServer

import config

log = logging.getLogger("sonhe")

SEPARADOR = "━━━━━━━━━━━━━━━━━━━━ ✦ ━━━━━━━━━━━━━━━━━━━━"

# Mesma imagem já usada no embed original de #passagem (porta no meio do trigal).
# É um link de CDN do Discord assinado — pode expirar (ver memória do projeto).
THUMBNAIL_PASSAGEM = (
    "https://cdn.discordapp.com/attachments/1533795653812093020/1537423462841327646/"
    "iamages.png?ex=6a7efcad&is=6a7dab2d&"
    "hm=aafd861c26cd920f60986480ba8483d37579e93ca14e56b156b6b2057d742c22&"
)


async def consultar_status() -> dict | None:
    """dict com status, ou None se offline/não configurado/sem resposta (Aternos dorme quando vazio)."""
    if not config.MINECRAFT_SERVER_ADDRESS:
        return None
    try:
        servidor = BedrockServer.lookup(f"{config.MINECRAFT_SERVER_ADDRESS}:{config.MINECRAFT_SERVER_PORT}")
        resposta = await servidor.async_status()
        return {
            "atual": resposta.players.online,
            "maximo": resposta.players.max,
            "versao": resposta.version.name,
        }
    except Exception:
        log.info("Servidor Minecraft não respondeu ao ping (offline, dormindo ou endereço errado).")
        return None


def _embed_passagem(status: dict | None) -> discord.Embed:
    if status is None:
        descricao = (
            "A entrada para o mundo do SONHE ainda não está aberta.\n\n"
            "O servidor encontra-se em processo de construção e, por enquanto, não há "
            "um endereço público disponível para conexão.\n\n"
            f"{SEPARADOR}\n\n"
            "🌐 Endereço\n████████████████████\n\n"
            "🚪 Porta\n█████\n\n"
            "📡 Status\n🔴 Indisponível\n\n"
            "O endereço de acesso será disponibilizado aqui assim que a Primeira Passagem "
            "estiver pronta para receber novos exploradores.\n\n"
            "Não é necessário procurar por outro endereço ou solicitar acesso antecipadamente.\n\n"
            "Quando chegar a hora, você saberá.\n\n"
            f"{SEPARADOR}\n\n"
            "📋 Informações\n\n"
            "Plataforma: Minecraft Bedrock\n"
            "Acesso: Ainda indisponível\n"
            "Estado: Em construção\n\n"
            f"{SEPARADOR}\n\n"
            "Algumas portas precisam permanecer fechadas enquanto o lugar do outro lado "
            "ainda está sendo construído."
        )
    else:
        descricao = (
            "A Primeira Passagem está aberta.\n\n"
            "O SONHE está recebendo exploradores agora.\n\n"
            f"{SEPARADOR}\n\n"
            f"🌐 Endereço\n{config.MINECRAFT_SERVER_ADDRESS}\n\n"
            f"🚪 Porta\n{config.MINECRAFT_SERVER_PORT}\n\n"
            "📡 Status\n🟢 Online\n\n"
            f"👥 Sonhadores agora\n{status['atual']}/{status['maximo']}\n\n"
            f"{SEPARADOR}\n\n"
            "📋 Informações\n\n"
            "Plataforma: Minecraft Bedrock\n"
            f"Versão: {status['versao']}\n"
            "Estado: Aberto\n\n"
            f"{SEPARADOR}\n\n"
            "Copie o endereço e a porta exatamente como estão acima."
        )

    embed = discord.Embed(title="🚪 Primeira Passagem", description=descricao, color=config.COR_BOAS_VINDAS_1)
    embed.set_author(name="🌙 Sistema de Acesso")
    embed.set_thumbnail(url=THUMBNAIL_PASSAGEM)
    embed.set_footer(text="Projeto Sonhe • Created by Team ANÚBIS.")
    return embed


class Status(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self._mensagem_id: int | None = None
        self._ultimo_online: bool | None = None  # None = ainda não sabemos (primeira checagem)
        self.atualizar_passagem.start()

    def cog_unload(self):
        self.atualizar_passagem.cancel()

    @app_commands.command(name="status", description="Mostra se o servidor Minecraft do SONHE está online.")
    async def status(self, interaction: discord.Interaction):
        await interaction.response.defer()
        await interaction.followup.send(embed=_embed_passagem(await consultar_status()))

    @tasks.loop(minutes=5)
    async def atualizar_passagem(self):
        canal = self.bot.get_channel(config.CHANNEL_PASSAGEM_ID)
        if canal is None:
            return

        status = await consultar_status()

        await self._avisar_transicao(status is not None)

        embed = _embed_passagem(status)

        if self._mensagem_id is not None:
            try:
                msg = await canal.fetch_message(self._mensagem_id)
                await msg.edit(embed=embed)
                return
            except discord.NotFound:
                self._mensagem_id = None
            except discord.HTTPException:
                log.exception("Falha ao editar embed de #passagem.")
                return

        async for msg in canal.history(limit=20):
            if msg.author.id == self.bot.user.id:
                self._mensagem_id = msg.id
                await msg.edit(embed=embed)
                return

        self._mensagem_id = (await canal.send(embed=embed)).id

    @atualizar_passagem.before_loop
    async def _antes(self):
        await self.bot.wait_until_ready()

    async def _avisar_transicao(self, online_agora: bool):
        """Manda um aviso avulso no chat-mine só quando o status MUDA (não a cada 5 min)."""
        se_mudou = self._ultimo_online is not None and self._ultimo_online != online_agora
        self._ultimo_online = online_agora
        if not se_mudou:
            return

        canal = self.bot.get_channel(config.CHANNEL_CHAT_MINE_ID)
        if canal is None:
            return
        if online_agora:
            embed = discord.Embed(description="🟢 O servidor do SONHE está online.", color=0x57A64A)
        else:
            embed = discord.Embed(description="🔴 O servidor do SONHE saiu do ar.", color=0x8A8A8A)
        try:
            await canal.send(embed=embed)
        except discord.HTTPException:
            log.exception("Falha ao avisar transição de status no chat-mine.")


async def setup(bot: commands.Bot):
    await bot.add_cog(Status(bot))
