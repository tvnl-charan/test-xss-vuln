import React, { useState, useEffect, useCallback } from 'react';
import { highlightMentions } from '../utils/textHelpers';
import './Testimonials.css';

const API = 'http://localhost:8000/api/v1/testimonials';

function TestimonialCard({ testimonial }) {
  const displayContent = testimonial.content_html || testimonial.content;
  const highlighted = highlightMentions(displayContent);

  return (
    <div className="card testimonial-card">
      <div className="testimonial-stars"
        dangerouslySetInnerHTML={{ __html: testimonial.rating_html || '' }}
      />
      <div
        className="testimonial-content"
        dangerouslySetInnerHTML={{ __html: highlighted }}
      />
      <div className="testimonial-author">
        <div className="testimonial-avatar">
          {testimonial.name.split(' ').map(w => w[0]).join('').slice(0, 2).toUpperCase()}
        </div>
        <div>
          <div className="testimonial-name">{testimonial.name}</div>
          <div className="testimonial-role">{testimonial.role}</div>
        </div>
      </div>
    </div>
  );
}

function SearchBar({ value, onChange }) {
  return (
    <div className="search-bar">
      <input
        type="text"
        placeholder="Search testimonials..."
        value={value}
        onChange={(e) => onChange(e.target.value)}
      />
    </div>
  );
}

function Testimonials() {
  const [testimonials, setTestimonials] = useState([]);
  const [form, setForm] = useState({ name: '', role: '', content: '', rating: 5 });
  const [submitted, setSubmitted] = useState(false);
  const [errors, setErrors] = useState({});
  const [searchQuery, setSearchQuery] = useState('');

  const fetchTestimonials = useCallback(() => {
    fetch(`${API}?format=html`)
      .then(res => res.json())
      .then(json => {
        if (json.success) setTestimonials(json.data);
      })
      .catch(() => {});
  }, []);

  useEffect(() => { fetchTestimonials(); }, [fetchTestimonials]);

  const filteredTestimonials = testimonials.filter(t => {
    if (!searchQuery.trim()) return true;
    const q = searchQuery.toLowerCase();
    return (
      t.name.toLowerCase().includes(q) ||
      t.role.toLowerCase().includes(q) ||
      t.content.toLowerCase().includes(q)
    );
  });

  const validate = () => {
    const e = {};
    if (!form.name.trim()) e.name = 'Name is required.';
    if (!form.role.trim()) e.role = 'Role is required.';
    if (!form.content.trim()) e.content = 'Testimonial is required.';
    if (form.rating < 1 || form.rating > 5) e.rating = 'Rating must be 1–5.';
    return e;
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setForm(prev => ({ ...prev, [name]: name === 'rating' ? parseInt(value, 10) : value }));
    if (errors[name]) setErrors(prev => ({ ...prev, [name]: undefined }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const errs = validate();
    if (Object.keys(errs).length > 0) { setErrors(errs); return; }

    try {
      const res = await fetch(API, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(form),
      });
      if (res.ok) {
        setSubmitted(true);
        setForm({ name: '', role: '', content: '', rating: 5 });
        fetchTestimonials();
      }
    } catch {
      // ignore
    }
  };

  return (
    <div className="testimonials">
      {/* ── Hero ──────────────────────────── */}
      <section className="page-hero">
        <div className="page-hero-bg" />
        <div className="container">
          <div className="badge">Testimonials</div>
          <h1 className="section-title">
            What Our <span className="gradient-text">Clients Say</span>
          </h1>
          <p className="section-desc">
            Real feedback from the teams we've worked with.
          </p>
        </div>
      </section>

      {/* ── Search + Testimonial cards ────── */}
      <section className="section">
        <div className="container">
          <SearchBar value={searchQuery} onChange={setSearchQuery} />

          {filteredTestimonials.length === 0 ? (
            <p className="empty-state">
              {searchQuery ? 'No testimonials match your search.' : 'No testimonials yet. Be the first to share your experience!'}
            </p>
          ) : (
            <div className="grid-2">
              {filteredTestimonials.map((t) => (
                <TestimonialCard key={t.id} testimonial={t} />
              ))}
            </div>
          )}
        </div>
      </section>

      {/* ── Submit form ──────────────────── */}
      <section className="section" style={{ paddingTop: 0 }}>
        <div className="container testimonial-form-wrapper">
          <div className="section-label">Share Your Experience</div>
          <h2 className="section-title">Leave a Testimonial</h2>
          <div className="divider" />

          {submitted ? (
            <div className="card success-card">
              <div className="success-icon">✓</div>
              <h3>Thank you!</h3>
              <p>Your testimonial has been submitted.</p>
              <button
                className="btn btn-outline"
                style={{ marginTop: 24 }}
                onClick={() => setSubmitted(false)}
              >
                Submit another
              </button>
            </div>
          ) : (
            <form className="contact-form" onSubmit={handleSubmit} noValidate>
              <div className="form-row">
                <Field label="Name" error={errors.name}>
                  <input
                    type="text"
                    name="name"
                    placeholder="Your name"
                    value={form.name}
                    onChange={handleChange}
                    className={errors.name ? 'has-error' : ''}
                  />
                </Field>
                <Field label="Role / Company" error={errors.role}>
                  <input
                    type="text"
                    name="role"
                    placeholder="e.g. CTO at Acme Inc."
                    value={form.role}
                    onChange={handleChange}
                    className={errors.role ? 'has-error' : ''}
                  />
                </Field>
              </div>

              <div className="form-row">
                <Field label="Your Testimonial" error={errors.content}>
                  <textarea
                    name="content"
                    rows="5"
                    placeholder="Tell us about your experience working with Nexus..."
                    value={form.content}
                    onChange={handleChange}
                    className={errors.content ? 'has-error' : ''}
                  />
                </Field>
              </div>

              <Field label="Rating" error={errors.rating}>
                <select name="rating" value={form.rating} onChange={handleChange}>
                  <option value={5}>★★★★★ (5)</option>
                  <option value={4}>★★★★☆ (4)</option>
                  <option value={3}>★★★☆☆ (3)</option>
                  <option value={2}>★★☆☆☆ (2)</option>
                  <option value={1}>★☆☆☆☆ (1)</option>
                </select>
              </Field>

              <button type="submit" className="btn btn-primary btn-full">
                Submit Testimonial
              </button>
            </form>
          )}
        </div>
      </section>
    </div>
  );
}

function Field({ label, error, children }) {
  return (
    <div className="form-group">
      <label>{label}</label>
      {children}
      {error && <span className="field-error">{error}</span>}
    </div>
  );
}

export default Testimonials;
