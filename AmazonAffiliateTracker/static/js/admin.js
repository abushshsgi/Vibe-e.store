// Admin JavaScript file

document.addEventListener('DOMContentLoaded', function() {
    // Initialize mobile sidebar toggle
    initSidebar();
    
    // Initialize image upload preview
    initImageUploadPreview();
    
    // Initialize product image management
    initProductImageManagement();
    
    // Initialize chart data loading
    initChartDataLoading();
    
    // Initialize real-time data updates
    initRealTimeUpdates();
});

// Mobile sidebar toggle
function initSidebar() {
    const sidebarToggle = document.querySelector('.admin-sidebar-toggle');
    const sidebar = document.querySelector('.admin-sidebar');
    const main = document.querySelector('.admin-main');
    
    if (sidebarToggle && sidebar && main) {
        sidebarToggle.addEventListener('click', function() {
            sidebar.classList.toggle('admin-sidebar-shown');
        });
        
        // Close sidebar when clicking outside on mobile
        document.addEventListener('click', function(event) {
            const isClickInside = sidebar.contains(event.target) || sidebarToggle.contains(event.target);
            
            if (!isClickInside && sidebar.classList.contains('admin-sidebar-shown')) {
                sidebar.classList.remove('admin-sidebar-shown');
            }
        });
    }
}

// Image upload preview
function initImageUploadPreview() {
    const fileInputs = document.querySelectorAll('input[type="file"]');
    
    fileInputs.forEach(input => {
        const previewContainer = document.querySelector(`#${input.id}Preview`);
        if (!previewContainer) return;
        
        input.addEventListener('change', function() {
            if (this.files && this.files[0]) {
                const reader = new FileReader();
                
                reader.onload = function(e) {
                    previewContainer.innerHTML = `<img src="${e.target.result}" class="img-fluid">`;
                };
                
                reader.readAsDataURL(this.files[0]);
            }
        });
    });
}

// Product image management
function initProductImageManagement() {
    // Set primary image
    window.selectPrimaryImage = function(imageId) {
        document.getElementById('primary_image').value = imageId;
        
        // Update UI
        document.querySelectorAll('.product-image-item').forEach(item => {
            item.classList.remove('is-primary');
        });
        
        const imageItem = document.querySelector(`.product-image-item button[onclick*="${imageId}"]`).closest('.product-image-item');
        if (imageItem) {
            imageItem.classList.add('is-primary');
        }
        
        // Update star icons
        document.querySelectorAll('.product-image-item button[title="Set as primary"] i').forEach(icon => {
            icon.classList.remove('text-warning');
        });
        
        const starIcon = document.querySelector(`.product-image-item button[onclick*="${imageId}"] i`);
        if (starIcon) {
            starIcon.classList.add('text-warning');
        }
    };
    
    // Mark image for deletion
    window.markImageForDeletion = function(imageId) {
        const container = document.getElementById('delete_images_container');
        
        // Check if image is already marked for deletion
        const existingInput = document.querySelector(`input[name="delete_image"][value="${imageId}"]`);
        
        if (existingInput) {
            // Unmark for deletion
            existingInput.remove();
            
            // Update UI
            const imageItem = document.querySelector(`.product-image-item button[onclick*="${imageId}"]`).closest('.product-image-item');
            if (imageItem) {
                imageItem.style.opacity = '1';
                imageItem.style.border = '1px solid var(--admin-border-color)';
            }
        } else {
            // Mark for deletion
            const input = document.createElement('input');
            input.type = 'hidden';
            input.name = 'delete_image';
            input.value = imageId;
            container.appendChild(input);
            
            // Update UI
            const imageItem = document.querySelector(`.product-image-item button[onclick*="${imageId}"]`).closest('.product-image-item');
            if (imageItem) {
                imageItem.style.opacity = '0.5';
                imageItem.style.border = '1px solid var(--danger)';
            }
        }
    };
}

// Chart data loading
function initChartDataLoading() {
    // Time range selectors for charts
    const timeRangeSelectors = document.querySelectorAll('.time-range-selector');
    if (timeRangeSelectors.length) {
        timeRangeSelectors.forEach(selector => {
            selector.addEventListener('click', function() {
                // Update active button
                timeRangeSelectors.forEach(btn => btn.classList.remove('active'));
                this.classList.add('active');
                
                // Reload chart data
                const days = this.getAttribute('data-days');
                loadChartData(days);
            });
        });
    }
}

// Load chart data
function loadChartData(days = 7) {
    // Daily views chart
    fetch(`/admin/api/stats/daily_views?days=${days}`)
        .then(response => response.json())
        .then(data => {
            updateDailyViewsChart(data.labels, data.data);
        })
        .catch(error => console.error('Error loading daily views data:', error));
    
    // Only load other charts on initial page load (days=7)
    if (days == 7) {
        // Product views chart
        fetch('/admin/api/stats/product_views')
            .then(response => response.json())
            .then(data => {
                updateProductViewsChart(data.labels, data.data);
            })
            .catch(error => console.error('Error loading product views data:', error));
        
        // Product clicks chart
        fetch('/admin/api/stats/product_clicks')
            .then(response => response.json())
            .then(data => {
                updateProductClicksChart(data.labels, data.data);
            })
            .catch(error => console.error('Error loading product clicks data:', error));
        
        // Conversion rate data
        loadConversionRateData();
    }
}

// Load conversion rate data
function loadConversionRateData() {
    fetch('/admin/api/stats/conversion_rate')
        .then(response => response.json())
        .then(data => {
            // Update overall rate
            document.getElementById('overallConversionRate').textContent = `${data.overall_rate}%`;
            
            // Update table
            const tableBody = document.getElementById('conversionRateTableBody');
            if (tableBody) {
                let tableHtml = '';
                
                if (data.products.length === 0) {
                    tableHtml = `<tr><td colspan="4" class="text-center">No data available</td></tr>`;
                } else {
                    data.products.forEach(product => {
                        tableHtml += `
                            <tr>
                                <td>${truncateText(product.product, 30)}</td>
                                <td class="text-center">${product.views}</td>
                                <td class="text-center">${product.clicks}</td>
                                <td class="text-end">
                                    <span class="badge bg-${getConversionRateColor(product.rate)}">${product.rate}%</span>
                                </td>
                            </tr>
                        `;
                    });
                }
                
                tableBody.innerHTML = tableHtml;
            }
        })
        .catch(error => console.error('Error loading conversion rate data:', error));
}

// Get color based on conversion rate
function getConversionRateColor(rate) {
    if (rate >= 10) return 'success';
    if (rate >= 5) return 'info';
    if (rate >= 2) return 'warning';
    return 'danger';
}

// Real-time updates
function initRealTimeUpdates() {
    // Simulate real-time updates for demo purposes
    // In a real project, this would use WebSockets or server-sent events
    setInterval(function() {
        const realtimeList = document.getElementById('realtimeViewsList');
        if (!realtimeList) return;
        
        // Get current time
        const now = new Date();
        const time = now.toTimeString().split(' ')[0];
        
        // In a real app, this would come from the server
        // This is just for demonstration
    }, 10000); // Check for updates every 10 seconds
}

// Utility: Truncate text
function truncateText(text, maxLength) {
    if (!text) return '';
    return text.length > maxLength ? text.substring(0, maxLength) + '...' : text;
}
