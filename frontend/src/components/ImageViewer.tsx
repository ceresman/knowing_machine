import { useState, useRef, useEffect } from 'react'
import { motion, AnimatePresence, useMotionValue, useSpring } from 'framer-motion'

interface ViewportState {
  scale: number;
  x: number;
  y: number;
}

export const ImageViewer: React.FC = () => {
  const [viewport, setViewport] = useState<ViewportState>({
    scale: 1,
    x: 0,
    y: 0,
  });

  const containerRef = useRef<HTMLDivElement>(null);
  const scale = useMotionValue(1);
  const x = useMotionValue(0);
  const y = useMotionValue(0);

  const smoothScale = useSpring(scale, {
    stiffness: 300,
    damping: 30,
    mass: 0.5,
  });

  const smoothX = useSpring(x, {
    stiffness: 300,
    damping: 30,
    mass: 0.5,
  });

  const smoothY = useSpring(y, {
    stiffness: 300,
    damping: 30,
    mass: 0.5,
  });

  const handleWheel = (e: React.WheelEvent) => {
    e.preventDefault();
    const scaleFactor = e.deltaY > 0 ? 0.9 : 1.1;
    const newScale = Math.min(Math.max(viewport.scale * scaleFactor, 0.1), 5);
    
    setViewport(prev => ({
      ...prev,
      scale: newScale,
    }));
    scale.set(newScale);
  };

  const handleDrag = (_: any, info: any) => {
    const newX = viewport.x + info.delta.x;
    const newY = viewport.y + info.delta.y;
    
    setViewport(prev => ({
      ...prev,
      x: newX,
      y: newY,
    }));
    
    x.set(newX);
    y.set(newY);
  };

  const resetView = () => {
    setViewport({ scale: 1, x: 0, y: 0 });
    scale.set(1);
    x.set(0);
    y.set(0);
  };

  useEffect(() => {
    const container = containerRef.current;
    if (container) {
      container.addEventListener('wheel', (e) => e.preventDefault(), { passive: false });
      return () => {
        container.removeEventListener('wheel', (e) => e.preventDefault());
      };
    }
  }, []);

  return (
    <div 
      ref={containerRef}
      className="fixed inset-0 overflow-hidden bg-gray-900"
      onWheel={handleWheel}
    >
      <AnimatePresence>
        <motion.div
          className="w-full h-full relative"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          transition={{ 
            duration: 0.5,
            ease: [0.4, 0, 0.2, 1]
          }}
        >
          <motion.div
            className="absolute left-1/2 top-1/2 origin-center cursor-grab active:cursor-grabbing"
            drag
            dragMomentum={false}
            onDrag={handleDrag}
            style={{
              scale: smoothScale,
              x: smoothX,
              y: smoothY,
            }}
          >
            <motion.img
              src="/images/merged_visualization.png"
              alt="Complete Visualization"
              className="max-w-none transform -translate-x-1/2 -translate-y-1/2"
              draggable={false}
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{
                duration: 0.5,
                ease: [0.4, 0, 0.2, 1]
              }}
            />
          </motion.div>
        </motion.div>
      </AnimatePresence>

      <div className="fixed bottom-4 left-1/2 transform -translate-x-1/2 flex gap-2 bg-black/50 p-2 rounded-lg">
        <motion.button
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 transition-colors"
          onClick={() => {
            const newScale = Math.min(viewport.scale * 1.2, 5);
            setViewport(prev => ({ ...prev, scale: newScale }));
            scale.set(newScale);
          }}
        >
          Zoom In
        </motion.button>
        <motion.button
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 transition-colors"
          onClick={() => {
            const newScale = Math.max(viewport.scale * 0.8, 0.1);
            setViewport(prev => ({ ...prev, scale: newScale }));
            scale.set(newScale);
          }}
        >
          Zoom Out
        </motion.button>
        <motion.button
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 transition-colors"
          onClick={resetView}
        >
          Reset
        </motion.button>
      </div>
    </div>
  );
}
