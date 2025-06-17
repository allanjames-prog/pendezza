document.addEventListener('DOMContentLoaded', function() {
    // Step navigation
    const form = document.getElementById('salonForm');
    const steps = document.querySelectorAll('.step-content');
    const stepIndicators = document.querySelectorAll('.steps .step');
    let currentStep = 0;

    // Show current step
    function showStep(stepIndex) {
        steps.forEach((step, index) => {
            step.classList.toggle('active', index === stepIndex);
        });
        
        stepIndicators.forEach((indicator, index) => {
            indicator.classList.toggle('active', index <= stepIndex);
        });
        
        currentStep = stepIndex;
    }

    // Next step
    document.querySelectorAll('.next-step').forEach(button => {
        button.addEventListener('click', function() {
            if (currentStep < steps.length - 1) {
                showStep(currentStep + 1);
            }
        });
    });

    // Previous step
    document.querySelectorAll('.prev-step').forEach(button => {
        button.addEventListener('click', function() {
            if (currentStep > 0) {
                showStep(currentStep - 1);
            }
        });
    });

    // Initialize
    showStep(0);
});