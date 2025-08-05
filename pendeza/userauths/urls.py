from django.urls import path

from userauths import views

app_name = "userauths"

urlpatterns = [
  path("sign_up/", views.RegisterView, name="sign_up"),
  path('logout/', views.logout_view, name="logout"),
  path("sign_in/", views.loginViewTemp, name="sign_in"),
  path("complete-profile/", views.complete_profile, name="complete_profile"),
  
]



