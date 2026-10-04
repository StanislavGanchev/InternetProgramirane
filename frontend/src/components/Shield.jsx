// Four heraldic shields used as avatars. Keys match Profile.avatar_key.
export const AVATARS = [
  { key: 'knight-1', label: 'Златен лъв', field: '#1B2A4A', charge: '#D4A72C', pattern: 'pale' },
  { key: 'knight-2', label: 'Червена кула', field: '#F2F4F7', charge: '#A3262A', pattern: 'chevron' },
  { key: 'knight-3', label: 'Сребърен път', field: '#2F5D50', charge: '#F2F4F7', pattern: 'bend' },
  { key: 'knight-4', label: 'Нощен пазач', field: '#A3262A', charge: '#1B2A4A', pattern: 'cross' },
]

const OUTLINE = 'M6 4h52v26c0 17-11.5 27-26 32C17.5 57 6 47 6 30z'

function Charge({ pattern, color }) {
  switch (pattern) {
    case 'pale':
      return <rect x="24" y="4" width="16" height="60" fill={color} />
    case 'chevron':
      return <path d="M6 44 32 18l26 26v12L32 30 6 56z" fill={color} />
    case 'bend':
      return <path d="M6 4h12l40 40v14z" fill={color} />
    case 'cross':
      return (
        <g fill={color}>
          <rect x="27" y="4" width="10" height="60" />
          <rect x="6" y="22" width="52" height="10" />
        </g>
      )
    default:
      return null
  }
}

export default function Shield({ avatarKey, size = 64, title }) {
  const avatar = AVATARS.find((item) => item.key === avatarKey) || AVATARS[0]
  const clipId = `clip-${avatar.key}`
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 64 64"
      role="img"
      aria-label={title || avatar.label}
    >
      <defs>
        <clipPath id={clipId}>
          <path d={OUTLINE} />
        </clipPath>
      </defs>
      <g clipPath={`url(#${clipId})`}>
        <rect width="64" height="64" fill={avatar.field} />
        <Charge pattern={avatar.pattern} color={avatar.charge} />
      </g>
      <path d={OUTLINE} fill="none" stroke="#2B3445" strokeWidth="2.5" />
    </svg>
  )
}
