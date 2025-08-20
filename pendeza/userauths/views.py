from django.shortcuts import render, redirect
from userauths.models import User, Profile
from userauths.forms import UserRegisterForm
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from .forms import ProfileForm


def RegisterView(request):
  if request.user.is_authenticated:
    messages.warning(request, f"You are already logged in")
    return redirect("salon:index")
  form = UserRegisterForm(request.POST or None)
  
  if form.is_valid():
    user = form.save(commit=False)
    user.role = form.cleaned_data.get("role")
    user.save()

    full_name = form.cleaned_data.get("full_name")
    phone = form.cleaned_data.get("phone")
    email = form.cleaned_data.get("email")
    password = form.cleaned_data.get("password1")

    user = authenticate(email=email, password=password)
    login(request, user)

    messages.success(request, f"Dear {full_name}, your account has been created successfully")

    profile = Profile.objects.get(user=request.user)
    profile.full_name = full_name
    profile.phone = phone
    profile.save()

    return redirect("userauths:complete_profile")
  else:
    form = UserRegisterForm()


  context = {
    "form" : form
  }
  return render(request, "userauthentication/sign_up.html", context)

@login_required
def complete_profile(request):
    profile = request.user.profile
    role = request.user.role  # Get the role from the user model

    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            profile = form.save(commit=False)
            
            # Optional: Add logic based on role
            if role == 'staff' and not profile.specialization:
                messages.error(request, "Staff must provide specialization.")
                return render(request, 'userauthentication/complete_profile.html', {
                    'form': form,
                    'role': role
                })
            
            profile.save()
            messages.success(request, "Profile completed.")
            return redirect("salon:index")
    else:
        form = ProfileForm(instance=profile)

    return render(request, 'userauthentication/complete_profile.html', {
        'form': form,
        'role': role  # Pass the role to the template
    })

@login_required
def logout_view(request):
    logout(request)
    messages.success(request, "You have been successfully logged out.")
    return redirect('salon:index')   


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
  
