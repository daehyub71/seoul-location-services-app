import { Map, List } from 'lucide-react'
import { motion } from 'framer-motion'

export type ViewMode = 'map' | 'list'

interface ViewModeToggleProps {
  mode: ViewMode
  onChange: (mode: ViewMode) => void
  className?: string
}

export default function ViewModeToggle({ mode, onChange, className = '' }: ViewModeToggleProps) {
  return (
    <div
      className={`
        inline-flex items-center bg-white rounded-full shadow-lg p-1 gap-1
        ${className}
      `}
    >
      <button
        onClick={() => onChange('map')}
        className={`
          relative px-4 py-2 rounded-full text-sm font-medium transition-all
          flex items-center gap-2
          ${mode === 'map' ? 'text-white' : 'text-gray-600 hover:text-gray-900'}
        `}
      >
        {mode === 'map' && (
          <motion.div
            layoutId="activeTab"
            className="absolute inset-0 bg-blue-600 rounded-full"
            transition={{ type: 'spring', duration: 0.5 }}
          />
        )}
        <Map className={`h-4 w-4 relative z-10`} />
        <span className="relative z-10">지도</span>
      </button>

      <button
        onClick={() => onChange('list')}
        className={`
          relative px-4 py-2 rounded-full text-sm font-medium transition-all
          flex items-center gap-2
          ${mode === 'list' ? 'text-white' : 'text-gray-600 hover:text-gray-900'}
        `}
      >
        {mode === 'list' && (
          <motion.div
            layoutId="activeTab"
            className="absolute inset-0 bg-blue-600 rounded-full"
            transition={{ type: 'spring', duration: 0.5 }}
          />
        )}
        <List className={`h-4 w-4 relative z-10`} />
        <span className="relative z-10">리스트</span>
      </button>
    </div>
  )
}
