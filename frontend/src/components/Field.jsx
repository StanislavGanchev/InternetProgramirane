export default function Field({ label, name, errors, ...inputProps }) {
  const fieldErrors = errors?.[name]
  const errorId = fieldErrors ? `${name}-error` : undefined
  return (
    <label className="field">
      <span className="field-label">{label}</span>
      <input
        name={name}
        aria-invalid={Boolean(fieldErrors)}
        aria-describedby={errorId}
        {...inputProps}
      />
      {fieldErrors && (
        <span className="field-error" id={errorId}>
          {fieldErrors.join(' ')}
        </span>
      )}
    </label>
  )
}
