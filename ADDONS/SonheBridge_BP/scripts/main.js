import { world, system, EquipmentSlot } from "@minecraft/server";
import { http, HttpRequestMethod, HttpHeader, HttpRequest } from "@minecraft/server-net";

// SONHE — ponte de chat com o Discord.
// Pack SEPARADO do SonheChat de propósito: @minecraft/server-net ainda é
// pré-lançamento (ago/2026) e só funciona se "@minecraft/server-net" estiver
// liberado no permissions.json do servidor. Se não estiver, é ESSE pack que
// falha ao carregar — o SonheChat (boas-vindas + rank/tag local) continua
// funcionando normal, porque não depende desse módulo.
//
// A API abaixo foi escrita com base na documentação oficial mais recente
// (learn.microsoft.com, atualizada em ago/2026), mas por ser preview ela
// pode ter mudado detalhes por versão — se algo não bater com o que
// aparecer no seu servidor, confere a versão exata do módulo primeiro.

// ══════════════════════════════════════════════════════════
// EDITAR AQUI antes de instalar no servidor:
const BRIDGE_URL = "https://SEU-APP.up.railway.app"; // URL pública do bot no Railway (sem / no final)
const BRIDGE_SECRET = "COLE_AQUI_O_MESMO_VALOR_DA_VARIAVEL_BRIDGE_SECRET_DO_RAILWAY";
// ══════════════════════════════════════════════════════════

const INTERVALO_POLLING_TICKS = 60; // 60 ticks ≈ 3s (20 ticks/s) — puxa mensagens/pedidos novos do Discord

const OBJ_RANK = "sonhe_rank"; // mesmo objetivo de scoreboard que o SonheChat_BP usa
const OBJ_TAG = "sonhe_tag";
const TAGS = ["", "Recém-chegado", "Explorador", "Investigador", "Guardião", "Veterano", "Lenda"];

// Placar de moedas locais do jogo. Não existe nenhum jeito de ganhar/gastar
// isso ainda (sem loja/comando pronto) — pensado pra ser setado manualmente
// por um admin via /scoreboard, ou por uma feature futura. No momento do
// /vincular, esse valor é somado UMA VEZ ao Statz do Discord (ver
// cogs/vinculacao.py) — depois disso o Discord vira a fonte única de
// verdade, não tem sincronização contínua.
const OBJ_MOEDAS = "sonhe_moedas";

// Cria os objetivos se ainda não existirem — inclui rank/tag pra esse pack
// funcionar sozinho mesmo sem o SonheChat_BP instalado (embora o normal seja
// os dois juntos).
function garantirObjetivos() {
    for (const [id, nome] of [
        [OBJ_RANK, "Rank SONHE"],
        [OBJ_TAG, "Tag SONHE"],
        [OBJ_MOEDAS, "Moedas SONHE"],
    ]) {
        if (!world.scoreboard.getObjective(id)) {
            world.scoreboard.addObjective(id, nome);
        }
    }
}
system.run(garantirObjetivos);

// Rank/tag são definidos por NOME (não por Entity online) porque o /vincular
// pode acontecer com o jogador momentaneamente fora do mundo, e porque
// scoreboard players set funciona por nome mesmo offline (cria uma entrada
// "fantasma" que passa a valer quando o jogador reconectar).
// world.getDimension() é chamado aqui dentro (não no topo do arquivo) porque
// esse arquivo roda em "early execution" no load do pack, e a API nativa
// ainda não está liberada nesse momento (gera ReferenceError e derruba o
// script inteiro, cancelando todos os subscribes abaixo).
function definirScorePorNome(objetivo, nomeJogador, valor) {
    const nomeSeguro = nomeJogador.replace(/"/g, "");
    // Dimension só tem runCommand (síncrono) — "runCommandAsync" nunca
    // existiu nessa API (confirmado na doc oficial); por isso essa chamada
    // sempre derrubava com "TypeError: not a function". runCommand lança
    // erro em caso de falha (ver try/catch nos dois lugares que chamam isso).
    try {
        world.getDimension("overworld").runCommand(`scoreboard players set "${nomeSeguro}" ${objetivo} ${valor}`);
    } catch (erro) {
        console.warn(`[SonheBridge] falha ao definir score "${objetivo}" de ${nomeJogador}: ${erro}`);
    }
}

// Nome amigável + artigo dos mobs mais comuns do survival, pra mensagem de
// morte citar quem matou ("por um zumbi") em vez de um "atacado(a)" genérico.
// O que não estiver aqui cai no typeId formatado (ver formatarNomeItem),
// com artigo neutro "um(a)" — nunca fica sem nome.
const NOMES_MOBS = {
    zombie: ["um", "zumbi"],
    husk: ["um", "zumbi do deserto"],
    drowned: ["um", "afogado"],
    zombie_villager: ["um", "zumbi aldeão"],
    skeleton: ["um", "esqueleto"],
    stray: ["um", "esqueleto glacial"],
    wither_skeleton: ["um", "esqueleto wither"],
    bogged: ["um", "bogged"],
    spider: ["uma", "aranha"],
    cave_spider: ["uma", "aranha das cavernas"],
    creeper: ["um", "creeper"],
    enderman: ["um", "Enderman"],
    endermite: ["um", "endermite"],
    witch: ["uma", "bruxa"],
    slime: ["um", "slime"],
    magma_cube: ["um", "cubo de magma"],
    blaze: ["um", "blaze"],
    ghast: ["um", "ghast"],
    phantom: ["um", "phantom"],
    pillager: ["um", "pilhador"],
    vindicator: ["um", "vindicador"],
    evocation_illager: ["um", "evocador"],
    ravager: ["um", "arrasador"],
    vex: ["um", "vex"],
    piglin: ["um", "piglin"],
    piglin_brute: ["um", "piglin brutamontes"],
    zombie_pigman: ["um", "zumbi porco"],
    hoglin: ["um", "hoglin"],
    zoglin: ["um", "zoglin"],
    wolf: ["um", "lobo"],
    polar_bear: ["um", "urso polar"],
    guardian: ["um", "guardião"],
    elder_guardian: ["um", "guardião ancião"],
    shulker: ["um", "shulker"],
    warden: ["o", "Warden"],
    breeze: ["um", "breeze"],
    wither: ["o", "Wither"],
    ender_dragon: ["o", "Dragão do Fim"],
};

function nomeMob(typeId) {
    const chave = typeId?.replace(/^minecraft:/, "");
    const [artigo, nome] = NOMES_MOBS[chave] ?? ["um(a)", formatarNomeItem(typeId ?? "algo")];
    return `${artigo} ${nome}`;
}

// Cobre as causas mais comuns em survival. Qualquer causa fora dessa lista
// cai no texto genérico do fim de mensagemMorte() — nunca fica sem mensagem.
// Lista oficial de causas: learn.microsoft.com (.../server/entitydamagecause)
const CAUSAS_MORTE = {
    fall: (v) => `${v} caiu de uma altura fatal.`,
    drowning: (v) => `${v} se afogou.`,
    lava: (v) => `${v} tentou nadar em lava.`,
    fire: (v) => `${v} pegou fogo.`,
    fireTick: (v) => `${v} queimou até o fim.`,
    starve: (v) => `${v} morreu de fome.`,
    void: (v) => `${v} caiu no vazio.`,
    suffocation: (v) => `${v} sufocou dentro de um bloco.`,
    lightning: (v) => `${v} foi atingido(a) por um raio.`,
    freezing: (v) => `${v} congelou.`,
    magma: (v) => `${v} pisou em magma.`,
    fallingBlock: (v) => `${v} foi esmagado(a) por um bloco.`,
    entityExplosion: (v, ehJogador, nomeAtacante) =>
        nomeAtacante ? `${v} foi explodido(a) por ${nomeAtacante}.` : `${v} foi pego(a) numa explosão.`,
    blockExplosion: (v) => `${v} foi pego(a) numa explosão.`,
    entityAttack: (v, ehJogador, nomeAtacante) =>
        ehJogador ? `${v} foi morto(a) por outro jogador.` : `${v} foi atacado(a) por ${nomeAtacante} e não resistiu.`,
    projectile: (v, ehJogador, nomeAtacante) =>
        ehJogador ? `${v} foi flechado(a) por outro jogador.` : `${v} foi atingido(a) por um projétil de ${nomeAtacante}.`,
};

function mensagemMorte(nomeVitima, causa, quemMatou) {
    const ehJogador = quemMatou?.typeId === "minecraft:player";
    const nomeAtacante = quemMatou && !ehJogador ? nomeMob(quemMatou.typeId) : null;
    const gerador = CAUSAS_MORTE[causa];
    if (gerador) return gerador(nomeVitima, ehJogador, nomeAtacante);
    return `${nomeVitima} não resistiu.`; // fallback genérico, cobre as causas mais raras
}

function obterTag(jogador) {
    const objetivo = world.scoreboard.getObjective(OBJ_TAG);
    if (!objetivo) return "";
    try {
        const indice = objetivo.getScore(jogador) ?? 0;
        return TAGS[indice] ?? "";
    } catch {
        return ""; // jogador sem score definido ainda
    }
}

function obterMoedas(jogador) {
    const objetivo = world.scoreboard.getObjective(OBJ_MOEDAS);
    if (!objetivo) return 0;
    try {
        return objetivo.getScore(jogador) ?? 0;
    } catch {
        return 0; // jogador sem score definido ainda
    }
}

function formatarNomeItem(typeId) {
    return typeId
        .replace(/^minecraft:/, "")
        .split("_")
        .map((p) => p.charAt(0).toUpperCase() + p.slice(1))
        .join(" ");
}

async function chamarBridge(caminho, corpo) {
    const req = new HttpRequest(`${BRIDGE_URL}${caminho}`);
    req.method = HttpRequestMethod.Post;
    req.headers = [
        new HttpHeader("Content-Type", "application/json"),
        new HttpHeader("Authorization", `Bearer ${BRIDGE_SECRET}`),
    ];
    req.body = JSON.stringify(corpo);
    req.timeout = 5;
    return http.request(req);
}

async function enviarParaDiscord(nomeJogador, mensagem, tag) {
    try {
        const resposta = await chamarBridge("/minecraft-chat", { jogador: nomeJogador, mensagem, tag });
        if (resposta.status !== 200) {
            console.warn(`[SonheBridge] backend respondeu status ${resposta.status}: ${resposta.body}`);
        }
    } catch (erro) {
        // Bridge fora do ar / sem internet liberada / módulo não habilitado.
        // Fica só no console do servidor — não interrompe o chat pro jogador.
        console.warn(`[SonheBridge] falha ao enviar mensagem pro Discord: ${erro}`);
    }
}

async function enviarMorteParaDiscord(mensagem) {
    try {
        await chamarBridge("/minecraft-morte", { mensagem });
    } catch (erro) {
        console.warn(`[SonheBridge] falha ao enviar mensagem de morte pro Discord: ${erro}`);
    }
}

async function enviarTransicaoParaDiscord(caminho, jogador) {
    try {
        await chamarBridge(caminho, { jogador });
    } catch (erro) {
        console.warn(`[SonheBridge] falha ao avisar ${caminho}: ${erro}`);
    }
}

// !vincular — gera o código automático de vinculação com o Discord.
async function solicitarVinculo(jogador) {
    try {
        const moedas = obterMoedas(jogador);
        const resposta = await chamarBridge("/minecraft-vincular-solicitar", {
            jogador: jogador.name,
            moedas,
        });
        if (resposta.status !== 200) {
            jogador.sendMessage("§cNão consegui gerar seu código agora. Tenta de novo em alguns segundos.");
            return;
        }
        const dados = JSON.parse(resposta.body);
        jogador.sendMessage(
            `§bSeu código de vinculação: §f${dados.codigo}\n` +
                `§7Use §f/vincular ${dados.codigo}§7 no Discord (vale por 15 minutos).`
        );
    } catch (erro) {
        jogador.sendMessage("§cNão consegui falar com o Discord agora. Tenta de novo em alguns segundos.");
        console.warn(`[SonheBridge] falha ao solicitar vínculo: ${erro}`);
    }
}

// Lê o inventário + equipamento de um jogador ONLINE e responde pro bot.
async function responderPedidoInventario(pedido) {
    const jogador = world.getAllPlayers().find((p) => p.name === pedido.jogador);
    if (!jogador) {
        await chamarBridge("/minecraft-inventario-resposta", {
            id: pedido.id,
            erro: "jogador offline no momento",
        }).catch(() => {});
        return;
    }

    const itens = [];
    const inventario = jogador.getComponent("minecraft:inventory");
    const container = inventario?.container;
    if (container) {
        for (let slot = 0; slot < container.size; slot++) {
            const stack = container.getItem(slot);
            if (stack) itens.push({ secao: "Inventário", nome: formatarNomeItem(stack.typeId), quantidade: stack.amount });
        }
    }

    const equipavel = jogador.getComponent("minecraft:equippable");
    const slotsEquipados = [
        [EquipmentSlot.Head, "Capacete"],
        [EquipmentSlot.Chest, "Peitoral"],
        [EquipmentSlot.Legs, "Calça"],
        [EquipmentSlot.Feet, "Botas"],
        [EquipmentSlot.Offhand, "Mão secundária"],
    ];
    for (const [slot, rotulo] of slotsEquipados) {
        const stack = equipavel?.getEquipment(slot);
        if (stack) itens.push({ secao: "Equipado", nome: `${rotulo}: ${formatarNomeItem(stack.typeId)}`, quantidade: stack.amount });
    }

    await chamarBridge("/minecraft-inventario-resposta", { id: pedido.id, itens }).catch((erro) => {
        console.warn(`[SonheBridge] falha ao responder pedido de inventário: ${erro}`);
    });
}

async function buscarFilaDoDiscord() {
    try {
        const req = new HttpRequest(`${BRIDGE_URL}/discord-queue`);
        req.method = HttpRequestMethod.Get;
        req.headers = [new HttpHeader("Authorization", `Bearer ${BRIDGE_SECRET}`)];
        req.timeout = 5;
        const resposta = await http.request(req);
        if (resposta.status !== 200) return;

        const dados = JSON.parse(resposta.body);
        for (const item of dados.mensagens ?? []) {
            if (item.tipo === "inventario_request") {
                system.run(() => responderPedidoInventario(item));
            } else if (item.tipo === "definir_rank") {
                system.run(() => definirScorePorNome(OBJ_RANK, item.jogador, item.rank));
            } else if (item.tipo === "definir_tag") {
                system.run(() => definirScorePorNome(OBJ_TAG, item.jogador, item.tag));
            } else {
                world.sendMessage(`§9[Discord] §f${item.autor}§7: §f${item.mensagem}`);
            }
        }
    } catch (erro) {
        console.warn(`[SonheBridge] falha ao buscar mensagens do Discord: ${erro}`);
    }
}

// Minecraft -> Discord (chat) + comando !vincular
// Não reformata a mensagem normal aqui — isso já é trabalho do SonheChat_BP.
// Esse pack só observa e retransmite, exceto "!vincular", que é interceptado
// (nunca aparece no chat do jogo — ver também o filtro de "!" no SonheChat_BP).
world.beforeEvents.chatSend.subscribe((evento) => {
    // Log de diagnóstico: se isso não aparecer no console ao mandar uma
    // mensagem, o SonheChat_BP (que cancela o evento antes) está impedindo
    // esse handler de rodar — nesse caso a ordem dos packs no mundo precisa
    // trocar (SonheBridge_BP antes do SonheChat_BP).
    console.warn(`[SonheBridge] chatSend recebido de ${evento.sender.name}: "${evento.message}"`);

    const mensagem = evento.message.trim();
    if (mensagem.toLowerCase() === "!vincular") {
        evento.cancel = true;
        const jogador = evento.sender;
        system.run(() => solicitarVinculo(jogador));
        return;
    }

    const nomeJogador = evento.sender.name;
    const tag = obterTag(evento.sender);
    system.run(() => enviarParaDiscord(nomeJogador, mensagem, tag));
});

// Minecraft -> Discord (mortes)
world.afterEvents.entityDie.subscribe((evento) => {
    if (evento.deadEntity.typeId !== "minecraft:player") return; // só mortes de jogador interessam aqui
    const nomeVitima = evento.deadEntity.name ?? evento.deadEntity.nameTag ?? "Alguém";
    const causa = evento.damageSource?.cause;
    const quemMatou = evento.damageSource?.damagingEntity;
    system.run(() => enviarMorteParaDiscord(mensagemMorte(nomeVitima, causa, quemMatou)));
});

// Minecraft -> Discord (entrada/saída no mundo)
world.afterEvents.playerSpawn.subscribe((evento) => {
    if (!evento.initialSpawn) return;
    system.run(() => enviarTransicaoParaDiscord("/minecraft-entrou", evento.player.name));
});

world.afterEvents.playerLeave.subscribe((evento) => {
    system.run(() => enviarTransicaoParaDiscord("/minecraft-saiu", evento.playerName));
});

// Discord -> Minecraft
// O Bedrock Dedicated Server não aceita conexão de entrada, então só resta
// puxar (polling) em vez de esperar o Discord avisar.
system.runInterval(() => {
    if (world.getAllPlayers().length === 0) return; // ninguém pra ver, poupa requisição
    buscarFilaDoDiscord();
}, INTERVALO_POLLING_TICKS);

// Heartbeat — avisa o bridge que o mundo está de pé (mesmo vazio). O bot não
// consegue confiar num ping UDP externo (rede do host do bot pode bloquear/
// atrasar RakNet), então é o jogo que avisa "continuo vivo" por HTTP, canal
// já comprovadamente estável (mesmo usado pelo polling acima).
const INTERVALO_HEARTBEAT_TICKS = 400; // 400 ticks ≈ 20s

async function enviarHeartbeat() {
    try {
        await chamarBridge("/minecraft-heartbeat", { jogadores: world.getAllPlayers().map((p) => p.name) });
    } catch (erro) {
        console.warn(`[SonheBridge] falha ao enviar heartbeat: ${erro}`);
    }
}

system.run(enviarHeartbeat); // primeiro heartbeat assim que o pack carrega, sem esperar os 20s
system.runInterval(enviarHeartbeat, INTERVALO_HEARTBEAT_TICKS);
