from rest_framework import generics, permissions, status
from rest_framework.response import Response
from .models import SDGActionPlan
from .serializers import SDGActionPlanSerializer
from .google_docs_service import GoogleDocsService, OAuthRequired
from django.db.models import Q
from django.utils import timezone
from django.db import transaction
from rest_framework.views import APIView
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import json
import pickle
from google_auth_oauthlib.flow import Flow
import os

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
        action_plan = serializer.save(user=self.request.user)
        
        # Create Google Docs document if project name is provided
        if action_plan.impact_project_name:
            try:
                google_docs_service = GoogleDocsService()
                content = {
                    'impact_project_name': action_plan.impact_project_name,
                    'name_of_designers': action_plan.name_of_designers,
                    'description': action_plan.description,
                    'plan_content': action_plan.plan_content
                }
                
                document_id = google_docs_service.create_document(
                    action_plan.impact_project_name, content)
                
                if document_id:
                    action_plan.google_doc_id = document_id
                    action_plan.google_doc_url = google_docs_service.get_document_url(document_id)
                    action_plan.google_doc_created = True
                    action_plan.last_sync_time = timezone.now()
                    action_plan.save()
                    
                    # Share document with team members
                    self._share_document_with_team(action_plan, google_docs_service)
                    
            except Exception as e:
                print(f"Error creating Google Docs document: {e}")


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

    def update(self, request, *args, **kwargs):
        with transaction.atomic():
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            updated_instance = serializer.save()
            
            # Sync with Google Docs if document exists
            if updated_instance.google_doc_id and updated_instance.google_doc_created:
                try:
                    google_docs_service = GoogleDocsService()
                    content = {
                        'impact_project_name': updated_instance.impact_project_name,
                        'name_of_designers': updated_instance.name_of_designers,
                        'description': updated_instance.description,
                        'plan_content': updated_instance.plan_content
                    }
                    
                    success = google_docs_service.update_document(
                        updated_instance.google_doc_id, content)
                    
                    if success:
                        updated_instance.last_sync_time = timezone.now()
                        updated_instance.save()
                        
                except Exception as e:
                    print(f"Error updating Google Docs document: {e}")
            
            return Response(serializer.data)
        
class SDGActionPlanDeleteView(UserActionPlanQuerysetMixin, generics.DestroyAPIView):
    serializer_class = SDGActionPlanSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'id'

    def get_queryset(self):
        return self.get_user_action_plans()

class SDGActionPlanGoogleDocsView(APIView):
    """View for Google Docs integration"""
    def get_queryset(self):
        return SDGActionPlan.objects.all()
    
    def post(self, request, id):
        """Sync action plan to Google Docs"""
        try:
            action_plan = self.get_queryset().get(id=id)
            try:
                docs_service = GoogleDocsService()
            except OAuthRequired as e:
                return Response({
                    'auth_required': True,
                    'auth_url': e.auth_url,
                    'message': 'Google Docs authorization required. Please authorize the application.'
                }, status=401)
            
            # Create Google Doc
            try:
                doc_id = docs_service.create_document_from_action_plan(action_plan)
                
                # Update the action plan with Google Doc ID
                action_plan.google_doc_id = doc_id
                action_plan.save()
                
                return Response({
                    'success': True,
                    'message': 'Action plan synced to Google Docs successfully',
                    'google_doc_id': doc_id,
                    'google_doc_url': f'https://docs.google.com/document/d/{doc_id}/edit'
                })
                
            except Exception as e:
                return Response({
                    'error': 'Failed to create Google Doc',
                    'message': str(e)
                }, status=500)
                    
        except SDGActionPlan.DoesNotExist:
            return Response({
                'error': 'Action plan not found'
            }, status=404)
        except Exception as e:
            return Response({
                'error': 'Unexpected error',
                'message': str(e)
            }, status=500)
    
    def _share_document_with_team(self, action_plan, google_docs_service):
        """Share Google Docs document with team members"""
        try:
            team_members = action_plan.team.members.all()
            for member in team_members:
                if member.email:
                    google_docs_service.share_document(
                        action_plan.google_doc_id, 
                        member.email, 
                        'writer'
                    )
        except Exception as e:
            print(f"Error sharing document with team: {e}")


@method_decorator(csrf_exempt, name='dispatch')
class GoogleOAuthCallbackView(APIView):
    """Handle Google OAuth callback"""
    
    def get(self, request):
        """Handle OAuth callback with authorization code"""
        try:
            # Get authorization code from query parameters
            code = request.GET.get('code')
            if not code:
                return HttpResponse(
                    """
                    <html>
                    <head><title>Authorization Failed</title></head>
                    <body>
                        <h2>Authorization Failed</h2>
                        <p>Authorization code not found. Please try again.</p>
                        <script>window.close();</script>
                    </body>
                    </html>
                    """, 
                    status=400
                )
            
            # Check if credentials file exists
            if not os.path.exists('credentials.json'):
                return HttpResponse(
                    """
                    <html>
                    <head><title>Configuration Error</title></head>
                    <body>
                        <h2>Configuration Error</h2>
                        <p>Google API credentials not configured. Please contact administrator.</p>
                        <script>window.close();</script>
                    </body>
                    </html>
                    """, 
                    status=500
                )
            
            # Load client configuration
            with open('credentials.json', 'r') as f:
                client_config = json.load(f)
            
            # Create flow
            flow = Flow.from_client_config(
                client_config,
                scopes=['https://www.googleapis.com/auth/documents', 'https://www.googleapis.com/auth/drive'],
                redirect_uri='http://localhost:8000/api/sdg-action-plan/auth/google/callback/'
            )
            
            # Exchange authorization code for credentials
            flow.fetch_token(code=code)
            credentials = flow.credentials
            
            # Save credentials
            with open('token.pickle', 'wb') as token:
                pickle.dump(credentials, token)
            
            return HttpResponse(
                """
                <html>
                <head><title>Authorization Successful</title></head>
                <body>
                    <h2>Authorization Successful!</h2>
                    <p>You can now close this window and return to the application.</p>
                    <p>The Google Docs integration is now ready to use.</p>
                    <script>
                        setTimeout(function() {
                            window.close();
                        }, 3000);
                    </script>
                </body>
                </html>
                """
            )
            
        except FileNotFoundError:
            return HttpResponse(
                """
                <html>
                <head><title>Configuration Error</title></head>
                <body>
                    <h2>Configuration Error</h2>
                    <p>Google API credentials file not found. Please contact administrator.</p>
                    <script>window.close();</script>
                </body>
                </html>
                """, 
                status=500
            )
        except json.JSONDecodeError:
            return HttpResponse(
                """
                <html>
                <head><title>Configuration Error</title></head>
                <body>
                    <h2>Configuration Error</h2>
                    <p>Invalid credentials file format. Please contact administrator.</p>
                    <script>window.close();</script>
                </body>
                </html>
                """, 
                status=500
            )
        except Exception as e:
            return HttpResponse(
                f"""
                <html>
                <head><title>Authorization Failed</title></head>
                <body>
                    <h2>Authorization Failed</h2>
                    <p>Error: {str(e)}</p>
                    <p>Please try again or contact administrator.</p>
                    <script>window.close();</script>
                </body>
                </html>
                """, 
                status=500
            )


class GoogleOAuthInitView(APIView):
    """Initialize Google OAuth flow"""
    
    def get(self, request):
        """Get authorization URL"""
        try:
            # Check if credentials file exists
            if not os.path.exists('credentials.json'):
                return Response({
                    'error': 'Google API credentials not configured',
                    'message': 'Please configure Google API credentials first',
                    'setup_instructions': [
                        '1. Go to Google Cloud Console',
                        '2. Create OAuth 2.0 credentials',
                        '3. Download the JSON file',
                        '4. Rename it to "credentials.json"',
                        '5. Place it in the backend/app directory'
                    ]
                }, status=400)
            
            # Load client configuration
            with open('credentials.json', 'r') as f:
                client_config = json.load(f)
            
            # Create flow
            flow = Flow.from_client_config(
                client_config,
                scopes=['https://www.googleapis.com/auth/documents', 'https://www.googleapis.com/auth/drive'],
                redirect_uri='http://localhost:8000/api/sdg-action-plan/auth/google/callback/'
            )
            
            # Generate authorization URL
            auth_url, _ = flow.authorization_url(
                access_type='offline',
                include_granted_scopes='true'
            )
            
            return Response({
                'auth_url': auth_url,
                'message': 'Please visit this URL to authorize the application'
            })
            
        except FileNotFoundError:
            return Response({
                'error': 'Google API credentials file not found',
                'message': 'Please configure Google API credentials first'
            }, status=400)
        except json.JSONDecodeError:
            return Response({
                'error': 'Invalid credentials file format',
                'message': 'The credentials file is not valid JSON'
            }, status=400)
        except Exception as e:
            return Response({
                'error': 'Failed to generate authorization URL',
                'message': str(e)
            }, status=500)
