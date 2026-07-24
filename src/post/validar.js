// Patterns that indicate LaTeX syntax (forbidden by spec-princ.md §4.2).
const PATRONES_LATEX = [
  /\\frac\b/,
  /\\cdot\b/,
  /\\sum\b/,
  /\\int\b/,
  /\\sqrt\b/,
  /\$\$[\s\S]+?\$\$/,
  /\$[^\n$]+?\$/,
  /\\\([\s\S]+?\\\)/,
  /\\\[[\s\S]+?\\\]/,
  /\\[a-zA-Z]+\{[^}]*\}/, // \command{...}
];

const PALABRAS_CLAVE_CIERRE = [
  /\bespero que (esto|te|les) (haya|ayude)/i,
  /\bqued[oó] a (tu|tu disposición|disposición)\b/i,
  /\bno dudes en consult/i,
  /\b¿.*(pregunta|duda|quieres|queres)\s*\?/i,
];

/**
 * Validate the generated document against spec-princ.md constraints.
 *
 * @param {string} texto
 * @param {{ minimo?: number }} [opts]
 * @returns {{ longitud: number, palabras: number, problemas: Array<{tipo: string, mensaje: string}> }}
 */
export function validarDocumento(texto, opts = {}) {
  const minimo = opts.minimo ?? 20000;
  const problemas = [];
  const longitud = texto.length;

  if (longitud < minimo) {
    problemas.push({
      tipo: 'longitud',
      mensaje: `Longitud ${longitud} caracteres < mínimo ${minimo}`,
    });
  }

  for (const p of PATRONES_LATEX) {
    if (p.test(texto)) {
      problemas.push({
        tipo: 'latex',
        mensaje: `Se detectó sintaxis LaTeX (patrón: ${p})`,
      });
      break;
    }
  }

  // "Número de clase" refers to the session/lesson number (spec §4.2), NOT to
  // regulatory categories like "chaleco clase 3", "extintor clase A", etc.
  // Exclude matches whose line contains category-indicating words.
  const reClase = /\b(clase|sesi[oó]n|encuentro)\s+(n[ºo°]?\.?\s*)?\d{1,3}\b/i;
  const mClase = texto.match(reClase);
  if (mClase) {
    const idx = texto.toLowerCase().indexOf(mClase[0].toLowerCase());
    const startLine = texto.lastIndexOf('\n', idx) + 1;
    const endLine = texto.indexOf('\n', idx);
    const linea = texto.slice(startLine, endLine === -1 ? undefined : endLine);
    const palabrasCategoria =
      /chaleco|extintor|fuego|incendio|norma|tensii[oó]n|tensi[oó]n|tension|guante|casco|protecci[oó]n|reflect|visibilidad|categor|energ/i;
    if (!palabrasCategoria.test(linea)) {
      problemas.push({
        tipo: 'numero_clase',
        mensaje: `Posible número de clase/sesión en el texto: "${mClase[0]}"`,
      });
    }
  }

  for (const p of PALABRAS_CLAVE_CIERRE) {
    if (p.test(texto)) {
      problemas.push({
        tipo: 'cierre_dubitativo',
        mensaje: `Posible cierre dubitativo/interactivo (patrón: ${p})`,
      });
      break;
    }
  }

  const palabras = (texto.trim().match(/\S+/g) ?? []).length;
  return { longitud, palabras, problemas };
}
