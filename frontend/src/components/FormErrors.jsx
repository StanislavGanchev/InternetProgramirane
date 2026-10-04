// Errors that are not tied to a single input (wrong credentials, server errors).
export default function FormErrors({ errors }) {
  const messages = [...(errors?.non_field_errors || []), ...(errors?.detail || [])]
  if (messages.length === 0) return null
  return (
    <div className="form-alert" role="alert">
      {messages.map((message) => (
        <p key={message}>{message}</p>
      ))}
    </div>
  )
}
