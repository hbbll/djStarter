from parler.models import TranslatableModel, TranslatedFields
from django.db import models


class Role(TranslatableModel):
    role = models.CharField(max_length=50, primary_key=True)
    priority = models.IntegerField(default=0)
    translations = TranslatedFields(name=models.CharField(max_length=50))

    def __str__(self):
        return self.safe_translation_getter("name", any_language=True)
