import { world, system, ItemStack } from "@minecraft/server";
import * as mc from "@minecraft/server"; // acesso seguro a símbolos de API preview (ex: EnchantmentType) sem quebrar o import se não existirem
import { http, HttpRequestMethod, HttpHeader, HttpRequest } from "@minecraft/server-net";
import { ActionFormData, ModalFormData, MessageFormData } from "@minecraft/server-ui";
import { abrirMenuPrincipal } from "./menu.js";

// SONHE — Auction House.
// Duas responsabilidades separadas por design: o ITEM fica em escrow aqui
// no Minecraft (dynamic properties do MUNDO, não do jogador — o vendedor
// pode estar offline quando o item precisa ser devolvido/entregue). O
// DINHEIRO (Statz) vive no SQLite do bot Discord e só se move via chamada
// HTTP síncrona pra Bridge, mesmo padrão comprovado de
// /minecraft-vincular-solicitar (ADDONS/SonheBridge_BP/scripts/main.js):
// o Minecraft faz o POST e espera a resposta na mesma chamada antes de
// tocar em item ou inventário. Nunca cacheie preço/status pra reusar depois.

// ══════════════════════════════════════════════════════════
// EDITAR AQUI antes de instalar no servidor:
const BRIDGE_URL = "https://SEU-APP.up.railway.app"; // URL pública do bot no Railway (sem / no final)
const BRIDGE_SECRET = "COLE_AQUI_O_MESMO_VALOR_DA_VARIAVEL_BRIDGE_SECRET_DO_RAILWAY";
// ══════════════════════════════════════════════════════════

const ICONE_PLACEHOLDER = "textures/ui/sonhe/placeholder";
const ITENS_POR_PAGINA = 10;
const INTERVALO_EXPIRACAO_TICKS = 1200; // ~60s (20 ticks/s)

const PREFIXO_ITEM = "sonhe_ah_item_";
const CHAVE_INDICE = "sonhe_ah_index";
const PREFIXO_CORREIO = "sonhe_ah_correio_";

// ── Helper de rede (mesmo padrão duplicado do SonheBridge_BP — packs não
// compartilham módulo JS entre si) ──────────────────────────
async function chamarBridge(caminho, corpo) {
    const req = new HttpRequest(`${BRIDGE_URL}${caminho}`);
    req.method = HttpRequestMethod.Post;
    req.headers = [
        new HttpHeader("Content-Type", "application/json"),
        new HttpHeader("Authorization", `Bearer ${BRIDGE_SECRET}`),
    ];
    req.body = JSON.stringify(corpo);
    req.timeout = 5;
    return http.request(req); // resposta tem .status (number) e .body (string JSON)
}

// ── Utilitários ──────────────────────────────────────────────
// crypto não está disponível no runtime — id único combinando tempo + sorte,
// suficiente pra não colidir dentro do mesmo mundo.
function gerarId(prefixo) {
    return `${prefixo}${Date.now().toString(36)}_${Math.random().toString(36).slice(2, 10)}`;
}

// Mesma formatação usada em outros módulos do pack (ex: SonheBridge_BP) —
// "minecraft:diamond_sword" -> "Diamond Sword".
function formatarNomeItem(typeId) {
    return typeId
        .replace(/^minecraft:/, "")
        .split("_")
        .map((p) => p.charAt(0).toUpperCase() + p.slice(1))
        .join(" ");
}

function formatarTempoRestante(ms) {
    if (ms <= 0) return "expirado";
    const totalMinutos = Math.floor(ms / 60000);
    const dias = Math.floor(totalMinutos / (60 * 24));
    const horas = Math.floor((totalMinutos % (60 * 24)) / 60);
    const minutos = totalMinutos % 60;
    if (dias > 0) return `${dias}d ${horas}h`;
    if (horas > 0) return `${horas}h ${minutos}min`;
    return `${minutos}min`;
}

// ── Dynamic properties do MUNDO (a Script API não lista propriedades
// existentes, então o índice precisa ser mantido manualmente em sincronia) ──

function lerIndice() {
    try {
        const bruto = world.getDynamicProperty(CHAVE_INDICE);
        if (typeof bruto !== "string" || bruto.length === 0) return { ativos: [] };
        const dados = JSON.parse(bruto);
        return dados && Array.isArray(dados.ativos) ? dados : { ativos: [] };
    } catch (erro) {
        console.warn(`[SonheMenu] falha ao ler ${CHAVE_INDICE}: ${erro}`);
        return { ativos: [] };
    }
}

function salvarIndice(indice) {
    try {
        world.setDynamicProperty(CHAVE_INDICE, JSON.stringify(indice));
    } catch (erro) {
        console.warn(`[SonheMenu] falha ao salvar ${CHAVE_INDICE}: ${erro}`);
    }
}

function removerDoIndice(listingId) {
    const indice = lerIndice();
    indice.ativos = indice.ativos.filter((id) => id !== listingId);
    salvarIndice(indice);
}

function lerItemEscrow(listingId) {
    try {
        const bruto = world.getDynamicProperty(`${PREFIXO_ITEM}${listingId}`);
        if (typeof bruto !== "string" || bruto.length === 0) return null;
        return JSON.parse(bruto);
    } catch (erro) {
        console.warn(`[SonheMenu] falha ao ler anúncio ${listingId}: ${erro}`);
        return null;
    }
}

function salvarItemEscrow(listingId, dados) {
    try {
        world.setDynamicProperty(`${PREFIXO_ITEM}${listingId}`, JSON.stringify(dados));
    } catch (erro) {
        console.warn(`[SonheMenu] falha ao salvar anúncio ${listingId}: ${erro}`);
    }
}

function removerItemEscrow(listingId) {
    try {
        world.setDynamicProperty(`${PREFIXO_ITEM}${listingId}`, undefined);
    } catch (erro) {
        console.warn(`[SonheMenu] falha ao remover anúncio ${listingId}: ${erro}`);
    }
}

function lerCorreio(nomeJogador) {
    try {
        const bruto = world.getDynamicProperty(`${PREFIXO_CORREIO}${nomeJogador}`);
        if (typeof bruto !== "string" || bruto.length === 0) return { pendentes: [] };
        const dados = JSON.parse(bruto);
        return dados && Array.isArray(dados.pendentes) ? dados : { pendentes: [] };
    } catch (erro) {
        console.warn(`[SonheMenu] falha ao ler correio de ${nomeJogador}: ${erro}`);
        return { pendentes: [] };
    }
}

function salvarCorreio(nomeJogador, dados) {
    try {
        world.setDynamicProperty(`${PREFIXO_CORREIO}${nomeJogador}`, JSON.stringify(dados));
    } catch (erro) {
        console.warn(`[SonheMenu] falha ao salvar correio de ${nomeJogador}: ${erro}`);
    }
}

function adicionarAoCorreio(nomeJogador, origem, itemSerializado) {
    const correio = lerCorreio(nomeJogador);
    correio.pendentes.push({ origem, item: itemSerializado });
    salvarCorreio(nomeJogador, correio);
}

// ── Serialização de item (escrow guarda só dados simples, nunca o ItemStack
// em si) ───────────────────────────────────────────────────
function serializarItem(item) {
    let encantamentos = [];
    try {
        const comp = item.getComponent("minecraft:enchantable");
        if (comp) {
            encantamentos = comp.getEnchantments().map((e) => ({ tipo: e.type.id, nivel: e.level }));
        }
    } catch (erro) {
        console.warn(`[SonheMenu] falha ao ler encantamentos do item anunciado: ${erro}`);
    }

    let durabilidade = null;
    try {
        const comp = item.getComponent("minecraft:durability");
        if (comp) durabilidade = { dano: comp.damage, maxDurabilidade: comp.maxDurability };
    } catch (erro) {
        console.warn(`[SonheMenu] falha ao ler durabilidade do item anunciado: ${erro}`);
    }

    let lore = [];
    try {
        lore = item.getLore() ?? [];
    } catch (erro) {
        console.warn(`[SonheMenu] falha ao ler lore do item anunciado: ${erro}`);
    }

    return {
        typeId: item.typeId,
        amount: item.amount,
        nameTag: item.nameTag ?? null,
        lore,
        encantamentos,
        durabilidade,
    };
}

// Reconstrói um ItemStack a partir dos dados salvos no escrow/correio. Cada
// componente é reaplicado isoladamente (try/catch próprio) — a falta de um
// não deve impedir os outros nem travar a entrega do item. Retorna também
// "avisos" (ex: "encantamentos") pra quem chamar poder contar pro jogador
// que algo não foi restaurado — nunca falha silenciosamente num item pago.
function reconstituirItemStack(dadosItem) {
    const itemStack = new ItemStack(dadosItem.typeId, dadosItem.amount);
    const avisos = [];

    try {
        if (dadosItem.nameTag) itemStack.nameTag = dadosItem.nameTag;
    } catch (erro) {
        console.warn(`[SonheMenu] falha ao reaplicar nome do item: ${erro}`);
    }

    try {
        if (dadosItem.lore && dadosItem.lore.length > 0) itemStack.setLore(dadosItem.lore);
    } catch (erro) {
        console.warn(`[SonheMenu] falha ao reaplicar lore do item: ${erro}`);
    }

    try {
        if (dadosItem.encantamentos && dadosItem.encantamentos.length > 0) {
            const comp = itemStack.getComponent("minecraft:enchantable");
            const TipoEncantamento = mc.EnchantmentType; // acesso seguro — vira undefined se a API não existir nesta versão
            if (comp && TipoEncantamento) {
                for (const ench of dadosItem.encantamentos) {
                    try {
                        comp.addEnchantment({ type: new TipoEncantamento(ench.tipo), level: ench.nivel });
                    } catch (erroEnch) {
                        console.warn(`[SonheMenu] falha ao reaplicar encantamento ${ench.tipo}: ${erroEnch}`);
                        avisos.push("encantamentos");
                    }
                }
            } else {
                console.warn("[SonheMenu] API de encantamentos indisponível nesta versão — item entregue sem os encantamentos originais.");
                avisos.push("encantamentos");
            }
        }
    } catch (erro) {
        console.warn(`[SonheMenu] falha ao reaplicar encantamentos do item: ${erro}`);
        avisos.push("encantamentos");
    }

    try {
        if (dadosItem.durabilidade) {
            const comp = itemStack.getComponent("minecraft:durability");
            if (comp) comp.damage = dadosItem.durabilidade.dano;
        }
    } catch (erro) {
        console.warn(`[SonheMenu] falha ao reaplicar durabilidade do item: ${erro}`);
    }

    return { itemStack, avisos: [...new Set(avisos)] };
}

function mensagemAvisos(avisos) {
    if (!avisos || avisos.length === 0) return null;
    if (avisos.includes("encantamentos")) {
        return "Atenção: não consegui restaurar os encantamentos originais desse item — avise um administrador.";
    }
    return null;
}

// Tenta entregar direto no inventário (se o jogador estiver online e couber);
// qualquer falha (offline, sem espaço nenhum) cai no correio inteiro. Se só
// parte do stack couber, container.addItem NÃO lança erro — devolve o
// restante que não coube (undefined = coube tudo). Ignorar esse retorno
// faria o item sobrando simplesmente desaparecer depois do jogador já ter
// pago por ele, então o que sobra vai pro correio serializado de novo a
// partir do que de fato ficou de fora (nunca o item inteiro original).
function entregarOuGuardarNoCorreio(nomeJogadorAlvo, itemStack, itemSerializado, origem) {
    try {
        const jogadorOnline = world.getAllPlayers().find((p) => p.name === nomeJogadorAlvo);
        const container = jogadorOnline?.getComponent("minecraft:inventory")?.container;
        if (container) {
            const sobrou = container.addItem(itemStack);
            if (sobrou === undefined) return; // coube tudo
            // coube só parte — guarda no correio exatamente o que ficou de fora, não o
            // item inteiro original (senão o jogador recebe em dobro a parte que já coube).
            adicionarAoCorreio(nomeJogadorAlvo, origem, serializarItem(sobrou));
            return;
        }
    } catch (erro) {
        console.warn(`[SonheMenu] item não coube direto pra ${nomeJogadorAlvo}, vai pro correio: ${erro}`);
    }
    // offline, sem container, ou erro inesperado antes de tentar addItem — guarda o item inteiro original
    adicionarAoCorreio(nomeJogadorAlvo, origem, itemSerializado);
}

// ── Menu principal da Auction House ──────────────────────────
export async function abrirAuctionHouse(jogador) {
    const form = new ActionFormData()
        .title("Auction House")
        .body("Compre e venda itens com outros jogadores do SONHE.")
        .button("Ver anúncios", ICONE_PLACEHOLDER)
        .button("Anunciar item", ICONE_PLACEHOLDER)
        .button("Minhas vendas", ICONE_PLACEHOLDER)
        .button("Voltar", ICONE_PLACEHOLDER);

    let resposta;
    try {
        resposta = await form.show(jogador);
    } catch (erro) {
        console.warn(`[SonheMenu] falha ao abrir Auction House pra ${jogador?.name}: ${erro}`);
        return;
    }
    if (resposta.canceled || resposta.selection === undefined) return;

    if (resposta.selection === 0) {
        await abrirVerAnuncios(jogador, 0);
    } else if (resposta.selection === 1) {
        await abrirAnunciarItem(jogador);
    } else if (resposta.selection === 2) {
        await abrirMinhasVendas(jogador);
    } else {
        await abrirMenuPrincipal(jogador);
    }
}

// ── Ver anúncios (comprar) ───────────────────────────────────
async function abrirVerAnuncios(jogador, pagina) {
    const indice = lerIndice();
    const agora = Date.now();
    const anuncios = [];
    for (const listingId of indice.ativos) {
        try {
            const dados = lerItemEscrow(listingId);
            if (!dados) continue;
            if (dados.expiraEm < agora) continue; // expiração real roda na rotina separada, aqui só não mostra
            anuncios.push(dados);
        } catch (erro) {
            console.warn(`[SonheMenu] falha ao ler anúncio ${listingId} na listagem: ${erro}`);
        }
    }

    if (anuncios.length === 0) {
        const form = new ActionFormData()
            .title("Ver anúncios")
            .body("Não há nenhum anúncio ativo no momento.")
            .button("Voltar", ICONE_PLACEHOLDER);
        try {
            const resposta = await form.show(jogador);
            if (!resposta.canceled && resposta.selection === 0) await abrirAuctionHouse(jogador);
        } catch (erro) {
            console.warn(`[SonheMenu] falha ao abrir Ver anúncios (vazio) pra ${jogador?.name}: ${erro}`);
        }
        return;
    }

    const totalPaginas = Math.ceil(anuncios.length / ITENS_POR_PAGINA);
    const paginaAtual = Math.min(Math.max(pagina, 0), totalPaginas - 1);
    const inicio = paginaAtual * ITENS_POR_PAGINA;
    const itensPagina = anuncios.slice(inicio, inicio + ITENS_POR_PAGINA);

    const form = new ActionFormData()
        .title(`Ver anúncios (${paginaAtual + 1}/${totalPaginas})`)
        .body("Escolha um anúncio pra ver os detalhes.");

    for (const dados of itensPagina) {
        const nome = dados.item.nameTag || formatarNomeItem(dados.item.typeId);
        const restante = formatarTempoRestante(dados.expiraEm - agora);
        form.button(`${nome}\n${dados.preco} moedas - ${dados.vendedorNomeMinecraft} (${restante})`, ICONE_PLACEHOLDER);
    }

    const temAnterior = paginaAtual > 0;
    const temProxima = paginaAtual < totalPaginas - 1;
    if (temAnterior) form.button("Página anterior", ICONE_PLACEHOLDER);
    if (temProxima) form.button("Próxima página", ICONE_PLACEHOLDER);
    form.button("Voltar", ICONE_PLACEHOLDER);

    let resposta;
    try {
        resposta = await form.show(jogador);
    } catch (erro) {
        console.warn(`[SonheMenu] falha ao abrir Ver anúncios pra ${jogador?.name}: ${erro}`);
        return;
    }
    if (resposta.canceled || resposta.selection === undefined) return;

    let indiceBotao = resposta.selection;
    if (indiceBotao < itensPagina.length) {
        await abrirDetalheAnuncio(jogador, itensPagina[indiceBotao].listingId, paginaAtual);
        return;
    }
    indiceBotao -= itensPagina.length;

    if (temAnterior) {
        if (indiceBotao === 0) {
            await abrirVerAnuncios(jogador, paginaAtual - 1);
            return;
        }
        indiceBotao -= 1;
    }
    if (temProxima) {
        if (indiceBotao === 0) {
            await abrirVerAnuncios(jogador, paginaAtual + 1);
            return;
        }
        indiceBotao -= 1;
    }
    // sobrou só o botão "Voltar"
    await abrirAuctionHouse(jogador);
}

async function abrirDetalheAnuncio(jogador, listingId, paginaOrigem) {
    const dados = lerItemEscrow(listingId);
    if (!dados) {
        jogador.sendMessage("Esse anúncio não está mais disponível.");
        await abrirVerAnuncios(jogador, paginaOrigem);
        return;
    }

    const nome = dados.item.nameTag || formatarNomeItem(dados.item.typeId);
    const linhas = [
        `Item: ${nome}`,
        `Quantidade: ${dados.item.amount}`,
        `Preço: ${dados.preco} moedas`,
        `Vendedor: ${dados.vendedorNomeMinecraft}`,
    ];
    if (dados.item.durabilidade) {
        const restante = dados.item.durabilidade.maxDurabilidade - dados.item.durabilidade.dano;
        linhas.push(`Durabilidade: ${restante}/${dados.item.durabilidade.maxDurabilidade}`);
    }
    if (dados.item.encantamentos && dados.item.encantamentos.length > 0) {
        linhas.push("Encantamentos:");
        for (const ench of dados.item.encantamentos) linhas.push(`- ${ench.tipo} ${ench.nivel}`);
    }

    const form = new MessageFormData().title("Detalhe do anúncio").body(linhas.join("\n")).button1("Comprar").button2("Voltar");

    let resposta;
    try {
        resposta = await form.show(jogador);
    } catch (erro) {
        console.warn(`[SonheMenu] falha ao abrir detalhe do anúncio ${listingId}: ${erro}`);
        return;
    }
    if (resposta.canceled || resposta.selection === undefined) return;

    if (resposta.selection === 0) {
        await confirmarCompra(jogador, listingId, paginaOrigem);
    } else {
        await abrirVerAnuncios(jogador, paginaOrigem);
    }
}

async function confirmarCompra(jogador, listingId, paginaOrigem) {
    const dados = lerItemEscrow(listingId);
    if (!dados) {
        jogador.sendMessage("Esse anúncio não está mais disponível.");
        await abrirVerAnuncios(jogador, paginaOrigem);
        return;
    }
    if (dados.vendedorNomeMinecraft === jogador.name) {
        jogador.sendMessage("Você não pode comprar seu próprio anúncio.");
        await abrirVerAnuncios(jogador, paginaOrigem);
        return;
    }

    // transactionId é gerado UMA vez e reusado em todas as tentativas desta
    // mesma compra (ver retry abaixo) — é a chave de idempotência no banco
    // (confirmar_compra_ah). Se gerássemos um novo a cada tentativa, uma
    // resposta perdida DEPOIS do commit no lado do bot faria o retry
    // debitar o comprador de novo (exatamente o risco documentado em
    // AUCTION_HOUSE.md, "Fluxo de compra").
    const transactionId = gerarId("ah_tx_");
    let resposta;
    const MAX_TENTATIVAS = 3;
    for (let tentativa = 1; tentativa <= MAX_TENTATIVAS; tentativa++) {
        try {
            resposta = await chamarBridge("/ah/comprar-confirmar", {
                transactionId,
                listingId,
                compradorNome: jogador.name,
            });
            break; // recebeu alguma resposta HTTP — não precisa retentar
        } catch (erro) {
            console.warn(`[SonheMenu] falha de rede ao confirmar compra ${listingId} (tentativa ${tentativa}): ${erro}`);
            if (tentativa === MAX_TENTATIVAS) {
                jogador.sendMessage("Não consegui confirmar a compra agora. Tenta de novo em alguns segundos.");
                return;
            }
        }
    }

    let corpo;
    try {
        corpo = JSON.parse(resposta.body);
    } catch (erro) {
        console.warn(`[SonheMenu] resposta inválida da Bridge na compra ${listingId}: ${erro}`);
        jogador.sendMessage("Não consegui confirmar a compra agora. Tenta de novo em alguns segundos.");
        return;
    }

    if (resposta.status !== 200 || corpo.status !== "ok") {
        const mensagens = {
            anuncio_indisponivel: "Esse anúncio não está mais disponível.",
            ja_vendido: "Esse item já foi vendido pra outra pessoa.",
            comprador_sem_vinculo: "Você precisa vincular sua conta do Discord antes de comprar (use !vincular).",
            saldo_insuficiente: "Você não tem moedas suficientes pra essa compra.",
        };
        jogador.sendMessage(mensagens[corpo.status] ?? "Não foi possível concluir a compra agora.");
        await abrirVerAnuncios(jogador, paginaOrigem);
        return;
    }

    // Bridge confirmou o pagamento — só agora o item sai do escrow.
    removerItemEscrow(listingId);
    removerDoIndice(listingId);

    let aviso = null;
    try {
        const { itemStack, avisos } = reconstituirItemStack(dados.item);
        entregarOuGuardarNoCorreio(jogador.name, itemStack, dados.item, "compra");
        aviso = mensagemAvisos(avisos);
    } catch (erro) {
        console.warn(`[SonheMenu] falha ao reconstituir item comprado ${listingId}: ${erro}`);
        adicionarAoCorreio(jogador.name, "compra", dados.item);
    }

    jogador.sendMessage(`Compra confirmada! Você pagou ${corpo.preco ?? dados.preco} moedas pra ${corpo.vendedorNome ?? dados.vendedorNomeMinecraft}.`);
    if (aviso) jogador.sendMessage(aviso);
}

// ── Anunciar item ─────────────────────────────────────────────
// Assinatura simples (typeId/amount/nameTag) pra comparar "é o mesmo item?"
// depois de um formulário assíncrono ficar aberto (o jogador pode ter
// trocado o slot selecionado ou o conteúdo dele nesse meio-tempo).
function assinaturaItem(item) {
    if (!item) return null;
    return { typeId: item.typeId, amount: item.amount, nameTag: item.nameTag ?? null };
}

function assinaturasIguais(a, b) {
    return !!a && !!b && a.typeId === b.typeId && a.amount === b.amount && a.nameTag === b.nameTag;
}

async function abrirAnunciarItem(jogador) {
    let item;
    try {
        const container = jogador.getComponent("minecraft:inventory")?.container;
        item = container?.getItem(jogador.selectedSlotIndex);
    } catch (erro) {
        console.warn(`[SonheMenu] falha ao ler item da mão de ${jogador?.name}: ${erro}`);
    }

    if (!item) {
        jogador.sendMessage("Segure o item que quer anunciar na mão.");
        return;
    }

    const slot = jogador.selectedSlotIndex;
    const assinaturaOriginal = assinaturaItem(item);

    const form = new ModalFormData()
        .title("Anunciar item")
        .textField("Preço (em moedas, número inteiro)", "Ex: 5000")
        .dropdown("Duração do anúncio", ["24 horas", "48 horas", "72 horas"], { defaultValueIndex: 0 });

    let resposta;
    try {
        resposta = await form.show(jogador);
    } catch (erro) {
        console.warn(`[SonheMenu] falha ao abrir formulário de anúncio pra ${jogador?.name}: ${erro}`);
        return;
    }
    if (resposta.canceled || !resposta.formValues) return;

    const [precoTexto, indiceDuracao] = resposta.formValues;
    const preco = Number(precoTexto);
    if (!Number.isInteger(preco) || preco <= 0) {
        jogador.sendMessage("Preço inválido — use um número inteiro maior que zero.");
        return;
    }

    const horasPorIndice = [24, 48, 72];
    const horas = horasPorIndice[indiceDuracao] ?? 24;
    const expiraEm = Date.now() + horas * 60 * 60 * 1000;

    // O formulário fica aberto por tempo arbitrário (o jogador digitando) —
    // revalida AQUI, antes de sequer chamar a Bridge, que o item continua
    // sendo o mesmo. Fecha a principal janela de duplicação/inconsistência
    // apontada na revisão (a menor janela entre isto e a remoção real do
    // item é coberta de novo dentro de confirmarAnuncio).
    let itemAtual;
    try {
        const container = jogador.getComponent("minecraft:inventory")?.container;
        itemAtual = container?.getItem(slot);
    } catch (erro) {
        console.warn(`[SonheMenu] falha ao revalidar item da mão de ${jogador?.name}: ${erro}`);
    }
    if (!assinaturasIguais(assinaturaItem(itemAtual), assinaturaOriginal)) {
        jogador.sendMessage("O item na sua mão mudou enquanto você definia o preço. Tenta anunciar de novo.");
        return;
    }

    await confirmarAnuncio(jogador, slot, assinaturaOriginal, preco, expiraEm);
}

async function confirmarAnuncio(jogador, slot, assinaturaOriginal, preco, expiraEm) {
    const listingId = gerarId("ah_");

    let resposta;
    try {
        resposta = await chamarBridge("/ah/anuncio-criar", {
            listingId,
            vendedorNome: jogador.name,
            preco,
            expiraEm,
        });
    } catch (erro) {
        console.warn(`[SonheMenu] falha de rede ao criar anúncio ${listingId}: ${erro}`);
        jogador.sendMessage("Não consegui criar o anúncio agora. Tenta de novo em alguns segundos.");
        return;
    }

    let corpo;
    try {
        corpo = JSON.parse(resposta.body);
    } catch (erro) {
        console.warn(`[SonheMenu] resposta inválida da Bridge ao criar anúncio ${listingId}: ${erro}`);
        jogador.sendMessage("Não consegui criar o anúncio agora. Tenta de novo em alguns segundos.");
        return;
    }

    if (resposta.status !== 200 || corpo.status !== "ok") {
        // Bridge não confirmou — o item NUNCA é tocado no inventário do jogador.
        const mensagens = {
            sem_vinculo: "Você precisa vincular sua conta do Discord antes de anunciar (use !vincular).",
        };
        jogador.sendMessage(mensagens[corpo.status] ?? "Não foi possível criar o anúncio agora.");
        return;
    }

    // Revalida de novo aqui — fecha a pequena janela entre a chamada HTTP
    // (que pode demorar) e a remoção real do item. Se o item mudou, a Bridge
    // já criou a linha do anúncio (sem dinheiro envolvido nesse passo) —
    // cancela ela de volta pra não deixar um anúncio "fantasma" sem escrow.
    let itemFinal;
    try {
        const container = jogador.getComponent("minecraft:inventory")?.container;
        itemFinal = container?.getItem(slot);
    } catch (erro) {
        console.warn(`[SonheMenu] falha ao revalidar item antes de remover (anúncio ${listingId}): ${erro}`);
    }
    if (!assinaturasIguais(assinaturaItem(itemFinal), assinaturaOriginal)) {
        console.warn(`[SonheMenu] item mudou entre criar e remover pro anúncio ${listingId} — cancelando anúncio órfão.`);
        try {
            await chamarBridge("/ah/anuncio-cancelar", { listingId, vendedorNome: jogador.name });
        } catch (erroCancelar) {
            console.warn(`[SonheMenu] falha ao cancelar anúncio órfão ${listingId}: ${erroCancelar}`);
        }
        jogador.sendMessage("O item na sua mão mudou antes de eu conseguir concluir o anúncio. Nada foi cobrado — tenta de novo.");
        return;
    }

    let itemSerializado;
    try {
        itemSerializado = serializarItem(itemFinal);
    } catch (erro) {
        console.warn(`[SonheMenu] falha ao serializar item do anúncio ${listingId}: ${erro}`);
        jogador.sendMessage("Não consegui preparar seu item pro anúncio. Tenta de novo.");
        try {
            await chamarBridge("/ah/anuncio-cancelar", { listingId, vendedorNome: jogador.name });
        } catch (erroCancelar) {
            console.warn(`[SonheMenu] falha ao cancelar anúncio ${listingId} após erro de serialização: ${erroCancelar}`);
        }
        return;
    }

    // Só remove o item da mão depois do "ok" da Bridge E da revalidação acima.
    try {
        const container = jogador.getComponent("minecraft:inventory")?.container;
        container?.setItem(slot, undefined);
    } catch (erro) {
        console.warn(`[SonheMenu] falha ao remover item da mão pra criar anúncio ${listingId}: ${erro}`);
    }

    salvarItemEscrow(listingId, {
        listingId,
        vendedorNomeMinecraft: jogador.name,
        criadoEm: Date.now(),
        expiraEm,
        preco,
        item: itemSerializado,
    });

    const indice = lerIndice();
    indice.ativos.push(listingId);
    salvarIndice(indice);

    jogador.sendMessage("Anúncio criado com sucesso!");
}

// ── Minhas vendas (cancelamento) ─────────────────────────────
async function abrirMinhasVendas(jogador) {
    const indice = lerIndice();
    const agora = Date.now();
    const meus = [];
    for (const listingId of indice.ativos) {
        try {
            const dados = lerItemEscrow(listingId);
            if (!dados) continue;
            if (dados.vendedorNomeMinecraft !== jogador.name) continue;
            meus.push(dados);
        } catch (erro) {
            console.warn(`[SonheMenu] falha ao ler anúncio ${listingId} em minhas vendas: ${erro}`);
        }
    }

    if (meus.length === 0) {
        const form = new ActionFormData()
            .title("Minhas vendas")
            .body("Você não tem nenhum anúncio ativo.")
            .button("Voltar", ICONE_PLACEHOLDER);
        try {
            const resposta = await form.show(jogador);
            if (!resposta.canceled && resposta.selection === 0) await abrirAuctionHouse(jogador);
        } catch (erro) {
            console.warn(`[SonheMenu] falha ao abrir Minhas vendas (vazio) pra ${jogador?.name}: ${erro}`);
        }
        return;
    }

    const form = new ActionFormData().title("Minhas vendas").body("Escolha um anúncio pra cancelar.");
    for (const dados of meus) {
        const nome = dados.item.nameTag || formatarNomeItem(dados.item.typeId);
        const status = dados.expiraEm < agora ? "expirado" : "ativo";
        form.button(`${nome}\n${dados.preco} moedas (${status})`, ICONE_PLACEHOLDER);
    }
    form.button("Voltar", ICONE_PLACEHOLDER);

    let resposta;
    try {
        resposta = await form.show(jogador);
    } catch (erro) {
        console.warn(`[SonheMenu] falha ao abrir Minhas vendas pra ${jogador?.name}: ${erro}`);
        return;
    }
    if (resposta.canceled || resposta.selection === undefined) return;

    if (resposta.selection < meus.length) {
        await confirmarCancelamento(jogador, meus[resposta.selection].listingId);
    } else {
        await abrirAuctionHouse(jogador);
    }
}

async function confirmarCancelamento(jogador, listingId) {
    const form = new MessageFormData()
        .title("Cancelar anúncio")
        .body("Cancelar este anúncio? O item volta pro seu inventário (ou pro correio, se não couber).")
        .button1("Sim")
        .button2("Não");

    let resposta;
    try {
        resposta = await form.show(jogador);
    } catch (erro) {
        console.warn(`[SonheMenu] falha ao abrir confirmação de cancelamento ${listingId}: ${erro}`);
        return;
    }
    if (resposta.canceled || resposta.selection === undefined || resposta.selection !== 0) {
        await abrirMinhasVendas(jogador);
        return;
    }

    const dados = lerItemEscrow(listingId);
    if (!dados) {
        jogador.sendMessage("Esse anúncio já não existe mais.");
        await abrirMinhasVendas(jogador);
        return;
    }

    let resp;
    try {
        resp = await chamarBridge("/ah/anuncio-cancelar", { listingId, vendedorNome: jogador.name });
    } catch (erro) {
        console.warn(`[SonheMenu] falha de rede ao cancelar anúncio ${listingId}: ${erro}`);
        jogador.sendMessage("Não consegui cancelar o anúncio agora. Tenta de novo em alguns segundos.");
        return;
    }

    let corpo;
    try {
        corpo = JSON.parse(resp.body);
    } catch (erro) {
        console.warn(`[SonheMenu] resposta inválida da Bridge ao cancelar ${listingId}: ${erro}`);
        jogador.sendMessage("Não consegui cancelar o anúncio agora. Tenta de novo em alguns segundos.");
        return;
    }

    if (resp.status !== 200 || corpo.status !== "ok") {
        jogador.sendMessage("Não foi possível cancelar o anúncio agora.");
        await abrirMinhasVendas(jogador);
        return;
    }

    removerItemEscrow(listingId);
    removerDoIndice(listingId);

    let aviso = null;
    try {
        const { itemStack, avisos } = reconstituirItemStack(dados.item);
        entregarOuGuardarNoCorreio(jogador.name, itemStack, dados.item, "cancelamento");
        aviso = mensagemAvisos(avisos);
    } catch (erro) {
        console.warn(`[SonheMenu] falha ao devolver item cancelado ${listingId}: ${erro}`);
        adicionarAoCorreio(jogador.name, "cancelamento", dados.item);
    }

    jogador.sendMessage("Anúncio cancelado. Seu item foi devolvido.");
    if (aviso) jogador.sendMessage(aviso);
}

// ── Rotina de expiração (sem UI, roda sozinha) ───────────────
async function expirarAnuncio(listingId, dados) {
    try {
        const resposta = await chamarBridge("/ah/anuncio-expirar", { listingId });
        let corpo;
        try {
            corpo = JSON.parse(resposta.body);
        } catch (erro) {
            console.warn(`[SonheMenu] resposta inválida da Bridge ao expirar ${listingId}: ${erro}`);
            return;
        }
        if (resposta.status !== 200 || corpo.status !== "ok") return; // tenta de novo no próximo ciclo

        removerItemEscrow(listingId);
        removerDoIndice(listingId);

        const { itemStack } = reconstituirItemStack(dados.item);
        entregarOuGuardarNoCorreio(dados.vendedorNomeMinecraft, itemStack, dados.item, "expiracao");
        // vendedor pode estar offline agora — não dá pra sendMessage; o aviso de
        // encantamento perdido (se houver) fica só no console nesse caminho.
    } catch (erro) {
        console.warn(`[SonheMenu] falha ao expirar anúncio ${listingId}: ${erro}`);
    }
}

function rodarExpiracaoAnuncios() {
    const indice = lerIndice();
    const agora = Date.now();

    for (const listingId of indice.ativos) {
        try {
            const dados = lerItemEscrow(listingId);
            if (!dados) {
                removerDoIndice(listingId); // escrow inconsistente (índice órfão) — limpa e segue
                continue;
            }
            if (dados.expiraEm >= agora) continue;

            expirarAnuncio(listingId, dados); // assíncrona; uma falha aqui não deve travar os outros itens
        } catch (erro) {
            console.warn(`[SonheMenu] falha ao processar expiração de ${listingId}: ${erro}`);
        }
    }
}

// ── Entrega do correio ao jogador reaparecer no mundo ────────
function entregarCorreioPendente(jogador) {
    const correio = lerCorreio(jogador.name);
    if (!correio.pendentes || correio.pendentes.length === 0) return;

    const container = jogador.getComponent("minecraft:inventory")?.container;
    if (!container) return;

    const restantes = [];
    const avisosAcumulados = new Set();
    let entregues = 0;
    for (const pendente of correio.pendentes) {
        try {
            const { itemStack, avisos } = reconstituirItemStack(pendente.item);
            // addItem NÃO lança erro se não couber — devolve o que restou
            // (undefined = coube tudo). Ignorar isso faria o item some depois
            // de já contar como "entregue".
            const sobrou = container.addItem(itemStack);
            if (sobrou === undefined) {
                entregues += 1;
                avisos.forEach((a) => avisosAcumulados.add(a));
            } else {
                restantes.push({ origem: pendente.origem, item: serializarItem(sobrou) });
            }
        } catch (erro) {
            console.warn(`[SonheMenu] item do correio de ${jogador.name} ainda não coube: ${erro}`);
            restantes.push(pendente);
        }
    }

    // Salva sempre (não só quando entregues > 0) — uma entrega parcial reduz
    // o correio mesmo sem completar nenhum item inteiro.
    salvarCorreio(jogador.name, { pendentes: restantes });

    if (entregues > 0) {
        jogador.sendMessage(`Você recuperou ${entregues} item(ns) da Auction House do seu correio.`);
        const aviso = mensagemAvisos([...avisosAcumulados]);
        if (aviso) jogador.sendMessage(aviso);
    }
}

// ── Self-registro (efeito colateral só de importar este arquivo) ────
try {
    system.runInterval(() => {
        try {
            rodarExpiracaoAnuncios();
        } catch (erro) {
            console.warn(`[SonheMenu] falha na rotina de expiração da Auction House: ${erro}`);
        }
    }, INTERVALO_EXPIRACAO_TICKS);
} catch (erro) {
    console.warn(`[SonheMenu] não consegui registrar a rotina de expiração da Auction House: ${erro}`);
}

try {
    world.afterEvents.playerSpawn.subscribe((evento) => {
        try {
            entregarCorreioPendente(evento.player);
        } catch (erro) {
            console.warn(`[SonheMenu] falha ao entregar correio da Auction House pra ${evento.player?.name}: ${erro}`);
        }
    });
} catch (erro) {
    console.warn(`[SonheMenu] não consegui registrar a entrega de correio da Auction House: ${erro}`);
}
