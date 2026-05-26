interface MaterialIconProps {
  name: string
  className?: string
  size?: number
  weight?: number
}

/** Google Material Symbols ikonunu render eder. */
export function MaterialIcon({ name, className = '', size, weight }: MaterialIconProps) {
  const variation =
    weight != null
      ? `'FILL' 0, 'wght' ${weight}, 'GRAD' 0, 'opsz' 24`
      : undefined

  return (
    <span
      className={`material-symbols-outlined ${className}`}
      style={{
        ...(size ? { fontSize: size } : {}),
        ...(variation ? { fontVariationSettings: variation } : {}),
      }}
      aria-hidden
    >
      {name}
    </span>
  )
}
