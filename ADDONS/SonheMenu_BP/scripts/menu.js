import { world } from "@minecraft/server";
import { ActionFormData } from "@minecraft/server-ui";
import { definirCasa, irParaCasaComEfeito, temCasaDefinida } from "./casa.js";
import { obterEstatisticas } from "./estatisticas.js";
import { obterConquistas, abrirConquistas } from "./conquistas.js";
import { obterEntradas, formatarEntrada } from "./diario.js";
import { dicaAtivada, alternarDica, dicaAleatoria } from "./configuracoes.js";
import { resumoInventario } from "./inventario_resumo.js";
import { abrirAuctionHouse } from "./auction.js";

// SONHE — núcleo do /menu.
// Casa/Status/Conquistas/Diário/Configurações/Inventário/Perfil/Auction
// House já usam dados reais (dynamic properties, scoreboard, e — só a AH —
// a Bridge HTTP pra mover Statz de verdade; ver AUCTION_HOUSE.md).
//
// Sem emoji Unicode normal no texto dos forms: a fonte do Bedrock não
// renderiza a maioria deles. O único glyph decorativo usado é o Minecoin
// nativo da fonte do jogo (), pra moedas.

const OBJ_TAG = "sonhe_tag";
const OBJ_MOEDAS = "sonhe_moedas";
// Marcador invisível (só códigos § de formatação, sem texto visível) que ativa a
// tela de grade custom (sonhe_forms.grid_screen, em SonheMenu_RP/ui/sonhe_grid.json)
// no lugar do form padrão. Só o menu principal usa — as outras telas do addon ficam
// na lista vertical de sempre.
const MARCADOR_GRADE = "§s§o§n§h§e§r";
const TAGS = ["", "Recém-chegado", "Explorador", "Investigador", "Guardião", "Veterano", "Lenda"];
const GLYPH_MOEDA = "";

// Ícones (SonheMenu_RP/textures/ui/sonhe/). "Minha Casa" já tem arte
// própria; todo botão sem textura definitiva usa o placeholder "404" até
// a arte real chegar.
const ICONE_CASA = "textures/ui/sonhe/casa";
const ICONE_PLACEHOLDER = "textures/ui/sonhe/placeholder";

function obterTag(jogador) {
    const objetivo = world.scoreboard.getObjective(OBJ_TAG);
    if (!objetivo) return "";
    try {
        const indice = objetivo.getScore(jogador) ?? 0;
        return TAGS[indice] ?? "";
    } catch {
        return ""; // jogador sem score definido ainda
    }
}

function obterMoedasLocais(jogador) {
    const objetivo = world.scoreboard.getObjective(OBJ_MOEDAS);
    if (!objetivo) return null;
    try {
        const valor = objetivo.getScore(jogador);
        return valor ?? null;
    } catch {
        return null; // jogador sem score definido ainda
    }
}

// Mesma abordagem manual de formatação de data usada em diario.js/
// conquistas.js — sem Intl, que não é garantido em todo runtime do Bedrock.
function formatarData(timestamp) {
    const data = new Date(timestamp);
    const dia = String(data.getDate()).padStart(2, "0");
    const mes = String(data.getMonth() + 1).padStart(2, "0");
    const ano = data.getFullYear();
    return `${dia}/${mes}/${ano}`;
}

function montarCabecalho(jogador) {
    const tag = obterTag(jogador);
    const moedas = obterMoedasLocais(jogador);
    const linhas = [`§5Ola, ${jogador.name}§r`];
    linhas.push(`§7${tag || "Sonhador"}§r`);
    linhas.push(moedas !== null ? `§7${GLYPH_MOEDA} ${moedas} (moedas locais)§r` : "§7Moedas locais indisponiveis§r");
    if (dicaAtivada(jogador)) {
        linhas.push("");
        linhas.push(`§8Dica: ${dicaAleatoria()}§r`);
    }
    return linhas.join("\n");
}

// Registro central de botões do menu principal. Pra adicionar um sistema
// futuro de verdade (ex: Auction House), basta trocar o "aoAbrir" do item
// correspondente por um handler real — o menu principal
// (abrirMenuPrincipal) não precisa ser tocado.
const PAGINAS = [
    { id: "casa", texto: "Minha Casa", icone: ICONE_CASA, aoAbrir: abrirCasa },
    { id: "perfil", texto: "Meu Perfil", icone: ICONE_PLACEHOLDER, aoAbrir: abrirPerfil },
    { id: "status", texto: "Status", icone: ICONE_PLACEHOLDER, aoAbrir: abrirStatus },
    { id: "auction", texto: "Auction House", icone: ICONE_PLACEHOLDER, aoAbrir: abrirAuctionHouse },
    { id: "inventario", texto: "Inventário", icone: ICONE_PLACEHOLDER, aoAbrir: abrirInventario },
    { id: "conquistas", texto: "Conquistas", icone: ICONE_PLACEHOLDER, aoAbrir: abrirConquistas },
    { id: "diario", texto: "Diário", icone: ICONE_PLACEHOLDER, aoAbrir: abrirDiario },
    { id: "config", texto: "Configurações", icone: ICONE_PLACEHOLDER, aoAbrir: abrirConfiguracoes },
];

async function abrirPerfil(jogador) {
    const tag = obterTag(jogador);
    const moedas = obterMoedasLocais(jogador);
    const conquistas = obterConquistas(jogador);
    const desbloqueadas = conquistas.filter((c) => c.desbloqueada).length;
    const entradasDiario = obterEntradas(jogador).length;
    const corpo = [
        `Nick: ${jogador.name}`,
        `Tag: ${tag || "- (sem tag ainda)"}`,
        moedas !== null ? `Moedas locais: ${GLYPH_MOEDA} ${moedas}` : "Moedas locais: indisponível",
        `Conquistas desbloqueadas: ${desbloqueadas}/${conquistas.length}`,
        `Entradas no diário: ${entradasDiario}`,
        "",
        "Data de vínculo e título: ainda não disponíveis por aqui.",
    ].join("\n");
    await abrirPaginaSecundaria(jogador, "Meu Perfil", corpo);
}

async function abrirStatus(jogador) {
    const stats = obterEstatisticas(jogador);
    const corpo = [
        `Blocos quebrados: ${stats.blocosQuebrados}`,
        `Mobs derrotados: ${stats.mobsDerrotados}`,
        `Mortes: ${stats.mortes}`,
        `Jogando desde: ${stats.primeiraEntrada !== null ? formatarData(stats.primeiraEntrada) : "-"}`,
    ].join("\n");
    await abrirPaginaSecundaria(jogador, "Status", corpo);
}

async function abrirDiario(jogador) {
    const entradas = obterEntradas(jogador);
    const corpo =
        entradas.length > 0
            ? entradas
                  .slice()
                  .reverse()
                  .map(formatarEntrada)
                  .join("\n\n")
            : "Ainda não há registros em seu diário.";
    await abrirPaginaSecundaria(jogador, "Meu Diário", corpo);
}

async function abrirInventario(jogador) {
    const resumo = resumoInventario(jogador);
    const linhasTop =
        resumo.topItens.length > 0
            ? resumo.topItens.map((item) => `${item.nome}: ${item.quantidade}`).join("\n")
            : "Nenhum item.";
    const corpo = [
        `Slots ocupados: ${resumo.slotsOcupados}`,
        `Slots vazios: ${resumo.slotsVazios}`,
        `Total de itens: ${resumo.totalItens}`,
        "",
        "Itens em maior quantidade:",
        linhasTop,
        "",
        "Seu inventário completo continua no botão de sempre.",
    ].join("\n");
    await abrirPaginaSecundaria(jogador, "Inventário", corpo);
}

// Tela de Casa tem botões próprios (não usa abrirPaginaSecundaria) porque
// precisa oferecer "Definir aqui" e, se já houver casa salva, "Ir para
// casa" — os índices dos botões mudam conforme esse estado.
async function abrirCasa(jogador) {
    const definida = temCasaDefinida(jogador);
    const corpo = definida
        ? "Sua casa está definida. Você pode ir até ela ou definir um novo local (substitui o anterior)."
        : 'Você ainda não definiu uma casa. Fique no local desejado e escolha "Definir casa aqui".';

    const form = new ActionFormData().title("§dMinha Casa§r").body(corpo);
    if (definida) form.button("Ir para casa", ICONE_PLACEHOLDER);
    form.button("Definir casa aqui", ICONE_PLACEHOLDER);
    form.button("Voltar", ICONE_PLACEHOLDER);
    form.button("Fechar", ICONE_PLACEHOLDER);

    const resposta = await mostrarForm(jogador, form, "Minha Casa");
    if (!resposta) return;

    let indice = resposta.selection;
    if (definida) {
        if (indice === 0) {
            const resultado = await irParaCasaComEfeito(jogador);
            if (!resultado.sucesso && resultado.motivo === "ja_em_canalizacao") {
                jogador.sendMessage("Você já está sendo levado para casa — aguarde.");
            } else if (!resultado.sucesso && resultado.motivo !== "interrompido") {
                jogador.sendMessage("Não consegui te levar até sua casa agora. Tenta de novo em alguns segundos.");
            }
            return;
        }
        indice -= 1; // realinha com os índices de "sem casa definida" abaixo
    }

    if (indice === 0) {
        const ok = definirCasa(jogador);
        jogador.sendMessage(ok ? "Casa definida aqui." : "Não consegui definir sua casa agora.");
        return;
    }
    if (indice === 1) {
        await abrirMenuPrincipal(jogador);
    }
    // indice === 2 ("Fechar") — só fecha, sem ação extra.
}

async function abrirConfiguracoes(jogador) {
    const ativada = dicaAtivada(jogador);
    const corpo = [
        `Dica ao abrir o menu: ${ativada ? "ativada" : "desativada"}.`,
        "",
        "Quando ativada, mostra uma frase curta cada vez que você abre o menu do SONHE.",
    ].join("\n");

    const form = new ActionFormData()
        .title("§dConfigurações§r")
        .body(corpo)
        .button(ativada ? "Desativar dica ao abrir o menu" : "Ativar dica ao abrir o menu", ICONE_PLACEHOLDER)
        .button("Voltar", ICONE_PLACEHOLDER)
        .button("Fechar", ICONE_PLACEHOLDER);

    const resposta = await mostrarForm(jogador, form, "Configurações");
    if (!resposta) return;

    if (resposta.selection === 0) {
        alternarDica(jogador);
        await abrirConfiguracoes(jogador); // reabre já mostrando o novo estado
        return;
    }
    if (resposta.selection === 1) {
        await abrirMenuPrincipal(jogador);
    }
}

// Helper pra formulários com botões dinâmicos (o número/ordem dos botões
// muda conforme o estado do jogador) — padroniza try/catch + o caso
// canceled/selection===undefined, e sempre avisa o jogador (best-effort)
// quando o form falha ao abrir. Retorna a resposta bruta, ou null se
// cancelado/fechado (silencioso) ou se falhou (já avisou o jogador).
async function mostrarForm(jogador, form, contexto) {
    let resposta;
    try {
        resposta = await form.show(jogador);
    } catch (erro) {
        console.warn(`[SonheMenu] falha ao abrir "${contexto}" pra ${jogador?.name}: ${erro}`);
        try {
            jogador.sendMessage("Não consegui abrir esse menu agora. Tenta de novo em alguns segundos.");
        } catch {
            // jogador pode ter desconectado — sem problema, só não mostra o aviso
        }
        return null;
    }
    if (resposta.canceled || resposta.selection === undefined) return null; // fechado pelo X, ou jogador saiu
    return resposta;
}

// Usada pelas páginas secundárias que só mostram texto (Perfil, Status,
// Diário, Inventário) — evita várias funções quase idênticas. "Voltar"
// reabre o menu principal; "Fechar" só deixa o form fechado (sem ação
// extra). A Auction House tem seu próprio fluxo em auction.js.
async function abrirPaginaSecundaria(jogador, titulo, corpo) {
    const form = new ActionFormData()
        .title(`§d${titulo}§r`)
        .body(corpo)
        .button("Voltar", ICONE_PLACEHOLDER)
        .button("Fechar", ICONE_PLACEHOLDER);

    const resposta = await mostrarForm(jogador, form, titulo);
    if (!resposta) return;
    if (resposta.selection === 0) {
        await abrirMenuPrincipal(jogador);
    }
}

export async function abrirMenuPrincipal(jogador) {
    const form = new ActionFormData().title(`${MARCADOR_GRADE}§dSONHE§r`).body(montarCabecalho(jogador));
    for (const pagina of PAGINAS) {
        if (pagina.icone) {
            form.button(pagina.texto, pagina.icone);
        } else {
            form.button(pagina.texto);
        }
    }
    form.button("Fechar", ICONE_PLACEHOLDER);

    const resposta = await mostrarForm(jogador, form, "Menu SONHE");
    if (!resposta) return;
    if (resposta.selection >= PAGINAS.length) return; // botão "Fechar"

    const pagina = PAGINAS[resposta.selection];
    if (pagina) {
        await pagina.aoAbrir(jogador);
    }
}
