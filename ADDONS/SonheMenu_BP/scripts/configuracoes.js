import { obterComPadrao, salvarDadosJogador } from "./dados_jogador.js";

// SONHE — preferências genéricas por jogador: um único JSON guardado numa
// dynamic property ("sonhe:prefs"), sem rede e sem banco externo. Outros
// módulos (menu.js) leem/gravam chaves individuais via obterPreferencia /
// definirPreferencia; dicaAtivada/alternarDica são açúcar pra chave
// "dicaAoAbrirMenu", o único toggle real deste arquivo.
//
// Leitura/escrita passa por dados_jogador.js: um erro de leitura pontual
// nunca é tratado como "sem preferências salvas" — nesse caso
// definirPreferencia aborta em vez de regravar {} por cima do que já
// existia.

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

function validarPrefs(dados) {
    return dados && typeof dados === "object" && !Array.isArray(dados) ? dados : null;
}

// Nunca lança: qualquer falha devolve "padrao" em vez de travar quem chamou.
export function obterPreferencia(jogador, chave, padrao) {
    try {
        const { dados: prefs } = obterComPadrao(jogador, PROP_PREFS, validarPrefs, () => ({}));
        return chave in prefs ? prefs[chave] : padrao;
    } catch (erro) {
        console.warn(`[SonheMenu] obterPreferencia("${chave}") falhou pra ${jogador?.name}: ${erro}`);
        return padrao;
    }
}

export function definirPreferencia(jogador, chave, valor) {
    try {
        const { dados: prefs, seguroSalvar } = obterComPadrao(jogador, PROP_PREFS, validarPrefs, () => ({}));
        if (!seguroSalvar) {
            console.warn(`[SonheMenu] pulando gravação da preferência "${chave}" pra ${jogador?.name} — leitura anterior falhou, não regravo por cima.`);
            return;
        }
        prefs[chave] = valor;
        salvarDadosJogador(jogador, PROP_PREFS, prefs);
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
