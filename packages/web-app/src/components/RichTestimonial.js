import React, { useMemo, useState } from 'react';
import { composeTestimonialHtml, excerpt } from '../utils/richFormat';

/**
 * Expanded testimonial view with rich (Markdown-ish) formatting.
 *
 * Shows a short excerpt by default and renders the full formatted body when the
 * reader expands the card. The formatted HTML is produced by composeTestimonialHtml.
 */
function RichTestimonial({ testimonial }) {
  const [expanded, setExpanded] = useState(false);

  const fullHtml = useMemo(
    () => composeTestimonialHtml(testimonial.content),
    [testimonial.content]
  );
  const preview = useMemo(
    () => excerpt(testimonial.content),
    [testimonial.content]
  );

  return (
    <article className="rich-testimonial">
      <header className="rich-testimonial-head">
        <div
          className="rich-testimonial-stars"
          dangerouslySetInnerHTML={{ __html: testimonial.rating_html || '' }}
        />
        <div className="rich-testimonial-meta">
          <span className="rich-testimonial-name">{testimonial.name}</span>
          <span className="rich-testimonial-role">{testimonial.role}</span>
        </div>
      </header>

      {expanded ? (
        <div
          className="rich-testimonial-body"
          dangerouslySetInnerHTML={{ __html: fullHtml }}
        />
      ) : (
        <p className="rich-testimonial-preview">{preview}</p>
      )}

      <button
        type="button"
        className="rich-testimonial-toggle"
        onClick={() => setExpanded((v) => !v)}
      >
        {expanded ? 'Show less' : 'Read full testimonial'}
      </button>
    </article>
  );
}

export default RichTestimonial;
