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
