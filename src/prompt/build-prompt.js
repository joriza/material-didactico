import {
  ROL,
  ESTRATEGIA_PEDAGOGICA,
  REGLAS_ESCRITURA,
  ESTRUCTURA_DOCUMENTO,
  REGLA_SINTESIS,
} from './reglas.js';

/**
 * @typedef {Object} VariablesDoc
 * @property {string} establecimiento
 * @property {string} materia
 * @property {string} carrera
 * @property {string} curso
 * @property {string} docente
 */

/**
 * @typedef {Object} Marco
 * @property {number|null} clase
 * @property {string} ejeTematico
 * @property {boolean} repaso
 * @property {string[]} temas
 * @property {string} contextoAdicional
 */

/**
 * Build the { system, prompt } pair for the main document generation.
 *
 * @param {VariablesDoc} vars
 * @param {Marco} marco
 * @param {{ minimo: number }} opts
 */
export function construirPrompt(vars, marco, opts) {
  const system = [
    ROL,
    '',
    'OBJETIVO: producir un documento técnico de estudio, finalizado y autosuficiente, sobre los temas indicados.',
    '',
    ESTRATEGIA_PEDAGOGICA,
    '',
    REGLAS_ESCRITURA,
    '',
    ESTRUCTURA_DOCUMENTO,
    '',
    `EXTENSIÓN: el documento debe tener como MÍNIMO ${opts.minimo} caracteres (incluyendo espacios). Es preferible pecar de extenso que de corto. Desarrollá cada tema con profundidad, justificando causas y procedimientos.`,
    '',
    REGLA_SINTESIS,
  ].join('\n');

  const temasLista = marco.temas.map((t, i) => `  ${i + 1}. ${t}`).join('\n');
  const contexto = marco.contextoAdicional
    ? `- Contexto adicional: ${marco.contextoAdicional}`
    : '';

  const prompt = [
    'DATOS DE CONTEXTO INSTITUCIONAL Y PEDAGÓGICO:',
    `- Establecimiento: ${vars.establecimiento}`,
    `- Materia: ${vars.materia}`,
    `- Carrera: ${vars.carrera}`,
    `- Curso: ${vars.curso}`,
    `- Docente a cargo: ${vars.docente}`,
    '',
    'MARCO DE REFERENCIA:',
    ...(marco.ejeTematico ? [`- Eje temático: ${marco.ejeTematico}`] : []),
    `- ¿Es clase de repaso?: ${marco.repaso ? 'Sí' : 'No'}`,
    `- Temas a desarrollar:`,
    temasLista,
    contexto,
    '',
    'Redactá el documento técnico de estudio completo siguiendo todas las reglas indicadas. No incluyas la sección "Síntesis y Conclusión".',
  ]
    .filter((l) => l !== null)
    .join('\n');

  return { system, prompt };
}

/**
 * Build the continuation prompt when the first generation came up short.
 *
 * @param {string} cola  tail of the document produced so far
 * @param {number} minimo
 */
export function construirPromptContinuacion(cola, minimo) {
  const system = [
    'Continuás la redacción de un documento técnico didáctico ya iniciado.',
    'REGLAS: no repitas lo ya escrito, no vuelvas a poner el título, no agregues introducción, no escribas cierre ni la sección "Síntesis y Conclusión".',
    `Retomá exactamente donde terminó el texto y seguí desarrollando con la misma profundidad y tono hasta alcanzar un total de al menos ${minimo} caracteres.`,
    REGLAS_ESCRITURA,
  ].join('\n');

  const prompt = [
    'A continuación se muestra el final del documento redactado hasta ahora (NO lo repitas; solo continuá a partir de ahí):',
    '',
    `"""${cola}"""`,
    '',
    'Continuá el desarrollo del documento.',
  ].join('\n');

  return { system, prompt };
}
