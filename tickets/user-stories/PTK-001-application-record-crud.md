---
id: PTK-001
title: "Create, edit, delete, and view application records"
status: completed
type: story
labels: [records, crud, backend, frontend]
priority: p0
assignee: jhondel
created: 2026-10-07
updated: 2026-10-07
---

## User Story

**As a** user tracking client acquisition,
**I want** to create, edit, delete, and view application records,
**so that** I can manage my prospect pipeline effectively.

---

## Background / Context
From Design Doc 2 (FR-1.1 to FR-1.5): the core CRUD for records including company, contact, date created, last date contacted, technical audit, source, and status. Company and status are required. This is the foundation for the tracker.

---

## Acceptance Criteria
- [/] **AC1:**
  - **Given** a user with valid input
  - **When** they submit a new application record
  - **Then** the record is saved with company, status, contact, dates, audit text, source
- [/] **AC2:**
  - **Given** an existing record
  - **When** the user edits it
  - **Then** the updated fields persist and are visible
- [/] **AC3:**
  - **Given** an existing record with notes
  - **When** the user deletes the record
  - **Then** notes and follow-up cascade-delete; audit logs remain
- [/] **AC4:**
  - **Given** a record exists
  - **When** the user views it
  - **Then** all fields including notes and follow-up are shown
- [/] **AC5:**
  - **Given** multiple records
  - **When** the user navigates
  - **Then** paginated list is returned (sizes: 10, 20, 50, 100)

---

## Out of Scope
- Filter/search logic (PTK-003)
- Note management (PTK-002)
- Audit log UI (PTK-006)

---

## Design & Technical Notes
- Models: `Record`, `Note`, `FollowUp`, `AuditLog`
- API: POST /api/v1/records, PATCH /api/v1/records/{id}, DELETE /api/v1/records/{id}, GET /api/v1/records/{id}, GET /api/v1/records
- Serializers: RecordWriteSerializer, RecordListSerializer, RecordDetailSerializer
- Service layer for writes (ADR-0004)

---

## Dependencies
- Blocked by: None
- Blocks: PTK-002, PTK-003, PTK-005

---

## Definition of Done
- [ ] Code complete and peer reviewed
- [ ] Unit / integration tests ≥ 80% coverage on views
- [ ] Acceptance criteria verified
- [ ] No critical bugs
