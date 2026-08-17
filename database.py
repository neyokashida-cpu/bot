"""
SONHE — Persistência (SQLite)
Um arquivo .db local, sem servidor externo. Guarda XP, Statz, amizade e
casamento — tudo que precisa sobreviver a um restart do bot.
"""

import datetime
import random
import string

import aiosqlite

CAMINHO_DB = "sonhe.db"

_SCHEMA = """
CREATE TABLE IF NOT EXISTS perfis (
    user_id INTEGER PRIMARY KEY,
    xp INTEGER NOT NULL DEFAULT 0,
    statz INTEGER NOT NULL DEFAULT 0,
    amizade INTEGER NOT NULL DEFAULT 0,
    ultimo_daily TEXT,
    ultima_mensagem_economia TEXT,
    casado_com INTEGER,
    casado_em TEXT,
    minecraft_nome TEXT,
    minecraft_status TEXT,
    minecraft_codigo TEXT,
    minecraft_vinculado_em TEXT
);

CREATE TABLE IF NOT EXISTS propostas_casamento (
    proponente_id INTEGER NOT NULL,
    alvo_id INTEGER NOT NULL,
    criado_em TEXT NOT NULL,
    PRIMARY KEY (proponente_id, alvo_id)
);

CREATE TABLE IF NOT EXISTS codigos_vinculo (
    codigo TEXT PRIMARY KEY,
    minecraft_nome TEXT NOT NULL,
    moedas_iniciais INTEGER NOT NULL DEFAULT 0,
    criado_em TEXT NOT NULL
);
"""


# Colunas adicionadas depois do schema inicial. CREATE TABLE IF NOT EXISTS não
# altera uma tabela "perfis" que já existe (bancos antigos, como o sonhe.db já
# em uso) — por isso a migração abaixo confere e adiciona só o que falta.
_COLUNAS_NOVAS = {
    "minecraft_nome": "TEXT",
    "minecraft_status": "TEXT",
    "minecraft_codigo": "TEXT",
    "minecraft_vinculado_em": "TEXT",
}


async def iniciar():
    async with aiosqlite.connect(CAMINHO_DB) as db:
        await db.executescript(_SCHEMA)
        cursor = await db.execute("PRAGMA table_info(perfis)")
        colunas_existentes = {linha[1] for linha in await cursor.fetchall()}
        for nome, tipo in _COLUNAS_NOVAS.items():
            if nome not in colunas_existentes:
                await db.execute(f"ALTER TABLE perfis ADD COLUMN {nome} {tipo}")
        await db.commit()


async def _garantir_perfil(db: aiosqlite.Connection, user_id: int):
    await db.execute("INSERT OR IGNORE INTO perfis (user_id) VALUES (?)", (user_id,))


async def obter_perfil(user_id: int) -> dict:
    async with aiosqlite.connect(CAMINHO_DB) as db:
        db.row_factory = aiosqlite.Row
        await _garantir_perfil(db, user_id)
        await db.commit()
        cursor = await db.execute("SELECT * FROM perfis WHERE user_id = ?", (user_id,))
        linha = await cursor.fetchone()
        return dict(linha)


async def ajustar_xp(user_id: int, quantidade: int):
    async with aiosqlite.connect(CAMINHO_DB) as db:
        await _garantir_perfil(db, user_id)
        await db.execute("UPDATE perfis SET xp = xp + ? WHERE user_id = ?", (quantidade, user_id))
        await db.commit()


async def ajustar_statz(user_id: int, quantidade: int):
    async with aiosqlite.connect(CAMINHO_DB) as db:
        await _garantir_perfil(db, user_id)
        await db.execute("UPDATE perfis SET statz = statz + ? WHERE user_id = ?", (quantidade, user_id))
        await db.commit()


async def ajustar_amizade(user_id: int, quantidade: int):
    async with aiosqlite.connect(CAMINHO_DB) as db:
        await _garantir_perfil(db, user_id)
        await db.execute("UPDATE perfis SET amizade = amizade + ? WHERE user_id = ?", (quantidade, user_id))
        await db.commit()


async def marcar_daily(user_id: int, quantidade: int) -> bool:
    """Concede o daily se passou 24h desde o último. Retorna True se concedeu."""
    agora = datetime.datetime.now(datetime.timezone.utc)
    async with aiosqlite.connect(CAMINHO_DB) as db:
        db.row_factory = aiosqlite.Row
        await _garantir_perfil(db, user_id)
        cursor = await db.execute("SELECT ultimo_daily FROM perfis WHERE user_id = ?", (user_id,))
        linha = await cursor.fetchone()
        ultimo = linha["ultimo_daily"]
        if ultimo:
            ultimo_dt = datetime.datetime.fromisoformat(ultimo)
            if agora - ultimo_dt < datetime.timedelta(hours=24):
                return False

        await db.execute(
            "UPDATE perfis SET statz = statz + ?, ultimo_daily = ? WHERE user_id = ?",
            (quantidade, agora.isoformat(), user_id),
        )
        await db.commit()
        return True


async def cooldown_mensagem_ok(user_id: int, segundos: int) -> bool:
    """Confere e já atualiza o cooldown de XP/Statz por mensagem (evita farm)."""
    agora = datetime.datetime.now(datetime.timezone.utc)
    async with aiosqlite.connect(CAMINHO_DB) as db:
        db.row_factory = aiosqlite.Row
        await _garantir_perfil(db, user_id)
        cursor = await db.execute(
            "SELECT ultima_mensagem_economia FROM perfis WHERE user_id = ?", (user_id,)
        )
        linha = await cursor.fetchone()
        ultima = linha["ultima_mensagem_economia"]
        if ultima:
            ultima_dt = datetime.datetime.fromisoformat(ultima)
            if agora - ultima_dt < datetime.timedelta(seconds=segundos):
                return False

        await db.execute(
            "UPDATE perfis SET ultima_mensagem_economia = ? WHERE user_id = ?",
            (agora.isoformat(), user_id),
        )
        await db.commit()
        return True


async def criar_proposta(proponente_id: int, alvo_id: int):
    agora = datetime.datetime.now(datetime.timezone.utc).isoformat()
    async with aiosqlite.connect(CAMINHO_DB) as db:
        await db.execute(
            "INSERT OR REPLACE INTO propostas_casamento (proponente_id, alvo_id, criado_em) "
            "VALUES (?, ?, ?)",
            (proponente_id, alvo_id, agora),
        )
        await db.commit()


async def obter_proposta(proponente_id: int, alvo_id: int) -> dict | None:
    async with aiosqlite.connect(CAMINHO_DB) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT * FROM propostas_casamento WHERE proponente_id = ? AND alvo_id = ?",
            (proponente_id, alvo_id),
        )
        linha = await cursor.fetchone()
        return dict(linha) if linha else None


async def remover_proposta(proponente_id: int, alvo_id: int):
    async with aiosqlite.connect(CAMINHO_DB) as db:
        await db.execute(
            "DELETE FROM propostas_casamento WHERE proponente_id = ? AND alvo_id = ?",
            (proponente_id, alvo_id),
        )
        await db.commit()


async def casar(user_a: int, user_b: int):
    agora = datetime.datetime.now(datetime.timezone.utc).isoformat()
    async with aiosqlite.connect(CAMINHO_DB) as db:
        await _garantir_perfil(db, user_a)
        await _garantir_perfil(db, user_b)
        await db.execute(
            "UPDATE perfis SET casado_com = ?, casado_em = ? WHERE user_id = ?",
            (user_b, agora, user_a),
        )
        await db.execute(
            "UPDATE perfis SET casado_com = ?, casado_em = ? WHERE user_id = ?",
            (user_a, agora, user_b),
        )
        await db.commit()


async def divorciar(user_a: int, user_b: int):
    async with aiosqlite.connect(CAMINHO_DB) as db:
        await db.execute(
            "UPDATE perfis SET casado_com = NULL, casado_em = NULL WHERE user_id IN (?, ?)",
            (user_a, user_b),
        )
        await db.commit()


# ── Vinculação Minecraft ↔ Discord ──────────────────────────
# Fluxo atual (automático, via bridge — precisa de @minecraft/server-net
# liberado no host, ver ADDONS/SonheBridge_BP):
#   1. O jogador roda "!vincular" dentro do jogo. O addon manda o nome dele
#      (e o saldo atual do placar sonhe_moedas) pro bot via HTTP.
#   2. O bot gera um código curto de uso único (criar_codigo_vinculo) e
#      devolve pro jogo — o addon mostra o código só pra esse jogador.
#   3. O jogador roda /vincular <código> no Discord. Se o código bater e não
#      tiver expirado, o vínculo é confirmado na hora, sem staff.
# /admin link e /admin unlink continuam existindo como override manual pra
# staff (ex: jogador sem acesso ao Discord no momento, ou correção de erro).


async def criar_codigo_vinculo(nome_minecraft: str, moedas_iniciais: int = 0) -> str:
    """Gera um código de uso único pro jogador confirmar no Discord com /vincular."""
    codigo = "".join(random.choices(string.ascii_uppercase + string.digits, k=4))
    agora = datetime.datetime.now(datetime.timezone.utc).isoformat()
    async with aiosqlite.connect(CAMINHO_DB) as db:
        await db.execute(
            "INSERT OR REPLACE INTO codigos_vinculo (codigo, minecraft_nome, moedas_iniciais, criado_em) "
            "VALUES (?, ?, ?, ?)",
            (codigo, nome_minecraft, moedas_iniciais, agora),
        )
        await db.commit()
    return codigo


async def consumir_codigo_vinculo(codigo: str, minutos_validade: int) -> dict | None:
    """Apaga o código (uso único) e retorna {minecraft_nome, moedas_iniciais} se ainda era válido."""
    codigo = codigo.strip().upper()
    async with aiosqlite.connect(CAMINHO_DB) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT * FROM codigos_vinculo WHERE codigo = ?", (codigo,))
        linha = await cursor.fetchone()
        if not linha:
            return None
        await db.execute("DELETE FROM codigos_vinculo WHERE codigo = ?", (codigo,))
        await db.commit()

    criado_em = datetime.datetime.fromisoformat(linha["criado_em"])
    agora = datetime.datetime.now(datetime.timezone.utc)
    if agora - criado_em > datetime.timedelta(minutes=minutos_validade):
        return None
    return {"minecraft_nome": linha["minecraft_nome"], "moedas_iniciais": linha["moedas_iniciais"]}


async def confirmar_vinculo(user_id: int, nome_minecraft: str):
    """Uso por staff (/admin link) ou pela confirmação automática via código."""
    agora = datetime.datetime.now(datetime.timezone.utc).isoformat()
    async with aiosqlite.connect(CAMINHO_DB) as db:
        await _garantir_perfil(db, user_id)
        await db.execute(
            "UPDATE perfis SET minecraft_nome = ?, minecraft_status = 'confirmado', "
            "minecraft_codigo = NULL, minecraft_vinculado_em = ? WHERE user_id = ?",
            (nome_minecraft, agora, user_id),
        )
        await db.commit()


async def desvincular_minecraft(user_id: int):
    async with aiosqlite.connect(CAMINHO_DB) as db:
        await db.execute(
            "UPDATE perfis SET minecraft_nome = NULL, minecraft_status = NULL, "
            "minecraft_codigo = NULL, minecraft_vinculado_em = NULL WHERE user_id = ?",
            (user_id,),
        )
        await db.commit()


async def obter_vinculo_confirmado_por_nome(nome_minecraft: str) -> dict | None:
    """Confere se esse nome já está confirmado em OUTRO perfil (evita duplicar)."""
    async with aiosqlite.connect(CAMINHO_DB) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT * FROM perfis WHERE minecraft_status = 'confirmado' "
            "AND minecraft_nome = ? COLLATE NOCASE",
            (nome_minecraft,),
        )
        linha = await cursor.fetchone()
        return dict(linha) if linha else None
