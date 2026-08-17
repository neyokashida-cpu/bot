"""
SONHE — Status do servidor Minecraft (Bedrock, Aternos)
Fonte principal: heartbeat do SonheBridge_BP (cogs/bridge.py), mandado por
HTTP de dentro do jogo — canal comprovadamente confiável (mesmo usado por
/minecraft-entrou e /discord-queue). Fallback: ping externo via mcstatus
(protocolo RakNet/Unconnected Ping-Pong), usado só se o heartbeat nunca
chegou (ex: addon antigo, ou bridge acabou de subir). O ping externo por
UDP costuma dar timeout dependendo da rede de saída do host do bot — por
isso não é mais a fonte primária.

Mantém o embed fixo de #passagem (config.CHANNEL_PASSAGEM_ID) atualizado,
reaproveitando exatamente o mesmo formato/identidade visual já publicado
ali (autor "🌙 Sistema de Acesso", separadores ━━━, blocos de texto
Endereço/Porta/Status) — só o conteúdo muda entre online/offline.
"""

import logging
import random

import discord
from discord import app_commands
from discord.ext import commands, tasks
from mcstatus import BedrockServer

import config
import database

CHAVE_ESTADO_MENSAGEM = "passagem_mensagem_id"

log = logging.getLogger("sonhe")

SEPARADOR = "━━━━━━━━━━━━━━━━━━━━ ✦ ━━━━━━━━━━━━━━━━━━━━"

# Pool de imagens pra quando o servidor está OFFLINE/dormindo — tema "acordar
# do sonho" (o jogo te força a acordar). Sorteada tanto no embed fixo de
# #passagem quanto no aviso avulso de "saiu do ar" no chat-mine.
THUMBNAILS_PASSAGEM_OFFLINE = (
    "https://cdn.discordapp.com/attachments/1533795653812093020/1538951904061821018/"
    "ac4.jfif?ex=6a848c26&is=6a833aa6&hm=0ddeafbac281c87ee4425a404b698379090633dba532d4374bc24e610d08c0c9&",
    "https://cdn.discordapp.com/attachments/1533795653812093020/1538951904363806832/"
    "ac3.jfif?ex=6a848c26&is=6a833aa6&hm=534bb7a50c6597c5d510faa3f54b3674e3690eb5e4ba22450974173a9775676f&",
    "https://cdn.discordapp.com/attachments/1533795653812093020/1538951904753619114/"
    "ac2.jfif?ex=6a848c26&is=6a833aa6&hm=fc93376ae4b03171a61744975d650837b502c9b671f2c9e52b7cfd9dc43b75b4&",
    "https://cdn.discordapp.com/attachments/1533795653812093020/1538951905118658620/"
    "ac.jfif?ex=6a848c26&is=6a833aa6&hm=bf5ae6da7e502f6ddcb26612a6af13b7cfad4ee8b0fb3360de31699ace7dd6a8&",
    "https://cdn.discordapp.com/attachments/1533795653812093020/1538952272376242286/"
    "images_6.jfif?ex=6a848c7e&is=6a833afe&hm=c2d7cdecf2b8791e4b6f403fac6b811f787537851228af234cc48467e655ef22&",
)

# Pool de imagens pra quando o servidor está ONLINE — sorteia uma a cada
# atualização do embed, pra não ficar sempre com a mesma thumbnail.
THUMBNAILS_PASSAGEM_ONLINE = (
    "https://cdn.discordapp.com/attachments/1533795653812093020/1538950865476526200/"
    "ab2.png?ex=6a848b2e&is=6a8339ae&hm=2f69382d1c7ed9198e5998ef6b242ae5dfc1db40fb3030c5de706d9ec6c84753&",
    "https://cdn.discordapp.com/attachments/1533795653812093020/1538950865006755981/"
    "ab3.png?ex=6a848b2e&is=6a8339ae&hm=231d1aef26af19e29696d6ec16c110343f9b8025ab9e8bedcd1a5344321d8f2c&",
    "https://cdn.discordapp.com/attachments/1533795653812093020/1538950864503312434/"
    "ab4.png?ex=6a848b2e&is=6a8339ae&hm=8e94f3c2ee4da533570d1c6b8b49d50b31aeff9d3a18c0e67f2f07336b0832cb&",
)


async def consultar_status(bot: commands.Bot) -> dict | None:
    """dict com status, ou None se offline/não configurado/sem resposta (Aternos dorme quando vazio)."""
    bridge = bot.get_cog("Bridge")
    if bridge is not None:
        info = bridge.status_via_heartbeat()
        if info is not None:
            return info

    if not config.MINECRAFT_SERVER_ADDRESS:
        return None
    try:
        servidor = BedrockServer.lookup(
            f"{config.MINECRAFT_SERVER_ADDRESS}:{config.MINECRAFT_SERVER_PORT}", timeout=8
        )
        resposta = await servidor.async_status()
        return {
            "atual": resposta.players.online,
            "maximo": resposta.players.max,
            "versao": resposta.version.name,
        }
    except Exception as e:
        log.info(f"Servidor Minecraft não respondeu ao ping ({type(e).__name__}: {e}).")
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
            f"Versão: {status.get('versao') or '—'}\n"
            "Estado: Aberto\n\n"
            f"{SEPARADOR}\n\n"
            "Copie o endereço e a porta exatamente como estão acima."
        )

    thumbnail = random.choice(THUMBNAILS_PASSAGEM_ONLINE if status is not None else THUMBNAILS_PASSAGEM_OFFLINE)

    embed = discord.Embed(title="🚪 Primeira Passagem", description=descricao, color=config.COR_BOAS_VINDAS_1)
    embed.set_author(name="🌙 Sistema de Acesso")
    embed.set_thumbnail(url=thumbnail)
    embed.set_footer(text="Projeto Sonhe • Created by Team ANÚBIS.")
    return embed


class Status(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self._mensagem_id: int | None = None
        self._ultimo_online: bool = False  # assume offline até a 1ª checagem — se já estiver online, isso conta como transição e dispara o aviso bonito
        self.atualizar_passagem.start()

    def cog_unload(self):
        self.atualizar_passagem.cancel()

    @app_commands.command(name="status", description="Mostra se o servidor Minecraft do SONHE está online.")
    async def status(self, interaction: discord.Interaction):
        await interaction.response.defer()
        await interaction.followup.send(embed=_embed_passagem(await consultar_status(self.bot)))

    @tasks.loop(minutes=5)
    async def atualizar_passagem(self):
        canal = self.bot.get_channel(config.CHANNEL_PASSAGEM_ID)
        if canal is None:
            return

        status = await consultar_status(self.bot)

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

        # Sem ID em memória (1ª rodada após restart) — tenta o scan de
        # histórico como último recurso antes de assumir que precisa criar
        # uma mensagem nova (evita duplicar o embed fixo a cada deploy).
        async for msg in canal.history(limit=20):
            if msg.author.id == self.bot.user.id:
                await self._salvar_mensagem_id(msg.id)
                await msg.edit(embed=embed)
                return

        await self._salvar_mensagem_id((await canal.send(embed=embed)).id)

    async def _salvar_mensagem_id(self, mensagem_id: int):
        self._mensagem_id = mensagem_id
        await database.definir_estado(CHAVE_ESTADO_MENSAGEM, str(mensagem_id))

    @atualizar_passagem.before_loop
    async def _antes(self):
        await self.bot.wait_until_ready()
        valor = await database.obter_estado(CHAVE_ESTADO_MENSAGEM)
        if valor is not None:
            self._mensagem_id = int(valor)

    async def _avisar_transicao(self, online_agora: bool):
        """Manda um aviso avulso no chat-mine só quando o status MUDA (não a cada 5 min)."""
        se_mudou = self._ultimo_online != online_agora
        self._ultimo_online = online_agora
        if not se_mudou:
            return

        canal = self.bot.get_channel(config.CHANNEL_CHAT_MINE_ID)
        if canal is None:
            return
        if online_agora:
            embed = discord.Embed(
                title="🚪 A Primeira Passagem abriu",
                description="O servidor do SONHE está online. Bora explorar! 🟢",
                color=0x57A64A,
            )
            embed.set_thumbnail(url=random.choice(THUMBNAILS_PASSAGEM_ONLINE))
        else:
            embed = discord.Embed(
                title="🚪 A Primeira Passagem fechou",
                description="O sonho te soltou por agora. Volta mais tarde. 🔴",
                color=0x8A8A8A,
            )
            embed.set_thumbnail(url=random.choice(THUMBNAILS_PASSAGEM_OFFLINE))
        embed.set_footer(text="Projeto Sonhe • Created by Team ANÚBIS.")
        try:
            await canal.send(embed=embed)
        except discord.HTTPException:
            log.exception("Falha ao avisar transição de status no chat-mine.")


async def setup(bot: commands.Bot):
    await bot.add_cog(Status(bot))
