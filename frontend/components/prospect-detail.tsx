"use client";
import { useState } from "react";
import { sourceLabels, statusLabels, type Prospect } from "@/lib/types";
import { Icon } from "./icon";
export function ProspectDetail({ prospect, onEdit, onDelete, onChange, onActivity }: {
    prospect: Prospect;
    onEdit: () => void;
    onDelete: () => void;
    onChange: (prospect: Prospect) => void;
    onActivity: (description: string) => void;
}) {
    const [confirmDelete, setConfirmDelete] = useState(false);
    const [note, setNote] = useState("");
    const [editingNote, setEditingNote] = useState<string | null>(null);
    return <div className="detail-content">
    <div className="detail-summary"><span className={`badge ${prospect.status}`}>{statusLabels[prospect.status]}</span><span className="muted">via {sourceLabels[prospect.source]}</span><button className="button" onClick={onEdit}><Icon name="edit" size={16}/> Edit prospect</button></div>
    <dl className="detail-grid"><div><dt>Email</dt><dd>{prospect.company_email || "Not provided"}</dd></div><div><dt>Phone</dt><dd>{prospect.company_contact_no || "Not provided"}</dd></div><div><dt>Last contacted</dt><dd>{prospect.last_date_contacted || "Not set"}</dd></div><div><dt>Added</dt><dd>{prospect.created_at.slice(0, 10)}</dd></div></dl>
    <section className="detail-section"><h3>Technical audit</h3><p className="preserve-lines">{prospect.technical_audit || "No technical audit yet. Edit this prospect to add your observations."}</p></section>
    <section className="detail-section reminder-detail"><Icon name="calendar"/><div><h3>Next follow-up {prospect.follow_up && <span className="muted">· {prospect.follow_up.date}</span>}</h3><p>{prospect.follow_up?.content || (prospect.follow_up ? "A reminder is scheduled." : "No reminder scheduled. Add one with Edit prospect.")}</p></div>{prospect.follow_up && <button className="icon-button" aria-label="Complete follow-up" title="Complete follow-up" onClick={() => { onChange({ ...prospect, follow_up: null }); onActivity("Follow-up completed"); }}><Icon name="check"/></button>}</section>
    <section className="detail-section"><h3>Notes <span className="count">{prospect.notes.length}</span></h3>
      <div className="notes-list">{prospect.notes.length === 0 && <p className="muted">Keep conversation details and next steps in one place.</p>}{prospect.notes.map((item) => <article className="note" key={item.id}><p className="preserve-lines">{item.content}</p><div className="note-footer"><time>{new Date(item.created_at).toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric", timeZone: "Asia/Manila" })}</time><button className="text-button" onClick={() => { setEditingNote(item.id); setNote(item.content); }}>Edit</button><button className="text-button danger-text" onClick={() => { onChange({ ...prospect, notes: prospect.notes.filter((n) => n.id !== item.id) }); if (editingNote === item.id) {
        setEditingNote(null);
        setNote("");
    } onActivity("Note deleted"); }}>Delete</button></div></article>)}</div>
      <form className="note-form" onSubmit={(event) => { event.preventDefault(); if (!note.trim())
        return; const content = note.trim(); onChange({ ...prospect, notes: editingNote ? prospect.notes.map((n) => n.id === editingNote ? { ...n, content } : n) : [...prospect.notes, { id: crypto.randomUUID(), content, created_at: new Date().toISOString() }] }); onActivity(editingNote ? "Note updated" : "Note added"); setNote(""); setEditingNote(null); }}><label className="sr-only" htmlFor="note">{editingNote ? "Edit note" : "New note"}</label><textarea id="note" rows={3} placeholder="Write a note about this prospect…" value={note} onChange={(event) => setNote(event.target.value)} required/><div className="note-actions">{editingNote && <button type="button" className="button" onClick={() => { setEditingNote(null); setNote(""); }}>Cancel edit</button>}<button className="button primary" disabled={!note.trim()}>{editingNote ? "Save note" : "Add note"}</button></div></form>
    </section>
    <div className="delete-zone">{confirmDelete ? <><p>Delete this prospect and its notes from this demo?</p><button className="button" onClick={() => setConfirmDelete(false)}>Keep prospect</button><button className="button danger" onClick={onDelete}>Delete prospect</button></> : <button className="text-button danger-text" onClick={() => setConfirmDelete(true)}><Icon name="trash" size={15}/> Delete prospect</button>}</div>
  </div>;
}
