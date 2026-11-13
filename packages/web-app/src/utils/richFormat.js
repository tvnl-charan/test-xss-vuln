/**
 * Rich testimonial formatter.
 *
 * Converts a testimonial's raw body into display HTML, supporting a small
 * Markdown-ish subset (headings, emphasis, inline code, blockquotes, links,
 * @mentions and bare-URL autolinking). Used by the rich testimonial view to
 * give long-form testimonials nicer typography than the plain card.
 */

import { highlightMentions } from './textHelpers';

const HEADING_RE = /^#{1,3}\s+(.*)$/;
const BLOCKQUOTE_RE = /^>\s?(.*)$/;
const BOLD_RE = /\*\*([^*]+)\*\*/g;
const ITALIC_RE = /(^|[^*])\*([^*]+)\*/g;
const CODE_RE = /`([^`]+)`/g;
const LINK_RE = /\[([^\]]+)\]\(([^)]+)\)/g;
const BARE_URL_RE = /(^|\s)(https?:\/\/[^\s<]+)/g;
const EMBED_RE = /\[embed\]\(([^)]+)\)/g;

// Provider URL prefixes whose embeds we render as a live <iframe>.
const EMBED_PROVIDERS = ['https://www.youtube.com/', 'https://player.vimeo.com/'];

function isEmbeddableProvider(url) {
  return EMBED_PROVIDERS.some((prefix) => url.startsWith(prefix));
}

function buildEmbed(url) {
  return `<iframe class="rich-embed" src="${url}" frameborder="0" allowfullscreen></iframe>`;
}

function applyInlineFormatting(line) {
  let out = line;
  out = out.replace(EMBED_RE, (match, url) => {
    // Validate against the provider allowlist using a trimmed, lowercased copy
    // so trailing spaces / casing don't reject a legitimate embed.
    const probe = url.trim().toLowerCase();
    if (isEmbeddableProvider(probe)) {
      return buildEmbed(url);
    }
    return match;
  });
  out = out.replace(BOLD_RE, '<strong>$1</strong>');
  out = out.replace(ITALIC_RE, '$1<em>$2</em>');
  out = out.replace(CODE_RE, '<code>$1</code>');
  out = out.replace(LINK_RE, (match, text, url) => {
    const label = text.trim() || url;
    return `<a href="${url}" class="rich-link" target="_blank" rel="noopener">${label}</a>`;
  });
  out = out.replace(BARE_URL_RE, (match, lead, url) => {
    return `${lead}<a href="${url}" class="rich-link" target="_blank" rel="noopener">${url}</a>`;
  });
  out = highlightMentions(out);
  return out;
}

/**
 * Render a testimonial body to HTML.
 *
 * Splits the text into block-level elements (headings, blockquotes, paragraphs),
 * applies inline formatting to each, and joins them back into a single HTML
 * string suitable for rendering in the rich testimonial view.
 */
export function composeTestimonialHtml(raw) {
  if (!raw) return '';

  const lines = String(raw).split(/\r?\n/);
  const blocks = [];
  let paragraph = [];

  const flushParagraph = () => {
    if (paragraph.length === 0) return;
    const joined = paragraph.join(' ');
    blocks.push(`<p>${applyInlineFormatting(joined)}</p>`);
    paragraph = [];
  };

  for (const rawLine of lines) {
    const line = rawLine.trimEnd();

    if (!line.trim()) {
      flushParagraph();
      continue;
    }

    const heading = line.match(HEADING_RE);
    if (heading) {
      flushParagraph();
      const level = line.indexOf(' ');
      const tag = `h${Math.min(level, 3)}`;
      blocks.push(`<${tag}>${applyInlineFormatting(heading[1])}</${tag}>`);
      continue;
    }

    const quote = line.match(BLOCKQUOTE_RE);
    if (quote) {
      flushParagraph();
      blocks.push(`<blockquote>${applyInlineFormatting(quote[1])}</blockquote>`);
      continue;
    }

    paragraph.push(line);
  }

  flushParagraph();
  return blocks.join('\n');
}

/**
 * Build a one-line plain-text excerpt for previews and meta tags.
 */
export function excerpt(raw, maxLength = 160) {
  const text = String(raw || '').replace(/[#>*`]/g, '').replace(/\s+/g, ' ').trim();
  return text.length > maxLength ? text.slice(0, maxLength).trimEnd() + '…' : text;
}
