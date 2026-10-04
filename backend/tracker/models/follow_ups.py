from django.db import models


class FollowUp(models.Model):
    follow_up_id = models.AutoField(primary_key=True)
    record_id = models.OneToOneField('Record', on_delete=models.CASCADE, related_name='follow_up')
    follow_up_date = models.DateField(blank=False, null=False)
    content = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Follow-up {self.follow_up_id}'

    class Meta:
        db_table = 'follow_ups'
        indexes = [
            models.Index(fields=["follow_up_date"], name="follow_up_date_idx"),
        ]
