import csv
from datetime import date
from io import StringIO
from unittest.mock import patch

import pytest
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import connection
from rest_framework.test import APIClient

from tracker.models import AuditLog, Record


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
def test_record_export_downloads_all_records_without_pagination():
    records = [
        Record.objects.create(company=f'Company {index}', status='contacted')
        for index in range(12)
    ]

    response = APIClient().get('/api/v1/records/export')

    assert response.status_code == 200
    assert response['Content-Type'] == 'text/csv'
    assert response['Content-Disposition'] == 'attachment; filename="records.csv"'
    rows = list(csv.DictReader(StringIO(response.content.decode('utf-8'))))
    assert len(rows) == 12
    assert [row['Record ID'] for row in rows] == [str(record.pk) for record in records]
    assert [row['Company'] for row in rows] == [record.company for record in records]


@pytest.mark.django_db
def test_record_export_preserves_all_fields_and_csv_special_characters():
    record = Record.objects.create(
        company='Café, "Example"',
        status='ongoing',
        company_contact_no='09123456789',
        company_email='contact@example.com',
        last_date_contacted=date(2026, 10, 15),
        technical_audit='First line, with a comma\nSecond "quoted" line',
        source='linkedin',
    )

    response = APIClient().get('/api/v1/records/export')

    assert response.status_code == 200
    rows = list(csv.DictReader(StringIO(response.content.decode('utf-8'))))
    assert rows == [{
        'Record ID': str(record.pk),
        'Company': 'Café, "Example"',
        'Status': 'ongoing',
        'Contact No': '09123456789',
        'Email': 'contact@example.com',
        'Last Date Contacted': '2026-10-15',
        'Technical Audit': 'First line, with a comma\nSecond "quoted" line',
        'Source': 'linkedin',
        'Created At': str(record.created_at),
        'Updated At': str(record.updated_at),
    }]


@pytest.mark.django_db
def test_record_export_returns_headers_when_no_records_exist():
    response = APIClient().get('/api/v1/records/export')

    assert response.status_code == 200
    rows = list(csv.reader(StringIO(response.content.decode('utf-8'))))
    assert rows == [[
        'Record ID', 'Company', 'Status', 'Contact No', 'Email',
        'Last Date Contacted', 'Technical Audit', 'Source',
        'Created At', 'Updated At',
    ]]


@pytest.mark.django_db
def test_record_export_includes_records_created_since_previous_export():
    client = APIClient()
    client.get('/api/v1/records/export')
    record = Record.objects.create(company='New company', status='contacted')

    response = client.get('/api/v1/records/export')

    assert response.status_code == 200
    rows = list(csv.DictReader(StringIO(response.content.decode('utf-8'))))
    assert len(rows) == 1
    assert rows[0]['Record ID'] == str(record.pk)
    assert rows[0]['Contact No'] == ''
    assert rows[0]['Last Date Contacted'] == ''


@pytest.mark.django_db
def test_record_import_requires_a_file():
    response = APIClient().post('/api/v1/records/import', {}, format='multipart')

    assert response.status_code == 400
    assert response.data == {'error': 'Please upload a CSV using the file field.'}
    assert not Record.objects.exists()


@pytest.mark.django_db
def test_record_import_requires_the_file_field_name():
    uploaded_file = SimpleUploadedFile(
        'records.csv', b'Company,Status\nExample,contacted\n', content_type='text/csv',
    )

    response = APIClient().post(
        '/api/v1/records/import', {'upload': uploaded_file}, format='multipart',
    )

    assert response.status_code == 400
    assert response.data == {'error': 'Please upload a CSV using the file field.'}
    assert not Record.objects.exists()


@pytest.mark.django_db
def test_record_import_creates_a_record_and_audit_entry():
    uploaded_file = SimpleUploadedFile(
        'records.csv', b'Company,Status\nExample,contacted\n', content_type='text/csv',
    )

    response = APIClient().post(
        '/api/v1/records/import', {'file': uploaded_file}, format='multipart',
    )

    assert response.status_code == 201
    assert response.data == {'created': 1}
    record = Record.objects.get(company='Example')
    log = AuditLog.objects.get(entity_type='record', entity_id=record.pk, action='create')
    assert log.initiator == 'anonymous'
    assert 'Example' in log.new_value


@pytest.mark.django_db(transaction=True)
def test_record_import_audits_every_record_and_clears_cache_after_commit():
    uploaded_file = SimpleUploadedFile(
        'records.csv',
        b'company,status\nFirst,contacted\nSecond,ongoing\n',
        content_type='text/csv',
    )
    cache.set('import-test-stale-records', 'stale')
    clear_cache = cache.clear

    def clear_after_commit():
        assert not connection.in_atomic_block
        assert Record.objects.count() == 2
        assert AuditLog.objects.filter(entity_type='record', action='create').count() == 2
        return clear_cache()

    try:
        with patch('tracker.views.cache.clear', side_effect=clear_after_commit) as clear:
            response = APIClient().post(
                '/api/v1/records/import', {'file': uploaded_file}, format='multipart',
            )
        assert response.status_code == 201
        assert response.data == {'created': 2}
        clear.assert_called_once_with()
        assert cache.get('import-test-stale-records') is None
        assert set(AuditLog.objects.values_list('entity_id', flat=True)) == set(
            Record.objects.values_list('record_id', flat=True)
        )
    finally:
        cache.delete('import-test-stale-records')


@pytest.mark.django_db(transaction=True)
def test_record_import_invalid_row_rolls_back_records_and_audits_without_clearing_cache():
    uploaded_file = SimpleUploadedFile(
        'records.csv', b'Company,Status\nValid,contacted\nInvalid,unknown\n',
        content_type='text/csv',
    )
    with patch('tracker.views.cache.clear') as clear:
        response = APIClient().post(
            '/api/v1/records/import', {'file': uploaded_file}, format='multipart',
        )

    assert response.status_code == 400
    assert int(response.data['row']) == 3
    assert 'status' in response.data['errors']
    assert not Record.objects.exists()
    assert not AuditLog.objects.exists()
    clear.assert_not_called()


@pytest.mark.django_db
def test_record_import_accepts_exported_csv_with_generated_fields_and_empty_values():
    original = Record.objects.create(company='Exported company', status='contacted')
    client = APIClient()
    exported = client.get('/api/v1/records/export')
    uploaded_file = SimpleUploadedFile('records.csv', exported.content, content_type='text/csv')

    response = client.post('/api/v1/records/import', {'file': uploaded_file}, format='multipart')

    assert response.status_code == 201
    imported = Record.objects.exclude(pk=original.pk).get()
    assert imported.company == original.company
    assert imported.last_date_contacted is None
    assert imported.source is None
    assert AuditLog.objects.filter(entity_id=imported.pk, action='create').exists()


@pytest.mark.django_db
@pytest.mark.parametrize('content', [
    b'',
    b'Company,Status\n',
    b'Company\nExample\n',
    b'Company,Status,Unexpected\nExample,contacted,value\n',
    b'Company,Status,company\nExample,contacted,Duplicate\n',
    b'Company,Status\nExample\n',
    b'Company,Status\nExample,contacted,extra\n',
    b'Company,Status\n"Unclosed quote,contacted\n',
    b'Company,Status\n\xff,contacted\n',
])
def test_record_import_rejects_invalid_csv_without_writes_or_cache_clear(content):
    uploaded_file = SimpleUploadedFile('records.csv', content, content_type='text/csv')
    with patch('tracker.views.cache.clear') as clear:
        response = APIClient().post(
            '/api/v1/records/import', {'file': uploaded_file}, format='multipart',
        )

    assert response.status_code == 400
    assert not Record.objects.exists()
    assert not AuditLog.objects.exists()
    clear.assert_not_called()
