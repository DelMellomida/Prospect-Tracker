from .models import AuditLog, Record
from .serializers import RecordWriteSerializer


def create_record(data) -> Record:
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

def update_record(record, data) -> Record:
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
