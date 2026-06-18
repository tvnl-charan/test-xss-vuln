import React, { useState, useEffect } from 'react';
import './Testimonials.css';

const API = 'http://localhost:8000/api/v1/testimonials';

function Testimonials() {
  const [testimonials, setTestimonials] = useState([]);
  const [form, setForm] = useState({ name: '', role: '', content: '' });
  const [submitted, setSubmitted] = useState(false);
  const [errors, setErrors] = useState({});

  const fetchTestimonials = () => {
    fetch(API)
      .then(res => res.json())
      .then(json => {
        if (json.success) setTestimonials(json.data);
      })
      .catch(() => {});
  };

  useEffect(() => { fetchTestimonials(); }, []);

  const validate = () => {
    const e = {};
    if (!form.name.trim()) e.name = 'Name is required.';
    if (!form.role.trim()) e.role = 'Role is required.';
    if (!form.content.trim()) e.content = 'Testimonial is required.';
    return e;
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setForm(prev => ({ ...prev, [name]: value }));
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
        setForm({ name: '', role: '', content: '' });
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

      {/* ── Testimonial cards ─────────────── */}
      <section className="section">
        <div className="container">
          {testimonials.length === 0 ? (
            <p className="empty-state">No testimonials yet. Be the first to share your experience!</p>
          ) : (
            <div className="grid-2">
              {testimonials.map((t) => (
                <div className="card testimonial-card" key={t.id}>
                  <div
                    className="testimonial-content"
                    dangerouslySetInnerHTML={{ __html: t.content }}
                  />
                  <div className="testimonial-author">
                    <div className="testimonial-avatar">
                      {t.name.split(' ').map(w => w[0]).join('').slice(0, 2).toUpperCase()}
                    </div>
                    <div>
                      <div className="testimonial-name">{t.name}</div>
                      <div className="testimonial-role">{t.role}</div>
                    </div>
                  </div>
                </div>
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
