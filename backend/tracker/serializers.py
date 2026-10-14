from django.utils import timezone
from rest_framework import serializers

from .models import AuditLog, FollowUp, Note, Record


class NoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Note
        fields = [
            'note_id',
            'record_id',
            'content',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'note_id', 
            'record_id',
            'created_at', 
            'updated_at'
        ]

class FollowUpSerializer(serializers.ModelSerializer):
    class Meta:
        model = FollowUp
        fields = [
            'follow_up_id',
            'record_id',
            'follow_up_date',
            'content',
            'created_at',
            'updated_at',
        ]

class RecordWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Record
        fields = [
            'company',
            'status',
            'company_contact_no',
            'company_email',
            'last_date_contacted',
            'technical_audit',
            'source',
        ]

class RecordListSerializer(serializers.ModelSerializer):
    follow_up_date = serializers.DateField(
        source='follow_up.follow_up_date',
        read_only=True,
        allow_null=True,
    )
    follow_up_due = serializers.SerializerMethodField()

    class Meta:
        model = Record
        fields = [
            'record_id',
            'company',
            'status',
            'company_contact_no',
            'company_email',
            'created_at',
            'updated_at',
            'follow_up_date',
            'follow_up_due',
        ]
        read_only_fields = [
            'record_id',
            'created_at',
            'updated_at',
        ]

    def get_follow_up_due(self, record):
        follow_up = getattr(record, 'follow_up', None)
        if follow_up and follow_up.follow_up_date:
            return follow_up.follow_up_date <= timezone.localdate()
        return False

class RecordDetailSerializer(serializers.ModelSerializer):
    notes = NoteSerializer(many=True, read_only=True)
    follow_up = FollowUpSerializer(read_only=True)

    class Meta:
        model = Record
        fields = [
            'record_id',
            'company',
            'status',
            'company_contact_no',
            'company_email',
            'last_date_contacted',
            'technical_audit',
            'source',
            'created_at',
            'updated_at',
            'notes',
            'follow_up',
        ]
        read_only_fields = [
            'record_id',
            'created_at',
            'updated_at',
        ]


class AuditLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuditLog
        fields = [
            'log_id', 'entity_type', 'entity_id', 'action', 'initiator',
            'old_value', 'new_value', 'created_at',
        ]
        read_only_fields = fields
