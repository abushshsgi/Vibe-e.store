// Main JavaScript file for Amazon Affiliate Marketplace

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Product image thumbnails
    initProductThumbnails();
    
    // Wishlist functionality
    initWishlistButtons();
    
    // Product clicks tracking
    initProductClickTracking();
    
    // Theme toggle in navigation
    initThemeToggle();
});

// Product image thumbnail gallery
function initProductThumbnails() {
    const thumbnails = document.querySelectorAll('.product-thumbnail');
    const mainImage = document.querySelector('.product-detail-image');
    
    if (!thumbnails.length || !mainImage) return;
    
    thumbnails.forEach(thumbnail => {
        thumbnail.addEventListener('click', function() {
            // Update active class
            thumbnails.forEach(t => t.classList.remove('active'));
            this.classList.add('active');
            
            // Update main image
            mainImage.src = this.getAttribute('data-full-img');
            mainImage.alt = this.alt;
        });
    });
}

// Wishlist functionality
function initWishlistButtons() {
    const wishlistButtons = document.querySelectorAll('.wishlist-btn');
    
    wishlistButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const productId = this.getAttribute('data-product-id');
            const isActive = this.classList.contains('active');
            
            if (isActive) {
                // Remove from wishlist
                removeFromWishlist(productId, this);
            } else {
                // Add to wishlist
                addToWishlist(productId, this);
            }
        });
    });
}

function addToWishlist(productId, button) {
    fetch(`/wishlist/add/${productId}`, {
        method: 'POST',
        headers: {
            'X-Requested-With': 'XMLHttpRequest',
            'Content-Type': 'application/json',
            'X-CSRFToken': getCsrfToken()
        },
        credentials: 'same-origin'
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            button.classList.add('active');
            showToast(data.message);
        } else {
            showToast(data.message);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showToast('An error occurred. Please try again.');
    });
}

function removeFromWishlist(productId, button) {
    fetch(`/wishlist/remove/${productId}`, {
        method: 'POST',
        headers: {
            'X-Requested-With': 'XMLHttpRequest',
            'Content-Type': 'application/json',
            'X-CSRFToken': getCsrfToken()
        },
        credentials: 'same-origin'
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            button.classList.remove('active');
            showToast(data.message);
            
            // If on wishlist page, remove the item from DOM
            if (window.location.pathname.includes('/wishlist')) {
                const itemElement = button.closest('.wishlist-item');
                if (itemElement) {
                    itemElement.remove();
                    
                    // Check if wishlist is empty
                    const remainingItems = document.querySelectorAll('.wishlist-item');
                    if (remainingItems.length === 0) {
                        const wishlistContainer = document.querySelector('.wishlist-container');
                        wishlistContainer.innerHTML = `
                            <div class="empty-state">
                                <i class="fas fa-heart-broken"></i>
                                <h3>Your wishlist is empty</h3>
                                <p>Browse our products and add items to your wishlist.</p>
                                <a href="/" class="btn btn-primary">Browse Products</a>
                            </div>
                        `;
                    }
                }
            }
        } else {
            showToast(data.message);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showToast('An error occurred. Please try again.');
    });
}

// Track product clicks
function initProductClickTracking() {
    const affiliateLinks = document.querySelectorAll('.product-affiliate-link');
    
    affiliateLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const productId = this.getAttribute('data-product-id');
            
            fetch(`/track/click/${productId}`)
                .then(response => response.json())
                .then(data => {
                    if (data.success && data.redirect) {
                        window.open(data.redirect, '_blank');
                    }
                })
                .catch(error => {
                    console.error('Error tracking click:', error);
                    window.open(this.href, '_blank');
                });
        });
    });
}

// Theme toggle functionality
function initThemeToggle() {
    const themeToggle = document.getElementById('themeToggle');
    if (!themeToggle) return;
    
    themeToggle.addEventListener('click', function() {
        const currentTheme = document.body.getAttribute('data-theme') || 'light';
        const newTheme = currentTheme === 'light' ? 'dark' : 'light';
        
        // Update theme icon
        if (newTheme === 'dark') {
            this.innerHTML = '<i class="fas fa-sun"></i>';
            this.setAttribute('title', 'Switch to light theme');
        } else {
            this.innerHTML = '<i class="fas fa-moon"></i>';
            this.setAttribute('title', 'Switch to dark theme');
        }
        
        // Redirect to theme change endpoint
        window.location.href = `/theme/${newTheme}?next=${window.location.pathname}`;
    });
}

// Utility: Get CSRF token from meta tag
function getCsrfToken() {
    return document.querySelector('meta[name="csrf-token"]').getAttribute('content');
}

// Utility: Show toast notification
function showToast(message) {
    // Check if toast container exists, create if not
    let toastContainer = document.querySelector('.toast-container');
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.className = 'toast-container position-fixed bottom-0 end-0 p-3';
        document.body.appendChild(toastContainer);
    }
    
    // Create toast element
    const toastId = 'toast-' + Date.now();
    const toastHtml = `
        <div id="${toastId}" class="toast" role="alert" aria-live="assertive" aria-atomic="true">
            <div class="toast-header">
                <strong class="me-auto">Notification</strong>
                <button type="button" class="btn-close" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
            <div class="toast-body">
                ${message}
            </div>
        </div>
    `;
    
    toastContainer.insertAdjacentHTML('beforeend', toastHtml);
    
    // Initialize and show toast
    const toastElement = document.getElementById(toastId);
    const toast = new bootstrap.Toast(toastElement, { autohide: true, delay: 3000 });
    toast.show();
    
    // Remove toast from DOM after it's hidden
    toastElement.addEventListener('hidden.bs.toast', function() {
        this.remove();
    });
}
