import json
from datetime import UTC, datetime
from unittest.mock import patch

import pytest
from django.db import transaction
from rest_framework.test import APIClient

from tracker.models import AuditLog, FollowUp, Note, Record
from tracker.services import (
    create_note,
    create_record,
    delete_note,
    delete_record,
    update_note,
    update_record,
)

pytestmark = pytest.mark.django_db(transaction=True)


def test_record_and_note_writes_each_create_one_log_with_json_snapshots():
    record, errors = create_record({'company': 'Before', 'status': 'contacted'})
    assert errors is None
    update_record(record, {'company': 'After'})
    note, errors = create_note(record, {'content': 'Before'})
    assert errors is None
    update_note(note, {'content': 'After'})
    note_id = note.pk
    delete_note(note, {})
    record_id = record.pk
    delete_record(record, {})

    assert AuditLog.objects.count() == 6
    for entity_type, entity_id, field in [
        ('record', record_id, 'company'), ('note', note_id, 'content'),
    ]:
        logs = AuditLog.objects.filter(entity_type=entity_type, entity_id=entity_id)
        assert logs.count() == 3
        created = logs.get(action='create')
        updated = logs.get(action='update')
        deleted = logs.get(action='delete')
        assert created.old_value is None
        assert json.loads(created.new_value)[field] == 'Before'
        assert json.loads(updated.old_value)[field] == 'Before'
        assert json.loads(updated.new_value)[field] == 'After'
        assert json.loads(deleted.old_value)[field] == 'After'
        assert deleted.new_value is None
        assert created.initiator == 'system'
        assert created.created_at.utcoffset().total_seconds() == 0


def test_follow_up_lifecycle_logs_once_per_entity_write():
    record = Record.objects.create(company='Example', status='contacted')
    payload = {'follow_up': {'follow_up_date': '2026-10-15', 'content': 'Before'}}
    update_record(record, payload)
    assert 'follow_up' in payload
    follow_up_id = FollowUp.objects.get(record_id=record).pk
    update_record(record, {'follow_up': {'content': 'After'}})
    update_record(record, {'follow_up': None})

    logs = AuditLog.objects.filter(entity_type='follow_up', entity_id=follow_up_id)
    assert logs.count() == 3
    assert json.loads(logs.get(action='update').old_value)['content'] == 'Before'
    assert json.loads(logs.get(action='update').new_value)['content'] == 'After'
    assert logs.get(action='delete').new_value is None
    assert AuditLog.objects.filter(entity_type='record', action='update').count() == 3
    update_record(record, {'follow_up': None})
    assert logs.count() == 3


def test_cascade_deletion_preserves_history_and_logs_each_deleted_child():
    record, _ = create_record({'company': 'Example', 'status': 'contacted'})
    note, _ = create_note(record, {'content': 'History'})
    update_record(record, {'follow_up': {'follow_up_date': '2026-10-15'}})
    ids = {'record': record.pk, 'note': note.pk,
           'follow_up': FollowUp.objects.get(record_id=record).pk}
    historical_ids = set(AuditLog.objects.values_list('pk', flat=True))
    delete_record(record, {})

    assert not Record.objects.exists()
    assert not Note.objects.exists()
    assert not FollowUp.objects.exists()
    assert historical_ids <= set(AuditLog.objects.values_list('pk', flat=True))
    assert AuditLog.objects.count() == len(historical_ids) + 3
    for entity_type, entity_id in ids.items():
        assert AuditLog.objects.filter(
            entity_type=entity_type, entity_id=entity_id, action='delete',
        ).count() == 1


def test_audits_wait_for_outer_commit_and_are_discarded_on_rollback():
    with transaction.atomic():
        record, _ = create_record({'company': 'Committed', 'status': 'contacted'})
        assert not AuditLog.objects.exists()
        record.company = 'Unsaved mutation'
    assert json.loads(AuditLog.objects.get().new_value)['company'] == 'Committed'

    with pytest.raises(RuntimeError), transaction.atomic():
        create_record({'company': 'Rolled back', 'status': 'contacted'})
        raise RuntimeError('Rollback')
    assert Record.objects.count() == 1
    assert AuditLog.objects.count() == 1


def test_invalid_writes_produce_no_audit_entries():
    record = Record.objects.create(company='Example', status='contacted')
    note = Note.objects.create(record_id=record, content='Before')
    for result in [
        create_record({'status': 'unknown'}), update_record(record, {'status': 'unknown'}),
        create_note(record, {'content': ''}), update_note(note, {'content': ''}),
    ]:
        assert result[0] is None
        assert result[1]
    assert not AuditLog.objects.exists()


def test_post_commit_audit_failure_leaves_committed_record_and_surfaces_error():
    with patch(
        'tracker.services.AuditLog.objects.create', side_effect=RuntimeError('Audit failed'),
    ):
        with pytest.raises(RuntimeError, match='Audit failed'):
            create_record({'company': 'Committed', 'status': 'contacted'})
    assert Record.objects.filter(company='Committed').exists()
    assert not AuditLog.objects.exists()


@pytest.mark.parametrize('method', ['put', 'patch'])
def test_api_updates_audit_records_and_notes_once(method):
    record = Record.objects.create(company='Before', status='contacted')
    note = Note.objects.create(record_id=record, content='Before')
    client = APIClient()
    response = getattr(client, method)(
        f'/api/v1/records/{record.pk}', {'company': 'After', 'status': 'ongoing'}, format='json',
    )
    assert response.status_code == 200
    response = getattr(client, method)(
        f'/api/v1/notes/{note.pk}', {'content': 'After'}, format='json',
    )
    assert response.status_code == 200
    assert AuditLog.objects.count() == 2
    assert set(AuditLog.objects.values_list('entity_type', flat=True)) == {'record', 'note'}


@pytest.mark.parametrize('path', ['/api/v1/audit-logs', '/api/v1/logs'])
def test_audit_api_is_paginated_newest_first_and_read_only(path):
    logs = [AuditLog.objects.create(entity_type='record', entity_id=i, action='create')
            for i in range(12)]
    client = APIClient()
    response = client.get(path)
    assert response.status_code == 200
    assert response.data['count'] == 12
    assert [row['log_id'] for row in response.data['results']] == [
        log.pk for log in reversed(logs)
    ][:10]
    assert len(client.get(path, {'page': 2}).data['results']) == 2
    assert client.get(f'{path}/{logs[0].pk}').status_code == 200
    assert client.post(path, {}, format='json').status_code == 405
    for method in ['put', 'patch', 'delete']:
        assert getattr(client, method)(f'{path}/{logs[0].pk}').status_code == 405
    assert AuditLog.objects.count() == 12


@pytest.mark.parametrize(('params', 'expected'), [
    ({'entity_type': 'note'}, [2]),
    ({'entity_id': 10}, [1, 0]),
    ({'action': 'update'}, [1]),
    ({'created_after': '2026-10-15T12:00:00Z'}, [2, 1]),
    ({'created_before': '2026-10-15T12:00:00Z'}, [1, 0]),
    ({'entity_type': 'record', 'entity_id': 10, 'action': 'update',
      'created_after': '2026-10-15T12:00:00Z',
      'created_before': '2026-10-15T12:00:00Z'}, [1]),
])
def test_audit_filters_individually_and_together(params, expected):
    logs = [
        AuditLog.objects.create(entity_type='record', entity_id=10, action='create'),
        AuditLog.objects.create(entity_type='record', entity_id=10, action='update'),
        AuditLog.objects.create(entity_type='note', entity_id=20, action='delete'),
    ]
    for hour, log in zip([11, 12, 13], logs, strict=True):
        AuditLog.objects.filter(pk=log.pk).update(
            created_at=datetime(2026, 10, 15, hour, tzinfo=UTC),
        )
    response = APIClient().get('/api/v1/audit-logs', params)
    assert response.status_code == 200
    assert [row['log_id'] for row in response.data['results']] == [logs[i].pk for i in expected]


@pytest.mark.parametrize('params', [
    {'created_after': 'bad-date'}, {'created_before': 'bad-date'},
    {'entity_id': 'bad-id'}, {'action': 'unknown'}, {'entity_type': 'unknown'},
])
def test_audit_filters_reject_invalid_values(params):
    assert APIClient().get('/api/v1/audit-logs', params).status_code == 400
