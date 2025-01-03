import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'

interface ImageViewerProps {
  initialZoom?: number
}

export const ImageViewer: React.FC<ImageViewerProps> = ({ initialZoom = 5 }) => {
  const [currentZoom, setCurrentZoom] = useState(initialZoom)
  const zoomLevels = Array.from({ length: 6 }, (_, i) => i + 5) // 5 to 10

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
          <span className="text-sm font-medium">Zoom Level:</span>
          <motion.select
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            value={currentZoom}
            onChange={(e) => setCurrentZoom(Number(e.target.value))}
            className="rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            {zoomLevels.map((level) => (
              <option key={level} value={level}>
                {level}
              </option>
            ))}
          </motion.select>
        </div>
      </motion.div>
      
      <motion.div
        layout
        transition={{ duration: 0.5, ease: [0.4, 0, 0.2, 1] }}
        className="bg-white rounded-lg shadow-md"
      >
        <motion.div
          layout
          transition={{ duration: 0.5, ease: [0.4, 0, 0.2, 1] }}
          className="relative w-full h-48 sm:h-64 md:h-96 lg:h-screen lg:max-h-screen overflow-auto"
        >
          <AnimatePresence mode="wait">
            <motion.img
              key={currentZoom}
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 1.2 }}
              transition={{
                duration: 0.5,
                ease: [0.4, 0, 0.2, 1],
                scale: {
                  duration: 0.7,
                  ease: [0.34, 1.56, 0.64, 1]
                }
              }}
              src={`/merged_tiles/merged_zoom_${currentZoom}.png`}
              alt={`Visualization at zoom level ${currentZoom}`}
              className="w-full h-auto object-contain"
            />
          </AnimatePresence>
        </motion.div>
      </motion.div>
    </motion.div>
  )
}
