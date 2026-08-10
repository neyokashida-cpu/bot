"""
SONHE — Diretrizes (leia-antes)
Spec: manual 10.3 (Discord), 10.4 (Servidor), 10.5 (Conclusao).

Postar nesta ordem, uma vez, dentro de 📖・leia-antes.
Só depois desses 3 embeds o !enviar_aceite (cogs/verification.py) faz sentido no mesmo canal.
"""

import discord
from discord.ext import commands

import config

COR_DIRETRIZES = 0x1B1F3B
COR_CONCLUSAO = 0xE0A860


class Regras(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="enviar_diretrizes")
    @commands.has_permissions(administrator=True)
    async def enviar_diretrizes(self, ctx: commands.Context):
        """
        Comando manual, só pra Direção: posta os 3 embeds de diretrizes no canal atual.
        Use uma vez em 📖・leia-antes, antes do !enviar_aceite.
        """
        for embed in (self._embed_discord(), self._embed_servidor(), self._embed_conclusao()):
            await ctx.send(embed=embed)
        await ctx.message.delete()

    def _embed_discord(self) -> discord.Embed:
        descricao = (
            "A leitura destas diretrizes é obrigatória e vale para todos os canais.\n\n"
            "**1 · Respeito é condição de permanência**\n"
            "Racismo, nazismo, homofobia, transfobia, xenofobia, capacitismo e apologia a "
            "qualquer forma de violência resultam em banimento imediato e permanente, sem "
            "aviso e sem recurso.\n\n"
            "**2 · Assédio não é opinião**\n"
            "Perseguição, ameaça, exposição de dados pessoais e insistência após recusa "
            "resultam em banimento.\n\n"
            "**3 · Conteúdo adulto é proibido**\n"
            "Nudez, conteúdo sexual explícito e gore não têm lugar em nenhum canal.\n\n"
            "**4 · Use o canal correto**\n"
            "Cada canal existe por um motivo. O motivo está no tópico do canal.\n\n"
            "**5 · Sem divulgação sem autorização**\n"
            "Convites de outros servidores, links de venda e propaganda dependem de "
            "autorização prévia da Direção.\n\n"
            "**6 · Conflito se resolve com a Expedição, não em público**\n"
            f"Abra um registro em <#{config.CHANNEL_ABRIR_REGISTRO_ID}>. Discussão pública sobre "
            "punição de terceiros será removida.\n\n"
            "**7 · Uma conta por pessoa**\n"
            "Contas alternativas para burlar punição resultam em banimento de todas as "
            "contas envolvidas.\n\n"
            "━━━━━━━━━━━━━━━━━━━━ ✦ ━━━━━━━━━━━━━━━━━━━━\n\n"
            "Desconhecer uma diretriz não isenta de sua aplicação."
        )
        embed = discord.Embed(title="Diretrizes do Discord", description=descricao, color=COR_DIRETRIZES)
        embed.set_author(name="📖 Diretrizes da Expedição")
        embed.set_footer(text="SONHE • Diretrizes — Documento 01 de 03")
        return embed

    def _embed_servidor(self) -> discord.Embed:
        descricao = (
            "O SONHE é um **survival semi-anárquico de exploração**.\n"
            "Há liberdade real. Há limites reais. Os dois são levados a sério.\n\n"
            "**O QUE É PERMITIDO**\n\n"
            "**1 · PvP é livre**\n"
            "Combate entre exploradores é permitido em qualquer lugar fora das áreas "
            "protegidas.\n\n"
            "**2 · Grief é permitido fora das áreas protegidas**\n"
            "Destruir, saquear e alterar construções alheias é permitido. Construir longe "
            "é decisão estratégica, não motivo de reclamação.\n\n"
            "**3 · Roubo, traição e emboscada são permitidos**\n"
            "Confiança é sua responsabilidade. A Expedição não intermedeia acordos entre "
            "exploradores.\n\n"
            "**4 · Você pode construir dentro dos Sonhos**\n"
            "Fora do Trecho Registrado, o Subúrbio é seu. Construa, quebre, ocupe, dispute.\n\n"
            "━━━━━━━━━━━━━━━━━━━━ ✦ ━━━━━━━━━━━━━━━━━━━━\n\n"
            "**O QUE É PROIBIDO**\n\n"
            "**5 · Áreas protegidas são intocáveis**\n"
            "A Primeira Passagem, o Trecho Registrado do Subúrbio e toda estrutura de "
            "Passagem são intocáveis: sem quebrar, sem construir, sem PvP. Tentativa de "
            "burlar a proteção resulta em banimento.\n\n"
            "**6 · Cheats e vantagens externas**\n"
            "Client modificado, X-ray, macro, fly, kill aura, ESP e similares resultam em "
            "**banimento permanente na primeira ocorrência**. Sem aviso, sem recurso.\n\n"
            "**7 · Exploits e duplicação**\n"
            "Uso de falha do jogo ou do servidor para duplicar itens ou travar o servidor "
            "resulta em banimento. Encontrar um exploit e **reportar** em "
            f"<#{config.CHANNEL_OCORRENCIAS_ID}> é reconhecido e recompensado.\n\n"
            "**8 · Estruturas que degradam o servidor**\n"
            "Máquinas construídas para causar lag resultam em banimento.\n\n"
            "**9 · Respeito vale dentro do jogo**\n"
            "Todas as diretrizes do Documento 01 valem no chat do jogo, em placas, em "
            "nomes de item e em livros. Hostilidade de jogo é permitida. Ofensa a pessoa "
            "real não é.\n\n"
            "━━━━━━━━━━━━━━━━━━━━ ✦ ━━━━━━━━━━━━━━━━━━━━\n\n"
            "Aqui, você pode quase tudo com o mundo.\n"
            "Nunca com as pessoas."
        )
        embed = discord.Embed(title="Diretrizes do Servidor", description=descricao, color=COR_DIRETRIZES)
        embed.set_author(name="🚪 Diretrizes da Passagem")
        embed.set_footer(text="SONHE • Diretrizes — Documento 02 de 03")
        return embed

    def _embed_conclusao(self) -> discord.Embed:
        descricao = (
            "Você concluiu a leitura das diretrizes da Expedição.\n\n"
            "**Sanções**\n"
            "Advertência · Silenciamento · Expulsão · Banimento\n"
            "A sanção é escolhida pela gravidade, não pela ordem.\n\n"
            "**Recurso**\n"
            f"Toda punição pode ser contestada uma única vez, em <#{config.CHANNEL_RECURSOS_ID}>.\n\n"
            "**Alterações**\n"
            f"Diretrizes podem mudar. Toda alteração é registrada em <#{config.CHANNEL_NOVIDADES_ID}>.\n\n"
            "━━━━━━━━━━━━━━━━━━━━ ✦ ━━━━━━━━━━━━━━━━━━━━\n\n"
            "Ao registrar sua leitura no botão abaixo, você declara ter lido e compreendido "
            "os dois documentos anteriores.\n\n"
            "O acesso à Primeira Passagem será liberado em seguida.\n\n"
            "🌙 Bons sonhos."
        )
        embed = discord.Embed(title="Leitura concluída", description=descricao, color=COR_CONCLUSAO)
        embed.set_author(name="🌙 Sistema de Registro")
        embed.set_footer(text="SONHE • Diretrizes — Documento 03 de 03")
        return embed


async def setup(bot: commands.Bot):
    await bot.add_cog(Regras(bot))
