"""
SONHE — Reação automática em #sugestões
Toda vez que um post novo é criado no fórum de sugestões, o bot reage com 🔼
pra facilitar votos da comunidade.
"""

import logging

import discord
from discord.ext import commands

import config

log = logging.getLogger("sonhe")


class Sugestoes(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_thread_create(self, thread: discord.Thread):
        if thread.parent_id != config.CHANNEL_SUGESTOES_ID:
            return

        try:
            mensagem = thread.starter_message or await thread.fetch_message(thread.id)
            await mensagem.add_reaction("🔼")
        except discord.HTTPException:
            log.exception("Falha ao reagir no post de sugestão %s", thread.id)


async def setup(bot: commands.Bot):
    await bot.add_cog(Sugestoes(bot))
