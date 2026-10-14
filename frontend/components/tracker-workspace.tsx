"use client";
import { useEffect, useState } from "react";
import Link from "next/link";
import { DEMO_TODAY, initialActivity, initialProspects } from "@/lib/mock-data";
import { sourceLabels, sources, statusLabels, statuses, type Activity, type Prospect, type ProspectInput, type Status } from "@/lib/types";
import { Icon } from "./icon";
import { Modal } from "./modal";
import { ProspectForm } from "./prospect-form";
import { ProspectDetail } from "./prospect-detail";
type View = "Overview" | "All prospects" | "Follow-ups" | "Activity";
const navigation = [{ label: "Overview", icon: "grid" }, { label: "All prospects", icon: "people" }, { label: "Follow-ups", icon: "clock" }, { label: "Activity", icon: "activity" }] as const;
const dateLabel = (date: string) => date ? new Date(`${date.slice(0, 10)}T12:00:00Z`).toLocaleDateString("en-US", { month: "short", day: "numeric", timeZone: "UTC" }) : "—";
const isDue = (prospect: Prospect) => Boolean(prospect.follow_up && prospect.follow_up.date <= DEMO_TODAY);
function CompanyMark({ company }: {
    company: string;
}) {
    const color = [...company].reduce((sum, char) => sum + char.charCodeAt(0), 0) % 5;
    return <span className={`company-mark mark-${color}`}>{company.split(" ").slice(0, 2).map((word) => word[0]).join("")}</span>;
}
export function TrackerWorkspace() {
    // Backend connection point: replace this seed and the mutation handlers below
    // with calls to your API. Components only receive data and callbacks.
    const [prospects, setProspects] = useState<Prospect[]>(initialProspects);
    const [activity, setActivity] = useState<Activity[]>(initialActivity);
    const [view, setView] = useState<View>("Overview");
    const [query, setQuery] = useState("");
    const [status, setStatus] = useState<Status | "all">("all");
    const [source, setSource] = useState("all");
    const [sort, setSort] = useState("newest");
    const [page, setPage] = useState(1);
    const [selectedId, setSelectedId] = useState<string | null>(null);
    const [editor, setEditor] = useState<"new" | Prospect | null>(null);
    const [helpOpen, setHelpOpen] = useState(false);
    const [toast, setToast] = useState("");
    const selected = prospects.find((prospect) => prospect.record_id === selectedId);
    const due = prospects.filter(isDue);
    const ongoing = prospects.filter((prospect) => prospect.status === "ongoing").length;
    const completed = prospects.filter((prospect) => prospect.status === "completion").length;
    const reminders = prospects.filter((prospect) => prospect.follow_up).sort((a, b) => a.follow_up!.date.localeCompare(b.follow_up!.date));
    const filtered = prospects.filter((prospect) => (status === "all" || prospect.status === status) && (source === "all" || prospect.source === source) && `${prospect.company} ${sourceLabels[prospect.source]} ${prospect.company_email}`.toLowerCase().includes(query.toLowerCase())).sort((a, b) => sort === "company" ? a.company.localeCompare(b.company) : sort === "oldest" ? a.last_date_contacted.localeCompare(b.last_date_contacted) : b.last_date_contacted.localeCompare(a.last_date_contacted));
    const pageCount = Math.max(1, Math.ceil(filtered.length / 6));
    const safePage = Math.min(page, pageCount);
    const visible = filtered.slice((safePage - 1) * 6, safePage * 6);
    useEffect(() => { if (!toast)
        return; const timer = setTimeout(() => setToast(""), 3500); return () => clearTimeout(timer); }, [toast]);
    function navigate(next: View) { setView(next); setQuery(""); setStatus("all"); setSource("all"); setPage(1); }
    function log(company: string, description: string) { setActivity((items) => [{ id: crypto.randomUUID(), company, description, created_at: new Date().toISOString() }, ...items]); }
    function updateProspect(updated: Prospect) { setProspects((items) => items.map((item) => item.record_id === updated.record_id ? updated : item)); }
    function saveProspect(input: ProspectInput) {
        if (!editor)
            return;
        if (editor === "new") {
            setProspects((items) => [{ ...input, record_id: crypto.randomUUID(), created_at: DEMO_TODAY, notes: [] }, ...items]);
            log(input.company, "Prospect added");
        }
        else {
            updateProspect({ ...editor, ...input });
            log(input.company, "Prospect updated");
        }
        setEditor(null);
        setToast(editor === "new" ? "Prospect added to your workspace" : "Changes saved");
    }
    function exportCsv() {
        const columns = ["company", "status", "company_email", "company_contact_no", "source", "last_date_contacted", "technical_audit"] as const;
        // Quote every field and neutralize spreadsheet formulas in user-entered text.
        const cell = (value: string) => `"${(/^[=+@\-\t\r\n]/.test(value) ? "'" + value : value).replaceAll('"', '""')}"`;
        const csv = [columns.join(","), ...filtered.map((item) => columns.map((key) => cell(item[key])).join(","))].join("\r\n");
        const url = URL.createObjectURL(new Blob([csv], { type: "text/csv;charset=utf-8;" }));
        const link = document.createElement("a");
        link.href = url;
        link.download = "prospects-demo.csv";
        link.click();
        setTimeout(() => URL.revokeObjectURL(url), 1000);
        setToast(`Exported ${filtered.length} prospects`);
    }
    return <div className="workspace">
    <aside className="sidebar">
      <div className="sidebar-content">
      <Link className="brand" href="/" aria-label="Prospect home"><span className="brand-icon"><Icon name="leaf" size={23}/></span>prospect<span className="brand-period">.</span></Link>
      <div className="workspace-switch"><span className="workspace-avatar">J</span><div><strong>My workspace</strong><small>Personal workspace</small></div><span className="workspace-tag">FREE</span></div>
      <p className="nav-caption">WORKSPACE</p>
      <nav aria-label="Main navigation">{navigation.map((item) => <button key={item.label} aria-label={item.label} title={item.label} className={`nav-item ${view === item.label ? "active" : ""}`} onClick={() => navigate(item.label)} aria-current={view === item.label ? "page" : undefined}><Icon name={item.icon}/><span>{item.label}</span>{item.label === "All prospects" && <span className="nav-count">{prospects.length}</span>}{item.label === "Follow-ups" && due.length > 0 && <span className="nav-count orange-count">{due.length}</span>}</button>)}</nav>
      <div className="sidebar-bottom"><div className="sidebar-tip"><span className="tip-icon"><Icon name="trend"/></span><strong>Small steps. Real progress.</strong><p>Your next opportunity starts with a conversation.</p><button className="text-button" onClick={() => setEditor("new")}>Make a connection <Icon name="arrow" size={15}/></button></div></div>
      </div>
      <button className="profile" onClick={() => setHelpOpen(true)}><span className="profile-avatar">J</span><span><strong>Jhondel</strong><small>Your personal workspace</small></span><Icon name="chevron" size={16}/></button>
    </aside>

    <div className="main-shell">
      <header className="topbar"><div className="breadcrumbs">Workspace <Icon name="chevron" size={13}/><span>{view}</span></div><div className="topbar-right"><span className="demo-pill"><span />Demo workspace</span><button className="help-button" onClick={() => setHelpOpen(true)} aria-label="About this demo">?</button><span className="top-avatar">J</span></div></header>
      <main id="main-content">
        <div className="page-heading"><div><div className="eyebrow">YOUR PIPELINE, A LITTLE CLEARER</div><h1>{view === "Overview" ? "Every connection counts." : view}</h1><p>{view === "Overview" ? "A little focus today. A new opportunity tomorrow." : view === "All prospects" ? "Good relationships start with keeping track." : view === "Follow-ups" ? "Keep the conversation going, one check-in at a time." : "A running history of your connections and next steps."}</p></div><button className="button primary" onClick={() => setEditor("new")}><Icon name="plus" size={18}/>Add prospect</button></div>

        {view === "Overview" && <>
          <div className="overview-meta"><span><span className="live-dot"/>Your workspace at a glance</span><span><Icon name="calendar" size={15}/> October 15, 2026 <span className="muted">· Sample day</span></span></div>
          <section className="stats-grid" aria-label="Pipeline summary">{[
                { label: "Total prospects", value: prospects.length, caption: "Connections in your workspace", icon: "people" as const, color: "lavender" },
                { label: "In progress", value: ongoing, caption: "Conversations moving forward", icon: "trend" as const, color: "blue" },
                { label: "Completed", value: completed, caption: "Connections turned into projects", icon: "check" as const, color: "green" },
                { label: "Follow-ups due", value: due.length, caption: "A good time to check in", icon: "clock" as const, color: "peach" },
            ].map((stat) => <article className="stat-card" key={stat.label}><div className="stat-top"><span>{stat.label}</span><span className={`stat-icon ${stat.color}`}><Icon name={stat.icon} size={18}/></span></div><strong>{String(stat.value).padStart(2, "0")}</strong><p>{stat.caption}</p></article>)}</section>
          <div className="insights-grid"><section className="panel pipeline-panel"><div className="panel-heading"><div><h2>Your pipeline</h2><p>From first hello to a project well done.</p></div><span className="subtle-tag">{prospects.length} prospects</span></div><div className="pipeline-bar" aria-hidden="true">{statuses.map((item) => <span key={item} className={item} style={{ flexGrow: prospects.filter((p) => p.status === item).length }}/>)}</div><div className="pipeline-legend">{statuses.map((item) => <button key={item} onClick={() => { navigate("All prospects"); setStatus(item); }}><span><i className={`status-dot ${item}`}/>{statusLabels[item]}</span><strong>{prospects.filter((p) => p.status === item).length}</strong></button>)}</div></section>
            <section className="focus-card"><div className="focus-copy"><span className="focus-label"><Icon name="clock" size={15}/> A LITTLE NUDGE</span><h2>{due.length ? `${due.length} conversations to pick up.` : "You’re all caught up."}</h2><p>{due.length ? "A simple follow-up can open the right door." : "Take a moment to find your next connection."}</p><button className="button" onClick={() => navigate("Follow-ups")}>View follow-ups <Icon name="arrow" size={16}/></button></div><div className="focus-art" aria-hidden="true"><div className="orbit orbit-one"/><div className="orbit orbit-two"/><span className="art-mail"><Icon name="mail" size={39}/></span><span className="art-check"><Icon name="check" size={17}/></span><span className="art-star">✳</span></div></section></div>
        </>}

        {(view === "Overview" || view === "All prospects") && <section className="panel prospects-panel"><div className="panel-heading"><div className="section-title"><h2>{view === "Overview" ? "Your prospects" : "Prospect directory"}</h2><span className="count">{prospects.length}</span></div><button className="button compact" onClick={exportCsv}><Icon name="download" size={16}/>Export CSV</button></div>
          <div className="table-toolbar"><div className="status-tabs" aria-label="Filter by status">{(["all", ...statuses] as const).map((item) => <button key={item} className={status === item ? "selected" : ""} onClick={() => { setStatus(item); setPage(1); }} aria-pressed={status === item}>{item === "all" ? "All prospects" : statusLabels[item]}</button>)}</div><div className="table-filters"><label className="search-field"><Icon name="search" size={17}/><span className="sr-only">Search prospects</span><input placeholder="Search company or source…" value={query} onChange={(event) => { setQuery(event.target.value); setPage(1); }}/></label><label className="sr-only" htmlFor="source">Filter by source</label><select id="source" value={source} onChange={(event) => { setSource(event.target.value); setPage(1); }}><option value="all">All sources</option>{sources.map((item) => <option key={item} value={item}>{sourceLabels[item]}</option>)}</select><label className="sr-only" htmlFor="sort">Sort prospects</label><select id="sort" value={sort} onChange={(event) => { setSort(event.target.value); setPage(1); }}><option value="newest">Last contacted: newest</option><option value="oldest">Last contacted: oldest</option><option value="company">Company: A–Z</option></select></div></div>
          <div className="table-scroll"><table><thead><tr><th>Company</th><th>Status</th><th>Source</th><th>Last contacted</th><th>Follow-up</th><th><span className="sr-only">View prospect</span></th></tr></thead><tbody>{visible.map((prospect) => <tr key={prospect.record_id}><td><button className="company-button" onClick={() => setSelectedId(prospect.record_id)}><CompanyMark company={prospect.company}/><span><strong>{prospect.company}</strong><small>{prospect.company_email || "No email added"}</small></span></button></td><td><span className={`badge ${prospect.status}`}><i />{statusLabels[prospect.status]}</span></td><td><span className="source-label"><span className={`source-icon ${prospect.source}`}>{prospect.source === "linkedin" ? "in" : prospect.source === "others" ? "↗" : sourceLabels[prospect.source][0].toLowerCase()}</span>{sourceLabels[prospect.source]}</span></td><td className="date-cell">{dateLabel(prospect.last_date_contacted)}</td><td><span className={isDue(prospect) ? "due-date" : "date-cell"}>{prospect.follow_up ? <><Icon name="calendar" size={13}/>{prospect.follow_up.date === DEMO_TODAY ? "Today" : dateLabel(prospect.follow_up.date)}{prospect.follow_up.date < DEMO_TODAY && <span className="overdue-dot" title="Overdue"/>}</> : "—"}</span></td><td><button className="icon-button row-open" aria-label={`View ${prospect.company}`} onClick={() => setSelectedId(prospect.record_id)}><Icon name="chevron" size={16}/></button></td></tr>)}</tbody></table></div>
          {filtered.length === 0 && <div className="empty-state"><Icon name="search" size={30}/><h3>No prospects found</h3><p>Try another search or add your next connection.</p><button className="button" onClick={() => { setQuery(""); setStatus("all"); setSource("all"); }}>Clear filters</button></div>}
          <div className="table-footer"><span>{filtered.length ? `Showing ${(safePage - 1) * 6 + 1}–${Math.min(safePage * 6, filtered.length)} of ${filtered.length} prospects` : "0 prospects"}</span><div><button className="button compact" disabled={safePage === 1} onClick={() => setPage(safePage - 1)}>Previous</button><span className="page-number">{safePage} / {pageCount}</span><button className="button compact" disabled={safePage >= pageCount} onClick={() => setPage(safePage + 1)}>Next</button></div></div>
        </section>}

        {view === "Follow-ups" && <section className="panel"><div className="panel-heading"><div><h2>Your next conversations</h2><p>{due.length} due · {reminders.length} scheduled · Sample day: October 15, 2026</p></div><Icon name="calendar"/></div>{reminders.length === 0 ? <div className="empty-state"><Icon name="check" size={32}/><h3>All clear for now</h3><p>Add a follow-up date when editing a prospect.</p></div> : <div className="reminder-list">{reminders.map((prospect) => <article key={prospect.record_id} className="reminder-row"><CompanyMark company={prospect.company}/><div className="reminder-copy"><button className="text-button" onClick={() => setSelectedId(prospect.record_id)}>{prospect.company}</button><p>{prospect.follow_up!.content || "Check in with this prospect."}</p></div><span className={isDue(prospect) ? "due-label" : "subtle-tag"}>{prospect.follow_up!.date < DEMO_TODAY ? "Overdue · " : ""}{prospect.follow_up!.date === DEMO_TODAY ? "Today" : dateLabel(prospect.follow_up!.date)}</span><button className="button compact" onClick={() => { updateProspect({ ...prospect, follow_up: null }); log(prospect.company, "Follow-up completed"); setToast("Follow-up marked complete"); }}><Icon name="check" size={15}/>Done</button></article>)}</div>}</section>}

        {view === "Activity" && <section className="panel"><div className="panel-heading"><div><h2>Workspace activity</h2><p>Sample events and changes made during this session.</p></div><span className="subtle-tag">{activity.length} events</span></div><div className="activity-list">{activity.map((item) => <article className="activity-row" key={item.id}><span className="activity-icon"><Icon name="activity" size={18}/></span><div><strong>{item.company}</strong><p>{item.description}</p></div><time>{dateLabel(item.created_at)}</time></article>)}</div></section>}
        <footer className="workspace-footer"><span><Icon name="leaf" size={14}/>Built for better connections.</span><span>Frontend preview <i /> Changes reset on refresh</span></footer>
      </main>
    </div>

    {selected && !editor && <Modal title={selected.company} onClose={() => setSelectedId(null)} wide><ProspectDetail prospect={selected} onEdit={() => setEditor(selected)} onChange={updateProspect} onActivity={(description) => log(selected.company, description)} onDelete={() => { setProspects((items) => items.filter((item) => item.record_id !== selected.record_id)); log(selected.company, "Prospect deleted"); setSelectedId(null); setToast("Prospect deleted"); }}/></Modal>}
    {editor && <Modal title={editor === "new" ? "A new connection" : "Edit prospect"} onClose={() => setEditor(null)} wide><ProspectForm prospect={editor === "new" ? undefined : editor} onSave={saveProspect} onCancel={() => setEditor(null)}/></Modal>}
    {helpOpen && <Modal title="Your practice workspace" onClose={() => setHelpOpen(false)}><div className="help-content"><span className="demo-pill"><span />Frontend demo</span><p>Explore your pipeline, add prospects, write notes, and schedule follow-ups. Everything runs locally in this page.</p><p>Changes reset when you refresh. The sample workspace uses October 15, 2026 as its reference day. There is no account or backend connection yet.</p><p>To start learning, see <code>frontend/README.md</code>. It explains the components, sample data, and where to connect your Django API later.</p><button className="button primary" onClick={() => setHelpOpen(false)}>Got it, let’s explore <Icon name="arrow" size={16}/></button></div></Modal>}
    <div className={`toast ${toast ? "visible" : ""}`} role="status" aria-live="polite">{toast && <><Icon name="check" size={18}/>{toast}</>}</div>
  </div>;
}
