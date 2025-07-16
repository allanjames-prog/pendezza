from django.urls import path
from .views import (
    SalonGalleryUploadView, SalonDetailView,
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

]