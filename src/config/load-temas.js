import { readFile } from 'node:fs/promises';

/**
 * Parse temas-a-tratar.md into an ordered list of topics.
 * Each non-empty, non-heading line is one topic (one output document).
 *
 * @param {string} path
 * @returns {Promise<Array<{ n: number, texto: string }>>}
 */
export async function loadTemas(path) {
  const raw = await readFile(path, 'utf8');
  const temas = [];
  let n = 0;
  for (const linea of raw.split(/\r?\n/)) {
    const t = linea.trim();
    if (!t || t.startsWith('#')) continue;
    n++;
    temas.push({ n, texto: t });
  }
  if (temas.length === 0) {
    throw new Error(`load-temas: no se encontro ninguna fila en ${path}`);
  }
  return temas;
}
