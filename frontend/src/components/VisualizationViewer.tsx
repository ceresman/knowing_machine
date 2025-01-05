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
  
  // Motion values for smooth animations
  const x = useMotionValue(0);
  const y = useMotionValue(0);
  const controls = useAnimation();
  
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
      className="relative w-full h-full overflow-hidden bg-gray-900"
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
        className="origin-center cursor-grab active:cursor-grabbing"
      >
        <motion.img
          src={imagePath}
          alt="Empire Visualization"
          className="select-none"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.5 }}
          style={{
            width: initialWidth,
            height: initialHeight,
            transformOrigin: 'center',
          }}
          draggable={false}
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
