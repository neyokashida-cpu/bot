// Validador estatico de JSON UI do SONHE.
// Cobre as classes de quebra SILENCIOSA que descobrimos na marra: o engine
// nao loga nada nesses casos, so volta pro vanilla. Rode antes de cada deploy.
//   node ADDONS/SonheMenu_RP/tools/validar_ui.js
const fs = require('fs');
const path = require('path');

const UI_DIR = path.join(__dirname, '..', 'ui');
let falhas = 0, avisos = 0;
const err = m => { console.log('  [FALHA] ' + m); falhas++; };
const warn = m => { console.log('  [aviso] ' + m); avisos++; };
const ok = m => console.log('  [ok] ' + m);

// tamanhos que dependem dos FILHOS  vs  que dependem do PAI
const DEP_FILHO = v => typeof v === 'string' && /%(c|cm)\b/.test(v);
const DEP_PAI  = v => typeof v === 'string' && (/^\s*\d+(\.\d+)?%/.test(v) && !/%(c|cm|x|y)/.test(v) || v === 'fill');

for (const arquivo of fs.readdirSync(UI_DIR).filter(f => f.endsWith('.json'))) {
  const p = path.join(UI_DIR, arquivo);
  const bruto = fs.readFileSync(p);
  console.log('\n=== ' + arquivo + ' ===');

  if (bruto[0] === 0xEF && bruto[1] === 0xBB && bruto[2] === 0xBF)
    err('tem BOM. Marcador § nao vai casar e nada loga.');
  else ok('sem BOM');

  const texto = bruto.toString('utf8');
  let j;
  try { j = JSON.parse(texto); ok('JSON valido'); }
  catch (e) { err('JSON invalido: ' + e.message); continue; }

  if (texto.includes('nine_slice_size'))
    err('usa nine_slice_size (typo). O correto e nineslice_size.');
  if (/"modifications"\s*:/.test(texto))
    err('usa modifications: nao funciona nesta build.');
  if (/"collection_index"\s*:/.test(texto))
    warn('usa collection_index: ja deu Unknown property nesta build.');

  // filho com o mesmo nome do proprio @base = quebra silenciosa
  const ref = /"([A-Za-z_0-9]+)@([A-Za-z_0-9]+)\.([A-Za-z_0-9]+)"/g;
  let m, colisoes = 0;
  while ((m = ref.exec(texto))) if (m[1] === m[3]) { err('colisao filho==base: ' + m[0]); colisoes++; }
  if (!colisoes) ok('nenhuma colisao filho==base');

  // $var usada em propriedade de layout sem default declarado
  const layout = /"(size|offset|alpha|layer|anchor_from|anchor_to|max_size|min_size)"\s*:\s*"\$([A-Za-z_0-9]+)"/g;
  while ((m = layout.exec(texto)))
    if (!texto.includes('"$' + m[2] + '|default"')) warn('$' + m[2] + ' em "' + m[1] + '" sem |default');

  // grid: familias mutuamente exclusivas + item em pixel fixo
  for (const [nome, def] of Object.entries(j)) {
    if (!def || def.type !== 'grid') continue;
    const temDim = !!def.grid_dimensions;
    const temMax = JSON.stringify(def.bindings || []).includes('maximum_grid_items');
    if (temDim && temMax) err(nome + ': grid_dimensions junto de #maximum_grid_items. Sao familias exclusivas.');
    else ok(nome + ': familia de grid coerente');

    if (Array.isArray(def.size) && typeof def.size[1] === 'number')
      warn(nome + ': altura fixa em grid. O vanilla usa "default".');

    const tplNome = (def.grid_item_template || '').split('.').pop();
    const tpl = j[tplNome];
    if (!tpl) { err(nome + ': grid_item_template "' + def.grid_item_template + '" nao existe neste arquivo.'); continue; }
    if (!Array.isArray(tpl.size) || !tpl.size.every(x => typeof x === 'number'))
      err(tplNome + ': item de grid precisa de PIXEL FIXO. Percentual = dependencia circular = quebra silenciosa.');
    else {
      ok(tplNome + ': item em pixel fixo ' + JSON.stringify(tpl.size));
      console.log('        colunas = floor(largura_do_pai / ' + tpl.size[0] + ')');
    }
  }

  // pai que depende dos filhos segurando filho que depende do pai
  (function circular(nome, def) {
    if (!def || typeof def !== 'object') return;
    for (const filho of def.controls || []) {
      for (const [k, v] of Object.entries(filho)) {
        const fs_ = v && v.size;
        if (Array.isArray(def.size) && Array.isArray(fs_)) {
          for (const eixo of [0, 1]) {
            if (DEP_FILHO(def.size[eixo]) && DEP_PAI(fs_[eixo]))
              err('circular em ' + nome + ' -> ' + k + ' (eixo ' + (eixo ? 'Y' : 'X') + '): pai ' +
                  JSON.stringify(def.size[eixo]) + ' com filho ' + JSON.stringify(fs_[eixo]));
          }
        }
        circular(nome + '/' + k, v);
      }
    }
  });
  for (const [nome, def] of Object.entries(j)) {
    if (!def || typeof def !== 'object' || !def.controls) continue;
    (function walk(n, d) {
      for (const filho of d.controls || []) {
        for (const [k, v] of Object.entries(filho)) {
          if (Array.isArray(d.size) && v && Array.isArray(v.size)) {
            for (const eixo of [0, 1]) {
              if (DEP_FILHO(d.size[eixo]) && DEP_PAI(v.size[eixo]))
                err('circular ' + n + ' -> ' + k + ' eixo ' + (eixo ? 'Y' : 'X') + ': pai ' +
                    JSON.stringify(d.size[eixo]) + ' / filho ' + JSON.stringify(v.size[eixo]));
            }
          }
          if (v && v.controls) walk(n + '/' + k, v);
        }
      }
    })(nome, def);
  }
}

console.log('\n' + (falhas ? 'FALHAS: ' + falhas : 'sem falhas') + ' | avisos: ' + avisos);
process.exit(falhas ? 1 : 0);
