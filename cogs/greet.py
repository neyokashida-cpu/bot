"""
SONHE — Greet + Autorole
Spec: manual 9.4-A (Greet), 9.4-B (Autorole), 10.1 e 10.2 (embeds).

Ao entrar um membro:
1. Recebe o cargo 👋 Recém-chegado (delay 0).
2. O canal 👋・despertar recebe os 2 embeds em sequência, sem ping fora do embed.
Nunca deletar essas mensagens.
"""

import discord
from discord.ext import commands

import config


class Greet(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        if member.guild.id != config.GUILD_ID:
            return

        # 9.4-B — Autorole, delay 0
        role = member.guild.get_role(config.ROLE_RECEM_CHEGADO_ID)
        if role:
            try:
                await member.add_roles(role, reason="Chegada registrada — Sistema de Registro")
            except discord.Forbidden:
                pass

        canal = member.guild.get_channel(config.CHANNEL_DESPERTAR_ID)
        if canal is None:
            return

        embed1 = self._embed_boas_vindas_1(member)
        await canal.send(embed=embed1)

    def _embed_boas_vindas_1(self, member: discord.Member) -> discord.Embed:
        guild = member.guild

        descricao = (
            f"||{member.mention}||\n\n"
            f"Sua chegada ao **{guild.name}** foi registrada.\n\n"
            "Este projeto nasceu com um único objetivo:\n"
            "transformar a sensação de um sonho em um lugar.\n\n"
            "Antes de iniciar sua travessia, reserve alguns minutos para conhecer o que existe aqui.\n\n"
            "━━━━━━━━━━━━━━━━━━━━ ✦ ━━━━━━━━━━━━━━━━━━━━\n\n"
            f"📖 Diretrizes da Expedição — <#{config.CHANNEL_LEIA_ANTES_ID}>\n"
            f"📚 Arquivos e documentação — <#{config.CHANNEL_O_QUE_E_ISSO_ID}>\n"
            f"📼 Registros de Desenvolvimento — <#{config.CHANNEL_NOVIDADES_ID}>\n"
            f"🚪 Acesso à Primeira Passagem — <#{config.CHANNEL_PASSAGEM_ID}>\n"
            f"🤝 Como contribuir — <#{config.CHANNEL_FACA_PARTE_ID}>\n\n"
            "━━━━━━━━━━━━━━━━━━━━ ✦ ━━━━━━━━━━━━━━━━━━━━\n\n"
            "🌙 Bons sonhos."
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
        embed.set_image(url=config.PANORAMA_SUBURBIO_URL)
        embed.set_footer(
            text="SONHE • A jornada está apenas começando.",
            icon_url=member.guild.icon.url if member.guild.icon else None,
        )

        embed.add_field(name="👤 Explorador", value=member.mention, inline=True)
        embed.add_field(name="📊 Exploradores", value=str(member.guild.member_count), inline=True)
        embed.add_field(name="🌾 Estado", value="Em desenvolvimento", inline=True)

        return embed


async def setup(bot: commands.Bot):
    await bot.add_cog(Greet(bot))
