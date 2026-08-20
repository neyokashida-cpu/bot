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

-- Pares chave/valor genéricos pra estado do bot que precisa sobreviver a um
-- restart mas não justifica tabela própria (ex: ID da mensagem fixa de
-- #passagem — ver cogs/status.py).
CREATE TABLE IF NOT EXISTS estado (
    chave TEXT PRIMARY KEY,
    valor TEXT NOT NULL
);

-- Auction House — ver AUCTION_HOUSE.md pra arquitetura completa. O ITEM em
-- si nunca é guardado aqui (fica em dynamic properties do mundo, no lado
-- Minecraft) — essas duas tabelas só espelham preço/status do anúncio e
-- garantem que dinheiro (Statz) só se move uma vez por transactionId.
CREATE TABLE IF NOT EXISTS ah_anuncios (
    listing_id          TEXT PRIMARY KEY,
    vendedor_discord_id TEXT NOT NULL,
    vendedor_nome_mc    TEXT NOT NULL,
    preco               INTEGER NOT NULL,
    status              TEXT NOT NULL DEFAULT 'ATIVO',
    criado_em           TEXT NOT NULL,
    expira_em           TEXT NOT NULL,
    finalizado_em       TEXT
);

-- transaction_id é a chave de idempotência: uma compra só é processada (só
-- move Statz) a primeira vez que esse transactionId aparece aqui — um
-- retry com o mesmo id nunca duplica débito/crédito (ver
-- confirmar_compra_ah).
CREATE TABLE IF NOT EXISTS ah_transacoes (
    transaction_id       TEXT PRIMARY KEY,
    listing_id           TEXT NOT NULL,
    comprador_discord_id TEXT NOT NULL,
    vendedor_discord_id  TEXT NOT NULL,
    valor                INTEGER NOT NULL,
    criado_em            TEXT NOT NULL
);

-- Índices pra consulta administrativa (/ah-listar, investigar reclamação)
-- não virar full scan conforme os anúncios/transações acumulam.
CREATE INDEX IF NOT EXISTS idx_ah_anuncios_status ON ah_anuncios(status);
CREATE INDEX IF NOT EXISTS idx_ah_anuncios_vendedor ON ah_anuncios(vendedor_discord_id);
CREATE INDEX IF NOT EXISTS idx_ah_transacoes_listing ON ah_transacoes(listing_id);
CREATE INDEX IF NOT EXISTS idx_ah_transacoes_comprador ON ah_transacoes(comprador_discord_id);
CREATE INDEX IF NOT EXISTS idx_ah_transacoes_vendedor ON ah_transacoes(vendedor_discord_id);
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


async def obter_estado(chave: str) -> str | None:
    async with aiosqlite.connect(CAMINHO_DB) as db:
        cursor = await db.execute("SELECT valor FROM estado WHERE chave = ?", (chave,))
        linha = await cursor.fetchone()
        return linha[0] if linha else None


async def definir_estado(chave: str, valor: str):
    async with aiosqlite.connect(CAMINHO_DB) as db:
        await db.execute(
            "INSERT INTO estado (chave, valor) VALUES (?, ?) "
            "ON CONFLICT(chave) DO UPDATE SET valor = excluded.valor",
            (chave, valor),
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


# ── Auction House ────────────────────────────────────────────
# Ver AUCTION_HOUSE.md pra arquitetura completa. Regra dura: o item nunca
# passa por aqui (fica em dynamic properties do mundo, no addon) — essas
# funções só movem Statz e controlam o status do anúncio (ATIVO/VENDIDO/
# CANCELADO/EXPIRADO). cogs/bridge.py é quem chama isso, nunca o addon
# direto.


async def criar_anuncio_ah(listing_id: str, vendedor_user_id: int, vendedor_nome_mc: str, preco: int, expira_em: str):
    agora = datetime.datetime.now(datetime.timezone.utc).isoformat()
    async with aiosqlite.connect(CAMINHO_DB) as db:
        await db.execute(
            "INSERT INTO ah_anuncios (listing_id, vendedor_discord_id, vendedor_nome_mc, preco, "
            "status, criado_em, expira_em) VALUES (?, ?, ?, ?, 'ATIVO', ?, ?)",
            (listing_id, str(vendedor_user_id), vendedor_nome_mc, preco, agora, expira_em),
        )
        await db.commit()


async def cancelar_anuncio_ah(listing_id: str, vendedor_user_id: int) -> bool:
    """Só cancela se o anúncio existir, ainda estiver ATIVO e pertencer a esse vendedor."""
    agora = datetime.datetime.now(datetime.timezone.utc).isoformat()
    async with aiosqlite.connect(CAMINHO_DB) as db:
        cursor = await db.execute(
            "UPDATE ah_anuncios SET status = 'CANCELADO', finalizado_em = ? "
            "WHERE listing_id = ? AND vendedor_discord_id = ? AND status = 'ATIVO'",
            (agora, listing_id, str(vendedor_user_id)),
        )
        await db.commit()
        return cursor.rowcount > 0


async def forcar_cancelar_anuncio_ah(listing_id: str) -> bool:
    """Uso administrativo (/ah-forcar-cancelar) — mesma query de cancelar_anuncio_ah, mas sem
    exigir que seja o vendedor pedindo. A devolução do item ao vendedor acontece sozinha no
    próximo ciclo de reconciliação do addon (ele detecta que o status não é mais ATIVO)."""
    agora = datetime.datetime.now(datetime.timezone.utc).isoformat()
    async with aiosqlite.connect(CAMINHO_DB) as db:
        cursor = await db.execute(
            "UPDATE ah_anuncios SET status = 'CANCELADO', finalizado_em = ? "
            "WHERE listing_id = ? AND status = 'ATIVO'",
            (agora, listing_id),
        )
        await db.commit()
        return cursor.rowcount > 0


async def listar_anuncios_ativos_ah() -> list[dict]:
    """Uso administrativo (/ah-listar)."""
    async with aiosqlite.connect(CAMINHO_DB) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT * FROM ah_anuncios WHERE status = 'ATIVO' ORDER BY criado_em ASC"
        )
        linhas = await cursor.fetchall()
        return [dict(linha) for linha in linhas]


async def obter_status_anuncios_ah(listing_ids: list[str]) -> dict[str, dict]:
    """Usado pela reconciliação periódica do addon (POST /ah/anuncios-status) — devolve o
    status atual de cada listing_id pedido, pra o addon comparar contra o que tem em escrow
    local e resolver o que ficou pendente (venda/cancelamento/expiração que o Minecraft não
    chegou a processar por queda de processo/rede). Um listing só tem 1 transação possível
    (só pode ser vendido uma vez), então o LEFT JOIN nunca duplica linha."""
    if not listing_ids:
        return {}
    async with aiosqlite.connect(CAMINHO_DB) as db:
        db.row_factory = aiosqlite.Row
        marcadores = ",".join("?" for _ in listing_ids)
        cursor = await db.execute(
            f"""
            SELECT a.listing_id, a.status, p.minecraft_nome AS comprador_nome_mc
            FROM ah_anuncios a
            LEFT JOIN ah_transacoes t ON t.listing_id = a.listing_id
            LEFT JOIN perfis p ON p.user_id = CAST(t.comprador_discord_id AS INTEGER)
            WHERE a.listing_id IN ({marcadores})
            """,
            listing_ids,
        )
        linhas = await cursor.fetchall()

    resultado = {}
    for linha in linhas:
        item = {"status": linha["status"]}
        if linha["status"] == "VENDIDO" and linha["comprador_nome_mc"]:
            item["compradorNomeMc"] = linha["comprador_nome_mc"]
        resultado[linha["listing_id"]] = item
    return resultado


async def expirar_anuncio_ah(listing_id: str) -> bool:
    """Chamado pela rotina periódica do addon — só marca EXPIRADO se ainda estiver ATIVO."""
    agora = datetime.datetime.now(datetime.timezone.utc).isoformat()
    async with aiosqlite.connect(CAMINHO_DB) as db:
        cursor = await db.execute(
            "UPDATE ah_anuncios SET status = 'EXPIRADO', finalizado_em = ? "
            "WHERE listing_id = ? AND status = 'ATIVO'",
            (agora, listing_id),
        )
        await db.commit()
        return cursor.rowcount > 0


async def confirmar_compra_ah(transaction_id: str, listing_id: str, comprador_user_id: int) -> dict:
    """Compra atômica e idempotente — nunca move Statz duas vezes pro mesmo transaction_id.

    Retorna {"status": "ok", "preco": int, "vendedor_nome_mc": str} em sucesso (inclusive num
    retry idempotente), ou {"status": "<motivo>"} sem tocar em Statz/status quando falha:
    "anuncio_indisponivel" (não existe), "ja_vendido" (outro comprador ganhou a corrida),
    "comprador_e_vendedor", "saldo_insuficiente".
    """
    async with aiosqlite.connect(CAMINHO_DB) as db:
        db.row_factory = aiosqlite.Row

        cursor = await db.execute("SELECT * FROM ah_anuncios WHERE listing_id = ?", (listing_id,))
        anuncio = await cursor.fetchone()
        if anuncio is None:
            return {"status": "anuncio_indisponivel"}

        # Idempotência: só existe uma linha em ah_transacoes pra esse transaction_id se a compra
        # JÁ foi concluída antes — um retry (rede, reconexão) repete a mesma resposta de sucesso
        # sem debitar/creditar de novo.
        cursor = await db.execute(
            "SELECT valor FROM ah_transacoes WHERE transaction_id = ?", (transaction_id,)
        )
        ja_concluida = await cursor.fetchone()
        if ja_concluida is not None:
            return {"status": "ok", "preco": ja_concluida["valor"], "vendedor_nome_mc": anuncio["vendedor_nome_mc"]}

        if anuncio["status"] != "ATIVO":
            return {"status": "anuncio_indisponivel"}

        if str(anuncio["vendedor_discord_id"]) == str(comprador_user_id):
            return {"status": "comprador_e_vendedor"}

        # Ganha a corrida quem conseguir essa UPDATE (afeta 0 ou 1 linha) — dois compradores
        # simultâneos nunca vendem o mesmo anúncio duas vezes.
        agora = datetime.datetime.now(datetime.timezone.utc).isoformat()
        cursor = await db.execute(
            "UPDATE ah_anuncios SET status = 'VENDIDO', finalizado_em = ? "
            "WHERE listing_id = ? AND status = 'ATIVO'",
            (agora, listing_id),
        )
        if cursor.rowcount == 0:
            await db.rollback()
            return {"status": "ja_vendido"}

        preco = anuncio["preco"]
        await _garantir_perfil(db, comprador_user_id)

        # Débito atômico e condicional — mesmo padrão do UPDATE de status acima (linha 421).
        # Duas compras concorrentes do MESMO comprador (dois anúncios diferentes, quase ao
        # mesmo tempo) nunca mais leem um saldo "válido" antes de qualquer commit: a segunda
        # perde a corrida AQUI (rowcount == 0), nunca no valor que tinha sido lido antes — um
        # SELECT + checagem em Python separados permitiriam saldo negativo (TOCTOU).
        cursor = await db.execute(
            "UPDATE perfis SET statz = statz - ? WHERE user_id = ? AND statz >= ?",
            (preco, comprador_user_id, preco),
        )
        if cursor.rowcount == 0:
            await db.rollback()  # desfaz o status='VENDIDO' de cima — o anúncio volta a ficar ATIVO
            return {"status": "saldo_insuficiente"}

        vendedor_user_id = int(anuncio["vendedor_discord_id"])
        await _garantir_perfil(db, vendedor_user_id)
        await db.execute("UPDATE perfis SET statz = statz + ? WHERE user_id = ?", (preco, vendedor_user_id))
        await db.execute(
            "INSERT INTO ah_transacoes "
            "(transaction_id, listing_id, comprador_discord_id, vendedor_discord_id, valor, criado_em) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (transaction_id, listing_id, str(comprador_user_id), str(vendedor_user_id), preco, agora),
        )
        await db.commit()
        return {"status": "ok", "preco": preco, "vendedor_nome_mc": anuncio["vendedor_nome_mc"]}
