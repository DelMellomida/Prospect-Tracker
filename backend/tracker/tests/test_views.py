import pytest
from rest_framework.test import APIClient

from tracker.models import Record


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
