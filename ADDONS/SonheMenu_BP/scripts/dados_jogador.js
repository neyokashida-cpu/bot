// SONHE — leitura/escrita segura de dados de jogador em dynamic properties.
// Existe pra corrigir uma causa raiz real: antes, um erro de leitura (JSON
// corrompido, exceção pontual do getDynamicProperty) era indistinguível de
// "jogador novo" — e a função de escrita gravava o valor zerado de volta,
// apagando pra sempre um dado que só tinha ficado momentaneamente
// ilegível. Aqui os dois casos são sempre distinguidos:
//   "ausente" — propriedade vazia/undefined -> jogador novo, seguro salvar.
//   "erro"    — leitura ou parse falhou -> NUNCA salvar por cima, só logar
//               e devolver um valor padrão só pra exibição temporária.

const PREFIXO_LOG = "[SonheData]";

// -> { estado: "ausente" | "ok" | "erro", dados }
// "validar(dadosBrutos)" recebe o JSON já parseado e deve devolver os
// dados normalizados (ou lançar/retornar null/undefined se inválido).
export function lerDadosJogador(jogador, chave, validar) {
    let bruto;
    try {
        bruto = jogador.getDynamicProperty(chave);
    } catch (erro) {
        console.warn(`${PREFIXO_LOG} erro ao ler dados jogador=${jogador?.name} propriedade=${chave} motivo=${erro}`);
        return { estado: "erro", dados: null };
    }

    if (typeof bruto !== "string" || bruto.length === 0) {
        return { estado: "ausente", dados: null };
    }

    try {
        const dadosBrutos = JSON.parse(bruto);
        const validado = validar(dadosBrutos);
        if (validado === null || validado === undefined) {
            console.warn(`${PREFIXO_LOG} erro ao ler dados jogador=${jogador?.name} propriedade=${chave} motivo=validar() rejeitou`);
            return { estado: "erro", dados: null };
        }
        return { estado: "ok", dados: validado };
    } catch (erro) {
        console.warn(`${PREFIXO_LOG} erro ao ler dados jogador=${jogador?.name} propriedade=${chave} motivo=${erro}`);
        return { estado: "erro", dados: null };
    }
}

export function salvarDadosJogador(jogador, chave, dados) {
    try {
        jogador.setDynamicProperty(chave, JSON.stringify(dados));
        return true;
    } catch (erro) {
        console.warn(`${PREFIXO_LOG} falha ao salvar dados jogador=${jogador?.name} propriedade=${chave} motivo=${erro}`);
        return false;
    }
}

// Açúcar pro caso comum: pega o dado já com um padrão pronto pra exibir, e
// diz se é seguro chamar salvarDadosJogador com ele depois. Quem chama
// SEMPRE precisa checar "seguroSalvar" antes de gravar — se vier false
// (erro de leitura), a escrita deve abortar e só logar, nunca regravar o
// padrão por cima do dado real que talvez ainda esteja lá.
export function obterComPadrao(jogador, chave, validar, criarPadrao) {
    const { estado, dados } = lerDadosJogador(jogador, chave, validar);
    if (estado === "ok") return { dados, seguroSalvar: true };
    if (estado === "ausente") return { dados: criarPadrao(), seguroSalvar: true };
    return { dados: criarPadrao(), seguroSalvar: false }; // estado === "erro"
}
