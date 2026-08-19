// SONHE — resumo leve do inventário do jogador. Não recria a tela vanilla
// (ela já existe e funciona): só conta slots ocupados/vazios, total de
// itens e os tipos com maior quantidade. Usado pelo botão "Inventário" do
// menu principal (menu.js).

// Formata "minecraft:diamond_pickaxe" -> "Diamond Pickaxe".
function formatarNomeItem(typeId) {
    const semNamespace = typeId.replace("minecraft:", "");
    return semNamespace
        .split("_")
        .filter((parte) => parte.length > 0)
        .map((parte) => parte[0].toUpperCase() + parte.slice(1))
        .join(" ");
}

function obterResumoZerado() {
    return { slotsOcupados: 0, slotsVazios: 0, totalItens: 0, topItens: [] };
}

// Nunca lança: componente/container ausente ou falha ao ler um slot caem
// no fallback zerado (ou pulam o slot) em vez de travar quem chamou.
export function resumoInventario(jogador) {
    try {
        const inventario = jogador.getComponent("minecraft:inventory");
        const container = inventario?.container;
        if (!container) return obterResumoZerado();

        let slotsOcupados = 0;
        let slotsVazios = 0;
        let totalItens = 0;
        const quantidadesPorTipo = new Map();

        for (let slot = 0; slot < container.size; slot++) {
            let item;
            try {
                item = container.getItem(slot);
            } catch (erro) {
                console.warn(`[SonheMenu] falha ao ler slot ${slot} do inventário de ${jogador?.name}: ${erro}`);
                continue;
            }

            if (!item) {
                slotsVazios++;
                continue;
            }

            slotsOcupados++;
            totalItens += item.amount;
            const atual = quantidadesPorTipo.get(item.typeId) || 0;
            quantidadesPorTipo.set(item.typeId, atual + item.amount);
        }

        const topItens = [...quantidadesPorTipo.entries()]
            .sort((a, b) => b[1] - a[1])
            .slice(0, 5)
            .map(([typeId, quantidade]) => ({ nome: formatarNomeItem(typeId), quantidade }));

        return { slotsOcupados, slotsVazios, totalItens, topItens };
    } catch (erro) {
        console.warn(`[SonheMenu] resumoInventario falhou pra ${jogador?.name}: ${erro}`);
        return obterResumoZerado();
    }
}
