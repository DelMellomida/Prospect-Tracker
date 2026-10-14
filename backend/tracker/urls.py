from rest_framework import routers

from . import views

router = routers.DefaultRouter(trailing_slash=False)
router.register(r'records', views.RecordViewSet, basename='record')
router.register(r'notes', views.NoteViewSet, basename='note')
router.register(r'audit-logs', views.LogViewSet, basename='audit-log')
router.register(r'logs', views.LogViewSet, basename='log')

urlpatterns = router.urls
