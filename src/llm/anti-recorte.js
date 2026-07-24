import { generarDocumento } from './generar.js';
import { construirPromptContinuacion } from '../prompt/build-prompt.js';

/**
 * Generate the main document, applying continuation retries when the result
 * falls short of the minimum length (anti-truncation strategy for local models).
 *
 * @param {object} args
 * @param {import('ai').LanguageModel} args.model
 * @param {string} args.system
 * @param {string} args.prompt
 * @param {number} [args.minimo=20000]
 * @param {number} [args.maxTokens=4096]
 * @param {number} [args.maxReintentos=2]
 * @param {number} [args.colaContinuacion=2000] characters of tail passed to retries
 * @param {(chunk: string, acumulado: string) => void} [args.onChunk]
 * @param {(etapa: string, info: object) => void} [args.onEtapa]
 */
export async function generarConMinimo({
  model,
  system,
  prompt,
  minimo = 20000,
  maxTokens = 16384,
  maxReintentos = 2,
  colaContinuacion = 2000,
  temperature = 0.2,
  onChunk,
  onEtapa,
}) {
  onEtapa?.('documento', { intento: 0 });
  const primera = await generarDocumento({ model, system, prompt, maxTokens, temperature, onChunk });
  let texto = primera.texto.trim();
  let usage = primera.usage;
  const intentos = [{ intento: 0, longitud: texto.length, finishReason: primera.finishReason }];

  for (let i = 1; i <= maxReintentos && texto.length < minimo; i++) {
    onEtapa?.('continuacion', { intento: i, longitudActual: texto.length });
    const cola = texto.slice(-colaContinuacion);
    const cont = construirPromptContinuacion(cola, minimo);
    const res = await generarDocumento({
      model,
      system: cont.system,
      prompt: cont.prompt,
      maxTokens,
      temperature,
      onChunk,
    });
    texto = `${texto}\n\n${res.texto.trim()}`.trim();
    usage = res.usage ?? usage;
    intentos.push({ intento: i, longitud: texto.length, finishReason: res.finishReason });
  }

  return { texto, usage, intentos, cumplido: texto.length >= minimo };
}
