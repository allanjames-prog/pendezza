from django.shortcuts import render, redirect
from userauthentication.models import User, Profile
from userauthentication.forms import UserRegisterForm
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required


def RegisterView(request):
  if request.user.is_authenticated:
    messages.warning(request, f"You are already logged in")
    return redirect("salon:index")
  form = UserRegisterForm(request.POST or None)
  
  if form.is_valid():
    form.save()
    full_name = form.cleaned_data.get("full_name")
    print("full name====", full_name)
    phone = form.cleaned_data.get("phone")
    print("full name====", full_name)
    email = form.cleaned_data.get("email")
    print("full name====", full_name)
    password = form.cleaned_data.get("password1")
    print("full name====", full_name)

    user = authenticate(email=email, password=password)
    login(request, user)

    messages.success(request, f"Dear {full_name}, your account has been created successfully")

    profile = Profile.objects.get(user=request.user)
    profile.full_name = full_name
    profile.phone = phone
    profile.save()

    return redirect("salon:index")
  else:
    form = UserRegisterForm()


  context = {
    "form" : form
  }
  return render(request, "userauthentication/sign_up.html", context)



@login_required
def logout_view(request):
    logout(request)
    messages.success(request, "You have been successfully logged out.")
    return redirect('salon:index')  # Redirect to your homepage after logout 

from django.views.decorators.cache import never_cache

@never_cache
def loginViewTemp(request):
    if request.user.is_authenticated:
        messages.warning(request, "You are already logged in")
        return redirect("salon:index")
    
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        try: 
            user_query = User.objects.get(email=email)
            user_auth = authenticate(request, email=email, password=password)

            if user_auth is not None:  # Changed to check user_auth instead of user_query
                login(request, user_auth)
                messages.success(request, "You are logged in")
                next_url = request.GET.get("next", "salon:index")
                response = redirect(next_url)
                # Prevent caching of the login page
                response['Cache-Control'] = 'no-store, must-revalidate'
                response['Pragma'] = 'no-cache'
                response['Expires'] = '0'
                return response
            else:
                messages.error(request, "Incorrect email or password.")
                return redirect("userauthentication:sign_in")
            
        except User.DoesNotExist:
            messages.error(request, "User does not exist")
            return redirect("userauthentication:sign_in")
    
    # Add cache control headers to the login page response
    response = render(request, "userauthentication/sign_in.html")
    response['Cache-Control'] = 'no-store, must-revalidate'
    response['Pragma'] = 'no-cache'
    response['Expires'] = '0'
    return response
  


# from django.contrib.auth.tokens import PasswordResetTokenGenerator
# from django.utils.encoding import force_str
# from django.utils.http import urlsafe_base64_decode
# from django.contrib.sites.shortcuts import get_current_site
# from django.core.mail import send_mail
# from django.template.loader import render_to_string
# from django.utils.http import urlsafe_base64_encode
# from django.utils.encoding import force_bytes
# from django.views import View
# from django.shortcuts import redirect
# from django.urls import reverse
# from django.contrib import messages

# class RequestPasswordResetEmail(View):
#     def get(self, request):
#         return render(request, 'userauthentication/request-reset-email.html')
    
#     def post(self, request):
#         email = request.POST['email']
        
#         if not User.objects.filter(email=email).exists():
#             messages.warning(request, 'No account with this email exists')
#             return redirect('userauthentication:request-reset-email')
        
#         user = User.objects.get(email=email)
#         uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
#         token = PasswordResetTokenGenerator().make_token(user)
        
#         current_site = get_current_site(request)
#         email_subject = 'Reset your password'
#         email_body = render_to_string('userauthentication/reset-password-email.html', {
#             'user': user,
#             'domain': current_site,
#             'uid': uidb64,
#             'token': token
#         })
        
#         send_mail(
#             email_subject,
#             '',
#             'noreply@pendezasalon.com',
#             [email],
#             html_message=email_body
#         )
        
#         messages.success(request, 'We have sent you an email with instructions to reset your password')
#         return redirect('userauthentication:sign_in')

# class CompletePasswordReset(View):
#     def get(self, request, uidb64, token):
#         try:
#             uid = force_str(urlsafe_base64_decode(uidb64))
#             user = User.objects.get(pk=uid)
            
#             if not PasswordResetTokenGenerator().check_token(user, token):
#                 messages.warning(request, 'Password reset link is invalid, please request a new one')
#                 return redirect('userauthentication:request-reset-email')
            
#             return render(request, 'userauthentication/set-new-password.html', {
#                 'uidb64': uidb64,
#                 'token': token
#             })
            
#         except Exception as e:
#             messages.warning(request, 'Something went wrong')
#             return redirect('userauthentication:request-reset-email')
    
#     def post(self, request, uidb64, token):
#         try:
#             uid = force_str(urlsafe_base64_decode(uidb64))
#             user = User.objects.get(pk=uid)
            
#             password = request.POST['password']
#             password2 = request.POST['password2']
            
#             if password != password2:
#                 messages.warning(request, 'Passwords do not match')
#                 return redirect('userauthentication:request-reset-email')
            
#             user.set_password(password)
#             user.save()
            
#             messages.success(request, 'Password reset successfully, you can now login with your new password')
#             return redirect('userauthentication:sign_in')
            
#         except Exception as e:
#             messages.warning(request, 'Something went wrong')
#             return redirect('userauthentication:request-reset-email')