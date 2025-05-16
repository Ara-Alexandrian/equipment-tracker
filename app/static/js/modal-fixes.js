/**
 * Modal fixes for GearVue application
 * Addresses issues with modals not properly closing and backdrop remaining visible
 */

document.addEventListener('DOMContentLoaded', function() {
    // Fix any modal backdrop issues across the site
    const fixBackdropIssues = function() {
        // Fix for lingering backdrops when modal is closed
        const closeModals = function() {
            // Find all modals
            const modals = document.querySelectorAll('.modal');
            
            // Add proper event listeners to each modal
            modals.forEach(modal => {
                // When the modal is hidden, remove any lingering backdrops
                modal.addEventListener('hidden.bs.modal', function() {
                    // Remove any lingering backdrops (they should have class modal-backdrop)
                    const backdrops = document.querySelectorAll('.modal-backdrop');
                    backdrops.forEach(backdrop => {
                        backdrop.remove();
                    });
                    
                    // Fix body classes when the modal is hidden
                    document.body.classList.remove('modal-open');
                    document.body.style.overflow = '';
                    document.body.style.paddingRight = '';
                });

                // If modal is closed via ESC key or clicking outside
                modal.addEventListener('click', function(event) {
                    if (event.target === modal) {
                        // Force modal to close properly
                        const bsModal = bootstrap.Modal.getInstance(modal);
                        if (bsModal) {
                            bsModal.hide();
                        }
                    }
                });
            });
            
            // Fix for any ESC key handling
            document.addEventListener('keydown', function(event) {
                if (event.key === 'Escape') {
                    // Check if any modal is open
                    const openModals = document.querySelectorAll('.modal.show');
                    openModals.forEach(openModal => {
                        const bsModal = bootstrap.Modal.getInstance(openModal);
                        if (bsModal) {
                            bsModal.hide();
                        }
                    });
                    
                    // Clean up any backdrops just in case
                    document.querySelectorAll('.modal-backdrop').forEach(backdrop => {
                        backdrop.remove();
                    });
                    
                    // Fix body
                    document.body.classList.remove('modal-open');
                    document.body.style.overflow = '';
                    document.body.style.paddingRight = '';
                }
            });
        };
        
        // Run backdrop fixes once DOM is loaded
        closeModals();
        
        // Also run them after a slight delay to catch any dynamically added modals
        setTimeout(closeModals, 500);
    };
    
    // Initial fix
    fixBackdropIssues();
    
    // Fix for QR code modal specifically
    const qrModal = document.getElementById('qrCodeModal');
    if (qrModal) {
        qrModal.addEventListener('hidden.bs.modal', function() {
            // Force clean up backdrop and body classes
            const backdrops = document.querySelectorAll('.modal-backdrop');
            backdrops.forEach(backdrop => {
                backdrop.remove();
            });
            
            document.body.classList.remove('modal-open');
            document.body.style.overflow = '';
            document.body.style.paddingRight = '';
            
            // Clean up QR code state
            const qrCodeDisplay = document.getElementById('qrCodeDisplay');
            const qrCodeError = document.getElementById('qrCodeError');
            const qrCodeLoading = document.getElementById('qrCodeLoading');
            
            // Reset modal state for next use
            if (qrCodeDisplay) qrCodeDisplay.style.display = 'none';
            if (qrCodeError) qrCodeError.style.display = 'none';
            if (qrCodeLoading) qrCodeLoading.style.display = 'block';
        });
        
        // Override the close button to ensure proper closing
        const closeButton = qrModal.querySelector('.btn-close, .btn-secondary');
        if (closeButton) {
            closeButton.addEventListener('click', function() {
                const bsModal = bootstrap.Modal.getInstance(qrModal);
                if (bsModal) {
                    bsModal.hide();
                }
                
                // Manual cleanup
                setTimeout(function() {
                    const backdrops = document.querySelectorAll('.modal-backdrop');
                    backdrops.forEach(backdrop => {
                        backdrop.remove();
                    });
                    
                    document.body.classList.remove('modal-open');
                    document.body.style.overflow = '';
                    document.body.style.paddingRight = '';
                }, 300);
            });
        }
    }
    
    // Check for dynamically added modals
    const observeDocument = function() {
        // Create an observer instance
        const observer = new MutationObserver(function(mutations) {
            let shouldReapplyFixes = false;
            
            mutations.forEach(function(mutation) {
                if (mutation.addedNodes.length) {
                    // Check if any added nodes are modals or contain modals
                    for (let i = 0; i < mutation.addedNodes.length; i++) {
                        const node = mutation.addedNodes[i];
                        if (node.nodeType === 1) { // Element node
                            if (node.classList && node.classList.contains('modal')) {
                                shouldReapplyFixes = true;
                                break;
                            } else if (node.querySelector && node.querySelector('.modal')) {
                                shouldReapplyFixes = true;
                                break;
                            }
                        }
                    }
                }
            });
            
            // Reapply fixes if needed
            if (shouldReapplyFixes) {
                fixBackdropIssues();
            }
        });
        
        // Observe the document body for added nodes
        observer.observe(document.body, { childList: true, subtree: true });
    };
    
    // Start observing for dynamically added modals
    observeDocument();
});