"""
SONHE — Sistema de tickets ("Registro")
Spec: contexto do projeto, item 10.

Painel:     🎫・abrir-registro (config.CHANNEL_ABRIR_REGISTRO_ID)
Categorias: Dúvida → Recepção, Problema no servidor → Guarda,
            Denúncia → Guarda, Recurso de punição → Direção.
Regra:      1 ticket aberto por pessoa.
Transcript: enviado pra #logs ao fechar.
SLA:        48h sem resposta de staff no canal → aviso automático pro cargo responsável.

Sem banco de dados: o estado de cada ticket vive no tópico do canal
("sonhe-ticket:<autor_id>:<categoria>[:sla_avisado]") e no created_at do próprio canal.
"""

import datetime
import io

import discord
from discord.ext import commands, tasks

import config

CUSTOM_ID_SELECT = "sonhe:abrir_ticket_select"
CUSTOM_ID_FECHAR = "sonhe:fechar_ticket"

TOPICO_PREFIXO = "sonhe-ticket"
SLA_HORAS = 48

CATEGORIAS = {
    "duvida": {"label": "Dúvida", "emoji": "❓", "role_id": config.ROLE_RECEPCAO_ID},
    "problema": {"label": "Problema no servidor", "emoji": "🛠️", "role_id": config.ROLE_GUARDA_ID},
    "denuncia": {"label": "Denúncia", "emoji": "🚨", "role_id": config.ROLE_GUARDA_ID},
    "recurso": {"label": "Recurso de punição", "emoji": "⚖️", "role_id": config.ROLE_DIRECAO_ID},
}


def _slugify(nome: str) -> str:
    limpo = "".join(c.lower() if c.isalnum() else "-" for c in nome).strip("-")
    return limpo[:20] or "explorador"


class AbrirTicketSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label=dados["label"], value=chave, emoji=dados["emoji"])
            for chave, dados in CATEGORIAS.items()
        ]
        super().__init__(
            placeholder="Selecione o motivo do seu registro...",
            options=options,
            custom_id=CUSTOM_ID_SELECT,
        )

    async def callback(self, interaction: discord.Interaction):
        cog = interaction.client.get_cog("Tickets")
        await cog.abrir_ticket(interaction, self.values[0])


class PainelTickets(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(AbrirTicketSelect())


class FecharTicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="Fechar registro",
        style=discord.ButtonStyle.danger,
        emoji="🔒",
        custom_id=CUSTOM_ID_FECHAR,
    )
    async def fechar(self, interaction: discord.Interaction, button: discord.ui.Button):
        cog = interaction.client.get_cog("Tickets")
        await cog.fechar_ticket(interaction)


class Tickets(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.checar_sla.start()

    def cog_unload(self):
        self.checar_sla.cancel()

    async def cog_load(self):
        self.bot.add_view(PainelTickets())
        self.bot.add_view(FecharTicketView())

    @commands.command(name="enviar_painel_tickets")
    @commands.has_permissions(administrator=True)
    async def enviar_painel_tickets(self, ctx: commands.Context):
        """
        Comando manual, só pra Direção: posta o painel de abertura de registro no canal atual.
        Use uma vez, dentro de 🎫・abrir-registro.
        """
        embed = discord.Embed(
            title="Abrir registro",
            description=(
                "Selecione abaixo o motivo do seu registro.\n"
                "Um canal privado será aberto entre você e a Expedição responsável.\n\n"
                "Só é possível manter **1 registro aberto por vez**."
            ),
            color=config.COR_BOAS_VINDAS_1,
        )
        embed.set_footer(text="SONHE • Sistema de Registro")
        await ctx.send(embed=embed, view=PainelTickets())
        await ctx.message.delete()

    def _ticket_existente(self, guild: discord.Guild, autor_id: int):
        prefixo = f"{TOPICO_PREFIXO}:{autor_id}:"
        for canal in guild.text_channels:
            if canal.topic and canal.topic.startswith(prefixo):
                return canal
        return None

    async def abrir_ticket(self, interaction: discord.Interaction, categoria_chave: str):
        guild = interaction.guild
        autor = interaction.user
        dados = CATEGORIAS[categoria_chave]

        existente = self._ticket_existente(guild, autor.id)
        if existente:
            await interaction.response.send_message(
                f"Você já tem um registro aberto: {existente.mention}", ephemeral=True
            )
            return

        role = guild.get_role(dados["role_id"])
        categoria = guild.get_channel(config.CATEGORY_TICKETS_ID) if config.CATEGORY_TICKETS_ID else None
        if not isinstance(categoria, discord.CategoryChannel):
            categoria = None

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            autor: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True),
            guild.me: discord.PermissionOverwrite(view_channel=True, send_messages=True),
        }
        if role:
            overwrites[role] = discord.PermissionOverwrite(view_channel=True, send_messages=True)

        try:
            canal = await guild.create_text_channel(
                name=f"ticket-{_slugify(autor.name)}",
                category=categoria,
                overwrites=overwrites,
                topic=f"{TOPICO_PREFIXO}:{autor.id}:{categoria_chave}",
                reason=f"Registro aberto por {autor} — {dados['label']}",
            )
        except discord.Forbidden:
            await interaction.response.send_message(
                "Não consegui abrir seu registro. Avise a Direção.", ephemeral=True
            )
            return

        embed = discord.Embed(
            title=f"Registro — {dados['label']}",
            description=(
                f"Explorador: {autor.mention}\n"
                f"Responsável: {role.mention if role else '—'}\n\n"
                "Descreva sua situação. A Expedição responsável vai te atender em breve."
            ),
            color=config.COR_BOAS_VINDAS_1,
        )
        embed.set_footer(text="SONHE • Sistema de Registro")
        await canal.send(
            content=f"{autor.mention} {role.mention if role else ''}".strip(),
            embed=embed,
            view=FecharTicketView(),
        )

        await interaction.response.send_message(f"Registro aberto: {canal.mention}", ephemeral=True)

    async def fechar_ticket(self, interaction: discord.Interaction):
        canal = interaction.channel
        if not canal.topic or not canal.topic.startswith(TOPICO_PREFIXO):
            await interaction.response.send_message("Isso não é um canal de registro.", ephemeral=True)
            return

        await interaction.response.send_message("Fechando registro e gerando transcript...", ephemeral=True)

        transcript = await self._gerar_transcript(canal)
        canal_logs = interaction.guild.get_channel(config.CHANNEL_LOGS_ID)
        if canal_logs:
            await canal_logs.send(
                content=f"Registro fechado: **#{canal.name}** por {interaction.user.mention}",
                file=discord.File(transcript, filename=f"{canal.name}.txt"),
            )

        await canal.delete(reason=f"Registro fechado por {interaction.user}")

    async def _gerar_transcript(self, canal: discord.TextChannel) -> io.BytesIO:
        linhas = []
        async for msg in canal.history(limit=None, oldest_first=True):
            hora = msg.created_at.strftime("%Y-%m-%d %H:%M")
            linhas.append(f"[{hora}] {msg.author}: {msg.content}")
        return io.BytesIO("\n".join(linhas).encode("utf-8"))

    @tasks.loop(hours=1)
    async def checar_sla(self):
        guild = self.bot.get_guild(config.GUILD_ID)
        if guild is None:
            return

        agora = discord.utils.utcnow()
        for canal in guild.text_channels:
            if not canal.topic or not canal.topic.startswith(TOPICO_PREFIXO):
                continue
            if canal.topic.endswith(":sla_avisado"):
                continue
            if agora - canal.created_at < datetime.timedelta(hours=SLA_HORAS):
                continue

            partes = canal.topic.split(":")
            autor_id, categoria_chave = int(partes[1]), partes[2]
            role_id = CATEGORIAS.get(categoria_chave, {}).get("role_id")
            role = guild.get_role(role_id) if role_id else None

            respondido = False
            async for msg in canal.history(limit=100, oldest_first=True):
                if msg.author.bot or msg.author.id == autor_id:
                    continue
                if role and role in getattr(msg.author, "roles", []):
                    respondido = True
                    break

            if respondido:
                continue

            if role:
                await canal.send(f"{role.mention} — registro sem resposta há mais de {SLA_HORAS}h.")
            await canal.edit(topic=f"{canal.topic}:sla_avisado")

    @checar_sla.before_loop
    async def before_checar_sla(self):
        await self.bot.wait_until_ready()


async def setup(bot: commands.Bot):
    await bot.add_cog(Tickets(bot))
