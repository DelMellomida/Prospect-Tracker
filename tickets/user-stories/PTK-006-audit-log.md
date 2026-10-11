---
id: PTK-006
title: "Audit log for every record, note, and follow-up change"
status: backlog
type: story
labels: [audit, backend, reliability]
priority: p0
assignee: jhondel
created: 2026-10-07
updated: 2026-10-07
---

## User Story

**As a** system operator and future auditor,
**I want** every create, update, or delete to write an audit entry,
**so that** changes are traceable and meet data integrity requirements.

---

## Background / Context
From Design Doc 2 (FR-7.1, NFR-3, NFR-5): audit logs are append-only, no foreign key (survives deletion), include entity_type, entity_id, action, initiator (system placeholder), old_value, new_value, timestamp (UTC).

---

## Acceptance Criteria
- [ ] **AC1:** Every write through service layer creates exactly one audit entry
- [ ] **AC2:** Audit entries have no update or delete endpoint (read-only)
- [ ] **AC3:** Deleting a record does not delete its audit entries
- [ ] **AC4:** Audit log list supports filters: entity_type, entity_id, action, created_after, created_before

---

## Design & Technical Notes
- `AuditLog` model: no FK to parent; `entity_type`, `entity_id` as plain values
- Endpoint: GET `/api/v1/audit-logs` (filterable, paginated, newest first)
- Service layer writes audit after DB commit

---

## Dependencies
- Blocked by: PTK-001
- Blocks: PTK-005
