---
id: PTK-004
title: "Set and view follow-up reminder per record"
status: backlog
type: story
labels: [follow-up, reminder, backend, frontend]
priority: p1
assignee: jhondel
created: 2026-10-07
updated: 2026-10-07
---

## User Story

**As a** user tracking prospects,
**I want** to set a follow-up reminder date per record,
**so that** overdue prospects are flagged and I stay on track.

---

## Background / Context
From Design Doc 2 (FR-4.1): one follow-up per record with a date and content. PATCH /records/{id} with nested `follow_up` object handles create/update/delete of the follow-up row. List shows `follow_up_due` computed flag.

---

## Acceptance Criteria
- [ ] **AC1:** PATCH with `follow_up` object creates a new follow-up row
- [ ] **AC2:** PATCH with `follow_up` updates existing row partially
- [ ] **AC3:** PATCH with `follow_up: null` deletes the follow-up row
- [ ] **AC4:** List response includes `follow_up_date` and `follow_up_due` flag
- [ ] **AC5:** Record delete cascades to follow-up; audit remains

---

## Design & Technical Notes
- Separate `FollowUp` table (ADR-0001 decision for future one-to-many)
- Service layer handles nested create/update/delete within same transaction

---

## Dependencies
- Blocked by: PTK-001
