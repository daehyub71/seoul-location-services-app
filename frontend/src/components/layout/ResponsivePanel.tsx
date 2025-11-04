import { useState, useEffect } from 'react'
import { motion, AnimatePresence, PanInfo } from 'framer-motion'
import { ChevronDown, ChevronUp, X } from 'lucide-react'

export interface ResponsivePanelProps {
  children: React.ReactNode
  title?: string
  isOpen?: boolean
  onClose?: () => void
  className?: string
}

export default function ResponsivePanel({
  children,
  title = 'Panel',
  isOpen = true,
  onClose,
  className = '',
}: ResponsivePanelProps) {
  const [isMobile, setIsMobile] = useState(false)
  const [sheetHeight, setSheetHeight] = useState<'collapsed' | 'half' | 'full'>('half')
  const [isDragging, setIsDragging] = useState(false)

  // Detect mobile view
  useEffect(() => {
    const checkMobile = () => {
      setIsMobile(window.innerWidth < 768)
    }

    checkMobile()
    window.addEventListener('resize', checkMobile)
    return () => window.removeEventListener('resize', checkMobile)
  }, [])

  // Handle drag end for mobile sheet
  const handleDragEnd = (_: any, info: PanInfo) => {
    setIsDragging(false)
    const velocity = info.velocity.y
    const offset = info.offset.y

    // Determine new height based on drag direction and velocity
    if (velocity > 500 || offset > 150) {
      // Dragging down
      if (sheetHeight === 'full') {
        setSheetHeight('half')
      } else if (sheetHeight === 'half') {
        setSheetHeight('collapsed')
      }
    } else if (velocity < -500 || offset < -150) {
      // Dragging up
      if (sheetHeight === 'collapsed') {
        setSheetHeight('half')
      } else if (sheetHeight === 'half') {
        setSheetHeight('full')
      }
    }
  }

  const getSheetHeightClass = () => {
    switch (sheetHeight) {
      case 'collapsed':
        return 'h-16'
      case 'half':
        return 'h-[50vh]'
      case 'full':
        return 'h-[85vh]'
      default:
        return 'h-[50vh]'
    }
  }

  if (!isOpen) return null

  // Desktop: Sidebar
  if (!isMobile) {
    return (
      <motion.aside
        initial={{ x: -320 }}
        animate={{ x: 0 }}
        exit={{ x: -320 }}
        transition={{ type: 'spring', damping: 25, stiffness: 200 }}
        className={`
          fixed left-0 top-16 bottom-0 w-80 bg-white border-r shadow-lg z-30
          flex flex-col
          ${className}
        `}
      >
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b bg-gray-50">
          <h2 className="text-lg font-bold text-gray-900">{title}</h2>
          {onClose && (
            <button
              onClick={onClose}
              className="p-1 hover:bg-gray-200 rounded transition-colors"
              aria-label="Close panel"
            >
              <X className="h-5 w-5 text-gray-600" />
            </button>
          )}
        </div>

        {/* Content */}
        <div className="flex-1 overflow-hidden">{children}</div>
      </motion.aside>
    )
  }

  // Mobile: Bottom Sheet
  return (
    <AnimatePresence>
      <motion.div
        initial={{ y: '100%' }}
        animate={{ y: 0 }}
        exit={{ y: '100%' }}
        transition={{ type: 'spring', damping: 30, stiffness: 300 }}
        drag="y"
        dragConstraints={{ top: 0, bottom: 0 }}
        dragElastic={0.2}
        onDragStart={() => setIsDragging(true)}
        onDragEnd={handleDragEnd}
        className={`
          fixed bottom-0 left-0 right-0 bg-white rounded-t-2xl shadow-2xl z-40
          flex flex-col transition-all duration-300
          ${getSheetHeightClass()}
          ${isDragging ? 'cursor-grabbing' : 'cursor-grab'}
          ${className}
        `}
        style={{
          touchAction: 'none',
        }}
      >
        {/* Drag Handle */}
        <div className="flex-shrink-0 py-2 px-4 border-b bg-gray-50 rounded-t-2xl">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3 flex-1">
              <div className="w-12 h-1 bg-gray-300 rounded-full" />
              <span className="text-sm font-semibold text-gray-700">{title}</span>
            </div>

            <div className="flex items-center gap-1">
              {sheetHeight !== 'collapsed' && (
                <button
                  onClick={() =>
                    setSheetHeight(sheetHeight === 'full' ? 'half' : 'collapsed')
                  }
                  className="p-1.5 hover:bg-gray-200 rounded transition-colors"
                  aria-label="Collapse sheet"
                >
                  <ChevronDown className="h-4 w-4 text-gray-600" />
                </button>
              )}
              {sheetHeight !== 'full' && (
                <button
                  onClick={() => setSheetHeight(sheetHeight === 'collapsed' ? 'half' : 'full')}
                  className="p-1.5 hover:bg-gray-200 rounded transition-colors"
                  aria-label="Expand sheet"
                >
                  <ChevronUp className="h-4 w-4 text-gray-600" />
                </button>
              )}
              {onClose && (
                <button
                  onClick={onClose}
                  className="p-1.5 hover:bg-gray-200 rounded transition-colors"
                  aria-label="Close panel"
                >
                  <X className="h-4 w-4 text-gray-600" />
                </button>
              )}
            </div>
          </div>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-hidden">
          {sheetHeight !== 'collapsed' && children}
        </div>
      </motion.div>
    </AnimatePresence>
  )
}
