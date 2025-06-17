document.addEventListener('DOMContentLoaded', function() {
  // Initialize all functionality
  initReviewCarousel();
  initReviewForm();
  initStarRating();
  initSmoothScrolling();
  initDatePicker();
  loadServices();
});

// Fading reviews functionality
function initReviewCarousel() {
  const fadeContainer = document.querySelector('.review-fade-container');
  if (!fadeContainer) return;

  const items = document.querySelectorAll('.review-fade-item');
  const totalItems = items.length;
  let currentIndex = 0;

  function cycleReviews() {
    items.forEach(item => item.classList.remove('active'));
    items[currentIndex].classList.add('active');
    currentIndex = (currentIndex + 1) % totalItems;
    setTimeout(cycleReviews, 5000);
  }

  if (totalItems > 0) {
    items[0].classList.add('active');
    setTimeout(cycleReviews, 5000);
  }
}

// Review form handling
function initReviewForm() {
  const reviewForm = document.getElementById('reviewForm');
  const submitBtn = document.getElementById('submitReviewBtn');
  const ratingError = document.getElementById('ratingError');

  if (!reviewForm || !submitBtn) return;

  // Form submission handler
  submitBtn.addEventListener('click', function(e) {
    e.preventDefault();
    const ratingSelected = document.querySelector('input[name="rating"]:checked');
    
    if (!ratingSelected) {
      ratingError.classList.remove('d-none');
      return;
    }
    
    ratingError.classList.add('d-none');
    
    // Prepare form data
    const formData = new FormData(reviewForm);
    
    fetch(reviewForm.action, {
      method: 'POST',
      body: formData,
      headers: {
        'X-Requested-With': 'XMLHttpRequest',
      }
    })
    .then(response => {
      if (!response.ok) throw new Error('Network response was not ok');
      return response.json();
    })
    .then(data => {
      if (data.success) {
        if (typeof Swal !== 'undefined') {
          Swal.fire({
            title: 'Success!',
            text: 'Thank you for your review!',
            icon: 'success',
            confirmButtonColor: 'var(--primary-color)'
          }).then(() => {
            // Close modal and refresh content
            const modal = bootstrap.Modal.getInstance(document.getElementById('reviewModal'));
            if (modal) modal.hide();
            location.reload();
          });
        } else {
          location.reload();
        }
      } else {
        throw new Error(data.error || 'Unknown error occurred');
      }
    })
    .catch(error => {
      console.error('Error:', error);
      if (typeof Swal !== 'undefined') {
        Swal.fire({
          title: 'Error',
          text: error.message,
          icon: 'error',
          confirmButtonColor: 'var(--primary-color)'
        });
      } else {
        alert('Error: ' + error.message);
      }
    });
  });
}

// Star rating interaction
function initStarRating() {
  const starInputs = document.querySelectorAll('.star-rating input');
  const ratingError = document.getElementById('ratingError');
  
  starInputs.forEach(input => {
    input.addEventListener('change', function() {
      if (ratingError) ratingError.classList.add('d-none');
    });
  });
}

// Smooth scrolling for anchor links
function initSmoothScrolling() {
  document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener("click", function(e) {
      e.preventDefault();
      const target = document.querySelector(this.getAttribute("href"));
      if (target) {
        target.scrollIntoView({
          behavior: "smooth",
          block: "start"
        });
      }
    });
  });
}

// Datepicker initialization
function initDatePicker() {
  const dateInput = document.getElementById("date");
  if (!dateInput) return;

  const today = new Date();
  const tomorrow = new Date(today);
  tomorrow.setDate(tomorrow.getDate() + 1);

  const formatDate = (date) => {
    return date.toISOString().split('T')[0];
  };

  dateInput.min = formatDate(tomorrow);
  
  const maxDate = new Date(today);
  maxDate.setMonth(maxDate.getMonth() + 3);
  dateInput.max = formatDate(maxDate);

  // Time input constraints
  const timeInput = document.getElementById("time");
  if (timeInput) {
    timeInput.min = "09:00";
    timeInput.max = "19:30";
    timeInput.step = "1800"; // 30 minutes
  }
}
function renderServices(container, spinner, services) {
  spinner?.remove();
  
  if (!services || services.length === 0) {
    container.innerHTML = `
      <div class="col-12 text-center">
        <p class="text-muted">No services available at this time</p>
      </div>
    `;
    return;
  }
}


// Services loader
function loadServices() {
  const container = document.getElementById('services-container');
  if (!container) return;

  const spinner = container.querySelector('.spinner-border');
  const salonSlug = container.dataset.salonSlug || '';

  fetch(`/salon/${salonSlug}/services/`)
    .then(response => {
      if (!response.ok) throw new Error('Network response was not ok');
      return response.json();
    })
    .then(services => {
      renderServices(container, spinner, services);
    })
    .catch(error => {
      console.error('Error loading services:', error);
      handleServicesError(container, spinner);
    });
}

function renderServices(container, spinner, services) {
  spinner?.remove();
  
  if (!services || services.length === 0) {
    container.innerHTML = `
      <div class="col-12 text-center">
        <p class="text-muted">No services available at this time</p>
      </div>
    `;
    return;
  }

  const activeServices = services.filter(service => service.is_active);
  let servicesHTML = '';
  
  activeServices.slice(0, 6).forEach(service => {
    servicesHTML += createServiceCardHTML(service);
  });

  container.innerHTML = servicesHTML;

  if (activeServices.length > 6) {
    document.getElementById('view-all-btn')?.classList.remove('d-none');
  }

  // Add event listeners for detail buttons
  document.querySelectorAll('.view-details').forEach(button => {
    button.addEventListener('click', function() {
      const serviceId = this.dataset.serviceId;
      showServiceDetails(serviceId);
    });
  });
}

function createServiceCardHTML(service) {
  const price = service.gender === 'Unisex' || !service.gender ? 
    `$${service.base_price}+` : 
    `From $${service.base_price}+`;
  
  const featuredBadge = service.is_featured ? 
    `<div class="featured-badge">Featured</div>` : '';
  
  const icon = service.icon ? 
    `<i class="${service.icon} me-2"></i>` : '';
  
  return `
    <div class="col-md-6 col-lg-4 mb-4">
      <div class="service-card h-100" data-service-id="${service.id}">
        ${featuredBadge}
        <div class="service-card-header">
          <h5 class="mb-0">
            ${icon}
            ${service.name}
          </h5>
          <span class="service-price">${price}</span>
        </div>
        <div class="service-card-body">
          ${service.description ? `<p>${service.description}</p>` : ''}
          <div class="d-flex justify-content-between align-items-center mt-3">
            <span class="service-duration">
              <i class="fas fa-clock me-1"></i>
              ${service.duration} min
            </span>
            <span class="service-category badge bg-light text-dark">
              ${service.category}
            </span>
            <button class="btn btn-sm btn-primary view-details" 
                    data-service-id="${service.id}">
              Details
            </button>
          </div>
        </div>
      </div>
    </div>
  `;
}

function handleServicesError(container, spinner) {
  spinner?.remove();
  container.innerHTML = `
    <div class="col-12 text-center">
      <p class="text-danger">Error loading services. Please try again later.</p>
    </div>
  `;
}


function showServiceDetails(serviceId) {
  const modal = new bootstrap.Modal(document.getElementById('serviceModal'));
  const modalTitle = document.getElementById('serviceModalTitle');
  const modalBody = document.getElementById('serviceModalBody');
  
  // Show loading state
  modalTitle.textContent = 'Loading...';
  modalBody.innerHTML = '<div class="text-center"><div class="spinner-border text-primary" role="status"><span class="visually-hidden">Loading...</span></div></div>';
  
  // Get the salon slug - more robust method
  const salonSlug = document.body.dataset.salonSlug || 
                   document.getElementById('services-container')?.dataset.salonSlug || 
                   window.location.pathname.split('/')[2];
  
  if (!salonSlug) {
    showError(modal, modalTitle, modalBody, 'Salon identifier missing');
    return;
  }
  
  console.log(`Fetching service ${serviceId} for salon ${salonSlug}`); // Debug log
  
  fetch(`/salon/${salonSlug}/services/${serviceId}/`)
    .then(response => {
      console.log('Raw response:', response); // Debug log
      if (!response.ok) {
        return response.json().then(err => {
          throw new Error(err.error || `HTTP error! status: ${response.status}`);
        }).catch(() => {
          throw new Error(`HTTP error! status: ${response.status}`);
        });
      }
      return response.json();
    })
    .then(service => {
      console.log('Service data:', service); // Debug log
      if (!service || !service.id) {
        throw new Error('Invalid service data received');
      }
      renderServiceDetails(modal, modalTitle, modalBody, service);
    })
    .catch(error => {
      console.error('Error loading service details:', error);
      showError(modal, modalTitle, modalBody, error.message);
    });
}

function renderServiceDetails(modal, modalTitle, modalBody, service) {
  modalTitle.textContent = service.name;
  
  const basePrice = service.base_price ? `$${parseFloat(service.base_price).toFixed(2)}` : 'Not specified';
  const womenPrice = service.women_price ? `$${parseFloat(service.women_price).toFixed(2)}` : 'Not offered';
  const menPrice = service.men_price ? `$${parseFloat(service.men_price).toFixed(2)}` : 'Not offered';
  const childrenPrice = service.children_price ? `$${parseFloat(service.children_price).toFixed(2)}` : 'Not offered';
  
  modalBody.innerHTML = `
    <div class="row">
      <div class="col-md-6">
        <p class="text-muted">${service.description || 'No description available.'}</p>
        <div class="mb-3">
          <h6>Duration:</h6>
          <p>${service.duration} minutes</p>
        </div>
        <div class="mb-3">
          <h6>Category:</h6>
          <p>${service.category_display || service.category || 'N/A'}</p>
        </div>
      </div>
      <div class="col-md-6">
        <div class="card">
          <div class="card-header bg-light">
            <h6 class="mb-0">Pricing</h6>
          </div>
          <div class="card-body">
            <ul class="list-group list-group-flush">
              <li class="list-group-item d-flex justify-content-between align-items-center">
                Base Price
                <span class="badge bg-primary rounded-pill">${basePrice}</span>
              </li>
              <li class="list-group-item d-flex justify-content-between align-items-center">
                Women
                <span class="badge bg-primary rounded-pill">${womenPrice}</span>
              </li>
              <li class="list-group-item d-flex justify-content-between align-items-center">
                Men
                <span class="badge bg-primary rounded-pill">${menPrice}</span>
              </li>
              <li class="list-group-item d-flex justify-content-between align-items-center">
                Children
                <span class="badge bg-primary rounded-pill">${childrenPrice}</span>
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  `;
  
  const bookNowBtn = document.querySelector('#serviceModal .btn-primary');
  if (bookNowBtn) {
    bookNowBtn.href = `#booking?service=${service.id}`;
  }
  
  modal.show();
}

function showError(modal, modalTitle, modalBody, message) {
  modalTitle.textContent = 'Error';
  modalBody.innerHTML = `
    <div class="alert alert-danger">
      <i class="fas fa-exclamation-circle me-2"></i>
      Could not load service details: ${message}
    </div>
    <button class="btn btn-secondary mt-2" onclick="window.location.reload()">
      <i class="fas fa-sync-alt me-1"></i> Try Again
    </button>
  `;
  modal.show();
}