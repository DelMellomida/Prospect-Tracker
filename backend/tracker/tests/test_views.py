import datetime

import pytest
from django.utils import timezone
from rest_framework.test import APIClient

from tracker.models import FollowUp, Note, Record


@pytest.mark.django_db
def test_record_list_is_paginated_by_default():
    for index in range(12):
        Record.objects.create(
            company=f'Company {index}',
            status='contacted',
        )

    client = APIClient()
    response_company = client.get('/api/v1/records')

    assert response_company.status_code == 200
    assert 'results' in response_company.data
    assert len(response_company.data['results']) == 10
    assert response_company.data['count'] == 12

@pytest.mark.django_db
def test_record_list_accepts_allowed_page_size():
    for index in range(25):
        Record.objects.create(
            company=f'Company {index}',
            status='contacted',
        )

    client = APIClient()
    response_company = client.get('/api/v1/records?page_size=20')

    assert response_company.status_code == 200
    assert len(response_company.data['results']) == 20

@pytest.mark.django_db
def test_record_list_rejects_disallowed_page_size():
    client = APIClient()
    response_company = client.get('/api/v1/records?page_size=37')

    assert response_company.status_code == 400


@pytest.mark.django_db
def test_create_note_for_record():
    record = Record.objects.create(
        company='Test Company',
        status='contacted',
    )

    client = APIClient()
    response_company = client.post(
        f'/api/v1/records/{record.record_id}/notes',
        {'content': 'Client asked for pricing.'},
        format='json',
    )

    assert response_company.status_code == 201
    assert response_company.data['record_id'] == record.record_id
    assert response_company.data['content'] == 'Client asked for pricing.'
    assert response_company.data['created_at']
    assert response_company.data['updated_at']
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
    response_company = client.patch(
        f'/api/v1/notes/{note.note_id}',
        {'content': 'Updated note.'},
        format='json',
    )

    note.refresh_from_db()
    assert response_company.status_code == 200
    assert response_company.data['content'] == 'Updated note.'
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
    response_company = client.delete(f'/api/v1/notes/{note.note_id}')

    assert response_company.status_code == 204
    assert not Note.objects.filter(note_id=note.note_id).exists()

@pytest.mark.django_db
def test_q_parameter_is_case_insensitive():
    Record.objects.create(company='Alpha Corp', status='contacted', source='linkedin')
    Record.objects.create(company='Beta LLC', status='ongoing', source='reddit')
    Record.objects.create(company='Gamma Inc', status='contacted', source='reddit')

    client = APIClient()
    response_company = client.get('/api/v1/records?q=alp')
    response_source = client.get('/api/v1/records?q=RED')

    assert response_company.status_code == 200
    assert response_source.status_code == 200
    assert len(response_company.data['results']) == 1
    assert len(response_source.data['results']) == 2
    assert response_company.data['results'][0]['company'] == 'Alpha Corp'
    assert {
        record['company']
        for record in response_source.data['results']
    } == {'Beta LLC', 'Gamma Inc'}

@pytest.mark.django_db
def test_status_parameter_filters_records():
    Record.objects.create(company='Alpha Corp', status='contacted', source='linkedin')
    Record.objects.create(company='Beta LLC', status='ongoing', source='reddit')
    Record.objects.create(company='Gamma Inc', status='contacted', source='reddit')

    client = APIClient()
    response_contacted = client.get('/api/v1/records?status=contacted')
    response_ongoing = client.get('/api/v1/records?status=ongoing')

    assert response_contacted.status_code == 200
    assert response_ongoing.status_code == 200
    assert len(response_contacted.data['results']) == 2
    assert len(response_ongoing.data['results']) == 1
    assert {
        record['company']
        for record in response_contacted.data['results']
    } == {'Alpha Corp', 'Gamma Inc'}
    assert response_ongoing.data['results'][0]['company'] == 'Beta LLC'

@pytest.mark.django_db
def test_sort_by_last_date_contacted_orders_records_ascending_and_descending():
    Record.objects.create(company='Alpha Corp', status='contacted', source='linkedin', last_date_contacted='2024-01-01')
    Record.objects.create(company='Beta LLC', status='ongoing', source='reddit', last_date_contacted='2024-02-01')
    Record.objects.create(company='Gamma Inc', status='contacted', source='reddit', last_date_contacted='2024-03-01')

    client = APIClient()
    response_asc = client.get('/api/v1/records?sort_by=last_date_contacted&order=asc')
    response_desc = client.get('/api/v1/records?sort_by=last_date_contacted&order=desc')

    assert response_asc.status_code == 200
    assert response_desc.status_code == 200
    assert len(response_asc.data['results']) == 3
    assert len(response_desc.data['results']) == 3
    assert response_asc.data['results'][0]['company'] == 'Alpha Corp'
    assert response_asc.data['results'][1]['company'] == 'Beta LLC'
    assert response_asc.data['results'][2]['company'] == 'Gamma Inc'
    assert response_desc.data['results'][0]['company'] == 'Gamma Inc'
    assert response_desc.data['results'][1]['company'] == 'Beta LLC'
    assert response_desc.data['results'][2]['company'] == 'Alpha Corp'

@pytest.mark.django_db
def test_follow_up_due_true_returns_records_due_today_or_earlier():
    record_one = Record.objects.create(company='Alpha Corp', status='contacted')
    record_two = Record.objects.create(company='Beta LLC', status='ongoing')
    record_three = Record.objects.create(company='Gamma Inc', status='contacted')
    record_four = Record.objects.create(company='Delta Ltd', status='ongoing')

    today = timezone.localdate()
    yesterday = today - datetime.timedelta(days=1)
    tomorrow = today + datetime.timedelta(days=1)

    FollowUp.objects.create(record_id=record_one, follow_up_date=yesterday)
    FollowUp.objects.create(record_id=record_two, follow_up_date=today)
    FollowUp.objects.create(record_id=record_three, follow_up_date=tomorrow)

    client = APIClient()
    response_due = client.get('/api/v1/records?follow_up_due=true')

    assert response_due.status_code == 200
    assert len(response_due.data['results']) == 2
    assert {record['company'] for record in response_due.data['results']} == {'Alpha Corp', 'Beta LLC'}

@pytest.mark.django_db
def test_record_list_rejects_disallowed_page_size():
    client = APIClient()
    response_page_size = client.get('/api/v1/records?page_size=37')
    response_page = client.get('/api/v1/records?page=abc')

    assert response_page_size.status_code == 400
    assert response_page.status_code == 400