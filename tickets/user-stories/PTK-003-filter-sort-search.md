---
id: PTK-003
title: "Filter, sort, and search application records"
status: backlog
type: story
labels: [search, filter, sort, backend, frontend]
priority: p0
assignee: jhondel
created: 2026-10-07
updated: 2026-10-07
---

## User Story

**As a** user managing prospects,
**I want** to filter by status, sort by last contacted date, and search company/source,
**so that** I can quickly find relevant records.

---

## Background / Context
From Design Doc 2 (FR-3.1, FR-3.2, FR-3.3): list endpoint supports status filter, sort_by (last_date_contacted asc/desc), partial case-insensitive search on company and source, and follow_up_due flag.

---

## Acceptance Criteria
- [/] **AC1:** Filter by status returns only records with that status
- [/] **AC2:** Sort by last_date_contacted asc/desc orders correctly
- [/] **AC3:** Search `q` returns partial case-insensitive matches on company or source
- [/] **AC4:** `follow_up_due=true` returns only records due today or earlier
- [/] **AC5:** Invalid `page_size` or `page` returns 400

---

## Design & Technical Notes
- Query params: status, q, sort_by, order, follow_up_due, page, page_size
- FilterSet using django-filter
- Indexes planned: B-tree on status, last_date_contacted; trigram on company/source

---

## Dependencies
- Blocked by: PTK-001
- Blocks: None
