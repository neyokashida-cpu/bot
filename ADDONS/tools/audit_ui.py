#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
audit_ui.py - auditoria estatica de JSON UI (Bedrock 1.26.x) para o SONHE Menu.

Uso:  python ADDONS/tools/audit_ui.py ADDONS/SonheMenu_RP
Exit code 1 se houver ERRO. Rodar SEMPRE antes de abrir o jogo.
Sem dependencia externa.
"""
import json, os, re, struct, sys, collections

ERR, WARN = [], []
def erro(m): ERR.append(m)
def aviso(m): WARN.append(m)

NS_VANILLA = {
    "common", "common_buttons", "common_dialogs", "common_toggles", "settings_common",
    "server_form", "chest_ui", "trade", "inventory", "hud", "start", "play",
    "pause", "sidebar_navigation", "achievements", "book", "sign", "npc_interact",
    "crafting", "furnace", "anvil", "enchanting", "beacon", "brewing_stand",
    "loom", "smithing_table", "stonecutter", "cartography", "grindstone",
    "structure_editor", "how_to_play", "toast_screen", "ui_holo_common",
}
PROP_PROIBIDA = {
    "modifications":    "regra do projeto: nao usar modifications",
    "collection_index": "nao existe nesta build (Unknown property)",
    "nine_slice_size":  "grafia errada; nine-slice mora no .json irmao do PNG",
    "z_order":          "legacy, ignorado (use layer)",
    "alignment":        "legacy, ignorado (use anchor_from/anchor_to)",
    "scroll_report":    "legacy, ignorado",
}
BINDINGS_OK = {
    "#title_text", "#form_text", "#form_button_contents", "#form_button_text",
    "#form_button_texture", "#form_button_texture_file_system",
    "#collection_length", "#maximum_grid_items", "#texture", "#texture_file_system",
    "#visible", "#enabled", "#nineslice_size",
}
TIPOS_COLLECTION = {"stack_panel", "collection_panel", "grid"}


def strip_jsonc(txt):
    out, i, n, in_s = [], 0, len(txt), False
    while i < n:
        c = txt[i]
        if in_s:
            out.append(c)
            if c == "\\" and i + 1 < n:
                out.append(txt[i + 1]); i += 2; continue
            if c == '"': in_s = False
            i += 1; continue
        if c == '"':
            in_s = True; out.append(c); i += 1; continue
        if c == "/" and i + 1 < n and txt[i + 1] == "/":
            while i < n and txt[i] != "\n": i += 1
            continue
        if c == "/" and i + 1 < n and txt[i + 1] == "*":
            i += 2
            while i + 1 < n and not (txt[i] == "*" and txt[i + 1] == "/"): i += 1
            i += 2; continue
        out.append(c); i += 1
    return "".join(out)


def png_size(path):
    with open(path, "rb") as f:
        d = f.read(33)
    if d[:8] != b"\x89PNG\r\n\x1a\n": return None
    w, h = struct.unpack(">II", d[16:24])
    return w, h, d[24], d[25]


def eixo(v):
    if isinstance(v, bool): return "unknown"
    if isinstance(v, (int, float)): return "fixed"
    if not isinstance(v, str): return "unknown"
    s = v.replace(" ", "")
    if s.startswith("$"): return "var"
    if s == "fill": return "parent"
    if s == "default": return "parent"
    if "%cm" in s or "%c" in s: return "child"
    if "%sm" in s: return "sibling"
    if "%x" in s or "%y" in s: return "self"
    if "%" in s: return "parent"
    if re.fullmatch(r"-?\d+(px)?", s): return "fixed"
    return "unknown"


def size_eixos(sz):
    if isinstance(sz, list) and len(sz) == 2: return eixo(sz[0]), eixo(sz[1])
    if isinstance(sz, str) and sz.startswith("$"): return "var", "var"
    return None


def main(pack):
    ui_dir = os.path.join(pack, "ui")
    defs_path = os.path.join(ui_dir, "_ui_defs.json")
    if not os.path.isfile(defs_path):
        erro("_ui_defs.json nao encontrado em " + ui_dir); return finish()
    listados = json.loads(open(defs_path, encoding="utf-8-sig").read()).get("ui_defs", [])

    no_disco = sorted("ui/" + f for f in os.listdir(ui_dir)
                      if f.endswith(".json") and f != "_ui_defs.json")
    for f in listados:
        if not os.path.isfile(os.path.join(pack, f)):
            erro("_ui_defs lista arquivo inexistente: " + f)
    for f in no_disco:
        if f not in listados:
            erro("arquivo NAO listado em _ui_defs (o jogo vai ignorar): " + f)

    arquivos = {}
    for rel in listados:
        p = os.path.join(pack, rel)
        if not os.path.isfile(p): continue
        raw = open(p, "rb").read()
        if raw[:3] == b"\xef\xbb\xbf":
            erro(rel + ": BOM UTF-8 presente (salve sem BOM)")
        try:
            txt = raw.decode("utf-8")
        except UnicodeDecodeError:
            erro(rel + ": nao e UTF-8 valido (Set-Content grava ANSI; use -Encoding utf8)")
            continue
        if b"\xa7" in raw.replace(b"\xc2\xa7", b""):
            erro(rel + ": byte 0xA7 solto = secao em ANSI. Regravar em UTF-8.")
        limpo = strip_jsonc(txt)
        if re.search(r",\s*[}\]]", limpo):
            erro(rel + ": trailing comma")
        try:
            arquivos[rel] = json.loads(limpo)
        except Exception as e:
            erro(rel + ": JSON invalido: " + str(e))

    defs, ns_locais = {}, set()
    for rel, doc in arquivos.items():
        ns = doc.get("namespace")
        if not ns:
            erro(rel + ": sem 'namespace'"); continue
        ns_locais.add(ns)
        for k, v in doc.items():
            if k == "namespace" or k.startswith("//"): continue
            nome = k.split("@")[0]
            if (ns, nome) in defs:
                erro("def duplicada '%s' no namespace '%s' (%s e %s)"
                     % (nome, ns, defs[(ns, nome)][0], rel))
            defs[(ns, nome)] = (rel, v, k)

    def filhos_de(corpo):
        for item in corpo.get("controls", []) or []:
            if not isinstance(item, dict): continue
            for k, v in item.items():
                yield k, (v if isinstance(v, dict) else {})

    def walk(rel, ns, path, key, corpo, pai_eixos, prof_scroll):
        nome = key.split("@")[0]
        base = key.split("@")[1] if "@" in key else None
        aqui = "%s:%s/%s" % (rel, path, key)

        if base:
            if base.startswith("$"):
                pass
            elif "." in base:
                bns, bdef = base.split(".", 1)
                if bns not in NS_VANILLA and bns not in ns_locais:
                    erro(aqui + ": @base '%s' -> namespace desconhecido" % base)
                elif bns in ns_locais and (bns, bdef) not in defs:
                    erro(aqui + ": @base '%s' nao existe no pack" % base)
                if bns == ns and bdef == nome:
                    erro(aqui + ": nome do filho == nome do proprio @base (quebra silenciosa)")
            else:
                if (ns, base) not in defs:
                    erro(aqui + ": @base local '%s' nao existe" % base)
                if base == nome:
                    erro(aqui + ": auto-heranca")
        elif "type" not in corpo:
            erro(aqui + ": sem 'type' e sem @base")

        for p, motivo in PROP_PROIBIDA.items():
            if p in corpo:
                erro(aqui + ": propriedade proibida '%s' (%s)" % (p, motivo))

        tipo = corpo.get("type")
        if tipo == "grid" and "collection_name" in corpo:
            erro(aqui + ": type:grid + collection_name (proibido pela regra do projeto)")
        if corpo.get("grid_rescaling_type") == "vertical":
            erro(aqui + ": grid_rescaling_type 'vertical' pode crashar o jogo")
        if "collection_name" in corpo and tipo and tipo not in TIPOS_COLLECTION:
            erro(aqui + ": collection_name em type '%s' (so stack_panel/collection_panel/grid)" % tipo)
        if "factory" in corpo and tipo and tipo not in TIPOS_COLLECTION:
            aviso(aqui + ": factory em type '%s'" % tipo)

        sz = corpo.get("size")
        eixos = size_eixos(sz) if sz is not None else None
        if eixos and "unknown" in eixos:
            erro(aqui + ": unidade de size invalida em %r" % (sz,))
        if pai_eixos and eixos:
            for i, ax in enumerate(("X", "Y")):
                if pai_eixos[i] == "child" and eixos[i] == "parent":
                    erro(aqui + ": DEPENDENCIA CIRCULAR no eixo %s (pai child-driven x filho %r)"
                         % (ax, sz[i]))
                if eixos[i] == "sibling":
                    aviso(aqui + ": %sm no eixo " + ax + " (pouco confiavel)")

        declaradas = set()
        for k in corpo:
            if k.startswith("$"):
                declaradas.add(k[1:].split("|")[0])
        corpo_txt = json.dumps(corpo, ensure_ascii=False)
        for prop in ("size", "offset", "texture", "max_size", "min_size"):
            v = corpo.get(prop)
            if v is None: continue
            for tok in set(re.findall(r"\$[A-Za-z0-9_]+", json.dumps(v, ensure_ascii=False))):
                if tok[1:] not in declaradas and (tok + "|default") not in corpo_txt:
                    aviso(aqui + ": usa %s em '%s' sem |default no mesmo def" % (tok, prop))

        bl = corpo.get("bindings")
        if isinstance(bl, list):
            vistos = set()
            for b in bl:
                if not isinstance(b, dict): continue
                bn = b.get("binding_name")
                if bn and bn not in BINDINGS_OK and not bn.startswith("$"):
                    aviso(aqui + ": binding_name desconhecido '%s' (falha em silencio)" % bn)
                if b.get("binding_type") == "view":
                    for ref in re.findall(r"#[a-z_]+", b.get("source_property_name", "") or ""):
                        if ref not in vistos and not b.get("source_control_name") \
                           and ref not in ("#texture", "#texture_file_system"):
                            erro(aqui + ": view binding le %s antes do data binding no mesmo array" % ref)
                elif bn:
                    vistos.add(bn)

        eh_scroll = bool(base) and base.endswith("scrolling_panel")
        if eh_scroll and prof_scroll >= 1:
            erro(aqui + ": scrolling_panel dentro de scrolling_panel")

        lista = list(filhos_de(corpo))
        nomes = [k.split("@")[0] for k, _ in lista]
        for d, c in collections.Counter(nomes).items():
            if c > 1: erro(aqui + ": dois irmaos com o mesmo nome '%s'" % d)
        fills = 0
        for ck, cv in lista:
            csz = cv.get("size")
            if isinstance(csz, list) and any(x == "fill" for x in csz): fills += 1
        if fills > 1:
            erro(aqui + ": %d filhos com 'fill' no mesmo container" % fills)
        if fills >= 1 and eixos and eixos[1] == "child":
            erro(aqui + ": filho com 'fill' dentro de container de altura child-driven")

        p2 = path + "/" + nome
        for ck, cv in lista:
            walk(rel, ns, p2, ck, cv, eixos or pai_eixos, prof_scroll + (1 if eh_scroll else 0))

    for (ns, nome), (rel, corpo, key) in sorted(defs.items()):
        if isinstance(corpo, dict):
            walk(rel, ns, "", key, corpo, None, 0)

    refs = set()
    for rel, doc in arquivos.items():
        refs |= set(re.findall(r'"(textures/[^"]+)"', json.dumps(doc)))
    for t in sorted(refs):
        png = os.path.join(pack, t + ".png")
        if not os.path.isfile(png):
            if "/sonhe/" in t: erro("textura do pack nao existe: " + t + ".png")
            continue
        w, h, bd, ct = png_size(png)
        if max(w, h) > 128:
            aviso("%s.png %dx%d: maior que qualquer textura de UI vanilla (max 128)" % (t, w, h))
        if ct not in (4, 6):
            aviso("%s.png colortype %d: SEM canal alpha (moldura nunca sera vazada)" % (t, ct))
        side = os.path.join(pack, t + ".json")
        if os.path.isfile(side):
            s = json.loads(open(side, encoding="utf-8-sig").read())
            extra = set(s) - {"nineslice_size", "base_size", "tiled"}
            if extra: erro("%s.json: chaves invalidas %s" % (t, sorted(extra)))
            if "nineslice_size" in s and "base_size" not in s:
                erro(t + ".json: nineslice_size sem base_size")
            bs, nss = s.get("base_size"), s.get("nineslice_size")
            lados = nss if isinstance(nss, list) else ([nss] * 4 if nss is not None else [])
            if bs and lados:
                if lados[0] + lados[2 % len(lados)] >= bs[0] or lados[1 % len(lados)] + lados[-1] >= bs[1]:
                    erro("%s.json: nineslice %s nao deixa centro dentro de base_size %s" % (t, nss, bs))
                if max(lados) > 16:
                    aviso("%s.json: nineslice %s = borda de %dpx NA TELA (vanilla usa 1-8)"
                          % (t, nss, max(lados)))
            if bs and (bs[0] != w or bs[1] != h):
                aviso("%s.json: base_size %s != PNG %dx%d (supersample)" % (t, bs, w, h))
    return finish()


def finish():
    for m in ERR: print("ERRO  " + m)
    for m in WARN: print("AVISO " + m)
    print("\n-- %d erro(s), %d aviso(s)" % (len(ERR), len(WARN)))
    return 1 if ERR else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "."))
