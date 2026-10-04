from django.db import models
from django.db.models import Q

from .choices import Actions, Type


class AuditLog(models.Model):
    log_id = models.AutoField(primary_key=True)
    entity_type = models.CharField(choices=Type.choices, max_length=50, blank=False, null=False)
    entity_id = models.IntegerField(blank=False, null=False)
    action = models.CharField(choices=Actions.choices, max_length=255, blank=False, null=False)
    initiator = models.CharField(max_length=255, blank=False, null=False, default='system')
    old_value = models.TextField(blank=True, null=True)
    new_value = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.action} {self.entity_type} {self.entity_id}'

    class Meta:
        db_table = 'audit_logs'
        constraints = [
            models.CheckConstraint(
                condition=Q(entity_type__in=Type.values),
                name='audit_log_entity_type_valid',
            ),
            models.CheckConstraint(
                condition=Q(action__in=Actions.values),
                name='audit_log_action_valid',
            ),
        ]
