import { useEffect } from 'react'

export default function Modal({
  titleId,
  labelledBy,
  onClose,
  children,
  className = '',
}) {
  useEffect(() => {
    const handleKeyDown = (event) => {
      if (event.key === 'Escape') onClose()
    }
    document.addEventListener('keydown', handleKeyDown)
    const previousOverflow = document.body.style.overflow
    document.body.style.overflow = 'hidden'
    return () => {
      document.removeEventListener('keydown', handleKeyDown)
      document.body.style.overflow = previousOverflow
    }
  }, [onClose])

  return (
    <div className="modal-backdrop" onMouseDown={onClose} role="presentation">
      <section
        className={`modal-panel ${className}`.trim()}
        role="dialog"
        aria-modal="true"
        aria-labelledby={labelledBy || titleId}
        onMouseDown={(event) => event.stopPropagation()}
      >
        <button
          className="modal-panel__close"
          type="button"
          onClick={onClose}
          aria-label="닫기"
        >
          ×
        </button>
        <div className="modal-panel__body">{children}</div>
      </section>
    </div>
  )
}
