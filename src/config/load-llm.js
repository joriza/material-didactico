import { readFile } from 'node:fs/promises';
import { createOpenAICompatible } from '@ai-sdk/openai-compatible';

const SOPORTADOS = new Set(['@ai-sdk/openai-compatible']);

/**
 * Load config-llm.json and build a ready-to-use model instance.
 *
 * Expected shape (single or multiple providers under "provider"):
 * {
 *   "provider": {
 *     "llama-cpp": {
 *       "npm": "@ai-sdk/openai-compatible",
 *       "name": "llama-cpp",
 *       "options": { "baseURL": "...", "apiKey": "..." },
 *       "models": { "model-id": { "name": "model-id" } }
 *     }
 *   }
 * }
 *
 * @param {string} path
 * @param {{ providerKey?: string, modelId?: string }} [override]
 */
export async function loadLlm(path, override = {}) {
  const raw = await readFile(path, 'utf8');
  const cfg = JSON.parse(raw);
  const providers = cfg.provider ?? cfg.providers;
  if (!providers || typeof providers !== 'object') {
    throw new Error('config-llm.json: falta la seccion "provider"');
  }
  const keys = Object.keys(providers);
  if (keys.length === 0) {
    throw new Error('config-llm.json: no hay providers definidos bajo "provider"');
  }
  const providerKey = override.providerKey ?? cfg.default ?? keys[0];
  const p = providers[providerKey];
  if (!p) {
    throw new Error(`config-llm.json: provider "${providerKey}" no existe (disponibles: ${keys.join(', ')})`);
  }
  // The "npm" field indicates which adapter to use. It is optional and
  // defaults to @ai-sdk/openai-compatible (the only supported adapter).
  const paquete = p.npm ?? '@ai-sdk/openai-compatible';
  if (!SOPORTADOS.has(paquete)) {
    throw new Error(
      `Provider "${providerKey}" usa npm="${paquete}". Solo se soporta: ${[...SOPORTADOS].join(', ')}.`,
    );
  }
  const options = p.options ?? {};

  // Resolve the API key. Order of precedence:
  //   1. explicit apiKey in config-llm.json
  //   2. environment variable (p.apiKeyEnv, defaulting to ZHIPU_API_KEY for cloud)
  //   3. dummy value for local servers (llama.cpp ignores it)
  const isLocal = /localhost|127\.0\.0\.1/i.test(options.baseURL ?? '');
  const envVar = isLocal ? null : (p.apiKeyEnv ?? 'ZHIPU_API_KEY');
  let apiKey = (options.apiKey ?? '').trim();
  if (apiKey === '' && envVar) apiKey = (process.env[envVar] ?? '').trim();
  if (apiKey === '') {
    if (isLocal) {
      apiKey = 'dummy-key';
    } else {
      throw new Error(
        `Provider "${providerKey}": falta la API key. Cargala en config-llm.json -> provider.${providerKey}.options.apiKey, o definí la variable de entorno ${envVar}.`,
      );
    }
  }
  const apiKeySource = options.apiKey?.trim() ? 'config' : (envVar ? `env:${envVar}` : 'dummy');

  const providerOptions = {
    name: p.name ?? providerKey,
    baseURL: options.baseURL,
    apiKey,
    headers: options.headers,
  };

  // llama.cpp reasoning models (Qwen3-style) dump output into reasoning_content
  // unless we disable thinking. Only applied where the provider requests it,
  // via "disableThinking": true (local models). Cloud APIs ignore this field.
  if (p.disableThinking === true) {
    providerOptions.transformRequestBody = (body) => ({
      ...body,
      chat_template_kwargs: {
        ...(body.chat_template_kwargs ?? {}),
        enable_thinking: false,
      },
    });
  }

  const provider = createOpenAICompatible(providerOptions);
  const modelEntries = Object.entries(p.models ?? {});
  if (modelEntries.length === 0) {
    throw new Error(`Provider "${providerKey}" no declara modelos bajo "models"`);
  }
  const modelId = override.modelId ?? modelEntries[0][0];
  const model = provider(modelId);
  return {
    provider,
    model,
    providerKey,
    modelId,
    baseURL: options.baseURL,
    apiKeySource,
  };
}
