import { ActionFormData } from "@minecraft/server-ui";
import { obterEstatisticas } from "./estatisticas.js";
import { abrirMenuPrincipal } from "./menu.js";
import { obterComPadrao, salvarDadosJogador } from "./dados_jogador.js";

// SONHE — conquistas: lista fixa, calculada só a partir das estatísticas
// reais de estatisticas.js (nada inventado). O progresso desbloqueado é
// guardado como JSON numa única dynamic property por jogador (sem rede,
// sem banco externo), no formato { [id]: timestampDoDesbloqueio }.

const PROP_CONQUISTAS = "sonhe:conquistas";
const ICONE_PLACEHOLDER = "textures/ui/sonhe/placeholder";

// Critérios simples e diretos sobre os campos de obterEstatisticas():
// blocosQuebrados, mobsDerrotados, mortes, primeiraEntrada.
const CONQUISTAS = [
    {
        id: "chegou_ao_sonhe",
        titulo: "Chegou ao SONHE",
        descricao: "Entrou no mundo do SONHE pela primeira vez.",
        criterio: (stats) => stats.primeiraEntrada !== null,
    },
    {
        id: "primeiras_escavacoes",
        titulo: "Primeiras Escavações",
        descricao: "Quebrou 50 blocos.",
        criterio: (stats) => stats.blocosQuebrados >= 50,
    },
    {
        id: "minerador",
        titulo: "Minerador",
        descricao: "Quebrou 500 blocos.",
        criterio: (stats) => stats.blocosQuebrados >= 500,
    },
    {
        id: "cacador",
        titulo: "Caçador",
        descricao: "Derrotou 10 mobs.",
        criterio: (stats) => stats.mobsDerrotados >= 10,
    },
    {
        id: "predador",
        titulo: "Predador",
        descricao: "Derrotou 50 mobs.",
        criterio: (stats) => stats.mobsDerrotados >= 50,
    },
    {
        id: "sobrevivente",
        titulo: "Sobrevivente",
        descricao: "Quebrou 100 blocos sem nunca morrer.",
        criterio: (stats) => stats.mortes === 0 && stats.blocosQuebrados >= 100,
    },
];

function validarDesbloqueadas(dados) {
    return dados && typeof dados === "object" && !Array.isArray(dados) ? dados : null;
}

// Confere cada conquista contra as estatísticas atuais. Quando o critério
// passa e ainda não existe timestamp salvo, grava Date.now() nesse exato
// momento (idempotente — só grava uma vez, não regrava depois). Quando o
// critério não passa, a conquista vem sempre como desbloqueada:false, sem
// timestamp, mesmo que tenha sobrado algo salvo de um estado anterior.
//
// Se a leitura anterior deu erro (seguroSalvar=false), a lista ainda é
// calculada normalmente pra exibição — só a gravação de novos
// desbloqueios é pulada, pra nunca regravar um objeto vazio por cima do
// progresso real do jogador.
export function obterConquistas(jogador) {
    try {
        const stats = obterEstatisticas(jogador);
        const { dados: desbloqueadas, seguroSalvar } = obterComPadrao(jogador, PROP_CONQUISTAS, validarDesbloqueadas, () => ({}));
        let alterou = false;

        const resultado = CONQUISTAS.map((conquista) => {
            const passou = conquista.criterio(stats);
            if (!passou) {
                return { id: conquista.id, titulo: conquista.titulo, descricao: conquista.descricao, desbloqueada: false, desbloqueadaEm: null };
            }

            if (desbloqueadas[conquista.id] === undefined) {
                desbloqueadas[conquista.id] = Date.now();
                alterou = true;
            }

            return {
                id: conquista.id,
                titulo: conquista.titulo,
                descricao: conquista.descricao,
                desbloqueada: true,
                desbloqueadaEm: desbloqueadas[conquista.id],
            };
        });

        if (alterou) {
            if (seguroSalvar) {
                salvarDadosJogador(jogador, PROP_CONQUISTAS, desbloqueadas);
            } else {
                console.warn(`[SonheMenu] pulando gravação de conquistas pra ${jogador?.name} — leitura anterior falhou, não regravo por cima.`);
            }
        }
        return resultado;
    } catch (erro) {
        console.warn(`[SonheMenu] obterConquistas falhou pra ${jogador?.name}: ${erro}`);
        // fallback: mesma lista, tudo bloqueado, pra nunca travar o menu
        return CONQUISTAS.map((conquista) => ({
            id: conquista.id,
            titulo: conquista.titulo,
            descricao: conquista.descricao,
            desbloqueada: false,
            desbloqueadaEm: null,
        }));
    }
}

// Formata só na exibição, ex: "19/08/2026 14:32" (mesma abordagem manual
// do diario.js — sem Intl, que não é garantido em todo runtime do Bedrock).
function formatarData(timestamp) {
    const data = new Date(timestamp);
    const dia = String(data.getDate()).padStart(2, "0");
    const mes = String(data.getMonth() + 1).padStart(2, "0");
    const ano = data.getFullYear();
    const hora = String(data.getHours()).padStart(2, "0");
    const minuto = String(data.getMinutes()).padStart(2, "0");
    return `${dia}/${mes}/${ano} ${hora}:${minuto}`;
}

function montarCorpo(conquistas) {
    const linhas = conquistas.map((conquista) => {
        if (conquista.desbloqueada) {
            return `[Desbloqueada] ${conquista.titulo}\n${conquista.descricao}\nEm: ${formatarData(conquista.desbloqueadaEm)}`;
        }
        return `[Bloqueada] ${conquista.titulo}\n${conquista.descricao}`;
    });
    return linhas.join("\n\n");
}

// Tela de conquistas do jogador — mesmo padrão de página secundária do
// menu.js: botão "Voltar" reabre o menu principal, "Fechar" só fecha.
export async function abrirConquistas(jogador) {
    const conquistas = obterConquistas(jogador);

    const form = new ActionFormData()
        .title("Conquistas")
        .body(montarCorpo(conquistas))
        .button("Voltar", ICONE_PLACEHOLDER)
        .button("Fechar", ICONE_PLACEHOLDER);

    let resposta;
    try {
        resposta = await form.show(jogador);
    } catch (erro) {
        console.warn(`[SonheMenu] falha ao abrir Conquistas pra ${jogador?.name}: ${erro}`);
        try {
            jogador.sendMessage("Não consegui abrir esse menu agora. Tenta de novo em alguns segundos.");
        } catch {
            // jogador pode ter desconectado — sem problema, só não mostra o aviso
        }
        return;
    }

    if (resposta.canceled || resposta.selection === undefined) return; // fechado pelo X, ou jogador saiu
    if (resposta.selection === 0) {
        await abrirMenuPrincipal(jogador);
    }
}
