# SONHE Menu — JSON UI: o que descobrimos (checkpoint 1.0.17)

Engine testada: Bedrock 1.26.44 (cliente Windows, launcher "Minecraft Bedrock").

## Fatos comprovados em jogo

1. `modifications` NAO existe nessa versao. O engine reporta
   `Unknown property [modifications]` e o controle fica sem `type`, quebrando a tela.
   => Override de controle vanilla se faz REDEFININDO a chave pelo nome puro.

2. Override por nome puro FUNCIONA no namespace `server_form`.
   Prova: redefinir `main_screen_content` sem `type` quebrou a tela inteira
   (`Type not specified (or @-base not found) for control: root_screen_panel`),
   ou seja o def substituiu o vanilla de verdade.
   Vale para `long_form`, `long_form_panel` e `main_screen_content`.

3. `nine_slice_size` dentro do controle `image` NAO existe nessa versao
   (`Unknown property [nine_slice_size]`). Nine-slice se declara SO no arquivo
   `.json` irmao do PNG: `{ "nineslice_size": N, "base_size": [w,h] }`.

4. `type: grid` + `collection_name: "form_buttons"` NAO popula.
   Testado com `grid_item_template`, `grid_dimensions` e
   `#form_button_contents` -> `#maximum_grid_items`: grid fica vazio.
   O que popula e o padrao do vanilla:
   `type: stack_panel` + `factory` com `control_ids` +
   `collection_name: "form_buttons"` +
   binding `#form_button_contents` -> `#collection_length`.

5. `#form_button_length` NAO existe. O nome real da contagem e
   `#form_button_contents` (confirmado no server_form.json vanilla da Mojang).

6. `factory` dentro de `type: grid` e invalido — factory so vive em
   stack_panel/collection_panel.

7. Nao setar `$default_button_texture` num `panel` PAI esperando que chegue
   no filho `@common_buttons.light_text_button`. As vars tem que ir no
   proprio no do botao.

8. Log de servidor dedicado NUNCA mostra erro de JSON UI — UI e renderizada
   no cliente. Usar o Content Log do cliente
   (Configuracoes > Nivel de Registro da Interface Grafica > Detalhes).

## Estado deste checkpoint

- `long_form` redefinido como panel contendo SO o grid (`hook_sonhe_grid`),
  sem o ramo `default_ui`. Ou seja: TODO ActionFormData do mundo usa a tela
  custom, sem a chave do marcador no titulo.
- A chave por marcador (`§d§r§e§a§m§r` no title + view binding com subtracao
  de string) ainda NAO foi revalidada depois de todos os outros fixes.
  Era o suspeito original, mas os bloqueios reais eram os itens 3 e 4.

## Pendencias visuais conhecidas

- `panel_frame.png` e `tile_frame.png` sao 1254x1254 RGB SEM alpha e sem
  borda desenhada — esticam feito nuvem. Precisam ser refeitas como moldura
  9-slice de verdade (RGBA, borda definida, tamanho pequeno tipo 48x48).
- Textura do botao "anda" entre estado normal e hover.
- `grid_screen` com `size: [340,240]` fixo fica grande demais em telas com
  poucos botoes.
- Falta label de `#form_text` na tela custom — por isso "Meu Perfil" aparece
  sem corpo de texto.
- Botoes ainda em lista; o layout de quadradinhos 3 por linha precisa ser
  feito com indices fixos de collection (`collection_index`), nao com grid.

---

# Rodada 2 de pesquisa (10 agentes, fontes primarias: bedrock-samples 1.26.40.5,
# bedrock-wiki, schema KalmeMarq, pack publicado Chest-UI "26.40 Update")

## CORRECOES a fatos que eu havia registrado errado

1. **`nineslice_size`** e o nome correto — SEM underscore entre "nine" e "slice".
   O `nine_slice_size` que eu usei era TYPO, e por isso deu `Unknown property`.
   Nao e que a engine nao suporte nine-slice no controle. Pode ir direto no
   controle `image`. O sidecar `.json` ao lado do PNG tambem funciona e e o que
   a Mojang usa (varredura dos 386 .json de textures/ui: as unicas chaves sao
   `nineslice_size` 342x, `base_size` 348x, `tiled` 4x).
   Ordem do array = `[left, top, right, bottom]`.

2. **`modifications` EXISTE** e e documentado. Meu erro foi outro: ele so edita
   def que JA existe em pack inferior; se nao acha, cria def nova e cai em
   "Type not specified". Nao vale a pena perseguir — override por nome puro
   funciona e e mais simples.

3. **`collection_index` existe no vanilla atual** (12 arquivos, ex:
   pdp_screenshots_section.json com collection_index 0/1/2 em stack_panel
   horizontal). O `Unknown property` que levei provavelmente veio do def sem
   `type` resolvido, nao da propriedade. Fica como plano B viavel.

4. **`type: grid` com collection NAO e incompativel com form_buttons.**
   A causa real da quebra silenciosa foi layout:
   - `grid_dimensions` e `#maximum_grid_items` sao FAMILIAS MUTUAMENTE
     EXCLUSIVAS. Nos 48 grids do vanilla 1.26.40 a combinacao aparece 0 vezes.
   - grid tem size default `["100%c","100%c"]`; item em `100%` fecha o ciclo.
   - TODO grid vanilla alimentado por collection usa grid E item em PIXEL FIXO.
   - numero de colunas = `floor(largura_do_grid / largura_do_item)`.
   - `grid_item_template` NAO leva `@` no vanilla.

## Regra unificadora da invalidacao silenciosa

O parser valida SO NOMES de propriedade. Nao valida tipo de valor, nem
existencia de namespace/@base, nem sanidade de layout. Logo:

- **Dependencia circular de tamanho e a causa nº1.** Em cada eixo, o pai OU o
  filho e dono do tamanho, nunca os dois. Pai `%c`/`%cm`/`%sm` exige filho em
  px, `default`, ou `%c` dos proprios filhos.
- `fill` e proibido dentro de pai com altura `%c`/`%cm`, e vale so uma vez por
  stack_panel, no eixo da orientacao.
- `main_screen_content` vanilla e literalmente `size: [0,0]` — qualquer `100%`
  abaixo dele vira 0px sem erro. Tela custom deve usar px ou `%c`.
- Nome de filho igual ao proprio @base, ou igual a um irmao, quebra em silencio.
- `min_size` e `max_size` EXISTEM e aceitam as mesmas unidades de size.

## Altura adaptativa: o padrao e o INVERSO do que eu tentei

O conteudo e FILHO da imagem de fundo, nao irmao dela. Assim nenhum eixo fica
circular: Y e child-driven de baixo pra cima, X e parent-driven da largura fixa.

    raiz    : [304, "100%cm"]   + max_size [304,"100%"]
      imagem: ["100%", "100%c + 24px"]  <- a moldura e o PAI
        stack: ["100% - 24px", "100%c"]
          itens...

Vanilla que usa isso: `common_dialogs.form_fitting_main_panel_no_buttons`,
`common_panel`, `dialog_background_opaque_with_child`, aplicado em
npc_interact_screen.json exatamente porque "there could be any amount of
student buttons and we don't want dead space". A Mojang usa `100%cm` (maior
filho) e nao `100%c` quando ha irmaos que nao devem somar altura.

## Botao: a textura nao "anda", o CONTEUDO anda

`light_text_button` define `$button_pressed_offset|default: [0,1]` e o estado
`pressed` faz `"$button_offset": "$button_pressed_offset"`. Corrige com
`"$button_pressed_offset": [0,0]`.

Nomes reais dos arquivos vanilla (os que eu citei nao existem):
- `resource_pack/ui/ui_template_buttons.json` -> namespace `common_buttons`
- `resource_pack/ui/ui_common.json`           -> namespace `common`
- `common.button_base` NAO existe; existe so `common.button`.

As 4 texturas de estado vivem em `light_button_assets@common.button`. As
vanilla sao 4x4 com nineslice 1 — textura custom sem sidecar equivalente
estica diferente em cada estado.

`dark_text_button` existe e ja vem com `$dark_button_default_text_color`,
poupando overrides de cor pra texto claro sobre arte escura.

## Chave por marcador §: continua valida

Nao existe API/binding/form id novo em 2026. O Chest-UI (commit "26.40 Update",
2026-08-14, praticamente esta build) usa § LITERAL dentro de
`source_property_name`. O par correto e simplesmente:

    "bindings": [
      { "binding_name": "#title_text" },
      { "binding_type": "view",
        "source_property_name": "((#title_text - '§d§r§e§a§m§r') = #title_text)",
        "target_property_name": "#visible" }
    ]

SEM `binding_type: global` e SEM `binding_condition` quando o controle e filho
direto do `long_form` sobrescrito. `global` so e necessario para controles
DENTRO de `sonhe_forms.grid_screen`.

ATENCAO WINDOWS: salvar o .json em UTF-8 sem BOM. `Set-Content`/`Add-Content`
do PowerShell usam ANSI por padrao e transformam § em 0xA7 solto, quebrando o
match em silencio.
