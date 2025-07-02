from rest_framework import generics, permissions, status
from rest_framework.response import Response
from django.contrib.auth.models import User
from teams.models import TeamMember
from .models import SDGActionPlan
from .serializers import SDGActionPlanSerializer
from django.db.models import Q
from rest_framework.permissions import BasePermission

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


# 权限类定义
class IsTeamOwnerOrAdmin(BasePermission):
    """检查用户是否是团队所有者或管理员"""
    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False
        
        # 表单创建者总是可以管理权限
        if obj.user == request.user:
            return True
        
        team_member = TeamMember.objects.filter(
            team=obj.team, 
            user=request.user, 
            is_pending=False
        ).first()
        
        return team_member and team_member.role in ['owner', 'admin']


class CanEditActionPlan(BasePermission):
    """Check if user can edit action plan"""
    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False
        
        user = request.user
        
        # Creator always has edit permission
        if obj.user == user:
            return True
            
        # Check if user is explicitly specified as editor (highest priority)
        if obj.editors.filter(id=user.id).exists():
            return True
            
        # Check team permissions
        team_member = TeamMember.objects.filter(
            team=obj.team, 
            user=user, 
            is_pending=False
        ).first()
        
        if team_member:
            # Team owner always has edit permission
            if team_member.role == 'owner':
                return True
                
            # If team edit is allowed
            if obj.allow_team_edit:
                # Team admins can edit
                if team_member.role == 'admin':
                    return True
                # If explicit permissions not required, regular members can edit
                elif not obj.require_explicit_permissions:
                    return True
        
        return False


class CanViewActionPlan(BasePermission):
    """Check if user can view action plan"""
    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False
        
        user = request.user
        
        # Creator always has view permission
        if obj.user == user:
            return True
            
        # Check if user is explicitly specified as viewer (highest priority)
        if obj.viewers.filter(id=user.id).exists():
            return True
            
        # Check team permissions
        team_member = TeamMember.objects.filter(
            team=obj.team, 
            user=user, 
            is_pending=False
        ).first()
        
        if team_member:
            # Team owner always has view permission
            if team_member.role == 'owner':
                return True
                
            # If team view is allowed
            if obj.allow_team_view:
                # Team members can view
                return True
        
        return False


# 视图类定义
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
    permission_classes = [CanEditActionPlan]
    lookup_field = 'id'

    def get_queryset(self):
        return self.get_user_action_plans()


class SDGActionPlanDeleteView(UserActionPlanQuerysetMixin, generics.DestroyAPIView):
    serializer_class = SDGActionPlanSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'id'

    def get_queryset(self):
        return self.get_user_action_plans()


# 新增权限管理视图
class ActionPlanPermissionsView(generics.GenericAPIView):
    """管理行动计划权限的视图"""
    permission_classes = [IsTeamOwnerOrAdmin]
    
    def post(self, request, *args, **kwargs):
        """更新表单权限设置"""
        action_plan_id = kwargs.get('id')
        
        try:
            action_plan = SDGActionPlan.objects.get(id=action_plan_id)
        except SDGActionPlan.DoesNotExist:
            return Response(
                {"message": "Action plan not found."}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # 检查权限
        self.check_object_permissions(request, action_plan)
        
        # 获取请求数据
        allow_team_edit = request.data.get('allow_team_edit')
        allow_team_view = request.data.get('allow_team_view')
        require_explicit_permissions = request.data.get('require_explicit_permissions')
        
        # 更新权限设置
        if allow_team_edit is not None:
            action_plan.allow_team_edit = allow_team_edit
        if allow_team_view is not None:
            action_plan.allow_team_view = allow_team_view
        if require_explicit_permissions is not None:
            action_plan.require_explicit_permissions = require_explicit_permissions
        
        action_plan.save()
        
        return Response({
            "message": "Permissions updated successfully.",
            "allow_team_edit": action_plan.allow_team_edit,
            "allow_team_view": action_plan.allow_team_view,
            "require_explicit_permissions": action_plan.require_explicit_permissions
        }, status=status.HTTP_200_OK)


class ActionPlanEditorsView(generics.GenericAPIView):
    """管理表单编辑者列表的视图"""
    permission_classes = [IsTeamOwnerOrAdmin]
    
    def post(self, request, *args, **kwargs):
        """添加或移除编辑者"""
        action_plan_id = kwargs.get('id')
        action = request.data.get('action')  # 'add' 或 'remove'
        user_ids = request.data.get('user_ids', [])
        
        try:
            action_plan = SDGActionPlan.objects.get(id=action_plan_id)
        except SDGActionPlan.DoesNotExist:
            return Response(
                {"message": "Action plan not found."}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # 检查权限
        self.check_object_permissions(request, action_plan)
        
        if action == 'add':
            users = User.objects.filter(id__in=user_ids)
            action_plan.editors.add(*users)
            message = f"Added {len(users)} users as editors."
        elif action == 'remove':
            users = User.objects.filter(id__in=user_ids)
            action_plan.editors.remove(*users)
            message = f"Removed {len(users)} users from editors."
        else:
            return Response(
                {"message": "Invalid action. Use 'add' or 'remove'."}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        return Response({
            "message": message,
            "editors": list(action_plan.editors.values_list('username', flat=True))
        }, status=status.HTTP_200_OK)
    
    def get(self, request, *args, **kwargs):
        """获取编辑者列表"""
        action_plan_id = kwargs.get('id')
        
        try:
            action_plan = SDGActionPlan.objects.get(id=action_plan_id)
        except SDGActionPlan.DoesNotExist:
            return Response(
                {"message": "Action plan not found."}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # 检查权限
        self.check_object_permissions(request, action_plan)
        
        editors = action_plan.editors.all()
        editor_data = [{
            'id': editor.id,
            'username': editor.username,
            'email': editor.email
        } for editor in editors]
        
        return Response({
            "editors": editor_data
        }, status=status.HTTP_200_OK)


class ActionPlanViewersView(generics.GenericAPIView):
    """管理表单查看者列表的视图"""
    permission_classes = [IsTeamOwnerOrAdmin]
    
    def post(self, request, *args, **kwargs):
        """添加或移除查看者"""
        action_plan_id = kwargs.get('id')
        action = request.data.get('action')  # 'add' 或 'remove'
        user_ids = request.data.get('user_ids', [])
        
        try:
            action_plan = SDGActionPlan.objects.get(id=action_plan_id)
        except SDGActionPlan.DoesNotExist:
            return Response(
                {"message": "Action plan not found."}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # 检查权限
        self.check_object_permissions(request, action_plan)
        
        if action == 'add':
            users = User.objects.filter(id__in=user_ids)
            action_plan.viewers.add(*users)
            message = f"Added {len(users)} users as viewers."
        elif action == 'remove':
            users = User.objects.filter(id__in=user_ids)
            action_plan.viewers.remove(*users)
            message = f"Removed {len(users)} users from viewers."
        else:
            return Response(
                {"message": "Invalid action. Use 'add' or 'remove'."}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        return Response({
            "message": message,
            "viewers": list(action_plan.viewers.values_list('username', flat=True))
        }, status=status.HTTP_200_OK)
    
    def get(self, request, *args, **kwargs):
        """获取查看者列表"""
        action_plan_id = kwargs.get('id')
        
        try:
            action_plan = SDGActionPlan.objects.get(id=action_plan_id)
        except SDGActionPlan.DoesNotExist:
            return Response(
                {"message": "Action plan not found."}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # 检查权限
        self.check_object_permissions(request, action_plan)
        
        viewers = action_plan.viewers.all()
        viewer_data = [{
            'id': viewer.id,
            'username': viewer.username,
            'email': viewer.email
        } for viewer in viewers]
        
        return Response({
            "viewers": viewer_data
        }, status=status.HTTP_200_OK)