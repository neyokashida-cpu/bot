"""
SONHE — MCP server pra Claude Code controlar o bot via API REST do Discord.
Nao usa gateway (nao conflita com main.py), so chama https://discord.com/api/v10.
Roda via `claude mcp add sonhe-discord -- python mcp_discord_server.py`.
"""

import httpx
from mcp.server.mcpserver import MCPServer

import config

API = "https://discord.com/api/v10"
HEADERS = {"Authorization": f"Bot {config.BOT_TOKEN}", "Content-Type": "application/json"}

mcp = MCPServer(name="sonhe-discord")


def _client() -> httpx.Client:
    return httpx.Client(base_url=API, headers=HEADERS, timeout=15)


@mcp.tool()
def send_message(channel_id: str, content: str) -> str:
    """Envia uma mensagem de texto simples num canal do Discord."""
    with _client() as c:
        r = c.post(f"/channels/{channel_id}/messages", json={"content": content})
        r.raise_for_status()
        return f"Mensagem enviada (id {r.json()['id']})"


@mcp.tool()
def send_embed(
    channel_id: str,
    title: str = "",
    description: str = "",
    color: int = 0x1B1F3B,
    image_url: str = "",
    thumbnail_url: str = "",
    footer: str = "",
    author_name: str = "",
) -> str:
    """Envia um embed num canal do Discord. Campos vazios sao omitidos do embed."""
    embed = {"title": title, "description": description, "color": color}
    if image_url:
        embed["image"] = {"url": image_url}
    if thumbnail_url:
        embed["thumbnail"] = {"url": thumbnail_url}
    if footer:
        embed["footer"] = {"text": footer}
    if author_name:
        embed["author"] = {"name": author_name}

    with _client() as c:
        r = c.post(f"/channels/{channel_id}/messages", json={"embeds": [embed]})
        r.raise_for_status()
        return f"Embed enviado (id {r.json()['id']})"


@mcp.tool()
def add_role(user_id: str, role_id: str) -> str:
    """Adiciona um cargo a um membro do servidor SONHE."""
    with _client() as c:
        r = c.put(f"/guilds/{config.GUILD_ID}/members/{user_id}/roles/{role_id}")
        r.raise_for_status()
        return "Cargo adicionado."


@mcp.tool()
def remove_role(user_id: str, role_id: str) -> str:
    """Remove um cargo de um membro do servidor SONHE."""
    with _client() as c:
        r = c.delete(f"/guilds/{config.GUILD_ID}/members/{user_id}/roles/{role_id}")
        r.raise_for_status()
        return "Cargo removido."


@mcp.tool()
def list_channels() -> list[dict]:
    """Lista os canais do servidor SONHE (id, nome, tipo)."""
    with _client() as c:
        r = c.get(f"/guilds/{config.GUILD_ID}/channels")
        r.raise_for_status()
        return [{"id": ch["id"], "name": ch["name"], "type": ch["type"]} for ch in r.json()]


@mcp.tool()
def list_roles() -> list[dict]:
    """Lista os cargos do servidor SONHE (id, nome)."""
    with _client() as c:
        r = c.get(f"/guilds/{config.GUILD_ID}/roles")
        r.raise_for_status()
        return [{"id": role["id"], "name": role["name"]} for role in r.json()]


if __name__ == "__main__":
    mcp.run()
