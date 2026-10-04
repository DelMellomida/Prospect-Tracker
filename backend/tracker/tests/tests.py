import pytest
from django.db import connection

from tracker.models import Record, Status


@pytest.mark.django_db
def test_record_can_be_created_in_postgres():
    assert connection.vendor == 'postgresql'

    record = Record.objects.create(
        company='Acme Corp',
        status=Status.CONTACTED,
        company_email='hello@example.com',
    )

    assert record.record_id is not None
