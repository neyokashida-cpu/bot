"""
SONHE — Greet + Autorole
Spec: manual 9.4-A (Greet), 9.4-B (Autorole), 10.1 e 10.2 (embeds).

Ao entrar um membro:
1. Recebe o cargo 👋 Recém-chegado (delay 0).
2. O canal 👋・despertar recebe o embed de boas-vindas, sem ping fora do embed.
Nunca deletar essas mensagens.
3. O canal 💬・sala-de-estar recebe uma reação curta e aleatória à chegada.
"""

import logging
import random

import discord
from discord.ext import commands

import config

log = logging.getLogger("sonhe")

# Mensagens de reação à chegada, enviadas em #sala-de-estar.
# Cada uma usa {mention} exatamente uma vez. Para adicionar/editar, basta
# alterar esta lista — a seleção aleatória e o envio já cobrem o resto.
MENSAGENS_SALA_DE_ESTAR = [
    # 🌙 Acolhedoras
    "👋 Todo mundo, deem boas-vindas para {mention}!",
    "🌙 {mention} acabou de chegar. Seja bem-vindo!",
    "✨ Olha quem apareceu: {mention}!",
    "🏡 {mention} chegou na sala de estar.",
    "☕ {mention} chegou. Alguém oferece um café?",
    "👋 Bem-vindo, {mention}! Sinta-se em casa.",
    "🌙 Seja bem-vindo(a), {mention}.",
    "✨ Mais um explorador chegou: {mention}.",
    "🏡 Façam espaço no sofá, {mention} chegou.",
    "👋 {mention} entrou. Bom te ver por aqui.",
    # 📁 Temáticas
    "🌙 {mention} adormeceu. Seja bem-vindo.",
    "🚪 {mention} encontrou a Primeira Passagem.",
    "🌾 {mention} acaba de atravessar o campo.",
    "📖 Um novo nome foi adicionado aos registros: {mention}.",
    "🌫️ {mention} surgiu através da neblina.",
    "📁 Registro iniciado para {mention}.",
    "🌙 {mention} chegou. O sonho continua.",
    "🚪 A porta estava aberta. {mention} decidiu entrar.",
    "📡 Sinal identificado. {mention} está entre nós.",
    "👁️ {mention} abriu os olhos.",
    "🌙 Mais um sonhador encontrou o caminho: {mention}.",
    "🗺️ {mention} chegou de uma expedição desconhecida.",
    # 👁️ Estranhas
    "👁️ {mention} chegou. Não olhe para trás.",
    "🌙 {mention} acordou no lugar errado.",
    "📺 A televisão mudou de canal quando {mention} entrou.",
    "🌫️ Ninguém viu {mention} chegar.",
    "📡 ...sinal estabilizado. Era só {mention} chegando.",
    "👁️ Alguém percebeu que {mention} chegou.",
    "🌾 O campo estava vazio até alguns segundos atrás. Agora {mention} está aqui.",
    "📁 {mention} foi encontrado e registrado.",
    "🌙 Não sabemos de onde {mention} veio.",
    "🕯️ A luz piscou quando {mention} entrou.",
    # 🏡 Cotidianas
    "☕ {mention} chegou bem na hora do café.",
    "🛋️ {mention} acabou de se acomodar no sofá.",
    "📺 {mention} chegou no meio do episódio.",
    "🌧️ {mention} entrou fugindo da chuva lá fora.",
    "🍞 {mention} chegou e já perguntou onde fica a cozinha.",
    "🧦 {mention} entrou de meias, sem fazer barulho.",
    "🪟 Alguém abriu a janela quando {mention} chegou.",
    "📻 O rádio estava tocando quando {mention} entrou.",
    "🕰️ {mention} chegou pontualmente, como sempre.",
    "🧺 {mention} entrou carregando algo que ninguém viu direito.",
    # 🐸 Aleatórias / engraçadas
    "🍪 {mention} chegou. Alguém escondeu os biscoitos.",
    "🛋️ {mention} oficialmente ocupou um lugar no sofá.",
    "👀 {mention} apareceu. Finjam que está tudo normal.",
    "☕ {mention} chegou. Café?",
    "📺 {mention} chegou bem na hora da televisão.",
    "🐸 Um sapo cruzou a sala quando {mention} entrou. Coincidência.",
    "🍕 {mention} chegou. Alguém pediu pizza?",
    "🎉 {mention} entrou e ninguém estava pronto pra festa.",
]


class Greet(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self._ultima_mensagem_sala_de_estar = None

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        if member.guild.id != config.GUILD_ID:
            return

        # 9.4-B — Autorole, delay 0: Recém-chegado + separadores de perfil
        ids_para_novo_membro = (config.ROLE_RECEM_CHEGADO_ID, *config.CARGOS_SEPARADORES)
        cargos = [
            role
            for role_id in ids_para_novo_membro
            if (role := member.guild.get_role(role_id)) is not None
        ]
        if cargos:
            try:
                await member.add_roles(*cargos, reason="Chegada registrada — Sistema de Registro")
            except discord.Forbidden:
                pass

        # Reação de chegada em #sala-de-estar — ação independente do fluxo abaixo.
        await self._enviar_mensagem_sala_de_estar(member)

        canal = member.guild.get_channel(config.CHANNEL_DESPERTAR_ID)
        if canal is None:
            return

        embed1 = self._embed_boas_vindas_1(member)
        try:
            await canal.send(embed=embed1)
        except discord.HTTPException:
            log.exception("Falha ao enviar embed de boas-vindas para %s", member)

    async def _enviar_mensagem_sala_de_estar(self, member: discord.Member):
        canal = member.guild.get_channel(config.CHANNEL_SALA_DE_ESTAR_ID)
        if canal is None:
            log.warning(
                "Canal sala-de-estar (%s) não encontrado — mensagem de chegada não enviada para %s",
                config.CHANNEL_SALA_DE_ESTAR_ID,
                member,
            )
            return

        mensagem = random.choice(MENSAGENS_SALA_DE_ESTAR)
        tentativas = 0
        while mensagem == self._ultima_mensagem_sala_de_estar and tentativas < 5:
            mensagem = random.choice(MENSAGENS_SALA_DE_ESTAR)
            tentativas += 1
        self._ultima_mensagem_sala_de_estar = mensagem

        try:
            await canal.send(mensagem.format(mention=member.mention))
        except discord.HTTPException:
            log.exception("Falha ao enviar mensagem de sala-de-estar para %s", member)

    def _embed_boas_vindas_1(self, member: discord.Member) -> discord.Embed:
        guild = member.guild

        descricao = (
            f"||{member.mention}||\n\n"
            f"Sua chegada ao **{guild.name}** foi registrada.\n\n"
            "Este projeto nasceu com um único objetivo:\n"
            "transformar a sensação de um sonho em um lugar.\n\n"
            "Antes de iniciar sua travessia, reserve alguns minutos para conhecer o que existe aqui.\n\n"
            "━━━━━━━━━━━━━━━ <a:Nuvens_Rosa:1536408683880124496> ━━━━━━━━━━━━━━━\n\n"
            f"📖 Diretrizes da Expedição — <#{config.CHANNEL_LEIA_ANTES_ID}>\n"
            f"📚 Arquivos e documentação — <#{config.CHANNEL_O_QUE_E_ISSO_ID}>\n"
            f"📼 Registros de Desenvolvimento — <#{config.CHANNEL_NOVIDADES_ID}>\n"
            f"🚪 Acesso à Primeira Passagem — <#{config.CHANNEL_PASSAGEM_ID}>\n"
            f"🤝 Como contribuir — <#{config.CHANNEL_FACA_PARTE_ID}>\n\n"
            "━━━━━━━━━━━━━━━━ <a:Nuvens:1536408711386632263> ━━━━━━━━━━━━━━━━\n\n"
            "🌙 Bons sonhos. <a:Patrick:1536408771335557140>"
        )

        embed = discord.Embed(
            title=f"Bem-vindo(a), {member.name}.",
            description=descricao,
            color=config.COR_BOAS_VINDAS_1,
        )
        embed.set_author(
            name=config.NOME_SISTEMA,
            icon_url=member.guild.icon.url if member.guild.icon else None,
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        if config.PANORAMA_SUBURBIO_URL:
            embed.set_image(url=config.PANORAMA_SUBURBIO_URL)
        embed.set_footer(
            text="ANUBIS• A jornada está apenas começando.",
            icon_url=config.ANUBIS_LOGO_URL,
        )

        embed.add_field(name="👤 Explorador", value=member.mention, inline=True)
        embed.add_field(name="📊 Exploradores", value=str(member.guild.member_count), inline=True)
        embed.add_field(name="🌾 Estado", value="Em desenvolvimento", inline=True)

        return embed

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        if member.guild.id != config.GUILD_ID:
            return

        canal = member.guild.get_channel(config.CHANNEL_ADEUS_ID)
        if canal is None:
            return

        embed = self._embed_sinal_perdido(member)
        try:
            await canal.send(embed=embed)
        except discord.HTTPException:
            log.exception("Falha ao enviar embed de saída para %s", member)

    def _embed_sinal_perdido(self, member: discord.Member) -> discord.Embed:
        descricao = (
            "**Sinal perdido.**\n\n"
            f"Perdemos contato com ★ | {member.display_name}.\n\n"
            "Não foi possível determinar se o explorador retornou ao mundo real...\n\n"
            "...ou apenas encontrou outro caminho."
        )

        embed = discord.Embed(description=descricao, color=config.COR_ADEUS)
        embed.set_author(name=config.NOME_SISTEMA)
        embed.set_thumbnail(url=config.IMAGEM_ERRO_404_URL)
        embed.set_footer(
            text="Projeto Sonhe • Created by Team ANÚBIS.",
            icon_url=config.ANUBIS_LOGO_URL,
        )

        return embed


async def setup(bot: commands.Bot):
    await bot.add_cog(Greet(bot))
