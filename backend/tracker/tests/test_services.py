import pytest

from tracker.models import AuditLog, FollowUp, Note, Record
from tracker.services import create_record, delete_record, update_record


@pytest.mark.django_db
def test_create_record_creates_record_and_audit_log():
    data = {
        'company': 'Test Company',
        'status': 'contacted',
        'company_contact_no': '1234567890',
        'company_email': 'test@example.com',
        'last_date_contacted': '2024-06-01',
        'technical_audit': 'Problem in SEO',
        'source': 'linkedin',
    }
    record, errors = create_record(data)

    assert errors is None
    assert record is not None
    assert AuditLog.objects.filter(entity_id=record.record_id).exists()

@pytest.mark.django_db
def test_update_record_updates_record_and_audit_log():
    record = Record.objects.create(
        company='Old Company',
        status='contacted',
    )

    updated_record, errors = update_record(record, {
        'company':'New Company',
        'status':'ongoing',
    })

    assert errors is None
    assert updated_record.company == 'New Company'
    assert updated_record.status == 'ongoing'
    assert AuditLog.objects.filter(
        entity_id=record.record_id,
        action='update'
    ).exists()

@pytest.mark.django_db
def test_delete_record_deletes_record_and_creates_audit_log():
    record = Record.objects.create(
        company='Delete Company',
        status='contacted',
    )
    note = Note.objects.create(
        record_id=record,
        content='This is a note for the deleted record.'
    )
    follow_up = FollowUp.objects.create(
        record_id=record,
        follow_up_date='2026-10-11',
        content='This is a follow-up for the deleted record.'
    )

    record_id, errors = delete_record(record, {'initiator': 'test_user'})


    assert errors is None
    assert not Record.objects.filter(record_id=record_id).exists()
    assert not Note.objects.filter(note_id=note.note_id).exists()
    assert not FollowUp.objects.filter(follow_up_id=follow_up.follow_up_id).exists()
    assert AuditLog.objects.filter(
        entity_id=record_id,
        action='delete'
    ).exists()
