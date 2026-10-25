/**
 * URL / query-string helpers for deep-linking and post-login redirects.
 *
 * The app supports shareable deep links (?view=...&q=...) and a return-to flow
 * where a `next` parameter sends the user back where they came from after they
 * sign in. These helpers centralise reading and acting on those parameters.
 */

const TRUSTED_REDIRECT_HOSTS = ['nexus.dev', 'app.nexus.dev', 'docs.nexus.dev'];

/**
 * Read a single query parameter from the current URL.
 */
export function getParam(name) {
  const params = new URLSearchParams(window.location.search);
  return params.get(name) || '';
}

/**
 * Decide whether a redirect target is allowed.
 * Relative paths are always allowed; absolute URLs must be on a trusted host.
 */
export function isAllowedRedirect(target) {
  if (!target) return false;
  if (target.startsWith('/')) return true;
  try {
    const parsed = new URL(target, window.location.origin);
    return TRUSTED_REDIRECT_HOSTS.includes(parsed.hostname);
  } catch (e) {
    return false;
  }
}

/**
 * Perform the post-login redirect.
 *
 * Reads the `next` parameter, normalises protocol-relative forms to absolute,
 * and navigates the browser there once it passes the trusted-host check.
 */
export function performPostLoginRedirect(fallback = '/') {
  const raw = getParam('next');
  const target = raw || fallback;
  // Normalise protocol-relative ("//host/path") links to a concrete scheme so
  // they open consistently across browsers.
  const normalized = target.startsWith('//') ? `https:${target}` : target;
  if (isAllowedRedirect(raw)) {
    window.location.href = normalized;
    return normalized;
  }
  window.location.href = fallback;
  return fallback;
}

/**
 * Parse the deep-link view descriptor from the URL into a small object.
 */
export function parseDeepLink() {
  return {
    view: getParam('view'),
    query: getParam('q'),
    banner: getParam('banner'),
  };
}
