/**
 * QR Code Generation Fixes
 * 
 * This script improves QR code generation reliability and handles error cases better.
 */

// Enhanced version of generateQRCodeForEquipment with better error handling and retry logic
function generateQRCodeWithRetry(equipmentId, manufacturer, model, serialNumber) {
    console.log("Enhanced QR code generation called for:", { equipmentId, manufacturer, model, serialNumber });
    
    // Show the QR code modal
    const qrModalElement = document.getElementById('qrCodeModal');
    if (!qrModalElement) {
        console.error('QR Modal not found on page');
        alert('QR Code viewer is not available on this page. Please try again from the equipment detail page.');
        return;
    }
    
    // Get the modal instance or create it
    let qrModal;
    try {
        if (bootstrap && bootstrap.Modal) {
            qrModal = bootstrap.Modal.getInstance(qrModalElement) || new bootstrap.Modal(qrModalElement);
            qrModal.show();
        } else {
            console.warn('Bootstrap not available, using basic modal display');
            qrModalElement.style.display = 'block';
            qrModalElement.classList.add('show');
            document.body.classList.add('modal-open');
            
            // Add backdrop
            const backdrop = document.createElement('div');
            backdrop.className = 'modal-backdrop fade show';
            document.body.appendChild(backdrop);
        }
    } catch (e) {
        console.error('Error showing modal:', e);
        alert('Error showing QR modal: ' + e.message);
        return;
    }
    
    // Show loading state
    const loadingElem = document.getElementById('qrCodeLoading');
    const errorElem = document.getElementById('qrCodeError');
    const displayElem = document.getElementById('qrCodeDisplay');
    const downloadBtn = document.getElementById('qrCodeDownloadBtn');
    const printBtn = document.getElementById('qrCodePrintBtn');
    
    if (loadingElem) loadingElem.style.display = 'block';
    if (errorElem) errorElem.style.display = 'none';
    if (displayElem) displayElem.style.display = 'none';
    if (downloadBtn) downloadBtn.style.display = 'none';
    if (printBtn) printBtn.style.display = 'none';
    
    // Validate equipment ID
    if (!equipmentId) {
        if (loadingElem) loadingElem.style.display = 'none';
        if (errorElem) {
            errorElem.textContent = "Missing equipment ID";
            errorElem.style.display = 'block';
        }
        return;
    }
    
    // Construct the URL for the QR code
    const baseUrl = window.location.origin;
    const qrUrl = `${baseUrl}/qr/equipment/${equipmentId}`;
    
    // Prepare request data
    const requestData = {
        url: qrUrl,
        equipment_id: equipmentId,
        manufacturer: manufacturer || '',
        model: model || '',
        serial: serialNumber || '',
        force_regenerate: true  // Force regeneration to ensure we get a fresh QR code
    };
    
    console.log('Sending QR code request:', requestData);
    
    // Function to handle network errors with a retry
    let retryCount = 0;
    const maxRetries = 2;
    
    function makeRequest() {
        // Add a timestamp to avoid caching
        const timestamp = new Date().getTime();
        const requestUrl = `/admin/equipment/generate-qr?_=${timestamp}`;
        
        fetch(requestUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Cache-Control': 'no-cache, no-store, must-revalidate',
                'Pragma': 'no-cache',
                'Expires': '0'
            },
            body: JSON.stringify(requestData),
        })
        .then(response => {
            console.log('QR code response status:', response.status);
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            console.log('QR code response data:', data);
            
            // Hide loading
            if (loadingElem) loadingElem.style.display = 'none';
            
            if (data.status === 'success') {
                // Add cache busting parameter to the QR code URL
                let qrCodeUrl = data.qr_code_url;
                if (qrCodeUrl.indexOf('?') === -1) {
                    qrCodeUrl += `?_=${new Date().getTime()}`;
                } else {
                    qrCodeUrl += `&_=${new Date().getTime()}`;
                }
                
                // Show QR code
                if (displayElem) displayElem.style.display = 'block';
                
                // Set image source with cache busting
                const qrImage = document.getElementById('qrCodeImage');
                if (qrImage) {
                    qrImage.onload = function() {
                        console.log("QR code image loaded successfully");
                    };
                    qrImage.onerror = function() {
                        console.error("QR code image failed to load");
                        // Try without cache busting as a fallback
                        qrImage.src = data.qr_code_url;
                    };
                    qrImage.src = qrCodeUrl;
                }
                
                // Set equipment ID
                const qrEquipmentId = document.getElementById('qrCodeEquipmentId');
                if (qrEquipmentId) qrEquipmentId.textContent = `Equipment ID: ${equipmentId}`;
                
                // Set URL display
                const qrUrlDisplay = document.getElementById('qrCodeUrlDisplay');
                if (qrUrlDisplay) qrUrlDisplay.textContent = `When scanned, takes you to: ${data.qr_url || qrUrl}`;
                
                // Set download link
                if (downloadBtn) {
                    downloadBtn.href = qrCodeUrl;
                    downloadBtn.download = `qr_code_${equipmentId}.png`;
                    downloadBtn.style.display = 'inline-block';
                }
                
                // Show print button
                if (printBtn) printBtn.style.display = 'inline-block';
                
                // Also update any QR container on the page
                const qrContainer = document.querySelector('.qr-container img');
                if (qrContainer) qrContainer.src = qrCodeUrl;
            } else {
                // Show error
                if (errorElem) {
                    errorElem.innerHTML = `<strong>Error:</strong> ${data.message || 'Failed to generate QR code'}<br>
                        <button class="btn btn-sm btn-outline-danger mt-2" onclick="generateQRCodeWithRetry('${equipmentId}', '${manufacturer}', '${model}', '${serialNumber}')">
                            <i class="bi bi-arrow-repeat"></i> Try Again
                        </button>`;
                    errorElem.style.display = 'block';
                }
            }
        })
        .catch(error => {
            console.error('Error generating QR code:', error);
            
            // Retry logic
            if (retryCount < maxRetries) {
                console.log(`Retrying QR code generation (attempt ${retryCount + 1}/${maxRetries})...`);
                retryCount++;
                
                // Show retrying message
                if (loadingElem) {
                    loadingElem.innerHTML = `
                        <div class="spinner-border text-primary" role="status">
                            <span class="visually-hidden">Loading...</span>
                        </div>
                        <p>Retrying QR code generation (attempt ${retryCount}/${maxRetries})...</p>
                    `;
                }
                
                // Retry after a delay
                setTimeout(makeRequest, 1500);
                return;
            }
            
            // Hide loading, show error after all retries failed
            if (loadingElem) loadingElem.style.display = 'none';
            
            if (errorElem) {
                errorElem.innerHTML = `<strong>Error:</strong> ${error.message}<br>
                    <small class="text-muted">There may be an issue with the QR code generator.</small><br>
                    <button class="btn btn-sm btn-outline-danger mt-2" onclick="generateQRCodeWithRetry('${equipmentId}', '${manufacturer}', '${model}', '${serialNumber}')">
                        <i class="bi bi-arrow-repeat"></i> Try Again
                    </button>`;
                errorElem.style.display = 'block';
            }
        });
    }
    
    // Start the request process
    makeRequest();
}

// Override the original function when this script loads
window.generateQRCodeForEquipment = generateQRCodeWithRetry;

// Also provide an alias with a shorter name
window.generateQR = generateQRCodeWithRetry;

// Apply fixes when the document is loaded
document.addEventListener('DOMContentLoaded', function() {
    console.log('QR fixes loaded, applying...');
    
    // Find all QR code buttons
    const allQrButtons = document.querySelectorAll('button[onclick*="generateQRCodeForEquipment"]');
    console.log(`Found ${allQrButtons.length} QR code buttons with inline onclick handlers`);
    
    // Update the onclick handlers to use our improved function
    allQrButtons.forEach((button, index) => {
        // Extract the parameters from the onclick attribute
        const onclickAttr = button.getAttribute('onclick');
        if (onclickAttr && onclickAttr.includes('generateQRCodeForEquipment')) {
            // Parse parameters from the onclick attribute
            const match = onclickAttr.match(/generateQRCodeForEquipment\('([^']*)',\s*'([^']*)',\s*'([^']*)',\s*'([^']*)'\)/);
            if (match) {
                const [_, equipmentId, manufacturer, model, serial] = match;
                
                // Replace with new function
                button.setAttribute('onclick', `generateQRCodeWithRetry('${equipmentId}', '${manufacturer}', '${model}', '${serial}')`);
                console.log(`Updated QR button #${index} for ${equipmentId}`);
            }
        }
    });
    
    // Also find QR buttons that might use data attributes
    const dataQrButtons = document.querySelectorAll('.qr-btn, .qr-dashboard-btn, .qr-direct-btn, [class*="qr-code-btn"]');
    console.log(`Found ${dataQrButtons.length} QR code buttons with data attributes`);
    
    dataQrButtons.forEach((button, index) => {
        const equipmentId = button.getAttribute('data-id') || button.getAttribute('data-equipment-id');
        const manufacturer = button.getAttribute('data-manufacturer') || '';
        const model = button.getAttribute('data-model') || '';
        const serial = button.getAttribute('data-serial') || '';
        
        if (equipmentId) {
            // Add event listener with the enhanced function
            button.addEventListener('click', function(e) {
                e.preventDefault();
                e.stopPropagation();
                generateQRCodeWithRetry(equipmentId, manufacturer, model, serial);
            });
            console.log(`Added enhanced QR event listener to button #${index} for ${equipmentId}`);
        }
    });
});