import { world, Player } from "@minecraft/server";

// SONHE — estatísticas de jogo por jogador: blocos quebrados, mobs
// derrotados, mortes e primeira entrada no mundo. Tudo numa única dynamic
// property por jogador (sem rede, sem banco externo — só o que a Script
// API já oferece). Outros módulos (menu.js / diário) consomem só via
// obterEstatisticas() e registrarPrimeiraEntradaSeNecessario().

const PROP_STATS = "sonhe:stats";

function obterStatsZerado() {
    return { blocosQuebrados: 0, mobsDerrotados: 0, mortes: 0, primeiraEntrada: null };
}

// Lê a dynamic property e devolve sempre um objeto válido: jogador novo,
// propriedade ainda vazia ou JSON corrompido caem no fallback zerado em
// vez de propagar erro pra quem chamou.
function lerStats(jogador) {
    let bruto;
    try {
        bruto = jogador.getDynamicProperty(PROP_STATS);
    } catch (erro) {
        console.warn(`[SonheMenu] falha ao ler ${PROP_STATS} de ${jogador?.name}: ${erro}`);
        return obterStatsZerado();
    }

    if (typeof bruto !== "string" || bruto.length === 0) return obterStatsZerado();

    try {
        const dados = JSON.parse(bruto);
        return {
            blocosQuebrados: Number(dados?.blocosQuebrados) || 0,
            mobsDerrotados: Number(dados?.mobsDerrotados) || 0,
            mortes: Number(dados?.mortes) || 0,
            primeiraEntrada: typeof dados?.primeiraEntrada === "number" ? dados.primeiraEntrada : null,
        };
    } catch (erro) {
        console.warn(`[SonheMenu] JSON inválido em ${PROP_STATS} de ${jogador?.name}, resetando: ${erro}`);
        return obterStatsZerado();
    }
}

function salvarStats(jogador, stats) {
    try {
        jogador.setDynamicProperty(PROP_STATS, JSON.stringify(stats));
    } catch (erro) {
        console.warn(`[SonheMenu] falha ao salvar ${PROP_STATS} de ${jogador?.name}: ${erro}`);
    }
}

// Lê, soma 1 num campo numérico e regrava — usado pelos três listeners.
function incrementarCampo(jogador, campo) {
    try {
        const stats = lerStats(jogador);
        stats[campo] = (stats[campo] || 0) + 1;
        salvarStats(jogador, stats);
    } catch (erro) {
        console.warn(`[SonheMenu] falha ao incrementar "${campo}" de ${jogador?.name}: ${erro}`);
    }
}

// Nunca retorna null — jogador sem histórico recebe o objeto zerado.
export function obterEstatisticas(jogador) {
    try {
        return lerStats(jogador);
    } catch (erro) {
        console.warn(`[SonheMenu] obterEstatisticas falhou pra ${jogador?.name}: ${erro}`);
        return obterStatsZerado();
    }
}

// Idempotente: só grava (e só retorna true) na primeira vez que roda pra
// esse jogador. O diário usa o retorno pra saber se é a primeira entrada.
export function registrarPrimeiraEntradaSeNecessario(jogador) {
    try {
        const stats = lerStats(jogador);
        if (stats.primeiraEntrada !== null) return false;
        stats.primeiraEntrada = Date.now();
        salvarStats(jogador, stats);
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
