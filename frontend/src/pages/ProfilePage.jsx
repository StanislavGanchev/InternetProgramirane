import { useState } from 'react'
import { api, ApiError } from '../api'
import Field from '../components/Field'
import FormErrors from '../components/FormErrors'
import Shield, { AVATARS } from '../components/Shield'

export default function ProfilePage({ user, onUserChange, onLogout }) {
  const [nickname, setNickname] = useState(user.profile.nickname)
  const [avatarKey, setAvatarKey] = useState(user.profile.avatar_key)
  const [errors, setErrors] = useState({})
  const [saved, setSaved] = useState(false)
  const [busy, setBusy] = useState(false)

  const dirty = nickname !== user.profile.nickname || avatarKey !== user.profile.avatar_key

  async function save(event) {
    event.preventDefault()
    setBusy(true)
    setErrors({})
    setSaved(false)
    try {
      const updated = await api.updateMe({ nickname, avatar_key: avatarKey })
      onUserChange(updated)
      setSaved(true)
    } catch (error) {
      setErrors(error instanceof ApiError ? error.errors : { detail: ['Няма връзка със сървъра.'] })
    } finally {
      setBusy(false)
    }
  }

  return (
    <main className="profile">
      <header className="topbar">
        <span className="topbar-name">Quiz Conquest</span>
        <button className="btn-quiet" type="button" onClick={onLogout}>
          Изход
        </button>
      </header>

      <section className="profile-hero">
        <Shield avatarKey={user.profile.avatar_key} size={120} />
        <div>
          <h1>{user.profile.nickname}</h1>
          <dl className="facts">
            <div><dt>Потребител</dt><dd>{user.username}</dd></div>
            <div><dt>Имейл</dt><dd>{user.email}</dd></div>
          </dl>
        </div>
      </section>

      <form className="profile-form" onSubmit={save} noValidate>
        <h2>Редактирай профила</h2>
        <FormErrors errors={errors} />
        <Field
          label="Прякор"
          name="nickname"
          maxLength={30}
          value={nickname}
          onChange={(e) => { setNickname(e.target.value); setSaved(false) }}
          errors={errors}
        />

        <fieldset className="avatars">
          <legend>Герб</legend>
          {AVATARS.map((avatar) => (
            <label key={avatar.key} className="avatar-option">
              <input
                type="radio"
                name="avatar_key"
                value={avatar.key}
                checked={avatarKey === avatar.key}
                onChange={() => { setAvatarKey(avatar.key); setSaved(false) }}
              />
              <Shield avatarKey={avatar.key} size={72} />
              <span>{avatar.label}</span>
            </label>
          ))}
          {errors.avatar_key && <span className="field-error">{errors.avatar_key.join(' ')}</span>}
        </fieldset>

        <div className="actions">
          <button className="btn-primary" type="submit" disabled={busy || !dirty}>
            {busy ? 'Запазване…' : 'Запази промените'}
          </button>
          {saved && <span className="saved" role="status">Промените са запазени.</span>}
        </div>
      </form>
    </main>
  )
}
