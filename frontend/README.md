# Prospect frontend

A Next.js + TypeScript practice frontend for your client prospect tracker. No backend is connected. No API requests, authentication, or database writes are implemented.

## Run it

```powershell
cd frontend
npm install
npm run dev
```

Open http://localhost:3000. To check your changes, run `npm run lint` and `npm run build`.

## What you can try

- Navigate between Overview, All prospects, Follow-ups, and Activity.
- Search by company, email, or source; filter by status/source; sort and paginate.
- Add, inspect, edit, and delete a prospect.
- Add, edit, and delete notes in a prospect's details.
- Set or remove a follow-up through Edit prospect, or mark one complete.
- Export the currently filtered prospects as CSV.

All changes are held in React state and reset when you refresh. Sample reminders use **October 15, 2026** as their reference date, so the demo always has useful examples. The profile is a sample identity, not a signed-in account. Activity is an in-memory UI feed, not a persistent audit log.

## Find your way around

| File | Responsibility |
| --- | --- |
| `app/page.tsx` | The home route; renders the workspace. |
| `app/layout.tsx` | Page metadata and shared HTML wrapper. |
| `app/globals.css` | Colors, layout, components, and mobile breakpoints. |
| `lib/types.ts` | TypeScript data shapes, statuses, and source labels. |
| `lib/mock-data.ts` | Sample prospects, sample events, and demo date. |
| `components/tracker-workspace.tsx` | UI state, navigation, filters, table, and mutation handlers. |
| `components/prospect-form.tsx` | Reusable add/edit form; returns values through `onSave`. |
| `components/prospect-detail.tsx` | Contact details, technical audit, notes, and delete confirmation. |
| `components/modal.tsx` | Accessible native dialog with Escape and focus handling. |
| `components/icon.tsx` | Small shared SVG icon component; no icon dependency. |

## How the pieces fit

1. `useState(initialProspects)` gives the workspace an editable list.
2. Search and filter state produce `filtered`, the list displayed in the table.
3. The form uses native HTML validation and `FormData` to collect values.
4. `onSave` calls `saveProspect`, which updates the local list.
5. React renders the table and summary again from that updated list.

The detail and form components receive values through **props** and report actions through **callbacks**. They don't need to know how data is stored. This is the seam you can keep when you add a backend.

## Connect your backend later

Start in `components/tracker-workspace.tsx`, at the comment above the state declarations. No inactive API client or environment configuration is needed for this demo.

1. Read `backend/tracker/serializers.py` and `backend/tracker/urls.py` to confirm the current response shapes and routes.
2. Add a small module such as `lib/api.ts` for requests when you are ready. Keep request code out of presentation components.
3. Replace the initial mock list with a records request. Add loading and error states. Backend pagination/filtering should replace the current client-side equivalents when using paginated results.
4. Update `saveProspect`, `updateProspect`, delete, and note/follow-up handlers to call their corresponding endpoints. Only update local state after a successful response, and show failures clearly.
5. Map the API's numeric IDs, nullable fields, note IDs, and nested follow-up fields into the UI types, or update the UI types to match. These frontend types are a starting point, not a guaranteed API contract.
6. Replace `DEMO_TODAY` with the intended current-date/timezone behavior and load the real audit log separately from this sample activity feed.

Status values (`contacted`, `ongoing`, `completion`, `dropped`) and source values match the existing Django choices. Display labels can differ: `ongoing` appears as “In progress”.

## Small exercises

- Change the accent color in `app/globals.css`.
- Add a sample company in `lib/mock-data.ts` and watch the summary change.
- Trace the Add prospect button through `editor`, `ProspectForm`, and `saveProspect`.
- Add a new optional display field to the type, sample data, form, and detail view.
