export default function Home() {
  return (
    <main style={{ fontFamily: 'system-ui, sans-serif', padding: '2rem' }}>
      <h1>Hello, World!</h1>
      <p>Bienvenue sur <strong>culturall-website</strong> — Next.js 14 + Django/Wagtail.</p>
      <p>
        Backend : <a href="http://localhost:8000/">localhost:8000</a> ·{' '}
        <a href="http://localhost:8000/admin/">Wagtail admin</a>
      </p>
    </main>
  );
}
