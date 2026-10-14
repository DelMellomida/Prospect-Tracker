"use client";
import { useEffect, useRef, type ReactNode } from "react";
import { Icon } from "./icon";
// Native dialog provides focus trapping, Escape handling, and modal semantics.
export function Modal({ title, onClose, children, wide = false }: {
    title: string;
    onClose: () => void;
    children: ReactNode;
    wide?: boolean;
}) {
    const ref = useRef<HTMLDialogElement>(null);
    useEffect(() => {
        const dialog = ref.current;
        dialog?.showModal();
        const previousOverflow = document.body.style.overflow;
        document.body.style.overflow = "hidden";
        return () => { dialog?.close(); document.body.style.overflow = previousOverflow; };
    }, []);
    return <dialog ref={ref} className={`modal ${wide ? "modal-wide" : ""}`} aria-labelledby="modal-title" onCancel={onClose} onClick={(event) => { if (event.target === event.currentTarget)
        onClose(); }}>
    <div className="modal-heading"><h2 id="modal-title">{title}</h2><button className="icon-button" onClick={onClose} aria-label="Close dialog"><Icon name="close"/></button></div>{children}
  </dialog>;
}
