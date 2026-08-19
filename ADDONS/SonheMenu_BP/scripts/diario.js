import { world } from "@minecraft/server";

// SONHE — diário do jogador: registro cronológico de eventos, guardado
// como JSON numa única dynamic property por jogador (sem rede, sem banco
// externo). Outros módulos (menu.js) consomem via obterEntradas() e
// formatarEntrada() pra exibir; o timestamp cru (quando) só é convertido
// pra texto legível na hora de exibir, nunca antes de salvar.

const PROP_DIARIO = "sonhe:diario";
const PROP_FLAG_PRIMEIRA_ENTRADA = "sonhe:diario_entrada_registrada";
const MAX_ENTRADAS = 30;

// Lê a dynamic property e devolve sempre um array válido: jogador novo,
// propriedade vazia ou JSON corrompido caem no fallback [] em vez de
// propagar erro pra quem chamou.
function lerEntradas(jogador) {
    let bruto;
    try {
        bruto = jogador.getDynamicProperty(PROP_DIARIO);
    } catch (erro) {
        console.warn(`[SonheMenu] falha ao ler ${PROP_DIARIO} de ${jogador?.name}: ${erro}`);
        return [];
    }

    if (typeof bruto !== "string" || bruto.length === 0) return [];

    try {
        const dados = JSON.parse(bruto);
        return Array.isArray(dados) ? dados : [];
    } catch (erro) {
        console.warn(`[SonheMenu] JSON inválido em ${PROP_DIARIO} de ${jogador?.name}, resetando: ${erro}`);
        return [];
    }
}

function salvarEntradas(jogador, entradas) {
    try {
        jogador.setDynamicProperty(PROP_DIARIO, JSON.stringify(entradas));
    } catch (erro) {
        console.warn(`[SonheMenu] falha ao salvar ${PROP_DIARIO} de ${jogador?.name}: ${erro}`);
    }
}

// Acrescenta uma entrada nova e corta as mais antigas, mantendo só as
// últimas MAX_ENTRADAS. "quando" é sempre o timestamp numérico cru
// (Date.now()) — formatar isso é trabalho de formatarEntrada, não daqui.
export function adicionarEntrada(jogador, texto) {
    try {
        const entradas = lerEntradas(jogador);
        entradas.push({ texto: String(texto ?? ""), quando: Date.now() });
        const recortadas = entradas.length > MAX_ENTRADAS ? entradas.slice(-MAX_ENTRADAS) : entradas;
        salvarEntradas(jogador, recortadas);
    } catch (erro) {
        console.warn(`[SonheMenu] adicionarEntrada falhou pra ${jogador?.name}: ${erro}`);
    }
}

// Nunca retorna null/undefined — jogador sem histórico recebe array vazio.
export function obterEntradas(jogador) {
    try {
        return lerEntradas(jogador);
    } catch (erro) {
        console.warn(`[SonheMenu] obterEntradas falhou pra ${jogador?.name}: ${erro}`);
        return [];
    }
}

// Formata só na exibição, ex: "19/08/2026 14:32". Sem Intl aqui — nem
// todo runtime de script do Bedrock tem suporte confiável, então monta a
// string manualmente (abordagem simples e comprovada).
function formatarData(timestamp) {
    const data = new Date(timestamp);
    const dia = String(data.getDate()).padStart(2, "0");
    const mes = String(data.getMonth() + 1).padStart(2, "0");
    const ano = data.getFullYear();
    const hora = String(data.getHours()).padStart(2, "0");
    const minuto = String(data.getMinutes()).padStart(2, "0");
    return `${dia}/${mes}/${ano} ${hora}:${minuto}`;
}

export function formatarEntrada(entrada) {
    try {
        const quando = formatarData(entrada?.quando);
        const texto = entrada?.texto ?? "";
        return `${quando} — ${texto}`;
    } catch (erro) {
        console.warn(`[SonheMenu] formatarEntrada falhou: ${erro}`);
        return String(entrada?.texto ?? "");
    }
}

// Grava a entrada de "primeira chegada" só uma vez por jogador. A flag
// separada (em vez de checar entradas.length === 0) garante idempotência
// mesmo se o jogador apagar/zerar o diário depois.
function registrarChegadaSeNecessario(jogador) {
    try {
        const jaRegistrado = jogador.getDynamicProperty(PROP_FLAG_PRIMEIRA_ENTRADA);
        if (jaRegistrado === true) return;
        jogador.setDynamicProperty(PROP_FLAG_PRIMEIRA_ENTRADA, true);
        adicionarEntrada(jogador, "Cheguei ao SONHE pela primeira vez.");
    } catch (erro) {
        console.warn(`[SonheMenu] registrarChegadaSeNecessario falhou pra ${jogador?.name}: ${erro}`);
    }
}

// ── Auto-registro do listener (roda ao importar este módulo) ──────────
// Só subscribe() aqui no top-level — nada de world.getDimension() ou
// qualquer API "early execution" fora de callback, pra não derrubar o
// script inteiro no load.
world.afterEvents.playerSpawn.subscribe((evento) => {
    try {
        if (evento.initialSpawn) {
            registrarChegadaSeNecessario(evento.player);
        }
    } catch (erro) {
        console.warn(`[SonheMenu] erro no listener playerSpawn (diário): ${erro}`);
    }
});
