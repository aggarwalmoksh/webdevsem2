/**
 * Payment Page JavaScript
 * Handles payment form validation and submission for District Events
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize payment form
    initPaymentForm();
    
    // Initialize Razorpay if it exists
    if (window.Razorpay) {
        initRazorpay();
    }
    
    // Set up tabs
    setupPaymentTabs();
    
    // Set up test mode for development
    setupTestMode();
});

/**
 * Initialize the payment form
 */
function initPaymentForm() {
    // Card Payment Form
    const cardForm = document.getElementById('cardPaymentForm');
    if (cardForm) {
        // Card Number Formatting
        const cardNumberInput = document.getElementById('cardNumber');
        if (cardNumberInput) {
            cardNumberInput.addEventListener('input', function(e) {
                let value = this.value.replace(/\D/g, '');
                let formattedValue = '';
                
                for (let i = 0; i < value.length; i++) {
                    if (i > 0 && i % 4 === 0) {
                        formattedValue += ' ';
                    }
                    formattedValue += value[i];
                }
                
                // Limit to 16 digits (with spaces)
                if (value.length > 16) {
                    formattedValue = formattedValue.substring(0, 19);
                }
                
                this.value = formattedValue;
            });
        }
        
        // Expiry Date Formatting
        const expiryInput = document.getElementById('expiryDate');
        if (expiryInput) {
            expiryInput.addEventListener('input', function(e) {
                let value = this.value.replace(/\D/g, '');
                
                if (value.length > 0) {
                    // Format MM/YY
                    const month = value.substring(0, 2);
                    const year = value.substring(2, 4);
                    
                    if (value.length > 2) {
                        this.value = `${month}/${year}`;
                    } else {
                        this.value = month;
                    }
                }
            });
        }
        
        // CVV Validation
        const cvvInput = document.getElementById('cvv');
        if (cvvInput) {
            cvvInput.addEventListener('input', function(e) {
                let value = this.value.replace(/\D/g, '');
                
                // Limit to 4 digits (AMEX has 4 digit CVV)
                if (value.length > 4) {
                    value = value.substring(0, 4);
                }
                
                this.value = value;
            });
        }
        
        // Card Payment Button
        const payCardButton = document.getElementById('payCardButton');
        if (payCardButton) {
            payCardButton.addEventListener('click', function() {
                // Validate card form
                if (validateCardForm()) {
                    // Show processing state
                    this.disabled = true;
                    this.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i> Processing...';
                    
                    // Simulate payment processing (would be handled by Razorpay in production)
                    simulateCardPayment();
                }
            });
        }
    }
    
    // UPI Payment Form
    const upiPayButton = document.getElementById('payUpiButton');
    if (upiPayButton) {
        upiPayButton.addEventListener('click', function() {
            const upiId = document.getElementById('upiId');
            
            if (upiId && upiId.value.trim() !== '') {
                // Show processing state
                this.disabled = true;
                this.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i> Processing...';
                
                // Simulate UPI payment processing
                simulateUpiPayment();
            } else {
                showError('Please enter a valid UPI ID.');
            }
        });
    }
    
    // Verify UPI button
    const verifyUpiButton = document.getElementById('verifyUpi');
    if (verifyUpiButton) {
        verifyUpiButton.addEventListener('click', function() {
            const upiId = document.getElementById('upiId');
            
            if (upiId && upiId.value.trim() !== '') {
                // Show verifying state
                this.disabled = true;
                this.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i> Verifying...';
                
                // Simulate UPI verification
                setTimeout(() => {
                    this.disabled = false;
                    this.innerHTML = 'Verified <i class="fas fa-check-circle text-success ms-1"></i>';
                    this.classList.remove('btn-primary');
                    this.classList.add('btn-success');
                }, 1500);
            } else {
                showError('Please enter a valid UPI ID.');
            }
        });
    }
    
    // Net Banking Payment
    const netBankingPayButton = document.getElementById('payNetbankingButton');
    if (netBankingPayButton) {
        netBankingPayButton.addEventListener('click', function() {
            const bankSelect = document.getElementById('bankSelect');
            
            if (bankSelect && bankSelect.value) {
                // Show processing state
                this.disabled = true;
                this.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i> Redirecting to bank...';
                
                // Simulate net banking redirection
                simulateNetBankingPayment();
            } else {
                showError('Please select a bank.');
            }
        });
    }
    
    // Wallet Payment
    const walletPayButton = document.getElementById('payWalletButton');
    if (walletPayButton) {
        walletPayButton.addEventListener('click', function() {
            const selectedWallet = document.querySelector('input[name="wallet"]:checked');
            
            if (selectedWallet) {
                // Show processing state
                this.disabled = true;
                this.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i> Redirecting to wallet...';
                
                // Simulate wallet payment redirection
                simulateWalletPayment(selectedWallet.value);
            } else {
                showError('Please select a wallet.');
            }
        });
    }
}

/**
 * Set up payment tabs
 */
function setupPaymentTabs() {
    const tabButtons = document.querySelectorAll('.nav-link[data-bs-toggle="tab"]');
    
    tabButtons.forEach(button => {
        button.addEventListener('click', function() {
            // Reset any error messages when switching tabs
            const errorElement = document.querySelector('.alert-danger');
            if (errorElement) {
                errorElement.remove();
            }
        });
    });
}

/**
 * Initialize Razorpay checkout
 */
function initRazorpay() {
    // This would be the integration with Razorpay
    // In a real app, the Razorpay checkout would be initialized here
    // But for our case, we're using a simulated payment flow
}

/**
 * Set up test mode for development
 */
function setupTestMode() {
    const testPaymentForm = document.getElementById('testPaymentForm');
    
    if (testPaymentForm) {
        testPaymentForm.addEventListener('submit', function(e) {
            // The form submission is handled by the server
            // No additional JS required for the test mode
            
            // Just add a visual feedback
            const submitButton = this.querySelector('button[type="submit"]');
            submitButton.disabled = true;
            submitButton.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i> Processing...';
        });
    }
}

/**
 * Validate card payment form
 * @returns {boolean} - True if form is valid, false otherwise
 */
function validateCardForm() {
    const cardNumber = document.getElementById('cardNumber');
    const expiryDate = document.getElementById('expiryDate');
    const cvv = document.getElementById('cvv');
    const nameOnCard = document.getElementById('nameOnCard');
    
    let isValid = true;
    
    // Clear previous errors
    const errorElement = document.querySelector('.alert-danger');
    if (errorElement) {
        errorElement.remove();
    }
    
    // Card Number Validation
    if (!cardNumber || cardNumber.value.replace(/\s/g, '').length < 16) {
        showError('Please enter a valid card number.');
        isValid = false;
    }
    
    // Expiry Date Validation
    if (!expiryDate || expiryDate.value.length < 5) {
        showError('Please enter a valid expiry date (MM/YY).');
        isValid = false;
    } else {
        // Check if card is expired
        const parts = expiryDate.value.split('/');
        if (parts.length === 2) {
            const month = parseInt(parts[0], 10);
            const year = parseInt('20' + parts[1], 10);
            const now = new Date();
            const currentMonth = now.getMonth() + 1;
            const currentYear = now.getFullYear();
            
            if (year < currentYear || (year === currentYear && month < currentMonth)) {
                showError('Your card has expired.');
                isValid = false;
            }
        }
    }
    
    // CVV Validation
    if (!cvv || cvv.value.length < 3) {
        showError('Please enter a valid CVV code.');
        isValid = false;
    }
    
    // Name Validation
    if (!nameOnCard || nameOnCard.value.trim() === '') {
        showError('Please enter the name on card.');
        isValid = false;
    }
    
    return isValid;
}

/**
 * Show error message
 * @param {string} message - The error message to display
 */
function showError(message) {
    // Create error alert
    const errorDiv = document.createElement('div');
    errorDiv.className = 'alert alert-danger alert-dismissible fade show mt-3';
    errorDiv.role = 'alert';
    errorDiv.innerHTML = `
        <i class="fas fa-exclamation-circle me-2"></i> ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    
    // Find where to insert the error
    const activeTab = document.querySelector('.tab-pane.active');
    
    if (activeTab) {
        // Insert at the top of the active tab
        activeTab.insertBefore(errorDiv, activeTab.firstChild);
    } else {
        // Insert at the top of the card body
        const cardBody = document.querySelector('.card-body');
        cardBody.insertBefore(errorDiv, cardBody.firstChild);
    }
    
    // Auto dismiss after 5 seconds
    setTimeout(() => {
        if (errorDiv.parentNode) {
            errorDiv.remove();
        }
    }, 5000);
}

/**
 * Simulate card payment processing
 */
function simulateCardPayment() {
    // In a real app, this would call the payment gateway API
    
    // For this simulation, we'll redirect to the success page after a delay
    setTimeout(() => {
        document.getElementById('razorpayForm').submit();
    }, 2000);
}

/**
 * Simulate UPI payment processing
 */
function simulateUpiPayment() {
    // In a real app, this would initiate the UPI payment flow
    
    // For this simulation, we'll redirect to the success page after a delay
    setTimeout(() => {
        document.getElementById('razorpayForm').submit();
    }, 2000);
}

/**
 * Simulate net banking payment processing
 */
function simulateNetBankingPayment() {
    // In a real app, this would redirect to the bank's page
    
    // For this simulation, we'll redirect to the success page after a delay
    setTimeout(() => {
        document.getElementById('razorpayForm').submit();
    }, 2000);
}

/**
 * Simulate wallet payment processing
 * @param {string} walletType - The selected wallet type
 */
function simulateWalletPayment(walletType) {
    // In a real app, this would redirect to the wallet provider
    
    // For this simulation, we'll redirect to the success page after a delay
    setTimeout(() => {
        document.getElementById('razorpayForm').submit();
    }, 2000);
}
