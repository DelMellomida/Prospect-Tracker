---
id: PTK-005
title: "Export records to CSV and import from CSV"
status: backlog
type: story
labels: [csv, export, import, backend]
priority: p2
assignee: jhondel
created: 2026-10-07
updated: 2026-10-07
---

## User Story

**As a** user managing prospect data,
**I want** to export and import records via CSV,
**so that** I can back up or migrate data easily.

---

## Background / Context
From Design Doc 2 (FR-5.1, FR-5.2): export at `/api/v1/records/export` (GET, CSV of all records), import at `/api/v1/records/import` (POST, CSV upload). Import uses service layer functions so audit and cache are handled.

---

## Acceptance Criteria
- [ ] **AC1:** GET `/records/export` downloads CSV with all records
- [ ] **AC2:** POST `/records/import` uploads a valid CSV and creates records
- [ ] **AC3:** Import writes audit entries per created record
- [ ] **AC4:** Import clears cache after commit

---

## Out of Scope
- Partial import / update via CSV
- CSV of notes or audit logs

---

## Design & Technical Notes
- CSV columns must match record fields
- Import uses service layer (`create_record`) to maintain audit + cache consistency

---

## Dependencies
- Blocked by: PTK-001, PTK-002, PTK-006
