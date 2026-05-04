from parler.models import TranslatableModel, TranslatedFields
from django.db import models


class PermissionGroup(TranslatableModel):
    code = models.CharField(max_length=50, unique=True)
    translations = TranslatedFields(name=models.CharField(max_length=50))

    def __str__(self):
        return self.safe_translation_getter("name", any_language=True)
