from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

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
from .filters import RecordFilter


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
