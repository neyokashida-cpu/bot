"""
SONHE — Vinculação Minecraft ↔ Discord
Comandos: /vincular, /desvincular, /admin link, /admin unlink

Fluxo atual (ver auditoria do projeto pra entender o motivo):
  1. O membro roda /vincular <nome> no Discord e recebe um código curto.
  2. Um Guarda/Direção/dono confirma com /admin link depois de checar o
     jogador (o código serve de conferência rápida, não é prova criptográfica).
A confirmação não é automática porque o bridge addon → backend depende de
@minecraft/server-net (hoje pré-lançamento, exige acesso ao permissions.json
do servidor — hosts com painel tipo Aternos normalmente não expõem isso).
Se isso mudar, confirmar_vinculo() em database.py já está pronta pra ser
chamada por um caminho automático, sem mudar o schema.
"""

import logging
import random
import string

import discord
from discord import app_commands
from discord.ext import commands

import config
import database

log = logging.getLogger("sonhe")


def _gerar_codigo() -> str:
    return "".join(random.choices(string.ascii_uppercase + string.digits, k=4))


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

    # ── /vincular ────────────────────────────────────────────
    @app_commands.command(
        name="vincular", description="Registra seu nome do Minecraft pra vincular com seu Discord."
    )
    @app_commands.describe(nome_minecraft="Seu gamertag/nome exatamente como aparece no jogo")
    async def vincular(self, interaction: discord.Interaction, nome_minecraft: str):
        nome_minecraft = nome_minecraft.strip()
        if not nome_minecraft or len(nome_minecraft) > 32:
            await interaction.response.send_message(
                "Esse nome não parece certo — manda exatamente como aparece no Minecraft (até 32 caracteres).",
                ephemeral=True,
            )
            return

        perfil = await database.obter_perfil(interaction.user.id)
        if perfil["minecraft_status"] == "confirmado":
            await interaction.response.send_message(
                f"Você já está vinculado como **{perfil['minecraft_nome']}**. "
                "Usa `/desvincular` primeiro se quiser trocar.",
                ephemeral=True,
            )
            return

        existente = await database.obter_vinculo_confirmado_por_nome(nome_minecraft)
        if existente and existente["user_id"] != interaction.user.id:
            await interaction.response.send_message(
                "Esse nome já está vinculado a outra conta. Se isso for engano, chama a ANÚBIS.",
                ephemeral=True,
            )
            return

        codigo = _gerar_codigo()
        await database.registrar_vinculo_pendente(interaction.user.id, nome_minecraft, codigo)

        embed = discord.Embed(
            title="🌙 Código de vinculação",
            description=(
                f"Nome registrado: **{nome_minecraft}**\n\n"
                f"Código: **SONHE-{codigo}**\n\n"
                "Fica com esse código e avisa um membro da ANÚBIS em jogo (ou em "
                "🎫・abrir-registro) pra confirmar. Isso ainda é feito à mão — assim "
                "que o vínculo automático existir, esse passo some."
            ),
            color=config.COR_DREAMCORE,
        )
        embed.set_footer(text="Projeto Sonhe • Created by Team ANÚBIS.")
        await interaction.response.send_message(embed=embed, ephemeral=True)

    # ── /desvincular ─────────────────────────────────────────
    @app_commands.command(name="desvincular", description="Remove o vínculo do seu Minecraft com esse Discord.")
    async def desvincular(self, interaction: discord.Interaction):
        perfil = await database.obter_perfil(interaction.user.id)
        if not perfil["minecraft_status"]:
            await interaction.response.send_message("Você não tem nenhum vínculo registrado.", ephemeral=True)
            return

        await database.desvincular_minecraft(interaction.user.id)
        await interaction.response.send_message("Vínculo removido.", ephemeral=True)

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


async def setup(bot: commands.Bot):
    await bot.add_cog(Vinculacao(bot))
