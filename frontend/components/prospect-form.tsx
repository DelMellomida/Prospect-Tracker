"use client";
import type { FormEvent } from "react";
import { DEMO_TODAY } from "@/lib/mock-data";
import { sources, sourceLabels, statuses, statusLabels, type Prospect, type ProspectInput } from "@/lib/types";
export function ProspectForm({ prospect, onSave, onCancel }: {
    prospect?: Prospect;
    onSave: (input: ProspectInput) => void;
    onCancel: () => void;
}) {
    function handleSubmit(event: FormEvent<HTMLFormElement>) {
        event.preventDefault();
        const data = new FormData(event.currentTarget);
        const value = (name: string) => String(data.get(name) ?? "").trim();
        onSave({ company: value("company"), status: value("status") as ProspectInput["status"], company_email: value("company_email"), company_contact_no: value("company_contact_no"), source: value("source") as ProspectInput["source"], last_date_contacted: value("last_date_contacted"), technical_audit: value("technical_audit"), follow_up: value("follow_up_date") ? { date: value("follow_up_date"), content: value("follow_up_content") } : null });
    }
    return <form onSubmit={handleSubmit} className="prospect-form">
    <p className="muted form-intro">A little context now makes your next conversation easier.</p>
    <label>Company <span className="required">*</span><input name="company" required maxLength={255} pattern=".*\S.*" autoFocus placeholder="e.g. Layers Studio" defaultValue={prospect?.company}/></label>
    <div className="form-grid">
      <label>Status<select name="status" defaultValue={prospect?.status ?? "contacted"}>{statuses.map((status) => <option key={status} value={status}>{statusLabels[status]}</option>)}</select></label>
      <label>Source<select name="source" defaultValue={prospect?.source ?? "others"}>{sources.map((source) => <option key={source} value={source}>{sourceLabels[source]}</option>)}</select></label>
      <label>Email<input name="company_email" type="email" placeholder="hello@company.com" defaultValue={prospect?.company_email}/></label>
      <label>Phone<input name="company_contact_no" type="tel" maxLength={20} placeholder="+63 …" defaultValue={prospect?.company_contact_no}/></label>
      <label>Last contacted<input name="last_date_contacted" type="date" defaultValue={prospect?.last_date_contacted ?? DEMO_TODAY}/></label>
      <label>Follow-up date<input name="follow_up_date" type="date" defaultValue={prospect?.follow_up?.date}/></label>
    </div>
    <label>Follow-up reminder<input name="follow_up_content" placeholder="What would you like to follow up on?" defaultValue={prospect?.follow_up?.content}/></label>
    <label>Technical audit<textarea name="technical_audit" rows={3} placeholder="Opportunities, website issues, or project ideas…" defaultValue={prospect?.technical_audit}/></label>
    <div className="form-footer"><span className="muted">Saved in this demo session only</span><button type="button" className="button" onClick={onCancel}>Cancel</button><button type="submit" className="button primary">{prospect ? "Save changes" : "Add prospect"}</button></div>
  </form>;
}
