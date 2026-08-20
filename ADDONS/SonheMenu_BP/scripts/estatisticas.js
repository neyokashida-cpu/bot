import { world, Player } from "@minecraft/server";
import { obterComPadrao, salvarDadosJogador } from "./dados_jogador.js";

// SONHE — estatísticas de jogo por jogador: blocos quebrados, mobs
// derrotados, mortes e primeira entrada no mundo. Tudo numa única dynamic
// property por jogador (sem rede, sem banco externo — só o que a Script
// API já oferece). Outros módulos (menu.js / diário) consomem só via
// obterEstatisticas() e registrarPrimeiraEntradaSeNecessario().
//
// Leitura/escrita passa por dados_jogador.js: um erro de leitura pontual
// (JSON corrompido, exceção) nunca é tratado como "jogador novo" — nesse
// caso a escrita aborta em vez de regravar um valor zerado por cima do
// dado real (ver seguroSalvar abaixo).

const PROP_STATS = "sonhe:stats";

function obterStatsZerado() {
    return { blocosQuebrados: 0, mobsDerrotados: 0, mortes: 0, primeiraEntrada: null };
}

function validarStats(dados) {
    if (!dados || typeof dados !== "object") return null;
    return {
        blocosQuebrados: Number(dados.blocosQuebrados) || 0,
        mobsDerrotados: Number(dados.mobsDerrotados) || 0,
        mortes: Number(dados.mortes) || 0,
        primeiraEntrada: typeof dados.primeiraEntrada === "number" ? dados.primeiraEntrada : null,
    };
}

// Lê, soma 1 num campo numérico e regrava — usado pelos três listeners.
function incrementarCampo(jogador, campo) {
    try {
        const { dados: stats, seguroSalvar } = obterComPadrao(jogador, PROP_STATS, validarStats, obterStatsZerado);
        if (!seguroSalvar) {
            console.warn(`[SonheMenu] pulando incremento de "${campo}" pra ${jogador?.name} — leitura anterior falhou, não regravo por cima.`);
            return;
        }
        stats[campo] = (stats[campo] || 0) + 1;
        salvarDadosJogador(jogador, PROP_STATS, stats);
    } catch (erro) {
        console.warn(`[SonheMenu] falha ao incrementar "${campo}" de ${jogador?.name}: ${erro}`);
    }
}

// Nunca retorna null — jogador sem histórico (ou leitura com erro) recebe
// o objeto zerado, só pra exibição; nunca é regravado como se fosse real.
export function obterEstatisticas(jogador) {
    try {
        const { dados } = obterComPadrao(jogador, PROP_STATS, validarStats, obterStatsZerado);
        return dados;
    } catch (erro) {
        console.warn(`[SonheMenu] obterEstatisticas falhou pra ${jogador?.name}: ${erro}`);
        return obterStatsZerado();
    }
}

// Idempotente: só grava (e só retorna true) na primeira vez que roda pra
// esse jogador. O diário usa o retorno pra saber se é a primeira entrada.
export function registrarPrimeiraEntradaSeNecessario(jogador) {
    try {
        const { dados: stats, seguroSalvar } = obterComPadrao(jogador, PROP_STATS, validarStats, obterStatsZerado);
        if (!seguroSalvar) {
            console.warn(`[SonheMenu] pulando registro de primeira entrada pra ${jogador?.name} — leitura anterior falhou.`);
            return false;
        }
        if (stats.primeiraEntrada !== null) return false;
        stats.primeiraEntrada = Date.now();
        salvarDadosJogador(jogador, PROP_STATS, stats);
        return true;
    } catch (erro) {
        console.warn(`[SonheMenu] registrarPrimeiraEntradaSeNecessario falhou pra ${jogador?.name}: ${erro}`);
        return false;
    }
}

// ── Auto-registro dos listeners (roda ao importar este módulo) ────────
// Só subscribe() aqui no top-level — nada de world.getDimension() ou
// qualquer API "early execution" fora de callback, pra não derrubar o
// script inteiro no load.

world.afterEvents.playerBreakBlock.subscribe((evento) => {
    try {
        incrementarCampo(evento.player, "blocosQuebrados");
    } catch (erro) {
        console.warn(`[SonheMenu] erro no listener playerBreakBlock: ${erro}`);
    }
});

world.afterEvents.entityDie.subscribe((evento) => {
    try {
        const vitima = evento.deadEntity;
        const quemMatou = evento.damageSource?.damagingEntity;
        if (vitima instanceof Player) {
            incrementarCampo(vitima, "mortes");
        } else if (quemMatou instanceof Player) {
            incrementarCampo(quemMatou, "mobsDerrotados");
        }
    } catch (erro) {
        console.warn(`[SonheMenu] erro no listener entityDie: ${erro}`);
    }
});

world.afterEvents.playerSpawn.subscribe((evento) => {
    try {
        if (evento.initialSpawn) {
            registrarPrimeiraEntradaSeNecessario(evento.player);
        }
    } catch (erro) {
        console.warn(`[SonheMenu] erro no listener playerSpawn: ${erro}`);
    }
});
