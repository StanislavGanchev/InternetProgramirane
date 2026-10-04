import { useState } from 'react'
import { api, ApiError } from '../api'
import AuthLayout from '../components/AuthLayout'
import Field from '../components/Field'
import FormErrors from '../components/FormErrors'

const EMPTY = { username: '', email: '', nickname: '', password: '', password_confirm: '' }

export default function RegisterPage({ onLogin, navigate }) {
  const [form, setForm] = useState(EMPTY)
  const [errors, setErrors] = useState({})
  const [busy, setBusy] = useState(false)

  const update = (event) => setForm({ ...form, [event.target.name]: event.target.value })

  async function submit(event) {
    event.preventDefault()
    if (form.password !== form.password_confirm) {
      setErrors({ password_confirm: ['Паролите не съвпадат.'] })
      return
    }
    setBusy(true)
    setErrors({})
    try {
      await api.register(form)
      // Registration does not start a session, so log in right away.
      const user = await api.login({ username: form.username, password: form.password })
      onLogin(user)
    } catch (error) {
      setErrors(error instanceof ApiError ? error.errors : { detail: ['Няма връзка със сървъра.'] })
    } finally {
      setBusy(false)
    }
  }

  return (
    <AuthLayout title="Регистрация" intro="Създай рицар и избери име, с което ще те виждат другите.">
      <form onSubmit={submit} noValidate>
        <FormErrors errors={errors} />
        <Field label="Потребителско име" name="username" autoComplete="username"
          value={form.username} onChange={update} errors={errors} required />
        <Field label="Имейл" name="email" type="email" autoComplete="email"
          value={form.email} onChange={update} errors={errors} required />
        <Field label="Прякор в играта" name="nickname" maxLength={30}
          value={form.nickname} onChange={update} errors={errors} required />
        <div className="field-row">
          <Field label="Парола" name="password" type="password" autoComplete="new-password"
            value={form.password} onChange={update} errors={errors} required />
          <Field label="Повтори паролата" name="password_confirm" type="password"
            autoComplete="new-password" value={form.password_confirm} onChange={update}
            errors={errors} required />
        </div>
        <button className="btn-primary" type="submit" disabled={busy}>
          {busy ? 'Създаване…' : 'Създай профил'}
        </button>
      </form>
      <p className="switch">
        Вече имаш профил?{' '}
        <a href="#/login" onClick={(e) => { e.preventDefault(); navigate('login') }}>
          Влез
        </a>
      </p>
    </AuthLayout>
  )
}
