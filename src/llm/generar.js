import { streamText } from 'ai';

/**
 * Generate a single text completion with streaming.
 *
 * @param {object} args
 * @param {import('ai').LanguageModel} args.model
 * @param {string} args.system
 * @param {string} args.prompt
 * @param {number} [args.maxTokens]
 * @param {number} [args.temperature=0.2] low temperature for technical/deterministic text
 * @param {(chunk: string, acumulado: string) => void} [args.onChunk]
 * @returns {Promise<{ texto: string, usage: any, finishReason: string }>}
 */
export async function generarDocumento({ model, system, prompt, maxTokens, temperature = 0.2, onChunk }) {
  const result = streamText({
    model,
    system,
    prompt,
    maxOutputTokens: maxTokens,
    temperature,
  });

  let texto = '';
  for await (const part of result.textStream) {
    texto += part;
    onChunk?.(part, texto);
  }

  const [usage, finishReason] = await Promise.all([result.usage, result.finishReason]);
  return { texto, usage, finishReason };
}
