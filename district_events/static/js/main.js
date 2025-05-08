document.addEventListener('DOMContentLoaded', function() {
  
    initTooltips();

    initPopovers();
    
    setupFlashMessages();
   
    setupMobileNav();
    setupSearch();
    
    // Initialize city selector on homepage
    initCitySelector();
    
    // Handle newsletter subscription
    setupNewsletterForm();
    
    // Initialize lazy loading for images
    initLazyLoading();
});

/**
 * Initialize Bootstrap tooltips
 */
function initTooltips() {
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl, {
            boundary: document.body
        });
    });
}

/**
 * Initialize Bootstrap popovers
 */
function initPopovers() {
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function(popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
}

/**
 * Handle flash message dismissal
 */
function setupFlashMessages() {
    const flashMessages = document.querySelectorAll('.alert');
    flashMessages.forEach(message => {
        // Auto dismiss after 5 seconds
        setTimeout(() => {
            const closeBtn = message.querySelector('.btn-close');
            if (closeBtn && message.parentNode) {
                closeBtn.click();
            }
        }, 5000);
    });
}

/**
 * Setup mobile navigation functionality
 */
function setupMobileNav() {
    const navbarToggler = document.querySelector('.navbar-toggler');
    const navbarCollapse = document.querySelector('.navbar-collapse');
    
    if (navbarToggler && navbarCollapse) {
        // Close navbar when clicking outside
        document.addEventListener('click', function(event) {
            const isClickInside = navbarToggler.contains(event.target) || navbarCollapse.contains(event.target);
            
            if (!isClickInside && navbarCollapse.classList.contains('show')) {
                navbarToggler.click();
            }
        });
        
        // Close navbar when clicking on a link (for mobile)
        const navLinks = navbarCollapse.querySelectorAll('.nav-link');
        navLinks.forEach(link => {
            link.addEventListener('click', function() {
                if (navbarCollapse.classList.contains('show')) {
                    navbarToggler.click();
                }
            });
        });
    }
}

/**
 * Setup search functionality
 */
function setupSearch() {
    const searchForm = document.querySelector('.search-form');
    const searchInput = searchForm ? searchForm.querySelector('input[type="search"]') : null;
    
    if (searchForm && searchInput) {
        // Prevent empty searches
        searchForm.addEventListener('submit', function(event) {
            if (!searchInput.value.trim()) {
                event.preventDefault();
                searchInput.focus();
            }
        });
        
        // Clear search on ESC key
        searchInput.addEventListener('keydown', function(event) {
            if (event.key === 'Escape') {
                searchInput.value = '';
                searchInput.blur();
            }
        });
    }
}

/**
 * Initialize city selector on homepage
 */
function initCitySelector() {
    const citySelector = document.getElementById('citySelector');
    
    if (citySelector) {
        citySelector.addEventListener('change', function() {
            // This is handled in the home.html template
            // The selector makes an AJAX call to filter events by city
        });
    }
}

/**
 * Setup newsletter subscription form
 */
function setupNewsletterForm() {
    const newsletterForm = document.getElementById('newsletterForm');
    
    if (newsletterForm) {
        newsletterForm.addEventListener('submit', function(event) {
            event.preventDefault();
            
            const emailInput = this.querySelector('input[type="email"]');
            const email = emailInput.value.trim();
            
            if (!email) {
                showFormError(emailInput, 'Please enter your email address');
                return;
            }
            
            if (!isValidEmail(email)) {
                showFormError(emailInput, 'Please enter a valid email address');
                return;
            }
            
            // Here you would normally send an AJAX request to subscribe the user
            // For this example, we'll just show a success message
            
            // Hide the form
            this.style.display = 'none';
            
            // Show success message
            const successMessage = document.createElement('div');
            successMessage.className = 'alert alert-success mt-3';
            successMessage.innerHTML = '<i class="fas fa-check-circle me-2"></i> Thank you for subscribing to our newsletter!';
            this.parentNode.appendChild(successMessage);
        });
    }
}

/**
 * Show form error message
 */
function showFormError(inputElement, message) {
    // Remove any existing error message
    const existingError = inputElement.parentNode.querySelector('.invalid-feedback');
    if (existingError) {
        existingError.remove();
    }
    
    // Add error class to input
    inputElement.classList.add('is-invalid');
    
    // Create and append error message
    const errorDiv = document.createElement('div');
    errorDiv.className = 'invalid-feedback';
    errorDiv.textContent = message;
    inputElement.parentNode.appendChild(errorDiv);
    
    // Focus the input
    inputElement.focus();
}

/**
 * Validate email format
 */
function isValidEmail(email) {
    const re = /^(([^<>()\[\]\\.,;:\s@"]+(\.[^<>()\[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
    return re.test(email.toLowerCase());
}

/**
 * Initialize lazy loading for images
 */
function initLazyLoading() {
    // Check if browser supports Intersection Observer
    if ('IntersectionObserver' in window) {
        const lazyImages = document.querySelectorAll('img[data-src]');
        
        const imageObserver = new IntersectionObserver(function(entries, observer) {
            entries.forEach(function(entry) {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    img.src = img.dataset.src;
                    img.removeAttribute('data-src');
                    imageObserver.unobserve(img);
                }
            });
        });
        
        lazyImages.forEach(function(image) {
            imageObserver.observe(image);
        });
    } else {
        // Fallback for browsers without Intersection Observer support
        // Load all images immediately
        const lazyImages = document.querySelectorAll('img[data-src]');
        lazyImages.forEach(function(img) {
            img.src = img.dataset.src;
            img.removeAttribute('data-src');
        });
    }
}

/**
 * Format currency amount
 * @param {number} amount - The amount to format
 * @param {string} currency - The currency code (default: INR)
 * @returns {string} - Formatted currency string
 */
function formatCurrency(amount, currency = 'INR') {
    const formatter = new Intl.NumberFormat('en-IN', {
        style: 'currency',
        currency: currency,
        minimumFractionDigits: 2
    });
    
    return formatter.format(amount);
}

/**
 * Format date to readable string
 * @param {Date|string} date - The date to format
 * @param {string} format - The format type (short, medium, long)
 * @returns {string} - Formatted date string
 */
function formatDate(date, format = 'medium') {
    if (typeof date === 'string') {
        date = new Date(date);
    }
    
    const options = {
        short: { day: 'numeric', month: 'short' },
        medium: { day: 'numeric', month: 'short', year: 'numeric' },
        long: { weekday: 'long', day: 'numeric', month: 'long', year: 'numeric' }
    };
    
    return date.toLocaleDateString('en-IN', options[format]);
}

/**
 * Format time to readable string
 * @param {Date|string} time - The time to format
 * @param {boolean} includeSeconds - Whether to include seconds
 * @returns {string} - Formatted time string
 */
function formatTime(time, includeSeconds = false) {
    if (typeof time === 'string') {
        // If time is in HH:MM:SS format
        if (time.includes(':')) {
            const parts = time.split(':');
            time = new Date();
            time.setHours(parseInt(parts[0], 10));
            time.setMinutes(parseInt(parts[1], 10));
            if (parts.length > 2) {
                time.setSeconds(parseInt(parts[2], 10));
            }
        } else {
            time = new Date(time);
        }
    }
    
    const options = {
        hour: '2-digit',
        minute: '2-digit',
        hour12: true
    };
    
    if (includeSeconds) {
        options.second = '2-digit';
    }
    
    return time.toLocaleTimeString('en-IN', options);
}

document.addEventListener('DOMContentLoaded', function() {
    const forgotPasswordButton = document.getElementById('forgot-password-btn'); // Assuming your button has this ID

    if (forgotPasswordButton) {
        forgotPasswordButton.addEventListener('click', function(event) {
            event.preventDefault(); // Prevent default form submission if the button is inside a form

            console.log('Forgot password button clicked!');

            // --- Your logic to handle the "Forgot Password" action goes here ---
            // For example:
            // 1. Redirect the user to the "Forgot Password" form page.
            window.location.href = '/forgot_password'; // Assuming you have a route for this

            // OR
            // 2. Show a modal dialog containing the "Forgot Password" form.
            //    (You'd need to have the HTML for the modal in your template
            //     and JavaScript to make it visible)
            //    const forgotPasswordModal = document.getElementById('forgot-password-modal');
            //    if (forgotPasswordModal) {
            //        forgotPasswordModal.style.display = 'block';
            //    }
        });
    } else {
        console.error('Forgot password button element not found! Make sure the ID in your HTML matches.');
    }
});