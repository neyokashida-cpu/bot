// SONHE — preferências genéricas por jogador: um único JSON guardado numa
// dynamic property ("sonhe:prefs"), sem rede e sem banco externo. Outros
// módulos (menu.js) leem/gravam chaves individuais via obterPreferencia /
// definirPreferencia; dicaAtivada/alternarDica são açúcar pra chave
// "dicaAoAbrirMenu", o único toggle real deste arquivo.

const PROP_PREFS = "sonhe:prefs";
const CHAVE_DICA = "dicaAoAbrirMenu";

// Frases curtas pro rodapé/dica do menu. Tom "sonho/expedição", nada de
// emoji Unicode (fonte do Bedrock não renderiza a maioria).
export const DICAS = [
    "Use o Diário pra ver seus marcos no SONHE.",
    "Sua Casa é única — defina com cuidado.",
    "A névoa esconde passagens; nem tudo se revela de primeira.",
    "Moedas locais valem dentro do SONHE — confira seu Perfil.",
    "Cada sonhador segue seu próprio caminho na expedição.",
    "Volte ao menu quando quiser — ele guarda seu progresso.",
    "Explorar com calma rende mais do que correr sem rumo.",
    "Nem toda passagem se abre na primeira tentativa.",
];

// Lê a dynamic property e devolve sempre um objeto válido: jogador novo,
// propriedade vazia ou JSON corrompido caem no fallback {} em vez de
// propagar erro pra quem chamou.
function lerPrefs(jogador) {
    let bruto;
    try {
        bruto = jogador.getDynamicProperty(PROP_PREFS);
    } catch (erro) {
        console.warn(`[SonheMenu] falha ao ler ${PROP_PREFS} de ${jogador?.name}: ${erro}`);
        return {};
    }

    if (typeof bruto !== "string" || bruto.length === 0) return {};

    try {
        const dados = JSON.parse(bruto);
        return dados && typeof dados === "object" && !Array.isArray(dados) ? dados : {};
    } catch (erro) {
        console.warn(`[SonheMenu] JSON inválido em ${PROP_PREFS} de ${jogador?.name}, resetando: ${erro}`);
        return {};
    }
}

function salvarPrefs(jogador, prefs) {
    try {
        jogador.setDynamicProperty(PROP_PREFS, JSON.stringify(prefs));
    } catch (erro) {
        console.warn(`[SonheMenu] falha ao salvar ${PROP_PREFS} de ${jogador?.name}: ${erro}`);
    }
}

// Nunca lança: qualquer falha devolve "padrao" em vez de travar quem chamou.
export function obterPreferencia(jogador, chave, padrao) {
    try {
        const prefs = lerPrefs(jogador);
        return chave in prefs ? prefs[chave] : padrao;
    } catch (erro) {
        console.warn(`[SonheMenu] obterPreferencia("${chave}") falhou pra ${jogador?.name}: ${erro}`);
        return padrao;
    }
}

export function definirPreferencia(jogador, chave, valor) {
    try {
        const prefs = lerPrefs(jogador);
        prefs[chave] = valor;
        salvarPrefs(jogador, prefs);
    } catch (erro) {
        console.warn(`[SonheMenu] definirPreferencia("${chave}") falhou pra ${jogador?.name}: ${erro}`);
    }
}

// Açúcar sintático pra chave da dica do menu — padrão ligado.
export function dicaAtivada(jogador) {
    return obterPreferencia(jogador, CHAVE_DICA, true);
}

// Inverte o toggle e devolve o novo valor já salvo.
export function alternarDica(jogador) {
    const novoValor = !dicaAtivada(jogador);
    definirPreferencia(jogador, CHAVE_DICA, novoValor);
    return novoValor;
}

// Math.random() aqui é só pra sortear a frase de exibição — não é o
// orquestrador, é código real do jogo.
export function dicaAleatoria() {
    const indice = Math.floor(Math.random() * DICAS.length);
    return DICAS[indice];
}
