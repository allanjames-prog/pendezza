from django.urls import path

from userauthentication import views

app_name = "userauthentication"

urlpatterns = [
  path("sign_up/", views.RegisterView, name="sign_up"),
  path('logout/', views.logout_view, name="logout"),
  path("sign_in/", views.loginViewTemp, name="sign_in"),
  
  # path('request-reset-email/', RequestPasswordResetEmail.as_view(), name="request-reset-email"),
  # path('reset-password/<uidb64>/<token>/', CompletePasswordReset.as_view(), name="reset-password"),

]





















