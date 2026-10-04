from rest_framework import viewsets
from rest_framework.response import Response


class EmptyListViewSet(viewsets.ViewSet):
    def list(self, request):
        return Response([])


class RecordViewSet(EmptyListViewSet):
    pass


class NoteViewSet(EmptyListViewSet):
    pass


class LogViewSet(EmptyListViewSet):
    pass
