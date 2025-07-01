from django.db import models

from django.db import models
from django.contrib.auth.models import User
from sdg_education.models import EducationDb
from sdg_actions.models import ActionDb

#Model for interactions between users and education pages
class EducationInteraction(models.Model):
    userId = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    educationId = models.ForeignKey(EducationDb, on_delete=models.CASCADE)
    educationName = models.TextField()

    related_sdgs = models.TextField(null=True, blank=True)
    related_disciplines = models.TextField(null=True, blank=True)
    related_industries = models.TextField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["educationId", "userId"]),
            models.Index(fields=["timestamp"]),
        ]

    def __str__(self):
        return f"{self.userId or 'Anonymous'} viewed Education {self.educationId.id}"

#Model for interactions between users and action pages
class ActionInteraction(models.Model):
    userId = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    actionId = models.ForeignKey(ActionDb, on_delete=models.CASCADE)
    actionName = models.TextField()

    related_sdgs = models.TextField(null=True, blank=True)
    related_industries = models.TextField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["actionId", "userId"]),
            models.Index(fields=["timestamp"]),
        ]

    def __str__(self):
        return f"{self.userId or 'Anonymous'} viewed Action {self.actionId.id}"

