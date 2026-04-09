import type { Metadata } from 'next';
import ContactForm from './ContactForm';

export const metadata: Metadata = {
  title: 'Contact',
};

export default function Contact() {
  return (
    <main className="page">
      <h1>Contact</h1>
      <p>
        Pour toute question ou proposition, n&apos;hésitez pas à nous contacter.
      </p>
      <ContactForm />
    </main>
  );
}
