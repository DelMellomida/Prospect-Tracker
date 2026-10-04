from django.db import models


class Status(models.TextChoices):
    CONTACTED = 'contacted', 'contacted'
    ONGOING = 'ongoing', 'ongoing'
    COMPLETION = 'completion', 'completion'
    DROPPED = 'dropped', 'dropped'


class Sources(models.TextChoices):
    REDDIT = 'reddit', 'reddit'
    DISCORD = 'discord', 'discord'
    FACEBOOK = 'facebook', 'facebook'
    LINKEDIN = 'linkedin', 'linkedin'
    OTHERS = 'others', 'others'


class Type(models.TextChoices):
    RECORD = 'record', 'record'
    NOTE = 'note', 'note'
    FOLLOW_UP = 'follow_up', 'follow_up'


class Actions(models.TextChoices):
    CREATE = 'create', 'create'
    UPDATE = 'update', 'update'
    DELETE = 'delete', 'delete'
