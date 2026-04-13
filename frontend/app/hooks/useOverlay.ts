'use client';

import { useCallback, useEffect, useRef, useState } from 'react';

export function useOverlay(isOpen: boolean, onClose: () => void) {
  const [visible, setVisible] = useState(false);
  const rafRef = useRef<number>(0);
  const timeoutRef = useRef<ReturnType<typeof setTimeout>>();

  const handleClose = useCallback(() => {
    setVisible(false);
    clearTimeout(timeoutRef.current);
    timeoutRef.current = setTimeout(onClose, 400);
  }, [onClose]);

  useEffect(() => {
    if (isOpen) {
      rafRef.current = requestAnimationFrame(() => setVisible(true));
      document.body.style.overflow = 'hidden';
      return () => {
        cancelAnimationFrame(rafRef.current);
        clearTimeout(timeoutRef.current);
        document.body.style.overflow = '';
      };
    } else {
      setVisible(false);
      document.body.style.overflow = '';
    }
  }, [isOpen]);

  useEffect(() => {
    if (!isOpen) return;
    function handleKeyDown(e: KeyboardEvent) {
      if (e.key === 'Escape') handleClose();
    }
    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, handleClose]);

  function handleBackdropClick(e: React.MouseEvent<HTMLDivElement>) {
    if (e.target === e.currentTarget) handleClose();
  }

  return { visible, handleClose, handleBackdropClick };
}
