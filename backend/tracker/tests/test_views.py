import pytest
from rest_framework.test import APIClient

from tracker.models import Note, Record


@pytest.mark.django_db
def test_record_list_is_paginated_by_default():
    for index in range(12):
        Record.objects.create(
            company=f'Company {index}',
            status='contacted',
        )

    client = APIClient()
    response = client.get('/api/v1/records')

    assert response.status_code == 200
    assert 'results' in response.data
    assert len(response.data['results']) == 10
    assert response.data['count'] == 12

@pytest.mark.django_db
def test_record_list_accepts_allowed_page_size():
    for index in range(25):
        Record.objects.create(
            company=f'Company {index}',
            status='contacted',
        )

    client = APIClient()
    response = client.get('/api/v1/records?page_size=20')

    assert response.status_code == 200
    assert len(response.data['results']) == 20

@pytest.mark.django_db
def test_record_list_rejects_disallowed_page_size():
    client = APIClient()
    response = client.get('/api/v1/records?page_size=37')

    assert response.status_code == 400


@pytest.mark.django_db
def test_create_note_for_record():
    record = Record.objects.create(
        company='Test Company',
        status='contacted',
    )

    client = APIClient()
    response = client.post(
        f'/api/v1/records/{record.record_id}/notes',
        {'content': 'Client asked for pricing.'},
        format='json',
    )

    assert response.status_code == 201
    assert response.data['record_id'] == record.record_id
    assert response.data['content'] == 'Client asked for pricing.'
    assert response.data['created_at']
    assert response.data['updated_at']
    assert Note.objects.filter(record_id=record, content='Client asked for pricing.').exists()


@pytest.mark.django_db
def test_update_note_content():
    record = Record.objects.create(
        company='Test Company',
        status='contacted',
    )
    note = Note.objects.create(
        record_id=record,
        content='Initial note.',
    )
    old_updated_at = note.updated_at

    client = APIClient()
    response = client.patch(
        f'/api/v1/notes/{note.note_id}',
        {'content': 'Updated note.'},
        format='json',
    )

    note.refresh_from_db()
    assert response.status_code == 200
    assert response.data['content'] == 'Updated note.'
    assert note.content == 'Updated note.'
    assert note.updated_at > old_updated_at


@pytest.mark.django_db
def test_delete_note_removes_note():
    record = Record.objects.create(
        company='Test Company',
        status='contacted',
    )
    note = Note.objects.create(
        record_id=record,
        content='Delete this note.',
    )

    client = APIClient()
    response = client.delete(f'/api/v1/notes/{note.note_id}')

    assert response.status_code == 204
    assert not Note.objects.filter(note_id=note.note_id).exists()
