import { Command } from 'commander';
import path from 'node:path';
import { existsSync } from 'node:fs';

import { loadDatos, variablesDoc } from './config/load-datos.js';
import { loadLlm } from './config/load-llm.js';
import { loadMarco } from './config/load-marco.js';
import { loadTemas } from './config/load-temas.js';
import { construirPrompt } from './prompt/build-prompt.js';
import { generarConMinimo } from './llm/anti-recorte.js';
import { generarSintesisCualitativa, ensamblarSintesis } from './post/sintesis.js';
import { validarDocumento } from './post/validar.js';
import { estimarTiempos, formatearDuracion } from './post/metricas.js';
import { escribirSalida, nombreBase } from './output/escribir.js';

const program = new Command();

program
  .name('z-material-didactico')
  .description('Generador de material didáctico técnico (LLM: llama.cpp local o GLM cloud)')
  .option('--fila <n>', 'genera el documento de la fila N de temas-a-tratar.md')
  .option('--todas', 'genera un documento por cada fila de temas-a-tratar.md', false)
  .option('-m, --marco <id|path>', 'modo legacy: número de clase o ruta a un archivo de marco')
  .option('--temas <path>', 'ruta a temas-a-tratar.md', 'temas-a-tratar.md')
  .option('--config-datos <path>', 'ruta a config-datos.md', 'config-datos.md')
  .option('--config-llm <path>', 'ruta a config-llm.json', 'config-llm.json')
  .option('-p, --provider <key>', 'provider a usar de config-llm.json (ej: llama-cpp, glm-cloud)')
  .option('--modelo <id>', 'id del modelo (sobreescribe el default del provider)')
  // Development default: 4000 chars for fast iteration. Set to 20000 for production (spec-princ §4.2).
  .option('--minimo <n>', 'mínimo de caracteres del documento (producción: 20000)', '4000')
  .option('--reintentos <n>', 'reintentos de continuación si queda corto', '2')
  .option('--max-tokens <n>', 'tokens máximos por llamada', '16384')
  .option('--temperature <n>', 'temperatura del muestreo (texto técnico)', '0.2')
  .option('--dry-run', 'arma el prompt y valida config sin llamar al LLM', false)
  .option('--sin-sintesis', 'omite la segunda llamada de síntesis', false)
  .action(run);

program.parseAsync(process.argv).catch((err) => {
  console.error('\n[ERROR]', describirError(err));
  if (process.env.DEBUG && err?.stack) console.error(err.stack);
  process.exit(1);
});

/**
 * Turn an AI SDK error (RetryError / APICallError) into a short, actionable message.
 */
function describirError(err) {
  const base = err?.lastError ?? err?.errors?.at?.(-1) ?? err;
  const parts = [];
  if (err?.name) parts.push(err.name);
  if (base?.statusCode) parts.push(`HTTP ${base.statusCode}`);
  if (base?.responseBody) parts.push(String(base.responseBody));
  const body = String(base?.responseBody ?? '');
  if (/1113|余额不足|insufficient|余额/i.test(body)) {
    parts.push('→ La cuenta no tiene saldo.');
  } else if (base?.statusCode === 401 || base?.statusCode === 403) {
    parts.push('→ Falló la autenticación: revisá la API key en config-llm.json');
  } else if (base?.statusCode === 404) {
    parts.push('→ Recurso no encontrado: revisá el baseURL y el id del modelo en config-llm.json');
  }
  if (parts.length === 0) parts.push(err?.message ?? String(err));
  return parts.join(' · ');
}

/**
 * @param {object} opts
 */
async function run(opts) {
  const genOpts = {
    minimo: Number(opts.minimo),
    maxTokens: Number(opts.maxTokens),
    maxReintentos: Number(opts.reintentos),
    temperature: Number(opts.temperature),
    sinSintesis: opts.sinSintesis,
  };

  // Resolve mode: temas-a-tratar.md (default) or legacy marco file.
  const modo = opts.todas ? 'todas' : opts.fila ? 'fila' : opts.marco ? 'marco' : null;
  if (!modo) {
    throw new Error('Especificá un modo: --fila <n> | --todas | --marco <id|path>. Insumo principal: temas-a-tratar.md.');
  }

  const vars = variablesDoc(await loadDatos(opts.configDatos));

  // Build the work list: each item { marco, fila, etiqueta }.
  /** @type {{ marco: object, fila: number|null, etiqueta: string }[]} */
  const trabajos = [];
  if (modo === 'marco') {
    const marcoPath = /^\d+$/.test(String(opts.marco))
      ? path.join('marcos', `clase-${opts.marco}.md`)
      : opts.marco;
    if (!existsSync(marcoPath)) throw new Error(`No se encuentra el archivo de marco: ${marcoPath}`);
    trabajos.push({ marco: await loadMarco(marcoPath), fila: null, etiqueta: `marco ${marcoPath}` });
  } else {
    const temas = await loadTemas(opts.temas);
    const sel = modo === 'todas' ? temas : temas.filter((t) => t.n === Number(opts.fila));
    if (sel.length === 0) {
      throw new Error(`No se encontró la fila ${opts.fila} en ${opts.temas} (tiene ${temas.length} filas).`);
    }
    for (const t of sel) {
      const marco = { clase: null, ejeTematico: null, repaso: false, temas: [t.texto], contextoAdicional: '' };
      trabajos.push({ marco, fila: t.n, etiqueta: `fila ${t.n}: ${t.texto}` });
    }
  }

  console.log(`→ Config: ${opts.configDatos} | ${opts.configLlm} | ${trabajos.length} trabajo(s) | minimo=${genOpts.minimo}`);

  if (opts.dryRun) {
    const { system, prompt } = construirPrompt(vars, trabajos[0].marco, { minimo: genOpts.minimo });
    console.log(`\n[DRY-RUN] Mostrando el prompt del primer trabajo (${trabajos[0].etiqueta}).`);
    console.log('--- SYSTEM ---\n' + system);
    console.log('\n--- PROMPT ---\n' + prompt);
    return;
  }

  const { model, providerKey, modelId, baseURL, apiKeySource } = await loadLlm(opts.configLlm, {
    providerKey: opts.provider,
    modelId: opts.modelo,
  });
  console.log(`→ LLM: provider="${providerKey}" model="${modelId}" @ ${baseURL} | key: ${apiKeySource}`);

  for (let i = 0; i < trabajos.length; i++) {
    const tr = trabajos[i];
    console.log(`\n========== [${i + 1}/${trabajos.length}] ${tr.etiqueta} ==========`);
    await generarUna({ vars, marco: tr.marco, fila: tr.fila, model, genOpts });
  }
  console.log(`\n✓ ${trabajos.length} documento(s) generado(s) en output/`);
}

/**
 * Generate one document end-to-end (prompt → generate → validate → synthesis → write).
 *
 * @param {object} args
 * @param {object} args.vars
 * @param {object} args.marco
 * @param {number|null} args.fila
 * @param {import('ai').LanguageModel} args.model
 * @param {object} args.genOpts
 */
async function generarUna({ vars, marco, fila, model, genOpts }) {
  const { minimo, maxTokens, maxReintentos, temperature, sinSintesis } = genOpts;

  console.log(`  • Tema: ${marco.temas[0]}`);

  const { system, prompt } = construirPrompt(vars, marco, { minimo });

  console.log(`→ Generando documento (mínimo ${minimo} caracteres)…`);
  const inicio = Date.now();
  let streamActivo = false;
  const { texto: documento, intentos, cumplido } = await generarConMinimo({
    model,
    system,
    prompt,
    minimo,
    maxTokens,
    maxReintentos,
    temperature,
    onChunk: (chunk) => {
      if (!streamActivo) {
        process.stdout.write('\n--- stream documento ---\n');
        streamActivo = true;
      }
      process.stdout.write(chunk);
    },
    onEtapa: (etapa, info) => {
      if (etapa === 'continuacion') {
        streamActivo = false;
        console.log(`\n  ↻ continuación #${info.intento} (llevamos ${info.longitudActual} caracteres)…`);
      }
    },
  });
  process.stdout.write('\n');
  const segGen = ((Date.now() - inicio) / 1000).toFixed(1);
  console.log(`  ✓ documento: ${documento.length} caracteres en ${segGen}s · ${intentos.length} llamada(s) · ${cumplido ? 'mínimo OK' : 'por debajo del mínimo'}`);

  const validacion = validarDocumento(documento, { minimo });
  const tiempos = estimarTiempos(documento);
  if (validacion.problemas.length) {
    console.log('  ⚠ Avisos de validación:');
    for (const p of validacion.problemas) console.log(`    - [${p.tipo}] ${p.mensaje}`);
  }

  let sintesis = '';
  if (!sinSintesis) {
    console.log('→ Generando sección "Síntesis y Conclusión"…');
    process.stdout.write('\n--- stream síntesis ---\n');
    const cualitativo = await generarSintesisCualitativa({
      model,
      documento,
      temperature,
      onChunk: (c) => process.stdout.write(c),
    });
    sintesis = ensamblarSintesis({ documento, tiempos, cualitativo });
    process.stdout.write('\n  ✓ síntesis generada.\n');
  } else {
    console.log('→ Se omitió la síntesis (--sin-sintesis).');
  }

  const nb = nombreBase(marco, fila);
  const archivo = await escribirSalida({ dir: 'output', nombreBase: nb, documento, sintesis });

  console.log('\n  --- resumen ---');
  console.log(`  Caracteres: ${documento.length} | Palabras: ${tiempos.palabras}`);
  console.log(`  Lectura continua: ~${formatearDuracion(tiempos.lecturaContinuaMin)} | activa: ~${formatearDuracion(tiempos.lecturaActivaMin)}`);
  console.log(`  Avisos: ${validacion.problemas.length} | Archivo: ${archivo}`);
}
