import { world, system, MolangVariableMap } from "@minecraft/server";
import { adicionarEntrada } from "./diario.js";

// SONHE — sistema de Home: apenas UMA casa por jogador, guardada como JSON
// numa única dynamic property (sem rede, sem banco externo, sem /tpa e sem
// homes entre jogadores). A flag separada existe só pra saber se essa é a
// primeira vez que o jogador define casa (pro registro no diário), sem
// depender de reler/interpretar o JSON da casa em si.

const PROP_CASA = "sonhe:casa";
const PROP_FLAG_JA_DEFINIU = "sonhe:casa_ja_definiu_antes";

// Lê a dynamic property e devolve sempre null ou um objeto válido —
// propriedade vazia, ausente ou JSON corrompido caem no fallback null em
// vez de propagar erro pra quem chamou.
function lerCasa(jogador) {
    let bruto;
    try {
        bruto = jogador.getDynamicProperty(PROP_CASA);
    } catch (erro) {
        console.warn(`[SonheMenu] falha ao ler ${PROP_CASA} de ${jogador?.name}: ${erro}`);
        return null;
    }

    if (typeof bruto !== "string" || bruto.length === 0) return null;

    try {
        const dados = JSON.parse(bruto);
        if (!dados || typeof dados !== "object") return null;
        const { x, y, z, dimensionId } = dados;
        if (typeof x !== "number" || typeof y !== "number" || typeof z !== "number" || typeof dimensionId !== "string") {
            return null;
        }
        return dados;
    } catch (erro) {
        console.warn(`[SonheMenu] JSON inválido em ${PROP_CASA} de ${jogador?.name}: ${erro}`);
        return null;
    }
}

// Salva {x, y, z, dimensionId} da posição atual do jogador. Se for a
// primeira vez que ele define casa, registra o marco no diário — a flag
// booleana garante que isso só aconteça uma vez, mesmo que a casa em si
// seja redefinida depois várias vezes.
export function definirCasa(jogador) {
    try {
        const local = jogador.location;
        const dados = {
            x: local.x,
            y: local.y,
            z: local.z,
            dimensionId: jogador.dimension.id,
        };
        jogador.setDynamicProperty(PROP_CASA, JSON.stringify(dados));

        let jaDefiniuAntes;
        try {
            jaDefiniuAntes = jogador.getDynamicProperty(PROP_FLAG_JA_DEFINIU);
        } catch (erro) {
            console.warn(`[SonheMenu] falha ao ler ${PROP_FLAG_JA_DEFINIU} de ${jogador?.name}: ${erro}`);
            jaDefiniuAntes = true; // por segurança, não registra diário de novo em caso de erro de leitura
        }

        if (jaDefiniuAntes !== true) {
            jogador.setDynamicProperty(PROP_FLAG_JA_DEFINIU, true);
            adicionarEntrada(jogador, "Defini minha primeira casa no SONHE.");
        }

        return true;
    } catch (erro) {
        console.warn(`[SonheMenu] definirCasa falhou pra ${jogador?.name}: ${erro}`);
        return false;
    }
}

// Teleporta o jogador pra casa salva. Pega a dimension aqui dentro da
// função (nunca no topo do arquivo) pra não derrubar o script no load.
export function irParaCasa(jogador) {
    try {
        const casa = lerCasa(jogador);
        if (!casa) return { sucesso: false, motivo: "sem_casa" };

        const dimensao = world.getDimension(casa.dimensionId);
        jogador.teleport({ x: casa.x, y: casa.y, z: casa.z }, { dimension: dimensao });
        return { sucesso: true };
    } catch (erro) {
        console.warn(`[SonheMenu] irParaCasa falhou pra ${jogador?.name}: ${erro}`);
        return { sucesso: false, motivo: "erro" };
    }
}

export function temCasaDefinida(jogador) {
    try {
        return lerCasa(jogador) !== null;
    } catch (erro) {
        console.warn(`[SonheMenu] temCasaDefinida falhou pra ${jogador?.name}: ${erro}`);
        return false;
    }
}

function aguardarTicks(ticks) {
    return new Promise((resolver) => {
        system.runTimeout(() => resolver(), ticks);
    });
}

// Canalização de 3s antes de voltar pra Home — contagem na actionbar + som,
// cancela se o jogador tomar dano nesse meio-tempo, e mostra partículas
// brancas no destino (só depois do teleporte de verdade, via irParaCasa —
// essa função não é modificada, só chamada no final). APIs confirmadas por
// pesquisa antes de usar: system.runTimeout/clearRun, world.afterEvents.
// entityHurt (propriedade hurtEntity), player.onScreenDisplay.setActionBar,
// player.playSound, Dimension.spawnParticle + MolangVariableMap.
export async function irParaCasaComEfeito(jogador) {
    const TICKS_POR_SEGUNDO = 20;
    const SEGUNDOS_CANALIZACAO = 3;
    let interrompido = false;

    const assinaturaDano = world.afterEvents.entityHurt.subscribe((evento) => {
        if (evento.hurtEntity === jogador) interrompido = true;
    });

    try {
        for (let segundosRestantes = SEGUNDOS_CANALIZACAO; segundosRestantes > 0; segundosRestantes--) {
            try {
                jogador.onScreenDisplay.setActionBar(`Voltando para casa em ${segundosRestantes}...`);
                jogador.playSound("entity.experience_orb.pickup");
            } catch (erroUi) {
                console.warn(`[SonheMenu] falha ao atualizar canalização de Home pra ${jogador?.name}: ${erroUi}`);
            }
            await aguardarTicks(TICKS_POR_SEGUNDO);
            if (interrompido) break;
        }

        if (interrompido) {
            try {
                jogador.onScreenDisplay.setActionBar("Canalização interrompida — você tomou dano.");
            } catch {
                // jogador pode ter desconectado — sem problema, só não mostra o aviso
            }
            return { sucesso: false, motivo: "interrompido" };
        }

        const resultado = irParaCasa(jogador);

        if (resultado && resultado.sucesso) {
            try {
                const cores = new MolangVariableMap();
                cores.setColorRGB("variable.color", { red: 1, green: 1, blue: 1 });
                jogador.dimension.spawnParticle("minecraft:colored_flame_particle", jogador.location, cores);
            } catch (erroParticula) {
                console.warn(`[SonheMenu] falha ao mostrar partícula de chegada em casa pra ${jogador?.name}: ${erroParticula}`);
            }
        }

        return resultado;
    } catch (erro) {
        console.warn(`[SonheMenu] irParaCasaComEfeito falhou pra ${jogador?.name}: ${erro}`);
        return { sucesso: false, motivo: "erro" };
    } finally {
        // Garante que o listener nunca fica pendurado, mesmo se algo acima
        // lançar (ex: jogador desconectou no meio da canalização).
        world.afterEvents.entityHurt.unsubscribe(assinaturaDano);
    }
}
