from rest_framework import status, viewsets
from rest_framework.response import Response

from .models import Record
from .serializers import RecordDetailSerializer, RecordListSerializer, RecordWriteSerializer
from .services import create_record, delete_record, update_record


class EmptyListViewSet(viewsets.ViewSet):
    def list(self, request):
        return Response([])


class RecordViewSet(viewsets.ModelViewSet):
    queryset = Record.objects.all().order_by('record_id')
    serializer_class = RecordWriteSerializer
    
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


class NoteViewSet(EmptyListViewSet):
    pass


class LogViewSet(EmptyListViewSet):
    pass
