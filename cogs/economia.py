"""
SONHE — Economia (Statz), progressão de nível e casamento
Comandos: /perfil, /daily, /casar pedir|aceitar|cancelar|divorciar
Ganho passivo: XP + Statz por mensagem no servidor (com cooldown, evita farm).
"""

import logging
import random

import discord
from discord import app_commands
from discord.ext import commands

import config
import database

log = logging.getLogger("sonhe")


def _nivel_atual(xp: int):
    atual = config.NIVEIS_XP[0]
    for tier in config.NIVEIS_XP:
        if xp >= tier[0]:
            atual = tier
        else:
            break
    return atual


def _proximo_nivel(xp: int):
    for tier in config.NIVEIS_XP:
        if tier[0] > xp:
            return tier
    return None


def _nivel_amizade(pontos: int):
    atual = config.NIVEIS_AMIZADE[0]
    for tier in config.NIVEIS_AMIZADE:
        if pontos >= tier[0]:
            atual = tier
        else:
            break
    return atual


class Economia(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # ── Ganho passivo por mensagem ──────────────────────────
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot or message.guild is None:
            return
        if message.guild.id != config.GUILD_ID:
            return
        if not await database.cooldown_mensagem_ok(message.author.id, config.COOLDOWN_MENSAGEM_ECONOMIA):
            return

        perfil = await database.obter_perfil(message.author.id)
        xp_antes = perfil["xp"]
        ganho_statz = random.randint(*config.STATZ_POR_MENSAGEM)

        await database.ajustar_xp(message.author.id, config.XP_POR_MENSAGEM)
        await database.ajustar_statz(message.author.id, ganho_statz)

        xp_depois = xp_antes + config.XP_POR_MENSAGEM
        tier_antes = _nivel_atual(xp_antes)
        tier_depois = _nivel_atual(xp_depois)
        if tier_depois != tier_antes:
            await self._atualizar_cargo_nivel(message.author, tier_depois)
            if perfil["minecraft_status"] == "confirmado":
                self._sincronizar_tag_minecraft(perfil["minecraft_nome"], config.NIVEIS_XP.index(tier_depois) + 1)
            try:
                await message.channel.send(
                    f"🌙 {message.author.mention} deu mais um passo no sonho — agora é **{tier_depois[2]}**."
                )
            except discord.HTTPException:
                log.exception("Falha ao anunciar nível novo de %s", message.author)

    def _sincronizar_tag_minecraft(self, nome_minecraft: str, indice_tag: int):
        """Manda a nova tag pro Minecraft (rank não muda aqui — level up não afeta staff/dono)."""
        bridge = self.bot.get_cog("Bridge")
        if bridge is None:
            return
        bridge.fila_para_minecraft.append({"tipo": "definir_tag", "jogador": nome_minecraft, "tag": indice_tag})

    async def _atualizar_cargo_nivel(self, member: discord.Member, tier_novo):
        roles_para_remover = []
        for _, role_id, _ in config.NIVEIS_XP:
            if role_id == tier_novo[1]:
                continue
            role = member.guild.get_role(role_id)
            if role and role in member.roles:
                roles_para_remover.append(role)

        role_novo = member.guild.get_role(tier_novo[1])
        try:
            if roles_para_remover:
                await member.remove_roles(*roles_para_remover, reason="Progressão de nível (XP)")
            if role_novo and role_novo not in member.roles:
                await member.add_roles(role_novo, reason="Progressão de nível (XP)")
        except discord.Forbidden:
            log.warning("Sem permissão pra atualizar cargo de nível de %s", member)

    # ── /perfil ──────────────────────────────────────────────
    @app_commands.command(name="perfil", description="Mostra o perfil no SONHE — XP, Statz, amizade e casamento.")
    @app_commands.describe(membro="Ver o perfil de outra pessoa (opcional)")
    async def perfil(self, interaction: discord.Interaction, membro: discord.Member | None = None):
        alvo = membro or interaction.user
        perfil = await database.obter_perfil(alvo.id)

        tier_atual = _nivel_atual(perfil["xp"])
        tier_proximo = _proximo_nivel(perfil["xp"])
        tier_amizade = _nivel_amizade(perfil["amizade"])

        if tier_proximo:
            progresso = f"{perfil['xp']}/{tier_proximo[0]} XP — faltam {tier_proximo[0] - perfil['xp']} pro próximo"
            proximo_txt = tier_proximo[2]
        else:
            progresso = f"{perfil['xp']} XP — nível máximo"
            proximo_txt = "— (já é o topo)"

        if perfil["casado_com"]:
            casamento = f"💍 <@{perfil['casado_com']}>"
        else:
            casamento = "Solteiro(a)"

        if perfil["minecraft_status"] == "confirmado":
            minecraft = f"✅ {perfil['minecraft_nome']}"
        elif perfil["minecraft_status"] == "pendente":
            minecraft = f"🕒 Pendente ({perfil['minecraft_nome']})"
        else:
            minecraft = "Não vinculado — `/vincular`"

        embed = discord.Embed(
            title=f"📖 Registro de {alvo.display_name}",
            color=config.COR_DREAMCORE,
        )
        embed.set_thumbnail(url=alvo.display_avatar.url)
        embed.add_field(name="🧭 Cargo atual", value=tier_atual[2], inline=True)
        embed.add_field(name="⬆️ Próximo cargo", value=proximo_txt, inline=True)
        embed.add_field(name="📈 Progresso", value=progresso, inline=False)
        embed.add_field(name=f"{config.EMOJI_MOEDA} {config.NOME_MOEDA}", value=str(perfil["statz"]), inline=True)
        embed.add_field(name="🤝 Amizade", value=f"{tier_amizade[1]} ({perfil['amizade']} pts)", inline=True)
        embed.add_field(name="💞 Relacionamento", value=casamento, inline=True)
        embed.add_field(name="🎮 Minecraft", value=minecraft, inline=True)
        embed.set_footer(text="Projeto Sonhe • Created by Team ANÚBIS.")

        await interaction.response.send_message(embed=embed)

    # ── /daily ───────────────────────────────────────────────
    @app_commands.command(name="daily", description=f"Resgata sua recompensa diária de {config.NOME_MOEDA}.")
    async def daily(self, interaction: discord.Interaction):
        quantidade = random.randint(*config.DAILY_STATZ)
        concedido = await database.marcar_daily(interaction.user.id, quantidade)
        if not concedido:
            await interaction.response.send_message(
                "Você já pegou seu daily hoje. Volta amanhã!", ephemeral=True
            )
            return
        await interaction.response.send_message(
            f"{config.EMOJI_MOEDA} Você recebeu **{quantidade} {config.NOME_MOEDA}** — mais um pedaço do sonho pro seu bolso. Volta amanhã pra mais."
        )

    # ── /casar ───────────────────────────────────────────────
    casar_group = app_commands.Group(name="casar", description="Sistema de casamento do SONHE")

    @casar_group.command(name="pedir", description="Pede alguém em casamento.")
    async def casar_pedir(self, interaction: discord.Interaction, membro: discord.Member):
        if membro.id == interaction.user.id:
            await interaction.response.send_message("Não dá pra casar com você mesmo(a) ksks.", ephemeral=True)
            return
        if membro.bot:
            await interaction.response.send_message("Ela é só um sistema, não dá pra casar assim não.", ephemeral=True)
            return

        perfil_prop = await database.obter_perfil(interaction.user.id)
        if perfil_prop["casado_com"]:
            await interaction.response.send_message(
                "Você já é casado(a). Precisa se divorciar antes (`/casar divorciar`).", ephemeral=True
            )
            return

        perfil_alvo = await database.obter_perfil(membro.id)
        if perfil_alvo["casado_com"]:
            await interaction.response.send_message(f"{membro.mention} já é casado(a) com outra pessoa.", ephemeral=True)
            return

        if perfil_prop["statz"] < config.CUSTO_CASAMENTO:
            await interaction.response.send_message(
                f"Pedir em casamento custa {config.CUSTO_CASAMENTO} {config.NOME_MOEDA} "
                f"e você tem {perfil_prop['statz']}.",
                ephemeral=True,
            )
            return

        await database.ajustar_statz(interaction.user.id, -config.CUSTO_CASAMENTO)
        await database.criar_proposta(interaction.user.id, membro.id)
        await interaction.response.send_message(
            f"💍 {interaction.user.mention} pediu {membro.mention} em casamento!\n"
            f"{membro.mention}, usa `/casar aceitar` e seleciona {interaction.user.mention} "
            f"pra aceitar (custa {config.CUSTO_CASAMENTO} {config.NOME_MOEDA})."
        )

    @casar_group.command(name="aceitar", description="Aceita um pedido de casamento pendente.")
    async def casar_aceitar(self, interaction: discord.Interaction, membro: discord.Member):
        proposta = await database.obter_proposta(membro.id, interaction.user.id)
        if not proposta:
            await interaction.response.send_message(
                f"Não tem nenhum pedido de casamento de {membro.mention} esperando.", ephemeral=True
            )
            return

        perfil_alvo = await database.obter_perfil(interaction.user.id)
        if perfil_alvo["casado_com"]:
            await database.remover_proposta(membro.id, interaction.user.id)
            await interaction.response.send_message(
                "Você já é casado(a) — o pedido antigo foi cancelado.", ephemeral=True
            )
            return

        if perfil_alvo["statz"] < config.CUSTO_CASAMENTO:
            await interaction.response.send_message(
                f"Aceitar custa {config.CUSTO_CASAMENTO} {config.NOME_MOEDA} "
                f"e você tem {perfil_alvo['statz']}.",
                ephemeral=True,
            )
            return

        perfil_prop = await database.obter_perfil(membro.id)
        if perfil_prop["casado_com"]:
            await database.remover_proposta(membro.id, interaction.user.id)
            await interaction.response.send_message(
                f"{membro.mention} já se casou com outra pessoa nesse meio tempo. Pedido cancelado.",
                ephemeral=True,
            )
            return

        await database.ajustar_statz(interaction.user.id, -config.CUSTO_CASAMENTO)
        await database.remover_proposta(membro.id, interaction.user.id)
        await database.casar(membro.id, interaction.user.id)
        await interaction.response.send_message(
            f"💍 {membro.mention} e {interaction.user.mention} agora são casados! "
            "Que o SONHE seja gentil com vocês dois."
        )

    @casar_group.command(name="cancelar", description="Cancela um pedido de casamento que você mandou.")
    async def casar_cancelar(self, interaction: discord.Interaction, membro: discord.Member):
        proposta = await database.obter_proposta(interaction.user.id, membro.id)
        if not proposta:
            await interaction.response.send_message(
                "Você não tem nenhum pedido pendente pra essa pessoa.", ephemeral=True
            )
            return

        await database.remover_proposta(interaction.user.id, membro.id)
        await database.ajustar_statz(interaction.user.id, config.CUSTO_CASAMENTO)
        await interaction.response.send_message(
            f"Pedido cancelado. Seus {config.CUSTO_CASAMENTO} {config.NOME_MOEDA} voltaram.", ephemeral=True
        )

    @casar_group.command(name="divorciar", description="Termina seu casamento atual.")
    async def casar_divorciar(self, interaction: discord.Interaction):
        perfil = await database.obter_perfil(interaction.user.id)
        if not perfil["casado_com"]:
            await interaction.response.send_message("Você não é casado(a) com ninguém.", ephemeral=True)
            return

        parceiro_id = perfil["casado_com"]
        await database.divorciar(interaction.user.id, parceiro_id)
        await interaction.response.send_message(f"💔 {interaction.user.mention} se divorciou de <@{parceiro_id}>.")


async def setup(bot: commands.Bot):
    await bot.add_cog(Economia(bot))
