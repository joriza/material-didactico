const PALABRAS_POR_MINUTO_LECTURA = 200; // continuous reading, adult technical text
const PALABRAS_POR_MINUTO_ACTIVA = 90; // reading + note-taking

/**
 * @param {string} texto
 */
export function contarPalabras(texto) {
  return (texto.trim().match(/\S+/g) ?? []).length;
}

/**
 * Estimate reading times from word count.
 * @param {string} texto
 */
export function estimarTiempos(texto) {
  const palabras = contarPalabras(texto);
  return {
    palabras,
    lecturaContinuaMin: Math.max(1, Math.round(palabras / PALABRAS_POR_MINUTO_LECTURA)),
    lecturaActivaMin: Math.max(1, Math.round(palabras / PALABRAS_POR_MINUTO_ACTIVA)),
  };
}

/**
 * Format a minute count as "X h Y min" or "Y min".
 * @param {number} min
 */
export function formatearDuracion(min) {
  if (min < 60) return `${min} min`;
  const h = Math.floor(min / 60);
  const m = min % 60;
  return m > 0 ? `${h} h ${m} min` : `${h} h`;
}
