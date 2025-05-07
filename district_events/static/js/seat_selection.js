/**
 * Seat Selection JavaScript
 * Handles seat selection and booking summary for District Events
 */

document.addEventListener('DOMContentLoaded', function() {
    // Check if we're on the seat selection page
    const isIndoorEvent = document.querySelector('.seating-map');
    const isOutdoorEvent = document.querySelector('.zone-selection');
    
    if (isIndoorEvent) {
        initTheaterSeating();
    } else if (isOutdoorEvent) {
        initZoneSelection();
    }
});

/**
 * Initialize Theater Style Seating
 */
function initTheaterSeating() {
    // Elements
    const seats = document.querySelectorAll('.seat:not(.booked)');
    const selectedSeatId = document.getElementById('selectedSeatId');
    const selectedSeatLabel = document.getElementById('selectedSeatLabel');
    const selectedSeatCategory = document.getElementById('selectedSeatCategory');
    const selectedSeatPrice = document.getElementById('selectedSeatPrice');
    const totalPrice = document.getElementById('totalPrice');
    const selectedSeatDetails = document.getElementById('selectedSeatDetails');
    const emptySelection = document.querySelector('.empty-selection');
    const proceedButton = document.getElementById('proceedToPaymentBtn');
    
    // Handle seat click
    seats.forEach(seat => {
        seat.addEventListener('click', function() {
            // Update UI by removing selected class from all seats
            seats.forEach(s => s.classList.remove('selected'));
            
            // Add selected class to clicked seat
            this.classList.add('selected');
            
            // Get seat details
            const seatId = this.dataset.seatId;
            const row = this.dataset.row;
            const number = this.dataset.number;
            const price = parseFloat(this.dataset.price);
            const category = this.dataset.category;
            
            // Update form fields
            selectedSeatId.value = seatId;
            
            // Update seat details in summary
            selectedSeatLabel.textContent = `${row}${number}`;
            selectedSeatCategory.textContent = category;
            selectedSeatPrice.textContent = `₹${price.toFixed(2)}`;
            totalPrice.textContent = `₹${price.toFixed(2)}`;
            
            // Show seat details and hide empty state
            selectedSeatDetails.classList.remove('d-none');
            if (emptySelection) {
                emptySelection.classList.add('d-none');
            }
            
            // Enable proceed button
            proceedButton.disabled = false;
        });
    });
}

/**
 * Initialize Zone Selection
 */
function initZoneSelection() {
    // Elements
    const zoneCards = document.querySelectorAll('.zone-card:not(.zone-sold-out)');
    const selectedZoneId = document.getElementById('selectedZoneId');
    const selectedQuantity = document.getElementById('selectedQuantity');
    const selectedZoneName = document.getElementById('selectedZoneName');
    const selectedZonePrice = document.getElementById('selectedZonePrice');
    const selectedZoneQuantity = document.getElementById('selectedZoneQuantity');
    const zoneTotalPrice = document.getElementById('zoneTotalPrice');
    const selectedZoneDetails = document.getElementById('selectedZoneDetails');
    const emptySelection = document.querySelector('.empty-selection');
    const proceedButton = document.getElementById('proceedToPaymentBtn');
    
    // Handle quantity controls
    const quantityInputs = document.querySelectorAll('.quantity-input');
    const decreaseButtons = document.querySelectorAll('.quantity-decrease');
    const increaseButtons = document.querySelectorAll('.quantity-increase');
    
    // Set up quantity decrease buttons
    decreaseButtons.forEach(button => {
        button.addEventListener('click', function() {
            const input = this.parentNode.querySelector('.quantity-input');
            const currentValue = parseInt(input.value);
            if (currentValue > 1) {
                input.value = currentValue - 1;
            }
        });
    });
    
    // Set up quantity increase buttons
    increaseButtons.forEach(button => {
        button.addEventListener('click', function() {
            const input = this.parentNode.querySelector('.quantity-input');
            const zoneCard = this.closest('.zone-card');
            const maxAvailable = parseInt(zoneCard.dataset.available);
            const currentValue = parseInt(input.value);
            
            if (currentValue < maxAvailable) {
                input.value = currentValue + 1;
            }
        });
    });
    
    // Prevent manual entry of invalid quantities
    quantityInputs.forEach(input => {
        input.addEventListener('change', function() {
            const zoneCard = this.closest('.zone-card');
            const maxAvailable = parseInt(zoneCard.dataset.available);
            let value = parseInt(this.value);
            
            if (isNaN(value) || value < 1) {
                value = 1;
            } else if (value > maxAvailable) {
                value = maxAvailable;
            }
            
            this.value = value;
        });
    });
    
    // Handle zone selection buttons
    const selectZoneButtons = document.querySelectorAll('.select-zone');
    selectZoneButtons.forEach(button => {
        button.addEventListener('click', function() {
            // Remove selected class from all zone cards
            zoneCards.forEach(card => card.classList.remove('selected'));
            
            // Add selected class to this zone card
            const zoneCard = this.closest('.zone-card');
            zoneCard.classList.add('selected');
            
            // Get zone details
            const zoneId = zoneCard.dataset.zoneId;
            const zoneName = zoneCard.dataset.name;
            const zonePrice = parseFloat(zoneCard.dataset.price);
            const quantityInput = zoneCard.querySelector('.quantity-input');
            const quantity = parseInt(quantityInput.value);
            
            // Update form fields
            selectedZoneId.value = zoneId;
            selectedQuantity.value = quantity;
            
            // Update zone details in summary
            selectedZoneName.textContent = zoneName;
            selectedZonePrice.textContent = `₹${zonePrice.toFixed(2)}`;
            selectedZoneQuantity.textContent = quantity;
            zoneTotalPrice.textContent = `₹${(zonePrice * quantity).toFixed(2)}`;
            
            // Show zone details and hide empty state
            selectedZoneDetails.classList.remove('d-none');
            if (emptySelection) {
                emptySelection.classList.add('d-none');
            }
            
            // Enable proceed button
            proceedButton.disabled = false;
        });
    });
    
    // Update total when quantity changes
    quantityInputs.forEach(input => {
        input.addEventListener('change', function() {
            const zoneCard = this.closest('.zone-card');
            
            // If this zone is selected, update the summary
            if (zoneCard.classList.contains('selected')) {
                const zonePrice = parseFloat(zoneCard.dataset.price);
                const quantity = parseInt(this.value);
                
                // Update form field
                selectedQuantity.value = quantity;
                
                // Update summary
                selectedZoneQuantity.textContent = quantity;
                zoneTotalPrice.textContent = `₹${(zonePrice * quantity).toFixed(2)}`;
            }
        });
    });
}

/**
 * Format currency amount
 * @param {number} amount - The amount to format
 * @returns {string} - Formatted currency string
 */
function formatCurrency(amount) {
    return '₹' + amount.toFixed(2);
}
