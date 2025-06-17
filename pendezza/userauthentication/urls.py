from django.urls import path

from userauthentication import views

app_name = "userauthentication"

urlpatterns = [
  path("sign_up/", views.RegisterView, name="sign_up"),
  path('logout/', views.logout_view, name="logout"),
  path("sign_in/", views.loginViewTemp, name="sign_in"),
  

]





















