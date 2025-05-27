import React from 'react';
import { motion } from 'framer-motion';
import { Plus } from 'lucide-react';

interface FloatingNewScanButtonProps {
  onClick?: () => void;
  className?: string;
}

const FloatingNewScanButton: React.FC<FloatingNewScanButtonProps> = ({ 
  onClick,
  className = '' 
}) => {
  const handleClick = () => {
    if (onClick) {
      onClick();
    } else {
      // Default action - navigate to create scan page
      window.location.href = '/create-scan';
    }
  };

  return (
    <motion.button
      className={`floating-button ${className}`}
      onClick={handleClick}
      whileHover={{ 
        scale: 1.05,
        y: -3,
        transition: { duration: 0.2 }
      }}
      whileTap={{ 
        scale: 1.02,
        y: -1,
        transition: { duration: 0.1 }
      }}
      initial={{ 
        opacity: 0, 
        scale: 0.8,
        y: 20
      }}
      animate={{ 
        opacity: 1, 
        scale: 1,
        y: 0
      }}
      transition={{ 
        duration: 0.5,
        delay: 0.3,
        type: "spring",
        stiffness: 300,
        damping: 20
      }}
      title="Tạo scan mới"
    >
      <motion.div 
        className="floating-button-icon"
        whileHover={{ 
          rotate: 90,
          transition: { duration: 0.2 }
        }}
      >
        <Plus size={24} strokeWidth={2.5} />
      </motion.div>
    </motion.button>
  );
};

export default FloatingNewScanButton; 