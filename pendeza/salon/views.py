from django.shortcuts import render, redirect, get_object_or_404
from salon.models import salon_image_upload_path, Salon, SalonGallery, SalonFeatures, SalonFaq, SalonServices, ServiceCategory, SalonStatus, BookingStatus, Booking, ServiceGender, PaymentStatus, StaffOnDuty, SalonReview
from django.core.paginator import Paginator
from django.http import Http404, JsonResponse
from django.views.decorators.cache import cache_page
from django.views.generic import View, ListView, CreateView, UpdateView, DeleteView, DetailView

from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy, reverse
from django.core.exceptions import PermissionDenied
from userauthentication.models import User
from datetime import datetime, timedelta
from django.forms.models import model_to_dict
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from .forms import SalonServiceForm
import json
from django.contrib.auth.decorators import login_required




# ========= SALON INDEX VIEW ==========
def index(request):
    salon_list = Salon.objects.filter(status=SalonStatus.LIVE)
    paginator = Paginator(salon_list, 10)  # Show 10 salons per page
    
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, "salon/salon.html", {"page_obj": page_obj})


# ========= SALON DETAIL VIEW ==========
@cache_page(60 * 15)  # Cache for 15 minutes
def salon_detail(request, slug):
    try:
        # Get the salon with prefetched related data
        salon = Salon.objects.select_related('user').prefetch_related(
            'gallery_images',
            'features',
            'faqs',
            'staff_members'  # Add this to prefetch staff members
        ).get(slug=slug, status=SalonStatus.LIVE)
        
        # Get active staff members ordered by display order (first 4 for the homepage)
        staff_members = salon.staff_members.filter(status='Active').order_by('display_order')[:4]
        
        # Increment view count
        salon.views += 1
        salon.save(update_fields=['views'])
        
        # Prepare context with all related data
        context = {
            'salon': salon,
            'gallery_images': salon.gallery_images.all(),
            'features': salon.features.filter(is_active=True),
            'faqs': salon.faqs.filter(is_active=True),
            'staff_members': staff_members,  # Add staff members to context
            'is_owner': request.user == salon.user,  # Check if current user owns the salon
        }
        
        return render(request, "salon/salon_detail.html", context)
        
    except Salon.DoesNotExist:
        raise Http404("Salon not found or not published yet")

# ========== SALON DELETE VIEW ==========
class SalonDeleteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        salon = get_object_or_404(Salon, pk=pk)
        
        # Check if the current user owns the salon
        if request.user != salon.user:
            return JsonResponse({'error': 'You do not have permission to delete this salon'}, status=403)
        
        # Delete the salon
        salon.delete()
        
        return JsonResponse({'success': True, 'message': 'Salon deleted successfully'})
    
# ========== SALON CREATE VIEW ==========
class SalonCreateView(LoginRequiredMixin, View):
    def post(self, request):
        name = request.POST.get('name')
        description = request.POST.get('description')
        address = request.POST.get('address')
        
        if name and description and address:
            salon = Salon(
                user=request.user,
                name=name,
                description=description,
                address=address,
                status=SalonStatus.DRAFT
            )
            salon.save()
            return JsonResponse({'success': True, 'message': 'Salon created successfully'})
        
        return JsonResponse({'error': 'Invalid data'}, status=400)
    
# ========== SALON UPDATE VIEW ==========
class SalonUpdateView(LoginRequiredMixin, View):
    def post(self, request, pk):
        salon = get_object_or_404(Salon, pk=pk)
        
        # Check if the current user owns the salon
        if request.user != salon.user:
            return JsonResponse({'error': 'You do not have permission to update this salon'}, status=403)
        
        # Update salon details
        name = request.POST.get('name')
        description = request.POST.get('description')
        address = request.POST.get('address')
        
        if name and description and address:
            salon.name = name
            salon.description = description
            salon.address = address
            salon.save()
            return JsonResponse({'success': True, 'message': 'Salon updated successfully'})
        
        return JsonResponse({'error': 'Invalid data'}, status=400)

# ===============================================
# SALON GALLERY
# ===============================================
# ========== SALON GALLERY UPLOAD VIEW ==========
class SalonGalleryUploadView(LoginRequiredMixin, View):
    def post(self, request, slug):
        salon = get_object_or_404(Salon, slug=slug)
        
        # Check if the current user owns the salon
        if request.user != salon.user:
            return JsonResponse({'error': 'You do not have permission to upload images to this salon'}, status=403)
        
        images = request.FILES.getlist('images')
        uploaded_images = []
        
        for img in images:
            gallery_image = SalonGallery(salon=salon, image=img)
            gallery_image.save()
            uploaded_images.append({
                'id': gallery_image.id,
                'url': gallery_image.image.url
            })
        
        return JsonResponse({
            'success': True,
            'message': f'{len(uploaded_images)} images uploaded successfully',
            'images': uploaded_images
        })

# ========== SALON GALLERY UPDATE VIEW ==========
class SalonGalleryUpdateView(LoginRequiredMixin, View):
    def post(self, request, slug, pk):
        salon = get_object_or_404(Salon, slug=slug)
        
        # Check if the current user owns the salon
        if request.user != salon.user:
            return JsonResponse({'error': 'You do not have permission to update this image'}, status=403)
        
        gallery_image = get_object_or_404(SalonGallery, id=pk, salon=salon)
        
        if 'image' in request.FILES:
            gallery_image.image = request.FILES['image']
            gallery_image.save()
            return JsonResponse({'success': True, 'message': 'Image updated successfully'})
        
        return JsonResponse({'error': 'Invalid data'}, status=400)
    
# ========== SALON GALLERY DELETE VIEW ==========
class SalonGalleryDeleteView(LoginRequiredMixin, View):
    def post(self, request, slug, pk):
        salon = get_object_or_404(Salon, slug=slug)
        
        # Check if the current user owns the salon
        if request.user != salon.user:
            return JsonResponse({'error': 'You do not have permission to delete this image'}, status=403)
        
        gallery_image = get_object_or_404(SalonGallery, id=pk, salon=salon)
        gallery_image.delete()
        
        return JsonResponse({'success': True, 'message': 'Image deleted successfully'})


# ========== SALON GALLERY STATUS UPDATE VIEW ==========
class SalonGalleryStatusUpdateView(LoginRequiredMixin, View):
    def post(self, request, slug, pk):
        salon = get_object_or_404(Salon, slug=slug)
        
        # Check if the current user owns the salon
        if request.user != salon.user:
            return JsonResponse({'error': 'You do not have permission to update this image'}, status=403)
        
        gallery_image = get_object_or_404(SalonGallery, id=pk, salon=salon)
        
        is_active = request.POST.get('is_active') == 'true'
        
        gallery_image.is_active = is_active
        gallery_image.save()
        
        return JsonResponse({'success': True, 'message': 'Image status updated successfully'})
    
# ===============================================
# SALON TEAM LIST VIEW
# ===============================================
from django.views.generic import ListView, DetailView
from .models import StaffOnDuty

class TeamListView(ListView):
    model = StaffOnDuty
    template_name = 'salon/team_list.html'
    context_object_name = 'staff_members'
    
    def get_queryset(self):
        return StaffOnDuty.objects.filter(
            salon__slug=self.kwargs['slug'],
            status='Active'
        ).order_by('display_order')

class TeamDetailView(DetailView):
    model = StaffOnDuty
    template_name = 'salon/team_detail.html'
    context_object_name = 'staff_member'
    
    def get_object(self, queryset=None):
        return get_object_or_404(
            StaffOnDuty,
            salon__slug=self.kwargs['slug'],
            id=self.kwargs['staff_id'],
            status='Active'
        )
# ========== SALON TEAM MEMBER UPDATE VIEW ==========
class TeamMemberUpdateView(LoginRequiredMixin, UpdateView):
    model = StaffOnDuty
    template_name = 'salon/team_member_form.html'
    fields = ['name', 'position', 'bio', 'image', 'status']
    
    def get_object(self, queryset=None):
        return get_object_or_404(
            StaffOnDuty,
            salon__slug=self.kwargs['slug'],
            id=self.kwargs['staff_id']
        )
    
    def form_valid(self, form):
        form.instance.salon = get_object_or_404(Salon, slug=self.kwargs['slug'])
        return super().form_valid(form)


# ========== STAFF AVAILABILITY CHECK ==========
class StaffAvailabilityView(LoginRequiredMixin, View):
    def get(self, request):
        staff_id = request.GET.get('staff_id')
        date = request.GET.get('date')
        service_id = request.GET.get('service_id')
        
        if not all([staff_id, date, service_id]):
            return JsonResponse({'error': 'Missing parameters'}, status=400)
        
        try:
            staff = User.objects.get(pk=staff_id)
            service = SalonServices.objects.get(pk=service_id)
            booking_date = datetime.strptime(date, '%Y-%m-%d').date()
        except (User.DoesNotExist, SalonServices.DoesNotExist, ValueError):
            return JsonResponse({'error': 'Invalid parameters'}, status=400)
        
        # Get existing bookings for this staff member on this date
        bookings = Booking.objects.filter(
            staff_member=staff,
            booking_date=booking_date
        ).exclude(status=BookingStatus.CANCELLED)
        
        # Get staff working hours (you'll need to implement this based on your StaffOnDuty model)
        working_hours = self.get_staff_working_hours(staff, booking_date)
        
        # Calculate available slots
        available_slots = self.calculate_available_slots(working_hours, bookings, service.duration)
        
        return JsonResponse({'available_slots': available_slots})

    def get_staff_working_hours(self, staff, date):
        try:
            staff_on_duty = StaffOnDuty.objects.get(staff_member=staff, date=date)
            return {
                'start': staff_on_duty.start_time,
                'end': staff_on_duty.end_time,
                'break_start': staff_on_duty.break_start_time,
                'break_end': staff_on_duty.break_end_time
            }
        except StaffOnDuty.DoesNotExist:
            return None

    def calculate_available_slots(self, working_hours, existing_bookings, service_duration):
       available_slots = []
       for hour in range(working_hours['start'], working_hours['end']):
           for minute in [0, 30]:
               slot = f"{hour:02}:{minute:02}"
               if slot not in [booking.start_time for booking in existing_bookings]:
                   available_slots.append(slot)
       return available_slots
    
# ========== SALON TEAM MEMBER DELETE VIEW ==========
class TeamMemberDeleteView(LoginRequiredMixin, View):
    def post(self, request, slug, staff_id):
        salon = get_object_or_404(Salon, slug=slug)
        
        # Check if the current user owns the salon
        if request.user != salon.user:
            return JsonResponse({'error': 'You do not have permission to delete this team member'}, status=403)
        
        staff_member = get_object_or_404(StaffOnDuty, id=staff_id, salon=salon)
        staff_member.delete()
        
        return JsonResponse({'success': True, 'message': 'Team member deleted successfully'})

# ===============================================
# SALON FEATURES
# ===============================================
# ========== SALON FEATURES VIEW ==========
class SalonFeaturesView(LoginRequiredMixin, View):
    def post(self, request, slug):
        salon = get_object_or_404(Salon, slug=slug)
        
        # Check if the current user owns the salon
        if request.user != salon.user:
            return JsonResponse({'error': 'You do not have permission to add features to this salon'}, status=403)
        
        feature_name = request.POST.get('feature_name')
        feature_description = request.POST.get('feature_description')
        
        if feature_name and feature_description:
            feature = SalonFeatures(salon=salon, name=feature_name, description=feature_description)
            feature.save()
            return JsonResponse({'success': True, 'message': 'Feature added successfully'})
        
        return JsonResponse({'error': 'Invalid data'}, status=400)
    
# ========== SALON FEATURES UPDATE VIEW ==========
class SalonFeaturesUpdateView(LoginRequiredMixin, View):
    def post(self, request, slug, feature_id):
        salon = get_object_or_404(Salon, slug=slug)
        
        # Check if the current user owns the salon
        if request.user != salon.user:
            return JsonResponse({'error': 'You do not have permission to update features of this salon'}, status=403)
        
        feature = get_object_or_404(SalonFeatures, id=feature_id, salon=salon)
        
        feature_name = request.POST.get('feature_name')
        feature_description = request.POST.get('feature_description')
        
        if feature_name and feature_description:
            feature.name = feature_name
            feature.description = feature_description
            feature.save()
            return JsonResponse({'success': True, 'message': 'Feature updated successfully'})
        
        return JsonResponse({'error': 'Invalid data'}, status=400)
    
# ========== SALON FEATURES DELETE VIEW ==========
class SalonFeaturesDeleteView(LoginRequiredMixin, View):
    def post(self, request, slug, feature_id):
        salon = get_object_or_404(Salon, slug=slug)
        
        # Check if the current user owns the salon
        if request.user != salon.user:
            return JsonResponse({'error': 'You do not have permission to delete features of this salon'}, status=403)
        
        feature = get_object_or_404(SalonFeatures, id=feature_id, salon=salon)
        feature.delete()
        
        return JsonResponse({'success': True, 'message': 'Feature deleted successfully'})


# ===============================================
# SALON FAQ
# ===============================================

# ========== SALON FAQ VIEW ==========
class SalonFaqView(LoginRequiredMixin, View):
    def post(self, request, slug):
        salon = get_object_or_404(Salon, slug=slug)
        
        # Check if the current user owns the salon
        if request.user != salon.user:
            return JsonResponse({'error': 'You do not have permission to add FAQs to this salon'}, status=403)
        
        question = request.POST.get('question')
        answer = request.POST.get('answer')
        
        if question and answer:
            faq = SalonFaq(salon=salon, question=question, answer=answer)
            faq.save()
            return JsonResponse({'success': True, 'message': 'FAQ added successfully'})
        
        return JsonResponse({'error': 'Invalid data'}, status=400)

# ========== SALON FAQ UPDATE VIEW ==========
class SalonFaqUpdateView(LoginRequiredMixin, View):
    def post(self, request, slug, faq_id):
        salon = get_object_or_404(Salon, slug=slug)
        
        # Check if the current user owns the salon
        if request.user != salon.user:
            return JsonResponse({'error': 'You do not have permission to update FAQs of this salon'}, status=403)
        
        faq = get_object_or_404(SalonFaq, id=faq_id, salon=salon)
        
        question = request.POST.get('question')
        answer = request.POST.get('answer')
        
        if question and answer:
            faq.question = question
            faq.answer = answer
            faq.save()
            return JsonResponse({'success': True, 'message': 'FAQ updated successfully'})
        
        return JsonResponse({'error': 'Invalid data'}, status=400)
    
# ========== SALON FAQ DELETE VIEW ==========
class SalonFaqDeleteView(LoginRequiredMixin, View):
    def post(self, request, slug, faq_id):
        salon = get_object_or_404(Salon, slug=slug)
        
        # Check if the current user owns the salon
        if request.user != salon.user:
            return JsonResponse({'error': 'You do not have permission to delete FAQs of this salon'}, status=403)
        
        faq = get_object_or_404(SalonFaq, id=faq_id, salon=salon)
        faq.delete()
        
        return JsonResponse({'success': True, 'message': 'FAQ deleted successfully'})
    

# ===============================================
# SALON SERVICES API VIEW
# ===============================================
@method_decorator(csrf_exempt, name='dispatch')
class SalonServiceAPIView(View):
    """Handles all service CRUD operations in one view"""
    
    def get(self, request, slug, service_id=None):
        """
        GET: Retrieve single service or list of all services
        - /salon/<slug>/services/ (list all)
        - /salon/<slug>/services/<service_id>/ (single service)
        """
        salon = get_object_or_404(Salon, slug=slug)
        
        # Verify ownership
        if request.user != salon.user and not request.user.is_staff:
            return JsonResponse({'error': 'Permission denied'}, status=403)
        
        if service_id:  # Single service
            service = get_object_or_404(SalonServices, id=service_id, salon=salon)
            data = {
                'id': service.id,
                'name': service.name,
                'description': service.description,
                'base_price': str(service.base_price),
                'women_price': str(service.women_price) if service.women_price else None,
                'men_price': str(service.men_price) if service.men_price else None,
                'children_price': str(service.children_price) if service.children_price else None,
                'duration': service.duration,
                'category': service.category,
                'category_display': service.get_category_display(),
                'gender': service.gender,
                'gender_display': service.get_gender_display(),
                'is_featured': service.is_featured,
                'is_active': service.is_active,
                'icon': service.icon,
                'created_at': service.created_at.isoformat(),
            }
            return JsonResponse(data)
        else:  # All services
            services = salon.services.all().order_by('category', 'name')
            services_data = [{
                'id': s.id,
                'name': s.name,
                'base_price': str(s.base_price),
                'duration': s.duration,
                'category': s.get_category_display(),
                'is_active': s.is_active
            } for s in services]
            return JsonResponse(services_data, safe=False)
    
    def post(self, request, slug):
        """
        POST: Create new service
        - /salon/<slug>/services/
        """
        if not request.META.get('HTTP_X_CSRFTOKEN') == request.COOKIES.get('csrftoken'):
            return JsonResponse({'error': 'CSRF verification failed'}, status=403)
        salon = get_object_or_404(Salon, slug=slug)
        
        if request.user != salon.user:
            return JsonResponse({'error': 'Permission denied'}, status=403)
        
        try:
            data = json.loads(request.body)
            form = SalonServiceForm(data)
            
            if form.is_valid():
                service = form.save(commit=False)
                service.salon = salon
                service.save()
                return JsonResponse({
                    'success': True,
                    'message': 'Service created successfully',
                    'service_id': service.id
                }, status=201)
            return JsonResponse({
                'error': 'Invalid data',
                'details': form.errors
            }, status=400)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
    
    def put(self, request, slug, service_id):
        """
        PUT: Update existing service
        - /salon/<slug>/services/<service_id>/
        """
        if not request.META.get('HTTP_X_CSRFTOKEN') == request.COOKIES.get('csrftoken'):
            return JsonResponse({'error': 'CSRF verification failed'}, status=403)
        salon = get_object_or_404(Salon, slug=slug)
        service = get_object_or_404(SalonServices, id=service_id, salon=salon)
        
        if request.user != salon.user:
            return JsonResponse({'error': 'Permission denied'}, status=403)
        
        try:
            data = json.loads(request.body)
            form = SalonServiceForm(data, instance=service)
            
            if form.is_valid():
                form.save()
                return JsonResponse({
                    'success': True,
                    'message': 'Service updated successfully'
                })
            return JsonResponse({
                'error': 'Invalid data',
                'details': form.errors
            }, status=400)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
    
    def patch(self, request, slug, service_id):
        """
        PATCH: Partial update of service (e.g., status toggle)
        - /salon/<slug>/services/<service_id>/
        """
        if not request.META.get('HTTP_X_CSRFTOKEN') == request.COOKIES.get('csrftoken'):
            return JsonResponse({'error': 'CSRF verification failed'}, status=403)
        salon = get_object_or_404(Salon, slug=slug)
        service = get_object_or_404(SalonServices, id=service_id, salon=salon)
        
        if request.user != salon.user:
            return JsonResponse({'error': 'Permission denied'}, status=403)
        
        try:
            data = json.loads(request.body)
            
            # Handle status toggle
            if 'is_active' in data:
                service.is_active = data['is_active']
                service.save()
                return JsonResponse({
                    'success': True,
                    'message': 'Service status updated',
                    'is_active': service.is_active
                })
            
            return JsonResponse({
                'error': 'No valid fields to update'
            }, status=400)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
    
    def delete(self, request, slug, service_id):
        """
        DELETE: Remove a service
        - /salon/<slug>/services/<service_id>/
        """
        if not request.META.get('HTTP_X_CSRFTOKEN') == request.COOKIES.get('csrftoken'):
            return JsonResponse({'error': 'CSRF verification failed'}, status=403)
        salon = get_object_or_404(Salon, slug=slug)
        service = get_object_or_404(SalonServices, id=service_id, salon=salon)
        
        if request.user != salon.user:
            return JsonResponse({'error': 'Permission denied'}, status=403)
        
        service.delete()
        return JsonResponse({
            'success': True,
            'message': 'Service deleted successfully'
        }, status=204)



# ============================================
# SALON REVIEWS
# ============================================
# ========== SALON REVIEWS VIEW ==========
# add_review

@login_required
def add_review(request, slug):
    if request.method == 'POST':
        try:
            data = request.POST
            salon = get_object_or_404(Salon, slug=slug)
            user = request.user
            rating = int(data.get('rating'))
            comment = data.get('comment')

            review = SalonReview.objects.create(
                salon=salon,
                user=user,
                rating=rating,
                comment=comment
            )

            return redirect('salon:salon_detail', slug=salon.slug)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)

    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=405)

# SALON REVIEW DETAIL VIEW
def salon_detail(request, slug):
    salon = get_object_or_404(Salon, slug=slug)
    reviews = salon.reviews.select_related('user').all()
    review_summary = SalonReview.objects.filter(salon=salon).first()
    context = {
        'salon': salon,
        'reviews': reviews,
        'review_summary': review_summary.get_review_summary() if review_summary else None
    }
    return render(request, 'salon/salon_detail.html', context)



# ============================================
# BOOKING AND PAYMENT STATUS VIEWS
# ============================================
# ========== BOOKING LIST VIEW ==========
class BookingListView(LoginRequiredMixin, ListView):
    model = Booking
    template_name = 'salon/booking_list.html'
    context_object_name = 'bookings'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        
        # For salon owners - show their salon's bookings
        if hasattr(self.request.user, 'salons'):
            salon_ids = self.request.user.salons.values_list('id', flat=True)
            return queryset.filter(salon_id__in=salon_ids)
        
        # For regular users - show only their bookings
        return queryset.filter(user=self.request.user)

# ========== BOOKING CREATE VIEW ==========
class BookingCreateView(LoginRequiredMixin, CreateView):
    model = Booking
    template_name = 'salon/booking_form.html'
    fields = ['salon', 'service', 'booking_date', 'start_time', 'gender', 'notes']
    success_url = reverse_lazy('booking_list')

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.status = BookingStatus.PENDING
        form.instance.payment_status = PaymentStatus.PENDING
        
        # Calculate price based on gender
        service = form.cleaned_data['service']
        form.instance.price = service.get_price_for_gender(form.cleaned_data['gender'])
        
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['services'] = SalonServices.objects.filter(is_active=True)
        return context

# ========== BOOKING DETAIL VIEW ==========
class BookingDetailView(LoginRequiredMixin, DetailView):
    model = Booking
    template_name = 'salon/booking_detail.html'
    context_object_name = 'booking'

    def get_queryset(self):
        queryset = super().get_queryset()
        return self.filter_by_user_permission(queryset)

    def filter_by_user_permission(self, queryset):
        booking = get_object_or_404(queryset, pk=self.kwargs['pk'])
        
        # Allow access if user is the booking owner or salon owner
        if self.request.user == booking.user or self.request.user == booking.salon.user:
            return queryset
        raise PermissionDenied

# ========== BOOKING UPDATE VIEW ==========
class BookingUpdateView(LoginRequiredMixin, UpdateView):
    model = Booking
    template_name = 'salon/booking_form.html'
    fields = ['service', 'booking_date', 'start_time', 'gender', 'notes']
    success_url = reverse_lazy('booking_list')

    def get_queryset(self):
        queryset = super().get_queryset()
        return self.filter_by_user_permission(queryset)

    def form_valid(self, form):
        if form.instance.status not in [BookingStatus.PENDING, BookingStatus.CONFIRMED]:
            form.add_error(None, "Only pending or confirmed bookings can be modified")
            return self.form_invalid(form)
        return super().form_valid(form)

# ========== BOOKING DELETE VIEW ==========
class BookingDeleteView(LoginRequiredMixin, DeleteView):
    model = Booking
    template_name = 'salon/booking_confirm_delete.html'
    success_url = reverse_lazy('booking_list')

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(user=self.request.user)

# ========== BOOKING STATUS UPDATE VIEW ==========
class BookingStatusUpdateView(LoginRequiredMixin, View):
    def post(self, request, pk):
        booking = get_object_or_404(Booking, pk=pk)
        
        # Verify user has permission (salon owner or staff)
        if request.user != booking.salon.user and request.user not in booking.salon.staff_members.all():
            return JsonResponse({'error': 'Permission denied'}, status=403)
        
        new_status = request.POST.get('status')
        if new_status not in BookingStatus.values:
            return JsonResponse({'error': 'Invalid status'}, status=400)
        
        # Validate status transitions
        valid_transitions = {
            BookingStatus.PENDING: [BookingStatus.CONFIRMED, BookingStatus.CANCELLED],
            BookingStatus.CONFIRMED: [BookingStatus.COMPLETED, BookingStatus.CANCELLED, BookingStatus.NO_SHOW],
            # Add other valid transitions as needed
        }
        
        if new_status not in valid_transitions.get(booking.status, []):
            return JsonResponse({'error': 'Invalid status transition'}, status=400)
        
        booking.status = new_status
        booking.save()
        
        return JsonResponse({
            'success': True,
            'new_status': booking.get_status_display(),
            'status_class': self.get_status_class(new_status)
        })

    def get_status_class(self, status):
        status_classes = {
            BookingStatus.PENDING: 'warning',
            BookingStatus.CONFIRMED: 'info',
            BookingStatus.COMPLETED: 'success',
            BookingStatus.CANCELLED: 'danger',
            BookingStatus.NO_SHOW: 'secondary',
        }
        return status_classes.get(status, 'light')

# ========== PAYMENT STATUS UPDATE VIEW ==========
class PaymentStatusUpdateView(LoginRequiredMixin, View):
    def post(self, request, pk):
        booking = get_object_or_404(Booking, pk=pk)
        
        # Verify user has permission (salon owner or staff)
        if request.user != booking.salon.user and request.user not in booking.salon.staff_members.all():
            return JsonResponse({'error': 'Permission denied'}, status=403)
        
        new_status = request.POST.get('status')
        if new_status not in PaymentStatus.values:
            return JsonResponse({'error': 'Invalid status'}, status=400)
        
        booking.payment_status = new_status
        booking.save()
        
        return JsonResponse({
            'success': True,
            'new_status': booking.get_payment_status_display(),
            'status_class': self.get_status_class(new_status)
        })

    def get_status_class(self, status):
        status_classes = {
            PaymentStatus.PENDING: 'warning',
            PaymentStatus.PAID: 'success',
            PaymentStatus.PARTIAL: 'info',
            PaymentStatus.REFUNDED: 'secondary',
            PaymentStatus.FAILED: 'danger',
        }
        return status_classes.get(status, 'light')

# ========== BOOKING CALENDAR VIEW ==========
class BookingCalendarView(LoginRequiredMixin, View):
    def get(self, request):
        # For salon owners - show their salon's bookings
        if hasattr(request.user, 'salons'):
            salon_ids = request.user.salons.values_list('id', flat=True)
            bookings = Booking.objects.filter(salon_id__in=salon_ids)
        else:
            # For regular users - show only their bookings
            bookings = Booking.objects.filter(user=request.user)
        
        events = []
        for booking in bookings:
            events.append({
                'title': booking.calendar_event_title,
                'start': f"{booking.booking_date}T{booking.start_time}",
                'end': f"{booking.booking_date}T{booking.end_time}",
                'status': booking.status,
                'payment_status': booking.payment_status,
                'url': reverse('booking_detail', kwargs={'pk': booking.pk}),
            })
        
        return JsonResponse(events, safe=False)


        
