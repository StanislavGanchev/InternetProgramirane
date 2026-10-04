import { useState } from 'react'
import { api, ApiError } from '../api'
import AuthLayout from '../components/AuthLayout'
import Field from '../components/Field'
import FormErrors from '../components/FormErrors'

export default function LoginPage({ onLogin, navigate }) {
  const [form, setForm] = useState({ username: '', password: '' })
  const [errors, setErrors] = useState({})
  const [busy, setBusy] = useState(false)

  const update = (event) => setForm({ ...form, [event.target.name]: event.target.value })

  async function submit(event) {
    event.preventDefault()
    setBusy(true)
    setErrors({})
    try {
      const user = await api.login(form)
      onLogin(user)
    } catch (error) {
      setErrors(error instanceof ApiError ? error.errors : { detail: ['Няма връзка със сървъра.'] })
    } finally {
      setBusy(false)
    }
  }

  return (
    <AuthLayout title="Вход" intro="Влез, за да продължиш завоеванието си.">
      <form onSubmit={submit} noValidate>
        <FormErrors errors={errors} />
        <Field
          label="Потребителско име"
          name="username"
          autoComplete="username"
          value={form.username}
          onChange={update}
          errors={errors}
          required
        />
        <Field
          label="Парола"
          name="password"
          type="password"
          autoComplete="current-password"
          value={form.password}
          onChange={update}
          errors={errors}
          required
        />
        <button className="btn-primary" type="submit" disabled={busy}>
          {busy ? 'Влизане…' : 'Влез'}
        </button>
      </form>
      <p className="switch">
        Нямаш профил?{' '}
        <a href="#/register" onClick={(e) => { e.preventDefault(); navigate('register') }}>
          Регистрирай се
        </a>
      </p>
    </AuthLayout>
  )
}
