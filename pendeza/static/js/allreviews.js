document.addEventListener('DOMContentLoaded', function() {
    // Smooth hover effects
    const reviewCards = document.querySelectorAll('.review-card');
    reviewCards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-5px)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = '';
        });
    });
    
    // Delete review functionality
    const deleteButtons = document.querySelectorAll('.delete-review');
    deleteButtons.forEach(button => {
        button.addEventListener('click', function() {
            const reviewId = this.getAttribute('data-review-id');
            if (confirm('Are you sure you want to delete this review?')) {
                fetch(`/reviews/${reviewId}/delete/`, {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': '{{ csrf_token }}',
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({})
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        document.querySelector(`.review-card[data-review-id="${reviewId}"]`).remove();
                        showToast('Review deleted successfully', 'success');
                        
                        // If no reviews left, show the no reviews message
                        if (document.querySelectorAll('.review-card').length === 0) {
                            const reviewsContainer = document.getElementById('reviews-container');
                            reviewsContainer.innerHTML = `
                                <div class="alert alert-info no-reviews">
                                    <i class="far fa-comment-dots fa-3x mb-3" style="color: #6c63ff;"></i>
                                    <h4>No Reviews Yet</h4>
                                    <p class="mb-0">Be the first to share your experience with this salon!</p>
                                </div>
                            `;
                        }
                    } else {
                        showToast('Failed to delete review', 'error');
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    showToast('An error occurred', 'error');
                });
            }
        });
    });
    
    // Toast notification function
    function showToast(message, type) {
        const toast = document.createElement('div');
        toast.className = `toast align-items-center text-white bg-${type} border-0 position-fixed bottom-0 end-0 m-3`;
        toast.setAttribute('role', 'alert');
        toast.setAttribute('aria-live', 'assertive');
        toast.setAttribute('aria-atomic', 'true');
        toast.style.zIndex = '1100';
        
        toast.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">
                    ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
        `;
        
        document.body.appendChild(toast);
        
        const bsToast = new bootstrap.Toast(toast);
        bsToast.show();
        
        // Remove toast after it's hidden
        toast.addEventListener('hidden.bs.toast', function() {
            document.body.removeChild(toast);
        });
    }
    
    // Animate page elements on load
    setTimeout(() => {
        document.querySelector('.container').style.opacity = '1';
        document.querySelector('.container').style.transform = 'translateY(0)';
        
        // Stagger review card animations
        reviewCards.forEach((card, index) => {
            setTimeout(() => {
                card.style.opacity = '1';
                card.style.transform = 'translateY(0)';
            }, index * 100);
        });
    }, 100);
});
