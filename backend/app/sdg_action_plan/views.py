from rest_framework import generics, permissions
from .models import SDGActionPlan
from .serializers import SDGActionPlanSerializer
from django.db.models import Q

# helper mixin to get the action plans of the user and their teams


class UserActionPlanQuerysetMixin:
    def get_user_action_plans(self):
        """
        Returns a queryset of SDGActionPlan objects that the current user can access
        """
        user = self.request.user
        team_ids = user.team_memberships.values_list('team__id', flat=True)
        qs = SDGActionPlan.objects.filter(
            Q(user=user) | Q(team__id__in=team_ids)).distinct()
        return qs


class SDGActionPlanListView(UserActionPlanQuerysetMixin, generics.ListAPIView):
    serializer_class = SDGActionPlanSerializer
    permission_classes = [permissions.IsAuthenticated]

    # returns all plans of teams user is in
    def get_queryset(self):
        return self.get_user_action_plans()


class SDGActionPlanCreateView(generics.CreateAPIView):
    serializer_class = SDGActionPlanSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class SDGActionPlanRetrieveView(UserActionPlanQuerysetMixin, generics.RetrieveAPIView):
    serializer_class = SDGActionPlanSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'id'

    def get_queryset(self):
        return self.get_user_action_plans()

# anyone can update the plan on the team


class SDGActionPlanUpdateView(UserActionPlanQuerysetMixin, generics.UpdateAPIView):
    serializer_class = SDGActionPlanSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'id'

    def get_queryset(self):
        return self.get_user_action_plans()


class SDGActionPlanDeleteView(UserActionPlanQuerysetMixin, generics.DestroyAPIView):
    serializer_class = SDGActionPlanSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'id'

    def get_queryset(self):
        return self.get_user_action_plans()
