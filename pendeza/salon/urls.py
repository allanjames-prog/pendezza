from django.urls import path
from .views import (
    SalonGalleryUploadView, TeamListView, TeamDetailView,
    TeamMemberUpdateView, TeamMemberDeleteView, SalonDetailView,
    SalonCreateView, SalonUpdateView, SalonDeleteView,
    index, salon_detail, add_review, SalonReviewsView
)

app_name = "salon"

urlpatterns = [
    # General Salon URLs
    path("", index, name="index"),
    path('create/', SalonCreateView.as_view(), name='salon_create'),
    path('<slug:slug>/', SalonDetailView.as_view(), name='salon_detail'),
    path('<slug:slug>/detail/', salon_detail, name='detail'),
    path('<int:pk>/update/', SalonUpdateView.as_view(), name='salon_update'),
    path('<int:pk>/delete/', SalonDeleteView.as_view(), name='salon_delete'),

    # Gallery
    path('<slug:slug>/upload-gallery/', SalonGalleryUploadView.as_view(), name='upload_gallery'),

    # Reviews
    path('<slug:slug>/add-review/', add_review, name='salon_review_create'),
    path('<slug:slug>/reviews/', SalonReviewsView.as_view(), name='all_reviews'),

    # Team Management
    path('<slug:slug>/team/', TeamListView.as_view(), name='team_list'),
    path('<slug:slug>/team/<uuid:staff_id>/', TeamDetailView.as_view(), name='team_detail'),
    path('<slug:slug>/team/<uuid:staff_id>/update/', TeamMemberUpdateView.as_view(), name='team_member_update'),
    path('<slug:slug>/team/<uuid:staff_id>/delete/', TeamMemberDeleteView.as_view(), name='team_member_delete'),
]