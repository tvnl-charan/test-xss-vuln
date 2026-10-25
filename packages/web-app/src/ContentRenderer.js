import { nl2br, highlightMentions } from './utils/textHelpers';

/**
 * Process raw user content into display-ready HTML.
 * Used by the testimonials detail view and the export page.
 */
export function renderUserContent(rawText, options = {}) {
  const { enableMentions = true, enableLineBreaks = true } = options;

  let html = rawText;
  if (enableLineBreaks) {
    html = nl2br(html);
  }
  if (enableMentions) {
    html = highlightMentions(html);
  }
  return html;
}

/**
 * Build a share-friendly text snippet from a testimonial.
 */
export function buildShareText(testimonial) {
  const quote = testimonial.content.length > 140
    ? testimonial.content.slice(0, 140) + '…'
    : testimonial.content;
  return `"${quote}" — ${testimonial.name}, ${testimonial.role}`;
}
