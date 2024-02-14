from django.db.models import TextChoices

class NoticeScope(TextChoices):
    TODOS = 'TODOS'
    PERSONAL = 'PRSNL'