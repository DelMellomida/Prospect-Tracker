---
id: PTK-002
title: "Add, edit, and delete notes on application records"
status: completed
type: story
labels: [notes, crud, backend, frontend]
priority: p0
assignee: jhondel
created: 2026-10-07
updated: 2026-10-07
---

## User Story

**As a** user tracking client acquisition,
**I want** to add, edit, and delete timestamped notes on records,
**so that** I can document responses and updates per prospect.

---

## Background / Context
From Design Doc 2 (FR-2.1 to FR-2.3): notes are child objects of records, auto-timestamped, with content only. Created through the record endpoint or directly.

---

## Acceptance Criteria
- [/] **AC1:**
  - **Given** a record exists
  - **When** user posts a note
  - **Then** note is saved with content, created_at, updated_at
- [/] **AC2:**
  - **Given** a note exists
  - **When** user edits content
  - **Then** updated_at updates and new content is shown
- [/] **AC3:**
  - **Given** a note exists
  - **When** user deletes it
  - **Then** note is removed, no orphan remains
- [/] **AC4:** Notes are included in record detail response

---

## Out of Scope
- Note search
- Note attachments

---

## Design & Technical Notes
- Endpoints: POST /api/v1/records/{record_id}/notes, PATCH /api/v1/notes/{note_id}, DELETE /api/v1/notes/{note_id}
- Model: `Note` with FK cascade delete to `Record`

---

## Dependencies
- Blocked by: PTK-001
- Blocks: PTK-006
