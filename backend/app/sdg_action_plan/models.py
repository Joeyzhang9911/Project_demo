from django.db import models
from django.contrib.auth.models import User
from teams.models import Team


class SDGActionPlan(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('final', 'Final'),
    ]

    # make sure to use empty string for blank fields in the database
    # only things that need to be filled out on creation is impact_project_name and team
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='action_plans')
    name_of_designers = models.TextField(blank=True)
    impact_project_name = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    plan_content = models.JSONField()
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='draft')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # store the path or url of the generated pdf
    pdf_file_path = models.CharField(max_length=255, blank=True, null=True)

    # each action plan only belongs to one team
    team = models.ForeignKey(
        Team, on_delete=models.CASCADE, related_name='action_plans')

    def __str__(self):
        return f"Action Plan: {self.impact_project_name} by {self.user.username}"
