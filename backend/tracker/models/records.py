from django.contrib.postgres.indexes import GinIndex
from django.db import models
from django.db.models import Q

from .choices import Sources, Status


class Record(models.Model):
    record_id = models.AutoField(primary_key=True)
    company = models.CharField(blank=False, null=False, max_length=255)
    status = models.CharField(max_length=50, choices=Status.choices)
    company_contact_no = models.CharField(max_length=20, blank=True, null=True)
    company_email = models.EmailField(blank=True, null=True)
    last_date_contacted = models.DateField(blank=True, null=True)
    technical_audit = models.TextField(blank=True, null=True)
    source = models.CharField(choices=Sources.choices, max_length=50, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.company

    class Meta:
        db_table = 'records'
        constraints = [
            models.CheckConstraint(
                condition=Q(status__in=Status.values),
                name='record_status_valid',
            ),
            models.CheckConstraint(
                condition=Q(source__in=Sources.values),
                name='record_source_valid',
            ),
        ]
        indexes = [
            models.Index(fields=["status"], name="records_status_idx"),
            models.Index(fields=["last_date_contacted"], name="records_last_contacted_idx"),
            GinIndex(fields=["company"], opclasses=["gin_trgm_ops"], name="records_company_trgm"),
            GinIndex(fields=["source"], opclasses=["gin_trgm_ops"], name="records_source_trgm"),
        ]
