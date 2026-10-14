import json
from functools import partial

from django.core.serializers.json import DjangoJSONEncoder
from django.db import transaction

from .models import AuditLog, FollowUp
from .serializers import FollowUpSerializer, NoteSerializer, RecordWriteSerializer


def _queue_audit(*, entity_type, entity_id, action, initiator, old_value, new_value):
    """Freeze snapshots now; insert the audit only after the outer transaction commits."""
    values = {
        'entity_type': entity_type,
        'entity_id': entity_id,
        'action': action,
        'initiator': initiator,
        'old_value': (
            json.dumps(old_value, cls=DjangoJSONEncoder) if old_value is not None else None
        ),
        'new_value': (
            json.dumps(new_value, cls=DjangoJSONEncoder) if new_value is not None else None
        ),
    }
    transaction.on_commit(partial(AuditLog.objects.create, **values))


# Record CRUD operations
@transaction.atomic
def create_record(data):
    serializer = RecordWriteSerializer(data=data)
    if serializer.is_valid():
        record = serializer.save()
        _queue_audit(
            entity_type='record',
            entity_id=record.record_id,
            action='create',
            initiator=data.get('initiator', 'system'),
            old_value=None,
            new_value=serializer.data,
        )
        return record, None
    return None, serializer.errors

@transaction.atomic
def update_record(record, data, *, partial=True):
    data = data.copy()
    missing = object()
    follow_up_data = data.pop('follow_up', missing)

    serializer = RecordWriteSerializer(record, data=data, partial=partial)
    old_value = RecordWriteSerializer(record).data

    if serializer.is_valid():
        record = serializer.save()
        if follow_up_data is not missing:
            follow_up = FollowUp.objects.filter(record_id=record).first()
            old_follow_up = FollowUpSerializer(follow_up).data if follow_up else None
            if follow_up_data is None:
                if follow_up:
                    follow_up_id = follow_up.pk
                    follow_up.delete()
                    _queue_audit(
                        entity_type='follow_up', entity_id=follow_up_id, action='delete',
                        initiator=data.get('initiator', 'system'),
                        old_value=old_follow_up, new_value=None,
                    )
            else:
                follow_up, created = FollowUp.objects.update_or_create(
                    record_id=record, defaults=follow_up_data,
                )
                _queue_audit(
                    entity_type='follow_up', entity_id=follow_up.pk,
                    action='create' if created else 'update',
                    initiator=data.get('initiator', 'system'),
                    old_value=old_follow_up, new_value=FollowUpSerializer(follow_up).data,
                )

        _queue_audit(
            entity_type='record',
            entity_id=record.record_id,
            action='update',
            initiator=data.get('initiator', 'system'),
            old_value=old_value,
            new_value=serializer.data,
        )
        return record, None
    return None, serializer.errors

@transaction.atomic
def delete_record(record, data) -> tuple[int, None]:
    old_record_id = record.record_id
    old_value = RecordWriteSerializer(record).data
    for note in record.notes.all():
        _queue_audit(
            entity_type='note', entity_id=note.pk, action='delete',
            initiator=data.get('initiator', 'system'),
            old_value=NoteSerializer(note).data, new_value=None,
        )
    follow_up = FollowUp.objects.filter(record_id=record).first()
    if follow_up:
        _queue_audit(
            entity_type='follow_up', entity_id=follow_up.pk, action='delete',
            initiator=data.get('initiator', 'system'),
            old_value=FollowUpSerializer(follow_up).data, new_value=None,
        )
    record.delete()
    _queue_audit(
        entity_type='record',
        entity_id=old_record_id,
        action='delete',
        initiator=data.get('initiator', 'system'),
        old_value=old_value,
        new_value=None,
    )
    return old_record_id, None

# Notes CRUD operations
@transaction.atomic
def create_note(record, data):
    serializer = NoteSerializer(data=data)
    if serializer.is_valid():
        note = serializer.save(record_id=record)
        _queue_audit(
            entity_type='note',
            entity_id=note.note_id,
            action='create',
            initiator=data.get('initiator', 'system'),
            old_value=None,
            new_value=serializer.data,
        )
        return note, None
    return None, serializer.errors

@transaction.atomic
def update_note(note, data, *, partial=True):
    serializer = NoteSerializer(note, data=data, partial=partial)
    old_value = NoteSerializer(note).data
    if serializer.is_valid():
        note = serializer.save()
        _queue_audit(
            entity_type='note',
            entity_id=note.note_id,
            action='update',
            initiator=data.get('initiator', 'system'),
            old_value=old_value,
            new_value=serializer.data,
        )
        return note, None
    return None, serializer.errors

@transaction.atomic
def delete_note(note, data) -> tuple[int, None]:
    old_note_id = note.note_id
    old_value = NoteSerializer(note).data
    note.delete()
    _queue_audit(
        entity_type='note',
        entity_id=old_note_id,
        action='delete',
        initiator=data.get('initiator', 'system'),
        old_value=old_value,
        new_value=None,
    )
    return old_note_id, None
