import logging
from django.utils import timezone

from django.db import models
from django.db.models import F
from rest_framework.exceptions import ValidationError

from core.const import CallbackStatus

logger = logging.getLogger(__name__)


class BaseModel(models.Model):
    class Meta:
        abstract = True

    date_created = models.DateTimeField('Date created', auto_now_add=True)
    date_last_updated = models.DateTimeField('Data last updated', auto_now=True)


class CodeBaseModel(BaseModel):
    code = models.CharField(max_length=50, unique=True, editable=False)

    code_prefix = ""  # Override in child classes, e.g., "LIC"
    counter_code = "" # Override in child classes, e.g., "LICENSE"

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        # Auto-generate code if not provided
        if not self.code:
            next_number = Counter.next(self.counter_code or self.code_prefix)
            self.code = f"{self.code_prefix}-{next_number:05d}"
        super().save(*args, **kwargs)


class Counter(models.Model):
    class Meta:
        verbose_name = 'Counter'
        verbose_name_plural = 'Counters'
        db_table = 'counter'

    code = models.CharField('Naming', max_length=20, primary_key=True)
    counter = models.IntegerField('Value', default=1)

    @classmethod
    def next(cls, code):
        try:
            cls.objects.filter(pk=code).update(counter=F('counter') + 1)
            logger.info(cls.objects.get(pk=code))
            return cls.objects.get(pk=code).counter
        except cls.DoesNotExist:
            return cls.objects.create(code=code, counter=1).counter

    def __str__(self):
        return '{}: {}'.format(self.code, self.counter)
