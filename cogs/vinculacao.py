"""
SONHE — Vinculação Minecraft ↔ Discord
Comandos: /vincular, /admin link, /admin unlink

Fluxo atual (automático, via SonheBridge_BP — precisa de @minecraft/server-net
liberado no host):
  1. O jogador roda "!vincular" dentro do jogo. O addon manda o nome dele pro
     bot, que gera um código de uso único e devolve — o addon mostra esse
     código só pra esse jogador (cogs/bridge.py trata a solicitação).
  2. O jogador roda /vincular <código> aqui no Discord. Se o código bater e
     não tiver expirado (config.VALIDADE_CODIGO_VINCULO_MINUTOS), o vínculo é
     confirmado na hora — sem staff.
  3. Se o jogador tinha moedas no placar sonhe_moedas do Minecraft, elas são
     somadas ao Statz do Discord nesse momento (soma única, não sincronização
     contínua — depois disso o Statz do Discord é a fonte única de verdade).

Rank/Tag no Minecraft vêm do cargo real do Discord (não são mais setados à
mão): rank = Dono/Admin/Staff se o cargo de staff correspondente existir, ou
Membro caso contrário; tag = a progressão de XP atual (Explorador, Lenda...).
São enviados via cogs/bridge.py (fila + polling do addon) sempre que o
vínculo é confirmado, e de novo a cada level up (ver cogs/economia.py).
/admin resync existe pra forçar o reenvio manualmente (ex: depois de uma
promoção de staff, que não dispara level up nenhum).

Só staff pode desvincular (/admin unlink) — de propósito, pra evitar que
alguém perca o vínculo (e o histórico de moedas somadas) sem querer.
/admin link continua existindo como override manual (ex: jogador sem acesso
ao Discord no momento, ou correção de erro).
"""

import logging

import discord
from discord import app_commands
from discord.ext import commands

import config
import database

log = logging.getLogger("sonhe")


class Vinculacao(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    def _tem_algum_cargo(self, autor: discord.abc.User, cargos_ids: set[int]) -> bool:
        guild = self.bot.get_guild(config.GUILD_ID)
        if guild is None:
            return False
        membro = guild.get_member(autor.id)
        if membro is None:
            return False
        return any(cargo.id in cargos_ids for cargo in membro.roles)

    def _eh_administracao(self, autor: discord.abc.User) -> bool:
        return self._tem_algum_cargo(
            autor,
            {
                config.ROLE_ANUBIS_DONO_ID,
                config.ROLE_DIRECAO_ID,
                config.ROLE_GUARDA_ID,
                config.ROLE_RECEPCAO_ID,
            },
        )

    # ── rank/tag no Minecraft, derivados do cargo real do Discord ──────
    @staticmethod
    def _indice_rank(membro: discord.Member) -> int:
        """0=Visitante (sem vínculo, nunca setado por aqui) 1=Membro 2=Staff 3=Admin 4=Dono."""
        cargos_ids = {c.id for c in membro.roles}
        if config.ROLE_ANUBIS_DONO_ID in cargos_ids:
            return 4
        if config.ROLE_DIRECAO_ID in cargos_ids:
            return 3
        if config.ROLE_GUARDA_ID in cargos_ids or config.ROLE_RECEPCAO_ID in cargos_ids:
            return 2
        return 1

    @staticmethod
    def _indice_tag(xp: int) -> int:
        """0=sem tag, 1..6 = NIVEIS_XP[0..5] (mesma ordem do array TAGS no addon)."""
        indice = 0
        for i, (limite, _, _) in enumerate(config.NIVEIS_XP):
            if xp >= limite:
                indice = i + 1
        return indice

    def _enfileirar_rank_tag(self, nome_minecraft: str, rank: int, tag: int):
        bridge = self.bot.get_cog("Bridge")
        if bridge is None:
            log.warning("Vinculacao: cog Bridge não carregado, não deu pra enfileirar rank/tag.")
            return
        bridge.fila_para_minecraft.append({"tipo": "definir_rank", "jogador": nome_minecraft, "rank": rank})
        bridge.fila_para_minecraft.append({"tipo": "definir_tag", "jogador": nome_minecraft, "tag": tag})

    # ── /vincular ────────────────────────────────────────────
    @app_commands.command(
        name="vincular", description="Confirma o vínculo com o código que você recebeu no jogo (!vincular)."
    )
    @app_commands.describe(codigo="O código de 4 dígitos que apareceu pra você dentro do Minecraft")
    async def vincular(self, interaction: discord.Interaction, codigo: str):
        perfil = await database.obter_perfil(interaction.user.id)
        if perfil["minecraft_status"] == "confirmado":
            await interaction.response.send_message(
                f"Você já está vinculado como **{perfil['minecraft_nome']}**. "
                "Só a ANÚBIS pode desfazer esse vínculo.",
                ephemeral=True,
            )
            return

        resultado = await database.consumir_codigo_vinculo(codigo, config.VALIDADE_CODIGO_VINCULO_MINUTOS)
        if resultado is None:
            await interaction.response.send_message(
                "Esse código não existe ou expirou. Roda `!vincular` de novo dentro do jogo pra gerar outro.",
                ephemeral=True,
            )
            return

        nome_minecraft = resultado["minecraft_nome"]
        moedas = resultado["moedas_iniciais"]

        existente = await database.obter_vinculo_confirmado_por_nome(nome_minecraft)
        if existente and existente["user_id"] != interaction.user.id:
            await interaction.response.send_message(
                "Esse nome já está vinculado a outra conta. Se isso for engano, chama a ANÚBIS.",
                ephemeral=True,
            )
            return

        await database.confirmar_vinculo(interaction.user.id, nome_minecraft)

        if isinstance(interaction.user, discord.Member):
            self._enfileirar_rank_tag(nome_minecraft, self._indice_rank(interaction.user), self._indice_tag(perfil["xp"]))

        descricao = f"Vinculado ao Minecraft **{nome_minecraft}**."
        if moedas > 0:
            await database.ajustar_statz(interaction.user.id, moedas)
            descricao += f"\n\n{config.EMOJI_MOEDA} {moedas} {config.NOME_MOEDA} do jogo somadas ao seu saldo."
        descricao += "\n\nSeu rank e tag no jogo devem atualizar em alguns segundos (precisa do servidor online)."

        embed = discord.Embed(title="🌙 Vínculo confirmado", description=descricao, color=config.COR_DREAMCORE)
        embed.set_footer(text="Projeto Sonhe • Created by Team ANÚBIS.")
        await interaction.response.send_message(embed=embed, ephemeral=True)

    # ── /admin ───────────────────────────────────────────────
    admin_group = app_commands.Group(name="admin", description="Comandos administrativos do SONHE")

    @admin_group.command(name="link", description="[Staff] Confirma o vínculo Minecraft de um membro.")
    @app_commands.describe(membro="Quem vai ser vinculado", nome_minecraft="Nome/gamertag confirmado em jogo")
    async def admin_link(self, interaction: discord.Interaction, membro: discord.Member, nome_minecraft: str):
        if not self._eh_administracao(interaction.user):
            await interaction.response.send_message("Só a ANÚBIS pode usar esse comando.", ephemeral=True)
            return

        nome_minecraft = nome_minecraft.strip()
        existente = await database.obter_vinculo_confirmado_por_nome(nome_minecraft)
        if existente and existente["user_id"] != membro.id:
            await interaction.response.send_message(
                f"**{nome_minecraft}** já está confirmado pra <@{existente['user_id']}>. "
                "Desvincula essa conta primeiro (`/admin unlink`) se for engano.",
                ephemeral=True,
            )
            return

        await database.confirmar_vinculo(membro.id, nome_minecraft)
        perfil_membro = await database.obter_perfil(membro.id)
        self._enfileirar_rank_tag(nome_minecraft, self._indice_rank(membro), self._indice_tag(perfil_membro["xp"]))

        await interaction.response.send_message(
            f"✅ {membro.mention} vinculado como **{nome_minecraft}**.", ephemeral=True
        )
        try:
            await membro.send(f"🌙 Seu Discord foi vinculado ao Minecraft **{nome_minecraft}** no SONHE.")
        except discord.Forbidden:
            pass

    @admin_group.command(name="unlink", description="[Staff] Remove o vínculo Minecraft de um membro.")
    @app_commands.describe(membro="Quem vai ter o vínculo removido")
    async def admin_unlink(self, interaction: discord.Interaction, membro: discord.Member):
        if not self._eh_administracao(interaction.user):
            await interaction.response.send_message("Só a ANÚBIS pode usar esse comando.", ephemeral=True)
            return

        await database.desvincular_minecraft(membro.id)
        await interaction.response.send_message(f"Vínculo de {membro.mention} removido.", ephemeral=True)

    @admin_group.command(
        name="resync", description="[Staff] Reenvia o rank/tag do Minecraft de um membro já vinculado."
    )
    @app_commands.describe(membro="Quem vai ter o rank/tag re-sincronizado")
    async def admin_resync(self, interaction: discord.Interaction, membro: discord.Member):
        if not self._eh_administracao(interaction.user):
            await interaction.response.send_message("Só a ANÚBIS pode usar esse comando.", ephemeral=True)
            return

        perfil = await database.obter_perfil(membro.id)
        if perfil["minecraft_status"] != "confirmado":
            await interaction.response.send_message(f"{membro.mention} não tem vínculo confirmado.", ephemeral=True)
            return

        self._enfileirar_rank_tag(perfil["minecraft_nome"], self._indice_rank(membro), self._indice_tag(perfil["xp"]))
        await interaction.response.send_message(
            f"🔄 Rank/tag de **{perfil['minecraft_nome']}** vão atualizar em alguns segundos "
            "(precisa do servidor Minecraft online).",
            ephemeral=True,
        )


async def setup(bot: commands.Bot):
    await bot.add_cog(Vinculacao(bot))
