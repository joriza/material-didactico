import { streamText } from 'ai';
import { formatearDuracion } from './metricas.js';

/**
 * Ask the LLM ONLY for the qualitative synthesis (one summary sentence + 5 key points).
 * Numeric values (character count, word count, reading times) are NEVER produced by
 * the model; they are injected by `ensamblarSintesis` from app-computed metrics.
 * This guarantees spec-princ.md §5.1 ("recuento total exacto de caracteres").
 *
 * @param {object} args
 * @param {import('ai').LanguageModel} args.model
 * @param {string} args.documento
 * @param {number} [args.temperature=0.2]
 * @param {number} [args.maxTokens=800]
 * @param {(chunk: string) => void} [args.onChunk]
 * @returns {Promise<{ oracion: string, puntos: string[] }>}
 */
export async function generarSintesisCualitativa({ model, documento, temperature = 0.2, maxTokens = 800, onChunk }) {
  const system = [
    'Sos un asistente que resume documentos técnicos didácticos.',
    'Tono impersonal y formal. No uses LaTeX. Sin cierres interactivos.',
    'Debés respetar EXACTAMENTE el formato de salida pedido.',
  ].join('\n');

  const prompt = [
    'A continuación se presenta el inicio del documento a sintetizar:',
    '',
    `"""${documento.slice(0, 6000)}"""`,
    '',
    'Respondé EXACTAMENTE con este formato y NADA más (sin conteos, sin tiempos, sin introducción):',
    'SINTESIS: <una sola oración que resuma el contenido>',
    'PUNTOS:',
    '1. <primer punto clave, ultracorto, una línea>',
    '2. <segundo punto>',
    '3. <tercer punto>',
    '4. <cuarto punto>',
    '5. <quinto punto>',
  ].join('\n');

  const result = streamText({ model, system, prompt, maxOutputTokens: maxTokens, temperature });
  let texto = '';
  for await (const part of result.textStream) {
    texto += part;
    onChunk?.(part);
  }
  return parsearCualitativo(texto);
}

/**
 * Tolerant parser for the structured qualitative output.
 * @param {string} texto
 */
export function parsearCualitativo(texto) {
  const oracionMatch = texto.match(/SINTESIS\s*:\s*(.+)/i);
  const oracion = oracionMatch ? oracionMatch[1].trim() : texto.trim().split(/\r?\n/)[0];
  const puntos = [];
  for (const linea of texto.split(/\r?\n/)) {
    const m = linea.match(/^\s*\d+[\.\)]\s*(.+)/);
    if (m && puntos.length < 5) puntos.push(m[1].trim());
  }
  return { oracion, puntos };
}

/**
 * Build the final "Síntesis y Conclusión" section with EXACT app-computed numbers.
 *
 * @param {object} args
 * @param {string} args.documento
 * @param {{ palabras: number, lecturaContinuaMin: number, lecturaActivaMin: number }} args.tiempos
 * @param {{ oracion: string, puntos: string[] }} args.cualitativo
 * @returns {string}
 */
export function ensamblarSintesis({ documento, tiempos, cualitativo }) {
  const lc = formatearDuracion(tiempos.lecturaContinuaMin);
  const la = formatearDuracion(tiempos.lecturaActivaMin);
  const puntos = cualitativo.puntos.length ? cualitativo.puntos : ['(no generados)'];
  const puntosMd = puntos.map((p) => `   - ${p}`).join('\n');
  return [
    '## Síntesis y Conclusión',
    '',
    `1. **Caracteres del informe principal:** ${documento.length}`,
    `2. **Síntesis global:** ${cualitativo.oracion || '(no generada)'}`,
    '3. **Puntos clave:**',
    puntosMd,
    '4. **Estimación de tiempos:**',
    `   - Lectura continua: ${lc} (~${tiempos.palabras} palabras).`,
    `   - Lectura activa (con toma de apuntes): ${la}.`,
  ].join('\n');
}
