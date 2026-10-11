from .models import AuditLog, Note, Record
from .serializers import NoteSerializer, RecordWriteSerializer

# Record CRUD operations
def create_record(data):
    serializer = RecordWriteSerializer(data=data)
    if serializer.is_valid():
        record = serializer.save()
        AuditLog.objects.create(
            entity_type='record',
            entity_id=record.record_id,
            action='create',
            initiator=data.get('initiator', 'system'),
            old_value=None,
            new_value=serializer.data,
        )
        return record, None
    return None, serializer.errors

def update_record(record, data):
    serializer = RecordWriteSerializer(record, data=data, partial=True)
    old_value = RecordWriteSerializer(record).data
    if serializer.is_valid():
        record = serializer.save()
        AuditLog.objects.create(
            entity_type='record',
            entity_id=record.record_id,
            action='update',
            initiator=data.get('initiator', 'system'),
            old_value=old_value,
            new_value=serializer.data,
        )
        return record, None
    return None, serializer.errors

def delete_record(record, data) -> tuple[int, None]:
    old_record_id = record.record_id
    old_value = RecordWriteSerializer(record).data
    record.delete()
    AuditLog.objects.create(
        entity_type='record',
        entity_id=old_record_id,
        action='delete',
        initiator=data.get('initiator', 'system'),
        old_value=old_value,
        new_value=None,
    )
    return old_record_id, None

# Notes CRUD operations
def create_note(record, data):
    serializer = NoteSerializer(data=data)
    if serializer.is_valid():
        note = serializer.save(record_id=record)
        AuditLog.objects.create(
            entity_type='note',
            entity_id=note.note_id,
            action='create',
            initiator=data.get('initiator', 'system'),
            old_value=None,
            new_value=serializer.data,
        )
        return note, None
    return None, serializer.errors

def update_note(note, data):
    serializer = NoteSerializer(note, data=data, partial=True)
    old_value = NoteSerializer(note).data
    if serializer.is_valid():
        note = serializer.save()
        AuditLog.objects.create(
            entity_type='note',
            entity_id=note.note_id,
            action='update',
            initiator=data.get('initiator', 'system'),
            old_value=old_value,
            new_value=serializer.data,
        )
        return note, None
    return None, serializer.errors

def delete_note(note, data) -> tuple[int, None]:
    old_note_id = note.note_id
    old_value = NoteSerializer(note).data
    note.delete()
    AuditLog.objects.create(
        entity_type='note',
        entity_id=old_note_id,
        action='delete',
        initiator=data.get('initiator', 'system'),
        old_value=old_value,
        new_value=None,
    )
    return old_note_id, None