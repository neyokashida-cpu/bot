import { world, system } from "@minecraft/server";

// SONHE — boas-vindas + chat com Rank/Tag.
// Sem @minecraft/server-net: tudo roda local dentro do mundo, sem depender de internet.
// Rank/Tag agora vêm do cargo real do Discord (ver ADDONS/SonheBridge_BP) —
// setados automaticamente no /vincular e a cada level up. Sem SonheBridge_BP
// instalado, continuam settable manualmente via /scoreboard, como antes.

const MAX_JOGADORES = 25;

// indice -> texto exibido. indice 0 e sempre o padrao (sem vinculo confirmado).
const RANKS = ["§8Visitante", "§7Membro", "§9Staff", "§cAdmin", "§6Dono"];
const TAGS = ["", "§fRecém-chegado", "§aExplorador", "§bInvestigador", "§dGuardião", "§5Veterano", "§6Lenda"];

const OBJ_RANK = "sonhe_rank";
const OBJ_TAG = "sonhe_tag";

function garantirObjetivos() {
    if (!world.scoreboard.getObjective(OBJ_RANK)) {
        world.scoreboard.addObjective(OBJ_RANK, "Rank SONHE");
    }
    if (!world.scoreboard.getObjective(OBJ_TAG)) {
        world.scoreboard.addObjective(OBJ_TAG, "Tag SONHE");
    }
}
system.run(garantirObjetivos);

function obterScore(nomeObjetivo, jogador, padrao) {
    const objetivo = world.scoreboard.getObjective(nomeObjetivo);
    if (!objetivo) return padrao;
    try {
        const valor = objetivo.getScore(jogador);
        return valor ?? padrao;
    } catch {
        // jogador nunca teve score definido nesse objetivo
        return padrao;
    }
}

// Boas-vindas
world.afterEvents.playerSpawn.subscribe((evento) => {
    if (!evento.initialSpawn) return;
    const total = world.getAllPlayers().length;
    world.sendMessage(
        `§bSeja bem-vindo(a), ${evento.player.name}. Agora somos (${total}/${MAX_JOGADORES}) sonhadores.`
    );
});

// Chat com Rank + Tag
world.beforeEvents.chatSend.subscribe((evento) => {
    evento.cancel = true;

    const jogador = evento.sender;
    const mensagem = evento.message;

    // Mensagens começando com "!" são comandos (ex: "!vincular", tratado pelo
    // SonheBridge_BP) — nunca aparecem no chat normal, com ou sem esse pack.
    if (mensagem.trim().startsWith("!")) return;

    const rankIndex = obterScore(OBJ_RANK, jogador, 0);
    const tagIndex = obterScore(OBJ_TAG, jogador, 0);
    const rank = RANKS[rankIndex] ?? RANKS[0];
    const tag = TAGS[tagIndex] ?? TAGS[0];

    const prefixoTag = tag ? `§7[${tag}§7] ` : "";
    const linha = `${rank}§r ${prefixoTag}§f${jogador.name} §7› §f${mensagem}`;

    // Reenvia fora do beforeEvent — evita reentrancia/instabilidade.
    system.run(() => world.sendMessage(linha));
});
