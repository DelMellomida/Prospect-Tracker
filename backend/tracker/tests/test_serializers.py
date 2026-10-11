import pytest

from tracker.models import FollowUp, Note, Record
from tracker.serializers import RecordDetailSerializer


@pytest.mark.django_db
def test_record_detail_serializer_includes_notes_and_follow_ups():
    record = Record.objects.create(
        company='Test Company',
        status='contacted',
    )
    note = Note.objects.create(
        record_id=record,
        content='This is a test note.'
    )
    follow_up = FollowUp.objects.create(
        record_id=record,
        follow_up_date='2026-10-11',
        content='This is a test follow-up.'
    )

    serializer = RecordDetailSerializer(record)
    data = serializer.data

    assert data['record_id'] == record.record_id
    assert data['notes'][0]['content'] == note.content
    assert data['follow_up']['content'] == follow_up.content
    assert data['follow_up']['follow_up_date'] == str(follow_up.follow_up_date)
