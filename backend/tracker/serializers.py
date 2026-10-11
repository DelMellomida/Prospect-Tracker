from rest_framework import serializers

from .models import FollowUp, Note, Record


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
        ]
        read_only_fields = [
            'record_id',
            'created_at',
            'updated_at',
        ]

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
