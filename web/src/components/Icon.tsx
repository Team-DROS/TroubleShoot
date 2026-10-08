type IconName =
  | 'arrow'
  | 'up-right'
  | 'check'
  | 'close'
  | 'play'
  | 'shield'
  | 'chip'
  | 'eye'
  | 'window'
  | 'terminal'
  | 'plus'
  | 'minus'
  | 'sound'
  | 'printer'
  | 'network'
  | 'stop'
  | 'refresh'
  | 'download'
  | 'menu'

const paths: Record<IconName, string> = {
  arrow: 'M4 12h15m-6-6 6 6-6 6',
  'up-right': 'M6 18 18 6M6 6h12v12',
  check: 'm5 12 4 4L19 6',
  close: 'm6 6 12 12M6 18 18 6',
  play: 'm9 5 11 7-11 7Z',
  shield: 'm12 3 8 3v6c0 5-8 9-8 9s-8-4-8-9V6Zm-4 9 3 3 5-6',
  chip: 'M7 7h10v10H7ZM9 3v4m6-4v4M9 17v4m6-4v4M3 9h4m-4 6h4m10-6h4m-4 6h4M10 10h4v4h-4Z',
  eye: 'M2 12s4-7 10-7 10 7 10 7-4 7-10 7S2 12 2 12Zm7 0a3 3 0 1 0 6 0 3 3 0 0 0-6 0',
  window: 'M3 4h18v16H3Zm0 5h18M7 6.5h.01m3 0h.01',
  terminal: 'M3 4h18v16H3Zm4 5 3 3-3 3m6 0h4',
  plus: 'M5 12h14M12 5v14',
  minus: 'M5 12h14',
  sound: 'M11 4 6 8H3v8h3l5 4Zm4 4a6 6 0 0 1 0 8m3-11a10 10 0 0 1 0 14',
  printer: 'M7 8V3h10v5M7 17H3V8h18v9h-4M7 13h10v8H7Zm10-2h.01',
  network: 'M3 8a14 14 0 0 1 18 0M6 12a9 9 0 0 1 12 0m-9 4a4 4 0 0 1 6 0m-3 4h.01',
  stop: 'M6 6h12v12H6Z',
  refresh: 'M20 8a8 8 0 0 0-14-3L3 8m0-5v5h5m-4 8a8 8 0 0 0 14 3l3-3m0 5v-5h-5',
  download: 'M12 3v12m-5-5 5 5 5-5M4 15v6h16v-6',
  menu: 'M4 7h16M4 12h16M4 17h16',
}

export function Icon({
  name,
  size = 20,
  className = '',
}: {
  name: IconName
  size?: number
  className?: string
}) {
  return (
    <svg
      className={className}
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.5"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
    >
      <path d={paths[name]} />
    </svg>
  )
}

export function Brand({ compact = false }: { compact?: boolean }) {
  return (
    <span className="brand">
      <span className="brand-symbol" aria-hidden="true">
        <i />
        <i />
        <i />
        <i />
      </span>
      {!compact && (
        <span>
          Trouble<span className="brand-light">Shoot</span>
          <span className="brand-period">.</span>
        </span>
      )}
    </span>
  )
}
