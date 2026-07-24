import { readFile } from 'node:fs/promises';

/**
 * Line format expected in config-datos.md:
 *   - **Key**: value
 */
const LINEA_VAR = /^\s*-\s*\*\*([^*]+)\*\*\s*:\s*(.+?)\s*$/;

/**
 * Parse config-datos.md into a plain { key: value } object.
 * @param {string} path
 * @returns {Promise<Record<string, string>>}
 */
export async function loadDatos(path) {
  const raw = await readFile(path, 'utf8');
  const vars = {};
  for (const linea of raw.split(/\r?\n/)) {
    const m = linea.match(LINEA_VAR);
    if (m) vars[m[1].trim()] = m[2].trim();
  }
  if (Object.keys(vars).length === 0) {
    throw new Error(`load-datos: no se encontro ninguna variable con formato "- **Clave**: valor" en ${path}`);
  }
  return vars;
}

// Variables required by spec-princ.md §1.2 (plus establishment).
const OBLIGATORIAS = [
  'Variable_Establecimiento',
  'Variable_Materia',
  'Variable_Carrera',
  'Variable_Curso',
  'Variable_Docente',
];

/**
 * Validate and project the raw variables into the document-relevant subset.
 * @param {Record<string, string>} vars
 */
export function variablesDoc(vars) {
  const faltantes = OBLIGATORIAS.filter((k) => !vars[k]);
  if (faltantes.length) {
    throw new Error(
      `config-datos.md: faltan variables obligatorias: ${faltantes.join(', ')}`,
    );
  }
  return {
    establecimiento: vars.Variable_Establecimiento,
    materia: vars.Variable_Materia,
    carrera: vars.Variable_Carrera,
    curso: vars.Variable_Curso,
    docente: vars.Variable_Docente,
  };
}
