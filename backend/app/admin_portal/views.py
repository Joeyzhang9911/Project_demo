from rest_framework import status, generics, permissions
from rest_framework.response import Response
from django.contrib.auth.models import User
from teams.models import Team, TeamMember
from teams.serializers import TeamMemberSerializer
from rest_framework.permissions import BasePermission, IsAuthenticated
from .models import EducationInteraction, ActionInteraction
from .serializers import EducationInteractionSerializer, ActionInteractionSerializer
from sdg_education.models import EducationDb
from sdg_actions.models import ActionDb
from sdg_action_plan.models import SDGActionPlan
from django.utils.timezone import now
from django.db.models import Sum, Max, F, Count
from django.db import models
from .utils import time_range_filter
from collections import Counter
from .utils import get_sdg_name
from rest_framework.views import APIView
from users.models import UserActivity

# Helper permission class to check is_staff or is_superuser
class IsSiteAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user and (request.user.is_staff or request.user.is_superuser)

### Function to show all users in the database (only admins can use)
class AdminUserListView(generics.GenericAPIView):
    permission_classes = [IsSiteAdmin]

    def get(self, request, *args, **kwargs):
        users = User.objects.values("id", "username", "email")
        return Response(list(users))

### Function to show all teams in the database (only admins can use)
class AdminTeamListView(generics.GenericAPIView):
    permission_classes = [IsSiteAdmin]

    def get(self, request, *args, **kwargs):
        teams = Team.objects.values("id", "name", "description", "created_at")
        return Response(list(teams))

### Function to show all members of any team in database (admin only)
class AdminTeamMembersView(generics.GenericAPIView):
    permission_classes = [IsSiteAdmin]
    serializer_class = TeamMemberSerializer

    def get(self, request, *args, **kwargs):
        team_id = kwargs.get("team_id")
        if not Team.objects.filter(id=team_id).exists():
            return Response({"message": "Team not found."}, status=status.HTTP_404_NOT_FOUND)

        #Gets all team member objects from a team id
        team = Team.objects.get(id=team_id)
        members = TeamMember.objects.filter(team=team)
        serializer = self.get_serializer(members, many=True)
        return Response({"members": serializer.data})

### Function to let admin kick members of a team 
class AdminKickMemberView(generics.GenericAPIView):
    permission_classes = [IsSiteAdmin]

    def post(self, request, *args, **kwargs):
        team_id = kwargs.get("team_id")
        username = request.data.get("username")

        if not Team.objects.filter(id=team_id).exists():
            return Response({"message": "Team not found."}, status=status.HTTP_404_NOT_FOUND)

        if not User.objects.filter(username=username).exists():
            return Response({"message": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        #Gets team and user from request body
        team = Team.objects.get(id=team_id)
        user = User.objects.get(username=username)

        if not TeamMember.objects.filter(team=team, user=user).exists():
            return Response({"message": "User is not a member of this team."}, status=status.HTTP_404_NOT_FOUND)

        membership = TeamMember.objects.get(team=team, user=user)

        #Can't kick team owner
        if membership.role == 'owner':
            return Response({"message": "Cannot remove the team owner."}, status=status.HTTP_403_FORBIDDEN)

        membership.delete()
        return Response({"message": f"{username} was removed from the team."}, status=status.HTTP_200_OK)

#Function to let admin update roles in a team
class AdminUpdateRoleView(generics.GenericAPIView):
    permission_classes = [IsSiteAdmin]

    def post(self, request, *args, **kwargs):
        team_id = kwargs.get("team_id")
        username = request.data.get("username")
        new_role = request.data.get("new_role")

        #Error checks
        if new_role not in ['admin', 'member']:
            return Response({"message": "Only 'admin' or 'member' roles can be assigned."}, status=status.HTTP_400_BAD_REQUEST)

        if not Team.objects.filter(id=team_id).exists():
            return Response({"message": "Team not found."}, status=status.HTTP_404_NOT_FOUND)

        if not User.objects.filter(username=username).exists():
            return Response({"message": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        team = Team.objects.get(id=team_id)
        user = User.objects.get(username=username)

        if not TeamMember.objects.filter(team=team, user=user).exists():
            return Response({"message": "User is not a member of this team."}, status=status.HTTP_404_NOT_FOUND)

        membership = TeamMember.objects.get(team=team, user=user)

        if membership.role == 'owner':
            return Response({"message": "Cannot change role of team owner."}, status=status.HTTP_403_FORBIDDEN)

        membership.role = new_role
        membership.save()

        return Response({"message": f"{username} changed to {new_role}."}, status=status.HTTP_200_OK)

###Function to log an education interaction
class LogEducationInteractionView(generics.CreateAPIView):
    serializer_class = EducationInteractionSerializer
    permission_classes = []

    def post(self, request, *args, **kwargs):
        education_id = request.data.get('educationId')
        education = EducationDb.objects.get(id=education_id)
        user = request.user if request.user.is_authenticated else None

        #Create education interaction object
        interaction = EducationInteraction.objects.create(
            userId=user,
            educationId=education,
            educationName=education.title,
            related_sdgs=education.sdgs_related,
            related_disciplines=education.related_to_which_discipline,
            related_industries=education.useful_for_which_industries
        )

        serializer = self.get_serializer(interaction)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

###Function to log an action interaction
class LogActionInteractionView(generics.CreateAPIView):
    serializer_class = ActionInteractionSerializer
    permission_classes = []

    def post(self, request, *args, **kwargs):
        action_id = request.data.get('actionId')
        action = ActionDb.objects.get(id=action_id)
        user = request.user if request.user.is_authenticated else None

        #Create an action interaction object
        interaction = ActionInteraction.objects.create(
            userId=user,
            actionId=action,
            actionName=action.actions,
            related_sdgs=action.sdgs,
            related_industries=action.related_industry
        )

        serializer = self.get_serializer(interaction)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

# Function to show how many times an education page has been viewed
class EducationViewCountView(generics.GenericAPIView):
    permission_classes = [IsSiteAdmin]

    def get(self, request, *args, **kwargs):
        education_id = kwargs.get('education_id')
        total_views = EducationInteraction.objects.filter(
            educationId=education_id).aggregate(total=Count('id'))['total'] or 0
        return Response({"education_id": education_id, "total_views": total_views}, status=status.HTTP_200_OK)

### Function to show how many times an action page has been viewed
class ActionViewCountView(generics.GenericAPIView):
    permission_classes = [IsSiteAdmin]

    def get(self, request, *args, **kwargs):
        action_id = kwargs.get('action_id')
        total_views = ActionInteraction.objects.filter(
            actionId=action_id).aggregate(total=Count('id'))['total'] or 0
        return Response({"action_id": action_id, "total_views": total_views}, status=status.HTTP_200_OK)

### Function to show the education/action pages a user has viewed, sorted by their most recently viewed
class UserInteractionsView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user_id = kwargs.get("user_id")

        educations = (
            EducationInteraction.objects.filter(userId=user_id)
            .values("educationId", "educationName")
            .annotate(count=models.Count("id"), last_accessed=Max("timestamp"))
            .order_by("-last_accessed")
        )

        actions = (
            ActionInteraction.objects.filter(userId=user_id)
            .values("actionId", "actionName")
            .annotate(count=models.Count("id"), last_accessed=Max("timestamp"))
            .order_by("-last_accessed")
        )

        # Formats date-time into human readable string
        for item in educations:
            item["last_accessed"] = item["last_accessed"].strftime(
                '%d %b %Y, %I:%M:%S %p')
        for item in actions:
            item["last_accessed"] = item["last_accessed"].strftime(
                '%d %b %Y, %I:%M:%S %p')

        return Response({
            "education_pages_viewed": list(educations),
            "action_plans_viewed": list(actions)
        }, status=status.HTTP_200_OK)

### Function to return the top education pages based on view count
class TopEducationsView(generics.GenericAPIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        time_range = request.data.get("time_range", "all time")
        time_filter = time_range_filter(time_range)

        # Filter based on time
        queryset = EducationInteraction.objects.all()
        if time_filter:
            queryset = queryset.filter(timestamp__gte=time_filter)

        #Sort by total views, then most recently accessed to break ties
        top_educations = (
            queryset
            .values("educationId", "educationName")
            .annotate(total_views=Count("id"), last_accessed=Max("timestamp"))
            .order_by("-total_views", "-last_accessed")[:20]
        )

        #Convert to human readable string
        for item in top_educations:
            item["last_accessed"] = item["last_accessed"].strftime(
                '%d %b %Y, %I:%M:%S %p')

        return Response(list(top_educations), status=status.HTTP_200_OK)

### Function to return the top action pages based on view count
class TopActionsView(generics.GenericAPIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        time_range = request.data.get("time_range", "all time")
        time_filter = time_range_filter(time_range)

        #Filter based on time
        queryset = ActionInteraction.objects.all()
        if time_filter:
            queryset = queryset.filter(timestamp__gte=time_filter)

        #Sort by total views, then most recently accessed to break ties
        top_actions = (
            queryset
            .values("actionId", "actionName")
            .annotate(total_views=Count("id"), last_accessed=Max("timestamp"))
            .order_by("-total_views", "-last_accessed")[:20]
        )

        #Convert to human readable string
        for item in top_actions:
            item["last_accessed"] = item["last_accessed"].strftime(
                '%d %b %Y, %I:%M:%S %p')

        return Response(list(top_actions), status=status.HTTP_200_OK)

### Function to return the top sdgs related to education pages based on view count
class TopEducationSDGsView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        time_range = request.data.get("time_range", "all time")
        time_filter = time_range_filter(time_range)

        #Filter based on time
        queryset = EducationInteraction.objects.all()
        if time_filter:
            queryset = queryset.filter(timestamp__gte=time_filter)

        # Extracts and counts all SDG appearances from the queryset
        all_sdgs = []
        for entry in queryset:
            if entry.related_sdgs:
                all_sdgs.extend([sdg.strip()
                                for sdg in entry.related_sdgs.split(',')])

        counter = Counter(all_sdgs)
        top_sdgs = counter.most_common(5)
        return Response([{"sdg": sdg, "sdg_name": get_sdg_name(sdg), "total_views": count} for sdg, count in top_sdgs], status=status.HTTP_200_OK)


### Function to return the top sdgs related to action pages based on view count
class TopActionSDGsView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        time_range = request.data.get("time_range", "all time")
        time_filter = time_range_filter(time_range)

        #Filter based on time
        queryset = ActionInteraction.objects.all()
        if time_filter:
            queryset = queryset.filter(timestamp__gte=time_filter)

        # Extracts and counts all SDG appearances from the queryset
        all_sdgs = []
        for entry in queryset:
            if entry.related_sdgs:
                all_sdgs.extend([sdg.strip()
                                for sdg in entry.related_sdgs.split(',')])

        counter = Counter(all_sdgs)
        top_sdgs = counter.most_common(5)
        return Response([{"sdg": sdg, "sdg_name": get_sdg_name(sdg), "total_views": count} for sdg, count in top_sdgs], status=status.HTTP_200_OK)


### Function to get all sdg plans as an admin
class AdminGetSDGPlansView(generics.GenericAPIView):
    permission_classes = [IsSiteAdmin]

    def get(self, request, *args, **kwargs):
        plans_qs = SDGActionPlan.objects.all().values()
        plans_list = list(plans_qs)
        return Response(plans_list)


class AdminGetSDGPlansCountView(generics.GenericAPIView):
    """
    GET /admin/sdg-plans/count/

    Returns:
      - all SDGActionPlan records (as list of dicts) and count of plans created since the given time range
    """
    permission_classes = [permissions.AllowAny]

    def get(self, request, *args, **kwargs):
        time_range = request.data.get("time_range")
        cutoff = time_range_filter(time_range)

        qs = SDGActionPlan.objects.all()

        if cutoff is not None:
            recent_qs = qs.filter(created_at__gte=cutoff)
            recent_count = recent_qs.count()
        else:
            recent_count = qs.count()

        plans_list = list(qs.values())

        return Response({
            "time_range": time_range or "all time",
            "recent_count": recent_count,
            "total_count": qs.count(),
            "plans": plans_list,
        })

class UserActivityAnalyticsView(APIView):
    """
    GET /api/admin/analytics/user-activity/?time_range=all|week|month

    返回当前用户的活动分析数据
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        time_range = request.GET.get("time_range", "all")
        user = request.user

        # 时间过滤
        from django.utils import timezone
        from datetime import timedelta

        qs = UserActivity.objects.filter(user=user)
        now_time = timezone.now()
        if time_range == "week":
            qs = qs.filter(timestamp__gte=now_time - timedelta(days=7))
        elif time_range == "month":
            qs = qs.filter(timestamp__gte=now_time - timedelta(days=30))

        # 页面活跃统计
        page_activities = {
            "total_visits": qs.filter(activity_type="page_view").count(),
            "total_active_time": int(qs.filter(activity_type="page_leave").aggregate(
                total=Sum("duration"))["total"] or 0),
            "most_visited_pages": list(
                qs.filter(activity_type="page_view")
                .values("page")
                .annotate(visit_count=Count("id"))
                .order_by("-visit_count")[:5]
            ),
            "average_session_time": float(
                (qs.filter(activity_type="page_leave").aggregate(
                    avg=Sum("duration"))["avg"] or 0) /
                max(qs.filter(activity_type="page_leave").count(), 1)
            ),
        }

        # 搜索行为统计
        search_qs = qs.filter(activity_type="search")
        search_activities = {
            "total_searches": search_qs.count(),
            "search_types": [],  # 可扩展
            "most_searched_terms": list(
                search_qs.values("search_query")
                .annotate(search_count=Count("id"))
                .order_by("-search_count")[:5]
            ),
        }

        # 表单行为统计
        form_edit_qs = qs.filter(activity_type="form_edit")
        form_activities = {
            "total_form_activities": form_edit_qs.count(),
            "form_edit_time": int(form_edit_qs.aggregate(
                total=Sum("duration"))["total"] or 0),
            "total_words_written": int(form_edit_qs.aggregate(
                total=Sum("form_word_count"))["total"] or 0),
            "most_active_forms": list(
                form_edit_qs.values("form_id")
                .annotate(activity_count=Count("id"))
                .order_by("-activity_count")[:5]
            ),
        }

        return Response({
            "page_activities": page_activities,
            "search_activities": search_activities,
            "form_activities": form_activities,
        })
