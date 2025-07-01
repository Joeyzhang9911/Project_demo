from django.db import models
from django.contrib.auth.models import User

#Model for teams
class Team(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

#Model for members of a team
class TeamMember(models.Model):
    ROLE_CHOICES = [
        ('owner', 'Owner'),
        ('admin', 'Admin'),
        ('member', 'Member'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='team_memberships')
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='members')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='member')
    is_pending = models.BooleanField(default=True)
    invited_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name='team_inviter')
    joined_on = models.DateTimeField(auto_now_add=True)
    can_invite = models.BooleanField(default=False) 

    class Meta:
        unique_together = ('user', 'team')

    def __str__(self):
        return f"{self.user.username} in {self.team.name} as {self.role}"