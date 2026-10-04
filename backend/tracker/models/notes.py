from django.db import models


class Note(models.Model):
    note_id = models.AutoField(primary_key=True)
    record_id = models.ForeignKey('Record', on_delete=models.CASCADE, related_name='notes')
    content = models.TextField(blank=False, null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Note {self.note_id}'

    class Meta:
        db_table = 'notes'
