/**
 * Thin fetch wrapper for the Nexus API.
 *
 * Normalises the {success, message, data} envelope so pages can `await get(...)`
 * and receive the unwrapped `data` directly, throwing on transport errors.
 */

const BASE = 'http://localhost:8000/api/v1';

async function request(path, options = {}) {
  const res = await fetch(`${BASE}${path}`, {
    headers: { 'Content-Type': 'application/json', ...(options.headers || {}) },
    ...options,
  });
  const json = await res.json().catch(() => ({ success: false, data: null }));
  return json;
}

export function get(path) {
  return request(path);
}

export function post(path, body, headers) {
  return request(path, { method: 'POST', body: JSON.stringify(body), headers });
}

export function put(path, body, headers) {
  return request(path, { method: 'PUT', body: JSON.stringify(body), headers });
}

export function del(path, headers) {
  return request(path, { method: 'DELETE', headers });
}

export { BASE };
