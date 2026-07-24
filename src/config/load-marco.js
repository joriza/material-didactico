import { readFile } from 'node:fs/promises';

/**
 * Parse a per-class reference file (marcos/clase-XX.md).
 *
 * Expected format:
 *   # Marco de referencia — Clase 12
 *   - Eje temático: 2 — Configuración de redes LAN
 *   - Repaso: no
 *   - Temas:
 *     - Casos de conectividad
 *     - Resolución de fallas de IP
 *   - Contexto adicional: texto libre opcional
 *
 * @param {string} path
 * @returns {Promise<{ clase: number|null, ejeTematico: string, repaso: boolean, temas: string[], contextoAdicional: string }>}
 */
export async function loadMarco(path) {
  const raw = await readFile(path, 'utf8');
  const lineas = raw.split(/\r?\n/);

  let clase = null;
  let ejeTematico = null;
  let repaso = false;
  let contextoAdicional = '';
  const temas = [];
  let enTemas = false;

  for (const linea of lineas) {
    const t = linea.trim();
    // Normalize: strip a leading list marker ("- " / "* ") from every line
    // so both "- Eje temático:" and "Eje temático:" are accepted.
    const tt = t.replace(/^[-*]\s+/, '');

    if (t.startsWith('#')) {
      const m = tt.match(/clase\s+(\d+)/i);
      if (m && clase === null) clase = Number(m[1]);
      enTemas = false;
      continue;
    }
    if (tt === '') {
      continue;
    }
    if (/^eje\s+tem[aá]tico\s*:/i.test(tt)) {
      ejeTematico = tt.split(':').slice(1).join(':').trim();
      enTemas = false;
      continue;
    }
    if (/^repaso\s*:/i.test(tt)) {
      const v = tt.split(':')[1].trim().toLowerCase();
      repaso = ['sí', 'si', 'true', '1', 'yes'].includes(v);
      enTemas = false;
      continue;
    }
    if (/^temas?\s*:/i.test(tt)) {
      enTemas = true;
      const after = tt.split(':').slice(1).join(':').trim();
      if (after) temas.push(after.replace(/^-\s*/, '').trim());
      continue;
    }
    if (/^contexto\s+adicional\s*:/i.test(tt)) {
      contextoAdicional = tt.split(':').slice(1).join(':').trim();
      enTemas = false;
      continue;
    }
    if (enTemas) {
      const item = tt.replace(/^-\s*/, '').trim();
      if (item) temas.push(item);
    }
  }

  if (!ejeTematico) {
    throw new Error(`marco: falta el campo "Eje tematico:" en ${path}`);
  }
  if (temas.length === 0) {
    throw new Error(`marco: falta la lista de "Temas:" en ${path}`);
  }
  return { clase, ejeTematico, repaso, temas, contextoAdicional };
}
