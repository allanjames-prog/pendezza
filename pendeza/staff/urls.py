from django.urls import path
from .views import (
     TeamListView, TeamDetailView,
    TeamMemberUpdateView, TeamMemberDeleteView, salon_detail
)

app_name = "salon"

urlpatterns = [
    # Team Management
    path('<slug:slug>/team/', TeamListView.as_view(), name='team_list'),
    path('<slug:slug>/team/<uuid:staff_id>/', TeamDetailView.as_view(), name='team_detail'),
    path('<slug:slug>/team/<uuid:staff_id>/update/', TeamMemberUpdateView.as_view(), name='team_member_update'),
    path('<slug:slug>/team/<uuid:staff_id>/delete/', TeamMemberDeleteView.as_view(), name='team_member_delete'),
]