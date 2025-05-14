from django.shortcuts import render, redirect, get_object_or_404
from salon.models import salon_image_upload_path, Salon, SalonGallery, SalonFeatures, SalonFaq, SalonServices, ServiceCategory, SalonStatus, BookingStatus, Booking, ServiceGender, PaymentStatus, StaffOnDuty, SalonReview
from django.core.paginator import Paginator
from django.http import Http404
from django.views.decorators.cache import cache_page
from django.views.generic import View, ListView, CreateView, UpdateView, DeleteView, DetailView
from django.http import JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin

from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy

from django.core.exceptions import PermissionDenied
from userauthentication.models import User
from datetime import datetime, timedelta
from django.urls import reverse

# Import json for JSON responses
import json



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
            'faqs'
        ).get(slug=slug, status=SalonStatus.LIVE)
        
        # Increment view count
        salon.views += 1
        salon.save(update_fields=['views'])
        
        # Prepare context with all related data
        context = {
            'salon': salon,
            'gallery_images': salon.gallery_images.all(),
            'features': salon.features.filter(is_active=True),
            'faqs': salon.faqs.filter(is_active=True),
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
# SALON SERVICES
# ===============================================

# ========== SALON SERVICES VIEW ==========
class SalonServicesView(LoginRequiredMixin, View):
    def post(self, request, slug):
        salon = get_object_or_404(Salon, slug=slug)
        
        # Check if the current user owns the salon
        if request.user != salon.user:
            return JsonResponse({'error': 'You do not have permission to add services to this salon'}, status=403)
        
        service_name = request.POST.get('service_name')
        service_description = request.POST.get('service_description')
        service_price = request.POST.get('service_price')
        service_duration = request.POST.get('service_duration')

        if service_name and service_description and service_price and service_duration:
            service = SalonServices(salon=salon, name=service_name, description=service_description, price=service_price, duration=service_duration)
            service.save()
            return JsonResponse({'success': True, 'message': 'Service added successfully'})

        return JsonResponse({'error': 'Invalid data'}, status=400)

# ========== SALON SERVICES UPDATE VIEW ==========
class SalonServicesUpdateView(LoginRequiredMixin, View):
    def post(self, request, slug, service_id):
        salon = get_object_or_404(Salon, slug=slug)
        
        # Check if the current user owns the salon
        if request.user != salon.user:
            return JsonResponse({'error': 'You do not have permission to update services of this salon'}, status=403)
        
        service = get_object_or_404(SalonServices, id=service_id, salon=salon)
        
        service_name = request.POST.get('service_name')
        service_description = request.POST.get('service_description')
        service_price = request.POST.get('service_price')
        service_duration = request.POST.get('service_duration')

        if service_name and service_description and service_price and service_duration:
            service.name = service_name
            service.description = service_description
            service.price = service_price
            service.duration = service_duration
            service.save()
            return JsonResponse({'success': True, 'message': 'Service updated successfully'})

        return JsonResponse({'error': 'Invalid data'}, status=400)
    
# ========== SALON SERVICES DELETE VIEW ==========
class SalonServicesDeleteView(LoginRequiredMixin, View):
    def post(self, request, slug, service_id):
        salon = get_object_or_404(Salon, slug=slug)
        
        # Check if the current user owns the salon
        if request.user != salon.user:
            return JsonResponse({'error': 'You do not have permission to delete services of this salon'}, status=403)
        
        service = get_object_or_404(SalonServices, id=service_id, salon=salon)
        service.delete()
        
        return JsonResponse({'success': True, 'message': 'Service deleted successfully'})

# ========== SALON SERVICES STATUS UPDATE VIEW ==========
class SalonServicesStatusUpdateView(LoginRequiredMixin, View):
    def post(self, request, slug, service_id):
        salon = get_object_or_404(Salon, slug=slug)
        
        # Check if the current user owns the salon
        if request.user != salon.user:
            return JsonResponse({'error': 'You do not have permission to update services of this salon'}, status=403)
        
        service = get_object_or_404(SalonServices, id=service_id, salon=salon)
        
        is_active = request.POST.get('is_active') == 'true'
        
        service.is_active = is_active
        service.save()
        
        return JsonResponse({'success': True, 'message': 'Service status updated successfully'})

# ========== SALON SERVICES ORDER UPDATE VIEW ==========
class SalonServicesOrderUpdateView(LoginRequiredMixin, View):
    def post(self, request, slug):
        salon = get_object_or_404(Salon, slug=slug)
        
        # Check if the current user owns the salon
        if request.user != salon.user:
            return JsonResponse({'error': 'You do not have permission to update services order of this salon'}, status=403)
        
        service_ids = request.POST.getlist('service_ids[]')
        
        for index, service_id in enumerate(service_ids):
            service = get_object_or_404(SalonServices, id=service_id, salon=salon)
            service.order = index
            service.save()
        
        return JsonResponse({'success': True, 'message': 'Service order updated successfully'})

# ========== SALON SERVICES CATEGORY VIEW ==========
class SalonServicesCategoryView(LoginRequiredMixin, View):
    def post(self, request, slug):
        salon = get_object_or_404(Salon, slug=slug)
        
        # Check if the current user owns the salon
        if request.user != salon.user:
            return JsonResponse({'error': 'You do not have permission to add categories to this salon'}, status=403)
        
        category_name = request.POST.get('category_name')
        
        if category_name:
            category = ServiceCategory(name=category_name)
            category.save()
            return JsonResponse({'success': True, 'message': 'Category added successfully'})
        
        return JsonResponse({'error': 'Invalid data'}, status=400)

# ========== SALON SERVICES CATEGORY UPDATE VIEW ==========
class SalonServicesCategoryUpdateView(LoginRequiredMixin, View):
    def post(self, request, slug, category_id):
        salon = get_object_or_404(Salon, slug=slug)
        
        # Check if the current user owns the salon
        if request.user != salon.user:
            return JsonResponse({'error': 'You do not have permission to update categories of this salon'}, status=403)
        
        category = get_object_or_404(ServiceCategory, id=category_id)

        category_name = request.POST.get('category_name')

        if category_name:
            category.name = category_name
            category.save()
            return JsonResponse({'success': True, 'message': 'Category updated successfully'})

        return JsonResponse({'error': 'Invalid data'}, status=400)

# ========== SALON SERVICES CATEGORY DELETE VIEW ==========
class SalonServicesCategoryDeleteView(LoginRequiredMixin, View):
    def post(self, request, slug, category_id):
        salon = get_object_or_404(Salon, slug=slug)
        
        # Check if the current user owns the salon
        if request.user != salon.user:
            return JsonResponse({'error': 'You do not have permission to delete categories of this salon'}, status=403)
        
        category = get_object_or_404(ServiceCategory, id=category_id)
        category.delete()
        
        return JsonResponse({'success': True, 'message': 'Category deleted successfully'})

# ========== SALON SERVICES CATEGORY STATUS UPDATE VIEW ==========
class SalonServicesCategoryStatusUpdateView(LoginRequiredMixin, View):  
    def post(self, request, slug, category_id):
        salon = get_object_or_404(Salon, slug=slug)
        
        # Check if the current user owns the salon
        if request.user != salon.user:
            return JsonResponse({'error': 'You do not have permission to update categories status of this salon'}, status=403)
        
        category = get_object_or_404(ServiceCategory, id=category_id)
        
        is_active = request.POST.get('is_active') == 'true'
        
        category.is_active = is_active
        category.save()
        
        return JsonResponse({'success': True, 'message': 'Category status updated successfully'})

# ========== SALON SERVICES CATEGORY ORDER UPDATE VIEW ==========
class SalonServicesCategoryOrderUpdateView(LoginRequiredMixin, View):
    def post(self, request, slug):
        salon = get_object_or_404(Salon, slug=slug)
        
        # Check if the current user owns the salon
        if request.user != salon.user:
            return JsonResponse({'error': 'You do not have permission to update categories order of this salon'}, status=403)
        
        category_ids = request.POST.getlist('category_ids[]')
        for index, category_id in enumerate(category_ids):
            category = get_object_or_404(ServiceCategory, id=category_id)
            category.order = index
            category.save()
        return JsonResponse({'success': True, 'message': 'Category order updated successfully'})

# ========== SALON SERVICES GENDER VIEW ==========
class SalonServicesGenderView(LoginRequiredMixin, View):
    def post(self, request, slug):
        salon = get_object_or_404(Salon, slug=slug)

        # Check if the current user owns the salon
        if request.user != salon.user:
            return JsonResponse({'error': 'You do not have permission to update gender of this salon'}, status=403)

        gender = request.POST.get('gender')

        if gender:
            salon.gender = gender
            salon.save()
            return JsonResponse({'success': True, 'message': 'Gender updated successfully'})

        return JsonResponse({'error': 'Invalid data'}, status=400)

# ========== SALON SERVICES GENDER UPDATE VIEW ==========
class SalonServicesGenderUpdateView(LoginRequiredMixin, View):
    def post(self, request, slug):
        salon = get_object_or_404(Salon, slug=slug)

        # Check if the current user owns the salon
        if request.user != salon.user:
            return JsonResponse({'error': 'You do not have permission to update gender of this salon'}, status=403)

        gender = request.POST.get('gender')

        if gender:
            salon.gender = gender
            salon.save()
            return JsonResponse({'success': True, 'message': 'Gender updated successfully'})

        return JsonResponse({'error': 'Invalid data'}, status=400)

# ========== SALON SERVICES GENDER DELETE VIEW ==========
class SalonServicesGenderDeleteView(LoginRequiredMixin, View):
    def post(self, request, slug):
        salon = get_object_or_404(Salon, slug=slug)

        # Check if the current user owns the salon
        if request.user != salon.user:
            return JsonResponse({'error': 'You do not have permission to delete gender of this salon'}, status=403)

        salon.gender = None
        salon.save()

        return JsonResponse({'success': True, 'message': 'Gender deleted successfully'})    

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
    

# ============================================
# SALON REVIEWS
# ============================================
# ========== SALON REVIEWS VIEW ==========
# add_review
def add_review(request, pk):
    data = json.loads(request.body)
    review = SalonReview(
        salon_id=pk,
        user=request.user,
        rating=data.get('rating'),
        comment=data.get('comment')
    )
    review.save()
    return JsonResponse(review.to_dict(), status=201)