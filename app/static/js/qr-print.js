/**
 * QR Code printing functionality.
 * This file contains functions for printing QR codes from the GearVue application.
 */

// Function to print the QR code
function printQRCode() {
    // Get the elements and values
    var printWindow = window.open('', '_blank');
    var qrImage = document.getElementById('qrCodeImage').src;
    var equipmentId = document.getElementById('qrCodeEquipmentId').textContent;
    
    // Simple HTML content with minimal formatting
    var html = [
        '<!DOCTYPE html>',
        '<html>',
        '<head>',
        '<title>QR Code Print</title>',
        '<style>',
        'body { font-family: Arial; text-align: center; padding: 20px; }',
        'img { max-width: 300px; height: auto; }',
        '.container { border: 1px solid #ccc; padding: 20px; display: inline-block; }',
        '</style>',
        '</head>',
        '<body>',
        '<div class="container">',
        '<img src="' + qrImage + '" alt="QR Code">',
        '<p><strong>' + equipmentId + '</strong></p>',
        '<p>Mary Bird Perkins Cancer Center</p>',
        '</div>',
        '<script>',
        'window.onload = function() {',
        '  setTimeout(function() { window.print(); }, 500);',
        '  setTimeout(function() { window.close(); }, 1000);',
        '};',
        '</script>',
        '</body>',
        '</html>'
    ].join('\n');
    
    // Write HTML to the window and close the document stream
    printWindow.document.open();
    printWindow.document.write(html);
    printWindow.document.close();
}