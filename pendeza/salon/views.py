from django.shortcuts import render, redirect, get_object_or_404
from salon.models import Salon, SalonStatus, SalonGallery, SalonFeatures, SalonFaq, ServiceGender, ServiceCategory, SalonServices, BookingStatus, PaymentStatus, Booking, StaffRole, StaffStatus, StaffOnDuty
from django.core.paginator import Paginator
from django.http import Http404
from django.views.decorators.cache import cache_page
from django.views.generic import View
from django.http import JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin



def index(request):
    salon_list = Salon.objects.filter(status=SalonStatus.LIVE)
    paginator = Paginator(salon_list, 10)  # Show 10 salons per page
    
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, "salon/salon.html", {"page_obj": page_obj})


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