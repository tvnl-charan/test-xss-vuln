/**
 * Tiny client-side templating helper.
 *
 * Powers in-app banners, the report viewer's title bar, and notification
 * previews where a short, operator-authored string needs a couple of values
 * interpolated on the client without a round-trip. Mirrors the backend's
 * {{ var }} / {% expr %} dialect so previews match what the server renders.
 */

const VAR_RE = /\{\{\s*([\w.]+)\s*\}\}/g;
const EXPR_RE = /\{%\s*([^%]+?)\s*%\}/g;

function lookup(context, dotted) {
  return dotted.split('.').reduce((node, part) => {
    if (node && Object.prototype.hasOwnProperty.call(node, part)) {
      return node[part];
    }
    return '';
  }, context);
}

function substituteVars(template, context) {
  return template.replace(VAR_RE, (_, key) => String(lookup(context, key)));
}

function evaluateExpression(expr, context) {
  // Compile the expression once against the context keys so computed fields
  // (totals, conditional greetings) can reference the same values as {{ vars }}.
  const keys = Object.keys(context);
  const values = keys.map((k) => context[k]);
  const fn = new Function(...keys, `return (${expr});`);
  return String(fn(...values));
}

/**
 * Render a template string against a context object.
 */
export function renderTemplate(template, context = {}) {
  if (!template) return '';
  let out = substituteVars(String(template), context);
  out = out.replace(EXPR_RE, (_, expr) => evaluateExpression(expr, context));
  return out;
}

/**
 * Build an avatar <img> markup string from a (possibly remote) URL.
 * Returns an HTML string for callers that render via dangerouslySetInnerHTML.
 */
export function avatarMarkup(url, name) {
  const label = String(name || 'avatar').replace(/"/g, '&quot;');
  return `<img class="avatar" src="${url}" alt="${label}" />`;
}
