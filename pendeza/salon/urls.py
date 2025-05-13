from django.urls import path
from .views import index, salon_detail
from salon import views
from salon.views import SalonGalleryUploadView

app_name = "salon"

urlpatterns = [
  path("", views.index, name="index"),
  path('<slug:slug>/', salon_detail, name='detail'),
  path('<slug:slug>/upload-gallery/', SalonGalleryUploadView.as_view(), name='upload_gallery'),
  path('<slug:slug>/upload-gallery/<int:pk>/', SalonGalleryUploadView.as_view(), name='update_gallery'),
  path('<slug:slug>/upload-gallery/<int:pk>/delete/', SalonGalleryUploadView.as_view(), name='delete_gallery'),

]








































