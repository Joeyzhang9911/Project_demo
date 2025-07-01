from django.urls import path
from .views import (
    SDGActionPlanListView,
    SDGActionPlanCreateView,
    SDGActionPlanRetrieveView,
    SDGActionPlanUpdateView,
    SDGActionPlanDeleteView,
)

urlpatterns = [
    # GET /api/sdg-action-plan/ returns the list of actions plans of teams user is in
    path('', SDGActionPlanListView.as_view(), name='action-plan-list'),
    # POST /api/sdg-action-plan/create/ creates a new action plan for a certain team
    path('create/', SDGActionPlanCreateView.as_view(), name='action-plan-create'),
    # GET /api/sdg-action-plan/<int:id>/ retrieves a specific action plan
    path('<int:id>/', SDGActionPlanRetrieveView.as_view(),
         name='action-plan-retrieve'),
    # PUT/PATCH /api/sdg-action-plan/<int:id>/update/ updates a specific action plan
    # anyone can update the plan on the team
    path('<int:id>/update/', SDGActionPlanUpdateView.as_view(),
         name='action-plan-update'),
    # DELETE /api/sdg-action-plan/<int:id>/delete/ deletes a specific action plan
    # anyone can delete the plan on the team
    path('<int:id>/delete/', SDGActionPlanDeleteView.as_view(),
         name='action-plan-delete'),
]
