/**
 * Text processing utilities for testimonial display.
 */

/**
 * Highlight @mentions in text by wrapping them in a styled span.
 * Accepts raw text or HTML strings — preserves existing markup.
 */
export function highlightMentions(text) {
  if (!text) return '';
  return text.replace(
    /@(\w+)/g,
    '<span class="mention">@$1</span>'
  );
}

/**
 * Truncate text to a maximum length, appending an ellipsis if needed.
 */
export function truncateText(text, maxLength = 200) {
  if (!text || text.length <= maxLength) return text;
  return text.slice(0, maxLength).trimEnd() + '…';
}

/**
 * Convert newlines to <br> tags for display in HTML contexts.
 */
export function nl2br(text) {
  if (!text) return '';
  return text.replace(/\n/g, '<br>');
}

/**
 * Build a preview snippet from user content.
 * Converts newlines, highlights mentions, then truncates.
 */
export function buildPreview(content, maxLength = 300) {
  let processed = nl2br(content);
  processed = highlightMentions(processed);
  return truncateText(processed, maxLength);
}
