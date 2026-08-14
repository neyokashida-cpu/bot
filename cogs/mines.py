"""
SONHE — Mines
/mines jogar aposta minas — jogo de tabuleiro 4x4 inspirado no Mines da Loritta.
Cada casa segura revelada aumenta o multiplicador; cair numa mina perde a aposta.
"""

import logging
import random

import discord
from discord import app_commands
from discord.ext import commands

import config
import database

log = logging.getLogger("sonhe")


class JogoMines:
    def __init__(self, dono: discord.abc.User, aposta: int, qtd_minas: int):
        self.dono = dono
        self.aposta = aposta
        self.qtd_minas = qtd_minas
        self.total = config.MINES_TAMANHO_TABULEIRO
        self.minas = set(random.sample(range(self.total), qtd_minas))
        self.reveladas: set[int] = set()
        self.finalizado = False

    @property
    def seguras_total(self) -> int:
        return self.total - self.qtd_minas

    def multiplicador(self, n: int | None = None) -> float:
        n = len(self.reveladas) if n is None else n
        if n <= 0:
            return 1.0
        prob = 1.0
        for i in range(n):
            prob *= (self.seguras_total - i) / (self.total - i)
        if prob <= 0:
            return 0.0
        return round((1 - config.MINES_HOUSE_EDGE) / prob, 2)


class BotaoTile(discord.ui.Button):
    def __init__(self, view: "MinesView", index: int):
        super().__init__(style=discord.ButtonStyle.secondary, label="🌫️", row=index // 4)
        self.jogo_view = view
        self.index = index

    async def callback(self, interaction: discord.Interaction):
        await self.jogo_view.revelar(interaction, self.index)


class BotaoEncerrar(discord.ui.Button):
    def __init__(self, view: "MinesView"):
        super().__init__(style=discord.ButtonStyle.success, label="💰 Encerrar", row=4)
        self.jogo_view = view

    async def callback(self, interaction: discord.Interaction):
        await self.jogo_view.encerrar(interaction)


class MinesView(discord.ui.View):
    def __init__(self, jogo: JogoMines):
        super().__init__(timeout=300)
        self.jogo = jogo
        self.message: discord.Message | None = None
        self._botoes_tile: list[BotaoTile] = []
        for i in range(jogo.total):
            botao = BotaoTile(self, i)
            self._botoes_tile.append(botao)
            self.add_item(botao)
        self.add_item(BotaoEncerrar(self))

    def _montar_embed(self, resultado: str | None = None) -> discord.Embed:
        j = self.jogo
        mult_atual = j.multiplicador()
        prox = None
        if len(j.reveladas) < j.seguras_total:
            prox = j.multiplicador(len(j.reveladas) + 1)

        aposta_txt = f"{j.aposta} {config.NOME_MOEDA}" if j.aposta > 0 else "Nada! Apenas por diversão :3"

        embed = discord.Embed(
            title="🌙 Mines",
            description=(
                "Cada passo revela mais um pedaço do sonho.\n"
                "Mas cuidado — alguns lugares fazem você despertar antes da hora."
            ),
            color=config.COR_DREAMCORE,
        )
        embed.add_field(name="🎲 Aposta", value=aposta_txt, inline=True)
        embed.add_field(name="💣 Minas", value=f"{j.qtd_minas} ({len(j.reveladas)}/{j.seguras_total})", inline=True)
        embed.add_field(name="✖️ Multiplicador", value=f"{mult_atual}x", inline=True)
        embed.add_field(
            name="⏭️ Próximo multiplicador",
            value=f"{prox}x" if prox is not None else "—",
            inline=True,
        )
        if resultado:
            embed.add_field(name="Resultado", value=resultado, inline=False)
        embed.set_footer(text="Projeto Sonhe • Created by Team ANÚBIS.")
        return embed

    async def revelar(self, interaction: discord.Interaction, index: int):
        if interaction.user.id != self.jogo.dono.id:
            await interaction.response.send_message("Esse jogo não é seu.", ephemeral=True)
            return
        if self.jogo.finalizado or index in self.jogo.reveladas:
            await interaction.response.defer()
            return

        if index in self.jogo.minas:
            await self._explodir(interaction)
            return

        self.jogo.reveladas.add(index)
        botao = self._botoes_tile[index]
        botao.style = discord.ButtonStyle.success
        botao.label = "✨"
        botao.disabled = True

        if len(self.jogo.reveladas) == self.jogo.seguras_total:
            await self._pagar_e_finalizar(interaction, "✨ Você atravessou o sonho inteiro sem despertar!")
            return

        await interaction.response.edit_message(embed=self._montar_embed(), view=self)

    async def encerrar(self, interaction: discord.Interaction):
        if interaction.user.id != self.jogo.dono.id:
            await interaction.response.send_message("Esse jogo não é seu.", ephemeral=True)
            return
        if self.jogo.finalizado:
            await interaction.response.defer()
            return

        await self._pagar_e_finalizar(interaction, "🌙 Você escolheu acordar a tempo — prêmio garantido.")

    async def _explodir(self, interaction: discord.Interaction):
        self.jogo.finalizado = True
        for i in self.jogo.minas:
            self._botoes_tile[i].style = discord.ButtonStyle.danger
            self._botoes_tile[i].label = "🌑"
        for item in self.children:
            item.disabled = True

        await interaction.response.edit_message(
            embed=self._montar_embed("🌑 Você despertou. O sonho (e a aposta) acabou aqui."), view=self
        )
        self.stop()

    async def _pagar_e_finalizar(self, interaction: discord.Interaction, motivo: str):
        self.jogo.finalizado = True
        multiplicador = self.jogo.multiplicador()
        premio = int(self.jogo.aposta * multiplicador)
        if premio > 0:
            await database.ajustar_statz(self.jogo.dono.id, premio)

        for i in self.jogo.minas:
            self._botoes_tile[i].style = discord.ButtonStyle.danger
            self._botoes_tile[i].label = "🌑"
        for item in self.children:
            item.disabled = True

        texto = f"{motivo}\nVocê ganhou **{premio} {config.NOME_MOEDA}** (x{multiplicador})."
        await interaction.response.edit_message(embed=self._montar_embed(texto), view=self)
        self.stop()

    async def on_timeout(self):
        if self.jogo.finalizado or self.message is None:
            return
        self.jogo.finalizado = True
        for item in self.children:
            item.disabled = True
        try:
            await self.message.edit(
                embed=self._montar_embed("🌫️ O sonho se dissolveu antes de você decidir — jogo encerrado sem resgate."),
                view=self,
            )
        except discord.HTTPException:
            log.exception("Falha ao encerrar Mines por timeout")


class Mines(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    mines_group = app_commands.Group(name="mines", description="Jogo de Mines do SONHE")

    @mines_group.command(name="jogar", description="Joga uma partida de Mines.")
    @app_commands.describe(
        aposta=f"Quantidade de {config.NOME_MOEDA} pra apostar (0 = só por diversão)",
        minas=f"Quantidade de minas no tabuleiro ({config.MINES_MIN_MINAS}-{config.MINES_MAX_MINAS}, padrão {config.MINES_PADRAO_QTD_MINAS})",
    )
    async def jogar(
        self,
        interaction: discord.Interaction,
        aposta: app_commands.Range[int, 0, None] = 0,
        minas: app_commands.Range[int, config.MINES_MIN_MINAS, config.MINES_MAX_MINAS] = config.MINES_PADRAO_QTD_MINAS,
    ):
        if aposta > 0:
            perfil = await database.obter_perfil(interaction.user.id)
            if perfil["statz"] < aposta:
                await interaction.response.send_message(
                    f"Você não tem {aposta} {config.NOME_MOEDA}. Seu saldo é {perfil['statz']}.",
                    ephemeral=True,
                )
                return
            await database.ajustar_statz(interaction.user.id, -aposta)

        jogo = JogoMines(interaction.user, aposta, minas)
        view = MinesView(jogo)
        await interaction.response.send_message(embed=view._montar_embed(), view=view)
        view.message = await interaction.original_response()


async def setup(bot: commands.Bot):
    await bot.add_cog(Mines(bot))
