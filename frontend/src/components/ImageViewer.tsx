import { useState, useEffect, useRef } from 'react'
import { motion, AnimatePresence, useMotionValue, useTransform } from 'framer-motion'

interface ImageViewerProps {
  initialZoom?: number
  initialPosition?: { x: number; y: number }
}

export const ImageViewer: React.FC<ImageViewerProps> = ({ 
  initialZoom = 1,
  initialPosition = { x: 0, y: 0 }
}) => {
  const [scale, setScale] = useState(initialZoom)
  const [position, setPosition] = useState(initialPosition)
  const containerRef = useRef<HTMLDivElement>(null)
  
  const x = useMotionValue(position.x)
  const y = useMotionValue(position.y)
  
  // Update URL parameters when position or zoom changes
  useEffect(() => {
    const params = new URLSearchParams(window.location.search)
    params.set('pos', `${position.x.toFixed(2)},${position.y.toFixed(2)},${scale.toFixed(4)}`)
    window.history.replaceState({}, '', `?${params.toString()}`)
  }, [position, scale])

  // Initialize from URL parameters
  useEffect(() => {
    const params = new URLSearchParams(window.location.search)
    const pos = params.get('pos')
    if (pos) {
      const [x, y, zoom] = pos.split(',').map(Number)
      if (!isNaN(x) && !isNaN(y) && !isNaN(zoom)) {
        setPosition({ x, y })
        setScale(zoom)
      }
    }
  }, [])

  const handleWheel = (e: React.WheelEvent) => {
    e.preventDefault()
    const delta = -e.deltaY * 0.01
    const newScale = Math.min(Math.max(scale + delta, 0.5), 2)
    setScale(newScale)
  }

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.5, ease: [0.4, 0, 0.2, 1] }}
      className="space-y-4"
    >
      <motion.div
        layout
        transition={{ duration: 0.3, ease: [0.4, 0, 0.2, 1] }}
        className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4"
      >
        <div className="flex items-center gap-2">
          <span className="text-sm font-medium">Zoom: {scale.toFixed(2)}x</span>
          <motion.button
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            onClick={() => setScale(Math.min(scale + 0.1, 2))}
            className="px-3 py-1 rounded-lg border border-gray-300 bg-white text-sm"
          >
            +
          </motion.button>
          <motion.button
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            onClick={() => setScale(Math.max(scale - 0.1, 0.5))}
            className="px-3 py-1 rounded-lg border border-gray-300 bg-white text-sm"
          >
            -
          </motion.button>
        </div>
      </motion.div>
      
      <motion.div
        layout
        transition={{ duration: 0.5, ease: [0.4, 0, 0.2, 1] }}
        className="bg-white rounded-lg shadow-md"
      >
        <motion.div
          ref={containerRef}
          layout
          transition={{ duration: 0.5, ease: [0.4, 0, 0.2, 1] }}
          className="relative w-full h-48 sm:h-64 md:h-96 lg:h-screen lg:max-h-[80vh] overflow-hidden"
          onWheel={handleWheel}
        >
          <AnimatePresence mode="wait">
            <motion.div
              style={{
                x,
                y,
                scale,
              }}
              drag
              dragConstraints={containerRef}
              dragElastic={0.1}
              dragMomentum={false}
              onDragEnd={(_, info) => {
                setPosition({
                  x: x.get(),
                  y: y.get(),
                })
              }}
              className="absolute inset-0 cursor-grab active:cursor-grabbing"
            >
              <motion.img
                src="/scripts/processed/complete_visualization.png"
                alt="Complete Visualization"
                className="w-full h-auto object-contain origin-center"
                style={{
                  maxWidth: 'none',
                  willChange: 'transform',
                }}
              />
            </motion.div>
          </AnimatePresence>
        </motion.div>
      </motion.div>
    </motion.div>
  )
}
