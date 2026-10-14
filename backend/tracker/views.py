import csv
from io import StringIO

from django.core.cache import cache
from django.db import transaction
from django.http import HttpResponse
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from .filters import RecordFilter
from .models import Note, Record
from .serializers import (
    NoteSerializer,
    RecordDetailSerializer,
    RecordListSerializer,
    RecordWriteSerializer,
)
from .services import (
    create_note,
    create_record,
    delete_note,
    delete_record,
    update_note,
    update_record,
)

FORMULA_PREFIXES = ('=', '+', '-', '@')


def _escape_formula_text(value):
    if isinstance(value, str) and value.startswith(FORMULA_PREFIXES):
        return f"'{value}"
    return value


def _unescape_formula_text(value):
    if (
        isinstance(value, str)
        and len(value) > 1
        and value[0] == "'"
        and value[1] in FORMULA_PREFIXES
    ):
        return value[1:]
    return value


class EmptyListViewSet(viewsets.ViewSet):
    def list(self, request):
        return Response([])


class RecordViewSet(viewsets.ModelViewSet):
    queryset = Record.objects.all().order_by('record_id')
    serializer_class = RecordWriteSerializer
    filterset_class = RecordFilter
    
    def get_serializer_class(self):
        if self.action == 'list':
            return RecordListSerializer
        if self.action == 'retrieve':
            return RecordDetailSerializer
        return RecordWriteSerializer

    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        data['initiator'] = request.user.username if request.user.is_authenticated else 'anonymous'
        record, errors = create_record(data)
        if record:
            serializer = self.get_serializer(record)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(errors, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, *args, **kwargs):
        data = request.data.copy()
        record = self.get_object()
        data['initiator'] = request.user.username if request.user.is_authenticated else 'anonymous'
        record, errors = update_record(record, data)
        if record:
            serializer = self.get_serializer(record)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        data = request.data.copy()
        record = self.get_object()
        data['initiator'] = request.user.username if request.user.is_authenticated else 'anonymous'
        record_id, errors = delete_record(record, data)
        if errors:
            return Response(errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'])
    def export(self, request, *args, **kwargs):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="records.csv"'
        writer = csv.writer(response)
        writer.writerow([
            'Record ID', 'Company', 'Status', 'Contact No', 'Email',
            'Last Date Contacted', 'Technical Audit', 'Source',
            'Created At', 'Updated At',
        ])
        for record in self.get_queryset():
            writer.writerow([
                record.record_id,
                _escape_formula_text(record.company),
                record.status,
                _escape_formula_text(record.company_contact_no),
                record.company_email,
                record.last_date_contacted,
                _escape_formula_text(record.technical_audit),
                record.source,
                record.created_at,
                record.updated_at
            ])
        return response

    @action(detail=False, methods=['post'], url_path='import')
    def import_records(self, request, *args, **kwargs):
        uploaded_file = request.FILES.get('file')
        if uploaded_file is None:
            return Response(
                {'error': 'Please upload a CSV using the file field.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        column_fields = {
            'Company': 'company',
            'Status': 'status',
            'Contact No': 'company_contact_no',
            'Email': 'company_email',
            'Last Date Contacted': 'last_date_contacted',
            'Technical Audit': 'technical_audit',
            'Source': 'source',
        }
        generated_columns = {'Record ID', 'Created At', 'Updated At',
                             'record_id', 'created_at', 'updated_at'}
        initiator = request.user.username if request.user.is_authenticated else 'anonymous'
        try:
            reader = csv.DictReader(
                StringIO(uploaded_file.read().decode('utf-8-sig')), strict=True,
            )
            headers = reader.fieldnames or []
            is_exported_file = {'Record ID', 'Created At', 'Updated At'}.issubset(headers)
            fields = [column_fields.get(header, header) for header in headers]
            if not {'company', 'status'}.issubset(fields):
                raise ValidationError({'error': 'CSV must include company and status columns.'})
            if len(fields) != len(set(fields)) or any(
                field not in column_fields.values() and header not in generated_columns
                for header, field in zip(headers, fields, strict=True)
            ):
                raise ValidationError({'error': 'CSV contains duplicate or unknown columns.'})

            with transaction.atomic():
                count = 0
                for row_number, row in enumerate(reader, start=2):
                    if None in row or any(value is None for value in row.values()):
                        raise ValidationError({
                            'row': row_number, 'error': 'Column count mismatch.',
                        })
                    data = {
                        column_fields.get(header, header): (
                            _unescape_formula_text(value) if is_exported_file else value
                        )
                        for header, value in row.items() if header not in generated_columns
                    }
                    for field in ('last_date_contacted', 'source'):
                        if data.get(field) == '':
                            data[field] = None
                    data['initiator'] = initiator
                    record, errors = create_record(data)
                    if errors is not None:
                        raise ValidationError({'row': row_number, 'errors': errors})
                    count += 1
                if not count:
                    raise ValidationError({'error': 'CSV must contain at least one record.'})
                transaction.on_commit(cache.clear)
        except (UnicodeDecodeError, csv.Error):
            raise ValidationError({'error': 'Upload a valid UTF-8 CSV file.'}) from None
        return Response({'created': count}, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'], url_path='notes')
    def create_note(self, request, *args, **kwargs):
        record = self.get_object()
        data = request.data.copy()
        data['initiator'] = request.user.username if request.user.is_authenticated else 'anonymous'
        note, errors = create_note(record, data)
        if note:
            serializer = NoteSerializer(note)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(errors, status=status.HTTP_400_BAD_REQUEST)


class NoteViewSet(viewsets.ModelViewSet):
    queryset = Note.objects.all().order_by('updated_at')
    serializer_class = NoteSerializer

    def partial_update(self, request, *args, **kwargs):
        note = self.get_object()
        data = request.data.copy()
        data['initiator'] = request.user.username if request.user.is_authenticated else 'anonymous'
        note, errors = update_note(note, data)
        if note:
            serializer = NoteSerializer(note)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        data = request.data.copy()
        note = self.get_object()
        data['initiator'] = request.user.username if request.user.is_authenticated else 'anonymous'
        note_id, errors = delete_note(note, data)
        if errors:
            return Response(errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_204_NO_CONTENT)


class LogViewSet(EmptyListViewSet):
    pass
