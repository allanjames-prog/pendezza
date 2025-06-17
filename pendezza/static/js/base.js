// Wait for DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    // Preloader
    window.addEventListener('load', function() {
        const preloader = document.getElementById('preloader');
        if (preloader) {
            setTimeout(function() {
                preloader.style.opacity = '0';
                setTimeout(function() {
                    preloader.style.display = 'none';
                }, 500);
            }, 500);
        }
    });

    // Navbar scroll effect
    window.addEventListener('scroll', function() {
        const navbar = document.querySelector('.navbar');
        if (navbar) {
            navbar.classList.toggle('scrolled', window.scrollY > 50);
        }
    });

    // Back to top button
    window.addEventListener('scroll', function() {
        const backToTop = document.getElementById('backToTop');
        if (backToTop) {
            backToTop.classList.toggle('active', window.pageYOffset > 300);
        }
    });

    // Back to top functionality
    const backToTopBtn = document.getElementById('backToTop');
    if (backToTopBtn) {
        backToTopBtn.addEventListener('click', function(e) {
            e.preventDefault();
            window.scrollTo({
                top: 0,
                behavior: 'smooth'
            });
        });
    }

    // Update copyright year
    const currentYear = document.getElementById('current-year');
    if (currentYear) {
        currentYear.textContent = new Date().getFullYear();
    }

    // Initialize AOS animation
    if (typeof AOS !== 'undefined') {
        AOS.init({
            duration: 800,
            easing: 'ease-in-out',
            once: true
        });
    }

    // Carousel initialization
    if (typeof $ !== 'undefined' && $('#reviewsCarousel').length) {
        $('#reviewsCarousel').carousel({
            interval: 5000
        });
    }

    // Logout confirmation
    document.querySelectorAll('form[action*="logout"] button[type="submit"]').forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const form = this.closest('form');

            if (typeof Swal !== 'undefined') {
                Swal.fire({
                    title: 'Logout?',
                    text: 'Are you sure you want to logout?',
                    icon: 'question',
                    showCancelButton: true,
                    confirmButtonColor: 'var(--primary-color)',
                    cancelButtonColor: '#d33',
                    confirmButtonText: 'Yes, logout!'
                }).then((result) => {
                    if (result.isConfirmed) {
                        form.submit();
                    }
                });
            } else {
                form.submit();
            }
        });
    });
});