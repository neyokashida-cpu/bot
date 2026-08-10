"""
SONHE — Botão de aceite (Registrar leitura)
Spec: manual 9.4-C.

Canal:            📖・leia-antes
Texto do botão:   Registrar leitura
Estilo:           Secundário (cinza)
Emoji:            🌙
Concede:          🧭 Explorador
Remove:           👋 Recém-chegado
Tipo:             Único (não desfaz)
Resposta efêmera: "Leitura registrada. A Primeira Passagem está aberta."

Usa View persistente (custom_id fixo) para sobreviver a restart do bot.
"""

import discord
from discord.ext import commands

import config

CUSTOM_ID_ACEITE = "sonhe:registrar_leitura"


class BotaoAceite(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)  # persistente

    @discord.ui.button(
        label="Registrar leitura",
        style=discord.ButtonStyle.secondary,
        emoji="🌙",
        custom_id=CUSTOM_ID_ACEITE,
    )
    async def registrar_leitura(self, interaction: discord.Interaction, button: discord.ui.Button):
        member = interaction.user
        guild = interaction.guild

        role_explorador = guild.get_role(config.ROLE_EXPLORADOR_ID)
        role_recem = guild.get_role(config.ROLE_RECEM_CHEGADO_ID)

        # Tipo "Único" — se já é Explorador, não repete a ação.
        if role_explorador in member.roles:
            await interaction.response.send_message(
                "Leitura já registrada anteriormente.", ephemeral=True
            )
            return

        try:
            if role_explorador:
                await member.add_roles(role_explorador, reason="Botão de aceite — leia-antes")
            if role_recem and role_recem in member.roles:
                await member.remove_roles(role_recem, reason="Botão de aceite — leia-antes")
        except discord.Forbidden:
            await interaction.response.send_message(
                "Não consegui atualizar seu cargo. Avise a Direção.", ephemeral=True
            )
            return

        await interaction.response.send_message(
            "Leitura registrada. A Primeira Passagem está aberta.", ephemeral=True
        )


class Verification(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def cog_load(self):
        # Registra a view persistente assim que o cog carrega.
        self.bot.add_view(BotaoAceite())

    @commands.command(name="enviar_aceite")
    @commands.has_permissions(administrator=True)
    async def enviar_aceite(self, ctx: commands.Context):
        """
        Comando manual, só pra Direção: envia o botão no canal atual.
        Use uma vez, dentro de 📖・leia-antes, depois dos 3 embeds de diretrizes.
        """
        await ctx.send(view=BotaoAceite())
        await ctx.message.delete()


async def setup(bot: commands.Bot):
    await bot.add_cog(Verification(bot))
