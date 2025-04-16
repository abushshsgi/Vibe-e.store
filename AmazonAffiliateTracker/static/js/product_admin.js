document.addEventListener('DOMContentLoaded', function() {
    // Product rating visualization
    const ratingSelect = document.getElementById('rating');
    const ratingStars = document.querySelector('.rating-stars');
    
    if (ratingSelect && ratingStars) {
        // Set initial stars
        updateStars(ratingSelect.value);
        
        // Update stars when rating changes
        ratingSelect.addEventListener('change', function() {
            updateStars(this.value);
        });
        
        function updateStars(rating) {
            rating = parseInt(rating, 10);
            let starsHtml = '';
            
            for (let i = 1; i <= 5; i++) {
                if (i <= rating) {
                    starsHtml += '<i class="fas fa-star text-warning"></i>';
                } else {
                    starsHtml += '<i class="far fa-star text-muted"></i>';
                }
            }
            
            ratingStars.innerHTML = starsHtml;
        }
    }
    
    // Image upload preview
    const imageInput = document.getElementById('product_images');
    const imagePreviewContainer = document.querySelector('.image-preview-container');
    
    if (imageInput && imagePreviewContainer) {
        imageInput.addEventListener('change', function() {
            // Clear previous previews
            imagePreviewContainer.innerHTML = '';
            
            if (this.files.length > 0) {
                // Create preview for each selected file
                Array.from(this.files).forEach((file, index) => {
                    const reader = new FileReader();
                    
                    reader.onload = function(e) {
                        const previewDiv = document.createElement('div');
                        previewDiv.className = 'image-preview';
                        
                        const img = document.createElement('img');
                        img.src = e.target.result;
                        img.alt = `Preview ${index + 1}`;
                        
                        previewDiv.appendChild(img);
                        imagePreviewContainer.appendChild(previewDiv);
                    }
                    
                    reader.readAsDataURL(file);
                });
            }
        });
    }
    
    // Handle primary image selection
    const primaryImageBtns = document.querySelectorAll('.set-primary-image');
    if (primaryImageBtns.length > 0) {
        primaryImageBtns.forEach(btn => {
            btn.addEventListener('click', function(e) {
                e.preventDefault();
                const imageId = this.dataset.imageId;
                selectPrimaryImage(imageId);
            });
        });
    }
    
    // Handle image deletion
    const deleteImageBtns = document.querySelectorAll('.delete-image');
    if (deleteImageBtns.length > 0) {
        deleteImageBtns.forEach(btn => {
            btn.addEventListener('click', function(e) {
                e.preventDefault();
                const imageId = this.dataset.imageId;
                markImageForDeletion(imageId);
            });
        });
    }
});

function selectPrimaryImage(imageId) {
    // Set hidden input for primary image
    document.getElementById('primary_image').value = imageId;
    
    // Update visual indicators
    document.querySelectorAll('.product-image-card').forEach(card => {
        card.classList.remove('is-primary');
    });
    
    document.querySelector(`.product-image-card[data-image-id="${imageId}"]`).classList.add('is-primary');
    
    // Update badges
    document.querySelectorAll('.primary-badge').forEach(badge => {
        badge.style.display = 'none';
    });
    
    document.querySelector(`.primary-badge[data-image-id="${imageId}"]`).style.display = 'block';
}

function markImageForDeletion(imageId) {
    const imageCard = document.querySelector(`.product-image-card[data-image-id="${imageId}"]`);
    const deleteCheckbox = document.querySelector(`#delete_image_${imageId}`);
    
    if (imageCard.classList.contains('marked-for-deletion')) {
        // Undo deletion
        imageCard.classList.remove('marked-for-deletion');
        deleteCheckbox.checked = false;
    } else {
        // Mark for deletion
        imageCard.classList.add('marked-for-deletion');
        deleteCheckbox.checked = true;
    }
}