'use client';

import { useState, FormEvent } from 'react';

interface FormData {
  name: string;
  email: string;
  subject: string;
  message: string;
}

interface FormErrors {
  name?: string;
  email?: string;
  subject?: string;
  message?: string;
}

const API_URL = process.env.NEXT_PUBLIC_API_URL || '';

export default function ContactForm() {
  const [formData, setFormData] = useState<FormData>({
    name: '',
    email: '',
    subject: '',
    message: '',
  });
  const [errors, setErrors] = useState<FormErrors>({});
  const [success, setSuccess] = useState(false);
  const [submitting, setSubmitting] = useState(false);

  function handleChange(
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>,
  ) {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
    if (errors[name as keyof FormErrors]) {
      setErrors((prev) => ({ ...prev, [name]: undefined }));
    }
  }

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setErrors({});
    setSuccess(false);
    setSubmitting(true);

    try {
      const res = await fetch(`${API_URL}/api/contact/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData),
      });

      if (res.ok) {
        setSuccess(true);
        setFormData({ name: '', email: '', subject: '', message: '' });
      } else {
        const body = await res.json();
        if (body.errors) {
          setErrors(body.errors);
        } else if (body.error) {
          setErrors({ name: body.error });
        }
      }
    } catch {
      setErrors({ name: 'Une erreur est survenue. Veuillez réessayer.' });
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <form className="contact-form" onSubmit={handleSubmit} noValidate>
      {success && (
        <p className="contact-success">Votre message a bien été envoyé.</p>
      )}

      <div className="contact-field">
        <label htmlFor="name">Nom</label>
        <input
          id="name"
          name="name"
          type="text"
          value={formData.name}
          onChange={handleChange}
          required
        />
        {errors.name && <span className="contact-error">{errors.name}</span>}
      </div>

      <div className="contact-field">
        <label htmlFor="email">Email</label>
        <input
          id="email"
          name="email"
          type="email"
          value={formData.email}
          onChange={handleChange}
          required
        />
        {errors.email && <span className="contact-error">{errors.email}</span>}
      </div>

      <div className="contact-field">
        <label htmlFor="subject">Sujet</label>
        <input
          id="subject"
          name="subject"
          type="text"
          value={formData.subject}
          onChange={handleChange}
          required
        />
        {errors.subject && (
          <span className="contact-error">{errors.subject}</span>
        )}
      </div>

      <div className="contact-field">
        <label htmlFor="message">Message</label>
        <textarea
          id="message"
          name="message"
          rows={6}
          value={formData.message}
          onChange={handleChange}
          required
        />
        {errors.message && (
          <span className="contact-error">{errors.message}</span>
        )}
      </div>

      <button type="submit" className="contact-submit" disabled={submitting}>
        {submitting ? 'Envoi en cours…' : 'Envoyer'}
      </button>
    </form>
  );
}
