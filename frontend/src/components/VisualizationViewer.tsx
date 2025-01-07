import React, { useEffect, useRef, useState } from 'react';
import { motion, useAnimation, useMotionValue, useSpring } from 'framer-motion';

interface VisualizationViewerProps {
  imagePath: string;
  initialWidth?: number;
  initialHeight?: number;
}

const VisualizationViewer: React.FC<VisualizationViewerProps> = ({
  imagePath,
  initialWidth = 1976,
  initialHeight = 2114,
}) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const [scale, setScale] = useState(0.5); // Initial scale matches matrix(0.5, 0, 0, 0.5, 0, 0)
  const [isDragging, setIsDragging] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  // Motion values for smooth animations
  const x = useMotionValue(0);
  const y = useMotionValue(0);
  const controls = useAnimation();
  
  // Add visual feedback classes based on dragging state
  const imageClasses = `select-none transition-all duration-200 ${
    isDragging ? 'brightness-90 scale-[0.99]' : ''
  } ${isLoading ? 'opacity-0' : 'opacity-100'}`;
  
  // Spring configuration for non-linear animations
  const springConfig = {
    stiffness: 700,
    damping: 30,
  };
  
  // Smooth scale animation
  const smoothScale = useSpring(scale, springConfig);
  
  // Handle zoom
  const handleWheel = (e: React.WheelEvent) => {
    e.preventDefault();
    const delta = -e.deltaY * 0.001;
    const newScale = Math.min(Math.max(scale + delta, 0.1), 2.0);
    setScale(newScale);
  };
  
  // Handle drag
  const handleDragStart = () => setIsDragging(true);
  const handleDragEnd = () => setIsDragging(false);
  
  // Handle window resize
  useEffect(() => {
    const handleResize = () => {
      if (containerRef.current) {
        const { width, height } = containerRef.current.getBoundingClientRect();
        // Adjust position to maintain viewport
        controls.start({
          x: x.get(),
          y: y.get(),
          transition: { type: 'spring', ...springConfig },
        });
      }
    };
    
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, [controls, x, y]);
  
  return (
    <div
      ref={containerRef}
      className="relative w-full h-[calc(100vh-4rem)] md:h-[calc(100vh-5rem)] lg:h-[calc(100vh-6rem)] overflow-hidden bg-gray-900 transition-all duration-300"
      onWheel={handleWheel}
    >
      <motion.div
        drag
        dragMomentum={false}
        dragElastic={0}
        onDragStart={handleDragStart}
        onDragEnd={handleDragEnd}
        style={{
          x,
          y,
          scale: smoothScale,
        }}
        className="origin-center cursor-grab active:cursor-grabbing relative"
      >
        {isLoading && (
          <div className="absolute inset-0 flex items-center justify-center bg-gray-900/50 backdrop-blur-sm">
            <div className="animate-spin rounded-full h-12 w-12 border-4 border-white border-t-transparent" />
          </div>
        )}
        {error && (
          <div className="absolute inset-0 flex items-center justify-center bg-red-900/50 backdrop-blur-sm">
            <div className="text-white bg-red-800/80 px-4 py-2 rounded-lg">{error}</div>
          </div>
        )}
        <motion.img
          src={imagePath}
          alt="Empire Visualization"
          className={imageClasses}
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.5, ease: [0.87, 0, 0.13, 1] }}
          style={{
            width: initialWidth,
            height: initialHeight,
            transformOrigin: 'center',
          }}
          draggable={false}
          onLoad={() => {
            setIsLoading(false);
            setError(null);
          }}
          onError={() => {
            setIsLoading(false);
            setError('Failed to load visualization');
          }}
        />
      </motion.div>
      
      {/* Zoom controls */}
      <div className="absolute bottom-4 right-4 flex gap-2">
        <button
          onClick={() => setScale(s => Math.min(s + 0.1, 2.0))}
          className="bg-white/10 hover:bg-white/20 text-white p-2 rounded-full"
        >
          +
        </button>
        <button
          onClick={() => setScale(s => Math.max(s - 0.1, 0.1))}
          className="bg-white/10 hover:bg-white/20 text-white p-2 rounded-full"
        >
          -
        </button>
      </div>
    </div>
  );
};

export default VisualizationViewer;
