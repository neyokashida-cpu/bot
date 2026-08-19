import { world, system } from "@minecraft/server";
import * as mcserver from "@minecraft/server";
import { abrirMenuPrincipal } from "./menu.js";
import "./estatisticas.js"; // auto-registra os listeners de blocos/mobs/mortes/primeira entrada

// SONHE — /menu (fundação).
// Bedrock não permite registrar um "/menu" puro via Script API — comandos
// customizados só existem namespaced (ex: /sonhe:menu) e dependem do toggle
// experimental "Custom Commands", que este projeto nunca usou antes (ver
// README deste pack). Por isso este arquivo tenta os DOIS caminhos:
//   1. "!menu" no chat — mesmo padrão 100% comprovado do "!vincular"
//      (ADDONS/SonheBridge_BP/scripts/main.js). Sempre funciona.
//   2. "/sonhe:menu" de verdade, via customCommandRegistry — experimental;
//      se o toggle não estiver ativo neste mundo, essa parte falha sozinha
//      (capturada abaixo) e o "!menu" continua garantido.

// ── 1) !menu — rede de segurança ────────────────────────────
// IMPORTANTE: este pack precisa carregar ANTES do SonheChat_BP na ordem do
// mundo. O SonheChat_BP cancela TODA mensagem de chat incondicionalmente
// (world.beforeEvents.chatSend) — se ele rodar primeiro, esse handler nunca
// recebe a mensagem. Foi exatamente o bug que quebrou "!vincular" até
// reordenar SonheBridge_BP antes de SonheChat_BP; o mesmo se aplica aqui.
world.beforeEvents.chatSend.subscribe((evento) => {
    if (evento.message.trim().toLowerCase() !== "!menu") return;
    evento.cancel = true;
    const jogador = evento.sender;
    system.run(() => abrirMenuPrincipal(jogador));
});

// ── 2) /sonhe:menu — comando real (experimental) ────────────
// Import via namespace (import * as mcserver) em vez de desestruturar
// "CommandPermissionLevel"/"CustomCommandStatus": se esses símbolos não
// existirem nesta versão da API, um import nomeado quebraria o carregamento
// do script inteiro (e levaria o "!menu" junto). Acessar como propriedade
// de objeto só resulta em "undefined", tratado abaixo com segurança.
try {
    mcserver.system.beforeEvents.startup.subscribe((inicio) => {
        try {
            inicio.customCommandRegistry.registerCommand(
                {
                    name: "sonhe:menu",
                    description: "Abre o menu central do SONHE.",
                    permissionLevel: mcserver.CommandPermissionLevel?.Any,
                },
                (origem) => {
                    const jogador = origem.sourceEntity;
                    if (jogador) {
                        system.run(() => abrirMenuPrincipal(jogador));
                    }
                    return { status: mcserver.CustomCommandStatus?.Success };
                }
            );
        } catch (erro) {
            console.warn(
                `[SonheMenu] não consegui registrar /sonhe:menu (toggle "Custom Commands" pode estar desativado neste mundo) — use !menu no chat: ${erro}`
            );
        }
    });
} catch (erro) {
    console.warn(`[SonheMenu] system.beforeEvents.startup indisponível nesta versão da API — use !menu no chat: ${erro}`);
}
