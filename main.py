"""
SONHE — Bot principal (ANÚBIS)
Executa localmente por enquanto. Depois sobe pro Railway sem mudar nada aqui.
"""

import asyncio
import logging

import discord
from discord.ext import commands

import config
import database

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("sonhe")

intents = discord.Intents.default()
intents.members = True  # necessário pro on_member_join (greet)
intents.message_content = True  # necessário pros comandos !enviar_diretrizes / !enviar_aceite

bot = commands.Bot(command_prefix="!", intents=intents)

COGS = [
    "cogs.greet",
    "cogs.verification",
    "cogs.regras",
    "cogs.tickets",
    "cogs.chat",
    "cogs.sugestoes",
    "cogs.economia",
    "cogs.mines",
    "cogs.status",
    "cogs.vinculacao",
    "cogs.bridge",
]

_sincronizado = False


@bot.event
async def on_ready():
    global _sincronizado
    await bot.change_presence(status=discord.Status.dnd)
    if not _sincronizado:
        guild = discord.Object(id=config.GUILD_ID)
        bot.tree.copy_global_to(guild=guild)
        comandos = await bot.tree.sync(guild=guild)
        log.info(f"{len(comandos)} slash commands sincronizados no servidor SONHE.")
        _sincronizado = True
    log.info(f"SONHE conectado como {bot.user} (ID: {bot.user.id})")
    log.info("A Expedição está online.")


async def main():
    await database.iniciar()
    async with bot:
        for cog in COGS:
            await bot.load_extension(cog)
            log.info(f"Cog carregado: {cog}")
        await bot.start(config.BOT_TOKEN)


if __name__ == "__main__":
    asyncio.run(main())
