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
def create_channel(name: str, type: int = 0, parent_id: str = "", topic: str = "") -> dict:
    """Cria um canal no servidor SONHE. type: 0=texto, 2=voz, 15=forum. parent_id opcional (categoria)."""
    payload = {"name": name, "type": type}
    if parent_id:
        payload["parent_id"] = parent_id
    if topic:
        payload["topic"] = topic

    with _client() as c:
        r = c.post(f"/guilds/{config.GUILD_ID}/channels", json=payload)
        r.raise_for_status()
        data = r.json()
        return {"id": data["id"], "name": data["name"], "type": data["type"]}


@mcp.tool()
def edit_channel(channel_id: str, topic: str = "", name: str = "") -> str:
    """Edita um canal existente (assunto/topico e/ou nome). Campos vazios sao ignorados."""
    payload = {}
    if topic:
        payload["topic"] = topic
    if name:
        payload["name"] = name

    with _client() as c:
        r = c.patch(f"/channels/{channel_id}", json=payload)
        r.raise_for_status()
        return "Canal atualizado."


@mcp.tool()
def delete_channel(channel_id: str) -> str:
    """Apaga um canal do servidor SONHE. Irreversivel."""
    with _client() as c:
        r = c.delete(f"/channels/{channel_id}")
        r.raise_for_status()
        return "Canal apagado."


@mcp.tool()
def edit_application(description: str = "", tags: list[str] | None = None) -> str:
    """Edita a descricao ('Sobre mim') e/ou as tags (max 5) do aplicativo do bot no Discord."""
    payload = {}
    if description:
        payload["description"] = description
    if tags:
        payload["tags"] = tags[:5]

    with _client() as c:
        r = c.patch("/applications/@me", json=payload)
        r.raise_for_status()
        return "Aplicativo atualizado."


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
