export default function AuthLayout({ title, intro, children }) {
  return (
    <main className="auth">
      <aside className="banner" aria-hidden="true">
        <div className="banner-cloth">
          <p className="banner-name">Quiz Conquest</p>
          <p className="banner-motto">Знанието завладява земи.</p>
        </div>
      </aside>
      <section className="auth-panel">
        <h1>{title}</h1>
        {intro && <p className="lede">{intro}</p>}
        {children}
      </section>
    </main>
  )
}
