/**
 * QR Code Debug Script
 * This script helps diagnose QR code button issues across the application
 */

console.log('QR Debug script loaded!');

// Global QR function - fallback implementation that will work across pages
window.generateQRCode = function(equipmentId, manufacturer, model, serialNumber) {
    console.log("Global generateQRCode called with:", { equipmentId, manufacturer, model, serialNumber });
    
    // Show the QR code modal
    const qrModalElement = document.getElementById('qrCodeModal');
    console.log('QR Modal element found:', !!qrModalElement);
    
    if (!qrModalElement) {
        alert('QR Modal not found on page. Cannot generate QR code.');
        return;
    }
    
    // Show modal
    try {
        if (typeof bootstrap !== 'undefined') {
            const qrModal = new bootstrap.Modal(qrModalElement);
            qrModal.show();
        } else {
            // Fallback when Bootstrap isn't available
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
    
    // Validate required fields
    if (!equipmentId) {
        if (loadingElem) loadingElem.style.display = 'none';
        if (errorElem) {
            errorElem.textContent = "Missing equipment ID";
            errorElem.style.display = 'block';
        } else {
            alert("Missing equipment ID");
        }
        return;
    }
    
    // Construct the URL for the QR code - direct to the equipment detail page
    const baseUrl = window.location.origin;
    const qrUrl = `${baseUrl}/qr/equipment/${equipmentId}`;
    
    // Make AJAX request to generate the QR code
    const requestData = {
        url: qrUrl,
        equipment_id: equipmentId,
        manufacturer: manufacturer || '',
        model: model || '',
        serial: serialNumber || ''
    };
    
    console.log('Sending QR code request:', requestData);
    
    fetch('/admin/equipment/generate-qr', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
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
            // Show QR code
            if (displayElem) displayElem.style.display = 'block';
            
            // Set image source
            const qrImage = document.getElementById('qrCodeImage');
            if (qrImage) qrImage.src = data.qr_code_url;
            
            // Set equipment ID
            const qrEquipmentId = document.getElementById('qrCodeEquipmentId');
            if (qrEquipmentId) qrEquipmentId.textContent = `Equipment ID: ${equipmentId}`;
            
            // Set URL display
            const qrUrlDisplay = document.getElementById('qrCodeUrlDisplay');
            if (qrUrlDisplay) qrUrlDisplay.textContent = `When scanned, takes you to: ${data.qr_url || qrUrl}`;
            
            // Set download link
            if (downloadBtn) {
                downloadBtn.href = data.qr_code_url;
                downloadBtn.download = `qr_code_${equipmentId}.png`;
                downloadBtn.style.display = 'inline-block';
            }
            
            // Show print button
            if (printBtn) printBtn.style.display = 'inline-block';
            
            // Also update any QR container on the page
            const qrContainer = document.querySelector('.qr-container img');
            if (qrContainer) qrContainer.src = data.qr_code_url;
        } else {
            // Show error
            if (errorElem) {
                errorElem.textContent = data.message || 'Failed to generate QR code';
                errorElem.style.display = 'block';
            } else {
                alert('Failed to generate QR code: ' + (data.message || 'Unknown error'));
            }
        }
    })
    .catch(error => {
        console.error('Error generating QR code:', error);
        
        // Hide loading, show error
        if (loadingElem) loadingElem.style.display = 'none';
        
        if (errorElem) {
            errorElem.textContent = `Error: ${error.message}`;
            errorElem.style.display = 'block';
        } else {
            alert('Error generating QR code: ' + error.message);
        }
    });
};

// Alias the function for other pages
window.generateQR = window.generateQRCode;
window.generateQRCodeForEquipment = window.generateQRCode;

document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM loaded in QR debug script');

    // Check for QR buttons in all pages
    const adminQrButtons = document.querySelectorAll('.qr-btn');
    const dashboardQrButtons = document.querySelectorAll('.qr-dashboard-btn');
    const directQrButtons = document.querySelectorAll('.qr-direct-btn');
    const generateQrBtns = document.querySelectorAll('#generateQRBtn, #regenerateQRBtn');

    console.log('Found QR buttons:', {
        'Admin': adminQrButtons.length,
        'Dashboard': dashboardQrButtons.length,
        'Direct': directQrButtons.length,
        'Generate': generateQrBtns.length
    });

    // Attach event handlers directly to all QR buttons
    function attachHandlers(buttons, name) {
        buttons.forEach((button, index) => {
            console.log(`Attaching handler to ${name} button ${index}:`, button);
            
            // Check if data attributes are present
            const id = button.getAttribute('data-id');
            const manufacturer = button.getAttribute('data-manufacturer');
            const model = button.getAttribute('data-model');
            const serial = button.getAttribute('data-serial');
            
            console.log(`Button ${index} data:`, { id, manufacturer, model, serial });
            
            // Attach handler
            button.addEventListener('click', function(e) {
                console.log(`${name} QR button ${index} clicked!`);
                e.preventDefault();
                e.stopPropagation();
                
                // Show debug info
                const debugInfo = document.createElement('div');
                debugInfo.style.position = 'fixed';
                debugInfo.style.top = '50px';
                debugInfo.style.right = '10px';
                debugInfo.style.backgroundColor = '#007bff';
                debugInfo.style.color = '#fff';
                debugInfo.style.padding = '10px';
                debugInfo.style.borderRadius = '5px';
                debugInfo.style.zIndex = '9999';
                debugInfo.innerHTML = `Button clicked: ${name} #${index}<br>ID: ${id}<br>Manufacturer: ${manufacturer}`;
                document.body.appendChild(debugInfo);
                
                setTimeout(() => {
                    debugInfo.remove();
                }, 3000);
                
                // Call our global function
                window.generateQRCode(id, manufacturer, model, serial);
            });
        });
    }

    attachHandlers(adminQrButtons, 'Admin');
    attachHandlers(dashboardQrButtons, 'Dashboard');
    attachHandlers(directQrButtons, 'Direct');
    attachHandlers(generateQrBtns, 'Generate');
    
    // Check if the QR modal exists
    const qrModal = document.getElementById('qrCodeModal');
    console.log('QR Modal found:', !!qrModal);
    
    // Check Bootstrap availability
    console.log('Bootstrap available:', typeof bootstrap !== 'undefined');
    if (typeof bootstrap !== 'undefined') {
        console.log('Bootstrap version:', bootstrap.Tooltip?.VERSION || 'unknown');
    }
    
    // Close button for modal without bootstrap
    const closeButtons = document.querySelectorAll('[data-bs-dismiss="modal"]');
    closeButtons.forEach(button => {
        button.addEventListener('click', function() {
            const modal = this.closest('.modal');
            if (modal) {
                modal.style.display = 'none';
                modal.classList.remove('show');
                document.body.classList.remove('modal-open');
                
                // Remove backdrop
                const backdrop = document.querySelector('.modal-backdrop');
                if (backdrop) backdrop.remove();
            }
        });
    });
});

// Print QR code function
window.printQRCode = function() {
    const printWindow = window.open('', '_blank');
    const qrImage = document.getElementById('qrCodeImage').src;
    const equipmentId = document.getElementById('qrCodeEquipmentId').textContent;
    
    printWindow.document.write(`
        <!DOCTYPE html>
        <html>
        <head>
            <title>QR Code - ${equipmentId}</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    text-align: center;
                    padding: 20px;
                }
                img {
                    max-width: 300px;
                    height: auto;
                }
                .container {
                    display: inline-block;
                    border: 1px solid #ccc;
                    padding: 20px;
                    margin: 10px;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <img src="${qrImage}" alt="QR Code">
                <div>
                    <p><strong>${equipmentId}</strong></p>
                    <p>Mary Bird Perkins Cancer Center</p>
                </div>
            </div>
            <script>
                window.onload = function() {
                    setTimeout(() => {
                        window.print();
                        setTimeout(() => {
                            window.close();
                        }, 100);
                    }, 500);
                };
            </script>
        </body>
        </html>
    `);
    printWindow.document.close();
};